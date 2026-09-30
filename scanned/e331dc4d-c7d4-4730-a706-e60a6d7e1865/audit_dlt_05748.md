# [?] [execution] Fix non-deterministic hot state promotions

## Summary
Severity: Unknown
Chain: Aptos
Component: aptos-labs/aptos-core
Published: 2026-06-11
Source: https://github.com/aptos-labs/aptos-core/commit/69fe58b6494cf22608a5055cb67bd87de1ea937b
Type: security-commit

## Details
[execution] Fix non-deterministic hot state promotions

`BlockHotStateOpAccumulator` capped promotions at `MAX_PROMOTIONS_PER_BLOCK`
while accumulating reads, dropping any key first seen after the cap was hit.
The per-transaction read set is a `HashSet`, so its iteration order — and
hence *which* keys survived the cap — differed across processes. Two
validators executing the same block could therefore promote different keys to
the hot state in the block epilogue and diverge.

Instead, accumulate every eligible key and apply the cap only when the
promotions are materialized, keeping the smallest keys via the ordered
`BTreeSet`. The retained subset is now a deterministic function of the
block's reads, regardless of the order they were observed.

While here, rename the drop counter to `promotions_dropped_over_cap` and have
it record how many keys were dropped rather than only that the cap was hit, so
the metric reflects how far over the cap a block ran.

## Patch
### aptos-move/block-executor/src/hot_state_op_accumulator.rs
```diff
@@ -10,7 +10,7 @@ use std::{collections::BTreeSet, fmt::Debug, hash::Hash};
 pub struct BlockHotStateOpAccumulator<Key> {
     /// Keys read but never written to across the entire block are to be made hot (or refreshed
     /// `hot_since_version` one is already hot but last refresh is far in the history) as the side
-    /// effect of the block epilogue (subject to per block limit)
+    /// effect of the block epilogue.
     to_make_hot: BTreeSet<Key>,
     /// Keep track of all the keys that are written to across the whole block, these keys are made
     /// hot (or have a refreshed `hot_since_version`) immediately at the version they got changed,
@@ -24,7 +24,8 @@ impl<Key> BlockHotStateOpAccumulator<Key>
 where
     Key: PartialOrd + Ord + Send + Sync + Clone + Hash + Eq + Debug,
 {
-    /// TODO(HotState): make on-chain config
+    /// TODO(HotState): make on-chain config. Also consider capping by total key size instead of
+    /// number.
     const MAX_PROMOTIONS_PER_BLOCK: usize = 1024 * 10;
 
     pub fn new() -> Self {
@@ -54,10 +55,6 @@ where
         }
 
         for key in reads {
-            if self.to_make_hot.len() >= self.max_promotions_per_block {
-                COUNTER.inc_with(&["max_promotions_per_block_hit"]);
-                continue;
-            }
             if self.writes.contains(key) {
                 continue;
             }
@@ -66,6 +63,73 @@ where
     }
 
     pub fn get_keys_to_make_hot(&self) -> BTreeSet<Key> {
-        self.to_make_hot.clone()
+        let num_eligible = self.to_make_hot.len();
+        if num_eligible > self.max_promotions_per_block {
+            COUNTER.inc_with_by(
+                &["promotions_dropped_over_cap"],
+                (num_eligible - self.max_promotions_per_block) as u64,
+            );
+        }
+        self.to_make_hot
+            .iter()
+            .take(self.max_promotions_per_block)
+            .cloned()
+            .collect()
+    }
+}
+
+#[cfg(test)]
+mod tests {
+    use super::*;
+
+    fn read(accu: &mut BlockHotStateOpAccumulator<u64>, keys: &[u64]) {
+        accu.add_transaction(std::iter::empty(), keys.iter());
+    }
+
+    fn write(accu: &mut BlockHotStateOpAccumulator<u64>, keys: &[u64]) {
+        accu.add_transaction(keys.iter(), std::iter::empty());
+    }
+
+    fn set(keys: &[u64]) -> BTreeSet<u64> {
+        keys.iter().copied().collect()
+    }
+
+    /// When more keys are eligible than the cap allows, the surviving subset must be the same
+    /// regardless of the order reads are observed in (the bug being that HashSet-ordered reads
+    /// made the dropped subset process-dependent).
+    #[test]
+    fn cap_selects_smallest_keys_independent_of_order() {
+        let mut forward = BlockHotStateOpAccumulator::<u64>::new_with_config(3);
+        for k in 0..10 {
+            read(&mut forward, &[k]);
+        }
+
+        let mut reverse = BlockHotStateOpAccumulator::<u64>::new_with_config(3);
+        for k in (0..10).rev() {
+            read(&mut reverse, &[k]);
+        }
+
+        let expected = set(&[0, 1, 2]);
+        assert_eq!(forward.get_keys_to_make_hot(), expected);
+        assert_eq!(reverse.get_keys_to_make_hot(), expected);
+    }
+
+    #[test]
+    fn written_keys_are_not_promoted() {
+        let mut accu = BlockHotStateOpAccumulator::<u64>::new_with_config(100);
+        // 2 is read and written in the same txn; the write makes it hot, so it must not also be
+        // promoted by the epilogue.
+        accu.add_transaction([2u64].iter(), [1u64, 2, 3].iter());
+        // A read of an already-written key in a later txn is likewise ignored.
+        read(&mut accu, &[2]);
+        assert_eq!(accu.get_keys_to_make_hot(), set(&[1, 3]));
+    }
+
+    #[test]
+    fn write_after_read_removes_promotion() {
+        let mut accu = BlockHotStateOpAccumulator::<u64>::new_with_config(100);
+        read(&mut accu, &[1, 2]);
+        write(&mut accu, &[1]);
+        assert_eq!(accu.get_keys_to_make_hot(), set(&[2]));
     }
 }
```
