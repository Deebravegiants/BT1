# [?] Fix crashes problems and remove temp crosslinks

## Summary
Severity: Unknown
Chain: Harmony
Component: harmony-one/harmony
Published: 2019-08-23
Source: https://github.com/harmony-one/harmony/commit/6a18b0401c0ff5668c0c9b873c9c9b0a10131461
Type: security-commit

## Details
Fix crashes problems and remove temp crosslinks

## Patch
### api/service/syncing/syncing.go
```diff
@@ -31,6 +31,7 @@ const (
 	SyncingPortDifference                        = 3000
 	inSyncThreshold                              = 0    // when peerBlockHeight - myBlockHeight <= inSyncThreshold, it's ready to join consensus
 	BatchSize                             uint32 = 1000 //maximum size for one query of block hashes
+	SyncLoopFrequency                            = 1    // unit in second
 )
 
 // SyncPeerConfig is peer config to sync.
@@ -732,20 +733,24 @@ func (ss *StateSync) SyncLoop(bc *core.BlockChain, worker *worker.Worker, willJo
 	if !isBeacon {
 		ss.RegisterNodeInfo()
 	}
+	ticker := time.NewTicker(SyncLoopFrequency * time.Second)
 	for {
-		otherHeight := ss.getMaxPeerHeight()
-		currentHeight := bc.CurrentBlock().NumberU64()
-		if currentHeight >= otherHeight {
-			utils.Logger().Info().Msgf("[SYNC] Node is now IN SYNC! (ShardID: %d)", bc.ShardID())
-			break
-		}
-		startHash := bc.CurrentBlock().Hash()
-		size := uint32(otherHeight - currentHeight)
-		if size > BatchSize {
-			size = BatchSize
+		select {
+		case <-ticker.C:
+			otherHeight := ss.getMaxPeerHeight()
+			currentHeight := bc.CurrentBlock().NumberU64()
+			if currentHeight >= otherHeight {
+				utils.Logger().Info().Msgf("[SYNC] Node is now IN SYNC! (ShardID: %d)", bc.ShardID())
+				break
+			}
+			startHash := bc.CurrentBlock().Hash()
+			size := uint32(otherHeight - currentHeight)
+			if size > BatchSize {
+				size = BatchSize
+			}
+			ss.ProcessStateSync(startHash[:], size, bc, worker)
+			ss.purgeOldBlocksFromCache()
 		}
-		ss.ProcessStateSync(startHash[:], size, bc, worker)
-		ss.purgeOldBlocksFromCache()
 	}
 	ss.purgeAllBlocksFromCache()
 }
```

### core/blockchain.go
```diff
@@ -1138,6 +1138,7 @@ func (bc *BlockChain) InsertChain(chain types.Blocks) (int, error) {
 				}
 				for _, crossLink := range *crossLinks {
 					bc.WriteCrossLinks(types.CrossLinks{crossLink}, false)
+					bc.DeleteCrossLinks(types.CrossLinks{crossLink}, true)
 					bc.WriteShardLastCrossLink(crossLink.ShardID(), crossLink)
 				}
 			}
@@ -2002,6 +2003,17 @@ func (bc *BlockChain) WriteCrossLinks(cls []types.CrossLink, temp bool) error {
 	return err
 }
 
+// DeleteCrossLinks removes the hashes of crosslinks by shardID and blockNum combination key
+// temp=true is to write the just received cross link that's not committed into blockchain with consensus
+func (bc *BlockChain) DeleteCrossLinks(cls []types.CrossLink, temp bool) error {
+	var err error
+	for i := 0; i < len(cls); i++ {
+		cl := cls[i]
+		err = rawdb.DeleteCrossLinkShardBlock(bc.db, cl.ShardID(), cl.BlockNum().Uint64(), temp)
+	}
+	return err
+}
+
 // ReadCrossLink retrieves crosslink given shardID and blockNum.
 // temp=true is to retrieve the just received cross link that's not committed into blockchain with consensus
 func (bc *BlockChain) ReadCrossLink(shardID uint32, blockNum uint64, temp bool) (*types.CrossLink, error) {
```

### core/rawdb/accessors_chain.go
```diff
@@ -519,6 +519,11 @@ func WriteCrossLinkShardBlock(db DatabaseWriter, shardID uint32, blockNum uint64
 	return db.Put(crosslinkKey(shardID, blockNum, temp), data)
 }
 
+// DeleteCrossLinkShardBlock deletes the blockHash given shardID and blockNum
+func DeleteCrossLinkShardBlock(db DatabaseDeleter, shardID uint32, blockNum uint64, temp bool) error {
+	return db.Delete(crosslinkKey(shardID, blockNum, temp))
+}
+
 // ReadShardLastCrossLink read the last cross link of a shard
 func ReadShardLastCrossLink(db DatabaseReader, shardID uint32) ([]byte, error) {
 	return db.Get(shardLastCrosslinkKey(shardID))
```

