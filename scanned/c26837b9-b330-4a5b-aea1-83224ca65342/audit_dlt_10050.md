# [?] Merge branch 'feat/supernova-async-exec' into fix-panic-outport-data-provider

## Summary
Severity: Unknown
Chain: MultiversX
Component: multiversx/mx-chain-go
Published: 2026-01-22
Source: https://github.com/multiversx/mx-chain-go/commit/c5abd001a5b74be77084c9c37e4293438dd63116
Type: security-commit

## Details
Merge branch 'feat/supernova-async-exec' into fix-panic-outport-data-provider

## Patch
### cmd/node/config/config.toml
```diff
@@ -227,6 +227,8 @@
         BatchDelaySeconds = 2
         MaxBatchSize = 100
         MaxOpenFiles = 10
+        ShardIDProviderType = "BinarySplit"
+        NumShards = 4
 
 [BootstrapStorage]
     [BootstrapStorage.Cache]
@@ -253,6 +255,8 @@
         BatchDelaySeconds = 2
         MaxBatchSize = 100
         MaxOpenFiles = 10
+        ShardIDProviderType = "BinarySplit"
+        NumShards = 4
 
 [ProofsStorage]
     [ProofsStorage.Cache]
@@ -292,6 +296,8 @@
         BatchDelaySeconds = 2
         MaxBatchSize = 30000
         MaxOpenFiles = 10
+        ShardIDProviderType = "BinarySplit"
+        NumShards = 4
 
 [UnsignedTransactionStorage]
     [UnsignedTransactionStorage.Cache]
@@ -996,6 +1002,8 @@
         BatchDelaySeconds = 2
         MaxBatchSize = 20000
         MaxOpenFiles = 10
+        ShardIDProviderType = "BinarySplit"
+        NumShards = 4
     [DbLookupExtensions.EpochByHashStorageConfig.Cache]
         Name = "DbLookupExtensions.EpochByHashStorage"
         Capacity = 20000
@@ -1006,6 +1014,8 @@
         BatchDelaySeconds = 2
         MaxBatchSize = 20000
         MaxOpenFiles = 10
+        ShardIDProviderType = "BinarySplit"
+        NumShards = 4
     [DbLookupExtensions.ResultsHashesByTxHashStorageConfig.Cache]
         Name = "DbLookupExtensions.ResultsHashesByTxHashStorage"
         Capacity = 20000
```

### common/constants.go
```diff
@@ -1034,6 +1034,9 @@ const CommitMaxTime = 3 * time.Second
 // PutInStorerMaxTime represents max time accepted for a put action, after which a warn message is displayed
 const PutInStorerMaxTime = time.Second
 
+// PutInStorerMaxTimeSupernova represents max time accepted for a put action with supernova activated, after which a warn message is displayed
+const PutInStorerMaxTimeSupernova = 600 * time.Millisecond
+
 // DefaultUnstakedEpoch represents the default epoch that is set for a validator that has not unstaked yet
 const DefaultUnstakedEpoch = math.MaxUint32
 
```

### process/block/baseProcess.go
```diff
@@ -1574,7 +1574,7 @@ func (bp *baseProcessor) prepareDataForBootStorer(args bootStorerDataArgs) {
 	}
 
 	elapsedTime := time.Since(startTime)
-	if elapsedTime >= common.PutInStorerMaxTime {
+	if elapsedTime >= bp.getPutInStorerMaxTime() {
 		log.Warn("saveDataForBootStorer", "elapsed time", elapsedTime)
 	}
 }
@@ -1773,7 +1773,7 @@ func (bp *baseProcessor) saveBody(body *block.Body, header data.HeaderHandler, h
 	bp.scheduledTxsExecutionHandler.SaveStateIfNeeded(headerHash)
 
 	elapsedTime := time.Since(startTime)
-	if elapsedTime >= common.PutInStorerMaxTime {
+	if elapsedTime >= bp.getPutInStorerMaxTime() {
 		log.Warn("saveBody", "elapsed time", elapsedTime)
 	}
 }
@@ -1894,7 +1894,7 @@ func (bp *baseProcessor) saveShardHeader(header data.HeaderHandler, headerHash [
 	bp.saveProof(headerHash, header)
 
 	elapsedTime := time.Since(startTime)
-	if elapsedTime >= common.PutInStorerMaxTime {
+	if elapsedTime >= bp.getPutInStorerMaxTime() {
 		log.Warn("saveShardHeader", "elapsed time", elapsedTime)
 	}
 }
@@ -1921,11 +1921,19 @@ func (bp *baseProcessor) saveMetaHeader(header data.HeaderHandler, headerHash []
 	bp.saveProof(headerHash, header)
 
 	elapsedTime := time.Since(startTime)
-	if elapsedTime >= common.PutInStorerMaxTime {
+	if elapsedTime >= bp.getPutInStorerMaxTime() {
 		log.Warn("saveMetaHeader", "elapsed time", elapsedTime)
 	}
 }
 
+func (bp *baseProcessor) getPutInStorerMaxTime() time.Duration {
+	if bp.enableEpochsHandler.IsFlagEnabled(common.SupernovaFlag) {
+		return common.PutInStorerMaxTimeSupernova
+	}
+
+	return common.PutInStorerMaxTime
+}
+
 func (bp *baseProcessor) saveProof(
 	hash []byte,
 	header data.HeaderHandler,
```

### storage/pruning/pruningStorer.go
```diff
@@ -692,6 +692,15 @@ func (ps *PruningStorer) Has(key []byte) error {
 
 // SetEpochForPutOperation will set the epoch to be used when using the put operation
 func (ps *PruningStorer) SetEpochForPutOperation(epoch uint32) {
+	ps.lock.RLock()
+	epochForPutOperation := ps.epochForPutOperation
+	ps.lock.RUnlock()
+
+	// do not try to aquire full lock if epoch already set
+	if epoch == epochForPutOperation {
+		return
+	}
+
 	ps.lock.Lock()
 	ps.epochForPutOperation = epoch
 	ps.lock.Unlock()
```
