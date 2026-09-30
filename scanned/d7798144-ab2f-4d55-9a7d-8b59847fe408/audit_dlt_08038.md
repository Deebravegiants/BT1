# [?] les: avoid fetcher deadlock on requestChn (#19571)

## Summary
Severity: Unknown
Chain: Celo
Component: celo-org/celo-blockchain
Published: 2019-05-17
Source: https://github.com/celo-org/celo-blockchain/commit/97d3615612a49488d02807944696d001b88f9e0d
Type: security-commit

## Details
les: avoid fetcher deadlock on requestChn (#19571)

* les: avoid fetcher deadlock on requestChn

## Patch
### les/fetcher.go
```diff
@@ -55,7 +55,8 @@ type lightFetcher struct {
 	requested         map[uint64]fetchRequest
 	deliverChn        chan fetchResponse
 	timeoutChn        chan uint64
-	requestChn        chan bool // true if initiated from outside
+	requestTriggered  bool
+	requestTrigger    chan struct{}
 	lastTrustedHeader *types.Header
 }
 
@@ -122,7 +123,7 @@ func newLightFetcher(pm *ProtocolManager) *lightFetcher {
 		deliverChn:     make(chan fetchResponse, 100),
 		requested:      make(map[uint64]fetchRequest),
 		timeoutChn:     make(chan uint64),
-		requestChn:     make(chan bool, 100),
+		requestTrigger: make(chan struct{}, 1),
 		syncDone:       make(chan *peer),
 		maxConfirmedTd: big.NewInt(0),
 	}
@@ -135,31 +136,26 @@ func newLightFetcher(pm *ProtocolManager) *lightFetcher {
 
 // syncLoop is the main event loop of the light fetcher
 func (f *lightFetcher) syncLoop() {
-	requesting := false
 	defer f.pm.wg.Done()
 	for {
 		select {
 		case <-f.pm.quitSync:
 			return
-		// when a new announce is received, request loop keeps running until
-		// no further requests are necessary or possible
-		case newAnnounce := <-f.requestChn:
+		// request loop keeps running until no further requests are necessary or possible
+		case <-f.requestTrigger:
 			f.lock.Lock()
-			s := requesting
-			requesting = false
 			var (
 				rq      *distReq
 				reqID   uint64
 				syncing bool
 			)
-
-			if !f.syncing && !(newAnnounce && s) {
+			if !f.syncing {
 				rq, reqID, syncing = f.nextRequest()
 			}
+			f.requestTriggered = rq != nil
 			f.lock.Unlock()
 
 			if rq != nil {
-				requesting = true
 				if _, ok := <-f.pm.reqDist.queue(rq); ok {
 					if syncing {
 						f.lock.Lock()
@@ -176,11 +172,11 @@ func (f *lightFetcher) syncLoop() {
 							}
 							f.reqMu.Unlock()
 							// keep starting new requests while possible
-							f.requestChn <- false
+							f.requestTrigger <- struct{}{}
 						}()
 					}
 				} else {
-					f.requestChn <- false
+					f.requestTrigger <- struct{}{}
 				}
 			}
 		case reqID := <-f.timeoutChn:
@@ -220,7 +216,7 @@ func (f *lightFetcher) syncLoop() {
 			f.checkSyncedHeaders(p)
 			f.syncing = false
 			f.lock.Unlock()
-			f.requestChn <- false
+			f.requestTrigger <- struct{}{} // f.requestTriggered is always true here
 		}
 	}
 }
@@ -354,7 +350,10 @@ func (f *lightFetcher) announce(p *peer, head *announceData) {
 	fp.lastAnnounced = n
 	p.lock.Unlock()
 	f.checkUpdateStats(p, nil)
-	f.requestChn <- true
+	if !f.requestTriggered {
+		f.requestTriggered = true
+		f.requestTrigger <- struct{}{}
+	}
 }
 
 // peerHasBlock returns true if we can assume the peer knows the given block
```
