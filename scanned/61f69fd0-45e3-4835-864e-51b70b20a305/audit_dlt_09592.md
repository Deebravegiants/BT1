# [?] Fix deadlock in state_manager / storage_manager. (#1873)

## Summary
Severity: Unknown
Chain: Conflux
Component: Conflux-Chain/conflux-rust
Published: 2020-10-01
Source: https://github.com/Conflux-Chain/conflux-rust/commit/0b9bcfcd5bd484670272a1da7bd56a247abfbf65
Type: security-commit

## Details
Fix deadlock in state_manager / storage_manager. (#1873)

## Patch
### core/storage/src/impls/state_manager.rs
```diff
@@ -309,21 +309,24 @@ impl StateManager {
                     }
                 }
                 Some(guarded_snapshot) => {
-                    snapshot_merkle_root = match self
-                        .storage_manager
-                        .get_snapshot_info_at_epoch(snapshot_epoch_id)
-                    {
-                        None => {
-                            warn!(
+                    let (guard, _snapshot) = guarded_snapshot.into();
+                    snapshot_merkle_root =
+                        match StorageManager::find_merkle_root(
+                            &guard,
+                            snapshot_epoch_id,
+                        ) {
+                            None => {
+                                warn!(
                                 "get_state_trees_for_next_epoch, shift snapshot, normal case, \
                                 snapshot info not found for snapshot {:?}. StateIndex: {:?}.",
                                 snapshot_epoch_id,
                                 parent_state_index,
                             );
-                            return Ok(None);
-                        }
-                        Some(snapshot_info) => snapshot_info.merkle_root,
-                    };
+                                return Ok(None);
+                            }
+                            Some(merkle_root) => merkle_root,
+                        };
+                    let guarded_snapshot = GuardedValue::new(guard, _snapshot);
                     let temp_maybe_intermediate_mpt = self
                         .storage_manager
                         .get_intermediate_mpt(snapshot_epoch_id)?;
@@ -625,6 +628,7 @@ use crate::{
     state::*,
     state_manager::*,
     storage_db::*,
+    utils::guarded_value::GuardedValue,
     StorageConfiguration,
 };
 use malloc_size_of_derive::MallocSizeOf as MallocSizeOfDerive;
```

### core/storage/src/impls/storage_manager/storage_manager.rs
```diff
@@ -122,7 +122,8 @@ pub struct StorageManager {
     // Note that for archive node the list here is just a subset of what's
     // available.
     //
-    // Lock order: while this is locked, in load_persist_state,
+    // Lock order: while this is locked, in load_persist_state and
+    // state_manager.rs:get_state_trees_for_next_epoch
     // snapshot_associated_mpts_by_epoch is locked later.
     current_snapshots: RwLock<Vec<SnapshotInfo>>,
     // Lock order: while this is locked, in register_new_snapshot and
@@ -295,6 +296,15 @@ impl StorageManager {
         new_storage_manager_result
     }
 
+    pub fn find_merkle_root(
+        current_snapshots: &Vec<SnapshotInfo>, epoch_id: &EpochId,
+    ) -> Option<MerkleHash> {
+        current_snapshots
+            .iter()
+            .find(|i| i.get_snapshot_epoch_id() == epoch_id)
+            .map(|i| i.merkle_root.clone())
+    }
+
     pub fn wait_for_snapshot(
         &self, snapshot_epoch_id: &EpochId, try_open: bool,
     ) -> Result<
@@ -1389,7 +1399,7 @@ use cfx_internal_common::{
 use fallible_iterator::FallibleIterator;
 use malloc_size_of::{MallocSizeOf, MallocSizeOfOps};
 use parking_lot::{Mutex, RwLock, RwLockReadGuard};
-use primitives::{EpochId, MERKLE_NULL_NODE, NULL_EPOCH};
+use primitives::{EpochId, MerkleHash, MERKLE_NULL_NODE, NULL_EPOCH};
 use rlp::{Decodable, DecoderError, Encodable, Rlp};
 use sqlite::Statement;
 use std::{
```
