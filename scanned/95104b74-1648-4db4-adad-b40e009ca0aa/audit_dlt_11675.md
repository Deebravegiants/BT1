# [?] [wallet] Fix potential overflow when adding block heights

## Summary
Severity: Unknown
Chain: Bitcoin
Component: bitcoindevkit/bdk
Published: 2020-05-08
Source: https://github.com/bitcoindevkit/bdk/commit/0e432f3b26fe98a1304f81dc1c3106a088b78b29
Type: security-commit

## Details
[wallet] Fix potential overflow when adding block heights

## Patch
### src/psbt/mod.rs
```diff
@@ -100,7 +100,7 @@ impl<'a> Satisfier<bitcoin::PublicKey> for PSBTSatisfier<'a> {
 
         if let Some(current_height) = self.current_height {
             // TODO: test >= / >
-            current_height >= self.create_height.unwrap_or(0) + height
+            current_height as u64 >= self.create_height.unwrap_or(0) as u64 + height as u64
         } else {
             self.assume_height_reached
         }
```
