# [?] blockchain/v2: fix "panic: duplicate block enqueued by processor" (#5499)

## Summary
Severity: Unknown
Chain: Cosmos
Component: cometbft/cometbft
Published: 2020-10-20
Source: https://github.com/cometbft/cometbft/commit/79d535dd67416ab2926b30c3f48ecb784e2f6c38
Type: security-commit

## Details
blockchain/v2: fix "panic: duplicate block enqueued by processor" (#5499)

When a peer is stopped due to some network issue, the Reactor calls scheduler#handleRemovePeer, which removes the peer from the scheduler. BUT the peer stays in the processor, which sometimes could lead to "duplicate block enqueued by processor" panic WHEN the same block is requested by the scheduler again from a different peer. The solution is to return scPeerError, which will be propagated to the processor. The processor will clean up the blocks associated with the peer in purgePeer.

Closes #5513, #5517

## Patch
### CHANGELOG_PENDING.md
```diff
@@ -26,4 +26,5 @@ Friendly reminder, we have a [bug bounty program](https://hackerone.com/tendermi
 
 ### BUG FIXES
 
+- [blockchain/v2] \#5499 Fix "duplicate block enqueued by processor" panic (@melekes)
 - [abci/grpc] \#5520 Return async responses in order, to avoid mempool panics. (@erikgrinaker)
```

### blockchain/v2/processor.go
```diff
@@ -17,13 +17,22 @@ type pcBlockVerificationFailure struct {
 	secondPeerID p2p.ID
 }
 
+func (e pcBlockVerificationFailure) String() string {
+	return fmt.Sprintf("pcBlockVerificationFailure{%d 1st peer: %v, 2nd peer: %v}",
+		e.height, e.firstPeerID, e.secondPeerID)
+}
+
 // successful block execution
 type pcBlockProcessed struct {
 	priorityNormal
 	height int64
 	peerID p2p.ID
 }
 
+func (e pcBlockProcessed) String() string {
+	return fmt.Sprintf("pcBlockProcessed{%d peer: %v}", e.height, e.peerID)
+}
+
 // processor has finished
 type pcFinished struct {
 	priorityNormal
@@ -87,9 +96,12 @@ func (state *pcState) synced() bool {
 }
 
 func (state *pcState) enqueue(peerID p2p.ID, block *types.Block, height int64) {
-	if _, ok := state.queue[height]; ok {
-		panic("duplicate block enqueued by processor")
+	if item, ok := state.queue[height]; ok {
+		panic(fmt.Sprintf(
+			"duplicate block %d (%X) enqueued by processor (sent by %v; existing block %X from %v)",
+			height, block.Hash(), peerID, item.block.Hash(), item.peerID))
 	}
+
 	state.queue[height] = queueItem{block: block, peerID: peerID}
 }
 
@@ -145,16 +157,20 @@ func (state *pcState) handle(event Event) (Event, error) {
 			}
 			return noOp, nil
 		}
-		first, second := firstItem.block, secondItem.block
 
-		firstParts := first.MakePartSet(types.BlockPartSizeBytes)
-		firstPartSetHeader := firstParts.Header()
-		firstID := types.BlockID{Hash: first.Hash(), PartSetHeader: firstPartSetHeader}
+		var (
+			first, second = firstItem.block, secondItem.block
+			firstParts    = first.MakePartSet(types.BlockPartSizeBytes)
+			firstID       = types.BlockID{Hash: first.Hash(), PartSetHeader: firstParts.Header()}
+		)
 
+		// verify if +second+ last commit "confirms" +first+ block
 		err = state.context.verifyCommit(tmState.ChainID, firstID, first.Height, second.LastCommit)
 		if err != nil {
 			state.purgePeer(firstItem.peerID)
-			state.purgePeer(secondItem.peerID)
+			if firstItem.peerID != secondItem.peerID {
+				state.purgePeer(secondItem.peerID)
+			}
 			return pcBlockVerificationFailure{
 					height: first.Height, firstPeerID: firstItem.peerID, secondPeerID: secondItem.peerID},
 				nil
@@ -170,7 +186,6 @@ func (state *pcState) handle(event Event) (Event, error) {
 		state.blocksSynced++
 
 		return pcBlockProcessed{height: first.Height, peerID: firstItem.peerID}, nil
-
 	}
 
 	return noOp, nil
```

### blockchain/v2/reactor.go
```diff
@@ -187,7 +187,7 @@ type rTryPrunePeer struct {
 }
 
 func (e rTryPrunePeer) String() string {
-	return fmt.Sprintf(": %v", e.time)
+	return fmt.Sprintf("rTryPrunePeer{%v}", e.time)
 }
 
 // ticker event for scheduling block requests
@@ -197,14 +197,18 @@ type rTrySchedule struct {
 }
 
 func (e rTrySchedule) String() string {
-	return fmt.Sprintf(": %v", e.time)
+	return fmt.Sprintf("rTrySchedule{%v}", e.time)
 }
 
 // ticker for block processing
 type rProcessBlock struct {
 	priorityNormal
 }
 
+func (e rProcessBlock) String() string {
+	return "rProcessBlock"
+}
+
 // reactor generated events based on blockchain related messages from peers:
 // blockResponse message received from a peer
 type bcBlockResponse struct {
@@ -215,6 +219,11 @@ type bcBlockResponse struct {
 	block  *types.Block
 }
 
+func (resp bcBlockResponse) String() string {
+	return fmt.Sprintf("bcBlockResponse{%d#%X (size: %d bytes) from %v at %v}",
+		resp.block.Height, resp.block.Hash(), resp.size, resp.peerID, resp.time)
+}
+
 // blockNoResponse message received from a peer
 type bcNoBlockResponse struct {
 	priorityNormal
@@ -223,6 +232,11 @@ type bcNoBlockResponse struct {
 	height int64
 }
 
+func (resp bcNoBlockResponse) String() string {
+	return fmt.Sprintf("bcNoBlockResponse{%v has no block at height %d at %v}",
+		resp.peerID, resp.height, resp.time)
+}
+
 // statusResponse message received from a peer
 type bcStatusResponse struct {
 	priorityNormal
@@ -232,25 +246,42 @@ type bcStatusResponse struct {
 	height int64
 }
 
+func (resp bcStatusResponse) String() string {
+	return fmt.Sprintf("bcStatusResponse{%v is at height %d (base: %d) at %v}",
+		resp.peerID, resp.height, resp.base, resp.time)
+}
+
 // new peer is connected
 type bcAddNewPeer struct {
 	priorityNormal
 	peerID p2p.ID
 }
 
+func (resp bcAddNewPeer) String() string {
+	return fmt.Sprintf("bcAddNewPeer{%v}", resp.peerID)
+}
+
 // existing peer is removed
 type bcRemovePeer struct {
 	priorityHigh
 	peerID p2p.ID
 	reason interface{}
 }
 
+func (resp bcRemovePeer) String() string {
+	return fmt.Sprintf("bcRemovePeer{%v due to %v}", resp.peerID, resp.reason)
+}
+
 // resets the scheduler and processor state, e.g. following a switch from state syncing
 type bcResetState struct {
 	priorityHigh
 	state state.State
 }
 
+func (e bcResetState) String() string {
+	return fmt.Sprintf("bcResetState{%v}", e.state)
+}
+
 // Takes the channel as a parameter to avoid race conditions on r.events.
 func (r *BlockchainReactor) demux(events <-chan Event) {
 	var lastRate = 0.0
```

### blockchain/v2/routine.go
```diff
@@ -2,6 +2,7 @@ package v2
 
 import (
 	"fmt"
+	"strings"
 	"sync/atomic"
 
 	"github.com/Workiva/go-datastructures/queue"
@@ -11,6 +12,8 @@ import (
 
 type handleFunc = func(event Event) (Event, error)
 
+const historySize = 25
+
 // Routine is a structure that models a finite state machine as serialized
 // stream of events processed by a handle function. This Routine structure
 // handles the concurrency and messaging guarantees. Events are sent via
@@ -21,6 +24,7 @@ type Routine struct {
 	name    string
 	handle  handleFunc
 	queue   *queue.PriorityQueue
+	history []Event
 	out     chan Event
 	fin     chan error
 	rdy     chan struct{}
@@ -34,6 +38,7 @@ func newRoutine(name string, handleFunc handleFunc, bufferSize int) *Routine {
 		name:    name,
 		handle:  handleFunc,
 		queue:   queue.NewPriorityQueue(bufferSize, true),
+		history: make([]Event, 0, historySize),
 		out:     make(chan Event, bufferSize),
 		rdy:     make(chan struct{}, 1),
 		fin:     make(chan error, 1),
@@ -53,13 +58,24 @@ func (rt *Routine) setMetrics(metrics *Metrics) {
 }
 
 func (rt *Routine) start() {
-	rt.logger.Info(fmt.Sprintf("%s: run\n", rt.name))
+	rt.logger.Info(fmt.Sprintf("%s: run", rt.name))
 	running := atomic.CompareAndSwapUint32(rt.running, uint32(0), uint32(1))
 	if !running {
 		panic(fmt.Sprintf("%s is already running", rt.name))
 	}
 	close(rt.rdy)
 	defer func() {
+		if r := recover(); r != nil {
+			var (
+				b strings.Builder
+				j int
+			)
+			for i := len(rt.history) - 1; i >= 0; i-- {
+				fmt.Fprintf(&b, "%d: %+v\n", j, rt.history[i])
+				j++
+			}
+			panic(fmt.Sprintf("%v\nlast events:\n%v", r, b.String()))
+		}
 		stopped := atomic.CompareAndSwapUint32(rt.running, uint32(1), uint32(0))
 		if !stopped {
 			panic(fmt.Sprintf("%s is failed to stop", rt.name))
@@ -82,7 +98,19 @@ func (rt *Routine) start() {
 			return
 		}
 		rt.metrics.EventsOut.With("routine", rt.name).Add(1)
-		rt.logger.Debug(fmt.Sprintf("%s: produced %T %+v\n", rt.name, oEvent, oEvent))
+		rt.logger.Debug(fmt.Sprintf("%s: produced %T %+v", rt.name, oEvent, oEvent))
+
+		// Skip rTrySchedule and rProcessBlock events as they clutter the history
+		// due to their frequency.
+		switch events[0].(type) {
+		case rTrySchedule:
+		case rProcessBlock:
+		default:
+			rt.history = append(rt.history, events[0].(Event))
+			if len(rt.history) > historySize {
+				rt.history = rt.history[1:]
+			}
+		}
 
 		rt.out <- oEvent
 	}
@@ -97,7 +125,7 @@ func (rt *Routine) send(event Event) bool {
 	err := rt.queue.Put(event)
 	if err != nil {
 		rt.metrics.EventsShed.With("routine", rt.name).Add(1)
-		rt.logger.Info(fmt.Sprintf("%s: send failed, queue was full/stopped \n", rt.name))
+		rt.logger.Error(fmt.Sprintf("%s: send failed, queue was full/stopped", rt.name))
 		return false
 	}
 
@@ -122,7 +150,7 @@ func (rt *Routine) stop() {
 		return
 	}
 
-	rt.logger.Info(fmt.Sprintf("%s: stop\n", rt.name))
+	rt.logger.Info(fmt.Sprintf("%s: stop", rt.name))
 	rt.queue.Dispose() // this should block until all queue items are free?
 }
 
```

### blockchain/v2/scheduler.go
```diff
@@ -2,6 +2,7 @@ package v2
 
 import (
 	"bytes"
+	"errors"
 	"fmt"
 	"math"
 	"sort"
@@ -18,20 +19,32 @@ type scFinishedEv struct {
 	reason string
 }
 
+func (e scFinishedEv) String() string {
+	return fmt.Sprintf("scFinishedEv{%v}", e.reason)
+}
+
 // send a blockRequest message
 type scBlockRequest struct {
 	priorityNormal
 	peerID p2p.ID
 	height int64
 }
 
+func (e scBlockRequest) String() string {
+	return fmt.Sprintf("scBlockRequest{%d from %v}", e.height, e.peerID)
+}
+
 // a block has been received and validated by the scheduler
 type scBlockReceived struct {
 	priorityNormal
 	peerID p2p.ID
 	block  *types.Block
 }
 
+func (e scBlockReceived) String() string {
+	return fmt.Sprintf("scBlockReceived{%d#%X from %v}", e.block.Height, e.block.Hash(), e.peerID)
+}
+
 // scheduler detected a peer error
 type scPeerError struct {
 	priorityHigh
@@ -40,7 +53,7 @@ type scPeerError struct {
 }
 
 func (e scPeerError) String() string {
-	return fmt.Sprintf("scPeerError - peerID %s, err %s", e.peerID, e.reason)
+	return fmt.Sprintf("scPeerError{%v errored with %v}", e.peerID, e.reason)
 }
 
 // scheduler removed a set of peers (timed out or slow peer)
@@ -49,13 +62,21 @@ type scPeersPruned struct {
 	peers []p2p.ID
 }
 
+func (e scPeersPruned) String() string {
+	return fmt.Sprintf("scPeersPruned{%v}", e.peers)
+}
+
 // XXX: make this fatal?
 // scheduler encountered a fatal error
 type scSchedulerFail struct {
 	priorityHigh
 	reason error
 }
 
+func (e scSchedulerFail) String() string {
+	return fmt.Sprintf("scSchedulerFail{%v}", e.reason)
+}
+
 type blockState int
 
 const (
@@ -295,6 +316,9 @@ func (sc *scheduler) setPeerRange(peerID p2p.ID, base int64, height int64) error
 	}
 
 	if base > height {
+		if err := sc.removePeer(peerID); err != nil {
+			return err
+		}
 		return fmt.Errorf("cannot set peer base higher than its height")
 	}
 
@@ -418,7 +442,7 @@ func (sc *scheduler) markProcessed(height int64) error {
 		return fmt.Errorf("cannot mark height %d received from block state %s", height, state)
 	}
 
-	sc.height++
+	sc.height = height + 1
 	delete(sc.receivedBlocks, height)
 	delete(sc.blockStates, height)
 	sc.addNewBlocks()
@@ -532,14 +556,12 @@ func (sc *scheduler) handleBlockResponse(event bcBlockResponse) (Event, error) {
 }
 
 func (sc *scheduler) handleNoBlockResponse(event bcNoBlockResponse) (Event, error) {
-	if len(sc.peers) == 0 {
-		return noOp, nil
-	}
-
+	// No such peer or peer was removed.
 	peer, ok := sc.peers[event.peerID]
 	if !ok || peer.state == peerStateRemoved {
 		return noOp, nil
 	}
+
 	// The peer may have been just removed due to errors, low speed or timeouts.
 	_ = sc.removePeer(event.peerID)
 
@@ -550,8 +572,9 @@ func (sc *scheduler) handleNoBlockResponse(event bcNoBlockResponse) (Event, erro
 
 func (sc *scheduler) handleBlockProcessed(event pcBlockProcessed) (Event, error) {
 	if event.height != sc.height {
-		panic(fmt.Sprintf("processed height %d but expected height %d", event.height, sc.height))
+		panic(fmt.Sprintf("processed height %d, but expected height %d", event.height, sc.height))
 	}
+
 	err := sc.markProcessed(event.height)
 	if err != nil {
 		// It is possible that a peer error or timeout is handled after the processor
@@ -601,11 +624,13 @@ func (sc *scheduler) handleRemovePeer(event bcRemovePeer) (Event, error) {
 	if sc.allBlocksProcessed() {
 		return scFinishedEv{reason: "removed peer"}, nil
 	}
-	return noOp, nil
+
+	// Return scPeerError so the peer (and all associated blocks) is removed from
+	// the processor.
+	return scPeerError{peerID: event.peerID, reason: errors.New("peer was stopped")}, nil
 }
 
 func (sc *scheduler) handleTryPrunePeer(event rTryPrunePeer) (Event, error) {
-
 	// Check behavior of peer responsible to deliver block at sc.height.
 	timeHeightAsked, ok := sc.pendingTime[sc.height]
 	if ok && time.Since(timeHeightAsked) > sc.peerTimeout {
```

### blockchain/v2/scheduler_test.go
```diff
@@ -586,8 +586,7 @@ func TestScSetPeerRange(t *testing.T) {
 				allB:  []int64{1, 2, 3, 4}},
 			args: args{peerID: "P1", base: 6, height: 5},
 			wantFields: scTestParams{
-				peers: map[string]*scPeer{"P1": {height: 4, state: peerStateReady}},
-				allB:  []int64{1, 2, 3, 4}},
+				peers: map[string]*scPeer{"P1": {height: 4, state: peerStateRemoved}}},
 			wantErr: true,
 		},
 		{
```
