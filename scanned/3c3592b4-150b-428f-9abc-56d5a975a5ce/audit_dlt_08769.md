# [?] les: fixed selectPeer deadlock, improved request distribution

## Summary
Severity: Unknown
Chain: Scroll
Component: scroll-tech/go-ethereum
Published: 2016-12-15
Source: https://github.com/scroll-tech/go-ethereum/commit/93f9c023ccda2256079484d6c2a3159818ba6691
Type: security-commit

## Details
les: fixed selectPeer deadlock, improved request distribution
les/flowcontrol: using proper types for relative and absolute times

## Patch
### les/fetcher.go
```diff
@@ -125,7 +125,7 @@ func (f *lightFetcher) syncLoop() {
 	f.pm.wg.Add(1)
 	defer f.pm.wg.Done()
 
-	requestStarted := false
+	requesting := false
 	for {
 		select {
 		case <-f.pm.quitSync:
@@ -134,13 +134,13 @@ func (f *lightFetcher) syncLoop() {
 		// no further requests are necessary or possible
 		case newAnnounce := <-f.requestChn:
 			f.lock.Lock()
-			s := requestStarted
-			requestStarted = false
+			s := requesting
+			requesting = false
 			if !f.syncing && !(newAnnounce && s) {
-				if peer, node, amount := f.nextRequest(); node != nil {
-					requestStarted = true
-					reqID, started := f.request(peer, node, amount)
-					if started {
+				reqID := getNextReqID()
+				if peer, node, amount, retry := f.nextRequest(reqID); node != nil {
+					requesting = true
+					if reqID, ok := f.request(peer, reqID, node, amount); ok {
 						go func() {
 							time.Sleep(softRequestTimeout)
 							f.reqMu.Lock()
@@ -154,6 +154,14 @@ func (f *lightFetcher) syncLoop() {
 							f.requestChn <- false
 						}()
 					}
+				} else {
+					if retry {
+						requesting = true
+						go func() {
+							time.Sleep(time.Millisecond * 100)
+							f.requestChn <- false
+						}()
+					}
 				}
 			}
 			f.lock.Unlock()
@@ -344,10 +352,11 @@ func (f *lightFetcher) peerHasBlock(p *peer, hash common.Hash, number uint64) bo
 }
 
 // request initiates a header download request from a certain peer
-func (f *lightFetcher) request(p *peer, n *fetcherTreeNode, amount uint64) (uint64, bool) {
+func (f *lightFetcher) request(p *peer, reqID uint64, n *fetcherTreeNode, amount uint64) (uint64, bool) {
 	fp := f.peers[p]
 	if fp == nil {
 		glog.V(logger.Debug).Infof("request: unknown peer")
+		p.fcServer.DeassignRequest(reqID)
 		return 0, false
 	}
 	if fp.bestConfirmed == nil || fp.root == nil || !f.checkKnownNode(p, fp.root) {
@@ -357,10 +366,10 @@ func (f *lightFetcher) request(p *peer, n *fetcherTreeNode, amount uint64) (uint
 			f.pm.synchronise(p)
 			f.syncDone <- p
 		}()
+		p.fcServer.DeassignRequest(reqID)
 		return 0, false
 	}
 
-	reqID := getNextReqID()
 	n.requested = true
 	cost := p.GetRequestCost(GetBlockHeadersMsg, int(amount))
 	p.fcServer.SendRequest(reqID, cost)
@@ -400,7 +409,7 @@ func (f *lightFetcher) requestedID(reqID uint64) bool {
 
 // nextRequest selects the peer and announced head to be requested next, amount
 // to be downloaded starting from the head backwards is also returned
-func (f *lightFetcher) nextRequest() (*peer, *fetcherTreeNode, uint64) {
+func (f *lightFetcher) nextRequest(reqID uint64) (*peer, *fetcherTreeNode, uint64, bool) {
 	var (
 		bestHash   common.Hash
 		bestAmount uint64
@@ -420,44 +429,53 @@ func (f *lightFetcher) nextRequest() (*peer, *fetcherTreeNode, uint64) {
 		}
 	}
 	if bestTd == f.maxConfirmedTd {
-		return nil, nil, 0
+		return nil, nil, 0, false
 	}
 
-	peer := f.pm.serverPool.selectPeer(func(p *peer) (bool, uint64) {
+	peer, _, locked := f.pm.serverPool.selectPeer(reqID, func(p *peer) (bool, time.Duration) {
 		fp := f.peers[p]
 		if fp == nil || fp.nodeByHash[bestHash] == nil {
 			return false, 0
 		}
 		return true, p.fcServer.CanSend(p.GetRequestCost(GetBlockHeadersMsg, int(bestAmount)))
 	})
+	if !locked {
+		return nil, nil, 0, true
+	}
 	var node *fetcherTreeNode
 	if peer != nil {
 		node = f.peers[peer].nodeByHash[bestHash]
 	}
-	return peer, node, bestAmount
+	return peer, node, bestAmount, false
 }
 
 // deliverHeaders delivers header download request responses for processing
 func (f *lightFetcher) deliverHeaders(peer *peer, reqID uint64, headers []*types.Header) {
 	f.deliverChn <- fetchResponse{reqID: reqID, headers: headers, peer: peer}
 }
 
-// processResponse processes header download request responses
+// processResponse processes header download request responses, returns true if successful
 func (f *lightFetcher) processResponse(req fetchRequest, resp fetchResponse) bool {
 	if uint64(len(resp.headers)) != req.amount || resp.headers[0].Hash() != req.hash {
+		glog.V(logger.Debug).Infof("response mismatch %v %016x != %v %016x", len(resp.headers), resp.headers[0].Hash().Bytes()[:8], req.amount, req.hash[:8])
 		return false
 	}
 	headers := make([]*types.Header, req.amount)
 	for i, header := range resp.headers {
 		headers[int(req.amount)-1-i] = header
 	}
 	if _, err := f.chain.InsertHeaderChain(headers, 1); err != nil {
+		if err == core.BlockFutureErr {
+			return true
+		}
+		glog.V(logger.Debug).Infof("InsertHeaderChain error: %v", err)
 		return false
 	}
 	tds := make([]*big.Int, len(headers))
 	for i, header := range headers {
 		td := f.chain.GetTd(header.Hash(), header.Number.Uint64())
 		if td == nil {
+			glog.V(logger.Debug).Infof("TD not found for header %v of %v", i+1, len(headers))
 			return false
 		}
 		tds[i] = td
```

