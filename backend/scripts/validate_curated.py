"""Validasi CSV kurasi sebelum commit. Hanya pustaka standar.

Pemakaian:
    python backend/scripts/validate_curated.py                # data/curated
    python backend/scripts/validate_curated.py tests/fixtures # folder lain

Keluar dengan kode 1 bila ada kegagalan. Laporan dikelompokkan per kurator
supaya baris yang gagal bisa dikembalikan ke pengisinya (SKEMA.md, bagi_tugas §6).
"""
import csv
import re
import sys
from collections import defaultdict
from pathlib import Path

HEADER = {
    "reference": ["id", "tipe", "nama", "nama_alternatif", "deskripsi", "bagian_dari", "lintang", "bujur",
                  "situs_web", "qid", "sumber", "kurator", "catatan"],
    "museums": ["id", "nama", "nama_alternatif", "jenis", "deskripsi", "berlokasi_di", "gambar", "alamat",
                "lintang", "bujur", "tahun_berdiri", "didirikan_oleh", "organisasi", "terkait_dengan", "jam_buka",
                "harga_tiket", "situs_web", "kode_museum", "qid", "sumber", "kurator", "catatan"],
    "collections": ["id", "nama", "nama_alternatif", "jenis", "deskripsi", "dimiliki_oleh", "berasal_dari",
                    "dibuat_oleh", "terkait_tokoh", "menggambarkan", "bahan", "tahun_pembuatan", "sumber",
                    "kurator", "catatan"],
}
WAJIB = {
    "reference": ["id", "tipe", "nama", "sumber", "kurator"],
    "museums": ["id", "nama", "jenis", "deskripsi", "berlokasi_di", "sumber", "kurator"],
    "collections": ["id", "nama", "jenis", "dimiliki_oleh", "sumber", "kurator"],
}
TIPE = {"Provinsi", "Kota", "Kabupaten", "Pulau", "Tokoh", "Peristiwa", "Organisasi"}
DAERAH = {"Provinsi", "Kota", "Kabupaten"}
JENIS_MUSEUM = {"Museum umum", "Museum sejarah", "Museum budaya", "Museum seni", "Museum alam",
                "Museum zoologi", "Museum militer", "Museum maritim", "Museum teknologi"}
JENIS_KOLEKSI = {"Senjata tradisional", "Tekstil", "Pakaian adat", "Perhiasan", "Naskah kuno",
                 "Arca dan prasasti", "Keramik dan gerabah", "Alat musik", "Alat rumah tangga",
                 "Benda perjuangan", "Foto dan dokumen", "Lukisan", "Spesimen alam", "Mata uang",
                 "Miniatur dan replika"}
# rujukan: kolom -> (berkas tujuan, tipe yang diterima atau None untuk museum)
RUJUKAN = {
    "reference": {"bagian_dari": {"Provinsi", "Pulau"}},
    "museums": {"berlokasi_di": {"Kota", "Kabupaten"}, "didirikan_oleh": {"Tokoh"},
                "organisasi": {"Organisasi"}, "terkait_dengan": "MUSEUM"},
    "collections": {"dimiliki_oleh": "MUSEUM", "berasal_dari": DAERAH, "dibuat_oleh": {"Tokoh"},
                    "terkait_tokoh": {"Tokoh"}, "menggambarkan": {"Peristiwa"}},
}
JAMAK = {"nama_alternatif", "jenis", "didirikan_oleh", "terkait_dengan", "dibuat_oleh", "terkait_tokoh",
         "menggambarkan", "bahan", "sumber"}

RE_ID = re.compile(r"^[A-Z][A-Za-z0-9]*$")
RE_QID = re.compile(r"^Q[1-9][0-9]*$")
RE_URL = re.compile(r"^(https://\S+|urn:fixture)$")


def nilai(baris, kolom):
    v = (baris.get(kolom) or "").strip()
    if not v:
        return []
    return v.split("|") if kolom in JAMAK else [v]


def baca(folder):
    data, galat = {}, []
    for nama, header in HEADER.items():
        path = folder / f"{nama}.csv"
        raw = path.read_bytes()
        if raw.startswith(b"\xef\xbb\xbf"):
            galat.append((None, f"{path.name}: diawali BOM; ekspor ulang sebagai UTF-8 tanpa BOM"))
        if b"\r\n" in raw:
            galat.append((None, f"{path.name}: akhir baris CRLF; harus LF"))
        with path.open(encoding="utf-8-sig", newline="") as f:
            r = csv.DictReader(f)
            if r.fieldnames != header:
                galat.append((None, f"{path.name}: header tidak sesuai SKEMA.md\n    ada:      {r.fieldnames}\n    harusnya: {header}"))
                data[nama] = []
                continue
            data[nama] = [(i + 2, b) for i, b in enumerate(r)]
    return data, galat


