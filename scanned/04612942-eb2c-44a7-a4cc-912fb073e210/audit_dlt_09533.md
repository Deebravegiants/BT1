# [?] Merge pull request #3574 from peilun-conflux/fix/slab-remove-oob-bound

## Summary
Severity: Unknown
Chain: Conflux
Component: Conflux-Chain/conflux-rust
Published: 2026-07-23
Source: https://github.com/Conflux-Chain/conflux-rust/commit/3ae53568793311a0cbb1d0fb80adfec1f415097e
Type: security-commit

## Details
Merge pull request #3574 from peilun-conflux/fix/slab-remove-oob-bound

fix(storage): out-of-bounds unchecked access in Slab::remove bound check

## Patch
### crates/dbs/storage/src/impls/delta_mpt/slab/mod.rs
```diff
@@ -846,7 +846,7 @@ impl<T, E: EntryTrait<EntryType = T>> Slab<T, E> {
     /// assert_eq!(slab.remove(hello), "hello");
     /// assert!(!slab.contains(hello));
     pub fn remove(&self, key: usize) -> Result<T> {
-        if key > self.entries.len() {
+        if key >= self.entries.len() {
             // Index out of range.
             return Err(Error::SlabKeyError);
         }
@@ -1024,3 +1024,29 @@ impl<'a, T, E: EntryTrait<EntryType = T>> Iterator for IterMut<'a, T, E> {
         None
     }
 }
+
+#[cfg(test)]
+mod tests {
+    use super::*;
+
+    // `entries` is kept filled to capacity, so `capacity()` is exactly the
+    // first out-of-bounds key; an off-by-one bound check in `remove` turns
+    // it into a one-past-the-end unchecked access.
+    #[test]
+    fn remove_key_at_capacity_is_rejected() {
+        let slab: Slab<u32> = Slab::with_capacity(10);
+        slab.insert(1).unwrap();
+        assert!(matches!(
+            slab.remove(slab.capacity()),
+            Err(Error::SlabKeyError)
+        ));
+    }
+
+    // Zero-capacity slab: entries' buffer is unallocated, so key 0 must
+    // already be rejected by the bound check.
+    #[test]
+    fn remove_from_empty_slab_is_rejected() {
+        let empty: Slab<u32> = Slab::default();
+        assert!(matches!(empty.remove(0), Err(Error::SlabKeyError)));
+    }
+}
```
