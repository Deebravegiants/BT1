# [?] fix(op-supernode): resolve VirtualNode mutex deadlock during shutdown (#19680)

## Summary
Severity: Unknown
Chain: Optimism
Component: ethereum-optimism/optimism
Published: 2026-03-20
Source: https://github.com/ethereum-optimism/optimism/commit/a33079410dc92678aa3cbde43111d9e26513ba10
Type: security-commit

## Details
fix(op-supernode): resolve VirtualNode mutex deadlock during shutdown (#19680)

VirtualNode.Start() held v.mu while calling inner.Stop(), but
inner.Stop() drains the op-node event system which calls back into
SyncStatus() — which also needs v.mu. This created a deadlock during
test cleanup, causing TestChallengerRespondsToMultipleInvalidClaimsEOA
to hang for 2 hours in CI.

Fix: release v.mu before calling inner.Stop(). State transitions
(VNStateStopped, clear cancel) happen under the lock, then the local
`n` variable (already holding the inner node reference) is used for
Stop() outside the lock. Also use `n` for the Start() goroutine
launch for consistency — never access v.inner outside v.mu.

Additionally, add a 60s defensive timeout to Supernode.Stop()'s
wg.Wait() so cleanup always proceeds in bounded time.

Refs: ethereum-optimism/optimism#19563

Co-authored-by: Claude Opus 4.6 (1M context) <noreply@anthropic.com>
