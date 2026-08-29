# [?] [SharovBot] execution: fix data race between PriorityQueue.Close() and worker Add() (#19889)

## Summary
Severity: Unknown
Chain: Ethereum
Component: erigontech/erigon
Published: 2026-03-19
Source: https://github.com/erigontech/erigon/commit/92265786c0486bf69ea4af1b9b5021fab06ae34e
Type: security-commit

## Details
[SharovBot] execution: fix data race between PriorityQueue.Close() and worker Add() (#19889)

## Problem

A data race was detected in CI between `PriorityQueue.Add()` (called by
worker goroutines) and `PriorityQueue.Close()` (called in the exec loop
goroutine):

```
WARNING: DATA RACE
Read at 0x00c004f306a0 by goroutine 432715:
  github.com/erigontech/erigon/execution/exec.(*PriorityQueue[...]).Add()
      execution/exec/txtask.go:980
  github.com/erigontech/erigon/execution/exec.(*Worker).Run()
      execution/exec/state.go:320

Previous write at 0x00c004f306a0 by goroutine 432716:
  github.com/erigontech/erigon/execution/exec.(*PriorityQueue[...]).Close()
      execution/exec/txtask.go:1101
  github.com/erigontech/erigon/execution/stagedsync.(*parallelExecutor).run.func1.deferwrap1()
      execution/stagedsync/exec3_parallel.go:906
```

CI:
https://github.com/erigontech/erigon/actions/runs/23085150487/job/67060750003

## Root Cause

`parallelExecutor.run()` was using `defer pe.rws.Close()` inside the
exec-loop goroutine. Worker goroutines run concurrently and call
`rws.Add()` which sends to a channel inside the queue. When the exec
loop exits, the deferred `Close()` closes that channel — but workers may
still be running and attempting to send, causing a
send-on-closed-channel race.

## Fix

Remove `defer pe.rws.Close()` from the exec-loop goroutine and call

_Trimmed to 38 lines — full report: https://github.com/erigontech/erigon/commit/92265786c0486bf69ea4af1b9b5021fab06ae34e_
