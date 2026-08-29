# [?] node, commitment: fix parallel exec deadlock on many-core machines (#22408)

## Summary
Severity: Unknown
Chain: Ethereum
Component: erigontech/erigon
Published: 2026-07-22
Source: https://github.com/erigontech/erigon/commit/4d6ef27f954fb17372f18c3a355e64ca2a3d4aad
Type: security-commit

## Details
node, commitment: fix parallel exec deadlock on many-core machines (#22408)

## Problem

On machines with ≥32 hardware threads (`runtime.NumCPU()`), the
engineapi tests deadlock deterministically when parallel execution is
enabled:

- `TestEngineApiUnwindRedoStateChurnPreservesState`
-
`TestEngineApiExecBlockBatchWithLenLtMaxReorgDepthAtTipThenUnwindShouldSucceed`

`engine_forkchoiceUpdated` stalls for the full 30s timeout, then fails
with `apply loop exited ... block(s) had tx-results without a
blockResult`.

Root cause: embedded/test nodes fall back to a hardcoded **32-slot**
read-tx semaphore in `node.OpenDatabase` (the CLI binary uses the
`--db.read.concurrency` default, `min(max(10, GOMAXPROCS*64), 9000)`, so
it is unaffected). Parallel exec spawns `NumCPU` workers, each lazily
opening a **long-lived read tx it keeps even while idle**. With `NumCPU
>= 32` the workers alone exhaust the semaphore: during unwind/redo,
`resetWorkers` rolls back the workers' txs, and on resume the freed
slots are re-acquired FIFO by whoever is queued — including commitment
warmup workers. A worker that has already claimed a task from the shared
queue can end up parked in `semaphore.Acquire` forever: its task is not
stealable, the other workers sit idle holding their slots, and the whole
pipeline (exec loop → apply loop → FCU) wedges. Commitment warmup
workers blocked in the same `Acquire` also held `Warmuper.CloseAndWait`
hostage, as their acquisition context is not cancellable from the
warmuper.

The defect has always been present: the 32-slot fallback dates back to
the original `node.OpenDatabase` code, and any embedded node with enough
exec workers could in principle exhaust it. It became much more likely
to trigger with #21240, which raised the parallel exec worker count from
`NumCPU/2` to `NumCPU`, lowering the deadlock threshold from ≥64 to ≥32
hardware threads — i.e. into the range of common development machines.

_Trimmed to 38 lines — full report: https://github.com/erigontech/erigon/commit/4d6ef27f954fb17372f18c3a355e64ca2a3d4aad_
