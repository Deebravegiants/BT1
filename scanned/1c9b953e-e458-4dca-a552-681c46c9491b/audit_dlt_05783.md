# [?] fix(test): fix TestBlockPoolMaliciousNode DATA RACE (#4636)

## Summary
Severity: Unknown
Chain: Cosmos
Component: cometbft/cometbft
Published: 2024-12-10
Source: https://github.com/cometbft/cometbft/commit/2b1db1c16bf2db16b81b49fef3581e79679fbed6
Type: security-commit

## Details
fix(test): fix TestBlockPoolMaliciousNode DATA RACE (#4636)

follow up to #4633 

See
https://github.com/cometbft/cometbft/actions/runs/12247740137/job/34188217504

<details>
<summary>DATA RACE</summary>

==================
WARNING: DATA RACE
Write at 0x00c00028f110 by goroutine 507:
  runtime.mapassign_faststr()
/opt/hostedtoolcache/go/1.23.1/x64/src/runtime/map_faststr.go:223 +0x0
  github.com/cometbft/cometbft/internal/blocksync.(*BlockPool).banPeer()
/home/runner/work/cometbft/cometbft/internal/blocksync/pool.go:433
+0x16f

github.com/cometbft/cometbft/internal/blocksync.(*BlockPool).RemovePeerAndRedoAllPeerRequests()
/home/runner/work/cometbft/cometbft/internal/blocksync/pool.go:266
+0x192

github.com/cometbft/cometbft/internal/blocksync.TestBlockPoolMaliciousNode.func4()
/home/runner/work/cometbft/cometbft/internal/blocksync/pool_test.go:353
+0x1ee

Previous read at 0x00c00028f110 by goroutine 501:
  runtime.mapaccess1_faststr()
/opt/hostedtoolcache/go/1.23.1/x64/src/runtime/map_faststr.go:13 +0x0

github.com/cometbft/cometbft/internal/blocksync.(*BlockPool).isPeerBanned()
/home/runner/work/cometbft/cometbft/internal/blocksync/pool.go:428
+0x128c

github.com/cometbft/cometbft/internal/blocksync.TestBlockPoolMaliciousNode()
/home/runner/work/cometbft/cometbft/internal/blocksync/pool_test.go:381
+0x1[20](https://github.com/cometbft/cometbft/actions/runs/12247740137/job/34188217504#step:6:21)5
  testing.tRunner()
/opt/hostedtoolcache/go/1.23.1/x64/src/testing/testing.go:1690 +0x226
  testing.(*T).Run.gowrap1()
/opt/hostedtoolcache/go/1.23.1/x64/src/testing/testing.go:1743 +0x44

Goroutine 507 (running) created at:

github.com/cometbft/cometbft/internal/blocksync.TestBlockPoolMaliciousNode()
/home/runner/work/cometbft/cometbft/internal/blocksync/pool_test.go:341
+0xdc4
  testing.tRunner()
/opt/hostedtoolcache/go/1.23.1/x64/src/testing/testing.go:1690 +0x226
  testing.(*T).Run.gowrap1()
/opt/hostedtoolcache/go/1.23.1/x64/src/testing/testing.go:1743 +0x44

Goroutine 501 (running) created at:
  testing.(*T).Run()
/opt/hostedtoolcache/go/1.23.1/x64/src/testing/testing.go:1743 +0x825
  testing.runTests.func1()

/opt/hostedtoolcache/go/1.23.1/x64/src/testing/testing.go:[21](https://github.com/cometbft/cometbft/actions/runs/12247740137/job/34188217504#step:6:22)68
+0x85
  testing.tRunner()
/opt/hostedtoolcache/go/1.23.1/x64/src/testing/testing.go:1690
+0x[22](https://github.com/cometbft/cometbft/actions/runs/12247740137/job/34188217504#step:6:23)6
  testing.runTests()

/opt/hostedtoolcache/go/1.[23](https://github.com/cometbft/cometbft/actions/runs/12247740137/job/34188217504#step:6:24).1/x64/src/testing/testing.go:2166
+0x8be
  testing.(*M).Run()
/opt/hostedtoolcache/go/1.23.1/x64/src/testing/testing.go:2034 +0xf17
  main.main()
      _testmain.go:83 +

</details>

### internal/blocksync/pool.go
```diff
@@ -384,6 +384,7 @@ func (pool *BlockPool) RemovePeer(peerID p2p.ID) {
 	pool.removePeer(peerID)
 }
 
+// CONTRACT: pool.mtx must be locked.
 func (pool *BlockPool) removePeer(peerID p2p.ID) {
 	for _, requester := range pool.requesters {
 		if requester.didRequestFrom(peerID) {
@@ -424,10 +425,19 @@ func (pool *BlockPool) updateMaxPeerHeight() {
 	pool.maxPeerHeight = max
 }
 
+// IsPeerBanned returns true if the peer is banned.
+func (pool *BlockPool) IsPeerBanned(peerID p2p.ID) bool {
+	pool.mtx.Lock()
+	defer pool.mtx.Unlock()
+	return pool.isPeerBanned(peerID)
+}
+
+// CONTRACT: pool.mtx must be locked.
 func (pool *BlockPool) isPeerBanned(peerID p2p.ID) bool {
 	return cmttime.Since(pool.bannedPeers[peerID]) < time.Second*60
 }
 
+// CONTRACT: pool.mtx must be locked.
 func (pool *BlockPool) banPeer(peerID p2p.ID) {
 	pool.Logger.Debug("Banning peer", peerID)
 	pool.bannedPeers[peerID] = cmttime.Now()
```

### internal/blocksync/pool_test.go
```diff
@@ -378,7 +378,7 @@ func TestBlockPoolMaliciousNode(t *testing.T) {
 			// Process request
 			peers[request.PeerID].inputChan <- inputData{t, pool, request}
 		case <-testTicker.C:
-			banned := pool.isPeerBanned("bad")
+			banned := pool.IsPeerBanned("bad")
 			bannedOnce = bannedOnce || banned // Keep bannedOnce true, even if the malicious peer gets unbanned
 			caughtUp, _, _ := pool.IsCaughtUp()
 			// Success: pool caught up and malicious peer was banned at least once
```
