# [?] fix(pos-client): resolve flaky test race condition

## Summary
Severity: Unknown
Chain: WalletConnect
Component: WalletConnect/walletconnect-monorepo
Published: 2026-01-14
Source: https://github.com/WalletConnect/walletconnect-monorepo/commit/1cbe5bb2f5b10b2615e5c4a5c071c85f87c251da
Type: security-commit

## Details
fix(pos-client): resolve flaky test race condition

Register all event listeners before triggering createPaymentIntent
to prevent race conditions where events could fire before handlers
were attached. Also increased test timeout to 90s to accommodate
RPC polling delays in CI.
