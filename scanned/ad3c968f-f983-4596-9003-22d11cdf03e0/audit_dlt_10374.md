# [?] fix data race in commin(); remove logger duplicated fileds

## Summary
Severity: Unknown
Chain: Sonic
Component: 0xsoniclabs/sonic
Published: 2019-02-06
Source: https://github.com/0xsoniclabs/sonic/commit/7ed48032ed2b19811153e6dec5d37cff15791815
Type: security-commit

## Details
fix data race in commin(); remove logger duplicated fileds

## Patch
### src/node/node.go
```diff
@@ -83,7 +83,7 @@ func NewNode(conf *Config,
 		conf:             conf,
 		core:             core,
 		localAddr:        localAddr,
-		logger:           conf.Logger.WithField("this_id", id),
+		logger:           conf.Logger.WithField("this_id", id).WithField("addr", localAddr),
 		peerSelector:     peerSelector,
 		trans:            trans,
 		netCh:            trans.Consumer(),
@@ -234,6 +234,7 @@ func (n *Node) lachesis(gossip bool) {
 				n.rpcJobs.decrement()
 			})
 		case <-n.controlTimer.tickCh:
+			n.logStats()
 			if gossip && n.gossipJobs.get() < 1 {
 				n.selectorLock.Lock()
 				peerAddr := n.peerSelector.Next().NetAddr
@@ -247,7 +248,6 @@ func (n *Node) lachesis(gossip bool) {
 				})
 				n.logger.Debug("Gossip")
 			}
-			n.logStats()
 			n.resetTimer()
 		case <-returnCh:
 			return
@@ -628,6 +628,9 @@ func (n *Node) sync(events []poset.WireEvent) error {
 
 func (n *Node) commit(block poset.Block) error {
 
+	n.coreLock.Lock()
+	defer n.coreLock.Unlock()
+
 	stateHash := []byte{0, 1, 2}
 	_, err := n.proxy.CommitBlock(block)
 	if err != nil {
@@ -657,8 +660,6 @@ func (n *Node) commit(block poset.Block) error {
 		// multiple nodes can't read from the same client
 
 		block.StateHash = stateHash
-		n.coreLock.Lock()
-		defer n.coreLock.Unlock()
 		sig, err := n.core.SignBlock(block)
 		if err != nil {
 			return err
@@ -768,13 +769,17 @@ func (n *Node) logStats() {
 		"t/s":                    stats["transactions_per_second"],
 		"rounds/s":               stats["rounds_per_second"],
 		"round_events":           stats["round_events"],
-		"id":                     stats["id"],
 		"state":                  stats["state"],
 		"z_gossipJobs":           n.gossipJobs.get(),
 		"z_rpcJobs":              n.rpcJobs.get(),
-		"addr":                   n.localAddr,
 		"pending_loaded_events":  n.GetPendingLoadedEvents(),
 		"last_round":             n.GetLastRound(),
+		// "addr" is already defined in Node.logger, see NewNode() function
+		// uncomment when needed
+		//		"addr":                   n.localAddr,
+		// "id" is duplicate of "this_id" in Node.logger, see NewNode() function
+		// uncomment when needed
+		//		"id":                     stats["id"],
 	}).Warn("logStats()")
 }
 
```
