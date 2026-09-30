# [?] Fix open connection race condition

## Summary
Severity: Unknown
Chain: Sei
Component: sei-protocol/sei-chain
Published: 2022-08-25
Source: https://github.com/sei-protocol/sei-chain/commit/de9c9c616598ab09b49fa9eee81fe2fe6f29171f
Type: security-commit

## Details
Fix open connection race condition

## Patch
### sei-tendermint/internal/blocksync/reactor.go
```diff
@@ -11,7 +11,6 @@ import (
 	"github.com/tendermint/tendermint/internal/consensus"
 	"github.com/tendermint/tendermint/internal/eventbus"
 	"github.com/tendermint/tendermint/internal/p2p"
-	"github.com/tendermint/tendermint/internal/p2p/conn"
 	sm "github.com/tendermint/tendermint/internal/state"
 	"github.com/tendermint/tendermint/internal/store"
 	"github.com/tendermint/tendermint/libs/log"
@@ -81,8 +80,8 @@ type Reactor struct {
 	consReactor consensusReactor
 	blockSync   *atomicBool
 
-	chCreator  p2p.ChannelCreator
 	peerEvents p2p.PeerEventSubscriber
+	channel    *p2p.Channel
 
 	requestsCh <-chan BlockRequest
 	errorsCh   <-chan peerError
@@ -100,7 +99,6 @@ func NewReactor(
 	blockExec *sm.BlockExecutor,
 	store *store.BlockStore,
 	consReactor consensusReactor,
-	channelCreator p2p.ChannelCreator,
 	peerEvents p2p.PeerEventSubscriber,
 	blockSync bool,
 	metrics *consensus.Metrics,
@@ -113,7 +111,6 @@ func NewReactor(
 		store:       store,
 		consReactor: consReactor,
 		blockSync:   newAtomicBool(blockSync),
-		chCreator:   channelCreator,
 		peerEvents:  peerEvents,
 		metrics:     metrics,
 		eventBus:    eventBus,
@@ -123,6 +120,10 @@ func NewReactor(
 	return r
 }
 
+func (r *Reactor) SetChannel(ch *p2p.Channel) {
+	r.channel = ch
+}
+
 // OnStart starts separate go routines for each p2p Channel and listens for
 // envelopes on each. In addition, it also listens for peer updates and handles
 // messages on that p2p channel accordingly. The caller must be sure to execute
@@ -131,12 +132,6 @@ func NewReactor(
 // If blockSync is enabled, we also start the pool and the pool processing
 // goroutine. If the pool fails to start, an error is returned.
 func (r *Reactor) OnStart(ctx context.Context) error {
-	blockSyncCh, err := r.chCreator(ctx, GetChannelDescriptor())
-	if err != nil {
-		return err
-	}
-	r.chCreator = func(context.Context, *conn.ChannelDescriptor) (*p2p.Channel, error) { return blockSyncCh, nil }
-
 	state, err := r.stateStore.Load()
 	if err != nil {
 		return err
@@ -162,13 +157,13 @@ func (r *Reactor) OnStart(ctx context.Context) error {
 		if err := r.pool.Start(ctx); err != nil {
 			return err
 		}
-		go r.requestRoutine(ctx, blockSyncCh)
+		go r.requestRoutine(ctx, r.channel)
 
-		go r.poolRoutine(ctx, false, blockSyncCh)
+		go r.poolRoutine(ctx, false, r.channel)
 	}
 
-	go r.processBlockSyncCh(ctx, blockSyncCh)
-	go r.processPeerUpdates(ctx, r.peerEvents(ctx), blockSyncCh)
+	go r.processBlockSyncCh(ctx, r.channel)
+	go r.processPeerUpdates(ctx, r.peerEvents(ctx), r.channel)
 
 	return nil
 }
@@ -378,13 +373,8 @@ func (r *Reactor) SwitchToBlockSync(ctx context.Context, state sm.State) error {
 
 	r.syncStartTime = time.Now()
 
-	bsCh, err := r.chCreator(ctx, GetChannelDescriptor())
-	if err != nil {
-		return err
-	}
-
-	go r.requestRoutine(ctx, bsCh)
-	go r.poolRoutine(ctx, true, bsCh)
+	go r.requestRoutine(ctx, r.channel)
+	go r.poolRoutine(ctx, true, r.channel)
 
 	if err := r.PublishStatus(types.EventDataBlockSyncStatus{
 		Complete: false,
```

### sei-tendermint/internal/blocksync/reactor_test.go
```diff
@@ -149,7 +149,6 @@ func makeReactor(
 		blockExec,
 		blockStore,
 		nil,
-		channelCreator,
 		peerEvents,
 		true,
 		consensus.NopMetrics(),
```

