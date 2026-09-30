# [?] fix(blocksync): fix deadlock in AddBlock caused by holding pool.mtx during sendError (#5931)

## Summary
Severity: Unknown
Chain: Cosmos
Component: cometbft/cometbft
Published: 2026-06-16
Source: https://github.com/cometbft/cometbft/commit/87d5264799a9b30618a0dee4be5e680f070d305a
Type: security-commit

## Details
fix(blocksync): fix deadlock in AddBlock caused by holding pool.mtx during sendError (#5931)

## Summary

Fix CI failure at:
https://github.com/cometbft/cometbft/actions/runs/27214146296/job/80350996164

- `AddBlock` held `pool.mtx` via a deferred `Unlock` while calling
`sendError` on an unbuffered channel. Any concurrent caller that also
needed `pool.mtx` would deadlock until the channel was drained.
- Fix by collecting the error in `sendErr` and dispatching it inside the
`defer` after the mutex is released.
- Adds a regression test `TestAddBlockDoesNotDeadlockOnSendError`.

---

#### PR checklist

- [x] Tests written/updated
- [x] Changelog entry added in `CHANGELOG.md`
- [ ] Updated relevant documentation (`docs/` or `spec/`) and code
comments

---------

Co-authored-by: mergify[bot] <37929162+mergify[bot]@users.noreply.github.com>

## Patch
### CHANGELOG.md
```diff
@@ -25,6 +25,9 @@
   `VerifyVoteExtension` handlers are inconsistent halts the node with a clear
   `CONSENSUS FAILURE` instead of stalling the whole network
   ([\#5204](https://github.com/cometbft/cometbft/issues/5204))
+- `[blocksync]` fix deadlock in `AddBlock` caused by holding `pool.mtx` during
+  `sendError`
+  ([\#5931](https://github.com/cometbft/cometbft/pull/5931))
 - `[blocksync]` hold `pool.mtx` and recompute `maxPeerHeight` in `Enable()`
   ([\#5888](https://github.com/cometbft/cometbft/pull/5888))
 - `[inspect]` fix flaky `TestInspectRun` and consolidate start/stop handshake
```

### blocksync/pool.go
```diff
@@ -366,7 +366,13 @@ func (pool *BlockPool) AddBlock(peerID p2p.ID, block *types.Block, extCommit *ty
 	}
 
 	pool.mtx.Lock()
-	defer pool.mtx.Unlock()
+	var sendErr error
+	defer func() {
+		pool.mtx.Unlock()
+		if sendErr != nil {
+			pool.sendError(sendErr, peerID)
+		}
+	}()
 
 	requester := pool.requesters[block.Height]
 	if requester == nil {
@@ -375,19 +381,17 @@ func (pool *BlockPool) AddBlock(peerID p2p.ID, block *types.Block, extCommit *ty
 		// can't punish it. But if the peer sent us a block we clearly didn't
 		// request, we disconnect.
 		if block.Height > pool.height || block.Height < pool.startHeight {
-			err := fmt.Errorf("peer sent us block #%d we didn't expect (current height: %d, start height: %d)",
+			sendErr = fmt.Errorf("peer sent us block #%d we didn't expect (current height: %d, start height: %d)",
 				block.Height, pool.height, pool.startHeight)
-			pool.sendError(err, peerID)
-			return err
+			return sendErr
 		}
 
 		return fmt.Errorf("got an already committed block #%d (possibly from the slow peer %s)", block.Height, peerID)
 	}
 
 	if !requester.setBlock(block, extCommit, peerID) {
-		err := fmt.Errorf("requested block #%d from %v, not %s", block.Height, requester.requestedFrom(), peerID)
-		pool.sendError(err, peerID)
-		return err
+		sendErr = fmt.Errorf("requested block #%d from %v, not %s", block.Height, requester.requestedFrom(), peerID)
+		return sendErr
 	}
 
 	pool.numPending.Add(-1)
```

### blocksync/pool_test.go
```diff
@@ -640,6 +640,46 @@ func TestBlockPoolMaxPeerHeightRefreshesOnPopRequest(t *testing.T) {
 		"peer B must contribute to maxPeerHeight once pool.height reaches its base")
 }
 
+// TestAddBlockDoesNotDeadlockOnSendError is a regression test for AddBlock
+// holding pool.mtx while calling sendError on an unbuffered channel.
+func TestAddBlockDoesNotDeadlockOnSendError(t *testing.T) {
+	requestsCh := make(chan BlockRequest, 10)
+	errorsCh := make(chan peerError) // unbuffered: keeps AddBlock blocked in sendError
+
+	pool := NewBlockPool(1, requestsCh, errorsCh, time.Second)
+	pool.SetLogger(log.TestingLogger())
+	require.NoError(t, pool.Start())
+	t.Cleanup(func() { _ = pool.Stop() })
+
+	pool.mtx.Lock()
+	req := newBPRequester(pool, 1)
+	req.peerID = "A"
+	pool.requesters[1] = req
+	pool.mtx.Unlock()
+
+	block := &types.Block{Header: types.Header{Height: 1}, LastCommit: &types.Commit{}}
+	extCommit := &types.ExtendedCommit{Height: 1}
+
+	// "B" did not request the block; setBlock fails → sendError while holding pool.mtx.
+	go func() { _ = pool.AddBlock("B", block, extCommit, 123) }()
+	time.Sleep(50 * time.Millisecond)
+
+	heightDone := make(chan struct{})
+	go func() {
+		pool.Height()
+		close(heightDone)
+	}()
+
+	select {
+	case <-heightDone:
+		<-errorsCh
+	case <-time.After(500 * time.Millisecond):
+		<-errorsCh
+		<-heightDone
+		t.Fatal("deadlock: AddBlock held pool.mtx while blocked in sendError")
+	}
+}
+
 func TestBlockPoolHasPendingRequestFrom(t *testing.T) {
 	requestsCh := make(chan BlockRequest, 10)
 	errorsCh := make(chan peerError, 10)
```
