# [?] fix(sync/statesync): panic-causing race between `<-quit` and `AddCode()` (#1284)

## Summary
Severity: Unknown
Chain: Avalanche
Component: ava-labs/avalanchego
Published: 2025-09-29
Source: https://github.com/ava-labs/avalanchego/commit/530ca18e0092153dc83226b835a837ddd6ad8637
Type: security-commit

## Details
fix(sync/statesync): panic-causing race between `<-quit` and `AddCode()` (#1284)

## Patch
### sync/statesync/code_queue.go
```diff
@@ -7,7 +7,6 @@ import (
 	"errors"
 	"fmt"
 	"sync"
-	"sync/atomic"
 
 	"github.com/ava-labs/libevm/common"
 	"github.com/ava-labs/libevm/core/rawdb"
@@ -16,16 +15,7 @@ import (
 	"github.com/ava-labs/coreth/plugin/evm/customrawdb"
 )
 
-// closeState models the lifecycle of the output channel.
-type closeState uint32
-
-const (
-	defaultQueueCapacity = 5000
-
-	closeStateOpen      closeState = 0
-	closeStateFinalized closeState = 1
-	closeStateQuit      closeState = 2
-)
+const defaultQueueCapacity = 5000
 
 var (
 	errFailedToAddCodeHashesToQueue = errors.New("failed to add code hashes to queue")
@@ -41,12 +31,14 @@ type CodeQueue struct {
 	db   ethdb.Database
 	quit <-chan struct{}
 
-	// Closed by [CodeQueue.Finalize] after the WaitGroup unblocks.
-	out       chan common.Hash
-	enqueueWG sync.WaitGroup
-
-	// Indicates why/if the output channel was closed.
-	closed atomicCloseState
+	// `in` and `out` MUST be the same channel. We need to be able to set `in`
+	// to nil after closing, to avoid a send-after-close, but
+	// [CodeQueue.CodeHashes] MUST NOT return a nil channel otherwise consumers
+	// will block permanently.
+	in            chan<- common.Hash // Invariant: open or nil, but never closed
+	out           <-chan common.Hash // Invariant: never nil
+	chanLock      sync.RWMutex
+	closeChanOnce sync.Once // See usage in [CodeQueue.closeOutChannelOnce]
 }
 
 // TODO: this will be migrated to using libevm's options pattern in a follow-up PR.
@@ -77,27 +69,26 @@ func NewCodeQueue(db ethdb.Database, quit <-chan struct{}, opts ...CodeQueueOpti
 		opt(&o)
 	}
 
+	ch := make(chan common.Hash, o.capacity)
 	q := &CodeQueue{
 		db:   db,
-		out:  make(chan common.Hash, o.capacity),
+		in:   ch,
+		out:  ch,
 		quit: quit,
 	}
 
 	if quit != nil {
 		// Close the output channel on early shutdown to unblock consumers.
 		go func() {
 			<-q.quit
-			// Transition to quit, wait for in-flight enqueues to finish,
-			// then close the output channel to signal consumers.
-			q.closed.markQuitAndClose(q.out, &q.enqueueWG)
+			q.closeChannelOnce()
 		}()
 	}
 
 	// Always initialize eagerly.
 	if err := q.init(); err != nil {
 		return nil, err
 	}
-
 	return q, nil
 }
 
@@ -106,6 +97,24 @@ func (q *CodeQueue) CodeHashes() <-chan common.Hash {
 	return q.out
 }
 
+func (q *CodeQueue) closeChannelOnce() bool {
+	var done bool
+	q.closeChanOnce.Do(func() {
+		q.chanLock.Lock()
+		defer q.chanLock.Unlock()
+
+		close(q.in)
+		// [CodeQueue.AddCode] takes a read lock before accessing `in` and we
+		// want it to block instead of allowing a send-after-close. Calling
+		// AddCode() after Finalize() isn't valid, and calling it after `quit`
+		// is closed will be picked up by the `select` so a nil alternative case
+		// is desirable.
+		q.in = nil
+		done = true
+	})
+	return done
+}
+
 // AddCode persists and enqueues new code hashes.
 // Persists idempotent "to-fetch" markers for all inputs and enqueues them as-is.
 // Returns errAddCodeAfterFinalize after a clean finalize and errFailedToAddCodeHashesToQueue on early quit.
@@ -114,15 +123,15 @@ func (q *CodeQueue) AddCode(codeHashes []common.Hash) error {
 		return nil
 	}
 
-	// If the queue has quit, do not attempt to send to the closed channel.
-	if q.closed.didQuit() {
-		return errFailedToAddCodeHashesToQueue
-	}
-
 	// Mark this enqueue as in-flight immediately so shutdown paths wait for us
 	// before closing the output channel.
-	q.enqueueWG.Add(1)
-	defer q.enqueueWG.Done()
+	q.chanLock.RLock()
+	defer q.chanLock.RUnlock()
+	if q.in == nil {
+		// Although this will happen anyway once the `select` is reached,
+		// bailing early avoids unnecessary database writes.
+		return errFailedToAddCodeHashesToQueue
+	}
 
 	batch := q.db.NewBatch()
 	// Persist all input hashes as to-fetch markers. Consumer will dedupe and skip
@@ -140,7 +149,7 @@ func (q *CodeQueue) AddCode(codeHashes []common.Hash) error {
 
 	for _, h := range codeHashes {
 		select {
-		case q.out <- h:
+		case q.in <- h: // guaranteed to be open or nil, but never closed
 		case <-q.quit:
 			return errFailedToAddCodeHashesToQueue
 		}
@@ -152,22 +161,9 @@ func (q *CodeQueue) AddCode(codeHashes []common.Hash) error {
 // Waits for in-flight enqueues to complete, then closes the output channel.
 // If the queue was already closed due to early quit, returns errFailedToFinalizeCodeQueue.
 func (q *CodeQueue) Finalize() error {
-	// Attempt to transition to finalized. If we win the CAS, wait for in-flight
-	// enqueues to complete and close the output channel. If we lose, return an
-	// error only if the queue has already quit - otherwise, it was already finalized.
-	if q.closed.canTransitionToFinalized() {
-		q.enqueueWG.Wait()
-		close(q.out)
-		return nil
-	}
-
-	// If CAS fails, check if the queue has already quit.
-	// NOTE: Callers who do not care about the error can ignore it.
-	if q.closed.didQuit() {
+	if !q.closeChannelOnce() {
 		return errFailedToFinalizeCodeQueue
 	}
-
-	// Already finalized - nothing to do.
 	return nil
 }
 
@@ -230,34 +226,3 @@ func recoverUnfetchedCodeHashes(db ethdb.Database) ([]common.Hash, error) {
 
 	return codeHashes, nil
 }
-
-// atomicCloseState provides a tiny typed wrapper around an atomic uint32.
-// It exposes enum-like operations to make intent explicit at call sites.
-type atomicCloseState struct {
-	v atomic.Uint32
-}
-
-func (s *atomicCloseState) get() closeState {
-	return closeState(s.v.Load())
-}
-
-func (s *atomicCloseState) transition(oldState, newState closeState) bool {
-	return s.v.CompareAndSwap(uint32(oldState), uint32(newState))
-}
-
-func (s *atomicCloseState) markQuitAndClose(out chan common.Hash, wg *sync.WaitGroup) {
-	if s.transition(closeStateOpen, closeStateQuit) {
-		// Ensure all in-flight enqueues have returned before closing the channel
-		// to avoid racing a send with a close.
-		wg.Wait()
-		close(out)
-	}
-}
-
-func (s *atomicCloseState) canTransitionToFinalized() bool {
-	return s.transition(closeStateOpen, closeStateFinalized)
-}
-
-func (s *atomicCloseState) didQuit() bool {
-	return s.get() == closeStateQuit
-}
```

### sync/statesync/code_queue_test.go
```diff
@@ -5,6 +5,7 @@ package statesync
 
 import (
 	"fmt"
+	"sync"
 	"testing"
 	"time"
 
@@ -106,6 +107,15 @@ func TestCodeQueue(t *testing.T) {
 					// Avoid leaking the internal goroutine
 					close(quit)
 				}
+
+				t.Run("after_quit_or_Finalize", func(t *testing.T) {
+					<-recvDone
+					ch := q.CodeHashes()
+					require.NotNilf(t, ch, "%T.CodeHashes()", q)
+					for range ch {
+						t.Fatalf("Unexpected receive on %T.CodeHashes()", q)
+					}
+				})
 			}()
 
 			var got []common.Hash
@@ -191,3 +201,46 @@ func TestCodeQueue_FinalizeWaitsForInflightAddCodeCalls(t *testing.T) {
 	require.NoError(t, <-addDone, "AddCode()")
 	<-finalized
 }
+
+func TestQuitAndAddCodeRace(t *testing.T) {
+	{
+		q := new(CodeQueue)
+		// Before the introduction of these fields, this test would panic.
+		_ = []any{&q.closeChanOnce, &q.chanLock}
+	}
+	for range 10_000 {
+		t.Run("", func(t *testing.T) {
+			t.Parallel()
+
+			quit := make(chan struct{})
+			q, err := NewCodeQueue(rawdb.NewMemoryDatabase(), quit)
+			require.NoError(t, err)
+
+			var ready, finished sync.WaitGroup
+			ready.Add(2)
+			finished.Add(2)
+			start := make(chan struct{})
+
+			go func() {
+				defer finished.Done()
+
+				ready.Done()
+				<-start
+				close(quit)
+			}()
+
+			go func() {
+				defer finished.Done()
+
+				in := []common.Hash{{}}
+				ready.Done()
+				<-start
+				q.AddCode(in)
+			}()
+
+			ready.Wait()
+			close(start)
+			finished.Wait()
+		})
+	}
+}
```
