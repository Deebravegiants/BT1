# [?] Fix stack overflows due to recursion in `Forest::find` (#358)

## Summary
Severity: Unknown
Chain: ZK
Component: 0xPolygonZero/plonky2
Published: 2021-11-15
Source: https://github.com/0xPolygonZero/plonky2/commit/9aafa447f87d04254cc9efa0e6c00665a15dd4cd
Type: security-commit

## Details
Fix stack overflows due to recursion in `Forest::find` (#358)

## Patch
### src/plonk/permutation_argument.rs
```diff
@@ -45,15 +45,23 @@ impl Forest {
     }
 
     /// Path compression method, see https://en.wikipedia.org/wiki/Disjoint-set_data_structure#Finding_set_representatives.
-    pub fn find(&mut self, x_index: usize) -> usize {
-        let x_parent = self.parents[x_index];
-        if x_parent != x_index {
-            let root_index = self.find(x_parent);
-            self.parents[x_index] = root_index;
-            root_index
-        } else {
-            x_index
+    pub fn find(&mut self, mut x_index: usize) -> usize {
+        // Note: We avoid recursion here since the chains can be long, causing stack overflows.
+
+        // First, find the representative of the set containing `x_index`.
+        let mut representative = x_index;
+        while self.parents[representative] != representative {
+            representative = self.parents[representative];
+        }
+
+        // Then, update each node in this chain to point directly to the representative.
+        while self.parents[x_index] != x_index {
+            let old_parent = self.parents[x_index];
+            self.parents[x_index] = representative;
+            x_index = old_parent;
         }
+
+        representative
     }
 
     /// Merge two sets.
```
