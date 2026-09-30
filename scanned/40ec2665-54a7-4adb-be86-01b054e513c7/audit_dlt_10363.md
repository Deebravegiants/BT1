# [?] fix of emitter deadlock

## Summary
Severity: Unknown
Chain: Sonic
Component: 0xsoniclabs/sonic
Published: 2019-09-26
Source: https://github.com/0xsoniclabs/sonic/commit/3cd086d36c4175486ecd82cf29271d4f62602878
Type: security-commit

## Details
fix of emitter deadlock

Merge pull request #335 from devintegral2/feature/fix-emitter-deadlock

## Patch
### src/gossip/emitter.go
```diff
@@ -182,10 +182,8 @@ func (em *Emitter) getTxTurn(txHash common.Hash, now time.Time, membersArr []com
 	return membersArr[turn]
 }
 
-func (em *Emitter) addTxs(e *inter.Event) *inter.Event {
-	poolTxs, err := em.txpool.Pending()
-	if err != nil {
-		log.Error("Tx pool transactions fetching error", "err", err)
+func (em *Emitter) addTxs(e *inter.Event, poolTxs map[common.Address]types.Transactions) *inter.Event {
+	if poolTxs == nil || len(poolTxs) == 0 {
 		return e
 	}
 
@@ -262,7 +260,7 @@ func (em *Emitter) findBestParents(epoch idx.Epoch, coinbase common.Address) (*h
 }
 
 // createEvent is not safe for concurrent use.
-func (em *Emitter) createEvent() *inter.Event {
+func (em *Emitter) createEvent(poolTxs map[common.Address]types.Transactions) *inter.Event {
 	coinbase := em.GetCoinbase()
 
 	if _, ok := em.engine.GetMembers()[coinbase]; !ok {
@@ -288,7 +286,7 @@ func (em *Emitter) createEvent() *inter.Event {
 	for i, p := range parents {
 		parent := em.store.GetEventHeader(epoch, p)
 		if parent == nil {
-			log.Crit("Emitter: head wasn't found", "e", p.String())
+			log.Crit("Emitter: head wasn't found", "event", p.String())
 		}
 		parentHeaders[i] = parent
 		if parentHeaders[i].Creator == coinbase && i != 0 {
@@ -326,7 +324,7 @@ func (em *Emitter) createEvent() *inter.Event {
 	}
 
 	// Add txs
-	event = em.addTxs(event)
+	event = em.addTxs(event, poolTxs)
 
 	if !em.isAllowedToEmit(event, selfParentHeader) {
 		return nil
@@ -433,10 +431,16 @@ func (em *Emitter) isAllowedToEmit(e *inter.Event, selfParent *inter.EventHeader
 }
 
 func (em *Emitter) EmitEvent() *inter.Event {
+	poolTxs, err := em.txpool.Pending() // request txs before locking engineMu to prevent deadlock!
+	if err != nil {
+		log.Error("Tx pool transactions fetching error", "err", err)
+		return nil
+	}
+
 	em.engineMu.Lock()
 	defer em.engineMu.Unlock()
 
-	e := em.createEvent()
+	e := em.createEvent(poolTxs)
 	if e == nil {
 		return nil
 	}
@@ -446,7 +450,7 @@ func (em *Emitter) EmitEvent() *inter.Event {
 	}
 	em.gasRate.Mark(int64(e.GasPowerUsed))
 	em.prevEmittedTime = time.Now() // record time after connecting, to add the event processing time
-	log.Info("New event emitted", "e", e.String())
+	log.Info("New event emitted", "event", e.String())
 
 	return e
 }
```

### src/gossip/evm_state_reader.go
```diff
@@ -81,7 +81,7 @@ func (r *EvmStateReader) getBlock(h hash.Event, n idx.Block, readTxs bool) *evm_
 		for _, id := range block.Events {
 			e := r.store.GetEvent(id)
 			if e == nil {
-				log.Crit("Event wasn't found", "e", id.String())
+				log.Crit("Event wasn't found", "event", id.String())
 				continue
 			}
 
```

### src/gossip/handler_test.go
```diff
@@ -151,6 +151,7 @@ func testBroadcastEvent(t *testing.T, totalPeers, broadcastExpected int, allowAg
 	pm := svc.pm
 	pm.Start(1000)
 	pm.synced = 1
+	pm.downloader.Terminate() // disable downloader so test would be deterministic
 	defer pm.Stop()
 
 	// create peers
@@ -177,14 +178,10 @@ func testBroadcastEvent(t *testing.T, totalPeers, broadcastExpected int, allowAg
 		for _, peer := range peers {
 			if allowAggressive {
 				// aggressive
-				assertar.NoError(
-					ExpectMsgOneOf(2, // NOTE: because GetPackInfosMsg could be received first
-						peer.app, EventsMsg, []*inter.Event{emitted}))
+				assertar.NoError(p2p.ExpectMsg(peer.app, EventsMsg, []*inter.Event{emitted}))
 			} else {
 				// announce
-				assertar.NoError(
-					ExpectMsgOneOf(2, // NOTE: because GetPackInfosMsg could be received first
-						peer.app, NewEventHashesMsg, []hash.Event{emitted.Hash()}))
+				assertar.NoError(p2p.ExpectMsg(peer.app, NewEventHashesMsg, []hash.Event{emitted.Hash()}))
 			}
 			if t.Failed() {
 				return
@@ -203,7 +200,7 @@ func testBroadcastEvent(t *testing.T, totalPeers, broadcastExpected int, allowAg
 
 	// create new event, but send it from new peer
 	{
-		emitted := svc.emitter.createEvent()
+		emitted := svc.emitter.createEvent(nil)
 		assertar.NotNil(emitted)
 		assertar.NoError(p2p.Send(newPeer.app, NewEventHashesMsg, []hash.Event{emitted.Hash()})) // announce
 		// now PM should request it
```

### src/gossip/helper_test.go
```diff
@@ -171,13 +171,3 @@ func (p *testPeer) handshake(t *testing.T, progress *PeerProgress, genesis commo
 func (p *testPeer) close() {
 	p.app.Close()
 }
-
-func ExpectMsgOneOf(times int, r p2p.MsgReader, code uint64, content interface{}) (err error) {
-	for i := 0; i < times; i++ {
-		err = p2p.ExpectMsg(r, code, content)
-		if err == nil {
-			return
-		}
-	}
-	return
-}
```

### src/gossip/packs_downloader/packs_downloader.go
```diff
@@ -29,7 +29,8 @@ type PacksDownloader struct {
 	// State
 	peers map[string]*PeerPacksDownloader
 
-	peersMu *sync.RWMutex
+	peersMu    *sync.RWMutex
+	terminated bool
 }
 
 // New creates a packs fetcher to retrieve events based on pack announcements.
@@ -62,6 +63,10 @@ func (d *PacksDownloader) RegisterPeer(peer Peer, myEpoch idx.Epoch) error {
 	d.peersMu.Lock()
 	defer d.peersMu.Unlock()
 
+	if d.terminated {
+		return nil
+	}
+
 	if d.peers[peer.Id] != nil || len(d.peers) >= maxPeers {
 		return nil
 	}
@@ -132,6 +137,7 @@ func (d *PacksDownloader) Terminate() {
 	d.peersMu.Lock()
 	defer d.peersMu.Unlock()
 
+	d.terminated = true
 	for _, peerDownloader := range d.peers {
 		peerDownloader.Stop()
 	}
```
