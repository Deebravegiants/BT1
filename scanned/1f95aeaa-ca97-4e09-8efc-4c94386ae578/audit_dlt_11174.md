# [?] fix: replace panic/expect with proper error returns in with_entries and compute_mutations (#555)

## Summary
Severity: Unknown
Chain: Miden
Component: 0xMiden/miden-vm
Published: 2025-10-19
Source: https://github.com/0xMiden/miden-vm/commit/1c1fed7f12983f391c0dc3d05e0cb30e467573e5
Type: security-commit

## Details
fix: replace panic/expect with proper error returns in with_entries and compute_mutations (#555)

## Patch
### miden-crypto/src/merkle/smt/large/mod.rs
```diff
@@ -291,7 +291,10 @@ impl<S: SmtStorage> LargeSmt<S> {
         let entries: Vec<(Word, Word)> = entries.into_iter().collect();
 
         if storage.has_leaves()? {
-            panic!("Cannot create SMT with non-empty storage");
+            return Err(StorageError::Unsupported(
+                "Cannot create SMT with non-empty storage".into(),
+            )
+            .into());
         }
         let mut tree = LargeSmt::new(storage)?;
         if entries.is_empty() {
@@ -463,8 +466,7 @@ impl<S: SmtStorage> LargeSmt<S> {
         leaf_indices.sort_unstable();
 
         // Get leaves from storage
-        let leaves_from_storage =
-            self.storage.get_leaves(&leaf_indices).expect("Failed to get leaves");
+        let leaves_from_storage = self.storage.get_leaves(&leaf_indices)?;
 
         // Map leaf indices to their corresponding leaves
         let leaf_map: Map<u64, SmtLeaf> = leaf_indices
```
