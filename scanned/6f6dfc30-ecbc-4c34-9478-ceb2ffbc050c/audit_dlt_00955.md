# [?] fix(react-native-compat): resolve iOS Pay initialization race condition

## Summary
Severity: Unknown
Chain: WalletConnect
Component: WalletConnect/walletconnect-monorepo
Published: 2026-01-14
Source: https://github.com/WalletConnect/walletconnect-monorepo/commit/b257f509262ef171322d7c309a119ef97b592004
Type: security-commit

## Details
fix(react-native-compat): resolve iOS Pay initialization race condition

Route all API methods through the serial queue to ensure they wait
for initialization to complete. Previously, API methods called the
Swift bridge directly while initialize used dispatch_async, causing
intermittent "Pay client not initialized" errors.
