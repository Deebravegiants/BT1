# [?] Merge pull request #7631 from multiversx/fix-panic-outport-data-provider

## Summary
Severity: Unknown
Chain: MultiversX
Component: multiversx/mx-chain-go
Published: 2026-01-22
Source: https://github.com/multiversx/mx-chain-go/commit/92c51f4c9c5451284533ced5598bafc6b7346d97
Type: security-commit

## Details
Merge pull request #7631 from multiversx/fix-panic-outport-data-provider

Fix panic outport data provider

## Patch
### outport/process/outportDataProvider.go
```diff
@@ -718,6 +718,10 @@ func putInMapTxsFromBody(
 
 		strCache := process.ShardCacherIdentifier(mb.SenderShardID, mb.ReceiverShardID)
 		cache := storeByType.ShardDataStore(strCache)
+		if check.IfNil(cache) {
+			log.Debug("putInMapTxsFromBody cannot find shard data store", "senderShardID", mb.SenderShardID, "receiverShardID", mb.ReceiverShardID, "type", mb.Type)
+			continue
+		}
 
 		for _, txHash := range mb.TxHashes {
 			txI, found := cache.Get(txHash)
```