### les/flowcontrol/control.go
```diff
@@ -24,7 +24,7 @@ import (
 	"github.com/ethereum/go-ethereum/common/mclock"
 )
 
-const fcTimeConst = 1000000
+const fcTimeConst = time.Millisecond
 
 type ServerParams struct {
 	BufLimit, MinRecharge uint64
@@ -33,7 +33,7 @@ type ServerParams struct {
 type ClientNode struct {
 	params   *ServerParams
 	bufValue uint64
-	lastTime int64
+	lastTime mclock.AbsTime
 	lock     sync.Mutex
 	cm       *ClientManager
 	cmNode   *cmNode
@@ -44,7 +44,7 @@ func NewClientNode(cm *ClientManager, params *ServerParams) *ClientNode {
 		cm:       cm,
 		params:   params,
 		bufValue: params.BufLimit,
-		lastTime: getTime(),
+		lastTime: mclock.Now(),
 	}
 	node.cmNode = cm.addNode(node)
 	return node
@@ -54,12 +54,12 @@ func (peer *ClientNode) Remove(cm *ClientManager) {
 	cm.removeNode(peer.cmNode)
 }
 
-func (peer *ClientNode) recalcBV(time int64) {
+func (peer *ClientNode) recalcBV(time mclock.AbsTime) {
 	dt := uint64(time - peer.lastTime)
 	if time < peer.lastTime {
 		dt = 0
 	}
-	peer.bufValue += peer.params.MinRecharge * dt / fcTimeConst
+	peer.bufValue += peer.params.MinRecharge * dt / uint64(fcTimeConst)
 	if peer.bufValue > peer.params.BufLimit {
 		peer.bufValue = peer.params.BufLimit
 	}
@@ -70,7 +70,7 @@ func (peer *ClientNode) AcceptRequest() (uint64, bool) {
 	peer.lock.Lock()
 	defer peer.lock.Unlock()
 
-	time := getTime()
+	time := mclock.Now()
 	peer.recalcBV(time)
 	return peer.bufValue, peer.cm.accept(peer.cmNode, time)
 }
@@ -79,7 +79,7 @@ func (peer *ClientNode) RequestProcessed(cost uint64) (bv, realCost uint64) {
 	peer.lock.Lock()
 	defer peer.lock.Unlock()
 
-	time := getTime()
+	time := mclock.Now()
 	peer.recalcBV(time)
 	peer.bufValue -= cost
 	peer.recalcBV(time)
@@ -94,66 +94,127 @@ func (peer *ClientNode) RequestProcessed(cost uint64) (bv, realCost uint64) {
 }
 
 type ServerNode struct {
-	bufEstimate uint64
-	lastTime    int64
-	params      *ServerParams
-	sumCost     uint64            // sum of req costs sent to this server
-	pending     map[uint64]uint64 // value = sumCost after sending the given req
-	lock        sync.RWMutex
+	bufEstimate     uint64
+	lastTime        mclock.AbsTime
+	params          *ServerParams
+	sumCost         uint64            // sum of req costs sent to this server
+	pending         map[uint64]uint64 // value = sumCost after sending the given req
+	assignedRequest uint64            // when != 0, only the request with the given ID can be sent to this peer
+	assignToken     chan struct{}     // send to this channel before assigning, read from it after deassigning
+	lock            sync.RWMutex
 }
 
 func NewServerNode(params *ServerParams) *ServerNode {
 	return &ServerNode{
 		bufEstimate: params.BufLimit,
-		lastTime:    getTime(),
+		lastTime:    mclock.Now(),
 		params:      params,
 		pending:     make(map[uint64]uint64),
+		assignToken: make(chan struct{}, 1),
 	}
 }
 
-func getTime() int64 {
-	return int64(mclock.Now())
-}
-
-func (peer *ServerNode) recalcBLE(time int64) {
+func (peer *ServerNode) recalcBLE(time mclock.AbsTime) {
 	dt := uint64(time - peer.lastTime)
 	if time < peer.lastTime {
 		dt = 0
 	}
-	peer.bufEstimate += peer.params.MinRecharge * dt / fcTimeConst
+	peer.bufEstimate += peer.params.MinRecharge * dt / uint64(fcTimeConst)
 	if peer.bufEstimate > peer.params.BufLimit {
 		peer.bufEstimate = peer.params.BufLimit
 	}
 	peer.lastTime = time
 }
 
-func (peer *ServerNode) canSend(maxCost uint64) uint64 {
+// safetyMargin is added to the flow control waiting time when estimated buffer value is low
+const safetyMargin = time.Millisecond * 200
+
+func (peer *ServerNode) canSend(maxCost uint64) time.Duration {
+	maxCost += uint64(safetyMargin) * peer.params.MinRecharge / uint64(fcTimeConst)
+	if maxCost > peer.params.BufLimit {
+		maxCost = peer.params.BufLimit
+	}
 	if peer.bufEstimate >= maxCost {
 		return 0
 	}
-	return (maxCost - peer.bufEstimate) * fcTimeConst / peer.params.MinRecharge
+	return time.Duration((maxCost - peer.bufEstimate) * uint64(fcTimeConst) / peer.params.MinRecharge)
 }
 
-func (peer *ServerNode) CanSend(maxCost uint64) uint64 {
+// CanSend returns the minimum waiting time required before sending a request
+// with the given maximum estimated cost
+func (peer *ServerNode) CanSend(maxCost uint64) time.Duration {
 	peer.lock.RLock()
 	defer peer.lock.RUnlock()
 
 	return peer.canSend(maxCost)
 }
 
+// AssignRequest tries to assign the server node to the given request, guaranteeing
+// that once it returns true, no request will be sent to the node before this one
+func (peer *ServerNode) AssignRequest(reqID uint64) bool {
+	select {
+	case peer.assignToken <- struct{}{}:
+	default:
+		return false
+	}
+	peer.lock.Lock()
+	peer.assignedRequest = reqID
+	peer.lock.Unlock()
+	return true
+}
+
+// MustAssignRequest waits until the node can be assigned to the given request.
+// It is always guaranteed that assignments are released in a short amount of time.
+func (peer *ServerNode) MustAssignRequest(reqID uint64) {
+	peer.assignToken <- struct{}{}
+	peer.lock.Lock()
+	peer.assignedRequest = reqID
+	peer.lock.Unlock()
+}
+
+// DeassignRequest releases a request assignment in case the planned request
+// is not being sent.
+func (peer *ServerNode) DeassignRequest(reqID uint64) {
+	peer.lock.Lock()
+	if peer.assignedRequest == reqID {
+		peer.assignedRequest = 0
+		<-peer.assignToken
+	}
+	peer.lock.Unlock()
+}
+
+// IsAssigned returns true if the server node has already been assigned to a request
+// (note that this function returning false does not guarantee that you can assign a request
+// immediately afterwards, its only purpose is to help peer selection)
+func (peer *ServerNode) IsAssigned() bool {
+	peer.lock.RLock()
+	locked := peer.assignedRequest != 0
+	peer.lock.RUnlock()
+	return locked
+}
+
 // blocks until request can be sent
 func (peer *ServerNode) SendRequest(reqID, maxCost uint64) {
 	peer.lock.Lock()
 	defer peer.lock.Unlock()
 
-	peer.recalcBLE(getTime())
-	for peer.bufEstimate < maxCost {
-		wait := time.Duration(peer.canSend(maxCost))
+	if peer.assignedRequest != reqID {
+		peer.lock.Unlock()
+		peer.MustAssignRequest(reqID)
+		peer.lock.Lock()
+	}
+
+	peer.recalcBLE(mclock.Now())
+	wait := peer.canSend(maxCost)
+	for wait > 0 {
 		peer.lock.Unlock()
 		time.Sleep(wait)
 		peer.lock.Lock()
-		peer.recalcBLE(getTime())
+		peer.recalcBLE(mclock.Now())
+		wait = peer.canSend(maxCost)
 	}
+	peer.assignedRequest = 0
+	<-peer.assignToken
 	peer.bufEstimate -= maxCost
 	peer.sumCost += maxCost
 	if reqID >= 0 {
@@ -162,14 +223,18 @@ func (peer *ServerNode) SendRequest(reqID, maxCost uint64) {
 }
 
 func (peer *ServerNode) GotReply(reqID, bv uint64) {
+
 	peer.lock.Lock()
 	defer peer.lock.Unlock()
 
+	if bv > peer.params.BufLimit {
+		bv = peer.params.BufLimit
+	}
 	sc, ok := peer.pending[reqID]
 	if !ok {
 		return
 	}
 	delete(peer.pending, reqID)
 	peer.bufEstimate = bv - (peer.sumCost - sc)
-	peer.lastTime = getTime()
+	peer.lastTime = mclock.Now()
 }
```

