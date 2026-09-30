# [?] fix(core): Fix crashes in execution_driver due to inability to execute transactions (#4928)

## Summary
Severity: Unknown
Chain: IOTA
Component: iotaledger/iota
Published: 2025-01-22
Source: https://github.com/iotaledger/iota/commit/94b801f0f856d766fb3ed1b884c08788a54862c0
Type: security-commit

## Details
fix(core): Fix crashes in execution_driver due to inability to execute transactions (#4928)

## Patch
### crates/iota-core/src/execution_cache/writeback_cache.rs
```diff
@@ -480,15 +480,41 @@ impl WritebackCache {
         debug!(?object_id, ?version, ?object, "inserting object entry");
         fail_point_async!("write_object_entry");
         self.metrics.record_cache_write("object");
-        self.dirty
-            .objects
-            .entry(*object_id)
-            .or_default()
-            .insert(version, object.clone());
+
+        // We must hold the lock for the object entry while inserting to the
+        // object_by_id_cache. Otherwise, a surprising bug can occur:
+        //
+        // 1. A thread executing TX1 can write object (O,1) to the dirty set and then
+        //    pause.
+        // 2. TX2, which reads (O,1) can begin executing, because TransactionManager
+        //    immediately schedules transactions if their inputs are available. It does
+        //    not matter that TX1 hasn't finished executing yet.
+        // 3. TX2 can write (O,2) to both the dirty set and the object_by_id_cache.
+        // 4. The thread executing TX1 can resume and write (O,1) to the
+        //    object_by_id_cache.
+        //
+        // Now, any subsequent attempt to get the latest version of O will return (O,1)
+        // instead of (O,2).
+        //
+        // This seems very unlikely, but it may be possible under the following
+        // circumstances:
+        // - While a thread is unlikely to pause for so long, moka cache uses optimistic
+        //   lock-free algorithms that have retry loops. Possibly, under high
+        //   contention, this code might spin for a surprisingly long time.
+        // - Additionally, many concurrent re-executions of the same tx could happen due
+        //   to the tx finalizer, plus checkpoint executor, consensus, and RPCs from
+        //   fullnodes.
+        let mut entry = self.dirty.objects.entry(*object_id).or_default();
+
         self.cached.object_by_id_cache.insert(
             *object_id,
-            Arc::new(Mutex::new(LatestObjectCacheEntry::Object(version, object))),
+            Arc::new(Mutex::new(LatestObjectCacheEntry::Object(
+                version,
+                object.clone(),
+            ))),
         );
+
+        entry.insert(version, object);
     }
 
     async fn write_marker_value(
```
