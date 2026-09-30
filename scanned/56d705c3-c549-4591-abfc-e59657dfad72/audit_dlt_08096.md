# [?] Merge pull request #10108 from yyforyongyu/fix-arb-deadlock

## Summary
Severity: Unknown
Chain: Bitcoin/Lightning
Component: lightningnetwork/lnd
Published: 2025-07-25
Source: https://github.com/lightningnetwork/lnd/commit/839370946ef85e9f1cea5e8c0fd3766a3034c1a6
Type: security-commit

## Details
Merge pull request #10108 from yyforyongyu/fix-arb-deadlock

Fix arbitrator deadlock found in `ResolveContract`

## Patch
### contractcourt/chain_arbitrator.go
```diff
@@ -270,6 +270,11 @@ type ChainArbitrator struct {
 	// beat is the current best known blockbeat.
 	beat chainio.Blockbeat
 
+	// resolvedChan is used to signal that the given channel outpoint has
+	// been resolved onchain. Once received, chain arbitrator will perform
+	// cleanups.
+	resolvedChan chan wire.OutPoint
+
 	quit chan struct{}
 
 	wg sync.WaitGroup
@@ -286,6 +291,7 @@ func NewChainArbitrator(cfg ChainArbitratorConfig,
 		activeWatchers: make(map[wire.OutPoint]*chainWatcher),
 		chanSource:     db,
 		quit:           make(chan struct{}),
+		resolvedChan:   make(chan wire.OutPoint),
 	}
 
 	// Mount the block consumer.
@@ -459,6 +465,9 @@ func newActiveChannelArbitrator(channel *channeldb.OpenChannel,
 				channel.ShortChanID(), htlc,
 			)
 		},
+		NotifyChannelResolved: func() {
+			c.notifyChannelResolved(chanPoint)
+		},
 	}
 
 	// The final component needed is an arbitrator log that the arbitrator
@@ -474,14 +483,6 @@ func newActiveChannelArbitrator(channel *channeldb.OpenChannel,
 		return nil, err
 	}
 
-	arbCfg.MarkChannelResolved = func() error {
-		if c.cfg.NotifyFullyResolvedChannel != nil {
-			c.cfg.NotifyFullyResolvedChannel(chanPoint)
-		}
-
-		return c.ResolveContract(chanPoint)
-	}
-
 	// Finally, we'll need to construct a series of htlc Sets based on all
 	// currently known valid commitments.
 	htlcSets := make(map[HtlcSetKey]htlcSet)
@@ -578,6 +579,17 @@ func (c *ChainArbitrator) Start(beat chainio.Blockbeat) error {
 	// Set the current beat.
 	c.beat = beat
 
+	// Start the goroutine which listens for signals to mark the channel as
+	// resolved.
+	//
+	// NOTE: We must start this goroutine here we won't block the following
+	// channel loading.
+	c.wg.Add(1)
+	go func() {
+		defer c.wg.Done()
+		c.resolveContracts()
+	}()
+
 	// First, we'll fetch all the channels that are still open, in order to
 	// collect them within our set of active contracts.
 	if err := c.loadOpenChannels(); err != nil {
@@ -697,6 +709,32 @@ func (c *ChainArbitrator) Start(beat chainio.Blockbeat) error {
 	return nil
 }
 
+// resolveContracts listens to the `resolvedChan` to mark a given channel as
+// fully resolved.
+func (c *ChainArbitrator) resolveContracts() {
+	for {
+		select {
+		// The channel arbitrator signals that a given channel has been
+		// resolved, we now update chain arbitrator's internal state for
+		// this channel.
+		case cp := <-c.resolvedChan:
+			if c.cfg.NotifyFullyResolvedChannel != nil {
+				c.cfg.NotifyFullyResolvedChannel(cp)
+			}
+
+			err := c.ResolveContract(cp)
+			if err != nil {
+				log.Errorf("Failed to resolve contract for "+
+					"channel %v", cp)
+			}
+
+		// Exit if the chain arbitrator is shutting down.
+		case <-c.quit:
+			return
+		}
+	}
+}
+
 // dispatchBlocks consumes a block epoch notification stream and dispatches
 // blocks to each of the chain arb's active channel arbitrators. This function
 // must be run in a goroutine.
@@ -762,6 +800,16 @@ func (c *ChainArbitrator) handleBlockbeat(beat chainio.Blockbeat) {
 	c.NotifyBlockProcessed(beat, err)
 }
 
+// notifyChannelResolved is used by the channel arbitrator to signal that a
+// given channel has been resolved.
+func (c *ChainArbitrator) notifyChannelResolved(cp wire.OutPoint) {
+	select {
+	case c.resolvedChan <- cp:
+	case <-c.quit:
+		return
+	}
+}
+
 // republishClosingTxs will load any stored cooperative or unilateral closing
 // transactions and republish them. This helps ensure propagation of the
 // transactions in the event that prior publications failed.
@@ -1346,20 +1394,16 @@ func (c *ChainArbitrator) loadPendingCloseChannels() error {
 					closeChanInfo.ShortChanID, htlc,
 				)
 			},
+			NotifyChannelResolved: func() {
+				c.notifyChannelResolved(chanPoint)
+			},
 		}
 		chanLog, err := newBoltArbitratorLog(
 			c.chanSource.Backend, arbCfg, c.cfg.ChainHash, chanPoint,
 		)
 		if err != nil {
 			return err
 		}
-		arbCfg.MarkChannelResolved = func() error {
-			if c.cfg.NotifyFullyResolvedChannel != nil {
-				c.cfg.NotifyFullyResolvedChannel(chanPoint)
-			}
-
-			return c.ResolveContract(chanPoint)
-		}
 
 		// We create an empty map of HTLC's here since it's possible
 		// that the channel is in StateDefault and updateActiveHTLCs is
```

