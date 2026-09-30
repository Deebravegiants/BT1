# [?] fix(blocksync): removeTimedoutPeers deadlock found via Byzantine prevote gossip race (#5839)

## Summary
Severity: Unknown
Chain: Cosmos
Component: cometbft/cometbft
Published: 2026-05-11
Source: https://github.com/cometbft/cometbft/commit/55ea8536d004161ad95b91b4ffc41ddfbfc9e0cb
Type: security-commit

## Details
fix(blocksync): removeTimedoutPeers deadlock found via Byzantine prevote gossip race (#5839)

---
Fix the CI failure at:

https://github.com/cometbft/cometbft/actions/runs/25498058929/job/74823025038

That run revealed two issues:

1. removeTimedoutPeers and onTimeout held pool.mtx while calling
   sendError, which blocks on errorsCh. The reactor loop (the only
   consumer) may itself wait for pool.mtx via AddBlock, forming a
   circular deadlock.

2. The split-delivery of conflicting prevotes required gossip to
   propagate before height 2 committed, which raced under -race.
   Fix: send both conflicting prevotes to every peer directly so each
   validator detects the equivocation without relying on gossip timing.

Follows up on #5814
#### PR checklist

- [x] Tests written/updated
- [ ] Changelog entry added in `CHANGELOG.md`
- [ ] Updated relevant documentation (`docs/` or `spec/`) and code
comments

## Patch
### CHANGELOG.md
```diff
@@ -6,6 +6,8 @@
 
 ### BUG FIXES
 
+- `[blocksync]` fix removeTimedoutPeers deadlock found via Byzantine prevote gossip race
+  ([\#5839](https://github.com/cometbft/cometbft/pull/5839))
 - `[mempool]` fix setRecheckFull/setDone race causing spurious ErrRecheckFull.
   ([\#5837](https://github.com/cometbft/cometbft/pull/5837))
 
```

### blocksync/pool.go
```diff
@@ -164,20 +164,18 @@ func (pool *BlockPool) makeRequestersRoutine() {
 
 func (pool *BlockPool) removeTimedoutPeers() {
 	pool.mtx.Lock()
-	defer pool.mtx.Unlock()
-
+	var timedOut []p2p.ID
 	for _, peer := range pool.peers {
 		if !peer.didTimeout && peer.numPending > 0 {
 			curRate := peer.recvMonitor.Status().CurRate
 			// curRate can be 0 on start
 			if curRate != 0 && curRate < minRecvRate {
-				err := errors.New("peer is not sending us data fast enough")
-				pool.sendError(err, peer.id)
 				pool.Logger.Error("SendTimeout", "peer", peer.id,
-					"reason", err,
+					"reason", "peer is not sending us data fast enough",
 					"curRate", fmt.Sprintf("%d KB/s", curRate/1024),
 					"minRate", fmt.Sprintf("%d KB/s", minRecvRate/1024))
 				peer.didTimeout = true
+				timedOut = append(timedOut, peer.id)
 			}
 
 			peer.curRate = curRate
@@ -195,6 +193,11 @@ func (pool *BlockPool) removeTimedoutPeers() {
 	}
 
 	pool.sortPeers()
+	pool.mtx.Unlock()
+
+	for _, peerID := range timedOut {
+		pool.sendError(errors.New("peer is not sending us data fast enough"), peerID)
+	}
 }
 
 // GetStatus returns pool's height, numPending requests and the number of
@@ -657,11 +660,11 @@ func (peer *bpPeer) decrPending(recvSize int) {
 
 func (peer *bpPeer) onTimeout() {
 	peer.pool.mtx.Lock()
-	defer peer.pool.mtx.Unlock()
+	peer.didTimeout = true
+	peer.pool.mtx.Unlock()
 
 	peer.pool.sendError(ErrPeerTimeout, peer.id)
 	peer.logger.Error("SendTimeout", "reason", ErrPeerTimeout, "timeout", peerTimeout)
-	peer.didTimeout = true
 }
 
 //-------------------------------------
```

### consensus/byzantine_test.go
```diff
@@ -150,21 +150,19 @@ func TestByzantinePrevoteEquivocation(t *testing.T) {
 			require.NoError(t, err)
 			peerList := reactors[byzantineNode].Switch.Peers().Copy()
 			bcs.Logger.Info("Getting peer list", "peers", peerList)
-			// send two votes to all peers (1st to one half, 2nd to another half)
-			for i, peer := range peerList {
-				if i < len(peerList)/2 {
-					bcs.Logger.Info("Signed and pushed vote", "vote", prevote1, "peer", peer)
-					peer.Send(p2p.Envelope{
-						Message:   &cmtcons.Vote{Vote: prevote1.ToProto()},
-						ChannelID: VoteChannel,
-					})
-				} else {
-					bcs.Logger.Info("Signed and pushed vote", "vote", prevote2, "peer", peer)
-					peer.Send(p2p.Envelope{
-						Message:   &cmtcons.Vote{Vote: prevote2.ToProto()},
-						ChannelID: VoteChannel,
-					})
-				}
+			// send both conflicting votes to every peer so each validator receives
+			// the equivocation directly, without depending on gossip propagation
+			// racing against height advancement.
+			for _, peer := range peerList {
+				bcs.Logger.Info("Signed and pushed votes", "vote1", prevote1, "vote2", prevote2, "peer", peer)
+				peer.Send(p2p.Envelope{
+					Message:   &cmtcons.Vote{Vote: prevote1.ToProto()},
+					ChannelID: VoteChannel,
+				})
+				peer.Send(p2p.Envelope{
+					Message:   &cmtcons.Vote{Vote: prevote2.ToProto()},
+					ChannelID: VoteChannel,
+				})
 			}
 		} else {
 			bcs.Logger.Info("Behaving normally")
```
