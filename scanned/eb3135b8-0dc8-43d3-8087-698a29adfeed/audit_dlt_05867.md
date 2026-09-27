# [?] fix(prover-autoscaler): fix deadlock in k8s event watcher (#4742)

## Summary
Severity: Unknown
Chain: zkSync
Component: matter-labs/zksync-era
Published: 2026-03-27
Source: https://github.com/matter-labs/zksync-era/commit/7feb7aafa339431a002283b0bf767d960fb7258f
Type: security-commit

## Details
fix(prover-autoscaler): fix deadlock in k8s event watcher (#4742)

## Summary
- Fix tokio::sync::Mutex deadlock in `k8s/watcher.rs` event handler that
caused agents to hang on startup when `FailedScheduling` events were
present
- Restore separate event handlers for `FailedScheduling` (pod-level
`out_of_resources`) and `FailedScaleUp` (namespace-level `scale_errors`)
to avoid double-counting errors that inflated `scale_errors` ~2x
- Each handler now acquires the mutex independently, eliminating the
deadlock

## Context
The deadlock was introduced in #4733 which merged two independent event
handlers into a single `if` block with two `self.cluster.lock().await`
calls. Since `tokio::sync::Mutex` is not reentrant, the second lock
blocked forever when the first was still held.

This caused agents on clusters with GPU exhaustion events
(`zksync-mainnet2` usc1 and `zksync-mainnet2-use1`) to become invisible
to the scaler (504 on `/cluster`), leaving 2 of 5 clusters unmanaged and
~1200 L4 GPU capacity unreachable.

## Test plan
- [x] Deployed and validated on all 5 mainnet2 clusters
- [x] Confirmed agents no longer deadlock on `FailedScheduling` events
- [x] Confirmed scaler sees all 5 clusters after fix
- [x] Confirmed `scale_errors` no longer double-counted

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-authored-by: Claude Opus 4.6 (1M context) <noreply@anthropic.com>