### contractcourt/channel_arbitrator.go
```diff
@@ -153,13 +153,9 @@ type ChannelArbitratorConfig struct {
 	// true. Otherwise this value is unset.
 	CloseType channeldb.ClosureType
 
-	// MarkChannelResolved is a function closure that serves to mark a
-	// channel as "fully resolved". A channel itself can be considered
-	// fully resolved once all active contracts have individually been
-	// fully resolved.
-	//
-	// TODO(roasbeef): need RPC's to combine for pendingchannels RPC
-	MarkChannelResolved func() error
+	// NotifyChannelResolved is used by the channel arbitrator to signal
+	// that a given channel has been resolved.
+	NotifyChannelResolved func()
 
 	// PutResolverReport records a resolver report for the channel. If the
 	// transaction provided is nil, the function should write the report
@@ -1397,10 +1393,7 @@ func (c *ChannelArbitrator) stateStep(
 		log.Infof("ChannelPoint(%v) has been fully resolved "+
 			"on-chain at height=%v", c.cfg.ChanPoint, triggerHeight)
 
-		if err := c.cfg.MarkChannelResolved(); err != nil {
-			log.Errorf("unable to mark channel resolved: %v", err)
-			return StateError, closeTx, err
-		}
+		c.cfg.NotifyChannelResolved()
 	}
 
 	log.Tracef("ChannelArbitrator(%v): next_state=%v", c.cfg.ChanPoint,
```

### contractcourt/channel_arbitrator_test.go
```diff
@@ -417,17 +417,16 @@ func createTestChannelArbitrator(t *testing.T, log ArbitratorLog,
 	}
 
 	// We'll use the resolvedChan to synchronize on call to
-	// MarkChannelResolved.
+	// NotifyChannelResolved.
 	resolvedChan := make(chan struct{}, 1)
 
 	// Next we'll create the matching configuration struct that contains
 	// all interfaces and methods the arbitrator needs to do its job.
 	arbCfg := &ChannelArbitratorConfig{
 		ChanPoint:   chanPoint,
 		ShortChanID: shortChanID,
-		MarkChannelResolved: func() error {
+		NotifyChannelResolved: func() {
 			resolvedChan <- struct{}{}
-			return nil
 		},
 		MarkCommitmentBroadcasted: func(_ *wire.MsgTx,
 			_ lntypes.ChannelParty) error {
@@ -547,7 +546,7 @@ func TestChannelArbitratorCooperativeClose(t *testing.T) {
 	}
 
 	// Cooperative close should do trigger a MarkChannelClosed +
-	// MarkChannelResolved.
+	// NotifyChannelResolved.
 	closeInfo := &CooperativeCloseInfo{
 		&channeldb.ChannelCloseSummary{},
 	}
```

### docs/release-notes/release-notes-0.20.0.md
```diff
@@ -33,6 +33,10 @@
   known TLV fields were incorrectly encoded into the `ExtraData` field of
   messages in the dynamic commitment set.
 
+- Fixed a [deadlock](https://github.com/lightningnetwork/lnd/pull/10108) that
+  can cause contract resolvers to be stuck at marking the channel force close as
+  being complete.
+
 # New Features
 
 ## Functional Enhancements
```