### sei-tendermint/internal/consensus/reactor.go
```diff
@@ -27,49 +27,54 @@ var (
 	_ p2p.Wrapper     = (*tmcons.Message)(nil)
 )
 
-// GetChannelDescriptor produces an instance of a descriptor for this
-// package's required channels.
-func getChannelDescriptors() map[p2p.ChannelID]*p2p.ChannelDescriptor {
-	return map[p2p.ChannelID]*p2p.ChannelDescriptor{
-		StateChannel: {
-			ID:                  StateChannel,
-			MessageType:         new(tmcons.Message),
-			Priority:            8,
-			SendQueueCapacity:   64,
-			RecvMessageCapacity: maxMsgSize,
-			RecvBufferCapacity:  128,
-			Name:                "state",
-		},
-		DataChannel: {
-			// TODO: Consider a split between gossiping current block and catchup
-			// stuff. Once we gossip the whole block there is nothing left to send
-			// until next height or round.
-			ID:                  DataChannel,
-			MessageType:         new(tmcons.Message),
-			Priority:            12,
-			SendQueueCapacity:   64,
-			RecvBufferCapacity:  512,
-			RecvMessageCapacity: maxMsgSize,
-			Name:                "data",
-		},
-		VoteChannel: {
-			ID:                  VoteChannel,
-			MessageType:         new(tmcons.Message),
-			Priority:            10,
-			SendQueueCapacity:   64,
-			RecvBufferCapacity:  128,
-			RecvMessageCapacity: maxMsgSize,
-			Name:                "vote",
-		},
-		VoteSetBitsChannel: {
-			ID:                  VoteSetBitsChannel,
-			MessageType:         new(tmcons.Message),
-			Priority:            5,
-			SendQueueCapacity:   8,
-			RecvBufferCapacity:  128,
-			RecvMessageCapacity: maxMsgSize,
-			Name:                "voteSet",
-		},
+func GetStateChannelDescriptor() *p2p.ChannelDescriptor {
+	return &p2p.ChannelDescriptor{
+		ID:                  StateChannel,
+		MessageType:         new(tmcons.Message),
+		Priority:            8,
+		SendQueueCapacity:   64,
+		RecvMessageCapacity: maxMsgSize,
+		RecvBufferCapacity:  128,
+		Name:                "state",
+	}
+}
+
+func GetDataChannelDescriptor() *p2p.ChannelDescriptor {
+	return &p2p.ChannelDescriptor{
+		// TODO: Consider a split between gossiping current block and catchup
+		// stuff. Once we gossip the whole block there is nothing left to send
+		// until next height or round.
+		ID:                  DataChannel,
+		MessageType:         new(tmcons.Message),
+		Priority:            12,
+		SendQueueCapacity:   64,
+		RecvBufferCapacity:  512,
+		RecvMessageCapacity: maxMsgSize,
+		Name:                "data",
+	}
+}
+
+func GetVoteChannelDescriptor() *p2p.ChannelDescriptor {
+	return &p2p.ChannelDescriptor{
+		ID:                  VoteChannel,
+		MessageType:         new(tmcons.Message),
+		Priority:            10,
+		SendQueueCapacity:   64,
+		RecvBufferCapacity:  128,
+		RecvMessageCapacity: maxMsgSize,
+		Name:                "vote",
+	}
+}
+
+func GetVoteSetChannelDescriptor() *p2p.ChannelDescriptor {
+	return &p2p.ChannelDescriptor{
+		ID:                  VoteSetBitsChannel,
+		MessageType:         new(tmcons.Message),
+		Priority:            5,
+		SendQueueCapacity:   8,
+		RecvBufferCapacity:  128,
+		RecvMessageCapacity: maxMsgSize,
+		Name:                "voteSet",
 	}
 }
 
@@ -103,8 +108,9 @@ type BlockSyncReactor interface {
 	GetRemainingSyncTime() time.Duration
 }
 
-//go:generate ../../scripts/mockery_generate.sh ConsSyncReactor
 // ConsSyncReactor defines an interface used for testing abilities of node.startStateSync.
+//
+//go:generate ../../scripts/mockery_generate.sh ConsSyncReactor
 type ConsSyncReactor interface {
 	SwitchToConsensus(sm.State, bool)
 	SetStateSyncingMetrics(float64)
@@ -127,7 +133,8 @@ type Reactor struct {
 	readySignal chan struct{} // closed when the node is ready to start consensus
 
 	peerEvents p2p.PeerEventSubscriber
-	chCreator  p2p.ChannelCreator
+
+	channels *channelBundle
 }
 
 // NewReactor returns a reference to a new consensus reactor, which implements
@@ -137,7 +144,6 @@ type Reactor struct {
 func NewReactor(
 	logger log.Logger,
 	cs *State,
-	channelCreator p2p.ChannelCreator,
 	peerEvents p2p.PeerEventSubscriber,
 	eventBus *eventbus.EventBus,
 	waitSync bool,
@@ -152,8 +158,8 @@ func NewReactor(
 		eventBus:    eventBus,
 		Metrics:     metrics,
 		peerEvents:  peerEvents,
-		chCreator:   channelCreator,
 		readySignal: make(chan struct{}),
+		channels:    &channelBundle{},
 	}
 	r.BaseService = *service.NewBaseService(logger, "Consensus", r)
 
@@ -171,6 +177,22 @@ type channelBundle struct {
 	votSet *p2p.Channel
 }
 
+func (r *Reactor) SetStateChannel(ch *p2p.Channel) {
+	r.channels.state = ch
+}
+
+func (r *Reactor) SetDataChannel(ch *p2p.Channel) {
+	r.channels.data = ch
+}
+
+func (r *Reactor) SetVoteChannel(ch *p2p.Channel) {
+	r.channels.vote = ch
+}
+
+func (r *Reactor) SetVoteSetChannel(ch *p2p.Channel) {
+	r.channels.votSet = ch
+}
+
 // OnStart starts separate go routines for each p2p Channel and listens for
 // envelopes on each. In addition, it also listens for peer updates and handles
 // messages on that p2p channel accordingly. The caller must be sure to execute
@@ -180,37 +202,13 @@ func (r *Reactor) OnStart(ctx context.Context) error {
 
 	peerUpdates := r.peerEvents(ctx)
 
-	var chBundle channelBundle
-	var err error
-
-	chans := getChannelDescriptors()
-	chBundle.state, err = r.chCreator(ctx, chans[StateChannel])
-	if err != nil {
-		return err
-	}
-
-	chBundle.data, err = r.chCreator(ctx, chans[DataChannel])
-	if err != nil {
-		return err
-	}
-
-	chBundle.vote, err = r.chCreator(ctx, chans[VoteChannel])
-	if err != nil {
-		return err
-	}
-
-	chBundle.votSet, err = r.chCreator(ctx, chans[VoteSetBitsChannel])
-	if err != nil {
-		return err
-	}
-
 	// start routine that computes peer statistics for evaluating peer quality
 	//
 	// TODO: Evaluate if we need this to be synchronized via WaitGroup as to not
 	// leak the goroutine when stopping the reactor.
 	go r.peerStatsRoutine(ctx, peerUpdates)
 
-	r.subscribeToBroadcastEvents(ctx, chBundle.state)
+	r.subscribeToBroadcastEvents(ctx, r.channels.state)
 
 	if !r.WaitSync() {
 		if err := r.state.Start(ctx); err != nil {
@@ -222,11 +220,11 @@ func (r *Reactor) OnStart(ctx context.Context) error {
 
 	go r.updateRoundStateRoutine(ctx)
 
-	go r.processStateCh(ctx, chBundle)
-	go r.processDataCh(ctx, chBundle)
-	go r.processVoteCh(ctx, chBundle)
-	go r.processVoteSetBitsCh(ctx, chBundle)
-	go r.processPeerUpdates(ctx, peerUpdates, chBundle)
+	go r.processStateCh(ctx, *r.channels)
+	go r.processDataCh(ctx, *r.channels)
+	go r.processVoteCh(ctx, *r.channels)
+	go r.processVoteSetBitsCh(ctx, *r.channels)
+	go r.processPeerUpdates(ctx, peerUpdates, *r.channels)
 
 	return nil
 }
```

