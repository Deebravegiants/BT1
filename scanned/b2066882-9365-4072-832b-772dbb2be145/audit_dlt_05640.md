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
- #19507 — early-return bypass of `<-LogCommitmentsDone`
(goroutine+channel removed entirely)

## Test plan

- [x] `make erigon` builds clean
- [x] `go test ./execution/stagedsync/... -short` passes
- [x] Validated on mainnet: node sailed through previously-stuck block
24,373,106 and continued syncing at 7-16 blk/s

🤖 Generated with [Claude Code](https://claude.com/claude-code)

---------

Co-authored-by: Mark Holt <erigon@dev-bm-e3-ethmainnet-n4.erigon.io>
Co-authored-by: Claude Opus 4.6 <noreply@anthropic.com>

### execution/exec/txtask.go
```diff
@@ -743,7 +743,7 @@ func (q *QueueWithRetry) RetryTxNumsList() (out []uint64) {
 }
 func (q *QueueWithRetry) Len() (l int) { return q.RetriesLen() + q.NewTasksLen() }
 
-// Add "new task" (which was never executed yet). May block internal channel is full.
+// Add "new task" (which was never executed yet). May block if internal channel is full.
 // Expecting already-ordered tasks.
 func (q *QueueWithRetry) Add(ctx context.Context, t Task) {
 	q.lock.Lock()
@@ -760,6 +760,26 @@ func (q *QueueWithRetry) Add(ctx context.Context, t Task) {
 	}
 }
 
+// TryAdd attempts to add a task without blocking. Returns true if the task was
+// enqueued, false if the channel is full or the queue is closed.
+func (q *QueueWithRetry) TryAdd(t Task) bool {
+	q.lock.Lock()
+	closed := q.closed
+	newTasks := q.newTasks
+	q.lock.Unlock()
+
+	if closed {
+		return false
+	}
+
+	select {
+	case newTasks <- t:
+		return true
+	default:
+		return false
+	}
+}
+
 // ReTry returns failed (conflicted) task. It's non-blocking method.
 // All failed tasks have higher priority than new one.
 // No limit on amount of txs added by this method.
```

### execution/stagedsync/exec3_parallel.go
```diff
@@ -701,7 +701,8 @@ func (pe *parallelExecutor) execLoop(ctx context.Context) (err error) {
 						fmt.Println(blockResult.BlockNum, "apply count", blockResult.ApplyCount)
 					}
 
-					blockExecutor.applyResults <- &txResult{
+					select {
+					case blockExecutor.applyResults <- &txResult{
 						blockNum:              blockResult.BlockNum,
 						txNum:                 blockResult.lastTxNum,
 						rules:                 result.Rules(),
@@ -710,14 +711,21 @@ func (pe *parallelExecutor) execLoop(ctx context.Context) (err error) {
 						traceFroms:            result.TraceFroms,
 						traceTos:              result.TraceTos,
 						cumulativeBlobGasUsed: blockExecutor.blobGasUsed,
+					}:
+					case <-ctx.Done():
+						return ctx.Err()
 					}
 				}
 
 				if !blockExecutor.execStarted.IsZero() {
 					pe.blockExecMetrics.Duration.Add(time.Since(blockExecutor.execStarted))
 					pe.blockExecMetrics.BlockCount.Add(1)
 				}
-				blockExecutor.applyResults <- blockResult
+				select {
+				case blockExecutor.applyResults <- blockResult:
+				case <-ctx.Done():
+					return ctx.Err()
+				}
 				pe.Lock()
 				delete(pe.blockExecutors, blockResult.BlockNum)
 				pe.Unlock()
@@ -1656,7 +1664,11 @@ func (be *blockExecutor) nextResult(ctx context.Context, pe *parallelExecutor, r
 				}
 			}
 
-			be.applyResults <- &applyResult
+			select {
+			case be.applyResults <- &applyResult:
+			case <-ctx.Done():
+				return nil, ctx.Err()
+			}
 		}
 	}
 
@@ -1748,9 +1760,8 @@ func (be *blockExecutor) scheduleExecution(ctx context.Context, pe *parallelExec
 	for i := 0; i < len(toExecute); i++ {
 		nextTx := toExecute[i]
 		execTask := be.tasks[nextTx]
-		if nextTx == maxValidated+1 {
-			be.skipCheck[nextTx] = true
-		} else {
+		isNextValidated := nextTx == maxValidated+1
+		if !isNextValidated {
 			txIndex := execTask.Version().TxIndex
 			if be.txIncarnations[nextTx] > 0 &&
 				(be.execAborted[nextTx] > 0 || be.execFailed[nextTx] > 0 || !be.blockIO.HasReads(txIndex) ||
@@ -1765,34 +1776,48 @@ func (be *blockExecutor) scheduleExecution(ctx context.Context, pe *parallelExec
 				be.execTasks.pushPending(nextTx)
 				continue
 			}
-			be.cntSpecExec++
 		}
 
-		if dbg.TraceTransactionIO && be.txIncarnations[nextTx] > 1 {
-			fmt.Println(be.blockNum, "EXEC", nextTx, be.txIncarnations[nextTx], "maxValidated", maxValidated, be.blockIO.HasReads(nextTx), "failed", be.execFailed[nextTx], "aborted", be.execAborted[nextTx])
+		tv := &taskVersion{
+			execTask:   execTask,
+			versionMap: be.versionMap,
+			profile:    be.profile,
+			stats:      be.stats,
+			statsMutex: &be.Mutex,
 		}
 
-		be.cntExec++
-
 		if incarnation := be.txIncarnations[nextTx]; incarnation == 0 {
-			pe.in.Add(ctx, &taskVersion{
-				execTask:   execTask,
-				version:    execTask.Version(),
-				versionMap: be.versionMap,
-				profile:    be.profile,
-				stats:      be.stats,
-				statsMutex: &be.Mutex})
+			tv.version = execTask.Version()
+			// Use TryAdd to avoid blocking the execLoop goroutine.
+			// If the input queue is full, return remaining tasks to
+			// pending — they will be scheduled on the next call to
+			// scheduleExecution (triggered by each processed result).
+			if !pe.in.TryAdd(tv) {
+				be.execTasks.pushPending(nextTx)
+				for j := i + 1; j < len(toExecute); j++ {
+					be.execTasks.pushPending(toExecute[j])
+				}
+				return
+			}
 		} else {
 			version := execTask.Version()
 			version.Incarnation = incarnation
-			pe.in.ReTry(&taskVersion{
-				execTask:   execTask,
-				version:    version,
-				versionMap: be.versionMap,
-				profile:    be.profile,
-				stats:      be.stats,
-				statsMutex: &be.Mutex})
+			tv.version = version
+			pe.in.ReTry(tv)
+		}
+
+		// Commit side-effects only after successful enqueue.
+		if isNextValidated {
+			be.skipCheck[nextTx] = true
+		} else {
+			be.cntSpecExec++
 		}
+
+		if dbg.TraceTransactionIO && be.txIncarnations[nextTx] > 1 {
+			fmt.Println(be.blockNum, "EXEC", nextTx, be.txIncarnations[nextTx], "maxValidated", maxValidated, be.blockIO.HasReads(nextTx), "failed", be.execFailed[nextTx], "aborted", be.execAborted[nextTx])
+		}
+
+		be.cntExec++
 	}
 }
 
```
