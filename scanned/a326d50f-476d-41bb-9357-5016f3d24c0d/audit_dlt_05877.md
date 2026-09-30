# [?] miner: fix data race during shutdown (#23435)

## Summary
Severity: Unknown
Chain: Scroll
Component: scroll-tech/go-ethereum
Published: 2021-10-08
Source: https://github.com/scroll-tech/go-ethereum/commit/ee120ef865e9468fef0bbb0a0bcffba93e3e358e
Type: security-commit

## Details
miner: fix data race during shutdown (#23435)

This fixes a data race on worker.current by moving the call to StopPrefetcher
into the main loop.

The commit also contains fixes for two other races in unit tests of unrelated packages.

## Patch
### eth/gasprice/gasprice_test.go
```diff
@@ -151,7 +151,7 @@ func newTestBackend(t *testing.T, londonBlock *big.Int, pending bool) *testBacke
 	// Construct testing chain
 	diskdb := rawdb.NewMemoryDatabase()
 	gspec.Commit(diskdb)
-	chain, err := core.NewBlockChain(diskdb, nil, gspec.Config, engine, vm.Config{}, nil, nil)
+	chain, err := core.NewBlockChain(diskdb, &core.CacheConfig{TrieCleanNoPrefetch: true}, gspec.Config, engine, vm.Config{}, nil, nil)
 	if err != nil {
 		t.Fatalf("Failed to create local chain, %v", err)
 	}
```

### eth/handler_eth_test.go
```diff
@@ -486,7 +486,6 @@ func TestCheckpointChallenge(t *testing.T) {
 }
 
 func testCheckpointChallenge(t *testing.T, syncmode downloader.SyncMode, checkpoint bool, timeout bool, empty bool, match bool, drop bool) {
-	t.Parallel()
 
 	// Reduce the checkpoint handshake challenge timeout
 	defer func(old time.Duration) { syncChallengeTimeout = old }(syncChallengeTimeout)
```

### miner/worker.go
```diff
@@ -321,9 +321,6 @@ func (w *worker) isRunning() bool {
 // close terminates all background threads maintained by the worker.
 // Note the worker does not support being closed multiple times.
 func (w *worker) close() {
-	if w.current != nil && w.current.state != nil {
-		w.current.state.StopPrefetcher()
-	}
 	atomic.StoreInt32(&w.running, 0)
 	close(w.exitCh)
 	w.wg.Wait()
@@ -455,6 +452,11 @@ func (w *worker) mainLoop() {
 	defer w.txsSub.Unsubscribe()
 	defer w.chainHeadSub.Unsubscribe()
 	defer w.chainSideSub.Unsubscribe()
+	defer func() {
+		if w.current != nil && w.current.state != nil {
+			w.current.state.StopPrefetcher()
+		}
+	}()
 
 	for {
 		select {
```
