# [?] stagedsync: fix parallel executor deadlock in scheduleExecution (#19877)

## Summary
Severity: Unknown
Chain: Ethereum
Component: erigontech/erigon
Published: 2026-03-14
Source: https://github.com/erigontech/erigon/commit/6e4206ff205a431904290a4bac22f9a517846089
Type: security-commit

## Details
stagedsync: fix parallel executor deadlock in scheduleExecution (#19877)

## Summary

- **Fix deadlock**: `scheduleExecution` used blocking `pe.in.Add()`
which deadlocked when workers couldn't submit results to a full
`ResultsQueue`. The execLoop blocked in `scheduleExecution`, preventing
it from draining results — creating a circular dependency. Added
`QueueWithRetry.TryAdd()` (non-blocking); when the queue is full, tasks
stay pending and are retried on the next `scheduleExecution` call.

- **Replace commitment progress channel with callback**: The `chan
*CommitProgress` + goroutine pattern caused two data races (fixed by
workarounds in #19501 and #19507). Replaced with a
`func(*CommitProgress)` callback closure, eliminating both races at the
source and removing the `sync.Mutex` workaround.

**Remaining performance issue**: During commitment, the apply goroutine
cannot service `asyncTxChan`, stalling block preparation. This will be
resolved when #19875 (decouple commitment from apply goroutine) is
complete.

## Deadlock Analysis

Goroutine dump from a node stuck at block 24,373,106 for 66+ minutes
showed:

```
execLoop → scheduleExecution → pe.in.Add (blocks, queue full)
  → 13 workers blocked on PriorityQueue.Add (resultCh full)
    → resultCh not drained (execLoop stuck in scheduleExecution)
      → apply goroutine idle (no results flowing)
```

## Supersedes

- #19501 — `sync.Mutex` workaround for concurrent `LogCommitments` calls
(mutex removed, race eliminated)

_Trimmed to 38 lines — full report: https://github.com/erigontech/erigon/commit/6e4206ff205a431904290a4bac22f9a517846089_
