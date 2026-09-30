# [?] [consensus] fix a race condition

## Summary
Severity: Unknown
Chain: Aptos
Component: aptos-labs/aptos-core
Published: 2025-10-03
Source: https://github.com/aptos-labs/aptos-core/commit/d4c5b9a792ff528c81aa3029934188b550da8621
Type: security-commit

## Details
[consensus] fix a race condition

There's a race condition where if the commit proof is forwarded, sync manager decides to sync but fails to retrieve block or something,
then a lower round commit proof can come and decides to pause pre_commit and sync but previous commit proof can resume the pre_commit to
go beyond the target version.

## Patch
### consensus/src/block_storage/sync_manager.rs
```diff
@@ -119,12 +119,6 @@ impl BlockStore {
         sync_info: &SyncInfo,
         mut retriever: BlockRetriever,
     ) -> anyhow::Result<()> {
-        self.sync_to_highest_commit_cert(
-            sync_info.highest_commit_cert().ledger_info(),
-            retriever.network.clone(),
-        )
-        .await;
-
         // When the local ordered round is very old than the received sync_info, this function will
         // (1) resets the block store with highest commit cert = sync_info.highest_quorum_cert()
         // (2) insert all the blocks between (inclusive) highest_commit_cert.commit_info().id() to
@@ -138,6 +132,12 @@ impl BlockStore {
         )
         .await?;
 
+        self.sync_to_highest_commit_cert(
+            sync_info.highest_commit_cert().ledger_info(),
+            retriever.network.clone(),
+        )
+        .await;
+
         // The insert_ordered_cert(order_cert) function call expects that order_cert.commit_info().id() block
         // is already stored in block_store. So, we first call insert_quorum_cert(highest_quorum_cert).
         // This call will ensure that the highest ceritified block along with all its ancestors are inserted
```
