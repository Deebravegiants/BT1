# [?] Fix a reentrant deadlock of getting traces.

## Summary
Severity: Unknown
Chain: Conflux
Component: Conflux-Chain/conflux-rust
Published: 2021-03-12
Source: https://github.com/Conflux-Chain/conflux-rust/commit/a7def924f90f46f48df64951384f2e6ac4a3597b
Type: security-commit

## Details
Fix a reentrant deadlock of getting traces.

## Patch
### core/src/block_data_manager/mod.rs
```diff
@@ -462,23 +462,24 @@ impl BlockDataManager {
     /// Get the traces for a single block without checking the assumed pivot
     /// block
     pub fn block_traces_by_hash(&self, hash: &H256) -> Option<BlockExecTraces> {
-        let maybe_traces = self
+        let maybe_traces_in_mem = self
             .block_traces
             .read()
             .get(hash)
-            .and_then(|traces_info| traces_info.get_current_data())
-            .or_else(|| {
-                self.db_manager.block_traces_from_db(hash).map(
-                    |DataVersionTuple(pivot, traces)| {
-                        self.block_traces
-                            .write()
-                            .entry(*hash)
-                            .or_insert(BlockTracesInfo::default())
-                            .insert_data(&pivot, traces.clone());
-                        traces
-                    },
-                )
-            });
+            .and_then(|traces_info| traces_info.get_current_data());
+        // Make sure the ReadLock of `block_traces` is dropped here.
+        let maybe_traces = maybe_traces_in_mem.or_else(|| {
+            self.db_manager.block_traces_from_db(hash).map(
+                |DataVersionTuple(pivot, traces)| {
+                    self.block_traces
+                        .write()
+                        .entry(*hash)
+                        .or_insert(BlockTracesInfo::default())
+                        .insert_data(&pivot, traces.clone());
+                    traces
+                },
+            )
+        });
         if maybe_traces.is_some() {
             self.cache_man.lock().note_used(CacheId::BlockTraces(*hash));
         }
```
