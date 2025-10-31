import './globals.css';
import type { ReactNode } from 'react';

export const metadata = {
  title: 'Inventory Packaging',
  description: 'Inventory Packaging App',
};

export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}

