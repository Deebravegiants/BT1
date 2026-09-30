# [?] fix(verifier): nil panic due to batch write (#911)

## Summary
Severity: Unknown
Chain: Scroll
Component: scroll-tech/go-ethereum
Published: 2024-07-19
Source: https://github.com/scroll-tech/go-ethereum/commit/de0385e7d25c21496f3eb2a63d14d761f896ab4d
Type: security-commit

## Details
fix(verifier): nil panic due to batch write (#911)

## Patch
### go.mod
```diff
@@ -50,7 +50,7 @@ require (
 	github.com/prometheus/tsdb v0.7.1
 	github.com/rjeczalik/notify v0.9.1
 	github.com/rs/cors v1.7.0
-	github.com/scroll-tech/da-codec v0.1.1-0.20240716101216-c55ed9455cf4
+	github.com/scroll-tech/da-codec v0.1.1-0.20240718144756-1875fd490923
 	github.com/scroll-tech/zktrie v0.8.4
 	github.com/shirou/gopsutil v3.21.11+incompatible
 	github.com/status-im/keycard-go v0.0.0-20190316090335-8537d3370df4
```

### go.sum
```diff
@@ -392,8 +392,8 @@ github.com/rogpeppe/go-internal v1.10.0/go.mod h1:UQnix2H7Ngw/k4C5ijL5+65zddjncj
 github.com/rs/cors v1.7.0 h1:+88SsELBHx5r+hZ8TCkggzSstaWNbDvThkVK8H6f9ik=
 github.com/rs/cors v1.7.0/go.mod h1:gFx+x8UowdsKA9AchylcLynDq+nNFfI8FkUZdN/jGCU=
 github.com/russross/blackfriday/v2 v2.0.1/go.mod h1:+Rmxgy9KzJVeS9/2gXHxylqXiyQDYRxCVz55jmeOWTM=
-github.com/scroll-tech/da-codec v0.1.1-0.20240716101216-c55ed9455cf4 h1:40Lby3huKNFZ2EXzxqVpADB+caepDRrNRoUgTsCKN88=
-github.com/scroll-tech/da-codec v0.1.1-0.20240716101216-c55ed9455cf4/go.mod h1:D6XEESeNVJkQJlv3eK+FyR+ufPkgVQbJzERylQi53Bs=
+github.com/scroll-tech/da-codec v0.1.1-0.20240718144756-1875fd490923 h1:A1ItzpnFDCHMh4g6cpeBZf7/fPf2lfwHbhjr/FSpk2w=
+github.com/scroll-tech/da-codec v0.1.1-0.20240718144756-1875fd490923/go.mod h1:D6XEESeNVJkQJlv3eK+FyR+ufPkgVQbJzERylQi53Bs=
 github.com/scroll-tech/zktrie v0.8.4 h1:UagmnZ4Z3ITCk+aUq9NQZJNAwnWl4gSxsLb2Nl7IgRE=
 github.com/scroll-tech/zktrie v0.8.4/go.mod h1:XvNo7vAk8yxNyTjBDj5WIiFzYW4bx/gJ78+NK6Zn6Uk=
 github.com/segmentio/kafka-go v0.1.0/go.mod h1:X6itGqS9L4jDletMsxZ7Dz+JFWxM6JHfPOCvTvk+EJo=
```

### params/version.go
```diff
@@ -24,7 +24,7 @@ import (
 const (
 	VersionMajor = 5         // Major version component of the current release
 	VersionMinor = 5         // Minor version component of the current release
-	VersionPatch = 13        // Patch version component of the current release
+	VersionPatch = 14        // Patch version component of the current release
 	VersionMeta  = "mainnet" // Version metadata to append to the version string
 )
 
```

### rollup/rollup_sync_service/rollup_sync_service.go
```diff
@@ -241,10 +241,15 @@ func (s *RollupSyncService) parseAndUpdateRollupEventLogs(logs []types.Log, endB
 				log.Warn("got nil when reading last finalized batch index. This should happen only once.")
 			}
 
+			parentBatchMeta := &rawdb.FinalizedBatchMeta{}
+			if startBatchIndex > 0 {
+				parentBatchMeta = rawdb.ReadFinalizedBatchMeta(s.db, startBatchIndex-1)
+			}
+
 			var highestFinalizedBlockNumber uint64
 			batchWriter := s.db.NewBatch()
 			for index := startBatchIndex; index <= batchIndex; index++ {
-				parentBatchMeta, chunks, err := s.getLocalInfoForBatch(index)
+				chunks, err := s.getLocalChunksForBatch(index)
 				if err != nil {
 					return fmt.Errorf("failed to get local node info, batch index: %v, err: %w", index, err)
 				}
@@ -256,6 +261,7 @@ func (s *RollupSyncService) parseAndUpdateRollupEventLogs(logs []types.Log, endB
 
 				rawdb.WriteFinalizedBatchMeta(batchWriter, index, finalizedBatchMeta)
 				highestFinalizedBlockNumber = endBlock
+				parentBatchMeta = finalizedBatchMeta
 
 				if index%100 == 0 {
 					log.Info("finalized batch progress", "batch index", index, "finalized l2 block height", endBlock)
@@ -283,17 +289,17 @@ func (s *RollupSyncService) parseAndUpdateRollupEventLogs(logs []types.Log, endB
 	return nil
 }
 
-func (s *RollupSyncService) getLocalInfoForBatch(batchIndex uint64) (*rawdb.FinalizedBatchMeta, []*encoding.Chunk, error) {
+func (s *RollupSyncService) getLocalChunksForBatch(batchIndex uint64) ([]*encoding.Chunk, error) {
 	chunkBlockRanges := rawdb.ReadBatchChunkRanges(s.db, batchIndex)
 	if len(chunkBlockRanges) == 0 {
-		return nil, nil, fmt.Errorf("failed to get batch chunk ranges, empty chunk block ranges")
+		return nil, fmt.Errorf("failed to get batch chunk ranges, empty chunk block ranges")
 	}
 
 	endBlockNumber := chunkBlockRanges[len(chunkBlockRanges)-1].EndBlockNumber
 	for i := 0; i < defaultMaxRetries; i++ {
 		if s.ctx.Err() != nil {
 			log.Info("Context canceled", "reason", s.ctx.Err())
-			return nil, nil, s.ctx.Err()
+			return nil, s.ctx.Err()
 		}
 
 		localSyncedBlockHeight := s.bc.CurrentBlock().Number().Uint64()
@@ -308,7 +314,7 @@ func (s *RollupSyncService) getLocalInfoForBatch(batchIndex uint64) (*rawdb.Fina
 
 	localSyncedBlockHeight := s.bc.CurrentBlock().Number().Uint64()
 	if localSyncedBlockHeight < endBlockNumber {
-		return nil, nil, fmt.Errorf("local node is not synced up to the required block height: %v, local synced block height: %v", endBlockNumber, localSyncedBlockHeight)
+		return nil, fmt.Errorf("local node is not synced up to the required block height: %v, local synced block height: %v", endBlockNumber, localSyncedBlockHeight)
 	}
 
 	chunks := make([]*encoding.Chunk, len(chunkBlockRanges))
@@ -317,12 +323,12 @@ func (s *RollupSyncService) getLocalInfoForBatch(batchIndex uint64) (*rawdb.Fina
 		for j := cr.StartBlockNumber; j <= cr.EndBlockNumber; j++ {
 			block := s.bc.GetBlockByNumber(j)
 			if block == nil {
-				return nil, nil, fmt.Errorf("failed to get block by number: %v", i)
+				return nil, fmt.Errorf("failed to get block by number: %v", i)
 			}
 			txData := encoding.TxsToTxsData(block.Transactions())
 			state, err := s.bc.StateAt(block.Root())
 			if err != nil {
-				return nil, nil, fmt.Errorf("failed to get block state, block: %v, err: %w", block.Hash().Hex(), err)
+				return nil, fmt.Errorf("failed to get block state, block: %v, err: %w", block.Hash().Hex(), err)
 			}
 			withdrawRoot := withdrawtrie.ReadWTRSlot(rcfg.L2MessageQueueAddress, state)
 			chunks[i].Blocks[j-cr.StartBlockNumber] = &encoding.Block{
@@ -333,13 +339,7 @@ func (s *RollupSyncService) getLocalInfoForBatch(batchIndex uint64) (*rawdb.Fina
 		}
 	}
 
-	// get metadata of parent batch: default to genesis batch metadata.
-	parentBatchMeta := &rawdb.FinalizedBatchMeta{}
-	if batchIndex > 0 {
-		parentBatchMeta = rawdb.ReadFinalizedBatchMeta(s.db, batchIndex-1)
-	}
-
-	return parentBatchMeta, chunks, nil
+	return chunks, nil
 }
 
 func (s *RollupSyncService) getChunkRanges(batchIndex uint64, vLog *types.Log) ([]*rawdb.ChunkBlockRange, error) {
```
