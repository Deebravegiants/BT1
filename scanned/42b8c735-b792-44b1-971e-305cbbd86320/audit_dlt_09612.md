# [?] fix two panics (#873)

## Summary
Severity: Unknown
Chain: Conflux
Component: Conflux-Chain/conflux-rust
Published: 2019-12-27
Source: https://github.com/Conflux-Chain/conflux-rust/commit/a88d016ee236765865f6c345bd3527280978fbc0
Type: security-commit

## Details
fix two panics (#873)

## Patch
### core/src/consensus/consensus_inner/consensus_new_block_handler.rs
```diff
@@ -1513,14 +1513,18 @@ impl ConsensusNewBlockHandler {
         }
         let storage_manager =
             self.data_man.storage_manager.get_storage_manager();
+        let parent_snapshot_height = if state_boundary_height == 0 {
+            0
+        } else {
+            state_boundary_height - storage_manager.get_snapshot_epoch_count()
+        };
         // FIXME Most are fake because not used now
         // And it's also not correct to unconditionally set delta_mpt and
         // intermediate_mpt as Some
         let snapshot_info = SnapshotInfo {
             serve_one_step_sync: false,
             merkle_root: Default::default(),
-            parent_snapshot_height: state_boundary_height
-                - storage_manager.get_snapshot_epoch_count(),
+            parent_snapshot_height,
             height: state_boundary_height,
             parent_snapshot_epoch_id: Default::default(),
             pivot_chain_parts: vec![start_hash],
```

### core/src/consensus/consensus_inner/mod.rs
```diff
@@ -2770,6 +2770,13 @@ impl ConsensusGraphInner {
         let start_pivot_index =
             (self.data_man.state_availability_boundary.read().lower_bound
                 - self.cur_era_genesis_height) as usize;
+        if start_pivot_index >= self.pivot_chain.len() {
+            // It seems that if this case happens, it is a full node and
+            // stated was synced from peers. So, `state_valid` will be recovered
+            // by `pivot_block_state_valid_map`.
+            // TODO: We may need to go through the whole logic.
+            return;
+        }
         let start_epoch_hash =
             self.arena[self.pivot_chain[start_pivot_index]].hash;
         // We will get the first
```

### tests/conflux_tracing.py
```diff
@@ -440,9 +440,9 @@ def set_test_params(self):
             "generate_tx": "true",
             "generate_tx_period_us": "100000",
             "enable_state_expose": "true",
-            "era_epoch_count": 50,
-            "snapshot_epoch_count": 25,
-            "era_checkpoint_gap": 50
+            "era_epoch_count": 100,
+            "snapshot_epoch_count": 50,
+            "era_checkpoint_gap": 100
         }
 
     def setup_nodes(self):
```
