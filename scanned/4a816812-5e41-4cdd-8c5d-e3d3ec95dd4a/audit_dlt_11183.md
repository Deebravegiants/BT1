# [?] fix: merkle store panics on bounds

## Summary
Severity: Unknown
Chain: Miden
Component: 0xMiden/miden-vm
Published: 2023-03-16
Source: https://github.com/0xMiden/miden-vm/commit/867b772d9a3f894ece86c629a2adcb78f5d41b05
Type: security-commit

## Details
fix: merkle store panics on bounds

Prior to this commit, the MerkleStore panicked under certain bounds. It
will prevent such panics by using checked operations.

ilog2, for instance, will panic when the operand is zero. However, there
is a documentation rule enforcing the merkle tree to be size at least 2.
If this rule is checked, then the panic is impossible.

## Patch
### src/bit.rs
```diff
@@ -19,7 +19,7 @@ impl BitIterator {
         let mask = bitmask(n);
         let ones = self.mask.trailing_ones();
         let mask_position = ones;
-        self.mask ^= mask << mask_position;
+        self.mask ^= mask.checked_shl(mask_position).unwrap_or(0);
         self
     }
 
@@ -31,7 +31,7 @@ impl BitIterator {
         let mask = bitmask(n);
         let ones = self.mask.leading_ones();
         let mask_position = u64::BITS - ones - n;
-        self.mask ^= mask << mask_position;
+        self.mask ^= mask.checked_shl(mask_position).unwrap_or(0);
         self
     }
 }
```

### src/merkle/mod.rs
```diff
@@ -35,7 +35,7 @@ pub use store::MerkleStore;
 // ERRORS
 // ================================================================================================
 
-#[derive(Clone, Debug)]
+#[derive(Clone, Debug, PartialEq, Eq)]
 pub enum MerkleError {
     ConflictingRoots(Vec<Word>),
     DepthTooSmall(u8),
```

### src/merkle/path_set.rs
```diff
@@ -57,6 +57,14 @@ impl MerklePathSet {
         self.total_depth
     }
 
+    /// Returns all the leaf indexes of this path set.
+    pub fn indexes(&self) -> impl Iterator<Item = NodeIndex> + '_ {
+        self.paths
+            .keys()
+            .copied()
+            .map(|index| NodeIndex::new(self.total_depth, index))
+    }
+
     /// Returns a node at the specified index.
     ///
     /// # Errors
```

