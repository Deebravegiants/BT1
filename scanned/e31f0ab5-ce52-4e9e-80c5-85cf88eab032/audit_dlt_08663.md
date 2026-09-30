# [?] Add missing check and protect from overflow.

## Summary
Severity: Unknown
Chain: Aleo
Component: AleoNet/snarkOS-test
Published: 2025-03-12
Source: https://github.com/AleoNet/snarkOS-test/commit/27575e79c63cf6ffb9d215d629d163415f5d4b07
Type: security-commit

## Details
Add missing check and protect from overflow.

## Patch
### node/sync/locators/src/block_locators.rs
```diff
@@ -195,13 +195,19 @@ impl<N: Network> BlockLocators<N> {
 
         // Ensure that `last_checkpoint_height` is
         // the largest multiple of `CHECKPOINT_INTERVAL` that does not exceed `last_recent_height`.
-        // That is, `last_checkpoint_height + CHECKPOINT_INTERVAL`
-        // must be greater than `last_recent_height`.
-        // We do not worry about this addition overflowing,
-        // because our use of `u32` for block heights implies that we do not expect to run out.
-        if last_checkpoint_height + CHECKPOINT_INTERVAL <= last_recent_height {
+        // That is, we must have
+        // `last_checkpoint_height <= last_recent_height < last_checkpoint_height + CHECKPOINT_INTERVAL`.
+        // Although we do not expect to run out of `u32` for block heights,
+        // `last_checkpoint_height` is an untrusted value that may come from a faulty validator,
+        // and thus we use a saturating addition;
+        // only a faulty validator would send block locators with such high block heights,
+        // under the assumption that the blockchain is always well below the `u32` limit for heights.
+        if !(last_checkpoint_height..last_checkpoint_height.saturating_add(CHECKPOINT_INTERVAL))
+            .contains(&last_recent_height)
+        {
             bail!(
-                "Last checkpoint height ({last_checkpoint_height}) is too small for last recent height ({last_recent_height})"
+                "Last checkpoint height ({last_checkpoint_height}) is not the largest multiple of ".to_string()
+                    + "{CHECKPOINT_INTERVAL} that does not exceed the last recent height ({last_recent_height})"
             )
         }
 
```
