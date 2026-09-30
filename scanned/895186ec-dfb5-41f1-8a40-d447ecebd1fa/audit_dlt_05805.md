# [?] Wait for blocksync goroutines on Stop to fix leveldb shutdown panic (#3415)

## Summary
Severity: Unknown
Chain: Sei
Component: sei-protocol/sei-chain
Published: 2026-05-15
Source: https://github.com/sei-protocol/sei-chain/commit/a27b9d64d394745a28e08f22c92cc666d6dfcb8c
Type: security-commit

## Details
Wait for blocksync goroutines on Stop to fix leveldb shutdown panic (#3415)

Reactor.OnStart and BlockPool.OnStart started their long-running
goroutines (requestRoutine, poolRoutine, processBlockSyncCh,
processPeerUpdates, makeRequestersRoutine) with raw `go fn(ctx)` using
the outer context. They were therefore not registered with the
BaseService WaitGroup, and Stop() never waited for them. The outer ctx
also outlived Stop, so the goroutines kept running after Stop returned.

During node shutdown this raced nodeImpl.OnStop's blockStore.Close():
poolRoutine, still inside SaveBlock -> Base() -> bs.db.Iterator,
observed its leveldb table reader released and panicked with
"leveldb/table: reader released".

Route each goroutine through BaseService.Spawn so it is tracked by the
WaitGroup and bound to inner.ctx. Stop() now cancels them and blocks
until they exit, which happens before the node closes the BlockStore DB.
Add a regression test that asserts no blocksync goroutines remain after
Reactor.Stop() returns.

<!-- CURSOR_SUMMARY -->
---

> [!NOTE]
> **Medium Risk**
> Changes blocksync/consensus goroutine lifecycles and shutdown
ordering; mistakes could cause hangs or missed transitions, but the
change is localized and covered by a new regression test.
> 
> **Overview**
> Fixes blocksync shutdown races by moving long-running goroutines off
raw `go` launches and onto `BaseService.Spawn`/`SpawnCritical`, ensuring
`Stop()` cancels the correct context and waits for all blocksync
routines to exit before the block store is closed.
> 
> Adds readiness gates (`blocksyncReady`, `consensusReady`) so routines
can be pre-spawned in `Reactor.OnStart` yet only begin work when block
sync starts or the consensus handoff completes, and updates
`BlockPool`/`bpRequester` shutdown to avoid blocking on a full
`requestsCh`.
> 
> Updates the consensus handoff API (`SwitchToConsensus` signature) and
adds a regression test (`TestReactor_OnStopWaitsForGoroutines`) that
asserts no `internal/blocksync` goroutines remain after `Reactor.Stop()`
returns.
> 
> <sup>Reviewed by [Cursor Bugbot](https://cursor.com/bugbot) for commit
54793157e74446059bba5979cf6216a9db3b01f7. Bugbot is set up for automated
code reviews on this repo. Configure
[here](https://www.cursor.com/dashboard/bugbot).</sup>
<!-- /CURSOR_SUMMARY -->

### sei-tendermint/internal/blocksync/pool.go
```diff
@@ -135,20 +135,33 @@ func NewBlockPool(
 func (pool *BlockPool) OnStart(ctx context.Context) error {
 	pool.lastAdvance = time.Now()
 	pool.lastHundredBlockTimeStamp = pool.lastAdvance
-	go pool.makeRequestersRoutine(ctx)
+	pool.Spawn("makeRequestersRoutine", func(ctx context.Context) error {
+		pool.makeRequestersRoutine(ctx)
+		return nil
+	})
 
 	return nil
 }
 
 func (pool *BlockPool) OnStop() {
+	// Requester shutdown must not block behind a full requestsCh; Stop cancels ctx
+	// and waits for the Spawn-managed requester goroutine to exit.
 	pool.mtx.Lock()
-	defer pool.mtx.Unlock()
+	cancels := pool.cancels
+	pool.cancels = nil
+	requesters := make([]*bpRequester, 0, len(pool.requesters))
+	for _, requester := range pool.requesters {
+		requesters = append(requesters, requester)
+	}
+	pool.mtx.Unlock()
 
-	// cancel all running requesters if any
-	for _, cancel := range pool.cancels {
+	// Stop requesters outside pool.mtx; their shutdown path may observe pool state.
+	for _, cancel := range cancels {
 		cancel()
 	}
-	pool.cancels = []context.CancelFunc{}
+	for _, requester := range requesters {
+		requester.Stop()
+	}
 }
 
 // spawns requesters as needed
@@ -500,11 +513,16 @@ func (pool *BlockPool) requestersLen() int64 {
 	return int64(len(pool.requesters))
 }
 
-func (pool *BlockPool) sendRequest(height int64, peerID types.NodeID) {
+func (pool *BlockPool) sendRequest(ctx context.Context, height int64, peerID types.NodeID) bool {
 	if !pool.IsRunning() {
-		return
+		return false
+	}
+	select {
+	case pool.requestsCh <- BlockRequest{height, peerID}:
+		return true
+	case <-ctx.Done():
+		return false
 	}
-	pool.requestsCh <- BlockRequest{height, peerID}
 }
 
 func (pool *BlockPool) sendError(err error, peerID types.NodeID) {
@@ -622,7 +640,10 @@ func newBPRequester(pool *BlockPool, height int64) *bpRequester {
 }
 
 func (bpr *bpRequester) OnStart(ctx context.Context) error {
-	go bpr.requestRoutine(ctx)
+	bpr.Spawn("requestRoutine", func(ctx context.Context) error {
+		bpr.requestRoutine(ctx)
+		return nil
+	})
 	return nil
 }
 
@@ -695,14 +716,15 @@ func (bpr *bpRequester) redo(peerID types.NodeID, retryReason RetryReason) {
 // Responsible for making more requests as necessary
 // Returns only when a block is found (e.g. AddBlock() is called)
 func (bpr *bpRequester) requestRoutine(ctx context.Context) {
+	defer bpr.timeoutTicker.Stop()
+
 OUTER_LOOP:
 	for {
 		// Pick a peer to send request to.
 		var peer *bpPeer
 	PICK_PEER_LOOP:
 		for {
 			if !bpr.IsRunning() || !bpr.pool.IsRunning() || ctx.Err() != nil {
-				bpr.timeoutTicker.Stop()
 				return
 			}
 			if ctx.Err() != nil {
@@ -724,13 +746,14 @@ OUTER_LOOP:
 		bpr.mtx.Unlock()
 
 		// Send request and wait.
-		bpr.pool.sendRequest(bpr.height, peer.id)
+		if !bpr.pool.sendRequest(ctx, bpr.height, peer.id) {
+			return
+		}
 		bpr.timeoutTicker.Reset(peerTimeout)
 	WAIT_LOOP:
 		for {
 			select {
 			case <-ctx.Done():
-				bpr.timeoutTicker.Stop()
 				return
 			case redoOp := <-bpr.redoCh:
 				// if we don't have an existing block or this is a bad block
@@ -747,9 +770,6 @@ OUTER_LOOP:
 				}
 			case <-bpr.gotBlockCh:
 				// We got a block!
-				// Stop the goroutine to avoid leak
-				bpr.timeoutTicker.Stop()
-				bpr.Stop()
 				return
 			}
 		}
```

### sei-tendermint/internal/blocksync/reactor.go
```diff
@@ -72,7 +72,7 @@ func GetChannelDescriptor() p2p.ChannelDescriptor[*pb.Message] {
 type consensusReactor interface {
 	// For when we switch from block sync reactor to the consensus
 	// machine.
-	SwitchToConsensus(ctx context.Context, state sm.State, skipWAL bool)
+	SwitchToConsensus(state sm.State, skipWAL bool)
 }
 
 type peerError struct {
@@ -84,6 +84,8 @@ func (e peerError) Error() string {
 	return fmt.Sprintf("error with peer %v: %s", e.peerID, e.err.Error())
 }
 
+type blocksyncResult struct{ stateSynced bool }
+
 // Reactor handles long-term catchup syncing.
 type Reactor struct {
 	service.BaseService
@@ -100,6 +102,16 @@ type Reactor struct {
 	blockSync             *atomicBool
 	previousMaxPeerHeight int64
 
+	// blocksyncReady fires when blocksync should start processing blocks —
+	// either at OnStart (if blockSync was initially set) or via
+	// SwitchToBlockSync. Pre-spawned requestRoutine and poolRoutine wait on
+	// it before doing any work.
+	blocksyncReady utils.AtomicSend[utils.Option[blocksyncResult]]
+	// consensusReady fires once the blocksync->consensus handoff has
+	// happened. The pre-spawned autoRestartIfBehind monitor gates on this
+	// signal.
+	consensusReady utils.AtomicSend[bool]
+
 	router  *p2p.Router
 	channel *p2p.Channel[*pb.Message]
 
@@ -150,8 +162,9 @@ func NewReactor(
 		blocksBehindThreshold:     selfRemediationConfig.BlocksBehindThreshold,
 		blocksBehindCheckInterval: time.Duration(selfRemediationConfig.BlocksBehindCheckIntervalSeconds) * time.Second, //nolint:gosec // validated in config.ValidateBasic against MaxInt64
 		restartCooldownSeconds:    selfRemediationConfig.RestartCooldownSeconds,
+		blocksyncReady:            utils.NewAtomicSend(utils.None[blocksyncResult]()),
+		consensusReady:            utils.NewAtomicSend(false),
 	}
-
 	r.BaseService = *service.NewBaseService("BlockSync", r)
 	return r, nil
 }
@@ -186,23 +199,60 @@ func (r *Reactor) OnStart(ctx context.Context) error {
 	r.requestsCh = requestsCh
 	r.errorsCh = errorsCh
 
+	// Pre-spawn all long-running routines so their lifetime is bound to the
+	// BaseService WaitGroup. Conditional routines gate on AtomicSend[bool]
+	// signals so SwitchToBlockSync (and the in-poolRoutine consensus handoff
+	// for autoRestartIfBehind) can wake them later without spawning fresh
+	// goroutines from outside OnStart.
+	r.Spawn("requestRoutine", func(ctx context.Context) error {
+		_, err := r.blocksyncReady.Wait(ctx, func(o utils.Option[blocksyncResult]) bool {
+			return o.IsPresent()
+		})
+		if err != nil {
+			return err
+		}
+		r.requestRoutine(ctx)
+		return nil
+	})
+	r.Spawn("poolRoutine", func(ctx context.Context) error {
+		result, err := r.blocksyncReady.Wait(ctx, func(o utils.Option[blocksyncResult]) bool {
+			return o.IsPresent()
+		})
+		if err != nil {
+			return err
+		}
+		res := result.OrPanic("no blocksync result")
+		r.poolRoutine(ctx, res.stateSynced)
+		return nil
+	})
+	r.SpawnCritical("processBlockSyncCh", func(ctx context.Context) error {
+		r.processBlockSyncCh(ctx)
+		return nil
+	})
+	r.SpawnCritical("processPeerUpdates", func(ctx context.Context) error {
+		r.processPeerUpdates(ctx)
+		return nil
+	})
+	r.SpawnCritical("autoRestartIfBehind", func(ctx context.Context) error {
+		if _, err := r.consensusReady.Wait(ctx, func(ready bool) bool { return ready }); err != nil {
+			return err
+		}
+		r.autoRestartIfBehind(ctx)
+		return nil
+	})
+
 	if r.blockSync.IsSet() {
 		if err := r.pool.Start(ctx); err != nil {
 			return err
 		}
-		go r.requestRoutine(ctx)
-
-		go r.poolRoutine(ctx, false)
+		r.blocksyncReady.Store(utils.Some(blocksyncResult{false}))
 	}
-
-	go r.processBlockSyncCh(ctx)
-	go r.processPeerUpdates(ctx)
-
 	return nil
 }
 
-// OnStop stops the reactor by signaling to all spawned goroutines to exit and
-// blocking until they all exit.
+// OnStop stops the BlockPool. The reactor's own long-running goroutines were
+// registered with the BaseService WaitGroup via Spawn in OnStart, so the
+// BaseService blocks Stop() on their exit before this method returns.
 func (r *Reactor) OnStop() {
 	if r.blockSync.IsSet() {
 		r.pool.Stop()
@@ -380,9 +430,7 @@ func (r *Reactor) SwitchToBlockSync(ctx context.Context, state sm.State) error {
 	}
 
 	r.syncStartTime = time.Now()
-
-	go r.requestRoutine(ctx)
-	go r.poolRoutine(ctx, true)
+	r.blocksyncReady.Store(utils.Some(blocksyncResult{true}))
 
 	if err := r.PublishStatus(types.EventDataBlockSyncStatus{
 		Complete: false,
@@ -475,10 +523,11 @@ func (r *Reactor) poolRoutine(ctx context.Context, stateSynced bool) {
 
 			if r.consReactor != nil {
 				logger.Info("switching to consensus reactor", "height", height, "blocks_synced", blocksSynced, "state_synced", stateSynced, "max_peer_height", r.pool.MaxPeerHeight())
-				r.consReactor.SwitchToConsensus(ctx, state, blocksSynced > 0 || stateSynced)
-
-				// Auto restart should only be checked after switching to consensus mode
-				go r.autoRestartIfBehind(ctx)
+				// Use the node-scoped context: SwitchToConsensus is a handoff
+				// to a peer reactor whose lifecycle is not tied to blocksync.
+				r.consReactor.SwitchToConsensus(state, blocksSynced > 0 || stateSynced)
+				// Wake the pre-spawned auto-restart monitor.
+				r.consensusReady.Store(true)
 			}
 
 			return
```

### sei-tendermint/internal/blocksync/reactor_test.go
```diff
@@ -2,6 +2,8 @@ package blocksync
 
 import (
 	"context"
+	"runtime"
+	"strings"
 	"testing"
 	"time"
 
@@ -242,6 +244,85 @@ func TestReactor_AbruptDisconnect(t *testing.T) {
 	rts.network.Remove(t, rts.nodes[0])
 }
 
+// TestReactor_OnStopWaitsForGoroutines is a regression test for the
+// "panic: leveldb/table: reader released" shutdown panic seen on v6.4.4
+// sentry nodes. Before the fix, blocksync's long-running goroutines
+// (Reactor.requestRoutine, Reactor.poolRoutine, Reactor.processBlockSyncCh,
+// Reactor.processPeerUpdates, Reactor.autoRestartIfBehind, and
+// BlockPool.makeRequestersRoutine) were started with raw `go fn(ctx)` using
+// the outer ctx, instead of `Spawn(...)` which would register them with the
+// BaseService WaitGroup and bind them to BaseService.inner.ctx. As a result,
+// Reactor.Stop() / BlockPool.Stop() — which cancels only the inner ctx —
+// did not signal these goroutines to exit, let alone wait for them. The
+// node's OnStop then proceeded to n.blockStore.Close() while poolRoutine
+// was still mid-SaveBlock -> Base() -> bs.db.Iterator, causing goleveldb to
+// panic when the table reader was released underneath the live iterator.
+//
+// This test asserts the fix: after `reactor.Stop()` returns, the
+// blocksync-package goroutines have exited. The outer ctx is still live at
+// this point in the test, so the unfixed code keeps them running and the
+// assertion fails deterministically. On failure the live goroutine stacks
+// are dumped to make the leak obvious.
+func TestReactor_OnStopWaitsForGoroutines(t *testing.T) {
+	ctx := t.Context()
+
+	cfg, err := config.ResetTestRoot(t.TempDir(), "block_sync_reactor_stop_test")
+	require.NoError(t, err)
+
+	valSet, privVals := factory.ValidatorSet(ctx, 1, 30)
+	genDoc := factory.GenesisDoc(cfg, time.Now(), valSet.Validators, factory.ConsensusParams())
+
+	rts := setup(ctx, t, genDoc, privVals[0], []int64{0})
+
+	reactor := rts.reactors[rts.nodes[0]]
+	require.True(t, reactor.IsRunning())
+
+	dumpBlocksyncGoroutines := func() (string, int) {
+		buf := make([]byte, 1<<20)
+		n := runtime.Stack(buf, true)
+		var out strings.Builder
+		count := 0
+		for _, g := range strings.Split(string(buf[:n]), "\n\n") {
+			if !strings.Contains(g, "/internal/blocksync.") {
+				continue
+			}
+			// The test functions themselves live in the blocksync package, so
+			// runtime.Stack reports them as matches. Only count background
+			// routines spawned by Reactor.OnStart and BlockPool.OnStart,
+			// which are created by libs/service.Spawn, not testing.tRunner.
+			if strings.Contains(g, "testing.tRunner") {
+				continue
+			}
+			out.WriteString(g)
+			out.WriteString("\n\n")
+			count++
+		}
+		return out.String(), count
+	}
+
+	// OnStart Spawns 5 reactor routines and BlockPool.OnStart Spawns 1.
+	require.Eventually(t, func() bool {
+		_, c := dumpBlocksyncGoroutines()
+		return c >= 6
+	}, 5*time.Second, 10*time.Millisecond, "blocksync goroutines did not start")
+
+	reactor.Stop()
+	require.False(t, reactor.IsRunning())
+
+	deadline := time.Now().Add(2 * time.Second)
+	for time.Now().Before(deadline) {
+		if _, c := dumpBlocksyncGoroutines(); c == 0 {
+			return
+		}
+		time.Sleep(time.Millisecond)
+	}
+	dump, c := dumpBlocksyncGoroutines()
+	t.Fatalf("%d blocksync goroutine(s) still alive after Reactor.Stop() returned. "+
+		"This means at least one routine was not registered with the "+
+		"BaseService WaitGroup via Spawn(), so Stop did not wait for it. "+
+		"Live stacks:\n\n%s", c, dump)
+}
+
 func TestReactor_SyncTime(t *testing.T) {
 	ctx := t.Context()
 
```

### sei-tendermint/internal/consensus/byzantine_test.go
```diff
@@ -239,7 +239,7 @@ package consensus
 //
 //	for _, reactor := range rts.reactors {
 //		reactor.StopWaitSync()
-//		reactor.SwitchToConsensus(ctx, reactor.state.GetState(), false)
+//		reactor.SwitchToConsensus(reactor.state.GetState(), false)
 //	}
 //
 //	// Evidence should be submitted and committed at the third height but
```

### sei-tendermint/internal/consensus/invalid_test.go
```diff
@@ -46,7 +46,7 @@ func TestGossipVotesForHeightPoisonedProposalPOL(t *testing.T) {
 	reactor := rts.reactors[nodeIDs[0]]
 	peerID := nodeIDs[1]
 	state := reactor.state.GetState()
-	reactor.SwitchToConsensus(ctx, state, false)
+	reactor.SwitchToConsensus(state, false)
 
 	require.Eventually(t, func() bool {
 		_, ok := reactor.GetPeerState(peerID)
@@ -176,7 +176,7 @@ func TestReactorInvalidPrecommit(t *testing.T) {
 
 	for _, reactor := range rts.reactors {
 		state := reactor.state.GetState()
-		reactor.SwitchToConsensus(ctx, state, false)
+		reactor.SwitchToConsensus(state, false)
 	}
 
 	// this val sends a random precommit at each height
```

### sei-tendermint/internal/consensus/reactor.go
```diff
@@ -204,7 +204,7 @@ func (r *Reactor) WaitSync() bool {
 
 // SwitchToConsensus switches from block-sync mode to consensus mode. It resets
 // the state, turns off block-sync, and starts the consensus state-machine.
-func (r *Reactor) SwitchToConsensus(ctx context.Context, state sm.State, skipWAL bool) {
+func (r *Reactor) SwitchToConsensus(state sm.State, skipWAL bool) {
 	logger.Info("switching to consensus")
 
 	d := types.EventDataBlockSyncStatus{Complete: true, Height: state.LastBlockHeight}
```

### sei-tendermint/internal/consensus/reactor_test.go
```diff
@@ -196,7 +196,7 @@ func TestReactorBasic(t *testing.T) {
 
 	for _, reactor := range rts.reactors {
 		state := reactor.state.GetState()
-		reactor.SwitchToConsensus(ctx, state, false)
+		reactor.SwitchToConsensus(state, false)
 	}
 
 	t.Logf("wait till everyone makes the first new block")
@@ -312,7 +312,7 @@ func TestReactorWithEvidence(t *testing.T) {
 
 	for _, reactor := range rts.reactors {
 		state := reactor.state.GetState()
-		reactor.SwitchToConsensus(ctx, state, false)
+		reactor.SwitchToConsensus(state, false)
 	}
 
 	var wg sync.WaitGroup
@@ -360,7 +360,7 @@ func TestReactorCreatesBlockWhenEmptyBlocksFalse(t *testing.T) {
 
 	for _, reactor := range rts.reactors {
 		state := reactor.state.GetState()
-		reactor.SwitchToConsensus(ctx, state, false)
+		reactor.SwitchToConsensus(state, false)
 	}
 
 	// send a tx
@@ -404,7 +404,7 @@ func TestReactorRecordsVotesAndBlockParts(t *testing.T) {
 
 	for _, reactor := range rts.reactors {
 		state := reactor.state.GetState()
-		reactor.SwitchToConsensus(ctx, state, false)
+		reactor.SwitchToConsensus(state, false)
 	}
 
 	var wg sync.WaitGroup
@@ -475,7 +475,7 @@ func TestReactorValidatorSetChanges(t *testing.T) {
 	rts := setup(ctx, t, nPeers, unwrapTestStates(states), 1024) // buffer must be large enough to not deadlock
 	for _, reactor := range rts.reactors {
 		state := reactor.state.GetState()
-		reactor.SwitchToConsensus(ctx, state, false)
+		reactor.SwitchToConsensus(state, false)
 	}
 
 	blocksSubs := []eventbus.Subscription{}
```
