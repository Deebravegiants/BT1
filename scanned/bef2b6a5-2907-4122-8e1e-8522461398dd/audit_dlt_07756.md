# [?] fix(trie): do not panic when logging the current hash of `TrieWalker` (#16222)

## Summary
Severity: Unknown
Chain: Ethereum
Component: paradigmxyz/reth
Published: 2025-05-14
Source: https://github.com/paradigmxyz/reth/commit/6c188475fc8bd0159b8a82ce940f33ba1909f2a1
Type: security-commit

## Details
fix(trie): do not panic when logging the current hash of `TrieWalker` (#16222)

## Patch
### crates/trie/trie/src/node_iter.rs
```diff
@@ -281,7 +281,7 @@ where
                         trace!(
                             target: "trie::node_iter",
                             ?seek_key,
-                            walker_hash = ?self.walker.hash(),
+                            walker_hash = ?self.walker.maybe_hash(),
                             "skipping hashed seek"
                         );
 
```

### crates/trie/trie/src/trie_cursor/subnode.rs
```diff
@@ -158,7 +158,7 @@ impl CursorSubNode {
     ///
     /// Differs from [`Self::hash`] in that it returns `None` if the subnode is positioned at the
     /// child without a hash mask bit set. [`Self::hash`] panics in that case.
-    fn maybe_hash(&self) -> Option<B256> {
+    pub fn maybe_hash(&self) -> Option<B256> {
         self.node.as_ref().and_then(|node| match self.position {
             // Get the root hash for the parent branch node
             SubNodePosition::ParentBranch => node.root_hash,
```

### crates/trie/trie/src/walker.rs
```diff
@@ -117,11 +117,19 @@ impl<C> TrieWalker<C> {
         self.stack.last().map(|n| n.full_key())
     }
 
-    /// Returns the current hash in the trie if any.
+    /// Returns the current hash in the trie, if any.
     pub fn hash(&self) -> Option<B256> {
         self.stack.last().and_then(|n| n.hash())
     }
 
+    /// Returns the current hash in the trie, if any.
+    ///
+    /// Differs from [`Self::hash`] in that it returns `None` if the subnode is positioned at the
+    /// child without a hash mask bit set. [`Self::hash`] panics in that case.
+    pub fn maybe_hash(&self) -> Option<B256> {
+        self.stack.last().and_then(|n| n.maybe_hash())
+    }
+
     /// Indicates whether the children of the current node are present in the trie.
     pub fn children_are_in_trie(&self) -> bool {
         self.stack.last().is_some_and(|n| n.tree_flag())
```
