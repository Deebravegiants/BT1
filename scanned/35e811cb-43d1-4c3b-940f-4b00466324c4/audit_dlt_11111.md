# [?] Fix deadlock

## Summary
Severity: Unknown
Chain: zkSync Lite
Component: matter-labs/zksync
Published: 2023-03-25
Source: https://github.com/matter-labs/zksync/commit/cea211e9277c4c742b2a23bb0d31d2dbc454c9c7
Type: security-commit

## Details
Fix deadlock

Signed-off-by: Danil <deniallugo@gmail.com>

## Patch
### core/bin/zksync_core/src/state_keeper/mod.rs
```diff
@@ -333,11 +333,6 @@ impl ZkSyncStateKeeper {
                 .collect(),
         );
 
-        vlog::debug!(
-            "Requesting new miniblock from mempool. {} txs are excluded from search. {} chunks left",
-            executed_txs.len(),
-            self.pending_block.chunks_left
-        );
         let mempool_req = MempoolBlocksRequest::GetBlock(GetBlockRequest {
             last_priority_op_number: self.pending_block.unprocessed_priority_op_current,
             block_timestamp,
```

### core/bin/zksync_witness_generator/src/witness_generator.rs
```diff
@@ -122,7 +122,7 @@ impl<DB: DatabaseInterface> WitnessGenerator<DB> {
             metrics::increment_counter!("witness_generator.cache_access", "type" => "hit_in_memory");
             return Ok(Some((*block, cache.clone())));
         }
-
+        drop(cache);
         let mut storage = self.database.acquire_connection().await?;
         if let Some((block, cache)) = self.database.load_account_tree_cache(&mut storage).await? {
             let cache = SparseMerkleTreeSerializableCacheBN256::decode_bincode(&cache);
```
