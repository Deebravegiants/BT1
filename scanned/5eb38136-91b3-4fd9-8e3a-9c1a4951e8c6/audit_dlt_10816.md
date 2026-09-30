# [?] gossip: data race fix

## Summary
Severity: Unknown
Chain: Sonic
Component: 0xsoniclabs/sonic
Published: 2019-08-27
Source: https://github.com/0xsoniclabs/sonic/commit/d9b3226f3c19d5302157c73586f201c0001edf3d
Type: security-commit

## Details
gossip: data race fix

Merge pull request #308 from sfxdxdev/data-race-fix

## Patch
### src/gossip/apply_genesis.go
```diff
@@ -16,7 +16,7 @@ func (s *Store) ApplyGenesis(genesis *genesis.Genesis) (genesisFiWitness hash.Ev
 		dummyFiWitness := inter.NewEvent()
 		// for nice-looking ID
 		dummyFiWitness.Epoch = 0
-		dummyFiWitness.Lamport = idx.Lamport(poset.SuperFrameLen)
+		dummyFiWitness.Lamport = idx.Lamport(poset.EpochLen)
 		// actual data hashed
 		dummyFiWitness.Extra = genesis.ExtraData
 		dummyFiWitness.ClaimedTime = header.Time
```

### src/gossip/consensus.go
```diff
@@ -22,8 +22,8 @@ type Consensus interface {
 	Prepare(e *inter.Event) *inter.Event
 	// LastBlock returns current block.
 	LastBlock() (idx.Block, hash.Event)
-	// CurrentSuperFrame returns current SuperFrameN.
-	CurrentSuperFrameN() idx.SuperFrame
+	// CurrentEpoch returns current EpochN.
+	CurrentEpochN() idx.Epoch
 	// GetMembers returns members of current super-frame.
 	GetMembers() pos.Members
 
```

### src/gossip/emitter.go
```diff
@@ -27,7 +27,7 @@ type Emitter struct {
 
 	myAddr     common.Address
 	privateKey *ecdsa.PrivateKey
-	prevEpoch  idx.SuperFrame
+	prevEpoch  idx.Epoch
 
 	onEmitted func(e *inter.Event)
 
@@ -97,7 +97,7 @@ func (em *Emitter) createEvent() *inter.Event {
 	}
 
 	var (
-		epoch      = em.engine.CurrentSuperFrameN()
+		epoch      = em.engine.CurrentEpochN()
 		seq        idx.Event
 		parents    hash.Events
 		maxLamport idx.Lamport
```

