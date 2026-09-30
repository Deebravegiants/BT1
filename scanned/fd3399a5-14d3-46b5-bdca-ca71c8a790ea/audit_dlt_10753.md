# [?] fix panic outport data provider

## Summary
Severity: Unknown
Chain: MultiversX
Component: multiversx/mx-chain-go
Published: 2026-01-21
Source: https://github.com/multiversx/mx-chain-go/commit/2d9fe10e2b7e6a23bdc994c02cf9447cba95b8c7
Type: security-commit

## Details
fix panic outport data provider

## Patch
### outport/process/outportDataProvider.go
```diff
@@ -718,6 +718,10 @@ func putInMapTxsFromBody(
 
 		strCache := process.ShardCacherIdentifier(mb.SenderShardID, mb.ReceiverShardID)
 		cache := storeByType.ShardDataStore(strCache)
+		if check.IfNil(cache) {
+			log.Warn("putInMapTxsFromBody cannot find shard data store", "shardID", mb.SenderShardID, "shardID", mb.ReceiverShardID, "type", mb.Type)
+			continue
+		}
 
 		for _, txHash := range mb.TxHashes {
 			txI, found := cache.Get(txHash)
```
