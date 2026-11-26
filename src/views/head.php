<?php

$__judul = $judul ?? $title ?? $page_title ?? null;
$__judul_tab = $__judul !== null && $__judul !== ''
    ? $__judul . ' · Museum Sumatera'
    : 'Museum Sumatera — Pencarian Semantik';

$__halaman = basename($_SERVER['SCRIPT_NAME'] ?? 'index.php');

$__menu = [
    ['index.php',    'Cari',     ['index.php', 'museum.php']],
    ['ontologi.php', 'Ontologi', ['ontologi.php']],
    ['graf.php',     'Graf',     ['graf.php']],
    ['tentang.php',  'Tentang',  ['tentang.php']],
];

$__menu = array_values(array_filter(
    $__menu,
    fn ($m) => $m[0] !== 'graf.php' || is_file(__DIR__ . '/../../public/graf.php')
));
?><!DOCTYPE html>
<html lang="id">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title><?= htmlspecialchars($__judul_tab, ENT_QUOTES, 'UTF-8') ?></title>
  <link rel="preload" href="/fonts/inter-latin-400-normal.woff2" as="font" type="font/woff2" crossorigin>
  <link rel="stylesheet" href="/fonts/fonts.css">
  <link rel="stylesheet" href="/app.css">
</head>
<body class="min-h-screen bg-stone-50 font-sans text-stone-800 antialiased">
  <a href="#isi" class="sr-only focus:not-sr-only focus:absolute focus:left-4 focus:top-4 focus:rounded focus:bg-white focus:px-3 focus:py-2 focus:shadow">Langsung ke isi</a>

  <header class="border-b border-stone-200 bg-white">
    <div class="mx-auto flex max-w-6xl flex-wrap items-center justify-between gap-x-8 gap-y-3 px-4 py-4">
      <a href="/index.php" class="group flex items-baseline gap-2">
        <span class="font-serif text-xl font-semibold text-stone-900 group-hover:text-amber-800">Museum Sumatera</span>
        <span class="text-xs uppercase tracking-wider text-stone-500">pencarian semantik</span>
      </a>

      <nav aria-label="Menu utama">
        <ul class="flex flex-wrap gap-1 text-sm">
          <?php foreach ($__menu as [$__berkas, $__label, $__aktif_di]):
              $__aktif = in_array($__halaman, $__aktif_di, true); ?>
            <li>
              <a href="/<?= $__berkas ?>"
                 <?= $__aktif ? 'aria-current="page"' : '' ?>
                 class="block rounded-md px-3 py-2 <?= $__aktif
                     ? 'bg-amber-100 font-medium text-amber-900'
                     : 'text-stone-600 hover:bg-stone-100 hover:text-stone-900' ?>">
                <?= htmlspecialchars($__label, ENT_QUOTES, 'UTF-8') ?>
              </a>
            </li>
          <?php endforeach; ?>
        </ul>
      </nav>
    </div>
  </header>

  <main id="isi" class="mx-auto max-w-6xl px-4 py-8">
<?php
unset($__judul, $__judul_tab, $__halaman, $__menu, $__berkas, $__label, $__aktif_di, $__aktif);