### src/gossip/handler.go
```diff
@@ -53,7 +53,7 @@ func checkLenLimits(size int, v interface{}) error {
 }
 
 type dagNotifier interface {
-	SubscribeNewEpoch(ch chan<- idx.SuperFrame) event.Subscription
+	SubscribeNewEpoch(ch chan<- idx.Epoch) event.Subscription
 	SubscribeNewPack(ch chan<- idx.Pack) event.Subscription
 	SubscribeNewEmitted(ch chan<- *inter.Event) event.Subscription
 }
@@ -85,7 +85,7 @@ type ProtocolManager struct {
 	emittedEventsSub event.Subscription
 	newPacksCh       chan idx.Pack
 	newPacksSub      event.Subscription
-	newEpochsCh      chan idx.SuperFrame
+	newEpochsCh      chan idx.Epoch
 	newEpochsSub     event.Subscription
 
 	// channels for fetcher, syncer, txsyncLoop
@@ -198,7 +198,7 @@ func (pm *ProtocolManager) onlyInterestedEvents(ids hash.Events) hash.Events {
 	}
 	pm.engineMu.RLock()
 	defer pm.engineMu.RUnlock()
-	epoch := pm.engine.CurrentSuperFrameN()
+	epoch := pm.engine.CurrentEpochN()
 
 	interested := make(hash.Events, 0, len(ids))
 	for _, id := range ids {
@@ -281,7 +281,7 @@ func (pm *ProtocolManager) Start(maxPeers int) {
 		pm.newPacksCh = make(chan idx.Pack, 4)
 		pm.newPacksSub = pm.notifier.SubscribeNewPack(pm.newPacksCh)
 		// epoch changes
-		pm.newEpochsCh = make(chan idx.SuperFrame, 4)
+		pm.newEpochsCh = make(chan idx.Epoch, 4)
 		pm.newEpochsSub = pm.notifier.SubscribeNewEpoch(pm.newEpochsCh)
 	}
 
@@ -329,7 +329,7 @@ func (pm *ProtocolManager) newPeer(pv int, p *p2p.Peer, rw p2p.MsgReadWriter) *p
 
 func (pm *ProtocolManager) myProgress() PeerProgress {
 	blockI, block := pm.engine.LastBlock()
-	epoch := pm.engine.CurrentSuperFrameN()
+	epoch := pm.engine.CurrentEpochN()
 	return PeerProgress{
 		Epoch:        epoch,
 		NumOfBlocks:  blockI,
@@ -392,7 +392,7 @@ func (pm *ProtocolManager) handleMsg(p *peer) error {
 	}
 	defer msg.Discard()
 
-	myEpoch := pm.engine.CurrentSuperFrameN()
+	myEpoch := pm.engine.CurrentEpochN()
 	peerDwnlr := pm.downloader.Peer(p.id)
 
 	// Handle the message depending on its contents
@@ -409,8 +409,8 @@ func (pm *ProtocolManager) handleMsg(p *peer) error {
 		if len(progress.LastPackInfo.Heads) > hardLimitItems {
 			return errResp(ErrMsgTooLarge, "%v", msg)
 		}
-		p.progress = progress
-		if p.progress.Epoch == myEpoch {
+		p.SetProgress(progress)
+		if progress.Epoch == myEpoch {
 			atomic.StoreUint32(&pm.synced, 1) // Mark initial sync done on any peer which has the same epoch
 		}
 
@@ -730,7 +730,7 @@ func (pm *ProtocolManager) onNewEpochLoop() {
 	for {
 		select {
 		case myEpoch := <-pm.newEpochsCh:
-			peerEpoch := func(peer string) idx.SuperFrame {
+			peerEpoch := func(peer string) idx.Epoch {
 				p := pm.peers.Peer(peer)
 				if p == nil {
 					return 0
@@ -768,7 +768,7 @@ func (pm *ProtocolManager) txBroadcastLoop() {
 type NodeInfo struct {
 	Network     uint64      `json:"network"` // network ID
 	Genesis     common.Hash `json:"genesis"` // SHA3 hash of the host's genesis object
-	Epoch       idx.SuperFrame
+	Epoch       idx.Epoch
 	NumOfEvents idx.Event
 	//Config  *params.ChainConfig `json:"config"`  // Chain configuration for the fork rules
 }
@@ -778,6 +778,6 @@ func (pm *ProtocolManager) NodeInfo() *NodeInfo {
 	return &NodeInfo{
 		Network: pm.config.Net.NetworkId,
 		Genesis: pm.engine.GetGenesisHash(),
-		Epoch:   pm.engine.CurrentSuperFrameN(),
+		Epoch:   pm.engine.CurrentEpochN(),
 	}
 }
```

### src/gossip/helper_test.go
```diff
@@ -128,7 +128,7 @@ func newTestPeer(name string, version int, pm *ProtocolManager, shake bool) (*te
 		var (
 			genesis       = pm.engine.GetGenesisHash()
 			blockI, block = pm.engine.LastBlock()
-			epoch         = pm.engine.CurrentSuperFrameN()
+			epoch         = pm.engine.CurrentEpochN()
 			myProgress    = &PeerProgress{
 				Epoch:        epoch,
 				NumOfBlocks:  blockI,
```

### src/gossip/pack.go
```diff
@@ -18,10 +18,10 @@ const (
 	maxPackEventsNum = softLimitItems
 )
 
-func (s *Service) packs_onNewEvent(e *inter.Event, epoch idx.SuperFrame) {
+func (s *Service) packs_onNewEvent(e *inter.Event, epoch idx.Epoch) {
 	// due to default values, we don't need to explicitly set values at a start of an epoch
 	packIdx := s.store.GetPacksNumOrDefault(epoch)
-	packInfo := s.store.GetPackInfoOrDefault(s.engine.CurrentSuperFrameN(), packIdx)
+	packInfo := s.store.GetPackInfoOrDefault(s.engine.CurrentEpochN(), packIdx)
 
 	s.store.AddToPack(epoch, packIdx, e.Hash())
 
@@ -38,10 +38,10 @@ func (s *Service) packs_onNewEvent(e *inter.Event, epoch idx.SuperFrame) {
 	s.store.SetPackInfo(epoch, packIdx, packInfo)
 }
 
-func (s *Service) packs_onNewEpoch(oldEpoch, newEpoch idx.SuperFrame) {
+func (s *Service) packs_onNewEpoch(oldEpoch, newEpoch idx.Epoch) {
 	// pin the last pack
 	packIdx := s.store.GetPacksNumOrDefault(oldEpoch)
-	packInfo := s.store.GetPackInfoOrDefault(s.engine.CurrentSuperFrameN(), packIdx)
+	packInfo := s.store.GetPackInfoOrDefault(s.engine.CurrentEpochN(), packIdx)
 
 	packInfo.Heads = s.store.GetHeads(oldEpoch)
 	s.store.SetPackInfo(oldEpoch, packIdx, packInfo)
```

