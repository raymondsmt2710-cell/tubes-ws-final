# Skema CSV Kurasi

**Pemilik:** Charles · **Konsumen:** Alvin, Ryan Fredryck, Raymond, Ryan Dani
**Basis:** `plan.md` revisi 7 §5.2, §5.3, §6.2 · `bagi_tugas.md` revisi 3 §3, §6
**Status:** dibekukan pada rapat hari 1. Perubahan kolom lewat Charles; kolom baru yang butuh properti baru lewat Alvin.

Tiga berkas:

| Berkas | Isi | Kelas RDF |
|---|---|---|
| `reference.csv` | wilayah, tokoh, peristiwa, organisasi | `Provinsi`, `Kota`, `Kabupaten`, `Pulau`, `Tokoh`, `Peristiwa`, `Organisasi` |
| `museums.csv` | museum hasil kurasi | `Museum` |
| `collections.csv` | koleksi museum | `Koleksi` |

Urutan pengisian: **reference → museums → collections**, karena baris yang merujuk butuh baris yang dirujuk.

---

## 1. Cara mengisi (untuk semua anggota)

Jangan sunting CSV di repo. Isi di **Google Sheet "Kurasi Museum Sumatera"**, tab yang sesuai, dengan kolom `kurator` berisi nama Anda. Charles yang mengekspor dan meng-commit setelah QA.

Contoh lengkap satu baris museum, dibaca per kolom:

| Kolom | Isi | Keterangan |
|---|---|---|
| `id` | `MuseumNegeriSumut` | nama unik, tanpa spasi, tidak pernah diubah |
| `nama` | `Museum Negeri Provinsi Sumatera Utara` | nama resmi |
| `nama_alternatif` | `Museum Negeri Sumut\|Museum Negeri Medan` | nama lain yang sering dicari, pisahkan dengan `\|` |
| `jenis` | `Museum umum` | ambil dari daftar §4 |
| `deskripsi` | 1–3 kalimat | tulis sendiri, jangan salin Wikipedia |
| `berlokasi_di` | `KotaMedan` | **`id`** kota/kabupaten dari `reference.csv`, bukan nama |
| `gambar` | `https://upload.wikimedia.org/…jpg` | wajib dicari, boleh kosong; bila kosong tulis alasannya di `catatan` |
| `sumber` | `https://…` | halaman yang membuktikan isi baris ini |
| `kurator` | `Charles` | nama Anda |

Kolom yang tidak tahu jawabannya: **kosongkan**. Jangan tulis `-`, `?`, `N/A`, atau perkiraan.

---

## 2. Aturan format

| Aturan | Nilai |
|---|---|
| Encoding | UTF-8 **tanpa BOM** |
| Pemisah kolom | koma `,` — ekspor dari Google Sheets atau LibreOffice, **jangan simpan dari Excel** (Excel berlokal Indonesia memakai `;`) |
| Kutip | `"` bila sel memuat koma, kutip, atau baris baru (RFC 4180) |
| Nilai jamak | dipisah `\|` tanpa spasi: `Museum umum\|Museum sejarah` |
| Sel kosong | dibiarkan kosong |
| Desimal | titik: `3.5952` |
| Akhir baris | LF (dijaga `.gitattributes`: `*.csv text eol=lf`) |
| Urutan kolom | sama persis dengan header di berkas; jangan menambah atau menukar kolom |

---

## 3. Aturan `id`

`id` adalah nama lokal IRI: `KotaMedan` → `http://usu.ac.id/museum#KotaMedan`.

1. **Unik di ketiga berkas sekaligus**, karena semua berbagi satu namespace.
2. ASCII, PascalCase, tanpa spasi dan tanda baca: `MuseumNegeriSumut`, `KabupatenNiasSelatan`.
3. Awalan tipe untuk wilayah: `Kota…`, `Kabupaten…`, `Pulau…`. Provinsi tanpa awalan: `SumateraUtara`, `Bali`.
4. Koleksi bernama umum diberi akhiran museum: `KerisMuseumNegeriSumut`, bukan `Keris`.
5. **Sekali dipakai, tidak diubah**, walau salah ketik. IRI yang berubah memutus tautan `museum.php?id=…` dan tes.
6. Kolom rujukan (`berlokasi_di`, `dimiliki_oleh`, `bagian_dari`, …) berisi **`id`**, bukan nama.
7. Sebelum memakai `id` baru, periksa tab `daftar_id` di Sheet.

