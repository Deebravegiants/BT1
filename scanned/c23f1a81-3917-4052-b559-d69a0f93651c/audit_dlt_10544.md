# [?] FAB-15151 fix data race in Raft chain UT

## Summary
Severity: Unknown
Chain: Hyperledger Fabric
Component: hyperledger/fabric
Published: 2019-04-12
Source: https://github.com/hyperledger/fabric/commit/3aa8ddbfd91c20e5b0fdda41cae5436366012c86
Type: security-commit

## Details
FAB-15151 fix data race in Raft chain UT

Change-Id: Ie8e8d3aeb80f8b6bd19fde687ffe6201ccbbf5e8
Signed-off-by: Jay Guo <guojiannan1101@gmail.com>

## Patch
### orderer/consensus/etcdraft/chain_test.go
```diff
@@ -3890,14 +3890,22 @@ func (n *network) join(id uint64, expectLeaderChange bool) {
 
 // elect deterministically elects a node as leader
 func (n *network) elect(id uint64) {
-	c := n.chains[id]
+	n.RLock()
+	candidate := n.chains[id]
+	var followers []*chain
+	for _, c := range n.chains {
+		if c.id != id {
+			followers = append(followers, c)
+		}
+	}
+	n.RUnlock()
 
 	// Send node an artificial MsgTimeoutNow to emulate leadership transfer.
-	c.Consensus(&orderer.ConsensusRequest{Payload: protoutil.MarshalOrPanic(&raftpb.Message{Type: raftpb.MsgTimeoutNow})}, 0)
-	Eventually(c.observe, LongEventualTimeout).Should(Receive(StateEqual(id, raft.StateLeader)))
+	candidate.Consensus(&orderer.ConsensusRequest{Payload: protoutil.MarshalOrPanic(&raftpb.Message{Type: raftpb.MsgTimeoutNow})}, 0)
+	Eventually(candidate.observe, LongEventualTimeout).Should(Receive(StateEqual(id, raft.StateLeader)))
 
 	// now observe leader change on other nodes
-	for _, c := range n.chains {
+	for _, c := range followers {
 		if c.id == id {
 			continue
 		}
@@ -3912,7 +3920,9 @@ func (n *network) elect(id uint64) {
 		}
 	}
 
+	n.Lock()
 	n.leader = id
+	n.Unlock()
 }
 
 // sets the configEnv var declared above
```
