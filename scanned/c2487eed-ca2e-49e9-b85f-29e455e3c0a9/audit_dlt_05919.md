# [?] fix: dynamically load WASM provider to avoid TextDecoder crash in React Native debug builds

## Summary
Severity: Unknown
Chain: WalletConnect
Component: WalletConnect/walletconnect-monorepo
Published: 2026-02-13
Source: https://github.com/WalletConnect/walletconnect-monorepo/commit/c1131bd8acd6fcaef2c465b14cd538117f0e2ab8
Type: security-commit

## Details
fix: dynamically load WASM provider to avoid TextDecoder crash in React Native debug builds

The WASM provider and its dependencies (brotli, yttrium binary) were
statically imported, causing TextDecoder-dependent code to load even in
React Native where it is unavailable in debug builds. The WASM module
is now loaded via dynamic import() only when not in a React Native
environment.

Co-authored-by: Cursor <cursoragent@cursor.com>
