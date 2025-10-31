# STOCK

## Setup & Run

1. `pnpm install` (or `npm install`)
2. Copy `.env.example` to `.env` and fill required values
3. `pnpm prisma:generate && pnpm prisma:migrate` (creates local SQLite DB)
4. `pnpm db:seed`
5. `pnpm dev` then open `http://localhost:3000` (login admin: `admin@local` / `ChangeMe123!`)

If you don’t use pnpm, npm equivalents:
- `npm install`
- `npm run prisma:generate && npm run prisma:migrate`
- `npm run db:seed`
- `npm run dev`

Generate a secure `NEXTAUTH_SECRET`:
- OpenSSL: `openssl rand -base64 32`
- Node: `node -e "console.log(require('crypto').randomBytes(32).toString('base64'))"`