### src/gossip/packs_downloader/packs_downloader.go
```diff
@@ -38,15 +38,15 @@ func New(fetcher *fetcher.Fetcher, onlyNotConnected onlyNotConnectedFn, dropPeer
 
 type Peer struct {
 	Id    string
-	Epoch idx.SuperFrame
+	Epoch idx.Epoch
 
 	RequestPackInfos packInfoRequesterFn
 	RequestPack      packRequesterFn
 }
 
 // RegisterPeer injects a new download peer into the set of block source to be
 // used for fetching hashes and blocks from.
-func (d *PacksDownloader) RegisterPeer(peer Peer, myEpoch idx.SuperFrame) error {
+func (d *PacksDownloader) RegisterPeer(peer Peer, myEpoch idx.Epoch) error {
 	if peer.Epoch < myEpoch {
 		// this peer is useless for syncing
 		return d.UnregisterPeer(peer.Id)
@@ -66,7 +66,7 @@ func (d *PacksDownloader) RegisterPeer(peer Peer, myEpoch idx.SuperFrame) error
 	return nil
 }
 
-func (d *PacksDownloader) OnNewEpoch(myEpoch idx.SuperFrame, peerEpoch func(string) idx.SuperFrame) {
+func (d *PacksDownloader) OnNewEpoch(myEpoch idx.Epoch, peerEpoch func(string) idx.Epoch) {
 	d.peersMu.Lock()
 	defer d.peersMu.Unlock()
 
```

### src/gossip/packs_downloader/peer_downloader.go
```diff
@@ -42,28 +42,28 @@ type onlyNotConnectedFn func(ids hash.Events) hash.Events
 type dropPeerFn func(peer string)
 
 // request pack info from the peer
-type packInfoRequesterFn func(epoch idx.SuperFrame, indexes []idx.Pack) error
+type packInfoRequesterFn func(epoch idx.Epoch, indexes []idx.Pack) error
 
 // request full pack from the peer
-type packRequesterFn func(epoch idx.SuperFrame, index idx.Pack) error
+type packRequesterFn func(epoch idx.Epoch, index idx.Pack) error
 
 type packsNumData struct {
-	epoch    idx.SuperFrame // in the specified epoch
-	packsNum idx.Pack       // there's this number of packs
+	epoch    idx.Epoch // in the specified epoch
+	packsNum idx.Pack  // there's this number of packs
 }
 
 type packInfoData struct {
-	epoch idx.SuperFrame // the epoch where pack is located
-	index idx.Pack       // the seq number of the pack
-	heads hash.Events    // Hashes of the pack heads
-	time  time.Time      // Timestamp of the announcement
+	epoch idx.Epoch   // the epoch where pack is located
+	index idx.Pack    // the seq number of the pack
+	heads hash.Events // Hashes of the pack heads
+	time  time.Time   // Timestamp of the announcement
 }
 
 type packData struct {
-	epoch idx.SuperFrame // the epoch where pack is located
-	index idx.Pack       // the seq number of the pack
-	ids   hash.Events    // Event hashes which form the pack
-	time  time.Time      // Timestamp of the announcement
+	epoch idx.Epoch   // the epoch where pack is located
+	index idx.Pack    // the seq number of the pack
+	ids   hash.Events // Event hashes which form the pack
+	time  time.Time   // Timestamp of the announcement
 
 	fetchEvents fetcher.EventsRequesterFn
 }
@@ -84,8 +84,8 @@ type PeerPacksDownloader struct {
 	onlyNotConnected onlyNotConnectedFn
 
 	// Announce states
-	myEpoch idx.SuperFrame // the epoch where where we're syncing
-	peer    Peer           // the peer we're syncing with
+	myEpoch idx.Epoch // the epoch where where we're syncing
+	peer    Peer      // the peer we're syncing with
 
 	packsNum     idx.Pack               // total num of packs the peer has (not all of them are requested!)
 	packInfos    *tree.Map              // the short descriptors of received peer's packs
@@ -95,7 +95,7 @@ type PeerPacksDownloader struct {
 }
 
 // New creates a packs fetcher to retrieve events based on pack announcements. Works only with 1 peer.
-func newPeer(peer Peer, myEpoch idx.SuperFrame, fetcher *fetcher.Fetcher, onlyNotConnected onlyNotConnectedFn, dropPeer dropPeerFn) *PeerPacksDownloader {
+func newPeer(peer Peer, myEpoch idx.Epoch, fetcher *fetcher.Fetcher, onlyNotConnected onlyNotConnectedFn, dropPeer dropPeerFn) *PeerPacksDownloader {
 	return &PeerPacksDownloader{
 		notifyInfo:       make(chan *packInfoData, maxQueuedInfos),
 		notifyPacksNum:   make(chan *packsNumData, maxQueuedInfos),
@@ -126,7 +126,7 @@ func (d *PeerPacksDownloader) Stop() {
 
 // Notify announces the fetcher of the potential availability of a new event in
 // the network.
-func (d *PeerPacksDownloader) NotifyPackInfo(epoch idx.SuperFrame, index idx.Pack, heads hash.Events, time time.Time) error {
+func (d *PeerPacksDownloader) NotifyPackInfo(epoch idx.Epoch, index idx.Pack, heads hash.Events, time time.Time) error {
 	if d.myEpoch != epoch {
 		return nil // Short circuit if from another epoch
 	}
@@ -145,7 +145,7 @@ func (d *PeerPacksDownloader) NotifyPackInfo(epoch idx.SuperFrame, index idx.Pac
 	}
 }
 
-func (d *PeerPacksDownloader) NotifyPacksNum(epoch idx.SuperFrame, packsNum idx.Pack) error {
+func (d *PeerPacksDownloader) NotifyPacksNum(epoch idx.Epoch, packsNum idx.Pack) error {
 	if d.myEpoch != epoch {
 		return nil // Short circuit if from another epoch
 	}
@@ -163,7 +163,7 @@ func (d *PeerPacksDownloader) NotifyPacksNum(epoch idx.SuperFrame, packsNum idx.
 }
 
 // Enqueue tries to fill gaps the fetcher's future import queue.
-func (d *PeerPacksDownloader) NotifyPack(epoch idx.SuperFrame, index idx.Pack, ids hash.Events, time time.Time, fetchEvents fetcher.EventsRequesterFn) error {
+func (d *PeerPacksDownloader) NotifyPack(epoch idx.Epoch, index idx.Pack, ids hash.Events, time time.Time, fetchEvents fetcher.EventsRequesterFn) error {
 	if d.myEpoch != epoch {
 		return nil // Short circuit if from another epoch
 	}
```

