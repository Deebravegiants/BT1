# [?] fix(db): Fix "values cache update task failed" panics (#1561)

## Summary
Severity: Unknown
Chain: zkSync
Component: matter-labs/zksync-era
Published: 2024-04-03
Source: https://github.com/matter-labs/zksync-era/commit/f7c5c142e46de19abee540deb8a067934be17ca9
Type: security-commit

## Details
fix(db): Fix "values cache update task failed" panics (#1561)

## What ❔

Fixes a panic in `PostgresStorageCaches::schedule_values_update()` if
the update task has exited.

## Why ❔

Interrupts transaction processing and leads to false positives in panic
reporting.

## Checklist

- [x] PR title corresponds to the body of PR (we generate changelog
entries from PRs).
- [x] Tests for the changes have been added / updated.
- [x] Documentation comments have been added / updated.
- [x] Code has been formatted via `zk fmt` and `zk lint`.
- [x] Spellcheck has been run via `zk spellcheck`.
- [x] Linkcheck has been run via `zk linkcheck`.

## Patch
### core/lib/state/src/postgres/mod.rs
```diff
@@ -333,10 +333,10 @@ impl PostgresStorageCaches {
         };
         if values.cache.valid_for() < to_miniblock {
             // Filter out no-op updates right away in order to not store lots of them in RAM.
-            values
-                .command_sender
-                .send(to_miniblock)
-                .expect("values cache update task failed");
+            // Since the task updating the values cache (`PostgresStorageCachesTask`) is cancel-aware,
+            // it can stop before some of `schedule_values_update()` calls; in this case, it's OK
+            // to ignore the updates.
+            values.command_sender.send(to_miniblock).ok();
         }
     }
 }
```

### core/lib/state/src/postgres/tests.rs
```diff
@@ -1,6 +1,6 @@
 //! Tests for `PostgresStorage`.
 
-use std::{collections::HashMap, mem};
+use std::{collections::HashMap, mem, time::Duration};
 
 use rand::{
     rngs::StdRng,
@@ -384,11 +384,27 @@ impl ValuesCache {
     }
 }
 
+async fn wait_for_cache_update(values_cache: &ValuesCache, target_miniblock: MiniblockNumber) {
+    tokio::time::timeout(Duration::from_secs(5), async {
+        loop {
+            let valid_for = values_cache.0.read().unwrap().valid_for;
+            assert!(valid_for <= target_miniblock, "{valid_for:?}");
+            if valid_for == target_miniblock {
+                break;
+            }
+            tokio::time::sleep(Duration::from_millis(50)).await;
+        }
+    })
+    .await
+    .expect("timed out waiting for cache update");
+}
+
 fn test_values_cache(pool: &ConnectionPool<Core>, rt_handle: Handle) {
     let mut caches = PostgresStorageCaches::new(1_024, 1_024);
-    let _ = caches.configure_storage_values_cache(1_024 * 1_024, pool.clone());
-    // We cannot use an update task since it requires having concurrent DB connections
-    // that don't work in tests. We'll update values cache manually instead.
+    let task = caches.configure_storage_values_cache(1_024 * 1_024, pool.clone());
+    let (stop_sender, stop_receiver) = watch::channel(false);
+    let update_task_handle = tokio::task::spawn(task.run(stop_receiver));
+
     let values_cache = caches.values.as_ref().unwrap().cache.clone();
     let old_miniblock_assertions = values_cache.assertions(MiniblockNumber(0));
     let new_miniblock_assertions = values_cache.assertions(MiniblockNumber(1));
@@ -451,15 +467,10 @@ fn test_values_cache(pool: &ConnectionPool<Core>, rt_handle: Handle) {
         (non_existing_key, Some(H256::zero())),
     ]);
 
+    caches.schedule_values_update(MiniblockNumber(1));
     storage
         .rt_handle
-        .block_on(values_cache.update(
-            MiniblockNumber(0),
-            MiniblockNumber(1),
-            &mut storage.connection,
-        ))
-        .unwrap();
-    assert_eq!(values_cache.0.read().unwrap().valid_for, MiniblockNumber(1));
+        .block_on(wait_for_cache_update(&values_cache, MiniblockNumber(1)));
 
     assert_eq!(storage.read_value(&existing_key), H256::repeat_byte(1));
     assert_eq!(storage.read_value(&non_existing_key), H256::repeat_byte(2));
@@ -487,14 +498,23 @@ fn test_values_cache(pool: &ConnectionPool<Core>, rt_handle: Handle) {
         MiniblockNumber(0),
         true,
     )
-    .with_caches(caches);
+    .with_caches(caches.clone());
 
     assert_eq!(storage.read_value(&existing_key), initial_value);
     assert_eq!(storage.read_value(&non_existing_key), StorageValue::zero());
     assert_eq!(storage.read_value(&unmodified_key), unmodified_value);
 
     // None of the cache entries should be modified.
     assert_final_cache();
+
+    stop_sender.send_replace(true);
+    storage
+        .rt_handle
+        .block_on(update_task_handle)
+        .expect("update task panicked")
+        .unwrap();
+    // Check that `schedule_values_update()` doesn't panic after the update task is finished.
+    caches.schedule_values_update(MiniblockNumber(2));
 }
 
 #[tokio::test]
```
