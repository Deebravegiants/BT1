# [?] Merge "[FAB-14192] Fix deadlock in etcdraft chain"

## Summary
Severity: Unknown
Chain: Hyperledger Fabric
Component: hyperledger/fabric
Published: 2019-02-20
Source: https://github.com/hyperledger/fabric/commit/4dd3d73ea4e3cc31c1e9435b38c2825748a6eab2
Type: security-commit

## Details
Merge "[FAB-14192] Fix deadlock in etcdraft chain"

## Patch
### orderer/consensus/etcdraft/chain.go
```diff
@@ -160,7 +160,8 @@ type Chain struct {
 
 	fresh bool // indicate if this is a fresh raft node
 
-	node *node
+	// this is exported so that test can use `Node.Status()` to get raft node status.
+	Node *node
 	opts Options
 
 	Metrics *Metrics
@@ -255,7 +256,7 @@ func NewChain(
 		DisableProposalForwarding: true, // This prevents blocks from being accidentally proposed by followers
 	}
 
-	c.node = &node{
+	c.Node = &node{
 		chainID:      c.channelID,
 		chain:        c,
 		logger:       c.logger,
@@ -294,7 +295,8 @@ func (c *Chain) Start() {
 	if isJoin {
 		isMigration = c.detectMigration()
 	}
-	c.node.start(c.fresh, isJoin, isMigration)
+	c.Node.start(c.fresh, isJoin, isMigration)
+
 	close(c.startC)
 	close(c.errorC)
 
@@ -457,7 +459,7 @@ func (c *Chain) Consensus(req *orderer.ConsensusRequest, sender uint64) error {
 		return fmt.Errorf("failed to unmarshal StepRequest payload to Raft Message: %s", err)
 	}
 
-	if err := c.node.Step(context.TODO(), *stepMsg); err != nil {
+	if err := c.Node.Step(context.TODO(), *stepMsg); err != nil {
 		return fmt.Errorf("failed to process Raft Step message: %s", err)
 	}
 
@@ -536,25 +538,59 @@ func (c *Chain) serveRequest() {
 	submitC := c.submitC
 	var bc *blockCreator
 
-	becomeLeader := func() {
+	var propC chan<- *common.Block
+	var cancelProp context.CancelFunc
+	cancelProp = func() {} // no-op as initial value
+
+	becomeLeader := func() (chan<- *common.Block, context.CancelFunc) {
+		c.Metrics.IsLeader.Set(1)
+
 		c.blockInflight = 0
 		c.justElected = true
 		submitC = nil
+		ch := make(chan *common.Block, c.opts.MaxInflightMsgs)
 
 		// if there is unfinished ConfChange, we should resume the effort to propose it as
 		// new leader, and wait for it to be committed before start serving new requests.
 		if cc := c.getInFlightConfChange(); cc != nil {
-			if err := c.node.ProposeConfChange(context.TODO(), *cc); err != nil {
-				c.logger.Warnf("Failed to propose configuration update to Raft node: %s", err)
-			}
+			// The reason `ProposeConfChange` should be called in go routine is documented in `writeConfigBlock` method.
+			go func() {
+				if err := c.Node.ProposeConfChange(context.TODO(), *cc); err != nil {
+					c.logger.Warnf("Failed to propose configuration update to Raft node: %s", err)
+				}
+			}()
 
 			c.confChangeInProgress = cc
 			c.configInflight = true
 		}
-		c.Metrics.IsLeader.Set(1)
+
+		// Leader should call Propose in go routine, because this method may be blocked
+		// if node is leaderless (this can happen when leader steps down in a heavily
+		// loaded network). We need to make sure applyC can still be consumed properly.
+		ctx, cancel := context.WithCancel(context.Background())
+		go func(ctx context.Context, ch <-chan *common.Block) {
+			for {
+				select {
+				case b := <-ch:
+					data := utils.MarshalOrPanic(b)
+					if err := c.Node.Propose(ctx, data); err != nil {
+						c.logger.Errorf("Failed to propose block %d to raft and discard %d blocks in queue: %s", b.Header.Number, len(ch), err)
+						return
+					}
+					c.logger.Debugf("Proposed block %d to raft consensus", b.Header.Number)
+
+				case <-ctx.Done():
+					c.logger.Debugf("Quit proposing blocks, discarded %d blocks in the queue", len(ch))
+					return
+				}
+			}
+		}(ctx, ch)
+
+		return ch, cancel
 	}
 
 	becomeFollower := func() {
+		cancelProp()
 		c.blockInflight = 0
 		_ = c.support.BlockCutter().Cut()
 		stop()
@@ -591,7 +627,7 @@ func (c *Chain) serveRequest() {
 				stop()
 			}
 
-			c.propose(bc, batches...)
+			c.propose(propC, bc, batches...)
 
 			if c.configInflight {
 				c.logger.Info("Received config block, pause accepting transaction till it is committed")
@@ -610,7 +646,7 @@ func (c *Chain) serveRequest() {
 					c.Metrics.LeaderChanges.Add(1)
 
 					if newLeader == c.raftID {
-						becomeLeader()
+						propC, cancelProp = becomeLeader()
 					}
 
 					if soft.Lead == c.raftID {
@@ -654,7 +690,7 @@ func (c *Chain) serveRequest() {
 			c.apply(app.entries)
 
 			if c.justElected {
-				msgInflight := c.node.lastIndex() > c.appliedIndex
+				msgInflight := c.Node.lastIndex() > c.appliedIndex
 				if msgInflight || c.configInflight {
 					c.logger.Debugf("There are in flight blocks, new leader should not serve requests")
 					continue
@@ -686,7 +722,7 @@ func (c *Chain) serveRequest() {
 			}
 
 			c.logger.Debugf("Batch timer expired, creating block")
-			c.propose(bc, batch) // we are certain this is normal block, no need to block
+			c.propose(propC, bc, batch) // we are certain this is normal block, no need to block
 
 		case sn := <-c.snapC:
 			if sn.Metadata.Index <= c.appliedIndex {
@@ -705,6 +741,8 @@ func (c *Chain) serveRequest() {
 			}
 
 		case <-c.doneC:
+			cancelProp()
+
 			select {
 			case <-c.errorC: // avoid closing closed channel
 			default:
@@ -773,13 +811,14 @@ func (c *Chain) ordered(msg *orderer.SubmitRequest) (batches [][]*common.Envelop
 
 }
 
-func (c *Chain) propose(bc *blockCreator, batches ...[]*common.Envelope) {
+func (c *Chain) propose(ch chan<- *common.Block, bc *blockCreator, batches ...[]*common.Envelope) {
 	for _, batch := range batches {
 		b := bc.createNextBlock(batch)
-		data := utils.MarshalOrPanic(b)
-		if err := c.node.Propose(context.TODO(), data); err != nil {
-			c.logger.Errorf("Failed to propose block to raft: %s", err)
-			return // don't bother continue proposing next batch
+
+		select {
+		case ch <- b:
+		default:
+			c.logger.Panic("Programming error: limit of in-flight blocks does not properly take effect or block is proposed by follower")
 		}
 
 		// if it is config block, then we should wait for the commit of the block
@@ -788,7 +827,6 @@ func (c *Chain) propose(bc *blockCreator, batches ...[]*common.Envelope) {
 		}
 
 		c.blockInflight++
-		c.logger.Debugf("Proposed block %d to raft consensus, there are %d blocks in flight", b.Header.Number, c.blockInflight)
 	}
 
 	return
@@ -872,7 +910,7 @@ func (c *Chain) apply(ents []raftpb.Entry) {
 				continue
 			}
 
-			c.confState = *c.node.ApplyConfChange(cc)
+			c.confState = *c.Node.ApplyConfChange(cc)
 
 			switch cc.Type {
 			case raftpb.ConfChangeAddNode:
@@ -938,7 +976,7 @@ func (c *Chain) gc() {
 	for {
 		select {
 		case g := <-c.gcC:
-			c.node.takeSnapshot(g.index, g.state, g.data)
+			c.Node.takeSnapshot(g.index, g.state, g.data)
 		case <-c.doneC:
 			c.logger.Infof("Stop garbage collecting")
 			return
@@ -957,9 +995,9 @@ func (c *Chain) isConfig(env *common.Envelope) bool {
 
 func (c *Chain) configureComm() error {
 	// Reset unreachable map when communication is reconfigured
-	c.node.unreachableLock.Lock()
-	c.node.unreachable = make(map[uint64]struct{})
-	c.node.unreachableLock.Unlock()
+	c.Node.unreachableLock.Lock()
+	c.Node.unreachable = make(map[uint64]struct{})
+	c.Node.unreachableLock.Unlock()
 
 	nodes, err := c.remotePeers()
 	if err != nil {
@@ -1044,11 +1082,16 @@ func (c *Chain) writeConfigBlock(block *common.Block, index uint64) {
 
 	// update membership
 	if confChange != nil {
-		// ProposeConfChange returns error only if node being stopped.
-		// This proposal is dropped by followers because DisableProposalForwarding is enabled.
-		if err := c.node.ProposeConfChange(context.TODO(), *confChange); err != nil {
-			c.logger.Warnf("Failed to propose configuration update to Raft node: %s", err)
-		}
+		// We need to propose conf change in a go routine, because it may be blocked if raft node
+		// becomes leaderless, and we should not block `serveRequest` so it can keep consuming applyC,
+		// otherwise we have a deadlock.
+		go func() {
+			// ProposeConfChange returns error only if node being stopped.
+			// This proposal is dropped by followers because DisableProposalForwarding is enabled.
+			if err := c.Node.ProposeConfChange(context.TODO(), *confChange); err != nil {
+				c.logger.Warnf("Failed to propose configuration update to Raft node: %s", err)
+			}
+		}()
 
 		c.confChangeInProgress = confChange
 
@@ -1110,7 +1153,7 @@ func (c *Chain) getInFlightConfChange() *raftpb.ConfChange {
 	}
 
 	// extracting current Raft configuration state
-	confState := c.node.ApplyConfChange(raftpb.ConfChange{})
+	confState := c.Node.ApplyConfChange(raftpb.ConfChange{})
 
 	if len(confState.Nodes) == len(raftMetadata.Consenters) {
 		// since configuration change could only add one node or
```

