# [?] blocksync: fix flaky TestBlockPoolBasic deadlock under -race (#5867)

## Summary
Severity: Unknown
Chain: Cosmos
Component: cometbft/cometbft
Published: 2026-06-12
Source: https://github.com/cometbft/cometbft/commit/80199cffd75512d4356d7d1e5f7792fdd18f340c
Type: security-commit

## Details
blocksync: fix flaky TestBlockPoolBasic deadlock under -race (#5867)

## Summary

Fix the CI failure at:

https://github.com/cometbft/cometbft/actions/runs/25839950951/job/75922993075

Sending to `inputChan` directly inside the `select` case blocked the
drain loop when the buffer filled up under `-race`, preventing
`requestsCh` from being drained and causing all `bpRequester` goroutines
to deadlock.

The fix replaces per-request goroutines with a single dedicated
dispatcher goroutine that is the sole consumer of `requestsCh` for the
full test lifetime. Teardown order is: `pool.Stop()` first (so the pool
stops sending to `requestsCh`), then signal the dispatcher, wait for it
to exit, then close peer channels.

## Test plan

- [x] Re-run `TestBlockPoolBasic` with `-race` to confirm no timeout

---------

Co-authored-by: Alex | Cosmos Labs <alex@cosmoslabs.io>
Co-authored-by: mergify[bot] <37929162+mergify[bot]@users.noreply.github.com>

## Patch
### CHANGELOG.md
```diff
@@ -29,6 +29,8 @@
   ([\#5878](https://github.com/cometbft/cometbft/pull/5878))
 - `[evidence]` fix flaky `TestReactorsGossipNoCommittedEvidence` test
   ([\#5870](https://github.com/cometbft/cometbft/pull/5870))
+- `[blocksync]` fix flaky `TestBlockPoolBasic` deadlock under `-race`
+  ([\#5867](https://github.com/cometbft/cometbft/pull/5867))
 - `[blocksync]` fix removeTimedoutPeers deadlock found via Byzantine prevote gossip race
   ([\#5839](https://github.com/cometbft/cometbft/pull/5839))
 - `[mempool]` fix setRecheckFull/setDone race causing spurious ErrRecheckFull.
```

### blocksync/pool.go
```diff
@@ -577,15 +577,21 @@ func (pool *BlockPool) sendRequest(height int64, peerID p2p.ID) {
 	if !pool.IsRunning() {
 		return
 	}
-	pool.requestsCh <- BlockRequest{height, peerID}
+	select {
+	case pool.requestsCh <- BlockRequest{height, peerID}:
+	case <-pool.Quit():
+	}
 }
 
 // thread-safe.
 func (pool *BlockPool) sendError(err error, peerID p2p.ID) {
 	if !pool.IsRunning() {
 		return
 	}
-	pool.errorsCh <- peerError{err, peerID}
+	select {
+	case pool.errorsCh <- peerError{err, peerID}:
+	case <-pool.Quit():
+	}
 }
 
 // for debugging purposes
```

### blocksync/pool_test.go
```diff
@@ -3,6 +3,7 @@ package blocksync
 import (
 	"fmt"
 	"math"
+	"sync"
 	"testing"
 	"time"
 
@@ -48,20 +49,16 @@ func (p testPeer) runInputRoutine() {
 	}()
 }
 
-// Request desired, pretend like we got the block immediately.
+// simulateInput pretends a block was received immediately.
 func (p testPeer) simulateInput(input inputData) {
 	block := &types.Block{Header: types.Header{Height: input.request.Height}, LastCommit: &types.Commit{}} // real blocks have LastCommit
 	extCommit := &types.ExtendedCommit{
 		Height: input.request.Height,
 	}
-	// If this peer is malicious
 	if p.malicious {
 		realHeight := p.height - MaliciousLie
-		// And the requested height is above the real height
 		if input.request.Height > realHeight {
-			// Then provide a fake block
-			block.LastCommit = nil // Fake block, no LastCommit
-			// or provide no block at all, if we are close to the real height
+			block.LastCommit = nil
 			if input.request.Height <= realHeight+BlackholeSize {
 				input.pool.RedoRequestFrom(input.request.Height, p.id)
 				return
@@ -116,17 +113,27 @@ func TestBlockPoolBasic(t *testing.T) {
 
 	err := pool.Start()
 	if err != nil {
-		t.Error(err)
+		t.Fatal(err)
 	}
 
-	t.Cleanup(func() {
+	done := make(chan struct{})
+	var (
+		wg        sync.WaitGroup
+		closeDone sync.Once
+	)
+	stopDispatcher := func() {
+		closeDone.Do(func() { close(done) })
+	}
+	defer func() {
 		if err := pool.Stop(); err != nil {
 			t.Error(err)
 		}
-	})
+		stopDispatcher()
+		wg.Wait()
+		peers.stop()
+	}()
 
 	peers.start()
-	defer peers.stop()
 
 	// Introduce each peer.
 	go func() {
@@ -135,7 +142,6 @@ func TestBlockPoolBasic(t *testing.T) {
 		}
 	}()
 
-	// Start a goroutine to pull blocks
 	go func() {
 		for {
 			if !pool.IsRunning() {
@@ -150,18 +156,39 @@ func TestBlockPoolBasic(t *testing.T) {
 		}
 	}()
 
-	// Pull from channels
+	wg.Add(1)
+	go func() {
+		defer wg.Done()
+		for {
+			select {
+			case req, ok := <-requestsCh:
+				if !ok {
+					return
+				}
+				t.Logf("Pulled new BlockRequest %v", req)
+				isTerminal := req.Height == 300
+				select {
+				case peers[req.PeerID].inputChan <- inputData{t, pool, req}:
+					if isTerminal {
+						stopDispatcher()
+					}
+				case <-done:
+					return
+				}
+			case <-done:
+				return
+			}
+		}
+	}()
+
 	for {
 		select {
 		case err := <-errorsCh:
 			t.Error(err)
-		case request := <-requestsCh:
-			t.Logf("Pulled new BlockRequest %v", request)
-			if request.Height == 300 {
-				return // Done!
-			}
-
-			peers[request.PeerID].inputChan <- inputData{t, pool, request}
+			stopDispatcher()
+			return
+		case <-done:
+			return
 		}
 	}
 }
```