### les/flowcontrol/manager.go
```diff
@@ -20,22 +20,23 @@ package flowcontrol
 import (
 	"sync"
 	"time"
+
+	"github.com/ethereum/go-ethereum/common/mclock"
 )
 
 const rcConst = 1000000
 
 type cmNode struct {
-	node                       *ClientNode
-	lastUpdate                 int64
-	reqAccepted                int64
-	serving, recharging        bool
-	rcWeight                   uint64
-	rcValue, rcDelta           int64
-	finishRecharge, startValue int64
+	node                         *ClientNode
+	lastUpdate                   mclock.AbsTime
+	serving, recharging          bool
+	rcWeight                     uint64
+	rcValue, rcDelta, startValue int64
+	finishRecharge               mclock.AbsTime
 }
 
-func (node *cmNode) update(time int64) {
-	dt := time - node.lastUpdate
+func (node *cmNode) update(time mclock.AbsTime) {
+	dt := int64(time - node.lastUpdate)
 	node.rcValue += node.rcDelta * dt / rcConst
 	node.lastUpdate = time
 	if node.recharging && time >= node.finishRecharge {
@@ -62,7 +63,7 @@ func (node *cmNode) set(serving bool, simReqCnt, sumWeight uint64) {
 	}
 	if node.recharging {
 		node.rcDelta = -int64(node.node.cm.rcRecharge * node.rcWeight / sumWeight)
-		node.finishRecharge = node.lastUpdate + node.rcValue*rcConst/(-node.rcDelta)
+		node.finishRecharge = node.lastUpdate + mclock.AbsTime(node.rcValue*rcConst/(-node.rcDelta))
 	}
 }
 
@@ -73,7 +74,7 @@ type ClientManager struct {
 	maxSimReq, maxRcSum              uint64
 	rcRecharge                       uint64
 	resumeQueue                      chan chan bool
-	time                             int64
+	time                             mclock.AbsTime
 }
 
 func NewClientManager(rcTarget, maxSimReq, maxRcSum uint64) *ClientManager {
@@ -98,7 +99,7 @@ func (self *ClientManager) Stop() {
 }
 
 func (self *ClientManager) addNode(cnode *ClientNode) *cmNode {
-	time := getTime()
+	time := mclock.Now()
 	node := &cmNode{
 		node:           cnode,
 		lastUpdate:     time,
@@ -109,22 +110,22 @@ func (self *ClientManager) addNode(cnode *ClientNode) *cmNode {
 	defer self.lock.Unlock()
 
 	self.nodes[node] = struct{}{}
-	self.update(getTime())
+	self.update(mclock.Now())
 	return node
 }
 
 func (self *ClientManager) removeNode(node *cmNode) {
 	self.lock.Lock()
 	defer self.lock.Unlock()
 
-	time := getTime()
+	time := mclock.Now()
 	self.stop(node, time)
 	delete(self.nodes, node)
 	self.update(time)
 }
 
 // recalc sumWeight
-func (self *ClientManager) updateNodes(time int64) (rce bool) {
+func (self *ClientManager) updateNodes(time mclock.AbsTime) (rce bool) {
 	var sumWeight, rcSum uint64
 	for node, _ := range self.nodes {
 		rc := node.recharging
@@ -142,7 +143,7 @@ func (self *ClientManager) updateNodes(time int64) (rce bool) {
 	return
 }
 
-func (self *ClientManager) update(time int64) {
+func (self *ClientManager) update(time mclock.AbsTime) {
 	for {
 		firstTime := time
 		for node, _ := range self.nodes {
@@ -172,7 +173,7 @@ func (self *ClientManager) queueProc() {
 		for {
 			time.Sleep(time.Millisecond * 10)
 			self.lock.Lock()
-			self.update(getTime())
+			self.update(mclock.Now())
 			cs := self.canStartReq()
 			self.lock.Unlock()
 			if cs {
@@ -183,7 +184,7 @@ func (self *ClientManager) queueProc() {
 	}
 }
 
-func (self *ClientManager) accept(node *cmNode, time int64) bool {
+func (self *ClientManager) accept(node *cmNode, time mclock.AbsTime) bool {
 	self.lock.Lock()
 	defer self.lock.Unlock()
 
@@ -205,7 +206,7 @@ func (self *ClientManager) accept(node *cmNode, time int64) bool {
 	return true
 }
 
-func (self *ClientManager) stop(node *cmNode, time int64) {
+func (self *ClientManager) stop(node *cmNode, time mclock.AbsTime) {
 	if node.serving {
 		self.update(time)
 		self.simReqCnt--
@@ -214,7 +215,7 @@ func (self *ClientManager) stop(node *cmNode, time int64) {
 	}
 }
 
-func (self *ClientManager) processed(node *cmNode, time int64) (rcValue, rcCost uint64) {
+func (self *ClientManager) processed(node *cmNode, time mclock.AbsTime) (rcValue, rcCost uint64) {
 	self.lock.Lock()
 	defer self.lock.Unlock()
 
```

