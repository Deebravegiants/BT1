# [?] fix: prevent infinite loop and memory exhaustion in relayer reconnection

## Summary
Severity: Unknown
Chain: WalletConnect
Component: WalletConnect/walletconnect-monorepo
Published: 2026-03-26
Source: https://github.com/WalletConnect/walletconnect-monorepo/commit/e9eaeabfe814086f4aafff820767757e2d54c495
Type: security-commit

## Details
fix: prevent infinite loop and memory exhaustion in relayer reconnection

Fixes multiple interacting bugs in the relayer reconnect logic that
combine to create exponential growth of concurrent connect() calls
when the network is unreachable but isOnline() returns true.

- Eliminate `new Promise(async executor)` antipattern in connect() so
  subscriber.start() no longer runs as an unsupervised background task
  after WebSocket connection failure
- Move connectionAttemptInProgress reset to after the retry loop exits
  so restartTransport() stays blocked during all retry attempts
- Reset reconnectInProgress on early returns in onProviderDisconnect()
  to prevent the flag from getting permanently stuck
- Close old WebSocket in createProvider() before creating a new one
  to prevent leaked connections from accumulating on each retry
- Route toEstablishConnection() through transportOpen() for proper
  connectPromise serialization

Closes #7131

Made-with: Cursor
