# [?] fix query overflow: don't subtract one when height is zero

## Summary
Severity: Unknown
Chain: Penumbra
Component: penumbra-zone/penumbra
Published: 2023-07-21
Source: https://github.com/penumbra-zone/penumbra/commit/8d561b120e5850db703d90b1b65630bf126be487
Type: security-commit

## Details
fix query overflow: don't subtract one when height is zero

## Patch
### crates/bin/pd/src/info.rs
```diff
@@ -99,7 +99,8 @@ impl Info {
             //
             // Try to do this behavior by querying at height = latest-1.
             0 => {
-                let height = self.storage.latest_snapshot().version() - 1;
+                let version = self.storage.latest_snapshot().version();
+                let height = if version == 0 { version } else { version - 1 }
                 let snapshot = self
                     .storage
                     .snapshot(height)
```