### sei-tendermint/internal/consensus/reactor_test.go
```diff
@@ -85,31 +85,13 @@ func setup(
 	ctx, cancel := context.WithCancel(ctx)
 	t.Cleanup(cancel)
 
-	chCreator := func(nodeID types.NodeID) p2p.ChannelCreator {
-		return func(ctx context.Context, desc *p2p.ChannelDescriptor) (*p2p.Channel, error) {
-			switch desc.ID {
-			case StateChannel:
-				return rts.stateChannels[nodeID], nil
-			case DataChannel:
-				return rts.dataChannels[nodeID], nil
-			case VoteChannel:
-				return rts.voteChannels[nodeID], nil
-			case VoteSetBitsChannel:
-				return rts.voteSetBitsChannels[nodeID], nil
-			default:
-				return nil, fmt.Errorf("invalid channel; %v", desc.ID)
-			}
-		}
-	}
-
 	i := 0
 	for nodeID, node := range rts.network.Nodes {
 		state := states[i]
 
 		reactor := NewReactor(
 			state.logger.With("node", nodeID),
 			state,
-			chCreator(nodeID),
 			func(ctx context.Context) *p2p.PeerUpdates { return node.MakePeerUpdates(ctx, t) },
 			state.eventBus,
 			true,
@@ -696,7 +678,6 @@ func TestSwitchToConsensusVoteExtensions(t *testing.T) {
 				log.NewNopLogger(),
 				cs,
 				nil,
-				nil,
 				cs.eventBus,
 				true,
 				NopMetrics(),
```

