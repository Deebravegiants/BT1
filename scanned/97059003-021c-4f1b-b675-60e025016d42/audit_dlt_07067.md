# [?] execution/exec: fix AwaitDrain infinite loop when map worker crashes (#19425)

## Summary
Severity: Unknown
Chain: Ethereum
Component: erigontech/erigon
Published: 2026-02-23
Source: https://github.com/erigontech/erigon/commit/fb5c418844c02098a7b187f4499da0791bd59f07
Type: security-commit

## Details
execution/exec: fix AwaitDrain infinite loop when map worker crashes (#19425)

**Bug:** When a map worker in `NewHistoricalTraceWorkers` crashes, the
reduce goroutine loops forever instead of exiting with an error. Closes
#18252.

---

`PriorityQueue.AwaitDrain` has a fast-path for when `resultCh == nil`
(the queue has been closed and its internal channel fully drained):

```go
if resultCh == nil {
    return q.Drain(ctx, none)  // never checks ctx
}
```

`Drain` in that branch also returns immediately without inspecting the
context. When a map worker crashes:

1. `out.Close()` is called — if the channel is already empty, `resultCh`
is set to `nil` immediately.
2. The errgroup cancels its shared context.
3. The reduce goroutine calls `AwaitDrain(cancelledCtx, …)` → hits the
`resultCh == nil` path → `Drain` returns `(false, nil)`.
4. The reduce loop sees no error and no `closed` signal, so it spins
forever — stuck waiting for a txnum that the crashed worker never
produced.

**Fix**

Check `ctx.Err()` before taking the fast-path:

```go
if resultCh == nil {
    if err := ctx.Err(); err != nil {
        return false, err
    }
    return q.Drain(ctx, none)
}
```

Once the errgroup cancels the context, the next `AwaitDrain` call
returns `context.Canceled`. This unblocks the reduce goroutine, and the
original map worker error surfaces correctly through `workers.Wait()`.

## Patch
### execution/exec/txtask.go
```diff
@@ -952,6 +952,9 @@ func (q *PriorityQueue[T]) AwaitDrain(ctx context.Context, waitTime time.Duratio
 	q.Unlock()
 
 	if resultCh == nil {
+		if err := ctx.Err(); err != nil {
+			return false, err
+		}
 		var none T
 		return q.Drain(ctx, none)
 	}
```

### execution/exec/txtask_test.go
```diff
@@ -0,0 +1,85 @@
+// Copyright 2024 The Erigon Authors
+// This file is part of Erigon.
+//
+// Erigon is free software: you can redistribute it and/or modify
+// it under the terms of the GNU Lesser General Public License as published by
+// the Free Software Foundation, either version 3 of the License, or
+// (at your option) any later version.
+//
+// Erigon is distributed in the hope that it will be useful,
+// but WITHOUT ANY WARRANTY; without even the implied warranty of
+// MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
+// GNU Lesser General Public License for more details.
+//
+// You should have received a copy of the GNU Lesser General Public License
+// along with Erigon. If not, see <http://www.gnu.org/licenses/>.
+
+package exec
+
+import (
+	"context"
+	"testing"
+	"time"
+
+	"github.com/stretchr/testify/require"
+)
+
+// TestAwaitDrainExitsOnContextCancel reproduces the infinite-loop described in
+// https://github.com/erigontech/erigon/issues/18252.
+//
+// Scenario: a map worker crashes after some results have already been moved from
+// the resultCh into the heap (e.g. txnums 5..N), but the result the reduce is
+// waiting for (txnum 0) was never produced.  The map goroutine calls
+// out.Close(), which nils resultCh (because the channel is empty at that
+// moment), and the errgroup cancels the shared context.
+//
+// Before the fix, AwaitDrain took the "resultCh == nil" fast-path and returned
+// (false, nil) without ever inspecting ctx, so the reduce loop never terminated.
+func TestAwaitDrainExitsOnContextCancel(t *testing.T) {
+	q := NewResultsQueue(10, 10)
+
+	// Simulate a worker that produced txnum=5 but the worker responsible for
+	// txnum=0 already panicked without producing a result.
+	bgCtx := context.Background()
+	err := q.Add(bgCtx, &TxResult{Task: &TxTask{TxNum: 5}})
+	require.NoError(t, err)
+
+	// Let AwaitDrain move the item from the channel into the heap.
+	_, err = q.AwaitDrain(bgCtx, 50*time.Millisecond)
+	require.NoError(t, err)
+	// resultCh is now empty (all items are in the heap).
+
+	// Simulate the map goroutine calling out.Close() after crashing.
+	// Because resultCh is empty, Close() closes and nils the channel immediately.
+	q.Close()
+
+	// Simulate the errgroup cancelling the context because the map goroutine
+	// returned an error.
+	cancelCtx, cancel := context.WithCancel(bgCtx)
+	cancel()
+
+	// The reduce loop must exit promptly; without the fix it spins forever.
+	done := make(chan error, 1)
+	go func() {
+		for {
+			closed, err := q.AwaitDrain(cancelCtx, 10*time.Millisecond)
+			if err != nil {
+				done <- err
+				return
+			}
+			if closed {
+				done <- nil
+				return
+			}
+			// Simulate processResults making no progress (txnum 0 missing).
+		}
+	}()
+
+	select {
+	case err := <-done:
+		require.Error(t, err, "reduce loop must exit with an error when ctx is cancelled")
+		require.ErrorIs(t, err, context.Canceled)
+	case <-time.After(3 * time.Second):
+		t.Fatal("AwaitDrain did not respect context cancellation – infinite loop detected (issue #18252)")
+	}
+}
```
