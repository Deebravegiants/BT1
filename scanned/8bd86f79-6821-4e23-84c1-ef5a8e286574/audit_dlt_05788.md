# [?] fix(mempool): Fix data race when rechecking with async ABCI client (#2268)

## Summary
Severity: Unknown
Chain: Cosmos
Component: cometbft/cometbft
Published: 2024-05-07
Source: https://github.com/cometbft/cometbft/commit/f3775f4bbfd1528b21f13660f2a76ddb3255101f
Type: security-commit

## Details
fix(mempool): Fix data race when rechecking with async ABCI client (#2268)

Fixes ~~#2225 and~~ #1827 

(#2225 is now fixed in a separate PR, #2894)

The bug: during rechecking, when the `CheckTxAsync` request for the last
transaction fails, then the `resCbRecheck` callback on the response is
not called, and the recheck variables end up in a wrong state
(`recheckCursor != nil`, meaning that recheck has not finished). This
will cause a panic next time a new transaction arrives, and the
`CheckTx` response finds that rechecking hasn't finished.

This problem only happens when using the non-local ABCI client, where
`CheckTx` responses may arrive late or never, so the response won't be
processed by the callback. We have two options to fix this.
1. When we call `CheckTxAsync`, block waiting for a response. If the
response never arrives, it will block `Update` forever.
2. After sending all recheck requests, we flush the app connection and
set a timer to wait for late recheck responses. After the timer expires,
we finalise rechecking properly. If a CheckTx response arrives late, we
consider that it is safe to ignore it.

This PR implements option 2, as we cannot allow the risk to block the
node forever waiting for a response.

With the proposed changes, now when we reach the end of the rechecking
process, all requests and responses will be processed or discared, and
`recheckCursor` will always be `nil`.

This PR also:
- refactors all recheck logic to put it into a separate `recheck`
struct. The fix to the bug described above is the only change in the
recheck logic.
- adds 4 new tests.

---

#### PR checklist

- [x] Tests written/updated
- [ ] Changelog entry added in `.changelog` (we use
[unclog](https://github.com/informalsystems/unclog) to manage our
changelog)
- [ ] Updated relevant documentation (`docs/` or `spec/`) and code
comments
- [x] Title follows the [Conventional
Commits](https://www.conventionalcommits.org/en/v1.0.0/) spec

---------

Co-authored-by: Andy Nogueira <me@andynogueira.dev>
Co-authored-by: Daniel <daniel.cason@informal.systems>

### .changelog/unreleased/bug-fixes/1827-fix-recheck-async.md
```diff
@@ -0,0 +1,2 @@
+- [`mempool`] Fix data race when rechecking with async ABCI client
+  ([\#1827](https://github.com/cometbft/cometbft/issues/1827))
```

### .changelog/unreleased/improvements/1827-config-mempool-recheck-timeout.md
```diff
@@ -0,0 +1,3 @@
+`[config]` Added `recheck_timeout` mempool parameter to set how much time to wait for recheck
+ responses from the app (only applies to non-local ABCI clients).
+ ([\#1827](https://github.com/cometbft/cometbft/issues/1827/))
```

### config/config.go
```diff
@@ -866,6 +866,11 @@ type MempoolConfig struct {
 	// mempool may become invalid. If this does not apply to your application,
 	// you can disable rechecking.
 	Recheck bool `mapstructure:"recheck"`
+	// RecheckTimeout is the time the application has during the rechecking process
+	// to return CheckTx responses, once all requests have been sent. Responses that
+	// arrive after the timeout expires are discarded. It only applies to
+	// non-local ABCI clients and when recheck is enabled.
+	RecheckTimeout time.Duration `mapstructure:"recheck_timeout"`
 	// Broadcast (default: true) defines whether the mempool should relay
 	// transactions to other peers. Setting this to false will stop the mempool
 	// from relaying transactions to other peers until they are included in a
@@ -911,10 +916,11 @@ type MempoolConfig struct {
 // DefaultMempoolConfig returns a default configuration for the CometBFT mempool.
 func DefaultMempoolConfig() *MempoolConfig {
 	return &MempoolConfig{
-		Type:      MempoolTypeFlood,
-		Recheck:   true,
-		Broadcast: true,
-		WalPath:   "",
+		Type:           MempoolTypeFlood,
+		Recheck:        true,
+		RecheckTimeout: 1000 * time.Millisecond,
+		Broadcast:      true,
+		WalPath:        "",
 		// Each signature verification takes .5ms, Size reduced until we implement
 		// ABCI Recheck
 		Size:        5000,
```

### config/toml.go
```diff
@@ -402,6 +402,12 @@ type = "flood"
 # you can disable rechecking.
 recheck = {{ .Mempool.Recheck }}
 
+# recheck_timeout is the time the application has during the rechecking process
+# to return CheckTx responses, once all requests have been sent. Responses that 
+# arrive after the timeout expires are discarded. It only applies to 
+# non-local ABCI clients and when recheck is enabled.
+recheck_timeout = "{{ .Mempool.RecheckTimeout }}"
+
 # broadcast (default: true) defines whether the mempool should relay
 # transactions to other peers. Setting this to false will stop the mempool
 # from relaying transactions to other peers until they are included in a
```

### docs/references/config/config.toml.md
```diff
@@ -1226,6 +1226,26 @@ might become invalid. Setting `recheck = true` will go through the remaining tra
 If your application may remove transactions passed by CometBFT to your `PrepareProposal` handler,
 you probably want to set this configuration to `true` to avoid possible leaks in your mempool
 (transactions staying in the mempool until the node is next restarted).
+
+### mempool.recheck_timeout
+Time to wait for the application to return CheckTx responses after all recheck requests have been
+sent. Responses that arrive after the timeout expires are discarded.
+```toml
+recheck_timeout = "1000ms"
+```
+
+| Value type          | string (duration) |
+|:--------------------|:------------------|
+| **Possible values** | &gt;= `"1000ms"`   |
+
+This setting only applies to non-local ABCI clients and when `recheck` is enabled.
+
+The ideal value will strongly depend on the application. It could roughly be estimated as the
+average size of the mempool multiplied by the average time it takes the application to validate one
+transaction. We consider that the ABCI application runs in the same location as the CometBFT binary
+(see [`proxy_app`](#proxy_app)) so that the recheck duration is not affected by network delays when
+making requests and receiving responses.
+
 ### mempool.broadcast
 Broadcast the mempool content (uncommitted transactions) to other nodes.
 ```toml
```

### mempool/clist_mempool.go
```diff
@@ -6,6 +6,7 @@ import (
 	"fmt"
 	"sync"
 	"sync/atomic"
+	"time"
 
 	abcicli "github.com/cometbft/cometbft/abci/client"
 	abci "github.com/cometbft/cometbft/abci/types"
@@ -45,11 +46,8 @@ type CListMempool struct {
 
 	proxyAppConn proxy.AppConnMempool
 
-	// Track whether we're rechecking txs.
-	// These are not protected by a mutex and are expected to be mutated in
-	// serial (ie. by abci responses which are called in serial).
-	recheckCursor *clist.CElement // next expected response
-	recheckEnd    *clist.CElement // re-checking stops here
+	// Keeps track of the rechecking process.
+	recheck *recheck
 
 	// Concurrent linked-list of valid txs.
 	// `txsMap`: txKey -> CElement is for quick access to txs.
@@ -79,13 +77,12 @@ func NewCListMempool(
 	options ...CListMempoolOption,
 ) *CListMempool {
 	mp := &CListMempool{
-		config:        cfg,
-		proxyAppConn:  proxyAppConn,
-		txs:           clist.New(),
-		recheckCursor: nil,
-		recheckEnd:    nil,
-		logger:        log.NewNopLogger(),
-		metrics:       NopMetrics(),
+		config:       cfg,
+		proxyAppConn: proxyAppConn,
+		txs:          clist.New(),
+		recheck:      newRecheck(),
+		logger:       log.NewNopLogger(),
+		metrics:      NopMetrics(),
 	}
 	mp.height.Store(height)
 
@@ -303,14 +300,16 @@ func (mem *CListMempool) globalCb(req *abci.Request, res *abci.Response) {
 		checkType := req.GetCheckTx().GetType()
 		switch checkType {
 		case abci.CHECK_TX_TYPE_CHECK:
-			if mem.recheckCursor != nil {
-				// this should never happen
-				panic("recheck cursor is not nil before resCbFirstTime")
+			if !mem.recheck.done() {
+				panic(log.NewLazySprintf("rechecking has not finished; cannot check new tx %v",
+					types.Tx(req.GetCheckTx().Tx).Hash()))
 			}
 			mem.resCbFirstTime(req.GetCheckTx().Tx, res.GetCheckTx())
 
 		case abci.CHECK_TX_TYPE_RECHECK:
-			if mem.recheckCursor == nil {
+			if mem.recheck.done() {
+				mem.logger.Error("rechecking has finished; discard late recheck response",
+					"tx", log.NewLazySprintf("%v", types.Tx(req.GetCheckTx().Tx).Hash()))
 				return
 			}
 			mem.metrics.RecheckTimes.Add(1)
@@ -443,34 +442,10 @@ func (mem *CListMempool) resCbFirstTime(tx types.Tx, res *abci.CheckTxResponse)
 // The case where the app checks the tx for the first time is handled by the
 // resCbFirstTime callback.
 func (mem *CListMempool) resCbRecheck(tx types.Tx, res *abci.CheckTxResponse) {
-	memTx := mem.recheckCursor.Value.(*mempoolTx)
-
-	// Search through the remaining list of tx to recheck for a transaction that matches
-	// the one we received from the ABCI application.
-	for {
-		if bytes.Equal(tx, memTx.tx) {
-			// We've found a tx in the recheck list that matches the tx that we
-			// received from the ABCI application.
-			// Break, and use this transaction for further checks.
-			break
-		}
-
-		mem.logger.Error(
-			"re-CheckTx transaction mismatch",
-			"got", tx.Hash(),
-			"expected", memTx.tx.Hash(),
-		)
-
-		if mem.recheckCursor == mem.recheckEnd {
-			// we reached the end of the recheckTx list without finding a tx
-			// matching the one we received from the ABCI application.
-			// Return without processing any tx.
-			mem.recheckCursor = nil
-			return
-		}
-
-		mem.recheckCursor = mem.recheckCursor.Next()
-		memTx = mem.recheckCursor.Value.(*mempoolTx)
+	// Check whether tx is still in the list of transactions that can be rechecked.
+	if !mem.recheck.findNextEntryMatching(&tx) {
+		// Reached the end of the list and didn't find a matching tx; rechecking has finished.
+		return
 	}
 
 	var postCheckErr error
@@ -481,27 +456,11 @@ func (mem *CListMempool) resCbRecheck(tx types.Tx, res *abci.CheckTxResponse) {
 	if (res.Code != abci.CodeTypeOK) || postCheckErr != nil {
 		// Tx became invalidated due to newly committed block.
 		mem.logger.Debug("tx is no longer valid", "tx", tx.Hash(), "res", res, "postCheckErr", postCheckErr)
-		if err := mem.RemoveTxByKey(memTx.tx.Key()); err != nil {
+		if err := mem.RemoveTxByKey(tx.Key()); err != nil {
 			mem.logger.Debug("Transaction could not be removed from mempool", "err", err)
 		}
 		mem.tryRemoveFromCache(tx)
 	}
-
-	if mem.recheckCursor == mem.recheckEnd {
-		mem.recheckCursor = nil
-	} else {
-		mem.recheckCursor = mem.recheckCursor.Next()
-	}
-
-	if mem.recheckCursor == nil {
-		// Done!
-		mem.logger.Debug("done rechecking txs")
-
-		// in case the recheck removed all txs
-		if mem.Size() > 0 {
-			mem.notifyTxsAvailable()
-		}
-	}
 }
 
 // Safe for concurrent use by multiple goroutines.
@@ -589,6 +548,8 @@ func (mem *CListMempool) Update(
 	preCheck PreCheckFunc,
 	postCheck PostCheckFunc,
 ) error {
+	mem.logger.Debug("Update", "height", height, "len(txs)", len(txs))
+
 	// Set height
 	mem.height.Store(height)
 	mem.notifiedTxsAvailable.Store(false)
@@ -625,18 +586,14 @@ func (mem *CListMempool) Update(
 		}
 	}
 
-	// Either recheck non-committed txs to see if they became invalid
-	// or just notify there're some txs left.
+	// Recheck txs left in the mempool to remove them if they became invalid in the new state.
+	if mem.config.Recheck {
+		mem.recheckTxs()
+	}
+
+	// Notify if there are still txs left in the mempool.
 	if mem.Size() > 0 {
-		if mem.config.Recheck {
-			mem.logger.Debug("recheck txs", "numtxs", mem.Size(), "height", height)
-			mem.recheckTxs()
-			// At this point, mem.txs are being rechecked.
-			// mem.recheckCursor re-scans mem.txs and possibly removes some txs.
-			// Before mem.Reap(), we should wait for mem.recheckCursor to be nil.
-		} else {
-			mem.notifyTxsAvailable()
-		}
+		mem.notifyTxsAvailable()
 	}
 
 	// Update metrics
@@ -646,28 +603,140 @@ func (mem *CListMempool) Update(
 	return nil
 }
 
+// recheckTxs sends all transactions in the mempool to the app for re-validation. When the function
+// returns, all recheck responses from the app have been processed.
 func (mem *CListMempool) recheckTxs() {
-	if mem.Size() == 0 {
-		panic("recheckTxs is called, but the mempool is empty")
+	mem.logger.Debug("recheck txs", "height", mem.height.Load(), "num-txs", mem.Size())
+
+	if mem.Size() <= 0 {
+		return
 	}
 
-	mem.recheckCursor = mem.txs.Front()
-	mem.recheckEnd = mem.txs.Back()
+	mem.recheck.init(mem.txs.Front(), mem.txs.Back())
 
-	// Push txs to proxyAppConn
-	// NOTE: globalCb may be called concurrently.
+	// NOTE: globalCb may be called concurrently, but CheckTx cannot be executed concurrently
+	// because this function has the lock (via Update and Lock).
 	for e := mem.txs.Front(); e != nil; e = e.Next() {
-		memTx := e.Value.(*mempoolTx)
+		tx := e.Value.(*mempoolTx).tx
+		mem.recheck.numPendingTxs.Add(1)
+
+		// Send a CheckTx request to the app. If we're using a sync client, the resCbRecheck
+		// callback will be called right after receiving the response.
 		_, err := mem.proxyAppConn.CheckTxAsync(context.TODO(), &abci.CheckTxRequest{
-			Tx:   memTx.tx,
+			Tx:   tx,
 			Type: abci.CHECK_TX_TYPE_RECHECK,
 		})
 		if err != nil {
-			panic(fmt.Errorf("(re-)CheckTx request for tx %s failed: %w", log.NewLazySprintf("%v", memTx.tx.Hash()), err))
+			panic(fmt.Errorf("(re-)CheckTx request for tx %s failed: %w", log.NewLazySprintf("%v", tx.Hash()), err))
 		}
 	}
 
-	// In <v0.37 we would call FlushAsync at the end of recheckTx forcing the buffer to flush
-	// all pending messages to the app. There doesn't seem to be any need here as the buffer
-	// will get flushed regularly or when filled.
+	// Flush any pending asynchronous recheck requests to process.
+	mem.proxyAppConn.Flush(context.TODO())
+
+	// Give some time to finish processing the responses; then finish the rechecking process, even
+	// if not all txs were rechecked.
+	select {
+	case <-time.After(mem.config.RecheckTimeout):
+		mem.recheck.setDone()
+		mem.logger.Error("timed out waiting for recheck responses")
+	case <-mem.recheck.doneRechecking():
+	}
+
+	if n := mem.recheck.numPendingTxs.Load(); n > 0 {
+		mem.logger.Error("not all txs were rechecked", "not-rechecked", n)
+	}
+	mem.logger.Debug("done rechecking txs", "height", mem.height.Load(), "num-txs", mem.Size())
+}
+
+// The cursor and end pointers define a dynamic list of transactions that could be rechecked. The
+// end pointer is fixed. When a recheck response for a transaction is received, cursor will point to
+// the entry in the mempool corresponding to that transaction, thus narrowing the list. Transactions
+// corresponding to entries between the old and current positions of cursor will be ignored for
+// rechecking. This is to guarantee that recheck responses are processed in the same sequential
+// order as they appear in the mempool.
+type recheck struct {
+	cursor        *clist.CElement // next expected recheck response
+	end           *clist.CElement // last entry in the mempool to recheck
+	doneCh        chan struct{}   // to signal that rechecking has finished successfully (for async app connections)
+	numPendingTxs atomic.Int32    // number of transactions still pending to recheck
+}
+
+func newRecheck() *recheck {
+	return &recheck{
+		doneCh: make(chan struct{}, 1),
+	}
+}
+
+func (rc *recheck) init(first, last *clist.CElement) {
+	if !rc.done() {
+		panic("Having more than one rechecking process at a time is not possible.")
+	}
+	rc.cursor = first
+	rc.end = last
+	rc.numPendingTxs.Store(0)
+}
+
+// done returns true when there is no recheck response to process.
+func (rc *recheck) done() bool {
+	return rc.cursor == nil
+}
+
+// setDone registers that rechecking has finished.
+func (rc *recheck) setDone() {
+	rc.cursor = nil
+}
+
+// setNextEntry sets cursor to the next entry in the list. If there is no next, cursor will be nil.
+func (rc *recheck) setNextEntry() {
+	rc.cursor = rc.cursor.Next()
+}
+
+// tryFinish will check if the cursor is at the end of the list and notify the channel that
+// rechecking has finished. It returns true iff it's done rechecking.
+func (rc *recheck) tryFinish() bool {
+	if rc.cursor == rc.end {
+		// Reached end of the list without finding a matching tx.
+		rc.setDone()
+	}
+	if rc.done() {
+		// Notify that recheck has finished.
+		select {
+		case rc.doneCh <- struct{}{}:
+		default:
+		}
+		return true
+	}
+	return false
+}
+
+// findNextEntryMatching searches for the next transaction matching the given transaction, which
+// corresponds to the recheck response to be processed next. Then it checks if it has reached the
+// end of the list, so it can finish rechecking.
+//
+// The goal is to guarantee that transactions are rechecked in the order in which they are in the
+// mempool. Transactions whose recheck response arrive late or don't arrive at all are skipped and
+// not rechecked.
+func (rc *recheck) findNextEntryMatching(tx *types.Tx) bool {
+	found := false
+	for ; !rc.done(); rc.setNextEntry() {
+		expectedTx := rc.cursor.Value.(*mempoolTx).tx
+		if bytes.Equal(*tx, expectedTx) {
+			// Found an entry in the list of txs to recheck that matches tx.
+			found = true
+			rc.numPendingTxs.Add(-1)
+			break
+		}
+	}
+
+	if !rc.tryFinish() {
+		// Not finished yet; set the cursor for processing the next recheck response.
+		rc.setNextEntry()
+	}
+	return found
+}
+
+// doneRechecking returns the channel used to signal that rechecking has finished.
+func (rc *recheck) doneRechecking() <-chan struct{} {
+	return rc.doneCh
 }
```

### mempool/clist_mempool_test.go
```diff
@@ -272,14 +272,15 @@ func TestMempoolUpdateDoesNotPanicWhenApplicationMissedTx(t *testing.T) {
 	mockClient.On("SetLogger", mock.Anything)
 	mockClient.On("Error").Return(nil).Times(4)
 	mockClient.On("SetResponseCallback", mock.MatchedBy(func(cb abciclient.Callback) bool { callback = cb; return true }))
+	mockClient.On("CheckTxAsync", mock.Anything, mock.Anything).Return(nil, nil)
+	mockClient.On("Flush", mock.Anything).Return(nil)
 
 	mp, cleanup := newMempoolWithAppMock(mockClient)
 	defer cleanup()
 
 	// Add 4 transactions to the mempool by calling the mempool's `CheckTx` on each of them.
 	txs := []types.Tx{[]byte{0x01}, []byte{0x02}, []byte{0x03}, []byte{0x04}}
 	for _, tx := range txs {
-		mockClient.On("CheckTxAsync", mock.Anything, mock.Anything).Return(nil, nil).Once()
 		_, err := mp.CheckTx(tx)
 		require.NoError(t, err)
 	}
@@ -291,11 +292,10 @@ func TestMempoolUpdateDoesNotPanicWhenApplicationMissedTx(t *testing.T) {
 		callback(reqRes.Request, reqRes.Response)
 	}
 	require.Len(t, txs, mp.Size())
-	require.Nil(t, mp.recheckCursor)
+	require.True(t, mp.recheck.done())
 
 	// Calling update to remove the first transaction from the mempool.
 	// This call also triggers the mempool to recheck its remaining transactions.
-	mockClient.On("CheckTxAsync", mock.Anything, mock.Anything).Return(nil, nil)
 	err := mp.Update(0, []types.Tx{txs[0]}, abciResponses(1, abci.CodeTypeOK), nil, nil)
 	require.NoError(t, err)
 
@@ -658,16 +658,7 @@ func TestMempoolTxsBytes(t *testing.T) {
 }
 
 func TestMempoolNoCacheOverflow(t *testing.T) {
-	sockPath := fmt.Sprintf("unix:///tmp/echo_%v.sock", cmtrand.Str(6))
-	app := kvstore.NewInMemoryApplication()
-	server := newRemoteApp(t, sockPath, app)
-	t.Cleanup(func() {
-		if err := server.Stop(); err != nil {
-			t.Error(err)
-		}
-	})
-	cfg := test.ResetTestRoot("mempool_test")
-	mp, cleanup := newMempoolWithAppAndConfig(proxy.NewRemoteClientCreator(sockPath, "socket", true), cfg)
+	mp, cleanup := newMempoolWithAsyncConnection(t)
 	defer cleanup()
 
 	// add tx0
@@ -707,18 +698,7 @@ func TestMempoolNoCacheOverflow(t *testing.T) {
 // TODO: all of the tests should probably also run using the remote proxy app
 // since otherwise we're not actually testing the concurrency of the mempool here!
 func TestMempoolRemoteAppConcurrency(t *testing.T) {
-	sockPath := fmt.Sprintf("unix:///tmp/echo_%v.sock", cmtrand.Str(6))
-	app := kvstore.NewInMemoryApplication()
-	server := newRemoteApp(t, sockPath, app)
-	t.Cleanup(func() {
-		if err := server.Stop(); err != nil {
-			t.Error(err)
-		}
-	})
-
-	cfg := test.ResetTestRoot("mempool_test")
-
-	mp, cleanup := newMempoolWithAppAndConfig(proxy.NewRemoteClientCreator(sockPath, "socket", true), cfg)
+	mp, cleanup := newMempoolWithAsyncConnection(t)
 	defer cleanup()
 
 	// generate small number of txs
@@ -727,7 +707,7 @@ func TestMempoolRemoteAppConcurrency(t *testing.T) {
 	txs := NewRandomTxs(nTxs, txLen)
 
 	// simulate a group of peers sending them over and over
-	n := cfg.Mempool.Size
+	n := mp.config.Size
 	for i := 0; i < n; i++ {
 		txNum := mrand.Intn(nTxs)
 		tx := txs[txNum]
@@ -876,6 +856,165 @@ func TestMempoolSyncRecheckTxReturnError(t *testing.T) {
 	mp.recheckTxs()
 }
 
+// Test that rechecking finishes correctly when a CheckTx response never arrives, when using an
+// async ABCI client.
+func TestMempoolAsyncRecheckTxReturnError(t *testing.T) {
+	var callback abciclient.Callback
+	mockClient := new(abciclimocks.Client)
+	mockClient.On("Start").Return(nil)
+	mockClient.On("SetLogger", mock.Anything)
+	mockClient.On("Error").Return(nil).Times(4)
+	mockClient.On("SetResponseCallback", mock.MatchedBy(func(cb abciclient.Callback) bool { callback = cb; return true }))
+
+	mp, cleanup := newMempoolWithAppMock(mockClient)
+	defer cleanup()
+
+	// Mocking the async client will just send the request and not call the callback, which we do
+	// manually later. The first 4 times CheckTxAsync is called are for adding the transactions to
+	// the mempool.
+	mockClient.On("CheckTxAsync", mock.Anything, mock.Anything).Return(nil, nil).Times(4)
+
+	// Add 4 txs to the mempool.
+	txs := []types.Tx{[]byte{0x01}, []byte{0x02}, []byte{0x03}, []byte{0x04}}
+	for _, tx := range txs {
+		_, err := mp.CheckTx(tx)
+		require.NoError(t, err)
+	}
+
+	// There are still no replies from the app.
+	require.Zero(t, mp.Size())
+
+	// Invoke CheckTx callbacks asynchronously.
+	for _, tx := range txs {
+		reqRes := newReqRes(tx, abci.CodeTypeOK, abci.CHECK_TX_TYPE_CHECK)
+		callback(reqRes.Request, reqRes.Response)
+	}
+
+	// The 4 txs are added to the mempool.
+	require.Len(t, txs, mp.Size())
+
+	// Check that recheck has not started.
+	require.True(t, mp.recheck.done())
+	require.Nil(t, mp.recheck.cursor)
+	require.Nil(t, mp.recheck.end)
+	mockClient.AssertExpectations(t)
+
+	// One call to CheckTxAsync per tx, for rechecking.
+	mockClient.On("CheckTxAsync", mock.Anything, mock.Anything).Return(nil, nil).Times(4)
+
+	// On the async client, the callbacks are executed when flushing the connection. The app replies
+	// to the request for the first tx (valid) and for the third tx (invalid), so the callback is
+	// invoked twice. The app does not reply to the requests for the second and fourth txs, so the
+	// callback is not invoked on these two cases.
+	mockClient.On("Flush", mock.Anything).Run(func(_ mock.Arguments) {
+		// First tx is valid.
+		reqRes1 := newReqRes(txs[0], abci.CodeTypeOK, abci.CHECK_TX_TYPE_RECHECK)
+		callback(reqRes1.Request, reqRes1.Response)
+		// Third tx is invalid.
+		reqRes2 := newReqRes(txs[2], 1, abci.CHECK_TX_TYPE_RECHECK)
+		callback(reqRes2.Request, reqRes2.Response)
+	}).Return(nil)
+
+	// mp.recheck.done() should be true only before and after calling recheckTxs.
+	mp.recheckTxs()
+	require.True(t, mp.recheck.done())
+	require.Nil(t, mp.recheck.cursor)
+	require.NotNil(t, mp.recheck.end)
+	require.Equal(t, mp.recheck.end, mp.txs.Back())
+	require.Equal(t, len(txs)-1, mp.Size()) // one invalid tx was removed
+	require.Equal(t, int32(2), mp.recheck.numPendingTxs.Load())
+
+	mockClient.AssertExpectations(t)
+}
+
+// This test used to cause a data race when rechecking (see https://github.com/cometbft/cometbft/issues/1827).
+func TestMempoolRecheckRace(t *testing.T) {
+	mp, cleanup := newMempoolWithAsyncConnection(t)
+	defer cleanup()
+
+	// Add a bunch of transactions to the mempool.
+	var err error
+	txs := newUniqueTxs(10)
+	for _, tx := range txs {
+		_, err = mp.CheckTx(tx)
+		require.NoError(t, err)
+	}
+
+	// Update one transaction to force rechecking the rest.
+	mp.Lock()
+	err = mp.FlushAppConn()
+	require.NoError(t, err)
+	err = mp.Update(1, txs[:1], abciResponses(1, abci.CodeTypeOK), nil, nil)
+	require.NoError(t, err)
+	mp.Unlock()
+
+	// Recheck has finished
+	require.True(t, mp.recheck.done())
+	require.Nil(t, mp.recheck.cursor)
+
+	// Add again the same transaction that was updated. Recheck has finished so adding this tx
+	// should not result in a data race on the variable recheck.cursor.
+	_, err = mp.CheckTx(txs[:1][0])
+	require.Equal(t, err, ErrTxInCache)
+	require.Zero(t, mp.recheck.numPendingTxs.Load())
+}
+
+// Test adding transactions while a concurrent routine reaps txs and updates the mempool, simulating
+// the consensus module, when using an async ABCI client.
+func TestMempoolConcurrentCheckTxAndUpdate(t *testing.T) {
+	mp, cleanup := newMempoolWithAsyncConnection(t)
+	defer cleanup()
+
+	maxHeight := 100
+	var wg sync.WaitGroup
+	wg.Add(1)
+
+	// A process that continuously reaps and update the mempool, simulating creation and committing
+	// of blocks by the consensus module.
+	go func() {
+		defer wg.Done()
+
+		time.Sleep(50 * time.Millisecond) // wait a bit to have some txs in mempool before starting updating
+		for h := 1; h <= maxHeight; h++ {
+			if mp.Size() == 0 {
+				break
+			}
+			txs := mp.ReapMaxBytesMaxGas(100, -1)
+			mp.Lock()
+			err := mp.FlushAppConn() // needed to process the pending CheckTx requests and their callbacks
+			require.NoError(t, err)
+			err = mp.Update(int64(h), txs, abciResponses(len(txs), abci.CodeTypeOK), nil, nil)
+			require.NoError(t, err)
+			mp.Unlock()
+		}
+	}()
+
+	// Concurrently, add transactions (one per height).
+	for h := 1; h <= maxHeight; h++ {
+		_, err := mp.CheckTx(kvstore.NewTxFromID(h))
+		require.NoError(t, err)
+	}
+
+	wg.Wait()
+
+	// All added transactions should have been removed from the mempool.
+	require.Zero(t, mp.Size())
+}
+
+func newMempoolWithAsyncConnection(t *testing.T) (*CListMempool, cleanupFunc) {
+	t.Helper()
+	sockPath := fmt.Sprintf("unix:///tmp/echo_%v.sock", cmtrand.Str(6))
+	app := kvstore.NewInMemoryApplication()
+	server := newRemoteApp(t, sockPath, app)
+	t.Cleanup(func() {
+		if err := server.Stop(); err != nil {
+			t.Error(err)
+		}
+	})
+	cfg := test.ResetTestRoot("mempool_test")
+	return newMempoolWithAppAndConfig(proxy.NewRemoteClientCreator(sockPath, "socket", true), cfg)
+}
+
 // caller must close server.
 func newRemoteApp(t *testing.T, addr string, app abci.Application) service.Service {
 	t.Helper()
@@ -892,7 +1031,7 @@ func newRemoteApp(t *testing.T, addr string, app abci.Application) service.Servi
 	return server
 }
 
-func newReqRes(tx types.Tx, code uint32, requestType abci.CheckTxType) *abciclient.ReqRes { //nolint: unparam
+func newReqRes(tx types.Tx, code uint32, requestType abci.CheckTxType) *abciclient.ReqRes {
 	reqRes := abciclient.NewReqRes(abci.ToCheckTxRequest(&abci.CheckTxRequest{Tx: tx, Type: requestType}))
 	reqRes.Response = abci.ToCheckTxResponse(&abci.CheckTxResponse{Code: code})
 	return reqRes
```
