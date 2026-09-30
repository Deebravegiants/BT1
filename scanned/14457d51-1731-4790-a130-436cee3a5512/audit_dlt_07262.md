# [?] fix race condition on proposal height for published txs (#2021)

## Summary
Severity: Unknown
Chain: Cosmos
Component: cometbft/cometbft
Published: 2018-07-23
Source: https://github.com/cometbft/cometbft/commit/e36ce6f8931d3a924876f1e7990327403e2a7bfe
Type: security-commit

## Details
fix race condition on proposal height for published txs (#2021)

* #1920 try to fix race condition on proposal height for published txs

- related to create_empty_blocks=false
- published height for accepted tx can be wrong (too low)
- use the actual mempool height + 1 for the proposal
- expose Height() on mempool

* #1920 add initial test for mempool.Height()

- not sure how to test the lock
- can the mutex reference be of type Locker?
-- this way, we can use a "mock" of the mutex to test triggering

* #1920 use the ConsensusState height in favor of mempool

- gets rid of indirections
- doesn't need any "+1" magic

* #1920 cosmetic

- if we use cs.Height, it's enough to evaluate right before propose

* #1920 cleanup TODO and non-needed code

* #1920 add changelog entry

## Patch
### CHANGELOG.md
```diff
@@ -11,6 +11,9 @@ IMPROVEMENTS:
 - [config] Increase default send/recv rates to 5 mB/s
 - [libs/common] Generated gogoproto static marshaller methods
 
+BUG FIXES
+- [mempool] fixed a race condition when create_empty_blocks=false where a transaction is published at an old height
+
 
 ## 0.22.4
 
```

### consensus/state.go
```diff
@@ -571,8 +571,10 @@ func (cs *ConsensusState) receiveRoutine(maxSteps int) {
 		var mi msgInfo
 
 		select {
-		case height := <-cs.mempool.TxsAvailable():
-			cs.handleTxsAvailable(height)
+		case txAvailable := <-cs.mempool.TxsAvailable():
+			if txAvailable {
+				cs.handleTxsAvailable()
+			}
 		case mi = <-cs.peerMsgQueue:
 			cs.wal.Write(mi)
 			// handles proposals, block parts, votes
@@ -683,11 +685,12 @@ func (cs *ConsensusState) handleTimeout(ti timeoutInfo, rs cstypes.RoundState) {
 
 }
 
-func (cs *ConsensusState) handleTxsAvailable(height int64) {
+func (cs *ConsensusState) handleTxsAvailable() {
 	cs.mtx.Lock()
 	defer cs.mtx.Unlock()
 	// we only need to do this for round 0
-	cs.enterPropose(height, 0)
+	cs.Logger.Debug("handling available txs", "height to propose", cs.Height)
+	cs.enterPropose(cs.Height, 0)
 }
 
 //-----------------------------------------------------------------------------
```

### mempool/mempool.go
```diff
@@ -78,7 +78,7 @@ type Mempool struct {
 	recheckCursor        *clist.CElement // next expected response
 	recheckEnd           *clist.CElement // re-checking stops here
 	notifiedTxsAvailable bool
-	txsAvailable         chan int64 // fires the next height once for each height, when the mempool is not empty
+	txsAvailable         chan bool // fires once for each height, when the mempool is not empty
 
 	// Keep a cache of already-seen txs.
 	// This reduces the pressure on the proxyApp.
@@ -130,7 +130,7 @@ func NewMempool(
 // ensuring it will trigger once every height when transactions are available.
 // NOTE: not thread safe - should only be called once, on startup
 func (mem *Mempool) EnableTxsAvailable() {
-	mem.txsAvailable = make(chan int64, 1)
+	mem.txsAvailable = make(chan bool, 1)
 }
 
 // SetLogger sets the Logger.
@@ -348,7 +348,7 @@ func (mem *Mempool) resCbRecheck(req *abci.Request, res *abci.Response) {
 // TxsAvailable returns a channel which fires once for every height,
 // and only when transactions are available in the mempool.
 // NOTE: the returned channel may be nil if EnableTxsAvailable was not called.
-func (mem *Mempool) TxsAvailable() <-chan int64 {
+func (mem *Mempool) TxsAvailable() <-chan bool {
 	return mem.txsAvailable
 }
 
@@ -358,11 +358,11 @@ func (mem *Mempool) notifyTxsAvailable() {
 	}
 	if mem.txsAvailable != nil && !mem.notifiedTxsAvailable {
 		// channel cap is 1, so this will send once
+		mem.notifiedTxsAvailable = true
 		select {
-		case mem.txsAvailable <- mem.height + 1:
+		case mem.txsAvailable <- true:
 		default:
 		}
-		mem.notifiedTxsAvailable = true
 	}
 }
 
```

### mempool/mempool_test.go
```diff
@@ -38,7 +38,7 @@ func newMempoolWithApp(cc proxy.ClientCreator) *Mempool {
 	return mempool
 }
 
-func ensureNoFire(t *testing.T, ch <-chan int64, timeoutMS int) {
+func ensureNoFire(t *testing.T, ch <-chan bool, timeoutMS int) {
 	timer := time.NewTimer(time.Duration(timeoutMS) * time.Millisecond)
 	select {
 	case <-ch:
@@ -47,7 +47,7 @@ func ensureNoFire(t *testing.T, ch <-chan int64, timeoutMS int) {
 	}
 }
 
-func ensureFire(t *testing.T, ch <-chan int64, timeoutMS int) {
+func ensureFire(t *testing.T, ch <-chan bool, timeoutMS int) {
 	timer := time.NewTimer(time.Duration(timeoutMS) * time.Millisecond)
 	select {
 	case <-ch:
```

### state/services.go
```diff
@@ -27,7 +27,7 @@ type Mempool interface {
 	Flush()
 	FlushAppConn() error
 
-	TxsAvailable() <-chan int64
+	TxsAvailable() <-chan bool
 	EnableTxsAvailable()
 }
 
@@ -43,7 +43,7 @@ func (m MockMempool) Reap(n int) types.Txs                               { retur
 func (m MockMempool) Update(height int64, txs types.Txs) error           { return nil }
 func (m MockMempool) Flush()                                             {}
 func (m MockMempool) FlushAppConn() error                                { return nil }
-func (m MockMempool) TxsAvailable() <-chan int64                         { return make(chan int64) }
+func (m MockMempool) TxsAvailable() <-chan bool                          { return make(chan bool) }
 func (m MockMempool) EnableTxsAvailable()                                {}
 
 //------------------------------------------------------
```
