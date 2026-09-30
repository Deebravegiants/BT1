# [?] blockchain/v2: fix panic: processed height X+1 but expected height X (#5530)

## Summary
Severity: Unknown
Chain: Cosmos
Component: cometbft/cometbft
Published: 2020-10-20
Source: https://github.com/cometbft/cometbft/commit/020edbc11d29bb68dcc090a82a210980121fb90d
Type: security-commit

## Details
blockchain/v2: fix panic: processed height X+1 but expected height X (#5530)

Before: scheduler receives psBlockProcessed event, but does not mark block as processed because peer timed out (or was removed for other reasons) and all associated blocks were rescheduled.

After: scheduler receives psBlockProcessed event and marks block as processed in any case (even if peer who provided this block errors).

Closes #5387

## Patch
### CHANGELOG_PENDING.md
```diff
@@ -28,3 +28,5 @@ Friendly reminder, we have a [bug bounty program](https://hackerone.com/tendermi
 
 - [blockchain/v2] \#5499 Fix "duplicate block enqueued by processor" panic (@melekes)
 - [abci/grpc] \#5520 Return async responses in order, to avoid mempool panics. (@erikgrinaker)
+
+- [blockchain/v2] \#5530 Fix "processed height 4541 but expected height 4540" panic (@melekes)
```

### blockchain/v2/scheduler.go
```diff
@@ -436,17 +436,17 @@ func (sc *scheduler) markPending(peerID p2p.ID, height int64, time time.Time) er
 }
 
 func (sc *scheduler) markProcessed(height int64) error {
+	// It is possible that a peer error or timeout is handled after the processor
+	// has processed the block but before the scheduler received this event, so
+	// when pcBlockProcessed event is received, the block had been requested
+	// again => don't check the block state.
 	sc.lastAdvance = time.Now()
-	state := sc.getStateAtHeight(height)
-	if state != blockStateReceived {
-		return fmt.Errorf("cannot mark height %d received from block state %s", height, state)
-	}
-
 	sc.height = height + 1
+	delete(sc.pendingBlocks, height)
+	delete(sc.pendingTime, height)
 	delete(sc.receivedBlocks, height)
 	delete(sc.blockStates, height)
 	sc.addNewBlocks()
-
 	return nil
 }
 
@@ -577,9 +577,6 @@ func (sc *scheduler) handleBlockProcessed(event pcBlockProcessed) (Event, error)
 
 	err := sc.markProcessed(event.height)
 	if err != nil {
-		// It is possible that a peer error or timeout is handled after the processor
-		// has processed the block but before the scheduler received this event,
-		// so when pcBlockProcessed event is received the block had been requested again.
 		return scSchedulerFail{reason: err}, nil
 	}
 
```

### blockchain/v2/scheduler_test.go
```diff
@@ -992,19 +992,20 @@ func TestScMarkProcessed(t *testing.T) {
 		{
 			name: "processed an unreceived block",
 			fields: scTestParams{
-				peers:       map[string]*scPeer{"P1": {height: 2, state: peerStateReady}},
-				allB:        []int64{1, 2},
-				pending:     map[int64]p2p.ID{2: "P1"},
-				pendingTime: map[int64]time.Time{2: now},
-				received:    map[int64]p2p.ID{1: "P1"}},
+				height:        2,
+				peers:         map[string]*scPeer{"P1": {height: 4, state: peerStateReady}},
+				allB:          []int64{2},
+				pending:       map[int64]p2p.ID{2: "P1"},
+				pendingTime:   map[int64]time.Time{2: now},
+				targetPending: 1,
+			},
 			args: args{height: 2},
 			wantFields: scTestParams{
-				peers:       map[string]*scPeer{"P1": {height: 2, state: peerStateReady}},
-				allB:        []int64{1, 2},
-				pending:     map[int64]p2p.ID{2: "P1"},
-				pendingTime: map[int64]time.Time{2: now},
-				received:    map[int64]p2p.ID{1: "P1"}},
-			wantErr: true,
+				height:        3,
+				peers:         map[string]*scPeer{"P1": {height: 4, state: peerStateReady}},
+				allB:          []int64{3},
+				targetPending: 1,
+			},
 		},
 		{
 			name: "mark processed success",
@@ -1571,7 +1572,7 @@ func TestScHandleBlockProcessed(t *testing.T) {
 			name:      "empty scheduler",
 			fields:    scTestParams{height: 6},
 			args:      args{event: processed6FromP1},
-			wantEvent: scSchedulerFail{reason: fmt.Errorf("some error")},
+			wantEvent: noOpEvent{},
 		},
 		{
 			name: "processed block we don't have",
@@ -1583,7 +1584,7 @@ func TestScHandleBlockProcessed(t *testing.T) {
 				pendingTime: map[int64]time.Time{6: now},
 			},
 			args:      args{event: processed6FromP1},
-			wantEvent: scSchedulerFail{reason: fmt.Errorf("some error")},
+			wantEvent: noOpEvent{},
 		},
 		{
 			name: "processed block ok, we processed all blocks",
```
