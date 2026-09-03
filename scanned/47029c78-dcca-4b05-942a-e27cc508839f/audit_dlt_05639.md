# [?] stagedsync, membatchwithdb: fix data race in parallel executor overlay (#20036)

## Summary
Severity: Unknown
Chain: Ethereum
Component: erigontech/erigon
Published: 2026-03-20
Source: https://github.com/erigontech/erigon/commit/5c8ab95f073a348a6f4d744e3489f1dc261222c6
Type: security-commit

## Details
stagedsync, membatchwithdb: fix data race in parallel executor overlay (#20036)

## Summary

- Fix data race between executor and apply goroutines in the parallel
executor's `MemoryMutation` overlay path
- Add `OverlayTemporalReadView` — a `kv.TemporalTx` implementation that
gives each goroutine its own MDBX RO tx while sharing the in-memory
overlay
- Add `ForEach` to `OverlayReadView` to prevent overlay bypass (same
class of bug as `ForAmount`)
- Fix silent `Seek` error swallowing in `ForEach`/`ForAmount` on both
`MemoryMutation` and `OverlayReadView`

## Problem

When `rwTx` is a `MemoryMutation` (the overlay path from #19882), the
parallel executor shared the same object between the executor and apply
goroutines:

```go
case kv.TemporalTx:
    asyncTx = applyTx  // both goroutines share same MdbxTx
```

Both goroutines create/close cursors on the shared underlying `MdbxTx`,
racing on `toCloseMap` (a plain `map[uint64]kv.Closer`) and mdbx cursor
internals. This caused 18+ race-test failures on `bal-devnet-3`,
triggered by `experimentalBAL: true` changing execution timing.

## Fix

`OverlayTemporalReadView` wraps a caller-provided `kv.TemporalTx`
(independent RO tx) and merges reads with the `MemoryMutation`'s shared
in-memory layer — same approach as the existing `OverlayReadView` used
by engine server getters.

```go
```

_Trimmed to 38 lines — full report: https://github.com/erigontech/erigon/commit/5c8ab95f073a348a6f4d744e3489f1dc261222c6_
