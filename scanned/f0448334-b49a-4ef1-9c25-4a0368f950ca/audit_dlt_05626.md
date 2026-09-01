# [?] [SharovBot] fix: track MergeLoop goroutine in bgComponentsEg to prevent data race on shutdown (#22244)

## Summary
Severity: Unknown
Chain: Ethereum
Component: erigontech/erigon
Published: 2026-07-05
Source: https://github.com/erigontech/erigon/commit/deca4190ce499fec595f46befc679389ac9e4cee
Type: security-commit

## Details
[SharovBot] fix: track MergeLoop goroutine in bgComponentsEg to prevent data race on shutdown (#22244)

**[SharovBot]**

## Problem

A data race was detected in `TestImportClosesChaindataOnInitError`
(race-tests CI job, 2026-07-03):

```
WARNING: DATA RACE
Write at 0x00c0653acb90 by goroutine 321:
  github.com/erigontech/erigon/db/state.(*Aggregator).Close()
      db/state/aggregator.go:630

Previous read at 0x00c0653acb90 by goroutine 373:
  github.com/erigontech/erigon/db/state.(*Aggregator).MergeLoop()
      db/state/aggregator.go:1228
  github.com/erigontech/erigon/node/eth.New.func16()
      node/eth/backend.go:1133
```

## Context

PR #22203 (merged 2026-07-04) addressed this race by replacing
`sync.WaitGroup` with a `closingWaitGroup` latch in `Aggregator`, making
`MergeLoop`'s `TryAdd()` properly ordered against `Close()`'s
`BeginClose()+Wait()`.

## This PR

This PR provides an additional, complementary fix: track the MergeLoop
goroutine in `bgComponentsEg` so `Stop()` → `bgComponentsEg.Wait()`
explicitly waits for the MergeLoop goroutine to exit before
`chainDB.Close()` is called.

Without this, `bgComponentsEg.Wait()` in `Stop()` returns without
waiting for the MergeLoop goroutine (since it was launched as a bare `go

_Trimmed to 38 lines — full report: https://github.com/erigontech/erigon/commit/deca4190ce499fec595f46befc679389ac9e4cee_
