# [?] emitter: fix txpool-related deadlock

## Summary
Severity: Unknown
Chain: Sonic
Component: 0xsoniclabs/sonic
Published: 2019-09-25
Source: https://github.com/0xsoniclabs/sonic/commit/945a90219ba72d6530b700a80d6d4a3e96673ee2
Type: security-commit

## Details
emitter: fix txpool-related deadlock

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
@@ -321,7 +319,7 @@ func (em *Emitter) createEvent() *inter.Event {
 	}
 
 	// Add txs
-	event = em.addTxs(event)
+	event = em.addTxs(event, poolTxs)
 
 	if !em.isAllowedToEmit(event, selfParentHeader) {
 		return nil
@@ -428,10 +426,16 @@ func (em *Emitter) isAllowedToEmit(e *inter.Event, selfParent *inter.EventHeader
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
```
