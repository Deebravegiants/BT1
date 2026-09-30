# [?] fix sync race condition

## Summary
Severity: Unknown
Chain: Harmony
Component: harmony-one/harmony
Published: 2020-11-04
Source: https://github.com/harmony-one/harmony/commit/0e95cb634bad2b599235975484e53fc48b2bf0bc
Type: security-commit

## Details
fix sync race condition

## Patch
### api/service/syncing/syncing.go
```diff
@@ -33,6 +33,7 @@ const (
 	RegistrationNumber              = 3
 	SyncingPortDifference           = 3000
 	inSyncThreshold                 = 0    // when peerBlockHeight - myBlockHeight <= inSyncThreshold, it's ready to join consensus
+	syncStatusCheckCount            = 3    // check this many times before confirming it's out of sync
 	SyncLoopBatchSize        uint32 = 1000 // maximum size for one query of block hashes
 	verifyHeaderBatchSize    uint64 = 100  // block chain header verification batch size
 	SyncLoopFrequency               = 1    // unit in second
@@ -920,6 +921,7 @@ func (ss *StateSync) SyncLoop(bc *core.BlockChain, worker *worker.Worker, isBeac
 	// remove SyncLoopFrequency
 	ticker := time.NewTicker(SyncLoopFrequency * time.Second)
 	defer ticker.Stop()
+	outOfSyncCount := 1
 	for range ticker.C {
 		otherHeight := ss.getMaxPeerHeight(isBeacon)
 		currentHeight := bc.CurrentBlock().NumberU64()
@@ -929,6 +931,10 @@ func (ss *StateSync) SyncLoop(bc *core.BlockChain, worker *worker.Worker, isBeac
 					isBeacon, bc.ShardID(), otherHeight, currentHeight)
 			break
 		}
+		if outOfSyncCount < syncStatusCheckCount {
+			outOfSyncCount++
+			continue
+		}
 		utils.Logger().Info().
 			Msgf("[SYNC] Node is OUT OF SYNC (isBeacon: %t, ShardID: %d, otherHeight: %d, currentHeight: %d)",
 				isBeacon, bc.ShardID(), otherHeight, currentHeight)
```

### consensus/consensus_v2.go
```diff
@@ -289,10 +289,12 @@ func (consensus *Consensus) Start(
 				}
 			case <-consensus.syncReadyChan:
 				consensus.getLogger().Info().Msg("[ConsensusMainLoop] syncReadyChan")
+				consensus.mutex.Lock()
 				consensus.SetBlockNum(consensus.Blockchain.CurrentHeader().Number().Uint64() + 1)
 				consensus.SetViewIDs(consensus.Blockchain.CurrentHeader().ViewID().Uint64() + 1)
 				mode := consensus.UpdateConsensusInformation()
 				consensus.current.SetMode(mode)
+				consensus.mutex.Unlock()
 				consensus.getLogger().Info().Str("Mode", mode.String()).Msg("Node is IN SYNC")
 
 			case <-consensus.syncNotReadyChan:
```

### consensus/validator.go
```diff
@@ -229,14 +229,10 @@ func (consensus *Consensus) onCommitted(msg *msg_pb.Message) {
 		Uint64("MsgViewID", recvMsg.ViewID).
 		Msg("[OnCommitted] Received committed message")
 
-	// It's ok to receive committed message for last block due to pipelining.
-	// The committed message for last block could include more signatures now.
-	if recvMsg.BlockNum < consensus.blockNum-1 {
-		consensus.getLogger().Debug().
-			Uint64("MsgBlockNum", recvMsg.BlockNum).
-			Msg("Wrong BlockNum Received, ignoring!")
+	if !consensus.isRightBlockNumCheck(recvMsg) {
 		return
 	}
+
 	if recvMsg.BlockNum > consensus.blockNum {
 		consensus.getLogger().Info().Msg("[OnCommitted] low consensus block number. Spin up state sync")
 		consensus.spinUpStateSync()
```

### node/node_newblock.go
```diff
@@ -60,10 +60,12 @@ func (node *Node) WaitForConsensusReadyV2(readySignal chan consensus.ProposalTyp
 						}
 						select {
 						case commitSigs := <-commitSigsChan:
+							utils.Logger().Info().Msg("[ProposeNewBlock] received commit sigs asynchronously")
 							if len(commitSigs) > bls.BLSSignatureSizeInBytes {
 								newCommitSigsChan <- commitSigs
 							}
 						case <-time.After(waitTime):
+							utils.Logger().Info().Msg("[ProposeNewBlock] timeout waiting for commit sigs, reading directly from DB")
 							sigs, err := node.Consensus.BlockCommitSigs(node.Blockchain().CurrentBlock().NumberU64())
 
 							if err != nil {
```
