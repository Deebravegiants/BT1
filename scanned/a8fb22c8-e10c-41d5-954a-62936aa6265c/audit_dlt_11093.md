# [?] op-supervisor: fix data race in test (#12824)

## Summary
Severity: Unknown
Chain: Boba
Component: bobanetwork/boba
Published: 2024-11-05
Source: https://github.com/bobanetwork/boba/commit/6fbf9db6d57158797127516bc231dad480918289
Type: security-commit

## Details
op-supervisor: fix data race in test (#12824)

* op-supervisor: fix data race in test

This test is flaky in CI. I believe it may be related to a data race: the `count` variable was being read from/written to across multiple threads which could lead to invalid data being read by the test. I verified that the data race was gone by running the test with `-race`.

* Use >= rather than exact numbers

## Patch
### op-supervisor/supervisor/backend/cross/worker_test.go
```diff
@@ -2,6 +2,7 @@ package cross
 
 import (
 	"context"
+	"sync/atomic"
 	"testing"
 	"time"
 
@@ -13,20 +14,20 @@ import (
 func TestWorker(t *testing.T) {
 	logger := testlog.Logger(t, log.LevelDebug)
 	t.Run("do work", func(t *testing.T) {
-		count := 0
+		var count int32
 		w := NewWorker(logger, func(ctx context.Context) error {
-			count++
+			atomic.AddInt32(&count, 1)
 			return nil
 		})
 		t.Cleanup(w.Close)
 		// when ProcessWork is called, the workFn is called once
 		require.NoError(t, w.ProcessWork())
-		require.Equal(t, 1, count)
+		require.EqualValues(t, 1, atomic.LoadInt32(&count))
 	})
 	t.Run("background worker", func(t *testing.T) {
-		count := 0
+		var count int32
 		w := NewWorker(logger, func(ctx context.Context) error {
-			count++
+			atomic.AddInt32(&count, 1)
 			return nil
 		})
 		t.Cleanup(w.Close)
@@ -36,13 +37,13 @@ func TestWorker(t *testing.T) {
 		// the count should increment once
 		w.StartBackground()
 		require.Eventually(t, func() bool {
-			return count == 1
+			return atomic.LoadInt32(&count) == 1
 		}, 2*time.Second, 100*time.Millisecond)
 	})
 	t.Run("background worker OnNewData", func(t *testing.T) {
-		count := 0
+		var count int32
 		w := NewWorker(logger, func(ctx context.Context) error {
-			count++
+			atomic.AddInt32(&count, 1)
 			return nil
 		})
 		t.Cleanup(w.Close)
@@ -52,55 +53,55 @@ func TestWorker(t *testing.T) {
 		// the count should increment once
 		w.StartBackground()
 		require.Eventually(t, func() bool {
-			return count == 1
+			return atomic.LoadInt32(&count) == 1
 		}, 2*time.Second, 100*time.Millisecond)
 		// when OnNewData is called, the worker runs again
 		w.OnNewData()
 		require.Eventually(t, func() bool {
-			return count == 2
+			return atomic.LoadInt32(&count) == 2
 		}, 2*time.Second, 100*time.Millisecond)
 		// and due to the long poll duration, the worker does not run again
 		require.Never(t, func() bool {
-			return count > 2
-		}, 10*time.Second, 100*time.Millisecond)
+			return atomic.LoadInt32(&count) > 2
+		}, time.Second, 100*time.Millisecond)
 	})
 	t.Run("background fast poll", func(t *testing.T) {
-		count := 0
+		var count int32
 		w := NewWorker(logger, func(ctx context.Context) error {
-			count++
+			atomic.AddInt32(&count, 1)
 			return nil
 		})
 		t.Cleanup(w.Close)
 		// set a long poll duration so the worker does not auto-run
 		w.pollDuration = 100 * time.Millisecond
 		// when StartBackground is called, the worker runs in the background
-		// the count should increment rapidly and reach 10 in 1 second
+		// the count should increment rapidly and reach at least 10 in 1 second
 		w.StartBackground()
 		require.Eventually(t, func() bool {
-			return count == 10
+			return atomic.LoadInt32(&count) >= 10
 		}, 2*time.Second, 100*time.Millisecond)
 	})
 	t.Run("close", func(t *testing.T) {
-		count := 0
+		var count int32
 		w := NewWorker(logger, func(ctx context.Context) error {
-			count++
+			atomic.AddInt32(&count, 1)
 			return nil
 		})
 		t.Cleanup(w.Close) // close on cleanup in case of early error
 		// set a long poll duration so the worker does not auto-run
 		w.pollDuration = 100 * time.Millisecond
 		// when StartBackground is called, the worker runs in the background
-		// the count should increment rapidly and reach 10 in 1 second
+		// the count should increment rapidly and reach at least 10 in 1 second
 		w.StartBackground()
 		require.Eventually(t, func() bool {
-			return count == 10
+			return atomic.LoadInt32(&count) >= 10
 		}, 10*time.Second, time.Second)
 		// once the worker is closed, it stops running
 		// and the count does not increment
 		w.Close()
-		stopCount := count
+		stopCount := atomic.LoadInt32(&count)
 		require.Never(t, func() bool {
-			return count != stopCount
-		}, 3*time.Second, 100*time.Millisecond)
+			return atomic.LoadInt32(&count) != stopCount
+		}, time.Second, 100*time.Millisecond)
 	})
 }
```
