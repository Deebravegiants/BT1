# [?] fix shard nodes panicking while requesting epoch start meta proof

## Summary
Severity: Unknown
Chain: MultiversX
Component: multiversx/mx-chain-go
Published: 2025-04-24
Source: https://github.com/multiversx/mx-chain-go/commit/5c7f7a3ae1bcc50c3fdcfe18180b997cc485e1bd
Type: security-commit

## Details
fix shard nodes panicking while requesting epoch start meta proof

## Patch
### process/block/shardblock.go
```diff
@@ -392,7 +392,7 @@ func (sp *shardProcessor) requestEpochStartInfo(header data.ShardHeaderHandler,
 	sp.dataPool.Headers().RemoveHeaderByHash(header.GetEpochStartMetaHash())
 	go sp.requestHandler.RequestMetaHeader(header.GetEpochStartMetaHash())
 
-	sp.requestProofIfNeeded(header.GetEpochStartMetaHash(), header.GetEpoch(), core.MetachainShardId)
+	sp.requestEpochStartProofIfNeeded(header.GetEpochStartMetaHash())
 
 	headersPool := sp.dataPool.Headers()
 	for {
@@ -408,7 +408,7 @@ func (sp *shardProcessor) requestEpochStartInfo(header data.ShardHeaderHandler,
 		epochStartMetaHdr, err := headersPool.GetHeaderByHash(header.GetEpochStartMetaHash())
 		if err != nil {
 			go sp.requestHandler.RequestMetaHeader(header.GetEpochStartMetaHash())
-			sp.requestProofIfNeeded(header.GetEpochStartMetaHash(), header.GetEpoch(), core.MetachainShardId)
+			sp.requestEpochStartProofIfNeeded(header.GetEpochStartMetaHash())
 			continue
 		}
 
@@ -420,7 +420,7 @@ func (sp *shardProcessor) requestEpochStartInfo(header data.ShardHeaderHandler,
 				continue
 			}
 		} else {
-			hasProof := sp.requestProofIfNeeded(header.GetEpochStartMetaHash(), header.GetEpoch(), core.MetachainShardId)
+			hasProof := sp.requestEpochStartProofIfNeeded(header.GetEpochStartMetaHash())
 			if !hasProof {
 				continue
 			}
@@ -432,6 +432,21 @@ func (sp *shardProcessor) requestEpochStartInfo(header data.ShardHeaderHandler,
 	return process.ErrTimeIsOut
 }
 
+func (sp *shardProcessor) requestEpochStartProofIfNeeded(hash []byte) bool {
+	if !sp.enableEpochsHandler.IsFlagEnabledInEpoch(common.AndromedaFlag, sp.epochStartTrigger.MetaEpoch()) {
+		return true
+	}
+
+	hasProof := sp.proofsPool.HasProof(core.MetachainShardId, hash)
+	if hasProof {
+		return true
+	}
+
+	go sp.requestHandler.RequestEquivalentProofByHash(core.MetachainShardId, hash)
+
+	return false
+}
+
 // RevertStateToBlock recreates the state tries to the root hashes indicated by the provided root hash and header
 func (sp *shardProcessor) RevertStateToBlock(header data.HeaderHandler, rootHash []byte) error {
 	rootHashHolder := holders.NewDefaultRootHashesHolder(rootHash)
```
