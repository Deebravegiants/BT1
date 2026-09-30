# [?] avoid duplicate pending receipts to protect memory overflow

## Summary
Severity: Unknown
Chain: Harmony
Component: harmony-one/harmony
Published: 2019-09-25
Source: https://github.com/harmony-one/harmony/commit/6914ea90225b0e2295c1daa851d94618a363ee91
Type: security-commit

## Details
avoid duplicate pending receipts to protect memory overflow

## Patch
### node/node.go
```diff
@@ -99,7 +99,7 @@ type Node struct {
 	pendingCrossLinks     []*block.Header
 	pendingClMutex        sync.Mutex
 
-	pendingCXReceipts []*types.CXReceiptsProof // All the receipts received but not yet processed for Consensus
+	pendingCXReceipts map[uint64]*types.CXReceiptsProof // All the receipts received but not yet processed for Consensus
 	pendingCXMutex    sync.Mutex
 
 	// Shard databases
@@ -294,9 +294,14 @@ func (node *Node) AddPendingTransaction(newTx *types.Transaction) {
 // AddPendingReceipts adds one receipt message to pending list.
 func (node *Node) AddPendingReceipts(receipts *types.CXReceiptsProof) {
 	node.pendingCXMutex.Lock()
-	node.pendingCXReceipts = append(node.pendingCXReceipts, receipts)
-	node.pendingCXMutex.Unlock()
-	utils.Logger().Error().Int("totalPendingReceipts", len(node.pendingCXReceipts)).Msg("Got ONE more receipt message")
+	defer node.pendingCXMutex.Unlock()
+	blockNum := receipts.Header.Number().Uint64()
+	if _, ok := node.pendingCXReceipts[blockNum]; ok {
+		utils.Logger().Info().Int("totalPendingReceipts", len(node.pendingCXReceipts)).Msg("Already Got Same Receipt message")
+		return
+	}
+	node.pendingCXReceipts[blockNum] = receipts
+	utils.Logger().Info().Int("totalPendingReceipts", len(node.pendingCXReceipts)).Msg("Got ONE more receipt message")
 }
 
 // Take out a subset of valid transactions from the pending transaction list
@@ -404,6 +409,8 @@ func New(host p2p.Host, consensusObj *consensus.Consensus, chainDBFactory shardc
 			node.BeaconWorker = worker.New(node.Beaconchain().Config(), beaconChain, chain.Engine)
 		}
 
+		node.pendingCXReceipts = make(map[uint64]*types.CXReceiptsProof)
+
 		node.Consensus.VerifiedNewBlock = make(chan *types.Block)
 		// the sequence number is the next block number to be added in consensus protocol, which is always one more than current chain header block
 		node.Consensus.SetBlockNum(blockchain.CurrentBlock().NumberU64() + 1)
```

### node/node_newblock.go
```diff
@@ -202,9 +202,16 @@ func (node *Node) proposeReceiptsProof() []*types.CXReceiptsProof {
 	pendingReceiptsList := []*types.CXReceiptsProof{}
 
 	node.pendingCXMutex.Lock()
+	defer node.pendingCXMutex.Unlock()
 
-	sort.Slice(node.pendingCXReceipts, func(i, j int) bool {
-		return node.pendingCXReceipts[i].MerkleProof.ShardID < node.pendingCXReceipts[j].MerkleProof.ShardID || (node.pendingCXReceipts[i].MerkleProof.ShardID == node.pendingCXReceipts[j].MerkleProof.ShardID && node.pendingCXReceipts[i].MerkleProof.BlockNum.Cmp(node.pendingCXReceipts[j].MerkleProof.BlockNum) < 0)
+	// not necessary to sort the list, but we just prefer to process the list ordered by shard and blocknum
+	pendingCXReceipts := []*types.CXReceiptsProof{}
+	for _, v := range node.pendingCXReceipts {
+		pendingCXReceipts = append(pendingCXReceipts, v)
+	}
+
+	sort.Slice(pendingCXReceipts, func(i, j int) bool {
+		return pendingCXReceipts[i].MerkleProof.ShardID < pendingCXReceipts[j].MerkleProof.ShardID || (pendingCXReceipts[i].MerkleProof.ShardID == pendingCXReceipts[j].MerkleProof.ShardID && pendingCXReceipts[i].MerkleProof.BlockNum.Cmp(pendingCXReceipts[j].MerkleProof.BlockNum) < 0)
 	})
 
 	m := make(map[common.Hash]bool)
@@ -244,8 +251,10 @@ Loop:
 		numProposed = numProposed + len(cxp.Receipts)
 	}
 
-	node.pendingCXReceipts = pendingReceiptsList
-	node.pendingCXMutex.Unlock()
+	for _, v := range pendingReceiptsList {
+		blockNum := v.Header.Number().Uint64()
+		node.pendingCXReceipts[blockNum] = v
+	}
 
 	utils.Logger().Debug().Msgf("[proposeReceiptsProof] number of validReceipts %d", len(validReceiptsList))
 	return validReceiptsList
```
