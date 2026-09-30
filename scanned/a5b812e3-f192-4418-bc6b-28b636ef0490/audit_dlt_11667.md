# [?] Merge bitcoindevkit/bdk#2180: fix(chain): prevent integer overflow in `SpkIterator::new_with_range`

## Summary
Severity: Unknown
Chain: Bitcoin
Component: bitcoindevkit/bdk
Published: 2026-04-23
Source: https://github.com/bitcoindevkit/bdk/commit/10d9333ab34a0c10912c732958a48b6269924e91
Type: security-commit

## Details
Merge bitcoindevkit/bdk#2180: fix(chain): prevent integer overflow in `SpkIterator::new_with_range`

b340e96f0221f6c3088fe5daf2b87c56b3bf4010 fix(chain): prevent integer overflow in `SpkIterator::new_with_range` (Elias Rohrer)

Pull request description:

  ### Description

  The start and end bound calculations used unchecked addition which
  overflows when given `u32::MAX`, causing the iterator to silently produce
  wrong results (e.g., an empty iterator for `0..=u32::MAX` in release
  mode). Use `saturating_add` to handle the boundary correctly.

  ### Checklists

  #### All Submissions:

  * [x] I followed the [contribution guidelines](https://github.com/bitcoindevkit/bdk/blob/master/CONTRIBUTING.md)

  #### Bugfixes:

  * [ ] This pull request breaks the existing API
  * [x] I've added tests to reproduce the issue which are now passing
  * [ ] I'm linking the issue being fixed by this PR

ACKs for top commit:
  luisschwab:
    ACK b340e96f0221f6c3088fe5daf2b87c56b3bf4010

Tree-SHA512: f28ebcdb8f8b269d64c4d7bb4e38e8fcdc85864c35b0c287bc0d41d740d6b78bd2491533585f85805cc4f1c63ce4024c677081e7fa283f8f1ad0e18d0728d44f

## Patch
### crates/chain/src/spk_iter.rs
```diff
@@ -67,12 +67,12 @@ where
     {
         let start = match range.start_bound() {
             Bound::Included(start) => *start,
-            Bound::Excluded(start) => *start + 1,
+            Bound::Excluded(start) => start.saturating_add(1),
             Bound::Unbounded => u32::MIN,
         };
 
         let mut end = match range.end_bound() {
-            Bound::Included(end) => *end + 1,
+            Bound::Included(end) => end.saturating_add(1),
             Bound::Excluded(end) => *end,
             Bound::Unbounded => u32::MAX,
         };
@@ -136,6 +136,8 @@ where
 #[cfg(test)]
 #[cfg_attr(coverage_nightly, coverage(off))]
 mod test {
+    use core::ops::Bound;
+
     use crate::{
         bitcoin::secp256k1::Secp256k1,
         indexer::keychain_txout::KeychainTxOutIndex,
@@ -264,6 +266,31 @@ mod test {
             None
         );
     }
+
+    #[test]
+    fn test_spkiterator_no_overflow_on_u32_max_range() {
+        let (_, external_desc, _) = init_txout_index();
+
+        // Inclusive range up to u32::MAX should not overflow and should produce items
+        // (clamped to BIP32_MAX_INDEX).
+        let mut iter = SpkIterator::new_with_range(&external_desc, 0..=u32::MAX);
+        assert!(
+            iter.next().is_some(),
+            "0..=u32::MAX range should produce items, not overflow to empty"
+        );
+
+        // Exclusive start at u32::MAX should not overflow and should produce an empty iterator
+        // (start saturates to u32::MAX which is beyond BIP32_MAX_INDEX).
+        let mut iter = SpkIterator::new_with_range(
+            &external_desc,
+            (Bound::Excluded(u32::MAX), Bound::Included(u32::MAX)),
+        );
+        assert_eq!(
+            iter.next(),
+            None,
+            "range starting after u32::MAX should be empty"
+        );
+    }
 }
 
 #[test]
```
