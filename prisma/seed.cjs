/* eslint-disable no-console */
const { PrismaClient } = require('@prisma/client');
const bcrypt = require('bcrypt');
const prisma = new PrismaClient();

async function main() {
  // Basic warehouses
  const warehouses = await prisma.$transaction([
    prisma.warehouse.upsert({
      where: { code: 'VENUS' },
      update: {},
      create: { code: 'VENUS', name: 'VENUS' },
    }),
    prisma.warehouse.upsert({
      where: { code: 'PRODUKSI' },
      update: {},
      create: { code: 'PRODUKSI', name: 'Produksi' },
    }),
  ]);

  const pwd = await bcrypt.hash('ChangeMe123!', 10);

  // Default users
  await prisma.$transaction([
    prisma.user.upsert({
      where: { email: 'admin@local' },
      update: {},
      create: {
        name: 'Admin',
        email: 'admin@local',
        username: 'admin',
        passwordHash: pwd,
        role: 'ADMIN',
        isActive: true,
        mustChangePassword: true,
      },
    }),
    prisma.user.upsert({
      where: { email: 'operator@local' },
      update: {},
      create: {
        name: 'Operator',
        email: 'operator@local',
        username: 'operator',
        passwordHash: pwd,
        role: 'OPERATOR',
        isActive: true,
        mustChangePassword: true,
      },
    }),
    prisma.user.upsert({
      where: { email: 'viewer@local' },
      update: {},
      create: {
        name: 'Viewer',
        email: 'viewer@local',
        username: 'viewer',
        passwordHash: pwd,
        role: 'VIEWER',
        isActive: true,
        mustChangePassword: true,
      },
    }),
  ]);

  console.log('Seed complete:', { warehouses: warehouses.length });
}

main()
  .catch((e) => {
    console.error(e);
    process.exit(1);
  })
  .finally(async () => {
    await prisma.$disconnect();
  });

