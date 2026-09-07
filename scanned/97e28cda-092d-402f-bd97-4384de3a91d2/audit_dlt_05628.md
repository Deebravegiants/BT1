# [?] execution/execmodule: fix data race between background prune and next FCU (#21697)

## Summary
Severity: Unknown
Chain: Ethereum
Component: erigontech/erigon
Published: 2026-06-12
Source: https://github.com/erigontech/erigon/commit/16b8af16d4fe8f98c35e689c2c2c2540333549f9
Type: security-commit

## Details
execution/execmodule: fix data race between background prune and next FCU (#21697)

## Symptom

The hive `engine-cancun` test **"Re-Org Back into Canonical Chain,
Depth=5"** intermittently fails against erigon with `INVALID` /
`"Invalid chain after execution"`: the forward re-org executes zero
blocks, the head stays behind, and the handler reports `bad forkchoice`.

## Root cause

With `FcuBackgroundPrune=true` (the node default), `updateForkChoice`
launched the prune in a goroutine but released the FCU semaphore without
waiting for it, so the prune's `Sync.RunPrune` raced the next FCU's
`Sync.RunLoop` on the same pipeline `Sync` — the next FCU could skip its
execution stage and leave the head un-advanced. The background-commit
path had a sibling hole: its goroutine released the semaphore with no
ordering against the FCU goroutine's cleanup defers
(`ResetPendingUpdates` on `e.currentContext`,
`forkValidator.ClearWithUnwind`), racing the next request's
`e.currentContext` writes once it acquired the semaphore.

## Fix

The semaphore is the sole gate for the pipeline `Sync` and the module's
FCU state, so it is now released only after both the FCU's cleanup and
the background work are done:

- The background prune/commit goroutine holds the semaphore until it
finishes and releases it on exit. The FCU response is still sent without
waiting; a concurrent op returns `ExecutionStatusBusy` → `SYNCING`
(retried by the CL), as background-commit already behaved.
- All FCU cleanup runs before the semaphore is handed to the goroutine:
overlay teardown (`PublishOverlay(nil)` + `SharedDomains.Close()`, which
also frees the SD RAM immediately instead of holding it through the
prune), then `ResetPendingUpdates` + `ClearWithUnwind` as a once-guarded
function invoked eagerly at the handoff. Any follow-up op that acquires
the semaphore observes fully-settled state.

_Trimmed to 38 lines — full report: https://github.com/erigontech/erigon/commit/16b8af16d4fe8f98c35e689c2c2c2540333549f9_