### les/handler.go
```diff
@@ -24,6 +24,7 @@ import (
 	"math/big"
 	"net"
 	"sync"
+	"time"
 
 	"github.com/ethereum/go-ethereum/common"
 	"github.com/ethereum/go-ethereum/core"
@@ -228,6 +229,12 @@ func (pm *ProtocolManager) removePeer(id string) {
 	if peer == nil {
 		return
 	}
+	if err := pm.peers.Unregister(id); err != nil {
+		if err == errNotRegistered {
+			return
+		}
+		glog.V(logger.Error).Infoln("Removal failed:", err)
+	}
 	glog.V(logger.Debug).Infoln("Removing peer", id)
 
 	// Unregister the peer from the downloader and Ethereum peer set
@@ -241,9 +248,6 @@ func (pm *ProtocolManager) removePeer(id string) {
 			pm.fetcher.removePeer(peer)
 		}
 	}
-	if err := pm.peers.Unregister(id); err != nil {
-		glog.V(logger.Error).Infoln("Removal failed:", err)
-	}
 	// Hard disconnect at the networking layer
 	if peer != nil {
 		peer.Peer.Disconnect(p2p.DiscUselessPeer)
@@ -340,12 +344,14 @@ func (pm *ProtocolManager) handle(p *peer) error {
 		requestHeadersByHash := func(origin common.Hash, amount int, skip int, reverse bool) error {
 			reqID := getNextReqID()
 			cost := p.GetRequestCost(GetBlockHeadersMsg, amount)
+			p.fcServer.MustAssignRequest(reqID)
 			p.fcServer.SendRequest(reqID, cost)
 			return p.RequestHeadersByHash(reqID, cost, origin, amount, skip, reverse)
 		}
 		requestHeadersByNumber := func(origin uint64, amount int, skip int, reverse bool) error {
 			reqID := getNextReqID()
 			cost := p.GetRequestCost(GetBlockHeadersMsg, amount)
+			p.fcServer.MustAssignRequest(reqID)
 			p.fcServer.SendRequest(reqID, cost)
 			return p.RequestHeadersByNumber(reqID, cost, origin, amount, skip, reverse)
 		}
@@ -404,26 +410,23 @@ func (pm *ProtocolManager) handleMsg(p *peer) error {
 		return err
 	}
 
-	var costs *requestCosts
-	var reqCnt, maxReqs int
-
 	glog.V(logger.Debug).Infoln("msg:", msg.Code, msg.Size)
-	if rc, ok := p.fcCosts[msg.Code]; ok { // check if msg is a supported request type
-		costs = rc
-		if p.fcClient == nil {
-			return errResp(ErrRequestRejected, "")
+
+	costs := p.fcCosts[msg.Code]
+	reject := func(reqCnt, maxCnt uint64) bool {
+		if p.fcClient == nil || reqCnt > maxCnt {
+			return true
 		}
-		bv, ok := p.fcClient.AcceptRequest()
-		if !ok || bv < costs.baseCost {
-			return errResp(ErrRequestRejected, "")
+		bufValue, _ := p.fcClient.AcceptRequest()
+		cost := costs.baseCost + reqCnt*costs.reqCost
+		if cost > pm.server.defParams.BufLimit {
+			cost = pm.server.defParams.BufLimit
 		}
-		maxReqs = 10000
-		if bv < pm.server.defParams.BufLimit {
-			d := bv - costs.baseCost
-			if d/10000 < costs.reqCost {
-				maxReqs = int(d / costs.reqCost)
-			}
+		if cost > bufValue {
+			glog.V(logger.Error).Infof("Request from %v came %v too early", p.id, time.Duration((cost-bufValue)*1000000/pm.server.defParams.MinRecharge))
+			return true
 		}
+		return false
 	}
 
 	if msg.Size > ProtocolMaxMsgSize {
@@ -450,7 +453,7 @@ func (pm *ProtocolManager) handleMsg(p *peer) error {
 		}
 		glog.V(logger.Detail).Infoln("AnnounceMsg:", req.Number, req.Hash, req.Td, req.ReorgDepth)
 		if pm.fetcher != nil {
-			go pm.fetcher.announce(p, &req)
+			pm.fetcher.announce(p, &req)
 		}
 
 	case GetBlockHeadersMsg:
@@ -465,7 +468,7 @@ func (pm *ProtocolManager) handleMsg(p *peer) error {
 		}
 
 		query := req.Query
-		if query.Amount > uint64(maxReqs) || query.Amount > MaxHeaderFetch {
+		if reject(query.Amount, MaxHeaderFetch) {
 			return errResp(ErrRequestRejected, "")
 		}
 
@@ -573,8 +576,8 @@ func (pm *ProtocolManager) handleMsg(p *peer) error {
 			bytes  int
 			bodies []rlp.RawValue
 		)
-		reqCnt = len(req.Hashes)
-		if reqCnt > maxReqs || reqCnt > MaxBodyFetch {
+		reqCnt := len(req.Hashes)
+		if reject(uint64(reqCnt), MaxBodyFetch) {
 			return errResp(ErrRequestRejected, "")
 		}
 		for _, hash := range req.Hashes {
@@ -627,8 +630,8 @@ func (pm *ProtocolManager) handleMsg(p *peer) error {
 			bytes int
 			data  [][]byte
 		)
-		reqCnt = len(req.Reqs)
-		if reqCnt > maxReqs || reqCnt > MaxCodeFetch {
+		reqCnt := len(req.Reqs)
+		if reject(uint64(reqCnt), MaxCodeFetch) {
 			return errResp(ErrRequestRejected, "")
 		}
 		for _, req := range req.Reqs {
@@ -688,8 +691,8 @@ func (pm *ProtocolManager) handleMsg(p *peer) error {
 			bytes    int
 			receipts []rlp.RawValue
 		)
-		reqCnt = len(req.Hashes)
-		if reqCnt > maxReqs || reqCnt > MaxReceiptFetch {
+		reqCnt := len(req.Hashes)
+		if reject(uint64(reqCnt), MaxReceiptFetch) {
 			return errResp(ErrRequestRejected, "")
 		}
 		for _, hash := range req.Hashes {
@@ -751,8 +754,8 @@ func (pm *ProtocolManager) handleMsg(p *peer) error {
 			bytes  int
 			proofs proofsData
 		)
-		reqCnt = len(req.Reqs)
-		if reqCnt > maxReqs || reqCnt > MaxProofsFetch {
+		reqCnt := len(req.Reqs)
+		if reject(uint64(reqCnt), MaxProofsFetch) {
 			return errResp(ErrRequestRejected, "")
 		}
 		for _, req := range req.Reqs {
@@ -818,8 +821,8 @@ func (pm *ProtocolManager) handleMsg(p *peer) error {
 			bytes  int
 			proofs []ChtResp
 		)
-		reqCnt = len(req.Reqs)
-		if reqCnt > maxReqs || reqCnt > MaxHeaderProofsFetch {
+		reqCnt := len(req.Reqs)
+		if reject(uint64(reqCnt), MaxHeaderProofsFetch) {
 			return errResp(ErrRequestRejected, "")
 		}
 		for _, req := range req.Reqs {
@@ -872,8 +875,8 @@ func (pm *ProtocolManager) handleMsg(p *peer) error {
 		if err := msg.Decode(&txs); err != nil {
 			return errResp(ErrDecode, "msg %v: %v", msg, err)
 		}
-		reqCnt = len(txs)
-		if reqCnt > maxReqs || reqCnt > MaxTxSend {
+		reqCnt := len(txs)
+		if reject(uint64(reqCnt), MaxTxSend) {
 			return errResp(ErrRequestRejected, "")
 		}
 
```

