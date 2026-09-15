# [?] fix: release RLock before waitChan in stopAndWaitImpl to prevent deadlock

## Summary
Severity: Unknown
Chain: Arbitrum
Component: OffchainLabs/nitro
Published: 2026-04-07
Source: https://github.com/OffchainLabs/nitro/commit/ca8bea37dc9fb8d6e71cc9e947e5d411bb8b6e6b
Type: security-commit

## Details
fix: release RLock before waitChan in stopAndWaitImpl to prevent deadlock

Also add stack traces to LaunchThreadSafe panic recovery and regression
tests for both changes.

Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>