### src/merkle/store.rs
```diff
@@ -4,8 +4,8 @@
 //! (leaves or internal) to live as long as necessary and without duplication, this allows the
 //! implementation of efficient persistent data structures
 use super::{
-    BTreeMap, BTreeSet, EmptySubtreeRoots, MerkleError, MerklePath, MerkleTree, NodeIndex, Rpo256,
-    RpoDigest, SimpleSmt, Vec, Word,
+    BTreeMap, BTreeSet, EmptySubtreeRoots, MerkleError, MerklePath, MerklePathSet, MerkleTree,
+    NodeIndex, Rpo256, RpoDigest, SimpleSmt, Vec, Word,
 };
 
 #[derive(Debug, Default, Copy, Clone, Eq, PartialEq)]
@@ -81,6 +81,51 @@ impl MerkleStore {
         Ok(self)
     }
 
+    // PUBLIC ACCESSORS
+    // --------------------------------------------------------------------------------------------
+
+    /// Returns the node at `index` rooted on the tree `root`.
+    ///
+    /// # Errors
+    ///
+    /// This will return `NodeNotInStorage` if the element is not present in the store.
+    pub fn get_node(&self, root: Word, index: NodeIndex) -> Result<Word, MerkleError> {
+        let mut hash: RpoDigest = root.into();
+
+        // Check the root is in the storage when called with `NodeIndex::root()`
+        self.nodes
+            .get(&hash)
+            .ok_or(MerkleError::NodeNotInStorage(hash.into(), index))?;
+
+        for bit in index.bit_iterator().rev() {
+            let node = self
+                .nodes
+                .get(&hash)
+                .ok_or(MerkleError::NodeNotInStorage(hash.into(), index))?;
+            hash = if bit { node.right } else { node.left }
+        }
+
+        Ok(hash.into())
+    }
+
+    /// Returns the path for the node at `index` rooted on the tree `root`.
+    ///
+    /// The path starts at the sibling of the target leaf.
+    ///
+    /// # Errors
+    ///
+    /// This will return `NodeNotInStorage` if the element is not present in the store.
+    pub fn get_path(&self, root: Word, mut index: NodeIndex) -> Result<MerklePath, MerkleError> {
+        let mut path = Vec::with_capacity(index.depth().saturating_sub(1) as usize);
+        while index.depth() > 0 {
+            let sibling = index.sibling();
+            index.move_up();
+            let node = self.get_node(root, sibling)?;
+            path.push(node);
+        }
+        Ok(MerklePath::new(path))
+    }
+
     // STATE MUTATORS
     // --------------------------------------------------------------------------------------------
 
@@ -99,6 +144,10 @@ impl MerkleStore {
         I: IntoIterator<Item = Word>,
     {
         let leaves: Vec<_> = leaves.into_iter().collect();
+        if leaves.len() < 2 {
+            return Err(MerkleError::DepthTooSmall(leaves.len() as u8));
+        }
+
         let layers = leaves.len().ilog2();
         let tree = MerkleTree::new(leaves)?;
 
@@ -225,74 +274,24 @@ impl MerkleStore {
         Ok(roots.iter().next().unwrap().into())
     }
 
-    // PUBLIC ACCESSORS
-    // --------------------------------------------------------------------------------------------
-
-    /// Returns the node at `index` rooted on the tree `root`.
-    ///
-    /// # Errors
-    ///
-    /// This will return `NodeNotInStorage` if the element is not present in the store.
-    pub fn get_node(&self, root: Word, index: NodeIndex) -> Result<Word, MerkleError> {
-        let mut hash: RpoDigest = root.into();
-
-        // Check the root is in the storage when called with `NodeIndex::root()`
-        self.nodes
-            .get(&hash)
-            .ok_or(MerkleError::NodeNotInStorage(hash.into(), index))?;
-
-        for bit in index.bit_iterator().rev() {
-            let node = self
-                .nodes
-                .get(&hash)
-                .ok_or(MerkleError::NodeNotInStorage(hash.into(), index))?;
-            hash = if bit { node.right } else { node.left }
-        }
-
-        Ok(hash.into())
-    }
-
-    /// Returns the path for the node at `index` rooted on the tree `root`.
-    ///
-    /// # Errors
-    ///
-    /// This will return `NodeNotInStorage` if the element is not present in the store.
-    pub fn get_path(
-        &self,
-        root: Word,
-        index: NodeIndex,
-    ) -> Result<(Word, MerklePath), MerkleError> {
-        let mut hash: RpoDigest = root.into();
-        let mut path = Vec::new();
-        let node = RpoDigest::default();
-        for bit in index.bit_iterator() {
-            let node = self
-                .nodes
-                .get(&hash)
-                .ok_or(MerkleError::NodeNotInStorage(hash.into(), index))?;
-
-            hash = if bit {
-                path.push(node.left.into());
-                node.right
-            } else {
-                path.push(node.right.into());
-                node.left
-            }
-        }
-
-        Ok((node.into(), MerklePath::new(path)))
+    /// Appends the provided [MerklePathSet] into the store.
+    pub fn add_merkle_path_set(&mut self, path_set: &MerklePathSet) -> Result<Word, MerkleError> {
+        let root = path_set.root();
+        path_set.indexes().try_fold(root, |_, index| {
+            let node = path_set.get_node(index)?;
+            let path = path_set.get_path(index)?;
+            self.add_merkle_path(index.value(), node, path)
+        })
     }
 
-    // DATA MUTATORS
-    // --------------------------------------------------------------------------------------------
-
     pub fn set_node(
         &mut self,
         root: Word,
         index: NodeIndex,
         value: Word,
     ) -> Result<Word, MerkleError> {
-        let (current_node, path) = self.get_path(root, index)?;
+        let current_node = self.get_node(root, index)?;
+        let path = self.get_path(root, index)?;
         if current_node != value {
             self.add_merkle_path(index.value(), value, path)
         } else {
@@ -331,9 +330,12 @@ impl MerkleStore {
 
 #[cfg(test)]
 mod test {
-    use super::{MerkleError, MerkleStore, MerkleTree, NodeIndex, SimpleSmt, Word};
-    use crate::merkle::int_to_node;
-    use crate::merkle::MerklePathSet;
+    use super::*;
+    use crate::{
+        hash::rpo::Rpo256,
+        merkle::{int_to_node, MerklePathSet},
+        Felt, Word,
+    };
 
     const KEYS4: [u64; 4] = [0, 1, 2, 3];
     const LEAVES4: [Word; 4] = [
@@ -494,4 +496,53 @@ mod test {
 
         Ok(())
     }
+
+    #[test]
+    fn wont_open_to_different_depth_root() {
+        let empty = EmptySubtreeRoots::empty_hashes(64);
+        let a = [Felt::new(1); 4];
+        let b = [Felt::new(2); 4];
+
+        // compute the root for a different depth
+        let mut root = Rpo256::merge(&[a.into(), b.into()]);
+        for depth in (1..=63).rev() {
+            root = Rpo256::merge(&[root, empty[depth]]);
+        }
+        let root = Word::from(root);
+
+        let store = MerkleStore::default().with_merkle_tree([a, b]).unwrap();
+        let index = NodeIndex::root();
+        let err = store.get_node(root, index).err().unwrap();
+        assert_eq!(err, MerkleError::NodeNotInStorage(root, index));
+    }
+
+    #[test]
+    fn store_path_opens_from_leaf() {
+        let a = [Felt::new(1); 4];
+        let b = [Felt::new(2); 4];
+        let c = [Felt::new(3); 4];
+        let d = [Felt::new(4); 4];
+        let e = [Felt::new(5); 4];
+        let f = [Felt::new(6); 4];
+        let g = [Felt::new(7); 4];
+        let h = [Felt::new(8); 4];
+
+        let i = Rpo256::merge(&[a.into(), b.into()]);
+        let j = Rpo256::merge(&[c.into(), d.into()]);
+        let k = Rpo256::merge(&[e.into(), f.into()]);
+        let l = Rpo256::merge(&[g.into(), h.into()]);
+
+        let m = Rpo256::merge(&[i.into(), j.into()]);
+        let n = Rpo256::merge(&[k.into(), l.into()]);
+
+        let root = Rpo256::merge(&[m.into(), n.into()]);
+
+        let store = MerkleStore::default()
+            .with_merkle_tree([a, b, c, d, e, f, g, h])
+            .unwrap();
+        let path = store.get_path(root.into(), NodeIndex::new(3, 1)).unwrap();
+
+        let expected = MerklePath::new([a.into(), j.into(), n.into()].to_vec());
+        assert_eq!(path, expected);
+    }
 }
```