**Museum yang juga ada di Wikidata:** isi `qid`. `build_dataset.py` menggabungkan rekaman Wikidata ber-QID sama ke baris kurasi, dan `id` kurasi yang menjadi IRI. Bila bertentangan, data kurasi menang (`plan.md` §6.3).

---

## 4. Daftar terkontrol `jenis`

Ditulis persis seperti di tabel (huruf besar hanya di awal). Ejaan lain dihitung sebagai jenis berbeda oleh facet pencarian. Daftar resmi ada di komentar `data/ontology/museum.ttl` milik Alvin; tabel ini salinannya.

**Museum** (`plan.md` §5.1): Museum umum · Museum sejarah · Museum budaya · Museum seni · Museum alam · Museum zoologi · Museum militer · Museum maritim · Museum teknologi

**Koleksi** (usulan Charles, menunggu penetapan Alvin): Senjata tradisional · Tekstil · Pakaian adat · Perhiasan · Naskah kuno · Arca dan prasasti · Keramik dan gerabah · Alat musik · Alat rumah tangga · Benda perjuangan · Foto dan dokumen · Lukisan · Spesimen alam · Mata uang · Miniatur dan replika

---

## 5. `reference.csv`

| Kolom | Wajib | Properti RDF | Isi |
|---|---|---|---|
| `id` | ✔ | IRI subjek | §3 |
| `tipe` | ✔ | `rdf:type ex:<tipe>` | `Provinsi` · `Kota` · `Kabupaten` · `Pulau` · `Tokoh` · `Peristiwa` · `Organisasi` |
| `nama` | ✔ | `ex:nama`, `rdfs:label`@id | |
| `nama_alternatif` | | `ex:namaAlternatif` | jamak `\|`: `Medan` untuk `KotaMedan` |
| `deskripsi` | | `ex:deskripsi` | untuk Tokoh, Peristiwa, Organisasi |
| `bagian_dari` | ✔ untuk Kota/Kabupaten | `ex:bagianDari` | **satu langkah ke atas saja**: Kota/Kabupaten → Provinsi; Provinsi → Pulau |
| `lintang` | | `ex:lintang` (`xsd:decimal`) | wilayah |
| `bujur` | | `ex:bujur` (`xsd:decimal`) | wilayah |
| `situs_web` | | `ex:situsWeb` (`xsd:anyURI`) | Organisasi |
| `qid` | bila ada | `owl:sameAs wd:Q…` | `Q2140`, tanpa URL |
| `sumber` | ✔ | `dcterms:source` | URL, jamak `\|` |
| `kurator` | ✔ | — | diabaikan build |
| `catatan` | | — | diabaikan build |

`bagian_dari` jangan dilompati: `KotaMedan` diisi `SumateraUtara`, **bukan** `PulauSumatera`. Transitivitas dikerjakan reasoner.

**Kepulauan Riau dan Kepulauan Bangka Belitung** tidak terletak di Pulau Sumatera. `bagian_dari`-nya dibiarkan kosong sampai Alvin memutuskan (lihat `catatan` di baris masing-masing). Akibatnya: penelusuran lewat `PulauSumatera` tidak menemukan museum di dua provinsi itu, tetapi penelusuran per provinsi tetap jalan.

---

## 6. `museums.csv`

| Kolom | Wajib | Properti RDF | Isi |
|---|---|---|---|
| `id` | ✔ | IRI, `rdf:type ex:Museum` | §3 |
| `nama` | ✔ | `ex:nama`, `rdfs:label`@id | nama resmi |
| `nama_alternatif` | | `ex:namaAlternatif` | jamak `\|` |
| `jenis` | ✔ | `ex:jenis` | jamak `\|`, dari §4 |
| `deskripsi` | ✔ | `ex:deskripsi` | 1–3 kalimat, ditulis sendiri |
| `berlokasi_di` | ✔ | `ex:berlokasiDi` | `id` **Kota/Kabupaten** |
| `gambar` | dicari | `ex:gambar` (`xsd:anyURI`) | URL Wikimedia Commons (`upload.wikimedia.org`) atau situs resmi museum, diawali `https://`; kosong bila tak terverifikasi |
| `alamat` | | `ex:alamat` | |
| `lintang` | | `ex:lintang` | |
| `bujur` | | `ex:bujur` | |
| `tahun_berdiri` | | `ex:tahunBerdiri` (`xsd:gYear`) | 4 digit |
| `didirikan_oleh` | | `ex:didirikanOleh` | jamak `\|`, `id` Tokoh |
| `organisasi` | | `ex:bagianDariOrganisasi` | `id` Organisasi |
| `terkait_dengan` | | `ex:terkaitDengan` | jamak `\|`, `id` Museum; satu arah cukup (simetris) |
| `jam_buka` | | `ex:jamBuka` | teks: `Selasa–Minggu 08.00–16.00` |
| `harga_tiket` | | `ex:hargaTiket` (`xsd:integer`) | rupiah, dewasa, tanpa titik: `5000` |
| `situs_web` | | `ex:situsWeb` | diawali `https://` |
| `kode_museum` | | `ex:kodeMuseum` | kode resmi bila ada |
| `qid` | bila ada | `owl:sameAs` | |
| `sumber` | ✔ | `dcterms:source` | |
| `kurator` | ✔ | — | |
| `catatan` | | — | |

