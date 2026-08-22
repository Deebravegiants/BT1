# [?] chore: add npm overrides to fix security vulnerabilities

## Summary
Severity: Unknown
Chain: WalletConnect
Component: WalletConnect/walletconnect-monorepo
Published: 2026-01-28
Source: https://github.com/WalletConnect/walletconnect-monorepo/commit/4705628eff697aece9b104de4fe489ee82062cac
Type: security-commit

## Details
chore: add npm overrides to fix security vulnerabilities

Add overrides for transitive dependencies with known vulnerabilities:
- tar: ^7.5.7 (fixes arbitrary file overwrite via lerna)
- lodash: ^4.17.23 (fixes prototype pollution via wait-on)
- vite: ^7.3.1 (fixes server.fs.deny bypass via vitest)

This resolves 5 npm audit vulnerabilities (3 high, 2 moderate).