### sei-tendermint/internal/evidence/reactor.go
```diff
@@ -48,27 +48,25 @@ type Reactor struct {
 	logger log.Logger
 
 	evpool     *Pool
-	chCreator  p2p.ChannelCreator
 	peerEvents p2p.PeerEventSubscriber
 
 	mtx sync.Mutex
 
 	peerRoutines map[types.NodeID]context.CancelFunc
+	channel      *p2p.Channel
 }
 
 // NewReactor returns a reference to a new evidence reactor, which implements the
 // service.Service interface. It accepts a p2p Channel dedicated for handling
 // envelopes with EvidenceList messages.
 func NewReactor(
 	logger log.Logger,
-	chCreator p2p.ChannelCreator,
 	peerEvents p2p.PeerEventSubscriber,
 	evpool *Pool,
 ) *Reactor {
 	r := &Reactor{
 		logger:       logger,
 		evpool:       evpool,
-		chCreator:    chCreator,
 		peerEvents:   peerEvents,
 		peerRoutines: make(map[types.NodeID]context.CancelFunc),
 	}
@@ -78,18 +76,17 @@ func NewReactor(
 	return r
 }
 
+func (r *Reactor) SetChannel(ch *p2p.Channel) {
+	r.channel = ch
+}
+
 // OnStart starts separate go routines for each p2p Channel and listens for
 // envelopes on each. In addition, it also listens for peer updates and handles
 // messages on that p2p channel accordingly. The caller must be sure to execute
 // OnStop to ensure the outbound p2p Channels are closed. No error is returned.
 func (r *Reactor) OnStart(ctx context.Context) error {
-	ch, err := r.chCreator(ctx, GetChannelDescriptor())
-	if err != nil {
-		return err
-	}
-
-	go r.processEvidenceCh(ctx, ch)
-	go r.processPeerUpdates(ctx, r.peerEvents(ctx), ch)
+	go r.processEvidenceCh(ctx, r.channel)
+	go r.processPeerUpdates(ctx, r.peerEvents(ctx), r.channel)
 
 	return nil
 }
```

### sei-tendermint/internal/evidence/reactor_test.go
```diff
@@ -96,13 +96,8 @@ func setup(ctx context.Context, t *testing.T, stateStores []sm.Store) *reactorTe
 		rts.network.Nodes[nodeID].PeerManager.Register(ctx, pu)
 		rts.nodes = append(rts.nodes, rts.network.Nodes[nodeID])
 
-		chCreator := func(ctx context.Context, chdesc *p2p.ChannelDescriptor) (*p2p.Channel, error) {
-			return rts.evidenceChannels[nodeID], nil
-		}
-
 		rts.reactors[nodeID] = evidence.NewReactor(
 			logger,
-			chCreator,
 			func(ctx context.Context) *p2p.PeerUpdates { return pu },
 			rts.pools[nodeID])
 
```

### sei-tendermint/internal/mempool/reactor.go
```diff
@@ -33,30 +33,29 @@ type Reactor struct {
 	ids     *IDs
 
 	peerEvents p2p.PeerEventSubscriber
-	chCreator  p2p.ChannelCreator
 
 	// observePanic is a function for observing panics that were recovered in methods on
 	// Reactor. observePanic is called with the recovered value.
 	observePanic func(interface{})
 
 	mtx          sync.Mutex
 	peerRoutines map[types.NodeID]context.CancelFunc
+
+	channel *p2p.Channel
 }
 
 // NewReactor returns a reference to a new reactor.
 func NewReactor(
 	logger log.Logger,
 	cfg *config.MempoolConfig,
 	txmp *TxMempool,
-	chCreator p2p.ChannelCreator,
 	peerEvents p2p.PeerEventSubscriber,
 ) *Reactor {
 	r := &Reactor{
 		logger:       logger,
 		cfg:          cfg,
 		mempool:      txmp,
 		ids:          NewMempoolIDs(),
-		chCreator:    chCreator,
 		peerEvents:   peerEvents,
 		peerRoutines: make(map[types.NodeID]context.CancelFunc),
 		observePanic: defaultObservePanic,
@@ -66,11 +65,15 @@ func NewReactor(
 	return r
 }
 
+func (r *Reactor) SetChannel(ch *p2p.Channel) {
+	r.channel = ch
+}
+
 func defaultObservePanic(r interface{}) {}
 
 // getChannelDescriptor produces an instance of a descriptor for this
 // package's required channels.
-func getChannelDescriptor(cfg *config.MempoolConfig) *p2p.ChannelDescriptor {
+func GetChannelDescriptor(cfg *config.MempoolConfig) *p2p.ChannelDescriptor {
 	largestTx := make([]byte, cfg.MaxTxBytes)
 	batchMsg := protomem.Message{
 		Sum: &protomem.Message_Txs{
@@ -97,13 +100,8 @@ func (r *Reactor) OnStart(ctx context.Context) error {
 		r.logger.Info("tx broadcasting is disabled")
 	}
 
-	ch, err := r.chCreator(ctx, getChannelDescriptor(r.cfg))
-	if err != nil {
-		return err
-	}
-
-	go r.processMempoolCh(ctx, ch)
-	go r.processPeerUpdates(ctx, r.peerEvents(ctx), ch)
+	go r.processMempoolCh(ctx, r.channel)
+	go r.processPeerUpdates(ctx, r.peerEvents(ctx), r.channel)
 
 	return nil
 }
```

