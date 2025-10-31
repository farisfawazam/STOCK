# Prompt Web App Inventory Packaging

Bangunkan web app Inventory Packaging sesuai struktur Google Sheets berikut. Gunakan Next.js 14 + TypeScript + Prisma + SQLite (boleh ganti ke Postgres via .env), TailwindCSS, shadcn/ui, dan Zod untuk validasi.

## Modul & Halaman

Dashboard

KPI hari ini & bulan ini: Total Masuk, Keluar, Adjust In/Out, TW Out/In, 5 item tersering diselisih, 5 item teratas by throughput.

Grafik garis: stok item terpilih per hari.

Barang Masuk (MRD)

Tabel dengan filter tanggal, MRD No, nama barang. CRUD + impor CSV.

Barang Keluar (Filling/Consume)

Tabel dengan filter tanggal, No Filling, nama produk/karton. CRUD + impor CSV.

Adjust In dan Adjust Out

Dua halaman serupa untuk koreksi stok, wajib kolom alasan/KET.

Transfer Warehouse (TW)

Catat transfer antar gudang (asal, tujuan). CRUD + nomor TW otomatis.

Master Data

Item: kode, nama, satuan dasar (pcs), qtyPerDus, kategori, status aktif.

Gudang: kode, nama.

Stock

Periode & tanggal, stok awal, pergerakan, stok akhir, fisik vs sistem, selisih, persentase, KET (JALAN/TIDAK JALAN).

Laporan

Harian/Mingguan/Bulanan: ringkasan masuk/keluar/adjust/TW, dan CSV export.

## Aturan Perhitungan (engine)

Definisikan movement bertanda:

IN: MRD (Barang Masuk), Adjust In, TW In.

OUT: Filling (Barang Keluar), Adjust Out, TW Out.

Stok Sistem per item per gudang per tanggal dihitung akumulatif:
stok_t(n) = stok_t(n-1) + ΣIN(n) − ΣOUT(n).

Selisih bila ada opname: SELISIH = FISIK − VENUS (stok sistem);
Persentase: abs(SELISIH) / max(1, VENUS).

KET otomatis:

JALAN bila ada transaksi pada periode / selisih = 0;

TIDAK JALAN bila tidak ada transaksi > N hari (set N=14) atau persentase selisih > 5%. (Buat parameter konfigurasi.)

## Skema Basis Data (Prisma)

Warehouse(id, code, name)

Item(id, code UNIQUE, name, unit DEFAULT 'pcs', qtyPerDus Int, category?, isActive Boolean)

StockOpname(id, date, warehouseId, itemId, qtyFisik, note?)

Movement(id, date, type ENUM['MRD','FILLING','ADJ_IN','ADJ_OUT','TW_IN','TW_OUT'], refNo, warehouseFromId?, warehouseToId?, itemId, qty, note?)

PeriodOpening(id, periodMonth, periodYear, warehouseId, itemId, openingQty)

Index gabungan untuk Movement(date, itemId) dan Movement(type, refNo).

## Fitur Penting

Import CSV untuk tiap modul (map kolom otomatis ke: tanggal, refNo, item, qty, KET).

Auto-number: MRD/ADJ/TW sesuai pola TW/{seq}/{YYYY}/{MM}.

Audit log (updatedBy, createdBy, timestamps).

Role: Viewer (read-only), Operator (CRUD), Admin (master + konfigurasi).

Satuan dus: tampilkan helper kolom dus = floor(qty / qtyPerDus) dan sisa = qty % qtyPerDus.

Export: CSV/Excel dari tabel & laporan.

Filter & pencarian cepat di semua tabel.

Validasi: qty > 0, tanggal wajib; item & gudang harus ada.

## UI/UX

Gunakan shadcn/ui: Card, Table, Dialog, Form, Badge, Tabs, DatePicker.

Layout sidebar: Dashboard, Stock, Barang Masuk, Barang Keluar, Adjust In, Adjust Out, TW, Master, Laporan.

Komponen bersama: MovementForm, ImportDialog, ReportFilters.

## Seeder (contoh data)

5 gudang (VENUS, PRODUKSI, FG, RM, QA).

10 item contoh dari spreadsheet (kode & nama nyata), isi qtyPerDus sesuai kolom “QTY PER 1 DUS”.

30 hari transaksi campuran MRD/FILLING/ADJ/TW agar grafik jalan.

## API (Next.js Route Handlers)

GET /api/stock?date=YYYY-MM-DD&warehouseId=&itemId= → stok sistem + fisik (jika ada) + selisih.

GET /api/movements?type=&dateFrom=&dateTo=&itemId=&warehouseId=

POST /api/movements (buat transaksi)

POST /api/import/{module} (CSV)

GET /api/report/summary?granularity=day|week|month

## Perhitungan “STOCK” view (mirip sheet kamu)

Kolom: Periode, Pertanggal, Kode Barang, Nama Barang, Stock Awal, MRD, Filling, Adjust In, Adjust Out, TW In, TW Out, Stock Akhir, Venus (Sistem), Fisik (Opname, optional), Selisih, Qty per 1 Dus, Persentase, Ket.

Stock Akhir = Stock Awal + MRD + Adjust In + TW In − Filling − Adjust Out − TW Out.

Tampilkan badge warna untuk persentase selisih: <1% hijau, 1–5% kuning, >5% merah.

## Kualitas Kode

Ketik penuh (TS), ESLint/Prettier, pnpm.

Buat unit test minimal untuk fungsi kalkulasi stok & selisih.

Sertakan README dengan langkah setup, seeding, dan impor CSV.

Hasilkan proyek lengkap beserta file Prisma schema, komponen UI, route API, seeder, dan README. Pastikan aplikasi bisa pnpm install && pnpm prisma migrate dev && pnpm dev.

## Bonus Prompt Singkat

Build a Next.js + Prisma + SQLite Inventory Packaging app that mirrors these sheets: STOCK, BARANG MASUK (MRD), BARANG KELUAR (FILLING), ADJUST IN/OUT, TW. Implement movements (MRD, FILLING, ADJ_IN, ADJ_OUT, TW_IN, TW_OUT), stock formula opening + IN − OUT, opname vs system difference, CSV import/export, reports (day/week/month), role-based access, and pretty Tailwind + shadcn UI. Include seeds, tests, and README.