### src/gossip/peer.go
```diff
@@ -47,9 +47,9 @@ const (
 // PeerInfo represents a short summary of the sub-protocol metadata known
 // about a connected peer.
 type PeerInfo struct {
-	Version     int            `json:"version"` // protocol version negotiated
-	Epoch       idx.SuperFrame `json:"epoch"`
-	NumOfBlocks idx.Block      `json:"blocks"`
+	Version     int       `json:"version"` // protocol version negotiated
+	Epoch       idx.Epoch `json:"epoch"`
+	NumOfBlocks idx.Block `json:"blocks"`
 }
 
 type peer struct {
@@ -61,8 +61,6 @@ type peer struct {
 	version  int         // Protocol version negotiated
 	syncDrop *time.Timer // Timed connection dropper if sync progress isn't validated in time
 
-	lock sync.RWMutex
-
 	knownTxs    mapset.Set                // Set of transaction hashes known to be known by this peer
 	knownEvents mapset.Set                // Set of event hashes known to be known by this peer
 	queuedTxs   chan []*types.Transaction // Queue of transactions to broadcast to the peer
@@ -71,13 +69,27 @@ type peer struct {
 	term        chan struct{}             // Termination channel to stop the broadcaster
 
 	progress PeerProgress
+
+	sync.RWMutex
 }
 
-func (p *PeerProgress) InterestedIn(eventEpoch idx.SuperFrame) bool {
-	if p.Epoch == 0 || eventEpoch == 0 {
-		return false
-	}
-	return eventEpoch == p.Epoch || eventEpoch == p.Epoch+1
+func (p *peer) SetProgress(x PeerProgress) {
+	p.Lock()
+	defer p.Unlock()
+
+	p.progress = x
+}
+
+func (p *peer) InterestedIn(h hash.Event) bool {
+	e := h.Epoch()
+
+	p.RLock()
+	defer p.RUnlock()
+
+	return e != 0 &&
+		p.progress.Epoch != 0 &&
+		(e == p.progress.Epoch || e == p.progress.Epoch+1) &&
+		!p.knownEvents.Contains(h)
 }
 
 func (a *PeerProgress) Less(b PeerProgress) bool {
@@ -320,14 +332,14 @@ func (p *peer) RequestEvents(ids hash.Events) error {
 	return nil
 }
 
-func (p *peer) RequestPackInfos(epoch idx.SuperFrame, indexes []idx.Pack) error {
+func (p *peer) RequestPackInfos(epoch idx.Epoch, indexes []idx.Pack) error {
 	return p2p.Send(p.rw, GetPackInfosMsg, getPackInfosData{
 		Epoch:   epoch,
 		Indexes: indexes,
 	})
 }
 
-func (p *peer) RequestPack(epoch idx.SuperFrame, index idx.Pack) error {
+func (p *peer) RequestPack(epoch idx.Epoch, index idx.Pack) error {
 	return p2p.Send(p.rw, GetPackMsg, getPackData{
 		Epoch: epoch,
 		Index: index,
@@ -480,13 +492,13 @@ func (ps *peerSet) Len() int {
 
 // PeersWithoutEvent retrieves a list of peers that do not have a given event in
 // their set of known hashes.
-func (ps *peerSet) PeersWithoutEvent(hash hash.Event) []*peer {
+func (ps *peerSet) PeersWithoutEvent(e hash.Event) []*peer {
 	ps.lock.RLock()
 	defer ps.lock.RUnlock()
 
 	list := make([]*peer, 0, len(ps.peers))
 	for _, p := range ps.peers {
-		if p.progress.InterestedIn(hash.Epoch()) && !p.knownEvents.Contains(hash) {
+		if p.InterestedIn(e) {
 			list = append(list, p)
 		}
 	}
```