### sei-tendermint/internal/mempool/reactor_test.go
```diff
@@ -58,7 +58,7 @@ func setupReactors(ctx context.Context, t *testing.T, logger log.Logger, numNode
 		peerUpdates:     make(map[types.NodeID]*p2p.PeerUpdates, numNodes),
 	}
 
-	chDesc := getChannelDescriptor(cfg.Mempool)
+	chDesc := GetChannelDescriptor(cfg.Mempool)
 	rts.mempoolChannels = rts.network.MakeChannelsNoCleanup(ctx, t, chDesc)
 
 	for nodeID := range rts.network.Nodes {
@@ -75,15 +75,10 @@ func setupReactors(ctx context.Context, t *testing.T, logger log.Logger, numNode
 		rts.peerUpdates[nodeID] = p2p.NewPeerUpdates(rts.peerChans[nodeID], 1)
 		rts.network.Nodes[nodeID].PeerManager.Register(ctx, rts.peerUpdates[nodeID])
 
-		chCreator := func(ctx context.Context, chDesc *p2p.ChannelDescriptor) (*p2p.Channel, error) {
-			return rts.mempoolChannels[nodeID], nil
-		}
-
 		rts.reactors[nodeID] = NewReactor(
 			rts.logger.With("nodeID", nodeID),
 			cfg.Mempool,
 			mempool,
-			chCreator,
 			func(ctx context.Context) *p2p.PeerUpdates { return rts.peerUpdates[nodeID] },
 		)
 		rts.nodes = append(rts.nodes, nodeID)
```

### sei-tendermint/internal/p2p/pex/reactor.go
```diff
@@ -80,7 +80,6 @@ type Reactor struct {
 	logger log.Logger
 
 	peerManager *p2p.PeerManager
-	chCreator   p2p.ChannelCreator
 	peerEvents  p2p.PeerEventSubscriber
 	// list of available peers to loop through and send peer requests to
 	availablePeers map[types.NodeID]struct{}
@@ -100,19 +99,19 @@ type Reactor struct {
 
 	// the total number of unique peers added
 	totalPeers int
+
+	channel *p2p.Channel
 }
 
 // NewReactor returns a reference to a new reactor.
 func NewReactor(
 	logger log.Logger,
 	peerManager *p2p.PeerManager,
-	channelCreator p2p.ChannelCreator,
 	peerEvents p2p.PeerEventSubscriber,
 ) *Reactor {
 	r := &Reactor{
 		logger:               logger,
 		peerManager:          peerManager,
-		chCreator:            channelCreator,
 		peerEvents:           peerEvents,
 		availablePeers:       make(map[types.NodeID]struct{}),
 		requestsSent:         make(map[types.NodeID]struct{}),
@@ -123,18 +122,17 @@ func NewReactor(
 	return r
 }
 
+func (r *Reactor) SetChannel(ch *p2p.Channel) {
+	r.channel = ch
+}
+
 // OnStart starts separate go routines for each p2p Channel and listens for
 // envelopes on each. In addition, it also listens for peer updates and handles
 // messages on that p2p channel accordingly. The caller must be sure to execute
 // OnStop to ensure the outbound p2p Channels are closed.
 func (r *Reactor) OnStart(ctx context.Context) error {
-	channel, err := r.chCreator(ctx, ChannelDescriptor())
-	if err != nil {
-		return err
-	}
-
 	peerUpdates := r.peerEvents(ctx)
-	go r.processPexCh(ctx, channel)
+	go r.processPexCh(ctx, r.channel)
 	go r.processPeerUpdates(ctx, peerUpdates)
 	return nil
 }
```

### sei-tendermint/internal/p2p/pex/reactor_test.go
```diff
@@ -299,11 +299,7 @@ func setupSingle(ctx context.Context, t *testing.T) *singleTestReactor {
 	peerManager, err := p2p.NewPeerManager(nodeID, dbm.NewMemDB(), p2p.PeerManagerOptions{})
 	require.NoError(t, err)
 
-	chCreator := func(context.Context, *p2p.ChannelDescriptor) (*p2p.Channel, error) {
-		return pexCh, nil
-	}
-
-	reactor := pex.NewReactor(log.NewNopLogger(), peerManager, chCreator, func(_ context.Context) *p2p.PeerUpdates { return peerUpdates })
+	reactor := pex.NewReactor(log.NewNopLogger(), peerManager, func(_ context.Context) *p2p.PeerUpdates { return peerUpdates })
 
 	require.NoError(t, reactor.Start(ctx))
 	t.Cleanup(reactor.Wait)
@@ -388,18 +384,13 @@ func setupNetwork(ctx context.Context, t *testing.T, opts testOptions) *reactorT
 		rts.peerUpdates[nodeID] = p2p.NewPeerUpdates(rts.peerChans[nodeID], chBuf)
 		rts.network.Nodes[nodeID].PeerManager.Register(ctx, rts.peerUpdates[nodeID])
 
-		chCreator := func(context.Context, *p2p.ChannelDescriptor) (*p2p.Channel, error) {
-			return rts.pexChannels[nodeID], nil
-		}
-
 		// the first nodes in the array are always mock nodes
 		if idx < opts.MockNodes {
 			rts.mocks = append(rts.mocks, nodeID)
 		} else {
 			rts.reactors[nodeID] = pex.NewReactor(
 				rts.logger.With("nodeID", nodeID),
 				rts.network.Nodes[nodeID].PeerManager,
-				chCreator,
 				func(_ context.Context) *p2p.PeerUpdates { return rts.peerUpdates[nodeID] },
 			)
 		}
@@ -448,14 +439,9 @@ func (r *reactorTestSuite) addNodes(ctx context.Context, t *testing.T, nodes int
 		r.peerUpdates[nodeID] = p2p.NewPeerUpdates(r.peerChans[nodeID], r.opts.BufferSize)
 		r.network.Nodes[nodeID].PeerManager.Register(ctx, r.peerUpdates[nodeID])
 
-		chCreator := func(context.Context, *p2p.ChannelDescriptor) (*p2p.Channel, error) {
-			return r.pexChannels[nodeID], nil
-		}
-
 		r.reactors[nodeID] = pex.NewReactor(
 			r.logger.With("nodeID", nodeID),
 			r.network.Nodes[nodeID].PeerManager,
-			chCreator,
 			func(_ context.Context) *p2p.PeerUpdates { return r.peerUpdates[nodeID] },
 		)
 		r.nodes = append(r.nodes, nodeID)
```

