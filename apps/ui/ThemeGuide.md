# Theme Guide Prompt

Buat halaman `apps/ui/ThemeGuide.tsx` di proyek Next.js Inventory Packaging untuk mendemonstrasikan komponen UI konsisten.

## Persyaratan

- Gunakan Tailwind + shadcn/ui + recharts.
- Tampilkan:
  - Variasi tipografi (h1, h2, body, caption) dengan Inter/Plus Jakarta Sans.
  - Palet warna status (OK/Warning/Error/Inactive) beserta contoh badge.
  - Card KPI contoh dengan sparkline dummy.
  - Tabel virtualized (10k rows dummy) dengan sticky header, resize, pin, sorting, multi-filter.
  - Form contoh (Input, Select, DatePicker) dengan validasi Zod + react-hook-form.
  - Dialog konfirmasi dan Toast demo.
  - Dark/Light toggle preview.
  - Charts line & bar (dummy data) dengan legend/tooltip.
- Dokumentasikan shortcut keyboard (/, i, n, g+s) dan interaksi penting.
- Sertakan link kembali ke dokumentasi UI dan design tokens.

## Tujuan

Memudahkan tim QA & dev untuk melihat implementasi gaya sebelum menyentuh modul produksi.
