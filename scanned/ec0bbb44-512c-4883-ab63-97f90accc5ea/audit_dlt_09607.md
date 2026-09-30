# [?] fix deadlock in MallocSizeOf impl (#1107)

## Summary
Severity: Unknown
Chain: Conflux
Component: Conflux-Chain/conflux-rust
Published: 2020-03-22
Source: https://github.com/Conflux-Chain/conflux-rust/commit/ea19e9d09d0fc5d489b2b5f84e0c473c8df1efd2
Type: security-commit

## Details
fix deadlock in MallocSizeOf impl (#1107)

Co-authored-by: Ming Wu <ming@conflux-chain.org>

## Patch
### core/src/block_data_manager/mod.rs
```diff
@@ -209,22 +209,41 @@ pub struct BlockDataManager {
 
 impl MallocSizeOf for BlockDataManager {
     fn size_of(&self, ops: &mut MallocSizeOfOps) -> usize {
-        self.block_headers.read().size_of(ops)
-            + self.blocks.read().size_of(ops)
-            + self.compact_blocks.read().size_of(ops)
-            + self.block_receipts.read().size_of(ops)
-            + self.transaction_indices.read().size_of(ops)
-            + self.epoch_execution_commitments.read().size_of(ops)
-            + self.epoch_execution_contexts.read().size_of(ops)
-            + self.invalid_block_set.read().size_of(ops)
-            + self.cur_consensus_era_genesis_hash.read().size_of(ops)
-            + self.cur_consensus_era_stable_hash.read().size_of(ops)
+        let block_headers_size = self.block_headers.read().size_of(ops);
+        let blocks_size = self.blocks.read().size_of(ops);
+        let compact_blocks_size = self.compact_blocks.read().size_of(ops);
+        let block_receipts_size = self.block_receipts.read().size_of(ops);
+        let transaction_indices_size =
+            self.transaction_indices.read().size_of(ops);
+        let epoch_execution_commitments_size =
+            self.epoch_execution_commitments.read().size_of(ops);
+        let epoch_execution_contexts_size =
+            self.epoch_execution_contexts.read().size_of(ops);
+        let invalid_block_set_size = self.invalid_block_set.read().size_of(ops);
+        let cur_consensus_era_genesis_hash_size =
+            self.cur_consensus_era_genesis_hash.read().size_of(ops);
+        let cur_consensus_era_stable_hash_size =
+            self.cur_consensus_era_stable_hash.read().size_of(ops);
+        let cache_man_size = self.cache_man.lock().size_of(ops);
+        let state_availability_boundary_size =
+            self.state_availability_boundary.read().size_of(ops);
+
+        block_headers_size
+            + blocks_size
+            + compact_blocks_size
+            + block_receipts_size
+            + transaction_indices_size
+            + epoch_execution_commitments_size
+            + epoch_execution_contexts_size
+            + invalid_block_set_size
+            + cur_consensus_era_genesis_hash_size
+            + cur_consensus_era_stable_hash_size
             + self.config.size_of(ops)
             + self.tx_data_manager.size_of(ops)
             + self.true_genesis.size_of(ops)
-            + self.cache_man.lock().size_of(ops)
+            + cache_man_size
             + self.target_difficulty_manager.size_of(ops)
-            + self.state_availability_boundary.read().size_of(ops)
+            + state_availability_boundary_size
     }
 }
 
```

### core/src/consensus/mod.rs
```diff
@@ -161,11 +161,14 @@ pub struct ConsensusGraph {
 
 impl MallocSizeOf for ConsensusGraph {
     fn size_of(&self, ops: &mut MallocSizeOfOps) -> usize {
+        let best_info_size = self.best_info.read().size_of(ops);
+        let pivot_block_state_valid_map_size =
+            self.pivot_block_state_valid_map.lock().size_of(ops);
         self.inner.read().size_of(ops)
             + self.txpool.size_of(ops)
             + self.data_man.size_of(ops)
-            + self.best_info.read().size_of(ops)
-            + self.pivot_block_state_valid_map.lock().size_of(ops)
+            + best_info_size
+            + pivot_block_state_valid_map_size
     }
 }
 
```

### core/src/sync/synchronization_graph.rs
```diff
@@ -970,9 +970,12 @@ pub struct SynchronizationGraph {
 
 impl MallocSizeOf for SynchronizationGraph {
     fn size_of(&self, ops: &mut MallocSizeOfOps) -> usize {
-        let mut malloc_size = self.inner.read().size_of(ops)
+        let inner_size = self.inner.read().size_of(ops);
+        let initial_missed_block_hashes_size =
+            self.initial_missed_block_hashes.lock().size_of(ops);
+        let mut malloc_size = inner_size
             + self.data_man.size_of(ops)
-            + self.initial_missed_block_hashes.lock().size_of(ops);
+            + initial_missed_block_hashes_size;
 
         // TODO: Add statistics for consortium.
         if !self.is_consortium() {
```

### core/src/transaction_pool/mod.rs
```diff
@@ -108,13 +108,21 @@ pub struct TransactionPool {
 
 impl MallocSizeOf for TransactionPool {
     fn size_of(&self, ops: &mut MallocSizeOfOps) -> usize {
+        let inner_size = self.inner.read().size_of(ops);
+        let to_propagate_trans_size =
+            self.to_propagate_trans.read().size_of(ops);
+        let consensus_best_info_size =
+            self.consensus_best_info.lock().size_of(ops);
+        let set_tx_requests_size = self.set_tx_requests.lock().size_of(ops);
+        let recycle_tx_requests_size =
+            self.recycle_tx_requests.lock().size_of(ops);
         self.config.size_of(ops)
-            + self.inner.read().size_of(ops)
-            + self.to_propagate_trans.read().size_of(ops)
+            + inner_size
+            + to_propagate_trans_size
             + self.data_man.size_of(ops)
-            + self.consensus_best_info.lock().size_of(ops)
-            + self.set_tx_requests.lock().size_of(ops)
-            + self.recycle_tx_requests.lock().size_of(ops)
+            + consensus_best_info_size
+            + set_tx_requests_size
+            + recycle_tx_requests_size
     }
 }
 
```
