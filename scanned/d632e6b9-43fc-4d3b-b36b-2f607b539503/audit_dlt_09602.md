# [?] Fix a crash caused by invalid blocks. (#1469)

## Summary
Severity: Unknown
Chain: Conflux
Component: Conflux-Chain/conflux-rust
Published: 2020-05-22
Source: https://github.com/Conflux-Chain/conflux-rust/commit/92560e085004e1af3f2c9b7636a92e2e7dd9be1a
Type: security-commit

## Details
Fix a crash caused by invalid blocks. (#1469)

## Patch
### core/src/sync/synchronization_graph.rs
```diff
@@ -1904,7 +1904,9 @@ impl SynchronizationGraph {
             block.size(),
         );
 
-        if inner.arena[me].graph_status == BLOCK_INVALID {
+        // Note: If `me` is invalid, it has been removed from `arena` now,
+        // so we cannot access its `graph_status`.
+        if invalid_set.contains(&me) {
             BlockInsertionResult::Invalid
         } else if inner.arena[me].graph_status >= BLOCK_HEADER_GRAPH_READY {
             BlockInsertionResult::ShouldRelay
```