### les/helper_test.go
```diff
@@ -336,10 +336,23 @@ func (p *testPeer) close() {
 	p.app.Close()
 }
 
-type testServerPool peer
+type testServerPool struct {
+	peer *peer
+	lock sync.RWMutex
+}
+
+func (p *testServerPool) setPeer(peer *peer) {
+	p.lock.Lock()
+	defer p.lock.Unlock()
+
+	p.peer = peer
+}
+
+func (p *testServerPool) selectPeerWait(uint64, func(*peer) (bool, time.Duration), <-chan struct{}) *peer {
+	p.lock.RLock()
+	defer p.lock.RUnlock()
 
-func (p *testServerPool) selectPeer(func(*peer) (bool, uint64)) *peer {
-	return (*peer)(p)
+	return p.peer
 }
 
 func (p *testServerPool) adjustResponseTime(*poolEntry, time.Duration, bool) {
```

### les/odr.go
```diff
@@ -40,7 +40,7 @@ var (
 type peerDropFn func(id string)
 
 type odrPeerSelector interface {
-	selectPeer(func(*peer) (bool, uint64)) *peer
+	selectPeerWait(uint64, func(*peer) (bool, time.Duration), <-chan struct{}) *peer
 	adjustResponseTime(*poolEntry, time.Duration, bool)
 }
 
@@ -116,6 +116,7 @@ func (self *LesOdr) Deliver(peer *peer, msg *Msg) error {
 	if req.valFunc(self.db, msg) {
 		close(delivered)
 		req.lock.Lock()
+		delete(req.sentTo, peer)
 		if req.answered != nil {
 			close(req.answered)
 			req.answered = nil
@@ -150,6 +151,7 @@ func (self *LesOdr) requestPeer(req *sentReq, peer *peer, delivered, timeout cha
 	select {
 	case <-delivered:
 	case <-time.After(hardRequestTimeout):
+		glog.V(logger.Debug).Infof("ODR hard request timeout from peer %v", peer.id)
 		go self.removePeer(peer.id)
 	case <-self.stop:
 		return
@@ -187,12 +189,12 @@ func (self *LesOdr) networkRequest(ctx context.Context, lreq LesOdrRequest) erro
 	for {
 		var p *peer
 		if self.serverPool != nil {
-			p = self.serverPool.selectPeer(func(p *peer) (bool, uint64) {
-				if !lreq.CanSend(p) {
+			p = self.serverPool.selectPeerWait(reqID, func(p *peer) (bool, time.Duration) {
+				if _, ok := exclude[p]; ok || !lreq.CanSend(p) {
 					return false, 0
 				}
 				return true, p.fcServer.CanSend(lreq.GetCost(p))
-			})
+			}, ctx.Done())
 		}
 		if p == nil {
 			select {
```