---

## 7. `collections.csv`

| Kolom | Wajib | Properti RDF | Isi |
|---|---|---|---|
| `id` | ✔ | IRI, `rdf:type ex:Koleksi` | §3 |
| `nama` | ✔ | `ex:nama`, `rdfs:label`@id | |
| `nama_alternatif` | | `ex:namaAlternatif` | jamak `\|` |
| `jenis` | ✔ | `ex:jenis` | jamak `\|`, dari §4 |
| `deskripsi` | | `ex:deskripsi` | |
| `dimiliki_oleh` | ✔ | `ex:dimilikiOleh` | `id` Museum |
| `berasal_dari` | ✔\* | `ex:berasalDari` | `id` Provinsi/Kota/Kabupaten, **sespesifik mungkin** |
| `dibuat_oleh` | ✔\* | `ex:dibuatOleh` | jamak `\|`, `id` Tokoh |
| `terkait_tokoh` | | `ex:terkaitTokoh` | jamak `\|`, `id` Tokoh selain pembuat |
| `menggambarkan` | | `ex:menggambarkan` | jamak `\|`, `id` Peristiwa |
| `bahan` | | `ex:bahan` | jamak `\|` |
| `tahun_pembuatan` | | `ex:tahunPembuatan` | teks: `1890` atau `abad ke-19` |
| `sumber` | ✔ | `dcterms:source` | |
| `kurator` | ✔ | — | |
| `catatan` | | — | |

\* Wajib salah satu dari `berasal_dari` atau `dibuat_oleh`.

**`berasal_dari` sespesifik mungkin.** Ulos dari Nias diisi `KabupatenNias`, bukan `SumateraUtara`. Pola `(ex:bagianDari)*` naik sendiri ke provinsi; kebalikannya tidak bisa.

---

## 8. Pemetaan ke properti

Setiap kolom punya pasangan properti di `plan.md` §5.2–5.3, kecuali `tipe`, `kurator`, dan `catatan`. Tidak ada kolom cadangan. Properti invers **tidak** ditulis: `memilikiKoleksi`, `memilikiMuseum`, dan `mendirikan` diturunkan dari arah sebaliknya.

Semua baris memperoleh `dcterms:source` dari kolom `sumber`. `nama` ditulis dua kali — `ex:nama` dan `rdfs:label "…"@id` — karena pencarian dan entity linking memakai `rdfs:label`.

---

## 9. Data uji bukan data kurasi

Fixture di `plan.md` §5.5 dan `bagi_tugas.md` §4 (MuseumA/MuseumB, KerisBali yang dititipkan di museum Medan, TokohX) adalah **rekaan untuk menguji aturan OWL**. Bila masuk ke CSV ini, rekaan itu ikut menjadi fakta di graph asserted dan tampil di pencarian. Karena itu CSV kurasi hanya memuat baris yang bisa diverifikasi, dan fixture ditulis terpisah di `tests/fixtures/` dengan skema yang sama — usulan untuk Ryan Fredryck, pemilik `tests/`.

Yang boleh ada di kedua tempat hanya entitas wilayah yang memang nyata (`KotaMedan`, `SumateraUtara`, `Bali`, `PulauBali`, `KotaGunungsitoli`, …).

---

## 10. Keputusan terbuka

| # | Hal | Diputuskan oleh |
|---|---|---|
| 1 | Daftar `jenis` koleksi (§4) | Alvin |
| 2 | `bagian_dari` untuk Kepulauan Riau dan Bangka Belitung (§5) | Alvin |
| 3 | Alias "Nias": dipasang di `KabupatenNias` saja, bukan di `KotaGunungsitoli`, agar resolusi entitas tidak punya dua kandidat | Raymond (pencarian) |
| 4 | QID dan URL gambar di baris benih | diverifikasi saat QA gelombang 1 |