### node/node_cross_shard.go
```diff
@@ -119,7 +119,7 @@ func (node *Node) compareCrosslinkWithReceipts(cxp *types.CXReceiptsProof) error
 	if shardID == 0 {
 		block := beaconChain.GetBlockByNumber(blockNum)
 		if block == nil {
-			return ctxerror.New("[compareCrosslinkWithReceipts] Cannot get beaconchain heaer", "blockNum", blockNum, "shardID", shardID)
+			return ctxerror.New("[compareCrosslinkWithReceipts] Cannot get beaconchain header", "blockNum", blockNum, "shardID", shardID)
 		}
 		hash = block.Hash()
 		outgoingReceiptHash = block.OutgoingReceiptHash()
@@ -224,6 +224,12 @@ func (node *Node) ProposeCrossLinkDataForBeaconchain() (types.CrossLinks, error)
 			}
 
 			if link.BlockNum().Uint64() > firstCrossLinkBlock {
+				if lastLink == nil {
+					utils.Logger().Debug().
+						Err(err).
+						Msgf("[CrossLink] Haven't received the first cross link %d", link.BlockNum().Uint64())
+					break
+				}
 				err := node.VerifyCrosslinkHeader(lastLink.Header(), link.Header())
 				if err != nil {
 					utils.Logger().Debug().
@@ -271,8 +277,3 @@ func (node *Node) ProcessReceiptMessage(msgPayload []byte) {
 
 	node.AddPendingReceipts(&cxp)
 }
-
-// ProcessCrossShardTx verify and process cross shard transaction on destination shard
-func (node *Node) ProcessCrossShardTx(blocks []*types.Block) {
-	// TODO: add logic
-}
```

### node/node_handler.go
```diff
@@ -173,8 +173,6 @@ func (node *Node) messageHandler(content []byte, sender libp2p_peer.ID) {
 					role := node.NodeConfig.Role()
 					if role == nodeconfig.Validator {
 
-						go node.ProcessCrossShardTx(blocks)
-
 						for _, block := range blocks {
 							if block.ShardID() == 0 {
 								utils.Logger().Info().
@@ -281,8 +279,8 @@ func (node *Node) transactionMessageHandler(msgPayload []byte) {
 // NOTE: For now, just send to the client (basically not broadcasting)
 // TODO (lc): broadcast the new blocks to new nodes doing state sync
 func (node *Node) BroadcastNewBlock(newBlock *types.Block) {
-	utils.Logger().Info().Msgf("broadcasting new block %d", newBlock.NumberU64())
 	groups := []p2p.GroupID{node.NodeConfig.GetClientGroupID()}
+	utils.Logger().Info().Msgf("broadcasting new block %d, group %s", newBlock.NumberU64(), groups[0])
 	msg := host.ConstructP2pMessage(byte(0), proto_node.ConstructBlocksSyncMessage([]*types.Block{newBlock}))
 	if err := node.host.SendMessageToGroups(groups, msg); err != nil {
 		utils.Logger().Warn().Err(err).Msg("cannot broadcast new block")
```

### node/node_newblock.go
```diff
@@ -95,8 +95,8 @@ func (node *Node) WaitForConsensusReadyv2(readySignal chan struct{}, stopChan ch
 					if node.NodeConfig.ShardID == 0 {
 						crossLinksToPropose, err := node.ProposeCrossLinkDataForBeaconchain()
 						if err == nil {
-							data, err := rlp.EncodeToBytes(crossLinksToPropose)
-							if err == nil {
+							data, localErr := rlp.EncodeToBytes(crossLinksToPropose)
+							if localErr == nil {
 								newBlock, err = node.Worker.CommitWithCrossLinks(sig, mask, viewID, coinbase, data)
 								utils.Logger().Debug().
 									Uint64("blockNum", newBlock.NumberU64()).
@@ -138,7 +138,7 @@ func (node *Node) WaitForConsensusReadyv2(readySignal chan struct{}, stopChan ch
 }
 
 func (node *Node) proposeShardStateWithoutBeaconSync(block *types.Block) error {
-	if !core.IsEpochLastBlock(block) {
+	if block == nil || !core.IsEpochLastBlock(block) {
 		return nil
 	}
 	nextEpoch := new(big.Int).Add(block.Header().Epoch, common.Big1)
```

### node/worker/worker.go
```diff
@@ -65,7 +65,7 @@ func (w *Worker) SelectTransactionsForNewBlock(txs types.Transactions, maxNumTxs
 			if err != nil {
 				w.current.state.RevertToSnapshot(snap)
 				invalid = append(invalid, tx)
-				utils.GetLogger().Debug("Invalid transaction", "Error", err)
+				utils.Logger().Debug().Err(err).Msg("Invalid transaction")
 			} else {
 				selected = append(selected, tx)
 			}
```
