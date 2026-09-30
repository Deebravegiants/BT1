# [?] fix(sync/l1): prevent backward gap underflows in reorgs

## Summary
Severity: Unknown
Chain: Starknet
Component: software-mansion/pathfinder
Published: 2026-02-18
Source: https://github.com/software-mansion/pathfinder/commit/1fe9bff1934a11daa52da203154826ddc6860e6d
Type: security-commit

## Details
fix(sync/l1): prevent backward gap underflows in reorgs

## Patch
### crates/pathfinder/src/state/sync/l1.rs
```diff
@@ -176,6 +176,10 @@ async fn process_block(
             Ok(())
         }
         Err(AddSampleError::Gap { expected, actual }) => {
+            if actual < expected {
+                anyhow::bail!("Block number went backward: expected {expected}, got {actual}");
+            }
+
             let gap_size = actual.get() - expected.get();
 
             if gap_size > config.max_gap_blocks {
```
