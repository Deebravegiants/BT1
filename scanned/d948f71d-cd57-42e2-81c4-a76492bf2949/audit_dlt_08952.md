# [?] Protect against underflow in relayer (#1508)

## Summary
Severity: Unknown
Chain: Hyperlane
Component: hyperlane-xyz/hyperlane-monorepo
Published: 2023-01-05
Source: https://github.com/hyperlane-xyz/hyperlane-monorepo/commit/eb3550ad397dc6d08f9c5947d68aa75828269ae7
Type: security-commit

## Details
Protect against underflow in relayer (#1508)

## Patch
### rust/hyperlane-base/src/types/multisig.rs
```diff
@@ -62,14 +62,16 @@ impl MultisigCheckpointSyncer {
             // The highest viable checkpoint index is the minimum of the highest index
             // we (supposedly) have a quorum for, and the maximum index for which we can
             // generate a proof.
-            let mut index = std::cmp::min(*highest_quorum_index, maximum_index);
-            while index >= minimum_index {
+            let start_index = highest_quorum_index.min(&maximum_index);
+            if minimum_index > *start_index {
+                return Ok(None);
+            }
+            for index in (minimum_index..=*start_index).rev() {
                 if let Ok(Some(checkpoint)) =
                     self.fetch_checkpoint(index, validators, threshold).await
                 {
                     return Ok(Some(checkpoint));
                 }
-                index -= 1;
             }
         }
         Ok(None)
```
