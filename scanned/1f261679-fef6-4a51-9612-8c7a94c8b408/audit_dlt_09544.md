# [?] fix manifest panic on empty chunk_boundaries

## Summary
Severity: Unknown
Chain: Conflux
Component: Conflux-Chain/conflux-rust
Published: 2026-05-22
Source: https://github.com/Conflux-Chain/conflux-rust/commit/c22b3b686d7af5026695d3d4b0668023b7d9ad7a
Type: security-commit

## Details
fix manifest panic on empty chunk_boundaries

Replace unwrap() with match to avoid panic when validating a manifest
whose next is set but chunk_boundaries is empty.

## Patch
### crates/cfxcore/core/src/sync/state/storage.rs
```diff
@@ -180,10 +180,11 @@ impl RangedManifest {
             ));
         }
         if let Some(next) = &self.next {
-            if next != self.chunk_boundaries.last().unwrap() {
-                bail!(Error::InvalidSnapshotManifest(
+            match self.chunk_boundaries.last() {
+                Some(last) if next == last => (),
+                _ => bail!(Error::InvalidSnapshotManifest(
                     "next does not match last boundary".into(),
-                ));
+                )),
             }
         }
 
```