### les/odr_test.go
```diff
@@ -160,7 +160,8 @@ func testOdr(t *testing.T, protocol int, expFail uint64, fn odrTestFn) {
 	pm, db, odr := newTestProtocolManagerMust(t, false, 4, testChainGen)
 	lpm, ldb, odr := newTestProtocolManagerMust(t, true, 0, nil)
 	_, err1, lpeer, err2 := newTestPeerPair("peer", protocol, pm, lpm)
-	pool := (*testServerPool)(lpeer)
+	pool := &testServerPool{}
+	pool.setPeer(lpeer)
 	odr.serverPool = pool
 	select {
 	case <-time.After(time.Millisecond * 100):
@@ -190,13 +191,13 @@ func testOdr(t *testing.T, protocol int, expFail uint64, fn odrTestFn) {
 	}
 
 	// temporarily remove peer to test odr fails
-	odr.serverPool = nil
+	pool.setPeer(nil)
 	// expect retrievals to fail (except genesis block) without a les peer
 	test(expFail)
-	odr.serverPool = pool
+	pool.setPeer(lpeer)
 	// expect all retrievals to pass
 	test(5)
-	odr.serverPool = nil
+	pool.setPeer(nil)
 	// still expect all retrievals to pass, now data should be cached locally
 	test(5)
 }
```

