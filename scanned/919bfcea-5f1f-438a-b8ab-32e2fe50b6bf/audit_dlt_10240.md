# [?] Fix overflow

## Summary
Severity: Unknown
Chain: Phala
Component: Phala-Network/phala-blockchain
Published: 2022-12-01
Source: https://github.com/Phala-Network/phala-blockchain/commit/c25fc97c27ad60b89984183a48e5ad9d2f8589ab
Type: security-commit

## Details
Fix overflow

## Patch
### standalone/pherry/src/lib.rs
```diff
@@ -495,10 +495,11 @@ async fn batch_sync_block(
     let mut synced_blocks: BlockNumber = 0;
 
     let hdr_synced_to = if parachain {
-        next_para_headernum - 1
+        next_para_headernum
     } else {
-        next_headernum - 1
-    };
+        next_headernum
+    }
+    .saturating_sub(1);
     macro_rules! sync_blocks_to {
         ($to: expr) => {
             if next_blocknum <= $to {
```
