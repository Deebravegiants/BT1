# [?] fix(trie): avoid boundary parent unwrap panic in parallel sparse reveal (#23171)

## Summary
Severity: Unknown
Chain: Ethereum
Component: paradigmxyz/reth
Published: 2026-03-25
Source: https://github.com/paradigmxyz/reth/commit/80094e1bda876c3f45895af84fa37498ea1c2fe3
Type: security-commit

## Details
fix(trie): avoid boundary parent unwrap panic in parallel sparse reveal (#23171)

## Patch
### .changelog/tidy-ducks-bake.md
```diff
@@ -0,0 +1,5 @@
+---
+reth-trie-sparse: patch
+---
+
+Fixed a panic in `ParallelSparseTrie::reveal_nodes` when a boundary node's upper parent is absent or non-branch (e.g. when an upper extension crosses the boundary). The code now skips gracefully instead of unwrapping. Added a regression test covering this case.
```

### crates/trie/sparse/src/parallel.rs
```diff
@@ -253,27 +253,31 @@ impl SparseTrie for ParallelSparseTrie {
 
         let reachable_subtries = self.reachable_subtries();
 
-        // For boundary nodes that are blinded in upper subtrie, unset the blinded bit and remember
-        // the hash to pass into `reveal_node`.
+        // Best-effort for boundary nodes: if the parent upper node exists as a branch and the
+        // boundary child is still blinded, unset that blinded bit and carry the hash into
+        // `reveal_node`. If the parent path is absent/non-branch (for example upper extension
+        // crossing the boundary), skip without failing.
         let hashes_from_upper = nodes
             .iter()
             .filter_map(|node| {
-                if node.path.len() == UPPER_TRIE_MAX_DEPTH &&
-                    reachable_subtries.get(path_subtrie_index_unchecked(&node.path)) &&
-                    let SparseNode::Branch { blinded_mask, blinded_hashes, .. } = self
-                        .upper_subtrie
-                        .nodes
-                        .get_mut(&node.path.slice(0..UPPER_TRIE_MAX_DEPTH - 1))
-                        .unwrap()
+                if node.path.len() != UPPER_TRIE_MAX_DEPTH ||
+                    !reachable_subtries.get(path_subtrie_index_unchecked(&node.path))
                 {
-                    let nibble = node.path.last().unwrap();
-                    blinded_mask.is_bit_set(nibble).then(|| {
-                        blinded_mask.unset_bit(nibble);
-                        (node.path, blinded_hashes[nibble as usize])
-                    })
-                } else {
-                    None
+                    return None;
                 }
+
+                let parent_path = node.path.slice(0..UPPER_TRIE_MAX_DEPTH - 1);
+                let Some(SparseNode::Branch { blinded_mask, blinded_hashes, .. }) =
+                    self.upper_subtrie.nodes.get_mut(&parent_path)
+                else {
+                    return None;
+                };
+
+                let nibble = node.path.last().unwrap();
+                blinded_mask.is_bit_set(nibble).then(|| {
+                    blinded_mask.unset_bit(nibble);
+                    (node.path, blinded_hashes[nibble as usize])
+                })
             })
             .collect::<HashMap<_, _>>();
 
```

### crates/trie/sparse/tests/suite/main.rs
```diff
@@ -238,6 +238,7 @@ sparse_trie_tests! {
     test_reveal_nodes_with_branch_masks,
     test_reveal_nodes_skips_on_empty_root,
     test_reveal_nodes_filters_unreachable_boundary_leaves,
+    test_reveal_boundary_node_with_missing_upper_parent_branch,
     test_reveal_insert_reveal_preserves_branch_state,
     test_remove_then_reveal_does_not_overwrite_collapsed_node,
     test_insert_then_reveal_does_not_overwrite_branch,
```

### crates/trie/sparse/tests/suite/reveal_nodes.rs
```diff
@@ -1,4 +1,6 @@
 use super::*;
+use alloy_trie::{nodes::BranchNodeRef, TrieMask};
+use reth_trie_common::{BranchNodeV2, RlpNode};
 
 /// Empty slice is a no-op.
 ///
@@ -385,3 +387,46 @@ pub(super) fn test_insert_then_reveal_does_not_overwrite_branch<T: SparseTrie>(
         "root should match 3-key reference after insert + stale reveal"
     );
 }
+
+/// Boundary reveal should not assume an upper parent branch exists.
+///
+/// When root is an extension that crosses the upper/lower boundary, a boundary node path can be
+/// reachable even if there is no explicit upper branch at `path[..UPPER_TRIE_MAX_DEPTH - 1]`.
+/// Revealing such a node should not panic.
+pub(super) fn test_reveal_boundary_node_with_missing_upper_parent_branch<T: SparseTrie>(
+    new_trie: fn() -> T,
+) {
+    // Root reveals as extension [0x1, 0x2] with a branch below it at path 0x12.
+    // Use two children so the branch shape is canonical.
+    let child_hash_0 = RlpNode::word_rlp(&B256::repeat_byte(0xAA));
+    let child_hash_1 = RlpNode::word_rlp(&B256::repeat_byte(0xBB));
+    let state_mask = TrieMask::new(0b0011);
+    let branch_rlp = RlpNode::from_rlp(&alloy_rlp::encode(BranchNodeRef::new(
+        &[child_hash_0.clone(), child_hash_1.clone()],
+        state_mask,
+    )));
+    let root = TrieNodeV2::Branch(BranchNodeV2::new(
+        Nibbles::from_nibbles([0x1, 0x2]),
+        vec![child_hash_0, child_hash_1],
+        state_mask,
+        Some(branch_rlp),
+    ));
+
+    let mut trie = (new_trie)();
+    trie.set_root(root, None, false).expect("set_root should succeed");
+
+    // Before the fix this panicked at `hashes_from_upper` when trying to unwrap
+    // `upper_subtrie.nodes.get_mut([0x1])`.
+    //
+    // In this shape, 0x12 is the lower branch root path and 0x120/0x121 are its children.
+    // The missing entry is the upper parent at [0x1], which the old code incorrectly unwrapped.
+    let boundary_path = Nibbles::from_nibbles([0x1, 0x2]);
+    let leaf =
+        TrieNodeV2::Leaf(reth_trie_common::LeafNode::new(Nibbles::from_nibbles([0x3]), vec![0x01]));
+    trie.reveal_nodes(&mut [reth_trie_common::ProofTrieNodeV2 {
+        path: boundary_path,
+        node: leaf,
+        masks: None,
+    }])
+    .expect("boundary reveal should not panic");
+}
```
