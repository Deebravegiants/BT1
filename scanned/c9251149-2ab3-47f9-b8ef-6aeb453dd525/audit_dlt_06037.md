# [?] fix(factory): evict sender when an action panics during minting (#4921)

## Summary
Severity: Unknown
Chain: IoTeX
Component: iotexproject/iotex-core
Published: 2026-08-19
Source: https://github.com/iotexproject/iotex-core/commit/c2bab8df382eb88a5663f3341ec6897d3d38b71e
Type: security-commit

## Details
fix(factory): evict sender when an action panics during minting (#4921)

If a single pending action panics while runAction executes it during
minting, the panic previously unwound past the sender-eviction logic in
validateAndRun and was only caught by the mint goroutine's top-level
recover, discarding the whole draft without removing the action from
the pool. The same action would then be retried on every subsequent
mint attempt.

Recover the panic right around the single-action runAction call so it
is converted into an ordinary error and routed through the existing
default-error handling, which evicts the sender from the pool before
this draft is abandoned. This turns a potential run of repeated draft
failures into a one-time lost draft.

Co-authored-by: Claude Sonnet 5 <noreply@anthropic.com>