### sei-tendermint/internal/p2p/router.go
```diff
@@ -112,33 +112,33 @@ func (o *RouterOptions) Validate() error {
 //
 // On startup, three main goroutines are spawned to maintain peer connections:
 //
-//   dialPeers(): in a loop, calls PeerManager.DialNext() to get the next peer
-//   address to dial and spawns a goroutine that dials the peer, handshakes
-//   with it, and begins to route messages if successful.
+//	dialPeers(): in a loop, calls PeerManager.DialNext() to get the next peer
+//	address to dial and spawns a goroutine that dials the peer, handshakes
+//	with it, and begins to route messages if successful.
 //
-//   acceptPeers(): in a loop, waits for an inbound connection via
-//   Transport.Accept() and spawns a goroutine that handshakes with it and
-//   begins to route messages if successful.
+//	acceptPeers(): in a loop, waits for an inbound connection via
+//	Transport.Accept() and spawns a goroutine that handshakes with it and
+//	begins to route messages if successful.
 //
-//   evictPeers(): in a loop, calls PeerManager.EvictNext() to get the next
-//   peer to evict, and disconnects it by closing its message queue.
+//	evictPeers(): in a loop, calls PeerManager.EvictNext() to get the next
+//	peer to evict, and disconnects it by closing its message queue.
 //
 // When a peer is connected, an outbound peer message queue is registered in
 // peerQueues, and routePeer() is called to spawn off two additional goroutines:
 //
-//   sendPeer(): waits for an outbound message from the peerQueues queue,
-//   marshals it, and passes it to the peer transport which delivers it.
+//	sendPeer(): waits for an outbound message from the peerQueues queue,
+//	marshals it, and passes it to the peer transport which delivers it.
 //
-//   receivePeer(): waits for an inbound message from the peer transport,
-//   unmarshals it, and passes it to the appropriate inbound channel queue
-//   in channelQueues.
+//	receivePeer(): waits for an inbound message from the peer transport,
+//	unmarshals it, and passes it to the appropriate inbound channel queue
+//	in channelQueues.
 //
 // When a reactor opens a channel via OpenChannel, an inbound channel message
 // queue is registered in channelQueues, and a channel goroutine is spawned:
 //
-//   routeChannel(): waits for an outbound message from the channel, looks
-//   up the recipient peer's outbound message queue in peerQueues, and submits
-//   the message to it.
+//	routeChannel(): waits for an outbound message from the channel, looks
+//	up the recipient peer's outbound message queue in peerQueues, and submits
+//	the message to it.
 //
 // All channel sends in the router are blocking. It is the responsibility of the
 // queue interface in peerQueues and channelQueues to prioritize and drop
@@ -172,6 +172,13 @@ type Router struct {
 	channelMtx      sync.RWMutex
 	channelQueues   map[ChannelID]queue // inbound messages from all peers to a single channel
 	channelMessages map[ChannelID]proto.Message
+
+	chDescsToBeAdded []chDescAdderWithCallback
+}
+
+type chDescAdderWithCallback struct {
+	chDesc *ChannelDescriptor
+	cb     func(*Channel)
 }
 
 // NewRouter creates a new Router. The given Transports must already be
@@ -946,6 +953,13 @@ func (r *Router) setupQueueFactory(ctx context.Context) error {
 	return nil
 }
 
+func (r *Router) AddChDescToBeAdded(chDesc *ChannelDescriptor, callback func(*Channel)) {
+	r.chDescsToBeAdded = append(r.chDescsToBeAdded, chDescAdderWithCallback{
+		chDesc: chDesc,
+		cb:     callback,
+	})
+}
+
 // OnStart implements service.Service.
 func (r *Router) OnStart(ctx context.Context) error {
 	if err := r.setupQueueFactory(ctx); err != nil {
@@ -956,6 +970,14 @@ func (r *Router) OnStart(ctx context.Context) error {
 		return err
 	}
 
+	for _, chDescWithCb := range r.chDescsToBeAdded {
+		if ch, err := r.OpenChannel(ctx, chDescWithCb.chDesc); err != nil {
+			return err
+		} else {
+			chDescWithCb.cb(ch)
+		}
+	}
+
 	go r.dialPeers(ctx)
 	go r.evictPeers(ctx)
 	go r.acceptPeers(ctx, r.transport)
```

