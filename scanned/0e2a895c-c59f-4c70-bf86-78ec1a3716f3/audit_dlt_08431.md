# [?] Fixes TestParallelAbort nondeterministic failure #201 (#202)

## Summary
Severity: Unknown
Chain: Cosmos
Component: cometbft/cometbft
Published: 2018-04-23
Source: https://github.com/cometbft/cometbft/commit/8fa4211bbd2304d6f5b1307a8f1de9ec26f16434
Type: security-commit

## Details
Fixes TestParallelAbort nondeterministic failure #201 (#202)

## Patch
### common/async.go
```diff
@@ -32,7 +32,7 @@ type TaskResultSet struct {
 func newTaskResultSet(chz []TaskResultCh) *TaskResultSet {
 	return &TaskResultSet{
 		chz:     chz,
-		results: nil,
+		results: make([]taskResultOK, len(chz)),
 	}
 }
 
@@ -49,18 +49,20 @@ func (trs *TaskResultSet) LatestResult(index int) (TaskResult, bool) {
 }
 
 // NOTE: Not concurrency safe.
+// Writes results to trs.results without waiting for all tasks to complete.
 func (trs *TaskResultSet) Reap() *TaskResultSet {
-	if trs.results == nil {
-		trs.results = make([]taskResultOK, len(trs.chz))
-	}
 	for i := 0; i < len(trs.results); i++ {
 		var trch = trs.chz[i]
 		select {
-		case result := <-trch:
-			// Overwrite result.
-			trs.results[i] = taskResultOK{
-				TaskResult: result,
-				OK:         true,
+		case result, ok := <-trch:
+			if ok {
+				// Write result.
+				trs.results[i] = taskResultOK{
+					TaskResult: result,
+					OK:         true,
+				}
+			} else {
+				// We already wrote it.
 			}
 		default:
 			// Do nothing.
@@ -69,6 +71,27 @@ func (trs *TaskResultSet) Reap() *TaskResultSet {
 	return trs
 }
 
+// NOTE: Not concurrency safe.
+// Like Reap() but waits until all tasks have returned or panic'd.
+func (trs *TaskResultSet) Wait() *TaskResultSet {
+	for i := 0; i < len(trs.results); i++ {
+		var trch = trs.chz[i]
+		select {
+		case result, ok := <-trch:
+			if ok {
+				// Write result.
+				trs.results[i] = taskResultOK{
+					TaskResult: result,
+					OK:         true,
+				}
+			} else {
+				// We already wrote it.
+			}
+		}
+	}
+	return trs
+}
+
 // Returns the firstmost (by task index) error as
 // discovered by all previous Reap() calls.
 func (trs *TaskResultSet) FirstValue() interface{} {
@@ -116,7 +139,11 @@ func Parallel(tasks ...Task) (trs *TaskResultSet, ok bool) {
 			defer func() {
 				if pnk := recover(); pnk != nil {
 					atomic.AddInt32(numPanics, 1)
+					// Send panic to taskResultCh.
 					taskResultCh <- TaskResult{nil, ErrorWrap(pnk, "Panic in task")}
+					// Closing taskResultCh lets trs.Wait() work.
+					close(taskResultCh)
+					// Decrement waitgroup.
 					taskDoneCh <- false
 				}
 			}()
@@ -125,6 +152,8 @@ func Parallel(tasks ...Task) (trs *TaskResultSet, ok bool) {
 			// Send val/err to taskResultCh.
 			// NOTE: Below this line, nothing must panic/
 			taskResultCh <- TaskResult{val, err}
+			// Closing taskResultCh lets trs.Wait() work.
+			close(taskResultCh)
 			// Decrement waitgroup.
 			taskDoneCh <- abort
 		}(i, task, taskResultCh)
```

### common/async_test.go
```diff
@@ -91,10 +91,14 @@ func TestParallelAbort(t *testing.T) {
 	// Now let the last task (#3) complete after abort.
 	flow4 <- <-flow3
 
+	// Wait until all tasks have returned or panic'd.
+	taskResultSet.Wait()
+
 	// Verify task #0, #1, #2.
 	checkResult(t, taskResultSet, 0, 0, nil, nil)
 	checkResult(t, taskResultSet, 1, 1, errors.New("some error"), nil)
 	checkResult(t, taskResultSet, 2, 2, nil, nil)
+	checkResult(t, taskResultSet, 3, 3, nil, nil)
 }
 
 func TestParallelRecover(t *testing.T) {
```