### les/peer.go
```diff
@@ -241,7 +241,9 @@ func (p *peer) RequestHeaderProofs(reqID, cost uint64, reqs []*ChtReq) error {
 
 func (p *peer) SendTxs(cost uint64, txs types.Transactions) error {
 	glog.V(logger.Debug).Infof("%v relaying %v txs", p, len(txs))
-	p.fcServer.SendRequest(0, cost)
+	reqID := getNextReqID()
+	p.fcServer.MustAssignRequest(reqID)
+	p.fcServer.SendRequest(reqID, cost)
 	return p2p.Send(p.rw, SendTxMsg, txs)
 }
 
```

### les/request_test.go
```diff
@@ -71,7 +71,8 @@ func testAccess(t *testing.T, protocol int, fn accessTestFn) {
 	pm, db, _ := newTestProtocolManagerMust(t, false, 4, testChainGen)
 	lpm, ldb, odr := newTestProtocolManagerMust(t, true, 0, nil)
 	_, err1, lpeer, err2 := newTestPeerPair("peer", protocol, pm, lpm)
-	pool := (*testServerPool)(lpeer)
+	pool := &testServerPool{}
+	pool.setPeer(lpeer)
 	odr.serverPool = pool
 	select {
 	case <-time.After(time.Millisecond * 100):
@@ -102,10 +103,10 @@ func testAccess(t *testing.T, protocol int, fn accessTestFn) {
 	}
 
 	// temporarily remove peer to test odr fails
-	odr.serverPool = nil
+	pool.setPeer(nil)
 	// expect retrievals to fail (except genesis block) without a les peer
 	test(0)
-	odr.serverPool = pool
+	pool.setPeer(lpeer)
 	// expect all retrievals to pass
 	test(5)
 }
```

