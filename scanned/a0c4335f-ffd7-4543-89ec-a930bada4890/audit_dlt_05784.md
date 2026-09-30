# [?] fix(lanes): Panic when lane is not found (#4169)

## Summary
Severity: Unknown
Chain: Cosmos
Component: cometbft/cometbft
Published: 2024-09-24
Source: https://github.com/cometbft/cometbft/commit/3329e68931bccdf2e338c8c002f3845a16a4bf8b
Type: security-commit

## Details
fix(lanes): Panic when lane is not found (#4169)

There is always at least one lane, so it should not happen that a lane
is not found. This has cost me some debugging time.

---------

Co-authored-by: Jasmina Malicevic <jasmina.dustinac@gmail.com>
Co-authored-by: mergify[bot] <37929162+mergify[bot]@users.noreply.github.com>

## Patch
### internal/consensus/replay_test.go
```diff
@@ -76,13 +76,15 @@ func startNewStateAndWaitForBlock(
 	state, _ := stateStore.LoadFromDBOrGenesisFile(consensusReplayConfig.GenesisFile())
 	privValidator, err := loadPrivValidator(consensusReplayConfig)
 	require.NoError(t, err)
+	app := kvstore.NewInMemoryApplication()
+	_, lanesInfo := fetchAppInfo(t, app)
 	cs := newStateWithConfigAndBlockStore(
 		consensusReplayConfig,
 		state,
 		privValidator,
-		kvstore.NewInMemoryApplication(),
+		app,
 		blockDB,
-		nil,
+		lanesInfo,
 	)
 	cs.SetLogger(logger)
 
@@ -184,13 +186,15 @@ LOOP:
 		require.NoError(t, err)
 		privValidator, err := loadPrivValidator(consensusReplayConfig)
 		require.NoError(t, err)
+		app := kvstore.NewInMemoryApplication()
+		_, lanesInfo := fetchAppInfo(t, app)
 		cs := newStateWithConfigAndBlockStore(
 			consensusReplayConfig,
 			state,
 			privValidator,
 			kvstore.NewInMemoryApplication(),
 			blockDB,
-			nil,
+			lanesInfo,
 		)
 		cs.SetLogger(logger)
 
```

### mempool/clist_mempool.go
```diff
@@ -291,7 +291,7 @@ func (mem *CListMempool) LaneSizes(lane LaneID) (numTxs int, bytes int64) {
 
 	txs, ok := mem.lanes[lane]
 	if !ok {
-		return 0, bytes
+		panic(ErrLaneNotFound{laneID: lane})
 	}
 	return txs.Len(), bytes
 }
@@ -424,9 +424,12 @@ func (mem *CListMempool) handleCheckTxResponse(tx types.Tx, sender p2p.ID) func(
 			return ErrInvalidTx
 		}
 
-		// If the app returned a (non-zero) lane, use it; otherwise use the default lane.
+		// If the app returned a non-empty lane, use it; otherwise use the default lane.
 		lane := mem.defaultLane
 		if res.LaneId != "" {
+			if _, ok := mem.lanes[lane]; !ok {
+				panic(ErrLaneNotFound{laneID: lane})
+			}
 			lane = LaneID(res.LaneId)
 		}
 
@@ -450,31 +453,29 @@ func (mem *CListMempool) handleCheckTxResponse(tx types.Tx, sender p2p.ID) func(
 		}
 
 		// Add tx to mempool and notify that new txs are available.
-		if mem.addTx(tx, res.GasWanted, sender, lane) {
-			mem.notifyTxsAvailable()
-
-			if mem.onNewTx != nil {
-				mem.onNewTx(tx)
-			}
+		mem.addTx(tx, res.GasWanted, sender, lane)
+		mem.notifyTxsAvailable()
 
-			mem.updateSizeMetrics(lane)
+		if mem.onNewTx != nil {
+			mem.onNewTx(tx)
 		}
 
+		mem.updateSizeMetrics(lane)
+
 		return nil
 	}
 }
 
 // Called from:
 //   - handleCheckTxResponse (lock not held) if tx is valid
-func (mem *CListMempool) addTx(tx types.Tx, gasWanted int64, sender p2p.ID, lane LaneID) bool {
+func (mem *CListMempool) addTx(tx types.Tx, gasWanted int64, sender p2p.ID, lane LaneID) {
 	mem.txsMtx.Lock()
 	defer mem.txsMtx.Unlock()
 
 	// Get lane's clist.
 	txs, ok := mem.lanes[lane]
 	if !ok {
-		mem.logger.Error("Lane does not exist, not adding TX", "tx", log.NewLazySprintf("%X", tx.Hash()), "lane", lane)
-		return false
+		panic(ErrLaneNotFound{laneID: lane})
 	}
 
 	// Increase sequence number.
@@ -514,7 +515,6 @@ func (mem *CListMempool) addTx(tx types.Tx, gasWanted int64, sender p2p.ID, lane
 		"height", mem.height.Load(),
 		"total", mem.numTxs,
 	)
-	return true
 }
 
 // RemoveTxByKey removes a transaction from the mempool by its TxKey index.
```

### mempool/errors.go
```diff
@@ -147,3 +147,11 @@ type ErrDefaultLaneNotInList struct {
 func (e ErrDefaultLaneNotInList) Error() string {
 	return fmt.Sprintf("invalid lane info: list of lanes does not contain default lane; info %v", e.Info)
 }
+
+type ErrLaneNotFound struct {
+	laneID LaneID
+}
+
+func (e ErrLaneNotFound) Error() string {
+	return fmt.Sprintf("lane %s not found", e.laneID)
+}
```
