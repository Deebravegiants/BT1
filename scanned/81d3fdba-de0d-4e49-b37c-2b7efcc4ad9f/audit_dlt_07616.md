# [?] les/vflux: fixed panic and data races (#23865)

## Summary
Severity: Unknown
Chain: Ethereum
Component: ethereum/go-ethereum
Published: 2021-11-08
Source: https://github.com/ethereum/go-ethereum/commit/8be8ba450e3efda51b19389320f2b229545074cf
Type: security-commit

## Details
les/vflux: fixed panic and data races (#23865)

* les/vflux/server: fix BalanceOperation

* les/vflux/client: fixed data races

## Patch
### les/vflux/client/serverpool_test.go
```diff
@@ -19,6 +19,7 @@ package client
 import (
 	"math/rand"
 	"strconv"
+	"sync"
 	"sync/atomic"
 	"testing"
 	"time"
@@ -52,7 +53,7 @@ func testNodeIndex(id enode.ID) int {
 type ServerPoolTest struct {
 	db                   ethdb.KeyValueStore
 	clock                *mclock.Simulated
-	quit                 chan struct{}
+	quit                 chan chan struct{}
 	preNeg, preNegFail   bool
 	vt                   *ValueTracker
 	sp                   *ServerPool
@@ -62,6 +63,8 @@ type ServerPoolTest struct {
 	trusted              []string
 	waitCount, waitEnded int32
 
+	lock sync.Mutex
+
 	cycle, conn, servedConn  int
 	serviceCycles, dialCount int
 	disconnect               map[int][]int
@@ -112,7 +115,9 @@ func (s *ServerPoolTest) start() {
 		testQuery = func(node *enode.Node) int {
 			idx := testNodeIndex(node.ID())
 			n := &s.testNodes[idx]
+			s.lock.Lock()
 			canConnect := !n.connected && n.connectCycles != 0 && s.cycle >= n.nextConnCycle
+			s.lock.Unlock()
 			if s.preNegFail {
 				// simulate a scenario where UDP queries never work
 				s.beginWait()
@@ -155,7 +160,7 @@ func (s *ServerPoolTest) start() {
 	s.sp.unixTime = func() int64 { return int64(s.clock.Now()) / int64(time.Second) }
 	s.disconnect = make(map[int][]int)
 	s.sp.Start()
-	s.quit = make(chan struct{})
+	s.quit = make(chan chan struct{})
 	go func() {
 		last := int32(-1)
 		for {
@@ -167,15 +172,18 @@ func (s *ServerPoolTest) start() {
 					s.clock.Run(time.Second)
 				}
 				last = c
-			case <-s.quit:
+			case quit := <-s.quit:
+				close(quit)
 				return
 			}
 		}
 	}()
 }
 
 func (s *ServerPoolTest) stop() {
-	close(s.quit)
+	quit := make(chan struct{})
+	s.quit <- quit
+	<-quit
 	s.sp.Stop()
 	s.spi.Close()
 	for i := range s.testNodes {
@@ -234,7 +242,9 @@ func (s *ServerPoolTest) run() {
 		}
 		s.serviceCycles += s.servedConn
 		s.clock.Run(time.Second)
+		s.lock.Lock()
 		s.cycle++
+		s.lock.Unlock()
 	}
 }
 
```

### les/vflux/client/valuetracker.go
```diff
@@ -50,22 +50,22 @@ type NodeValueTracker struct {
 	lastTransfer         mclock.AbsTime
 	basket               serverBasket
 	reqCosts             []uint64
-	reqValues            *[]float64
+	reqValues            []float64
 }
 
 // UpdateCosts updates the node value tracker's request cost table
 func (nv *NodeValueTracker) UpdateCosts(reqCosts []uint64) {
 	nv.vt.lock.Lock()
 	defer nv.vt.lock.Unlock()
 
-	nv.updateCosts(reqCosts, &nv.vt.refBasket.reqValues, nv.vt.refBasket.reqValueFactor(reqCosts))
+	nv.updateCosts(reqCosts, nv.vt.refBasket.reqValues, nv.vt.refBasket.reqValueFactor(reqCosts))
 }
 
 // updateCosts updates the request cost table of the server. The request value factor
 // is also updated based on the given cost table and the current reference basket.
 // Note that the contents of the referenced reqValues slice will not change; a new
 // reference is passed if the values are updated by ValueTracker.
-func (nv *NodeValueTracker) updateCosts(reqCosts []uint64, reqValues *[]float64, rvFactor float64) {
+func (nv *NodeValueTracker) updateCosts(reqCosts []uint64, reqValues []float64, rvFactor float64) {
 	nv.lock.Lock()
 	defer nv.lock.Unlock()
 
@@ -112,7 +112,7 @@ func (nv *NodeValueTracker) Served(reqs []ServedRequest, respTime time.Duration)
 	var value float64
 	for _, r := range reqs {
 		nv.basket.add(r.ReqType, r.Amount, nv.reqCosts[r.ReqType]*uint64(r.Amount), expFactor)
-		value += (*nv.reqValues)[r.ReqType] * float64(r.Amount)
+		value += nv.reqValues[r.ReqType] * float64(r.Amount)
 	}
 	nv.rtStats.Add(respTime, value, expFactor)
 }
@@ -356,7 +356,7 @@ func (vt *ValueTracker) Register(id enode.ID) *NodeValueTracker {
 	reqTypeCount := len(vt.refBasket.reqValues)
 	nv.reqCosts = make([]uint64, reqTypeCount)
 	nv.lastTransfer = vt.clock.Now()
-	nv.reqValues = &vt.refBasket.reqValues
+	nv.reqValues = vt.refBasket.reqValues
 	nv.basket.init(reqTypeCount)
 
 	vt.connected[id] = nv
@@ -476,7 +476,7 @@ func (vt *ValueTracker) periodicUpdate() {
 	vt.refBasket.normalize()
 	vt.refBasket.updateReqValues()
 	for _, nv := range vt.connected {
-		nv.updateCosts(nv.reqCosts, &vt.refBasket.reqValues, vt.refBasket.reqValueFactor(nv.reqCosts))
+		nv.updateCosts(nv.reqCosts, vt.refBasket.reqValues, vt.refBasket.reqValueFactor(nv.reqCosts))
 	}
 	vt.saveToDb()
 }
```

### les/vflux/server/balance_tracker.go
```diff
@@ -223,8 +223,9 @@ func (bt *balanceTracker) BalanceOperation(id enode.ID, connAddress string, cb f
 		var nb *nodeBalance
 		if node := bt.ns.GetNode(id); node != nil {
 			nb, _ = bt.ns.GetField(node, bt.setup.balanceField).(*nodeBalance)
-		} else {
-			node = enode.SignNull(&enr.Record{}, id)
+		}
+		if nb == nil {
+			node := enode.SignNull(&enr.Record{}, id)
 			nb = bt.newNodeBalance(node, connAddress, false)
 		}
 		cb(nb)
```