### les/serverpool.go
```diff
@@ -265,33 +265,77 @@ func (pool *serverPool) adjustResponseTime(entry *poolEntry, time time.Duration,
 type selectPeerItem struct {
 	peer   *peer
 	weight int64
+	wait   time.Duration
 }
 
 func (sp selectPeerItem) Weight() int64 {
 	return sp.weight
 }
 
-// selectPeer selects a suitable peer for a request
-func (pool *serverPool) selectPeer(canSend func(*peer) (bool, uint64)) *peer {
+// selectPeer selects a suitable peer for a request, also returning a necessary waiting time to perform the request
+// and a "locked" flag meaning that the request has been assigned to the given peer and its execution is guaranteed
+// after the given waiting time. If locked flag is false, selectPeer should be called again after the waiting time.
+func (pool *serverPool) selectPeer(reqID uint64, canSend func(*peer) (bool, time.Duration)) (*peer, time.Duration, bool) {
 	pool.lock.Lock()
-	defer pool.lock.Unlock()
-
+	type selectPeer struct {
+		peer         *peer
+		rstat, tstat float64
+	}
+	var list []selectPeer
 	sel := newWeightedRandomSelect()
 	for _, entry := range pool.entries {
 		if entry.state == psRegistered {
-			p := entry.peer
-			ok, cost := canSend(p)
-			if ok {
-				w := int64(1000000000 * (peerSelectMinWeight + math.Exp(-(entry.responseStats.recentAvg()+float64(cost))/float64(responseScoreTC))*math.Pow((1-entry.timeoutStats.recentAvg()), timeoutPow)))
-				sel.update(selectPeerItem{peer: p, weight: w})
+			if !entry.peer.fcServer.IsAssigned() {
+				list = append(list, selectPeer{entry.peer, entry.responseStats.recentAvg(), entry.timeoutStats.recentAvg()})
 			}
 		}
 	}
+	pool.lock.Unlock()
+
+	for _, sp := range list {
+		ok, wait := canSend(sp.peer)
+		if ok {
+			w := int64(1000000000 * (peerSelectMinWeight + math.Exp(-(sp.rstat+float64(wait))/float64(responseScoreTC))*math.Pow((1-sp.tstat), timeoutPow)))
+			sel.update(selectPeerItem{peer: sp.peer, weight: w, wait: wait})
+		}
+	}
 	choice := sel.choose()
 	if choice == nil {
-		return nil
+		return nil, 0, false
+	}
+	peer, wait := choice.(selectPeerItem).peer, choice.(selectPeerItem).wait
+	locked := false
+	if wait < time.Millisecond*100 {
+		if peer.fcServer.AssignRequest(reqID) {
+			ok, w := canSend(peer)
+			wait = time.Duration(w)
+			if ok && wait < time.Millisecond*100 {
+				locked = true
+			} else {
+				peer.fcServer.DeassignRequest(reqID)
+				wait = time.Millisecond * 100
+			}
+		}
+	} else {
+		wait = time.Millisecond * 100
+	}
+	return peer, wait, locked
+}
+
+// selectPeer selects a suitable peer for a request, waiting until an assignment to
+// the request is guaranteed or the process is aborted.
+func (pool *serverPool) selectPeerWait(reqID uint64, canSend func(*peer) (bool, time.Duration), abort <-chan struct{}) *peer {
+	for {
+		peer, wait, locked := pool.selectPeer(reqID, canSend)
+		if locked {
+			return peer
+		}
+		select {
+		case <-abort:
+			return nil
+		case <-time.After(wait):
+		}
 	}
-	return choice.(selectPeerItem).peer
 }
 
 // eventLoop handles pool events and mutex locking for all internal functions
```
