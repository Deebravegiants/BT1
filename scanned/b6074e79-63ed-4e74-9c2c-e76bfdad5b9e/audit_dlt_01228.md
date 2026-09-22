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
`pe.rws.Close()` in `wait()` **after** `pe.waitWorkers()` returns. This
guarantees all worker goroutines have fully stopped before the result
queue channel is closed.

## Testing

- `go build ./...` passes
- Race condition confirmed by code inspection (consistent with CI
evidence)

Co-authored-by: SharovBot <bot@erigon.ci>
Co-authored-by: Giulio Rebuffo <giulio.rebuffo@gmail.com>
Co-authored-by: Andrew Ashikhmin <34320705+yperbasis@users.noreply.github.com>

### execution/stagedsync/exec3_parallel.go
```diff
@@ -958,7 +958,6 @@ func (pe *parallelExecutor) run(ctx context.Context) (context.Context, context.C
 	}
 
 	pe.execLoopGroup.Go(func() error {
-		defer pe.rws.Close()
 		defer pe.in.Release()
 		pe.resetWorkers(execLoopCtx, pe.rs, nil)
 		return pe.execLoop(execLoopCtx)
@@ -986,6 +985,7 @@ func (pe *parallelExecutor) wait(ctx context.Context) error {
 				return
 			}
 			pe.waitWorkers()
+			pe.rws.Close()
 		}
 		doneCh <- nil
 	}()
```