### sei-tendermint/internal/statesync/reactor.go
```diff
@@ -72,46 +72,52 @@ const (
 	maxLightBlockRequestRetries = 20
 )
 
-func getChannelDescriptors() map[p2p.ChannelID]*p2p.ChannelDescriptor {
-	return map[p2p.ChannelID]*p2p.ChannelDescriptor{
-		SnapshotChannel: {
-			ID:                  SnapshotChannel,
-			MessageType:         new(ssproto.Message),
-			Priority:            6,
-			SendQueueCapacity:   10,
-			RecvMessageCapacity: snapshotMsgSize,
-			RecvBufferCapacity:  128,
-			Name:                "snapshot",
-		},
-		ChunkChannel: {
-			ID:                  ChunkChannel,
-			Priority:            3,
-			MessageType:         new(ssproto.Message),
-			SendQueueCapacity:   4,
-			RecvMessageCapacity: chunkMsgSize,
-			RecvBufferCapacity:  128,
-			Name:                "chunk",
-		},
-		LightBlockChannel: {
-			ID:                  LightBlockChannel,
-			MessageType:         new(ssproto.Message),
-			Priority:            5,
-			SendQueueCapacity:   10,
-			RecvMessageCapacity: lightBlockMsgSize,
-			RecvBufferCapacity:  128,
-			Name:                "light-block",
-		},
-		ParamsChannel: {
-			ID:                  ParamsChannel,
-			MessageType:         new(ssproto.Message),
-			Priority:            2,
-			SendQueueCapacity:   10,
-			RecvMessageCapacity: paramMsgSize,
-			RecvBufferCapacity:  128,
-			Name:                "params",
-		},
+func GetSnapshotChannelDescriptor() *p2p.ChannelDescriptor {
+	return &p2p.ChannelDescriptor{
+		ID:                  SnapshotChannel,
+		MessageType:         new(ssproto.Message),
+		Priority:            6,
+		SendQueueCapacity:   10,
+		RecvMessageCapacity: snapshotMsgSize,
+		RecvBufferCapacity:  128,
+		Name:                "snapshot",
 	}
+}
 
+func GetChunkChannelDescriptor() *p2p.ChannelDescriptor {
+	return &p2p.ChannelDescriptor{
+		ID:                  ChunkChannel,
+		Priority:            3,
+		MessageType:         new(ssproto.Message),
+		SendQueueCapacity:   4,
+		RecvMessageCapacity: chunkMsgSize,
+		RecvBufferCapacity:  128,
+		Name:                "chunk",
+	}
+}
+
+func GetLightBlockChannelDescriptor() *p2p.ChannelDescriptor {
+	return &p2p.ChannelDescriptor{
+		ID:                  LightBlockChannel,
+		MessageType:         new(ssproto.Message),
+		Priority:            5,
+		SendQueueCapacity:   10,
+		RecvMessageCapacity: lightBlockMsgSize,
+		RecvBufferCapacity:  128,
+		Name:                "light-block",
+	}
+}
+
+func GetParamsChannelDescriptor() *p2p.ChannelDescriptor {
+	return &p2p.ChannelDescriptor{
+		ID:                  ParamsChannel,
+		MessageType:         new(ssproto.Message),
+		Priority:            2,
+		SendQueueCapacity:   10,
+		RecvMessageCapacity: paramMsgSize,
+		RecvBufferCapacity:  128,
+		Name:                "params",
+	}
 }
 
 // Metricer defines an interface used for the rpc sync info query, please see statesync.metrics
@@ -141,7 +147,6 @@ type Reactor struct {
 	conn           abciclient.Client
 	tempDir        string
 	peerEvents     p2p.PeerEventSubscriber
-	chCreator      p2p.ChannelCreator
 	sendBlockError func(context.Context, p2p.PeerError) error
 	postSyncHook   func(context.Context, sm.State) error
 
@@ -170,6 +175,11 @@ type Reactor struct {
 	metrics            *Metrics
 	backfillBlockTotal int64
 	backfilledBlocks   int64
+
+	snapshotChannel   *p2p.Channel
+	chunkChannel      *p2p.Channel
+	lightBlockChannel *p2p.Channel
+	paramsChannel     *p2p.Channel
 }
 
 // NewReactor returns a reference to a new state sync reactor, which implements
@@ -182,7 +192,6 @@ func NewReactor(
 	cfg config.StateSyncConfig,
 	logger log.Logger,
 	conn abciclient.Client,
-	channelCreator p2p.ChannelCreator,
 	peerEvents p2p.PeerEventSubscriber,
 	stateStore sm.Store,
 	blockStore *store.BlockStore,
@@ -198,7 +207,6 @@ func NewReactor(
 		initialHeight:  initialHeight,
 		cfg:            cfg,
 		conn:           conn,
-		chCreator:      channelCreator,
 		peerEvents:     peerEvents,
 		tempDir:        tempDir,
 		stateStore:     stateStore,
@@ -215,32 +223,29 @@ func NewReactor(
 	return r
 }
 
+func (r *Reactor) SetSnapshotChannel(ch *p2p.Channel) {
+	r.snapshotChannel = ch
+}
+
+func (r *Reactor) SetChunkChannel(ch *p2p.Channel) {
+	r.chunkChannel = ch
+}
+
+func (r *Reactor) SetLightBlockChannel(ch *p2p.Channel) {
+	r.lightBlockChannel = ch
+}
+
+func (r *Reactor) SetParamsChannel(ch *p2p.Channel) {
+	r.paramsChannel = ch
+}
+
 // OnStart starts separate go routines for each p2p Channel and listens for
 // envelopes on each. In addition, it also listens for peer updates and handles
 // messages on that p2p channel accordingly. Note, we do not launch a go-routine to
 // handle individual envelopes as to not have to deal with bounding workers or pools.
 // The caller must be sure to execute OnStop to ensure the outbound p2p Channels are
 // closed. No error is returned.
 func (r *Reactor) OnStart(ctx context.Context) error {
-	// construct channels
-	chDesc := getChannelDescriptors()
-	snapshotCh, err := r.chCreator(ctx, chDesc[SnapshotChannel])
-	if err != nil {
-		return err
-	}
-	chunkCh, err := r.chCreator(ctx, chDesc[ChunkChannel])
-	if err != nil {
-		return err
-	}
-	blockCh, err := r.chCreator(ctx, chDesc[LightBlockChannel])
-	if err != nil {
-		return err
-	}
-	paramsCh, err := r.chCreator(ctx, chDesc[ParamsChannel])
-	if err != nil {
-		return err
-	}
-
 	// define constructor and helper functions, that hold
 	// references to these channels for use later. This is not
 	// ideal.
@@ -250,23 +255,23 @@ func (r *Reactor) OnStart(ctx context.Context) error {
 			stateProvider: r.stateProvider,
 			conn:          r.conn,
 			snapshots:     newSnapshotPool(),
-			snapshotCh:    snapshotCh,
-			chunkCh:       chunkCh,
+			snapshotCh:    r.snapshotChannel,
+			chunkCh:       r.chunkChannel,
 			tempDir:       r.tempDir,
 			fetchers:      r.cfg.Fetchers,
 			retryTimeout:  r.cfg.ChunkRequestTimeout,
 			metrics:       r.metrics,
 		}
 	}
-	r.dispatcher = NewDispatcher(blockCh)
+	r.dispatcher = NewDispatcher(r.lightBlockChannel)
 	r.requestSnaphot = func() error {
 		// request snapshots from all currently connected peers
-		return snapshotCh.Send(ctx, p2p.Envelope{
+		return r.snapshotChannel.Send(ctx, p2p.Envelope{
 			Broadcast: true,
 			Message:   &ssproto.SnapshotsRequest{},
 		})
 	}
-	r.sendBlockError = blockCh.SendError
+	r.sendBlockError = r.lightBlockChannel.SendError
 
 	r.initStateProvider = func(ctx context.Context, chainID string, initialHeight int64) error {
 		to := light.TrustOptions{
@@ -289,7 +294,7 @@ func (r *Reactor) OnStart(ctx context.Context) error {
 				providers[idx] = NewBlockProvider(p, chainID, r.dispatcher)
 			}
 
-			stateProvider, err := NewP2PStateProvider(ctx, chainID, initialHeight, providers, to, paramsCh, r.logger.With("module", "stateprovider"))
+			stateProvider, err := NewP2PStateProvider(ctx, chainID, initialHeight, providers, to, r.paramsChannel, r.logger.With("module", "stateprovider"))
 			if err != nil {
 				return fmt.Errorf("failed to initialize P2P state provider: %w", err)
 			}
@@ -306,10 +311,10 @@ func (r *Reactor) OnStart(ctx context.Context) error {
 	}
 
 	go r.processChannels(ctx, map[p2p.ChannelID]*p2p.Channel{
-		SnapshotChannel:   snapshotCh,
-		ChunkChannel:      chunkCh,
-		LightBlockChannel: blockCh,
-		ParamsChannel:     paramsCh,
+		SnapshotChannel:   r.snapshotChannel,
+		ChunkChannel:      r.chunkChannel,
+		LightBlockChannel: r.lightBlockChannel,
+		ParamsChannel:     r.paramsChannel,
 	})
 	go r.processPeerUpdates(ctx, r.peerEvents(ctx))
 
```
