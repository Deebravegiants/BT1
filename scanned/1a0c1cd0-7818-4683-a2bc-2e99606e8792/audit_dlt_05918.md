# [?] chore: fix security vulnerabilities and migrate rollup 2 to 4

## Summary
Severity: Unknown
Chain: WalletConnect
Component: WalletConnect/walletconnect-monorepo
Published: 2026-03-02
Source: https://github.com/WalletConnect/walletconnect-monorepo/commit/44d591d7a13898605707676089794ac487087eba
Type: security-commit

## Details
chore: fix security vulnerabilities and migrate rollup 2 to 4

Resolve all critical and high npm audit vulnerabilities:
- Update @aws-sdk/client-cloudwatch 3.971.0 -> 3.1000.0
- Update lerna 9.0.3 -> 9.0.5
- Add overrides for tar, axios, minimatch, @isaacs/brace-expansion,
  fast-xml-parser to patch transitive vulnerabilities

Migrate build tooling from Rollup 2 to Rollup 4:
- Update rollup 2.79.2 -> 4.59.0
- Update @rollup/plugin-commonjs 22 -> 29, plugin-node-resolve 13 -> 16,
  plugin-alias 5 -> 6, rollup-plugin-esbuild 4 -> 6
- Fix rollup-plugin-visualizer import (default -> named export)
- Add `with { type: "json" }` to JSON imports in per-package configs
- Add .js extensions to relative imports for Node.js ESM compatibility
- Replace __dirname with import.meta.url in ethereum-provider config

Made-with: Cursor
