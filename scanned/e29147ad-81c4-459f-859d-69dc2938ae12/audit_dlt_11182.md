# [?] fix: panic in `PartialMmr::untrack` (#382)

## Summary
Severity: Unknown
Chain: Miden
Component: 0xMiden/miden-vm
Published: 2025-02-18
Source: https://github.com/0xMiden/miden-vm/commit/535637d7fb689d0c0aedf411639684746f0c5e1f
Type: security-commit

## Details
fix: panic in `PartialMmr::untrack` (#382)

## Patch
### CHANGELOG.md
```diff
@@ -1,6 +1,7 @@
 ## 0.13.3 (tbd)
 
 - Implement `PartialSmt` (#372, #381).
+- Fix panic in `PartialMmr::untrack` (#382).
 
 ## 0.13.2 (2025-01-24)
 
```

### src/merkle/mmr/partial.rs
```diff
@@ -341,16 +341,13 @@ impl PartialMmr {
     pub fn untrack(&mut self, leaf_pos: usize) {
         let mut idx = InOrderIndex::from_leaf_pos(leaf_pos);
 
-        self.nodes.remove(&idx.sibling());
-
         // `idx` represent the element that can be computed by the authentication path, because
         // these elements can be computed they are not saved for the authentication of the current
         // target. In other words, if the idx is present it was added for the authentication of
         // another element, and no more elements should be removed otherwise it would remove that
         // element's authentication data.
-        while !self.nodes.contains_key(&idx) {
+        while self.nodes.remove(&idx.sibling()).is_some() && !self.nodes.contains_key(&idx) {
             idx = idx.parent();
-            self.nodes.remove(&idx.sibling());
         }
     }
 
@@ -949,4 +946,32 @@ mod tests {
 
         assert_eq!(partial_mmr, decoded);
     }
+
+    #[test]
+    fn test_partial_mmr_untrack() {
+        // build the MMR
+        let mmr: Mmr = LEAVES.into();
+
+        // get path and node for position 1
+        let node1 = mmr.get(1).unwrap();
+        let proof1 = mmr.open(1).unwrap();
+
+        // get path and node for position 2
+        let node2 = mmr.get(2).unwrap();
+        let proof2 = mmr.open(2).unwrap();
+
+        // create partial MMR and add authentication path to nodes at position 1 and 2
+        let mut partial_mmr: PartialMmr = mmr.peaks().into();
+        partial_mmr.track(1, node1, &proof1.merkle_path).unwrap();
+        partial_mmr.track(2, node2, &proof2.merkle_path).unwrap();
+
+        // untrack nodes at positions 1 and 2
+        partial_mmr.untrack(1);
+        partial_mmr.untrack(2);
+
+        // nodes should not longer be tracked
+        assert!(!partial_mmr.is_tracked(1));
+        assert!(!partial_mmr.is_tracked(2));
+        assert_eq!(partial_mmr.nodes().count(), 0);
+    }
 }
```
