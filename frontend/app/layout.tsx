import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Ballet Action Anticipation",
  description: "Predict next ballet actions using GRU neural network trained on AnnChor dataset",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
