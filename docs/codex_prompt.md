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

## Prompt: AUTH (Login/Logout), RBAC, & Keamanan

Tambahkan modul autentikasi & otorisasi ke proyek Inventory Packaging (Next.js 14 + TypeScript + Prisma + SQLite/Postgres, Tailwind, shadcn/ui).

### Fitur

- Login via Credentials (email/username + password) + opsi Google SSO (opsional, bisa dimatikan via ENV).
- Role-Based Access Control (RBAC): ADMIN, OPERATOR, VIEWER.
- ADMIN: kelola master (Item, Gudang), semua CRUD, konfigurasi, lihat audit log.
- OPERATOR: CRUD transaksi (MRD, FILLING, ADJ_IN, ADJ_OUT, TW), import CSV.
- VIEWER: read-only semua laporan & dashboard.
- Session via NextAuth (JWT), password hashing bcrypt.
- Proteksi page: middleware cek role per route (contoh: /master/** hanya ADMIN).
- Audit log: setiap perubahan simpan userId, timestamp, action, table, recordId, diff.
- Rate limit endpoint login (5x/menit/IP), backoff exponential.
- CSRF untuk POST/PUT/DELETE; Helmet headers; sanitasi input (Zod).
- Kebijakan password: min 8 karakter, kombinasi (huruf+angka/simbol), force reset pertama kali.

### Implementasi

- Prisma model User(id, name, email UNIQUE, username UNIQUE, passwordHash, role, isActive, createdAt, updatedAt).
- NextAuth Credentials provider + optional Google provider (tergantung ENV).
- Halaman: /login, /logout, /profile (ganti password), /admin/users (kelola user, reset password, assign role).
- Komponen: AuthGuard, RoleGate, RequireRole(roles: Role[]).
- Seed: 3 user default (admin/operator/viewer) dengan password ChangeMe123! dan wajib prompt ganti saat login pertama.
- Testing: unit test validasi password & authorization guard.

### Acceptance Criteria

- Akses tanpa login → redirect ke /login.
- Pengguna VIEWER tidak bisa membuka form CRUD (tombol disabled + toast).
- Log keluar otomatis setelah idle 30 menit (configurable).
- Seluruh perubahan tercatat di AuditLog.
- ENV dapat mematikan Google SSO dan hanya pakai Credentials.

## Prompt: UI/UX Cantik & Produktif

Rapikan UI/UX aplikasi dengan Tailwind + shadcn/ui dan prinsip dashboard modern.

### Desain Sistem

- Tema: Light & Dark mode (toggle), spacing konsisten, radius rounded-2xl, shadow lembut.
- Typography: Inter/Plus Jakarta Sans; ukuran bervariasi (h1,h2,base,sm).
- Warna status: hijau (ok), kuning (warning 1–5%), merah (>5%), abu (inactive).

### Pola Layout

- Sidebar (icon + label) : Dashboard, Stock, MRD, Filling, Adjust In, Adjust Out, TW, Master, Laporan, Admin.
- Header: search bar, date range picker, user menu (profile, logout).
- Breadcrumb di tiap halaman.

### Komponen & Interaksi

- Table Pro (shadcn Table):
  - Sticky header, kolom bisa resize, pin, sort, multi-filter (text/date/number/range).
  - Pagination, quick search (client), server-side filter (params).
  - Tombol Export CSV/Excel + Import (drag & drop) di kanan-atas tabel.
  - Row actions: Edit, Delete, View; konfirmasi modal untuk delete.
  - Skeleton loading + empty state (ilustrasi + CTA import).
- Form (shadcn Form, Dialog): validasi Zod, mask angka ribuan, datepicker, select item/gudang dengan typeahead.
- Cards KPI (Dashboard): Total Masuk/Keluar/Adjust/TW (hari ini & bulan ini), tren mini (sparkline).
- Grafik: Recharts (line & bar) untuk throughput harian; tooltip & legend responsif.
- Badge status JALAN/TIDAK JALAN, chip persentase selisih dengan warna dinamis.
- Keyboard shortcut: / = focus search, i = Import, n = New record, g s = ke Stock.

### Aksesibilitas & Detail

- Kontras warna AA, focus ring jelas, form label/aria lengkap.
- Teks angka rata kanan; gunakan thousand separator & unit dus (otomatis hitung dus & sisa).
- Toasts untuk sukses/error, retry saat network putus.

### Acceptance Criteria

- Tabel 10.000+ baris tetap lancar (virtualized rows).
- Semua halaman responsif (≥320px), dark mode stabil.
- Import CSV < 3 klik dari halaman mana pun.
- Semua aksi penting ≤2 langkah dari halaman utama modul.

## Prompt: Requirements, Setup, & Deploy

Lengkapi proyek dengan dokumen requirement, .env contoh, skrip setup, dan instruksi deploy.

### Prasyarat Teknis

- Node.js 20 LTS, pnpm terbaru.
- Database: default SQLite (dev) & Postgres (prod).
- Alat: Git, OpenSSL (buat secret), dan CLI Prisma.

### Dependensi Utama

- next, react, typescript, prisma, @prisma/client
- next-auth, bcrypt, zod, axios, dayjs
- tailwindcss, @shadcn/ui, clsx
- recharts, react-hook-form, @tanstack/react-table
- csv-parse, papaparse/xlsx (export), zod-form-data

### Struktur ENV & Contoh `.env.example`

```
# App
NEXT_PUBLIC_APP_NAME=Inventory Packaging
NEXTAUTH_URL=http://localhost:3000
NEXTAUTH_SECRET=replace_me # gunakan `openssl rand -base64 32`

# DB
DATABASE_URL="file:./dev.db"             # SQLite dev
# DATABASE_URL="postgresql://user:pass@host:5432/inventory"  # prod

# Auth Providers (opsional)
GOOGLE_CLIENT_ID=
GOOGLE_CLIENT_SECRET=
ENABLE_GOOGLE_SSO=false

# Security
RATE_LIMIT_LOGIN_PER_MIN=5
SESSION_MAX_IDLE_MINUTES=30
```

### Skrip pnpm

- `pnpm dev` — jalankan dev server
- `pnpm prisma:generate` — generate client
- `pnpm prisma:migrate` — migrasi schema
- `pnpm db:seed` — seeding user & contoh data
- `pnpm build` — build produksi
- `pnpm start` — start server produksi
- `pnpm test` — unit test kalkulasi stok & guard auth

### Langkah Setup Lokal

1. `pnpm install`
2. Salin `.env.example` → `.env` dan isi nilai yang perlu.
3. `pnpm prisma:generate && pnpm prisma:migrate`
4. `pnpm db:seed`
5. `pnpm dev` lalu buka `http://localhost:3000` (login admin: `admin@local` / `ChangeMe123!`).

### Data Import (CSV)

Sediakan template CSV per modul (MRD, FILLING, ADJ_IN, ADJ_OUT, TW) dengan header standar:

- MRD: tanggal, mrdNo, itemCode, itemName, qty, warehouse, ket
- FILLING: tanggal, fillingNo, productName, itemCode, karton, qty, warehouse, ket
- ADJ_IN/OUT: tanggal, adNo, itemCode, itemName, qty, warehouse, ket
- TW: tanggal, twNo, itemCode, itemName, qty, warehouseFrom, warehouseTo, ket

Endpoint `POST /api/import/{module}` menerima CSV; lakukan preview & mapping kolom sebelum commit.

### Deploy

- **Vercel**: set `DATABASE_URL` (Postgres via Neon/Supabase), `NEXTAUTH_URL`, `NEXTAUTH_SECRET`. Jalankan `prisma migrate deploy` pada build.
- **Docker**: siapkan `Dockerfile` + `docker-compose.yml` (service app + postgres).
- Buat health check route `/api/health`.

### Observability

- Logging terstruktur (pino), error boundary, halaman 404/500 khusus.
- Capture audit log & impor gagal (simpan file original untuk forensic).

### Acceptance Criteria

- Fresh clone → bisa jalan lokal ≤10 menit mengikuti README.
- Deploy produksi dengan Postgres tanpa modifikasi kode > 3 baris (cukup ENV).
- Seeding menciptakan 3 role & contoh transaksi agar dashboard langsung tampil.

 
## Bonus Prompt Singkat

Build a Next.js + Prisma + SQLite Inventory Packaging app that mirrors these sheets: STOCK, BARANG MASUK (MRD), BARANG KELUAR (FILLING), ADJUST IN/OUT, TW. Implement movements (MRD, FILLING, ADJ_IN, ADJ_OUT, TW_IN, TW_OUT), stock formula opening + IN − OUT, opname vs system difference, CSV import/export, reports (day/week/month), role-based access, and pretty Tailwind + shadcn UI. Include seeds, tests, and README.
