# [?] fix(sync): resolve shutdown deadlock in code queue during Firewood state sync (#5130)

## Summary
Severity: Unknown
Chain: Avalanche
Component: ava-labs/avalanchego
Published: 2026-04-14
Source: https://github.com/ava-labs/avalanchego/commit/6b9007d8495c95ed983f398f852a32d444cff123
Type: security-commit

## Details
fix(sync): resolve shutdown deadlock in code queue during Firewood state sync (#5130)

Signed-off-by: Tsvetan Dimitrov (tsvetan.dimitrov@avalabs.org)

## Patch
### graft/evm/go.mod
```diff
@@ -10,7 +10,6 @@ require (
 	github.com/ava-labs/libevm v1.13.14-0.4.0.rc.2
 	github.com/davecgh/go-spew v1.1.2-0.20180830191138-d8f796af33cc
 	github.com/deckarep/golang-set/v2 v2.1.0
-	github.com/google/go-cmp v0.7.0
 	github.com/gorilla/rpc v1.2.0
 	github.com/gorilla/websocket v1.5.0
 	github.com/holiman/bloomfilter/v2 v2.0.3
```

### graft/evm/sync/code/BUILD.bazel
```diff
@@ -44,8 +44,8 @@ graft_go_test(
         "@com_github_ava_labs_libevm//crypto",
         "@com_github_ava_labs_libevm//ethdb",
         "@com_github_ava_labs_libevm//ethdb/memorydb",
-        "@com_github_google_go_cmp//cmp",
         "@com_github_stretchr_testify//require",
+        "@org_golang_x_sync//errgroup",
         "@org_uber_go_goleak//:goleak",
     ],
 )
```

### graft/evm/sync/code/queue.go
```diff
@@ -23,27 +23,30 @@ const defaultQueueCapacity = 5000
 var (
 	_ types.Finalizer = (*Queue)(nil)
 
-	ErrFailedToAddCodeHashesToQueue = errors.New("failed to add code hashes to queue")
-	errFailedToFinalizeCodeQueue    = errors.New("failed to finalize code queue")
+	ErrQueueClosed = errors.New("code queue is closed")
 )
 
-// Queue implements the producer side of code fetching.
-// It accepts code hashes, persists durable "to-fetch" markers (idempotent per hash),
-// and enqueues the hashes as-is onto an internal channel consumed by the code syncer.
-// The queue does not perform in-memory deduplication or local-code checks - that is
-// the responsibility of the consumer.
+// Queue is a fan-in/fan-out bridge between code hash producers (leaf sync workers)
+// and the code syncer consumer. Producers call [Queue.AddCode] which persists durable
+// disk markers and appends hashes to an internal queue. A single background goroutine
+// forwards them to the output channel. [Queue.AddCode] never blocks the caller.
+//
+// Deduplication and local-code checks are the consumer's responsibility.
 type Queue struct {
-	db   ethdb.Database
-	quit <-chan struct{}
-
-	// `in` and `out` MUST be the same channel. We need to be able to set `in`
-	// to nil after closing, to avoid a send-after-close, but
-	// [CodeQueue.CodeHashes] MUST NOT return a nil channel otherwise consumers
-	// will block permanently.
-	in            chan<- common.Hash // Invariant: open or nil, but never closed
-	out           <-chan common.Hash // Invariant: never nil
-	chanLock      sync.RWMutex
-	closeChanOnce sync.Once // See usage in [CodeQueue.closeOutChannelOnce]
+	db  ethdb.Database
+	out chan common.Hash // output to consumer
+
+	cancel      context.CancelFunc
+	done        <-chan struct{} // cancelled on Shutdown
+	forwardDone chan struct{}   // closed when forward() exits
+
+	closeMu     sync.RWMutex
+	closeInOnce sync.Once
+	closed      bool
+
+	pendingMu sync.Mutex
+	pending   []common.Hash
+	in        chan struct{} // producer signal, buffered to 1
 
 	capacity int
 }
@@ -59,85 +62,60 @@ func WithCapacity(n int) QueueOption {
 	})
 }
 
-// NewQueue creates a new code queue applying optional functional options.
-// The `quit` channel, if non-nil, MUST eventually be closed to avoid leaking a
-// goroutine.
-func NewQueue(db ethdb.Database, quit <-chan struct{}, opts ...QueueOption) (*Queue, error) {
-	// Create with defaults, then apply options.
+// NewQueue creates a code queue. Call [Queue.Finalize] for normal completion
+// or [Queue.Shutdown] for cancellation. Both are safe to call in any order.
+func NewQueue(db ethdb.Database, opts ...QueueOption) (*Queue, error) {
 	q := &Queue{
 		db:       db,
-		quit:     quit,
 		capacity: defaultQueueCapacity,
 	}
 	options.ApplyTo(q, opts...)
 
-	// Initialize the channel with the (potentially overridden) capacity.
-	ch := make(chan common.Hash, q.capacity)
-	q.in = ch
-	q.out = ch
+	q.out = make(chan common.Hash, q.capacity)
+	q.in = make(chan struct{}, 1)
+	q.forwardDone = make(chan struct{})
 
-	if quit != nil {
-		// Close the output channel on early shutdown to unblock consumers.
-		go func() {
-			<-q.quit
-			q.closeChannelOnce()
-		}()
-	}
+	ctx, cancel := context.WithCancel(context.Background())
+	q.cancel = cancel
+	q.done = ctx.Done()
+
+	go q.forward()
 
-	// Always initialize eagerly.
 	if err := q.init(); err != nil {
+		cancel()
+		<-q.forwardDone
 		return nil, err
 	}
 	return q, nil
 }
 
-// CodeHashes returns the receive-only channel of code hashes to consume.
+// CodeHashes returns the receive-only channel consumed by the code syncer.
 func (q *Queue) CodeHashes() <-chan common.Hash {
 	return q.out
 }
 
-func (q *Queue) closeChannelOnce() bool {
-	var done bool
-	q.closeChanOnce.Do(func() {
-		q.chanLock.Lock()
-		defer q.chanLock.Unlock()
-
-		close(q.in)
-		// [CodeQueue.AddCode] takes a read lock before accessing `in` and we
-		// want it to block instead of allowing a send-after-close. Calling
-		// AddCode() after Finalize() isn't valid, and calling it after `quit`
-		// is closed will be picked up by the `select` so a nil alternative case
-		// is desirable.
-		q.in = nil
-		done = true
-	})
-	return done
-}
-
-// AddCode persists and enqueues new code hashes.
-// Persists idempotent "to-fetch" markers for all inputs and enqueues them as-is.
-// Returns errAddCodeAfterFinalize after a clean finalize and errFailedToAddCodeHashesToQueue on early quit.
+// AddCode persists code hashes as durable disk markers and enqueues them
+// for the forwarder goroutine. Never blocks the caller.
+// Returns [ErrQueueClosed] after [Queue.Shutdown] or [Queue.Finalize].
 func (q *Queue) AddCode(ctx context.Context, codeHashes []common.Hash) error {
 	if len(codeHashes) == 0 {
 		return nil
 	}
 
-	// Mark this enqueue as in-flight immediately so shutdown paths wait for us
-	// before closing the output channel.
-	q.chanLock.RLock()
-	defer q.chanLock.RUnlock()
-	if q.in == nil {
-		// Although this will happen anyway once the `select` is reached,
-		// bailing early avoids unnecessary database writes.
-		return ErrFailedToAddCodeHashesToQueue
+	if err := ctx.Err(); err != nil {
+		return err
 	}
 
+	q.closeMu.RLock()
+	defer q.closeMu.RUnlock()
+
+	if q.closed {
+		return ErrQueueClosed
+	}
+
+	// Persist to-fetch markers keyed by code hash (idempotent overwrites).
+	// The consumer deletes markers after fetching or if code is already present.
 	batch := q.db.NewBatch()
-	// Persist all input hashes as to-fetch markers. Consumer will dedupe and skip
-	// already-present code. Persisting all enables consumer-side retry.
-	// Note: markers are keyed by code hash, so repeated persists overwrite the same
-	// key rather than growing DB usage. The consumer deletes the marker after
-	// fulfilling the request (or when it detects code is already present).
 	for _, codeHash := range codeHashes {
 		if err := customrawdb.WriteCodeToFetch(batch, codeHash); err != nil {
 			return fmt.Errorf("failed to write code to fetch marker: %w", err)
@@ -148,49 +126,118 @@ func (q *Queue) AddCode(ctx context.Context, codeHashes []common.Hash) error {
 		return fmt.Errorf("failed to write batch of code to fetch markers due to: %w", err)
 	}
 
-	for _, h := range codeHashes {
-		select {
-		case q.in <- h: // guaranteed to be open or nil, but never closed
-		case <-q.quit:
-			return ErrFailedToAddCodeHashesToQueue
-		case <-ctx.Done():
-			return ctx.Err()
-		}
+	q.pendingMu.Lock()
+	q.pending = append(q.pending, codeHashes...)
+	q.pendingMu.Unlock()
+
+	// Signal coalescing: skip if the forwarder is already notified.
+	select {
+	case q.in <- struct{}{}:
+	default:
 	}
+
 	return nil
 }
 
-// Finalize signals that no further code hashes will be added.
-// Waits for in-flight enqueues to complete, then closes the output channel.
-// If the queue was already closed due to early quit, returns errFailedToFinalizeCodeQueue.
+// Finalize waits for all pending hashes to be sent, then closes out.
+// Blocks if no consumer is draining [Queue.CodeHashes]. Idempotent with [Queue.Shutdown].
 func (q *Queue) Finalize() error {
-	if !q.closeChannelOnce() {
-		return errFailedToFinalizeCodeQueue
-	}
+	q.stop(false)
 	return nil
 }
 
-// init enqueues any persisted code markers found on disk.
+// Shutdown cancels the forwarder, waits for exit, then closes out.
+// Unsent hashes are safe as disk markers and will be recovered on restart.
+// Idempotent with [Queue.Finalize].
+func (q *Queue) Shutdown() {
+	q.stop(true)
+}
+
+func (q *Queue) markClosed() {
+	q.closeMu.Lock()
+	defer q.closeMu.Unlock()
+	q.closed = true
+}
+
+// stop waits for in-flight AddCode calls (via write lock), optionally cancels
+// the forwarder, signals no more work, and waits for the forwarder to exit.
+func (q *Queue) stop(shouldCancel bool) {
+	q.markClosed()
+	if shouldCancel {
+		q.cancel()
+	}
+	q.closeInOnce.Do(func() {
+		close(q.in)
+	})
+	<-q.forwardDone
+}
+
+// forward moves hashes from pending to `q.out`. It owns `q.out` and closes it on exit.
+func (q *Queue) forward() {
+	defer func() {
+		close(q.out)
+		close(q.forwardDone)
+	}()
+	for {
+		select {
+		case _, ok := <-q.in:
+			stop := q.drainPending()
+			if !ok || stop {
+				return
+			}
+		case <-q.done:
+			return
+		}
+	}
+}
+
+// drainPending sends all accumulated pending hashes to out.
+// Returns true if cancelled via done.
+func (q *Queue) drainPending() bool {
+	takePending := func() []common.Hash {
+		q.pendingMu.Lock()
+		defer q.pendingMu.Unlock()
+		batch := q.pending
+		q.pending = nil
+		return batch
+	}
+
+	for {
+		batch := takePending()
+		if len(batch) == 0 {
+			return false
+		}
+
+		for _, h := range batch {
+			select {
+			case q.out <- h:
+			case <-q.done:
+				return true
+			}
+		}
+	}
+}
+
+// init recovers persisted code markers from disk and re-enqueues them.
+// AddCode will re-persist the same markers, which is a harmless redundancy
+// that only happens on resume after restart.
 func (q *Queue) init() error {
-	// Recover any persisted code markers and enqueue them.
-	// Note: dbCodeHashes are already present as "to-fetch" markers. addCode will
-	// re-persist them, which is a trivial redundancy that happens only on resume
-	// (e.g., after restart). We accept this to keep the code simple.
 	dbCodeHashes, err := recoverUnfetchedCodeHashes(q.db)
 	if err != nil {
 		return fmt.Errorf("unable to recover previous sync state: %w", err)
 	}
-	// Use context.Background() since init() runs during construction before sync starts.
-	// The channel is empty, so sends won't block. Shutdown is handled via q.quit in AddCode.
+
+	// context.Background: init runs during construction before sync starts,
+	// the queue is not closed yet so AddCode will always succeed.
 	if err := q.AddCode(context.Background(), dbCodeHashes); err != nil {
 		return fmt.Errorf("unable to resume previous sync: %w", err)
 	}
 
 	return nil
 }
 
-// recoverUnfetchedCodeHashes cleans out any codeToFetch markers from the database that are no longer
-// needed and returns any outstanding markers to the queue.
+// recoverUnfetchedCodeHashes returns persisted code markers that still need fetching
+// and deletes markers for code already present locally.
 func recoverUnfetchedCodeHashes(db ethdb.Database) ([]common.Hash, error) {
 	it := customrawdb.NewCodeToFetchIterator(db)
 	defer it.Release()
@@ -201,7 +248,6 @@ func recoverUnfetchedCodeHashes(db ethdb.Database) ([]common.Hash, error) {
 	for it.Next() {
 		codeHash := common.BytesToHash(it.Key()[len(customrawdb.CodeToFetchPrefix):])
 
-		// If we already have the codeHash, delete the marker from the database and continue.
 		if !rawdb.HasCode(db, codeHash) {
 			codeHashes = append(codeHashes, codeHash)
 			continue
@@ -214,7 +260,6 @@ func recoverUnfetchedCodeHashes(db ethdb.Database) ([]common.Hash, error) {
 			continue
 		}
 
-		// Write the batch to disk if it has reached the ideal batch size.
 		if err := batch.Write(); err != nil {
 			return nil, fmt.Errorf("failed to write batch removing old code markers: %w", err)
 		}
```

### graft/evm/sync/code/queue_test.go
```diff
@@ -4,36 +4,39 @@
 package code
 
 import (
-	"fmt"
+	"strconv"
 	"sync"
 	"testing"
-	"time"
 
 	"github.com/ava-labs/libevm/common"
 	"github.com/ava-labs/libevm/core/rawdb"
 	"github.com/ava-labs/libevm/crypto"
-	"github.com/google/go-cmp/cmp"
 	"github.com/stretchr/testify/require"
 	"go.uber.org/goleak"
+	"golang.org/x/sync/errgroup"
 
 	"github.com/ava-labs/avalanchego/utils/set"
 	"github.com/ava-labs/avalanchego/vms/evm/sync/customrawdb"
 )
 
+func TestMain(m *testing.M) {
+	goleak.VerifyTestMain(m, goleak.IgnoreCurrent())
+}
+
 func TestCodeQueue(t *testing.T) {
 	hashes := make([]common.Hash, 256)
 	for i := range hashes {
 		hashes[i] = crypto.Keccak256Hash([]byte{byte(i)})
 	}
 
 	tests := []struct {
-		name                  string
-		alreadyToFetch        set.Set[common.Hash]
-		alreadyHave           map[common.Hash][]byte
-		addCode               [][]common.Hash
-		want                  []common.Hash
-		quitInsteadOfFinalize bool
-		addCodeAfter          []common.Hash
+		name                      string
+		alreadyToFetch            set.Set[common.Hash]
+		alreadyHave               map[common.Hash][]byte
+		addCode                   [][]common.Hash
+		want                      []common.Hash
+		shutdownInsteadOfFinalize bool
+		addCodeAfter              []common.Hash
 	}{
 		{
 			name: "multiple_calls_to_addcode",
@@ -63,23 +66,21 @@ func TestCodeQueue(t *testing.T) {
 		{
 			name:        "deduplication_in_consumer",
 			alreadyHave: map[common.Hash][]byte{hashes[42]: {42}},
-			// It is the consumer's responsibility, not the queue's, to check
-			// the database.
+			// Deduplication is the consumer's responsibility, not the queue's.
 			addCode: [][]common.Hash{{hashes[42]}},
 			want:    []common.Hash{hashes[42]},
 		},
 		{
-			name:                  "external_shutdown_via_quit_channel",
-			quitInsteadOfFinalize: true,
-			addCodeAfter:          []common.Hash{hashes[11]},
-			want:                  nil,
+			name:                      "external_shutdown",
+			shutdownInsteadOfFinalize: true,
+			addCodeAfter:              []common.Hash{hashes[11]},
+			want:                      nil,
 		},
 	}
 
 	for _, tt := range tests {
 		t.Run(tt.name, func(t *testing.T) {
 			t.Parallel()
-			defer goleak.VerifyNone(t, goleak.IgnoreCurrent())
 
 			db := rawdb.NewMemoryDatabase()
 			for hash, code := range tt.alreadyHave {
@@ -89,162 +90,199 @@ func TestCodeQueue(t *testing.T) {
 				require.NoError(t, customrawdb.WriteCodeToFetch(db, hash))
 			}
 
-			quit := make(chan struct{})
-			q, err := NewQueue(db, quit)
-			require.NoError(t, err, "NewCodeQueue()")
-
-			recvDone := make(chan struct{})
-			go func() {
-				for _, add := range tt.addCode {
-					require.NoErrorf(t, q.AddCode(t.Context(), add), "%T.AddCode(%v)", q, add)
-				}
+			q, err := NewQueue(db)
+			require.NoError(t, err, "NewQueue()")
 
-				if tt.quitInsteadOfFinalize {
-					close(quit)
-					<-recvDone
-					err := q.AddCode(t.Context(), tt.addCodeAfter)
-					require.ErrorIsf(t, err, ErrFailedToAddCodeHashesToQueue, "%T.AddCode() after `quit` channel closed", q)
-				} else {
-					require.NoErrorf(t, q.Finalize(), "%T.Finalize()", q)
-					// Avoid leaking the internal goroutine
-					close(quit)
-				}
+			// AddCode is non-blocking, safe to call on main goroutine.
+			for _, add := range tt.addCode {
+				require.NoError(t, q.AddCode(t.Context(), add))
+			}
 
-				t.Run("after_quit_or_Finalize", func(t *testing.T) {
-					<-recvDone
-					ch := q.CodeHashes()
-					require.NotNilf(t, ch, "%T.CodeHashes()", q)
-					for range ch {
-						t.Fatalf("Unexpected receive: %T.CodeHashes()", q)
-					}
-				})
-			}()
-
-			var got []common.Hash
-			for h := range q.CodeHashes() {
-				got = append(got, h)
+			// Consumer runs in background, collects values.
+			got := drainAsync(q.CodeHashes())
+
+			if tt.shutdownInsteadOfFinalize {
+				q.Shutdown()
+				<-got.done
+				err := q.AddCode(t.Context(), tt.addCodeAfter)
+				require.ErrorIs(t, err, ErrQueueClosed)
+			} else {
+				require.NoError(t, q.Finalize())
+				<-got.done
 			}
-			close(recvDone)
-			require.Emptyf(t, cmp.Diff(tt.want, got), "Diff (-want +got) of values received from %T.CodeHashes()", q)
+
+			// Cross-batch ordering is not guaranteed because separate
+			// goroutines race. Compare as sets.
+			require.ElementsMatchf(t, tt.want, got.hashes, "values received from %T.CodeHashes()", q)
 
 			t.Run("restart_with_same_db", func(t *testing.T) {
-				q, err := NewQueue(db, nil, WithCapacity(len(tt.want)))
-				require.NoError(t, err, "NewCodeQueue([reused db])")
-				require.NoErrorf(t, q.Finalize(), "%T.Finalize() immediately after creation", q)
+				q, err := NewQueue(db, WithCapacity(len(tt.want)))
+				require.NoError(t, err, "NewQueue([reused db])")
+				require.NoError(t, q.Finalize())
 
-				got := make(set.Set[common.Hash])
-				for h := range q.CodeHashes() {
-					got.Add(h)
-				}
+				restart := drainAsync(q.CodeHashes())
+				<-restart.done
 
-				// Unlike newly added code hashes, the initialisation function
-				// checks for existing code when recovering from the database.
-				// The order can't be maintained.
+				// init checks for existing code when recovering from disk,
+				// so already-present hashes are excluded.
 				want := set.Of(tt.want...)
 				for hash := range tt.alreadyHave {
 					want.Remove(hash)
 				}
 
-				require.ElementsMatchf(t, want.List(), got.List(), "All received on %T.CodeHashes() after restart", q)
+				restartSet := make(set.Set[common.Hash])
+				for _, h := range restart.hashes {
+					restartSet.Add(h)
+				}
+				require.ElementsMatchf(t, want.List(), restartSet.List(), "All received on %T.CodeHashes() after restart", q)
 			})
 		})
 	}
 }
 
-// Test that Finalize waits for in-flight AddCode calls to complete before closing the channel.
-func TestCodeQueue_FinalizeWaitsForInflightAddCodeCalls(t *testing.T) {
-	const capacity = 1
+// TestFinalizeFlushesAllHashes verifies that AddCode is non-blocking and
+// Finalize waits for the forwarder goroutine to drain all pending hashes.
+func TestFinalizeFlushesAllHashes(t *testing.T) {
+	const (
+		capacity  = 1
+		numHashes = 50
+	)
 	db := rawdb.NewMemoryDatabase()
-	q, err := NewQueue(db, nil, WithCapacity(capacity))
-	require.NoError(t, err, "NewCodeQueue()")
+	q, err := NewQueue(db, WithCapacity(capacity))
+	require.NoError(t, err)
 
-	// Prepare multiple distinct hashes to exceed the buffer and cause AddCode to block on enqueue.
-	hashes := make([]common.Hash, capacity+2)
-	for i := range hashes {
-		hashes[i] = crypto.Keccak256Hash([]byte(fmt.Sprintf("code-%d", i)))
-	}
+	hashes := makeHashes(numHashes)
 
-	addDone := make(chan error, 1)
-	go func() {
-		addDone <- q.AddCode(t.Context(), hashes)
-	}()
+	// AddCode returns immediately despite capacity=1.
+	require.NoError(t, q.AddCode(t.Context(), hashes))
 
-	// Read the first enqueued hash to ensure AddCode is actively enqueuing and will block on the next send.
-	var got []common.Hash
-	got = append(got, <-q.CodeHashes())
+	// Consumer in background, Finalize on main goroutine.
+	got := drainAsync(q.CodeHashes())
+	require.NoError(t, q.Finalize())
+	<-got.done
 
-	// Call Finalize concurrently - it should block until AddCode returns.
-	finalized := make(chan struct{})
-	go func() {
-		require.NoError(t, q.Finalize(), "Finalize()")
-		close(finalized)
-	}()
+	require.Equal(t, hashes, got.hashes, "all hashes received in batch order")
+}
 
-	// Finalize should not complete yet because AddCode is still enqueuing (buffer=1 and we haven't drained).
-	select {
-	case <-finalized:
-		t.Fatal("Finalize returned before in-flight AddCode completed")
-	case <-addDone:
-		t.Fatal("AddCode returned before enqueuing all hashes")
-	case <-time.After(100 * time.Millisecond):
-		// TODO(powerslider) once we're using Go 1.25 and the `synctest` package
-		// is generally available, use it here instead of an arbitrary amount of
-		// time. Without this, we have no way to guarantee that Finalize() and
-		// AddCode() are actually blocked.
-	}
+// TestShutdownUnblocksGoroutines verifies that Shutdown cancels the stuck
+// forwarder goroutine, is idempotent with Finalize, and rejects later AddCode calls.
+func TestShutdownUnblocksGoroutines(t *testing.T) {
+	const capacity = 1
+	db := rawdb.NewMemoryDatabase()
+	q, err := NewQueue(db, WithCapacity(capacity))
+	require.NoError(t, err)
+
+	// Goroutines will block on send because capacity=1 and no consumer.
+	require.NoError(t, q.AddCode(t.Context(), makeHashes(100)))
+
+	q.Shutdown()
 
-	// Drain remaining enqueued hashes; this will unblock AddCode so it can finish.
-	for h := range q.CodeHashes() {
-		got = append(got, h)
+	// Drain any items buffered before cancel.
+	for range q.CodeHashes() {
 	}
-	require.Equal(t, hashes, got)
 
-	// Now AddCode should complete without error, and Finalize should return and close the channel.
-	require.NoError(t, <-addDone, "AddCode()")
-	<-finalized
+	// Finalize after Shutdown must not panic.
+	require.NoError(t, q.Finalize())
+
+	// AddCode after Shutdown must return ErrQueueClosed.
+	err = q.AddCode(t.Context(), []common.Hash{{}})
+	require.ErrorIs(t, err, ErrQueueClosed)
 }
 
-func TestQuitAndAddCodeRace(t *testing.T) {
-	{
-		q := new(Queue)
-		// Before the introduction of these fields, this test would panic.
-		_ = []any{&q.closeChanOnce, &q.chanLock}
-	}
-	for range 10_000 {
+// TestShutdownAndAddCodeRace verifies no panic or goroutine leak when
+// Shutdown and AddCode race against each other.
+func TestShutdownAndAddCodeRace(t *testing.T) {
+	for range 1_000 {
 		t.Run("", func(t *testing.T) {
 			t.Parallel()
 
-			quit := make(chan struct{})
-			q, err := NewQueue(rawdb.NewMemoryDatabase(), quit)
+			q, err := NewQueue(rawdb.NewMemoryDatabase())
 			require.NoError(t, err)
 
-			var ready, finished sync.WaitGroup
+			var (
+				ready sync.WaitGroup
+				eg    errgroup.Group
+			)
+
 			ready.Add(2)
-			finished.Add(2)
 			start := make(chan struct{})
 
-			go func() {
-				defer finished.Done()
-
+			eg.Go(func() error {
 				ready.Done()
 				<-start
-				close(quit)
-			}()
-
-			go func() {
-				defer finished.Done()
-
-				in := []common.Hash{{}}
+				q.Shutdown()
+				return nil
+			})
+			eg.Go(func() error {
 				ready.Done()
 				<-start
-				// Due to the race condition, AddCode may either succeed or fail
-				// depending on whether the quit channel is closed first
-				_ = q.AddCode(t.Context(), in)
-			}()
+				// May succeed or return ErrQueueClosed depending on timing.
+				_ = q.AddCode(t.Context(), []common.Hash{{}})
+				return nil
+			})
 
 			ready.Wait()
 			close(start)
-			finished.Wait()
+			require.NoError(t, eg.Wait())
+		})
+	}
+}
+
+// TestConcurrentAddCodeAndConsume stress-tests concurrent producers and a
+// single consumer on a small-capacity channel.
+func TestConcurrentAddCodeAndConsume(t *testing.T) {
+	const (
+		numProducers      = 5
+		hashesPerProducer = 100
+		capacity          = 2
+	)
+	db := rawdb.NewMemoryDatabase()
+	q, err := NewQueue(db, WithCapacity(capacity))
+	require.NoError(t, err)
+
+	// AddCode is non-blocking, but we want concurrent calls for stress.
+	var producerEg errgroup.Group
+	for i := range numProducers {
+		producerEg.Go(func() error {
+			hashes := make([]common.Hash, hashesPerProducer)
+			for j := range hashes {
+				hashes[j] = crypto.Keccak256Hash([]byte{byte(i), byte(j)})
+			}
+			return q.AddCode(t.Context(), hashes)
 		})
 	}
+
+	got := drainAsync(q.CodeHashes())
+
+	require.NoError(t, producerEg.Wait())
+	require.NoError(t, q.Finalize())
+	<-got.done
+
+	require.Len(t, got.hashes, numProducers*hashesPerProducer)
+}
+
+// drainResult holds values collected from a channel by drainAsync.
+type drainResult struct {
+	hashes []common.Hash
+	done   chan struct{} // closed when draining completes
+}
+
+// drainAsync reads all values from ch in a background goroutine.
+func drainAsync(ch <-chan common.Hash) *drainResult {
+	r := &drainResult{done: make(chan struct{})}
+	go func() {
+		defer close(r.done)
+		for h := range ch {
+			r.hashes = append(r.hashes, h)
+		}
+	}()
+	return r
+}
+
+func makeHashes(n int) []common.Hash {
+	hashes := make([]common.Hash, n)
+	for i := range hashes {
+		hashes[i] = crypto.Keccak256Hash([]byte(strconv.Itoa(i)))
+	}
+	return hashes
 }
```

### graft/evm/sync/code/syncer_test.go
```diff
@@ -58,7 +58,6 @@ func testCodeSyncer(t *testing.T, test codeSyncerTest, c codec.Manager) {
 
 	codeQueue, err := NewQueue(
 		clientDB,
-		make(chan struct{}),
 		WithCapacity(test.queueCapacity),
 	)
 	require.NoError(t, err)
```

### graft/evm/sync/engine/client.go
```diff
@@ -130,6 +130,7 @@ type client struct {
 	config           *ClientConfig
 	resumableSummary message.Syncable
 	cancel           context.CancelFunc
+	codeQueue        *code.Queue
 	wg               sync.WaitGroup
 	err              error
 }
@@ -286,6 +287,9 @@ func (c *client) Shutdown() error {
 	if c.cancel != nil {
 		c.cancel()
 	}
+	if c.codeQueue != nil {
+		c.codeQueue.Shutdown()
+	}
 	c.wg.Wait() // wait for the background goroutine to exit
 	return nil
 }
@@ -390,10 +394,11 @@ func (c *client) newSyncerRegistry(summary message.Syncable) (*SyncerRegistry, e
 		return nil, fmt.Errorf("failed to create block syncer: %w", err)
 	}
 
-	codeQueue, err := code.NewQueue(c.config.ChainDB, c.config.StateSyncDone)
+	codeQueue, err := code.NewQueue(c.config.ChainDB)
 	if err != nil {
 		return nil, fmt.Errorf("failed to create code queue: %w", err)
 	}
+	c.codeQueue = codeQueue
 
 	codeSyncer, err := code.NewSyncer(c.config.Client, c.config.ChainDB, codeQueue.CodeHashes())
 	if err != nil {
```

### graft/evm/sync/evmstate/firewood_syncer_test.go
```diff
@@ -81,7 +81,7 @@ func TestFirewoodSync(t *testing.T) {
 
 			// Code queue should be closed.
 			err := codeQueue.AddCode(t.Context(), []common.Hash{{1}})
-			require.ErrorIs(t, err, code.ErrFailedToAddCodeHashesToQueue)
+			require.ErrorIs(t, err, code.ErrQueueClosed)
 		})
 	}
 }
@@ -135,7 +135,7 @@ func TestFirewoodSyncerFinalizeScenarios(t *testing.T) {
 
 			// After finalize, the queue should reject new code additions.
 			err := codeQueue.AddCode(t.Context(), []common.Hash{{1}})
-			require.ErrorIs(t, err, code.ErrFailedToAddCodeHashesToQueue)
+			require.ErrorIs(t, err, code.ErrQueueClosed)
 		})
 	}
 }
@@ -154,7 +154,7 @@ func createSyncers(t *testing.T, clientState, serverState state.Database, root c
 	)
 
 	// Create the producer code queue.
-	codeQueue, err := code.NewQueue(clientState.DiskDB().(ethdb.Database), make(chan struct{}))
+	codeQueue, err := code.NewQueue(clientState.DiskDB().(ethdb.Database))
 	require.NoError(t, err, "NewCodeQueue()")
 
 	// Create the consumer code syncer.
```

### graft/evm/sync/evmstate/sync_test.go
```diff
@@ -66,7 +66,7 @@ func testSync(t *testing.T, test syncTest, c codec.Manager, leafReqType message.
 	mockClient.GetCodeIntercept = test.GetCodeIntercept
 
 	// Create the code fetcher.
-	fetcher, err := code.NewQueue(clientEthDB, make(chan struct{}))
+	fetcher, err := code.NewQueue(clientEthDB)
 	require.NoError(t, err, "failed to create code fetcher")
 
 	// Create the consumer code syncer.
```
