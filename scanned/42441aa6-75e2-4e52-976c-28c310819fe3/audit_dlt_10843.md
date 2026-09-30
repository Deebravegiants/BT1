# [?] fix: panic when duplicate block is found during replay

## Summary
Severity: Unknown
Chain: Stacks
Component: stacks-network/stacks-core
Published: 2025-12-02
Source: https://github.com/stacks-network/stacks-core/commit/2d50158e44ead128ad487505de22007fa78f1a6b
Type: security-commit

## Details
fix: panic when duplicate block is found during replay

## Patch
### contrib/stacks-inspect/src/lib.rs
```diff
@@ -253,7 +253,7 @@ fn collect_block_entries_for_selection(
     }) {
         let index_block_hash: String = row.get(0).unwrap();
         if !seen.insert(index_block_hash.clone()) {
-            continue;
+            panic!("Duplicate block found: {index_block_hash}");
         }
         entries.push(BlockScanEntry {
             index_block_hash,
@@ -274,7 +274,7 @@ fn collect_block_entries_for_selection(
     }) {
         let index_block_hash: String = row.get(0).unwrap();
         if !seen.insert(index_block_hash.clone()) {
-            continue;
+            panic!("Duplicate block found: {index_block_hash}");
         }
         entries.push(BlockScanEntry {
             index_block_hash,
```
