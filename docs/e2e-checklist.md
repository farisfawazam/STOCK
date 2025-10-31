# E2E Checklist – Inventory Packaging

1. **Authentication & Session**
   - Login gagal dengan password salah → tampilkan error & rate limit.
   - Login berhasil (admin/operator/viewer) → redirect dashboard; paksa ganti password pertama kali.
   - Session idle 30 menit → otomatis logout.
2. **Authorization**
   - Viewer hanya akses read-only; tombol CRUD disabled + toast.
   - Operator bisa CRUD transaksi tapi tidak akses /admin/users.
   - Admin akses penuh termasuk konfigurasi & audit log.
3. **CSV Import & Export**
   - Import valid MRD/FILLING/ADJ/TW → data masuk, audit log tersimpan.
   - Import invalid (header salah / qty <=0) → gagal dengan pesan & tidak commit.
   - Export CSV/Excel dari tabel & laporan.
4. **Stock Calculation**
   - Perhitungan stok mengikuti rumus opening + IN − OUT.
   - Selisih fisik vs sistem muncul dengan badge warna sesuai persen.
5. **Transfer Warehouse**
   - TW antar gudang mencatat asal/tujuan dan mengubah stok masing-masing.
6. **Audit & Logging**
   - Setiap perubahan CRUD tercatat dengan user, timestamp, diff.
   - Capture kegagalan impor (simpan file & error detail).
7. **UI/UX & Theme**
   - Light/Dark mode konsisten.
   - Keyboard shortcut (/ focus search, i import, n new, g s ke Stock).
   - Tabel >10k baris tetap responsif (virtualized).
   - Responsif mobile ≥320px.
8. **Reports & Dashboard**
   - KPI hari/bulan menampilkan angka sesuai data seed.
   - Grafik throughput harian bekerja dengan filter item.
9. **Security**
   - CSRF token wajib untuk POST/PUT/DELETE.
   - Helmet headers aktif; rate limiting login bekerja.
10. **Error Handling & Observability**
    - Error boundary halaman 404/500.
    - Health check `/api/health` mengembalikan status OK.