### src/gossip/poset_hook.go
```diff
@@ -42,11 +42,11 @@ func (hook *HookedEngine) Prepare(e *inter.Event) *inter.Event {
 	return hook.engine.Prepare(e)
 }
 
-func (hook *HookedEngine) CurrentSuperFrameN() idx.SuperFrame {
+func (hook *HookedEngine) CurrentEpochN() idx.Epoch {
 	if hook.engine == nil {
 		return 1
 	}
-	return hook.engine.CurrentSuperFrameN()
+	return hook.engine.CurrentEpochN()
 }
 
 func (hook *HookedEngine) LastBlock() (idx.Block, hash.Event) {
```

### src/gossip/protocol.go
```diff
@@ -107,36 +107,36 @@ type ethStatusData struct {
 }
 
 type PeerProgress struct {
-	Epoch        idx.SuperFrame
+	Epoch        idx.Epoch
 	NumOfBlocks  idx.Block
 	LastPackInfo PackInfo
 	LastBlock    hash.Event
 }
 
 type packInfosData struct {
-	Epoch           idx.SuperFrame
+	Epoch           idx.Epoch
 	TotalNumOfPacks idx.Pack // in specified epoch
 	Infos           []PackInfo
 }
 
 type packInfosDataRLP struct {
-	Epoch           idx.SuperFrame
+	Epoch           idx.Epoch
 	TotalNumOfPacks idx.Pack // in specified epoch
 	RawInfos        []rlp.RawValue
 }
 
 type getPackInfosData struct {
-	Epoch   idx.SuperFrame
+	Epoch   idx.Epoch
 	Indexes []idx.Pack
 }
 
 type getPackData struct {
-	Epoch idx.SuperFrame
+	Epoch idx.Epoch
 	Index idx.Pack
 }
 
 type packData struct {
-	Epoch idx.SuperFrame
+	Epoch idx.Epoch
 	Index idx.Pack
 	Ids   hash.Events
 }
```

### src/gossip/service.go
```diff
@@ -29,7 +29,7 @@ type ServiceFeed struct {
 	scope           event.SubscriptionScope
 }
 
-func (f *ServiceFeed) SubscribeNewEpoch(ch chan<- idx.SuperFrame) event.Subscription {
+func (f *ServiceFeed) SubscribeNewEpoch(ch chan<- idx.Epoch) event.Subscription {
 	return f.scope.Track(f.newEpoch.Subscribe(ch))
 }
 
@@ -146,7 +146,7 @@ func (s *Service) processEvent(realEngine Consensus, e *inter.Event) error {
 
 	s.packs_onNewEvent(e, e.Epoch)
 
-	newEpoch := realEngine.CurrentSuperFrameN()
+	newEpoch := realEngine.CurrentEpochN()
 	if newEpoch != oldEpoch {
 		s.packs_onNewEpoch(oldEpoch, newEpoch)
 		s.store.delEpochStore(oldEpoch)
```
