# [?] fix(batch-proposer): potential panic risk (#1311)

## Summary
Severity: Unknown
Chain: Scroll
Component: scroll-tech/scroll
Published: 2024-04-30
Source: https://github.com/scroll-tech/scroll/commit/34ad8ca7723085fa8f969131b251c184ca62254b
Type: security-commit

## Details
fix(batch-proposer): potential panic risk (#1311)

## Patch
### common/version/version.go
```diff
@@ -5,7 +5,7 @@ import (
 	"runtime/debug"
 )
 
-var tag = "v4.4.2"
+var tag = "v4.4.3"
 
 var commit = func() string {
 	if info, ok := debug.ReadBuildInfo(); ok {
```

### rollup/internal/controller/watcher/batch_proposer.go
```diff
@@ -133,15 +133,13 @@ func (p *BatchProposer) TryProposeBatch() {
 
 func (p *BatchProposer) updateDBBatchInfo(batch *encoding.Batch, codecVersion encoding.CodecVersion) error {
 	err := p.db.Transaction(func(dbTX *gorm.DB) error {
-		batch, dbErr := p.batchOrm.InsertBatch(p.ctx, batch, codecVersion, dbTX)
+		dbBatch, dbErr := p.batchOrm.InsertBatch(p.ctx, batch, codecVersion, dbTX)
 		if dbErr != nil {
-			log.Warn("BatchProposer.updateBatchInfoInDB insert batch failure",
-				"start chunk index", batch.StartChunkIndex, "end chunk index", batch.EndChunkIndex, "error", dbErr)
+			log.Warn("BatchProposer.updateBatchInfoInDB insert batch failure", "index", batch.Index, "parent hash", batch.ParentBatchHash.Hex(), "error", dbErr)
 			return dbErr
 		}
-		dbErr = p.chunkOrm.UpdateBatchHashInRange(p.ctx, batch.StartChunkIndex, batch.EndChunkIndex, batch.Hash, dbTX)
-		if dbErr != nil {
-			log.Warn("BatchProposer.UpdateBatchHashInRange update the chunk's batch hash failure", "hash", batch.Hash, "error", dbErr)
+		if dbErr = p.chunkOrm.UpdateBatchHashInRange(p.ctx, dbBatch.StartChunkIndex, dbBatch.EndChunkIndex, dbBatch.Hash, dbTX); dbErr != nil {
+			log.Warn("BatchProposer.UpdateBatchHashInRange update the chunk's batch hash failure", "hash", dbBatch.Hash, "error", dbErr)
 			return dbErr
 		}
 		return nil
```