### orderer/consensus/etcdraft/chain_test.go
```diff
@@ -74,7 +74,7 @@ var _ = Describe("Chain", func() {
 	BeforeEach(func() {
 		tlsCA, _ = tlsgen.NewCA()
 		channelID = "test-channel"
-		logger = flogging.NewFabricLogger(zap.NewNop())
+		logger = flogging.NewFabricLogger(zap.NewExample())
 		env = &common.Envelope{
 			Payload: marshalOrPanic(&common.Payload{
 				Header: &common.Header{ChannelHeader: marshalOrPanic(&common.ChannelHeader{Type: int32(common.HeaderType_MESSAGE), ChannelId: channelID})},
@@ -1869,6 +1869,68 @@ var _ = Describe("Chain", func() {
 					Consistently(c3.support.WriteBlockCallCount).Should(Equal(2))
 					Consistently(c1.support.WriteBlockCallCount).Should(Equal(1))
 				})
+
+				It("does not deadlock if leader steps down while config block is in-flight", func() {
+					configEnv := newConfigEnv(channelID, common.HeaderType_CONFIG, newConfigUpdateEnv(channelID, addConsenterConfigValue()))
+					c1.cutter.CutNext = true
+
+					signal := make(chan struct{})
+					stub := c1.support.WriteConfigBlockStub
+					c1.support.WriteConfigBlockStub = func(b *common.Block, meta []byte) {
+						signal <- struct{}{}
+						<-signal
+						stub(b, meta)
+					}
+
+					By("Sending config transaction")
+					Expect(c1.Configure(configEnv, 0)).To(Succeed())
+
+					Eventually(signal, LongEventualTimeout).Should(Receive())
+					network.disconnect(1)
+
+					By("Ticking leader till it steps down")
+					Eventually(func() raft.SoftState {
+						c1.clock.Increment(interval)
+						return c1.Node.Status().SoftState
+					}, LongEventualTimeout).Should(StateEqual(0, raft.StateFollower))
+
+					close(signal)
+
+					Eventually(c1.observe, LongEventualTimeout).Should(Receive(StateEqual(0, raft.StateFollower)))
+
+					By("Re-electing 1 as leader")
+					network.connect(1)
+					network.elect(1)
+
+					_, raftmetabytes := c1.support.WriteConfigBlockArgsForCall(0)
+					meta := &common.Metadata{Value: raftmetabytes}
+					raftmeta, err := etcdraft.ReadRaftMetadata(meta, nil)
+					Expect(err).NotTo(HaveOccurred())
+
+					c4 := newChain(timeout, channelID, dataDir, 4, raftmeta)
+					c4.init()
+
+					// if we join a node to existing network, it MUST already obtained blocks
+					// till the config block that adds this node to cluster.
+					c4.support.WriteBlock(c1.support.WriteBlockArgsForCall(0))
+					c4.support.WriteConfigBlock(c1.support.WriteConfigBlockArgsForCall(0))
+
+					network.addChain(c4)
+					c4.Start()
+
+					Eventually(func() <-chan raft.SoftState {
+						c1.clock.Increment(interval)
+						return c4.observe
+					}, LongEventualTimeout).Should(Receive(StateEqual(1, raft.StateFollower)))
+
+					By("Submitting tx to confirm network is still working")
+					Expect(c1.Order(env, 0)).To(Succeed())
+
+					network.exec(func(c *chain) {
+						Eventually(c.support.WriteBlockCallCount, LongEventualTimeout).Should(Equal(2))
+						Eventually(c.support.WriteConfigBlockCallCount, LongEventualTimeout).Should(Equal(1))
+					})
+				})
 			})
 		})
 
@@ -2055,6 +2117,47 @@ var _ = Describe("Chain", func() {
 					err = c1.Order(env, 0)
 					Expect(err).NotTo(HaveOccurred())
 				})
+
+				It("does not deadlock if propose is blocked", func() {
+					signal := make(chan struct{})
+					c1.cutter.CutNext = true
+					c1.support.SequenceStub = func() uint64 {
+						signal <- struct{}{}
+						<-signal
+						return 0
+					}
+
+					By("Sending a normal transaction")
+					Expect(c1.Order(env, 0)).To(Succeed())
+
+					Eventually(signal).Should(Receive())
+					network.disconnect(1)
+
+					By("Ticking leader till it steps down")
+					Eventually(func() raft.SoftState {
+						c1.clock.Increment(interval)
+						return c1.Node.Status().SoftState
+					}).Should(StateEqual(0, raft.StateFollower))
+
+					close(signal)
+
+					Eventually(c1.observe).Should(Receive(StateEqual(0, raft.StateFollower)))
+					c1.support.SequenceStub = nil
+					network.exec(func(c *chain) {
+						Eventually(c.support.WriteBlockCallCount, LongEventualTimeout).Should(Equal(0))
+					})
+
+					By("Re-electing 1 as leader")
+					network.connect(1)
+					network.elect(1)
+
+					By("Sending another normal transaction")
+					Expect(c1.Order(env, 0)).To(Succeed())
+
+					network.exec(func(c *chain) {
+						Eventually(c.support.WriteBlockCallCount, LongEventualTimeout).Should(Equal(1))
+					})
+				})
 			})
 
 			When("follower is disconnected", func() {
@@ -2688,7 +2791,7 @@ func newChain(timeout time.Duration, channel string, dataDir string, id uint64,
 		MaxSizePerMsg:   1024 * 1024,
 		MaxInflightMsgs: 256,
 		RaftMetadata:    raftMetadata,
-		Logger:          flogging.NewFabricLogger(zap.NewNop()),
+		Logger:          flogging.NewFabricLogger(zap.NewExample()),
 		MemoryStorage:   storage,
 		WALDir:          path.Join(dataDir, "wal"),
 		SnapDir:         path.Join(dataDir, "snapshot"),
```

### orderer/consensus/etcdraft/node.go
```diff
@@ -87,7 +87,11 @@ func (n *node) run() {
 				n.chain.snapC <- &rd.Snapshot
 			}
 
-			n.chain.applyC <- apply{rd.CommittedEntries, rd.SoftState}
+			// skip empty apply
+			if len(rd.CommittedEntries) != 0 || rd.SoftState != nil {
+				n.chain.applyC <- apply{rd.CommittedEntries, rd.SoftState}
+			}
+
 			n.Advance()
 
 			// TODO(jay_guo) leader can write to disk in parallel with replicating
```