def periksa(folder):
    data, galat = baca(folder)
    tipe_id = {}
    for nama, rows in data.items():
        for ln, b in rows:
            i = b["id"].strip()
            asal = f"{nama}.csv:{ln}"
            if i in tipe_id:
                galat.append((b.get("kurator"), f"{asal}: id '{i}' sudah dipakai di {tipe_id[i][1]}"))
            tipe_id[i] = ("MUSEUM" if nama == "museums" else "KOLEKSI" if nama == "collections"
                          else b["tipe"].strip(), asal)

    for nama, rows in data.items():
        for ln, b in rows:
            asal = f"{nama}.csv:{ln} ({b['id']})"
            k = b.get("kurator")
            salah = lambda pesan: galat.append((k, f"{asal}: {pesan}"))

            for kol in WAJIB[nama]:
                if not b[kol].strip():
                    salah(f"kolom wajib '{kol}' kosong")
            if b["id"] and not RE_ID.match(b["id"]):
                salah("id harus ASCII PascalCase tanpa spasi")
            if nama == "reference":
                if b["tipe"] not in TIPE:
                    salah(f"tipe '{b['tipe']}' tidak dikenal")
                if b["tipe"] in {"Kota", "Kabupaten"} and not b["bagian_dari"]:
                    salah("Kota/Kabupaten wajib punya bagian_dari")
            if nama == "collections" and not (b["berasal_dari"] or b["dibuat_oleh"]):
                salah("wajib salah satu dari berasal_dari atau dibuat_oleh")

            daftar = JENIS_MUSEUM if nama == "museums" else JENIS_KOLEKSI if nama == "collections" else None
            if daftar:
                for j in nilai(b, "jenis"):
                    if j not in daftar:
                        salah(f"jenis '{j}' tidak ada di daftar terkontrol")

            for kol, terima in RUJUKAN[nama].items():
                for ref in nilai(b, kol):
                    if ref not in tipe_id:
                        salah(f"{kol} '{ref}' tidak ditemukan")
                    elif terima != tipe_id[ref][0] and tipe_id[ref][0] not in (terima if isinstance(terima, set) else ()):
                        salah(f"{kol} '{ref}' bertipe {tipe_id[ref][0]}, harusnya {terima}")
                    if ref == b["id"]:
                        salah(f"{kol} menunjuk dirinya sendiri")

            for u in nilai(b, "sumber"):
                if not RE_URL.match(u):
                    salah(f"sumber '{u}' bukan URL https://")
            for kol in ("gambar", "situs_web"):
                if kol in b and b[kol] and not b[kol].startswith("https://"):
                    salah(f"{kol} harus diawali https://")
            if b.get("qid") and not RE_QID.match(b["qid"]):
                salah(f"qid '{b['qid']}' harus berbentuk Q123, tanpa URL")
            for kol, lo, hi in (("lintang", -11, 6), ("bujur", 94, 116)):
                if b.get(kol):
                    try:
                        if not lo <= float(b[kol]) <= hi:
                            salah(f"{kol} {b[kol]} di luar rentang {lo}..{hi}")
                    except ValueError:
                        salah(f"{kol} '{b[kol]}' bukan desimal bertitik")
            if b.get("tahun_berdiri") and not re.fullmatch(r"\d{4}", b["tahun_berdiri"]):
                salah("tahun_berdiri harus 4 digit")
            if b.get("harga_tiket") and not b["harga_tiket"].isdigit():
                salah("harga_tiket harus bilangan bulat tanpa titik")
            for kol, v in b.items():
                if v and v != v.strip():
                    salah(f"kolom '{kol}' diawali/diakhiri spasi")
                if v and v.strip() in {"-", "?", "N/A", "n/a"}:
                    salah(f"kolom '{kol}' berisi '{v}'; kosongkan saja")

    jumlah = {n: len(r) for n, r in data.items()}
    return galat, jumlah


def main():
    root = Path(__file__).resolve().parents[2]
    folder = Path(sys.argv[1]) if len(sys.argv) > 1 else root / "data" / "curated"
    galat, jumlah = periksa(folder)
    print(f"{folder}: " + ", ".join(f"{n} {j} baris" for n, j in jumlah.items()))
    if not galat:
        print("OK — tidak ada kegagalan.")
        return 0
    per = defaultdict(list)
    for k, p in galat:
        per[k or "(berkas)"].append(p)
    for k in sorted(per):
        print(f"\n[{k}]")
        for p in per[k]:
            print("  - " + p)
    print(f"\n{len(galat)} kegagalan.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
