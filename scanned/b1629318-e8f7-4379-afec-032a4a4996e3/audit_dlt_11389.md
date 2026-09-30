# [?] Merkle tree panics when there's a single leaf - fix

## Summary
Severity: Unknown
Chain: ZK
Component: arkworks-rs/snark
Published: 2020-04-27
Source: https://github.com/arkworks-rs/snark/commit/0809ed4e59bb659eb444fcb831386b1baa2ba41c
Type: security-commit

## Details
Merkle tree panics when there's a single leaf - fix

## Patch
### crypto-primitives/src/merkle_tree/mod.rs
```diff
@@ -268,6 +268,10 @@ fn log2(number: usize) -> usize {
 /// Returns the height of the tree, given the size of the tree.
 #[inline]
 fn tree_height(tree_size: usize) -> usize {
+    if tree_size == 1 {
+        return 1;
+    }
+
     log2(tree_size)
 }
 
```
