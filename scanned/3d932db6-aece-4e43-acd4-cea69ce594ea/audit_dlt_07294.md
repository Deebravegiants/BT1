# [?] fix(state-snapshots): Flat Storage Inlining doesn't crash if state snapshotting is in process (#9259)

## Summary
Severity: Unknown
Chain: NEAR
Component: near/nearcore
Published: 2023-06-28
Source: https://github.com/near/nearcore/commit/8cd095ffc98a6507ed2d2a8982a6a3e42ebc1b62
Type: security-commit

## Details
fix(state-snapshots): Flat Storage Inlining doesn't crash if state snapshotting is in process (#9259)

* fix(state-snapshots): Flat Storage Inlining doesn't crash if state snapshotting is ongoing

* Cleanup duplicated code

## Patch
### core/store/src/flat/inlining_migration.rs
```diff
@@ -2,6 +2,7 @@ use std::collections::HashMap;
 use std::sync::atomic::AtomicBool;
 use std::sync::Arc;
 use std::thread::JoinHandle;
+use std::time::Duration;
 
 use borsh::{BorshDeserialize, BorshSerialize};
 use crossbeam::channel;
@@ -229,12 +230,18 @@ pub fn inline_flat_state_values(
         let mut inlined_batch_count = 0;
         let mut batch_duration = std::time::Duration::ZERO;
         if !hash_to_value.is_empty() {
+            // Possibly flat storage head can be locked. If that happens wait a little bit and try again.
+            // The number of attempts is infinite because flat storage head is supposed to be usually unlocked.
+            interrupted = lock_flat_head_blocking(flat_storage_manager, keep_running, batch_index);
+            if interrupted {
+                break;
+            }
+            tracing::debug!(target: "store", "Locked flat storage for the inlining migration");
+
             // Here we need to re-read the latest FlatState values in `min_key..=max_key` range
             // while updates are disabled. This way we prevent updating the values that
             // were updated since migration start.
             let batch_inlining_start = std::time::Instant::now();
-            assert!(flat_storage_manager.set_flat_state_updates_mode(false));
-            tracing::info!(target: "store", "Locked flat storage for the inlining migration");
             let mut store_update = store.store_update();
             // rockdb API accepts the exclusive end of the range, so we append
             // `0u8` here to make sure `max_key` is included in the range
@@ -275,48 +282,59 @@ pub fn inline_flat_state_values(
     !interrupted
 }
 
+/// Blocks until the flat head is locked or until the thread is interrupted.
+/// Returns whether it was interrupted.
+fn lock_flat_head_blocking(
+    flat_storage_manager: &FlatStorageManager,
+    keep_running: &AtomicBool,
+    batch_index: usize,
+) -> bool {
+    loop {
+        if !keep_running.load(std::sync::atomic::Ordering::Relaxed) {
+            tracing::info!(target: "store", batch_index, "FlatState value inlining migration was interrupted");
+            return true;
+        }
+        if flat_storage_manager.set_flat_state_updates_mode(false) {
+            return false;
+        }
+        tracing::debug!(target: "store", "Couldn't lock flat storage for the inlining migration, will retry locking.");
+        std::thread::sleep(Duration::from_secs(1));
+    }
+}
+
 fn log_skipped(reason: &str, err: impl std::error::Error) {
     debug!(target: "store", %reason, %err, "Skipped value during FlatState inlining");
     SKIPPED_COUNT.inc();
 }
 
 #[cfg(test)]
 mod tests {
-    use std::sync::atomic::AtomicBool;
-
-    use borsh::{BorshDeserialize, BorshSerialize};
-    use near_primitives::hash::hash;
-    use near_primitives::shard_layout::ShardLayout;
-    use near_primitives::state::FlatStateValue;
-
+    use super::inline_flat_state_values;
     use crate::flat::store_helper::encode_flat_state_db_key;
     use crate::flat::types::INLINE_DISK_VALUE_THRESHOLD;
-    use crate::flat::FlatStorageManager;
-    use crate::{DBCol, NodeStorage, TrieCachingStorage};
-
-    use super::inline_flat_state_values;
+    use crate::flat::{FlatStateValuesInliningMigrationHandle, FlatStorageManager};
+    use crate::{DBCol, NodeStorage, Store, TrieCachingStorage};
+    use borsh::{BorshDeserialize, BorshSerialize};
+    use near_o11y::testonly::init_test_logger;
+    use near_primitives::hash::{hash, CryptoHash};
+    use near_primitives::shard_layout::{ShardLayout, ShardUId};
+    use near_primitives::state::FlatStateValue;
+    use std::sync::atomic::AtomicBool;
+    use std::time::Duration;
 
     #[test]
     fn full_migration() {
         let store = NodeStorage::test_opener().1.open().unwrap().get_hot_store();
         let shard_uid = ShardLayout::v0_single_shard().get_shard_uids()[0];
         let values =
             [vec![0], vec![1], vec![2; INLINE_DISK_VALUE_THRESHOLD + 1], vec![3], vec![4], vec![5]];
-        {
-            let mut store_update = store.store_update();
-            for (i, value) in values.iter().enumerate() {
-                let trie_key =
-                    TrieCachingStorage::get_key_from_shard_uid_and_hash(shard_uid, &hash(&value));
-                store_update.increment_refcount(DBCol::State, &trie_key, &value);
-                let fs_key = encode_flat_state_db_key(shard_uid, &[i as u8]);
-                let fs_value = FlatStateValue::value_ref(&value).try_to_vec().unwrap();
-                store_update.set(DBCol::FlatState, &fs_key, &fs_value);
-            }
-            store_update.commit().unwrap();
-        }
+        populate_flat_store(&store, shard_uid, &values);
+
+        let flat_storage_manager =
+            FlatStorageManager::test(store.clone(), &vec![shard_uid], CryptoHash::default());
         inline_flat_state_values(
             store.clone(),
-            &FlatStorageManager::new(store.clone()),
+            &flat_storage_manager,
             &AtomicBool::new(true),
             2,
             4,
@@ -336,4 +354,104 @@ mod tests {
             ]
         );
     }
+
+    #[test]
+    // Initializes several ref values.
+    // Locks flat storage head, and checks that the migration doesn't crash and doesn't proceed.
+    // Then it unlocks flat head and checks that the migration completes.
+    fn block_migration() {
+        init_test_logger();
+        let store = NodeStorage::test_opener().1.open().unwrap().get_hot_store();
+        let shard_uid = ShardLayout::v0_single_shard().get_shard_uids()[0];
+        let values =
+            [vec![0], vec![1], vec![2; INLINE_DISK_VALUE_THRESHOLD + 1], vec![3], vec![4], vec![5]];
+        populate_flat_store(&store, shard_uid, &values);
+
+        let flat_storage_manager =
+            FlatStorageManager::test(store.clone(), &vec![shard_uid], CryptoHash::default());
+        // Lock flat head.
+        assert!(flat_storage_manager.set_flat_state_updates_mode(false));
+        // Start a separate thread that should block waiting for the flat head.
+        let _handle = FlatStateValuesInliningMigrationHandle::start_background_migration(
+            store.clone(),
+            flat_storage_manager.clone(),
+            2,
+        );
+
+        // Give it time and check that no progress was made on the migration.
+        std::thread::sleep(Duration::from_secs(2));
+        assert_eq!(count_inlined_values(&store), 0);
+
+        // Unlock.
+        assert!(flat_storage_manager.set_flat_state_updates_mode(true));
+
+        // Give it more time. It should be unblocked now and the migration should complete.
+        std::thread::sleep(Duration::from_secs(2));
+        assert_eq!(count_inlined_values(&store), 5);
+    }
+
+    #[test]
+    // Initializes several ref values.
+    // Locks flat storage head, and checks that the migration doesn't crash and doesn't proceed.
+    // Interrupt the migration and check that the thread exits.
+    fn interrupt_blocked_migration() {
+        init_test_logger();
+        let store = NodeStorage::test_opener().1.open().unwrap().get_hot_store();
+        let shard_uid = ShardLayout::v0_single_shard().get_shard_uids()[0];
+        let values =
+            [vec![0], vec![1], vec![2; INLINE_DISK_VALUE_THRESHOLD + 1], vec![3], vec![4], vec![5]];
+        populate_flat_store(&store, shard_uid, &values);
+
+        let flat_storage_manager =
+            FlatStorageManager::test(store.clone(), &vec![shard_uid], CryptoHash::default());
+        // Lock flat head.
+        assert!(flat_storage_manager.set_flat_state_updates_mode(false));
+        // Start a separate thread that should block waiting for the flat head.
+        let handle = FlatStateValuesInliningMigrationHandle::start_background_migration(
+            store.clone(),
+            flat_storage_manager,
+            2,
+        );
+
+        // Give it time and check that no progress was made on the migration.
+        std::thread::sleep(Duration::from_secs(2));
+        assert_eq!(count_inlined_values(&store), 0);
+
+        // Interrupt.
+        handle.keep_running.store(false, std::sync::atomic::Ordering::Relaxed);
+        assert!(handle.handle.join().is_ok());
+        // Check that no migration took place.
+        assert_eq!(count_inlined_values(&store), 0);
+    }
+
+    fn populate_flat_store(store: &Store, shard_uid: ShardUId, values: &[Vec<u8>]) {
+        let mut store_update = store.store_update();
+        for (i, value) in values.iter().enumerate() {
+            let trie_key =
+                TrieCachingStorage::get_key_from_shard_uid_and_hash(shard_uid, &hash(&value));
+            store_update.increment_refcount(DBCol::State, &trie_key, &value);
+            let fs_key = encode_flat_state_db_key(shard_uid, &[i as u8]);
+            let fs_value = FlatStateValue::value_ref(&value).try_to_vec().unwrap();
+            store_update.set(DBCol::FlatState, &fs_key, &fs_value);
+        }
+        store_update.commit().unwrap();
+    }
+
+    fn count_inlined_values(store: &Store) -> u64 {
+        store
+            .iter(DBCol::FlatState)
+            .flat_map(|r| {
+                r.map(|(_, v)| {
+                    if matches!(
+                        FlatStateValue::try_from_slice(&v).unwrap(),
+                        FlatStateValue::Inlined(_)
+                    ) {
+                        1
+                    } else {
+                        0
+                    }
+                })
+            })
+            .sum::<u64>()
+    }
 }
```
