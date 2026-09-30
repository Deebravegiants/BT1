# [?] mmr: reject oversized forests to prevent num_nodes panics (#857)

## Summary
Severity: Unknown
Chain: Miden
Component: 0xMiden/miden-vm
Published: 2026-03-12
Source: https://github.com/0xMiden/miden-vm/commit/3c8fdcf6d4a7ef2b3f3a007c26a8f1eb27ae3013
Type: security-commit

## Details
mmr: reject oversized forests to prevent num_nodes panics (#857)

* mmr: reject oversized forests to prevent num_nodes panics

Forest deserialization previously accepted unbounded usize values. For values > usize::MAX/2 + 1, Forest::num_nodes asserted and would panic when downstream APIs (peaks/open/delta) were called.

An attacker could craft a serialized MMR with forest = usize::MAX/2 + 2 to crash consumers after deserialization.

This change enforces a maximum forest size at construction and deserialization, removes infallible constructors in favor of fallible ones, makes leaf appends return errors, and adds tests to cover oversize and iterator growth paths so oversized inputs are rejected before any panic can occur.

* mmr: cap forest size safely

* mmr: simplify append flow and document forest invariant

* mmr: trust apply invariants for new_peaks

* mmr: hard-cap max leaves to 2^k-1 and simplify xor/or

* mmr: remove redundant bounds checks and harden invariants

* mmr: centralize mask->node count helper usage

## Patch
### CHANGELOG.md
```diff
@@ -5,6 +5,7 @@
 ## 0.23.0 (2026-03-11)
 
 - Replaced `Subtree` internal storage with bitmask layout ([#784](https://github.com/0xMiden/crypto/pull/784)).
+- [BREAKING] Enforced a maximum MMR forest size and made MMR/forest constructors and appends fallible to reject oversized inputs ([#857](https://github.com/0xMiden/crypto/pull/857)).
 - [BREAKING] `PartialMmr::open()` now returns `Option<MmrProof>` instead of `Option<MmrPath>` ([#787](https://github.com/0xMiden/crypto/pull/787)).
 - [BREAKING] Refactored BLAKE3 to use `Digest<N>` struct, added `Digest192` type alias ([#811](https://github.com/0xMiden/crypto/pull/811)).
 - [BREAKING] Added validation to `PartialMmr::from_parts()` and `Deserializable` implementation, added `from_parts_unchecked()` for performance-critical code ([#812](https://github.com/0xMiden/crypto/pull/812)).
```

### miden-crypto/src/merkle/mmr/error.rs
```diff
@@ -12,6 +12,8 @@ pub enum MmrError {
     InvalidPeaks(String),
     #[error("mmr forest is out of bounds: requested {0} > current {1}")]
     ForestOutOfBounds(usize, usize),
+    #[error("mmr forest size {requested} exceeds maximum {max}")]
+    ForestSizeExceeded { requested: usize, max: usize },
     #[error("mmr peak does not match the computed merkle root of the provided authentication path")]
     PeakPathMismatch,
     #[error("requested peak index is {peak_idx} but the number of peaks is {peaks_len}")]
```

### miden-crypto/src/merkle/mmr/forest.rs
```diff
@@ -3,7 +3,7 @@ use core::{
     ops::{BitAnd, BitOr, BitXor, BitXorAssign},
 };
 
-use super::InOrderIndex;
+use super::{InOrderIndex, MmrError};
 use crate::{
     Felt,
     utils::{ByteReader, ByteWriter, Deserializable, DeserializationError, Serializable},
@@ -29,31 +29,61 @@ use crate::{
 /// - `Forest(0b1010)` is a forest with two trees: one with 8 leaves (15 nodes), one with 2 leaves
 ///   (3 nodes).
 /// - `Forest(0b1000)` is a forest with one tree, which has 8 leaves (15 nodes).
+///
+/// Forest sizes are capped at [`Forest::MAX_LEAVES`]. Use [`Forest::new`] or
+/// [`Forest::append_leaf`] to enforce the limit.
 #[derive(Debug, Copy, Clone, Default, PartialEq, Eq, PartialOrd, Ord)]
-#[cfg_attr(feature = "serde", derive(serde::Deserialize, serde::Serialize))]
+#[cfg_attr(feature = "serde", derive(serde::Serialize))]
 pub struct Forest(usize);
 
 impl Forest {
+    /// Maximum number of leaves supported by the forest.
+    ///
+    /// Rationale:
+    /// - We require `MAX_LEAVES <= usize::MAX / 2 + 1` so `num_nodes()` stays indexable via
+    ///   `usize`.
+    /// - We choose `usize::MAX / 2` (hard cutoff) rather than `usize::MAX / 2 + 1` so the cap is
+    ///   always of the form `2^k - 1` on all targets.
+    /// - With that shape, bitwise OR/XOR of valid forest values remains within bounds, so OR/XOR
+    ///   does not need additional overflow protection.
+    pub const MAX_LEAVES: usize = if (u32::MAX as usize) < (usize::MAX / 2) {
+        u32::MAX as usize
+    } else {
+        usize::MAX / 2
+    };
+
     /// Creates an empty forest (no trees).
     pub const fn empty() -> Self {
         Self(0)
     }
 
-    /// Creates a forest with `num_leaves` leaves.
-    pub const fn new(num_leaves: usize) -> Self {
-        Self(num_leaves)
+    /// Creates a forest with `num_leaves` leaves, returning an error if the value is too large.
+    pub fn new(num_leaves: usize) -> Result<Self, DeserializationError> {
+        if !Self::is_valid_size(num_leaves) {
+            return Err(DeserializationError::InvalidValue(format!(
+                "forest size {} exceeds maximum {}",
+                num_leaves,
+                Self::MAX_LEAVES
+            )));
+        }
+        Ok(Self(num_leaves))
     }
 
     /// Creates a forest with a given height.
     ///
-    /// This is equivalent to `Forest::new(1 << height)`.
+    /// This is equivalent to creating a forest with `1 << height` leaves.
     ///
     /// # Panics
     ///
     /// This will panic if `height` is greater than `usize::BITS - 1`.
-    pub const fn with_height(height: usize) -> Self {
+    pub fn with_height(height: usize) -> Self {
         assert!(height < usize::BITS as usize);
-        Self::new(1 << height)
+        Self::new(1 << height).expect("forest height exceeds maximum")
+    }
+
+    /// Returns true if `num_leaves` is within the supported bounds.
+    pub const fn is_valid_size(num_leaves: usize) -> bool {
+        num_leaves <= Self::MAX_LEAVES
     }
 
     /// Returns true if there are no trees in the forest.
@@ -64,8 +94,15 @@ impl Forest {
     /// Adds exactly one more leaf to the capacity of this forest.
     ///
     /// Some smaller trees might be merged together.
-    pub fn append_leaf(&mut self) {
+    pub fn append_leaf(&mut self) -> Result<(), MmrError> {
+        if self.0 >= Self::MAX_LEAVES {
+            return Err(MmrError::ForestSizeExceeded {
+                requested: self.0.saturating_add(1),
+                max: Self::MAX_LEAVES,
+            });
+        }
         self.0 += 1;
+        Ok(())
     }
 
     /// Returns a count of leaves in the entire underlying forest (MMR).
@@ -75,11 +112,11 @@ impl Forest {
 
     /// Return the total number of nodes of a given forest.
     ///
-    /// # Panics
-    ///
-    /// This will panic if the forest has size greater than `usize::MAX / 2 + 1`.
+    /// This relies on the `Forest` invariant that `num_leaves() <= Forest::MAX_LEAVES`.
+    /// The internal assertion is a defensive check and should be unreachable for values created
+    /// through validated constructors/deserializers.
     pub const fn num_nodes(self) -> usize {
-        assert!(self.0 <= usize::MAX / 2 + 1);
+        assert!(self.0 <= Self::MAX_LEAVES);
         if self.0 <= usize::MAX / 2 {
             self.0 * 2 - self.num_trees()
         } else {
@@ -197,11 +234,12 @@ impl Forest {
     ///
     /// ```
     /// # use miden_crypto::merkle::mmr::Forest;
-    /// let range = Forest::new(0b0101_0110);
-    /// assert_eq!(range.trees_larger_than(1), Forest::new(0b0101_0100));
+    /// let range = Forest::new(0b0101_0110).unwrap();
+    /// assert_eq!(range.trees_larger_than(1), Forest::new(0b0101_0100).unwrap());
     /// ```
     pub fn trees_larger_than(self, tree_idx: u32) -> Self {
-        self & high_bitmask(tree_idx + 1)
+        let mask = high_bitmask(tree_idx + 1);
+        Self::new(self.0 & mask).expect("forest size exceeds maximum")
     }
 
     /// Creates a new forest with all possible trees smaller than the smallest tree in this
@@ -216,7 +254,7 @@ impl Forest {
     /// For a non-panicking version of this function, see [`Forest::all_smaller_trees()`].
     pub fn all_smaller_trees_unchecked(self) -> Self {
         debug_assert_eq!(self.num_trees(), 1);
-        Self::new(self.0 - 1)
+        Self::new(self.0 - 1).expect("forest size exceeds maximum")
     }
 
     /// Creates a new forest with all possible trees smaller than the smallest tree in this
@@ -232,9 +270,16 @@ impl Forest {
     }
 
     /// Returns a forest with exactly one tree, one size (depth) larger than the current one.
-    pub fn next_larger_tree(self) -> Self {
+    ///
+    /// # Errors
+    /// Returns an error if the resulting forest would exceed [`Forest::MAX_LEAVES`].
+    pub(crate) fn next_larger_tree(self) -> Result<Self, MmrError> {
         debug_assert_eq!(self.num_trees(), 1);
-        Forest(self.0 << 1)
+        let value = self.0.saturating_mul(2);
+        if value > Self::MAX_LEAVES {
+            return Err(MmrError::ForestSizeExceeded { requested: value, max: Self::MAX_LEAVES });
+        }
+        Ok(Forest(value))
     }
 
     /// Returns true if the forest contains a single-node tree.
@@ -244,25 +289,29 @@ impl Forest {
 
     /// Add a single-node tree if not already present in the forest.
     pub fn with_single_leaf(self) -> Self {
-        Self::new(self.0 | 1)
+        // Setting the lowest bit cannot exceed MAX_LEAVES when MAX_LEAVES is 2^k - 1.
+        Self(self.0 | 1)
     }
 
     /// Remove the single-node tree if present in the forest.
     pub fn without_single_leaf(self) -> Self {
-        Self::new(self.0 & (usize::MAX - 1))
+        // Clearing the lowest bit does not add leaves.
+        Self(self.0 & (usize::MAX - 1))
     }
 
     /// Returns a new forest that does not have the trees that `other` has.
     pub fn without_trees(self, other: Forest) -> Self {
-        self ^ other
+        // Clearing bits does not add leaves.
+        Self(self.0 & !other.0)
     }
 
     /// Returns index of the forest tree for a specified leaf index.
     pub fn tree_index(&self, leaf_idx: usize) -> usize {
         let root = self
             .leaf_to_corresponding_tree(leaf_idx)
             .expect("position must be part of the forest");
-        let smaller_tree_mask = Self::new(2_usize.pow(root) - 1);
+        let smaller_tree_mask =
+            Self::new(2_usize.pow(root) - 1).expect("forest size exceeds maximum");
         let num_smaller_trees = (*self & smaller_tree_mask).num_trees();
         self.num_trees() - num_smaller_trees - 1
     }
@@ -350,8 +399,7 @@ impl Forest {
     /// Given a leaf index in the current forest, return the tree number responsible for the
     /// leaf.
     ///
-    /// Note:
-    /// The result is a tree position `p`, it has the following interpretations:
+    /// The result is a tree position `p`:
     /// - `p+1` is the depth of the tree.
     /// - Because the root element is not part of the proof, `p` is the length of the authentication
     ///   path.
@@ -396,8 +444,8 @@ impl Forest {
     /// the leaf belongs.
     pub(super) fn leaf_relative_position(self, leaf_idx: usize) -> Option<usize> {
         let tree_idx = self.leaf_to_corresponding_tree(leaf_idx)?;
-        let forest_before = self & high_bitmask(tree_idx + 1);
-        Some(leaf_idx - forest_before.0)
+        let mask = high_bitmask(tree_idx + 1);
+        Some(leaf_idx - (self.0 & mask))
     }
 }
 
@@ -417,23 +465,27 @@ impl BitAnd<Forest> for Forest {
     type Output = Self;
 
     fn bitand(self, rhs: Self) -> Self::Output {
-        Self::new(self.0 & rhs.0)
+        Self::new(self.0 & rhs.0).expect("forest size exceeds maximum")
     }
 }
 
+// Compile-time invariant: MAX_LEAVES must be exactly 2^k - 1.
+const _: () =
+    assert!(Forest::MAX_LEAVES != 0 && (Forest::MAX_LEAVES & (Forest::MAX_LEAVES + 1)) == 0);
+
 impl BitOr<Forest> for Forest {
     type Output = Self;
 
     fn bitor(self, rhs: Self) -> Self::Output {
-        Self::new(self.0 | rhs.0)
+        Self(self.0 | rhs.0)
     }
 }
 
 impl BitXor<Forest> for Forest {
     type Output = Self;
 
     fn bitxor(self, rhs: Self) -> Self::Output {
-        Self::new(self.0 ^ rhs.0)
+        Self(self.0 ^ rhs.0)
     }
 }
 
@@ -443,9 +495,29 @@ impl BitXorAssign<Forest> for Forest {
     }
 }
 
-impl From<Felt> for Forest {
-    fn from(value: Felt) -> Self {
-        Self::new(value.as_canonical_u64() as usize)
+impl TryFrom<Felt> for Forest {
+    type Error = MmrError;
+
+    fn try_from(value: Felt) -> Result<Self, Self::Error> {
+        let value = usize::try_from(value.as_canonical_u64()).map_err(|_| {
+            MmrError::ForestSizeExceeded {
+                requested: usize::MAX,
+                max: Self::MAX_LEAVES,
+            }
+        })?;
+        if value > Self::MAX_LEAVES {
+            return Err(MmrError::ForestSizeExceeded { requested: value, max: Self::MAX_LEAVES });
+        }
+        Ok(Self(value))
+    }
+}
+
+pub(crate) fn largest_tree_from_mask(mask: usize) -> Forest {
+    if mask == 0 {
+        Forest::empty()
+    } else {
+        let bit = mask.ilog2();
+        Forest::new(1usize << bit).expect("forest size exceeds maximum")
     }
 }
 
@@ -456,12 +528,8 @@ impl From<Forest> for Felt {
 }
 
 /// Return a bitmask for the bits including and above the given position.
-pub(crate) const fn high_bitmask(bit: u32) -> Forest {
-    if bit > usize::BITS - 1 {
-        Forest::empty()
-    } else {
-        Forest::new(usize::MAX << bit)
-    }
+pub(crate) fn high_bitmask(bit: u32) -> usize {
+    if bit > usize::BITS - 1 { 0 } else { usize::MAX << bit }
 }
 
 // SERIALIZATION
@@ -476,7 +544,18 @@ impl Serializable for Forest {
 impl Deserializable for Forest {
     fn read_from<R: ByteReader>(source: &mut R) -> Result<Self, DeserializationError> {
         let value = source.read_usize()?;
-        Ok(Self::new(value))
+        Self::new(value)
+    }
+}
+
+#[cfg(feature = "serde")]
+impl<'de> serde::Deserialize<'de> for Forest {
+    fn deserialize<D>(deserializer: D) -> Result<Self, D::Error>
+    where
+        D: serde::Deserializer<'de>,
+    {
+        let value = usize::deserialize(deserializer)?;
+        Self::new(value).map_err(serde::de::Error::custom)
     }
 }
 
```

### miden-crypto/src/merkle/mmr/full.rs
```diff
@@ -16,6 +16,7 @@ use super::{
     super::{InnerNodeInfo, MerklePath},
     MmrDelta, MmrError, MmrPath, MmrPeaks, MmrProof,
     forest::{Forest, TreeSizeIterator},
+    nodes_from_mask,
 };
 use crate::{
     Word,
@@ -64,6 +65,35 @@ impl Mmr {
         }
     }
 
+    /// Constructs an MMR from an iterator of leaves.
+    ///
+    /// # Errors
+    /// Returns an error if the maximum forest size is exceeded.
+    pub fn try_from_iter<T: IntoIterator<Item = Word>>(values: T) -> Result<Self, MmrError> {
+        Self::try_from_iter_with_limit(values, Forest::MAX_LEAVES)
+    }
+
+    pub(crate) fn try_from_iter_with_limit<T: IntoIterator<Item = Word>>(
+        values: T,
+        max_leaves: usize,
+    ) -> Result<Self, MmrError> {
+        let mut mmr = Mmr::new();
+        let iter = values.into_iter();
+        let (lower, _) = iter.size_hint();
+        if lower > max_leaves {
+            return Err(MmrError::ForestSizeExceeded { requested: lower, max: max_leaves });
+        }
+        let mut count = 0usize;
+        for v in iter {
+            count += 1;
+            if count > max_leaves {
+                return Err(MmrError::ForestSizeExceeded { requested: count, max: max_leaves });
+            }
+            mmr.add(v)?;
+        }
+        Ok(mmr)
+    }
+
     // ACCESSORS
     // ============================================================================================
 
@@ -121,7 +151,13 @@ impl Mmr {
     }
 
     /// Adds a new element to the MMR.
-    pub fn add(&mut self, el: Word) {
+    ///
+    /// # Errors
+    /// Returns an error if the MMR exceeds the maximum supported forest size.
+    pub fn add(&mut self, el: Word) -> Result<(), MmrError> {
+        // Fail early before mutating nodes.
+        let old_forest = self.forest;
+        self.forest.append_leaf()?;
         // Note: every node is also a tree of size 1, adding an element to the forest creates a new
         // rooted-tree of size 1. This may temporarily break the invariant that every tree in the
         // forest has different sizes, the loop below will eagerly merge trees of same size and
@@ -130,16 +166,22 @@ impl Mmr {
 
         let mut left_offset = self.nodes.len().saturating_sub(2);
         let mut right = el;
-        let mut left_tree = 1;
-        while !(self.forest & Forest::new(left_tree)).is_empty() {
+        let mut left_tree = 1usize;
+        while (old_forest.num_leaves() & left_tree) != 0 {
             right = Poseidon2::merge(&[self.nodes[left_offset], right]);
             self.nodes.push(right);
 
-            left_offset = left_offset.saturating_sub(Forest::new(left_tree).num_nodes());
-            left_tree <<= 1;
+            debug_assert!(left_tree <= Forest::MAX_LEAVES);
+            let left_nodes = left_tree * 2 - 1;
+            left_offset = left_offset.saturating_sub(left_nodes);
+
+            match left_tree.checked_shl(1) {
+                Some(next) => left_tree = next,
+                None => break,
+            }
         }
 
-        self.forest.append_leaf();
+        Ok(())
     }
 
     /// Returns the current peaks of the MMR.
@@ -197,8 +239,8 @@ impl Mmr {
         let mut result = Vec::new();
 
         // Find the largest tree in this [Mmr] which is new to `from_forest`.
-        let candidate_trees = to_forest ^ from_forest;
-        let mut new_high = candidate_trees.largest_tree_unchecked();
+        let candidate_mask = to_forest.num_leaves() ^ from_forest.num_leaves();
+        let mut new_high = super::forest::largest_tree_from_mask(candidate_mask);
 
         // Collect authentication nodes used for tree merges
         // ----------------------------------------------------------------------------------------
@@ -221,14 +263,16 @@ impl Mmr {
                 // - target: tree from which to load the sibling. On the first iteration this is a
                 //   value known by the partial mmr, on subsequent iterations this value is to be
                 //   computed from the known peaks and provided authentication nodes.
-                let known = (common_trees | merges | target).num_nodes();
+                let known_mask =
+                    common_trees.num_leaves() | merges.num_leaves() | target.num_leaves();
+                let known = nodes_from_mask(known_mask);
                 let sibling = target.num_nodes();
                 result.push(self.nodes[known + sibling - 1]);
 
                 // Update the target and account for tree merges
-                target = target.next_larger_tree();
+                target = target.next_larger_tree()?;
                 while !(merges & target).is_empty() {
-                    target = target.next_larger_tree();
+                    target = target.next_larger_tree()?;
                 }
                 // Remove the merges done so far
                 merges ^= merges & target.all_smaller_trees_unchecked();
@@ -298,7 +342,7 @@ impl Mmr {
 
         // The tree walk below goes from the root to the leaf, compute the root index to start
         let mut forest_target: usize = 1usize << tree_bit;
-        let mut index = Forest::new(forest_target).num_nodes() - 1;
+        let mut index = nodes_from_mask(forest_target) - 1;
 
         // Loop until the leaf is reached
         while forest_target > 1 {
@@ -307,7 +351,7 @@ impl Mmr {
 
             // compute the indices of the right and left subtrees based on the post-order
             let right_offset = index - 1;
-            let left_offset = right_offset - Forest::new(forest_target).num_nodes();
+            let left_offset = right_offset - nodes_from_mask(forest_target);
 
             let left_or_right = relative_pos & forest_target;
             let sibling = if left_or_right != 0 {
@@ -337,18 +381,7 @@ impl Mmr {
 // CONVERSIONS
 // ================================================================================================
 
-impl<T> From<T> for Mmr
-where
-    T: IntoIterator<Item = Word>,
-{
-    fn from(values: T) -> Self {
-        let mut mmr = Mmr::new();
-        for v in values {
-            mmr.add(v)
-        }
-        mmr
-    }
-}
+// No TryFrom<T> impl: it conflicts with core’s blanket TryFrom<U> where U: Into<T>.
 
 // SERIALIZATION
 // ================================================================================================
@@ -415,7 +448,7 @@ impl Iterator for MmrNodes<'_> {
 
             // compute the number of nodes in the right tree, this is the offset to the
             // previous left parent
-            let right_nodes = Forest::new(self.last_right).num_nodes();
+            let right_nodes = Forest::new(self.last_right).unwrap().num_nodes();
             // the next parent position is one above the position of the pair
             let parent = self.last_right << 1;
 
@@ -453,10 +486,11 @@ impl Iterator for MmrNodes<'_> {
 mod tests {
     use alloc::vec::Vec;
 
+    use super::super::nodes_from_mask;
     use crate::{
         Felt, Word, ZERO,
-        merkle::mmr::Mmr,
-        utils::{Deserializable, Serializable},
+        merkle::mmr::{Forest, Mmr},
+        utils::{Deserializable, DeserializationError, Serializable},
     };
 
     #[test]
@@ -465,10 +499,28 @@ mod tests {
             .map(|value| Word::new([ZERO, ZERO, ZERO, Felt::new(value)]))
             .collect::<Vec<_>>();
 
-        let mmr = Mmr::from(nodes);
+        let mmr = Mmr::try_from_iter(nodes).unwrap();
         let serialized = mmr.to_bytes();
         let deserialized = Mmr::read_from_bytes(&serialized).unwrap();
         assert_eq!(mmr.forest, deserialized.forest);
         assert_eq!(mmr.nodes, deserialized.nodes);
     }
+
+    #[test]
+    fn test_deserialization_rejects_large_forest() {
+        let mut bytes = (Forest::MAX_LEAVES + 1).to_bytes();
+        bytes.extend_from_slice(&0usize.to_bytes()); // empty nodes vector
+
+        let result = Mmr::read_from_bytes(&bytes);
+        assert!(matches!(result, Err(DeserializationError::InvalidValue(_))));
+    }
+
+    #[test]
+    fn test_nodes_from_mask_at_max_leaves() {
+        let expected = (Forest::MAX_LEAVES as u128)
+            .saturating_mul(2)
+            .saturating_sub(Forest::MAX_LEAVES.count_ones() as u128);
+        assert!(expected <= usize::MAX as u128);
+        assert_eq!(nodes_from_mask(Forest::MAX_LEAVES), expected as usize);
+    }
 }
```

### miden-crypto/src/merkle/mmr/mod.rs
```diff
@@ -12,6 +12,14 @@ mod proof;
 #[cfg(test)]
 mod tests;
 
+/// Returns the number of nodes represented by a forest bitmask.
+///
+/// `mask` is a forest-leaf mask (same encoding as [`Forest::num_leaves()`]): each set bit denotes
+/// one peak/tree with leaf count `2^bit_position`.
+fn nodes_from_mask(mask: usize) -> usize {
+    Forest::new(mask).expect("mask must encode a valid forest").num_nodes()
+}
+
 // REEXPORTS
 // ================================================================================================
 pub use delta::MmrDelta;
```

### miden-crypto/src/merkle/mmr/partial.rs
```diff
@@ -300,8 +300,12 @@ impl PartialMmr {
     /// inserted into this [PartialMmr] as a result of this operation.
     ///
     /// When `track` is `true` the new leaf is tracked and its value is stored.
-    pub fn add(&mut self, leaf: Word, track: bool) -> Vec<(InOrderIndex, Word)> {
-        self.forest.append_leaf();
+    ///
+    /// # Errors
+    /// Returns an error if the MMR exceeds the maximum supported forest size.
+    pub fn add(&mut self, leaf: Word, track: bool) -> Result<Vec<(InOrderIndex, Word)>, MmrError> {
+        // Fail early before mutating nodes.
+        self.forest.append_leaf()?;
         // The smallest tree height equals the number of merges because adding a leaf is like
         // adding 1 in binary: each carry corresponds to a merge. For example, forest 3 (0b11)
         // + 1 = 4 (0b100) requires 2 carries/merges to form a tree of height 2.
@@ -380,7 +384,7 @@ impl PartialMmr {
 
         self.peaks.push(peak);
 
-        new_nodes
+        Ok(new_nodes)
     }
 
     /// Adds the authentication path represented by [MerklePath] if it is valid.
@@ -400,9 +404,12 @@ impl PartialMmr {
     ) -> Result<(), MmrError> {
         // Checks there is a tree with same depth as the authentication path, if not the path is
         // invalid.
-        let tree = Forest::new(1 << path.depth());
+        let path_depth = path.depth();
+        let tree_leaves =
+            1usize.checked_shl(path_depth as u32).ok_or(MmrError::UnknownPeak(path_depth))?;
+        let tree = Forest::new(tree_leaves).map_err(|_| MmrError::UnknownPeak(path_depth))?;
         if (tree & self.forest).is_empty() {
-            return Err(MmrError::UnknownPeak(path.depth()));
+            return Err(MmrError::UnknownPeak(path_depth));
         };
 
         // ignore the trees smaller than the target (these elements are position after the current
@@ -527,10 +534,10 @@ impl PartialMmr {
         }
 
         // find the trees to merge (bitmask of existing trees that will be combined)
-        let changes = self.forest ^ delta.forest;
+        let changes = self.forest.num_leaves() ^ delta.forest.num_leaves();
         // `largest_tree_unchecked()` panics if `changes` is empty. `changes` cannot be empty
         // unless `self.forest == delta.forest`, which is guarded against above.
-        let largest = changes.largest_tree_unchecked();
+        let largest = super::forest::largest_tree_from_mask(changes);
         // The largest tree itself also cannot be an empty forest, so this cannot panic either.
         let trees_to_merge = self.forest & largest.all_smaller_trees_unchecked();
 
@@ -546,7 +553,9 @@ impl PartialMmr {
 
             (merge_count, new_peaks)
         } else {
-            (0, changes)
+            let new_peaks = Forest::new(changes)
+                .expect("changes must be a valid forest under apply invariants");
+            (0, new_peaks)
         };
 
         // verify the delta size
@@ -611,7 +620,7 @@ impl PartialMmr {
 
                 peak_idx = peak_idx.parent();
                 new = Poseidon2::merge(&[left, right]);
-                target = target.next_larger_tree();
+                target = target.next_larger_tree()?;
             }
 
             debug_assert!(peak_count == trees_to_merge.num_trees());
@@ -746,7 +755,7 @@ impl Deserializable for PartialMmr {
     ) -> Result<Self, crate::utils::DeserializationError> {
         use crate::utils::DeserializationError;
 
-        let forest = Forest::new(usize::read_from(source)?);
+        let forest = Forest::new(usize::read_from(source)?)?;
         let peaks_vec = Vec::<Word>::read_from(source)?;
         let nodes = NodeMap::read_from(source)?;
         if !source.has_more_bytes() {
@@ -790,7 +799,7 @@ mod tests {
             mmr::{InOrderIndex, Mmr, forest::Forest},
             store::MerkleStore,
         },
-        utils::{ByteWriter, Deserializable, Serializable},
+        utils::{ByteWriter, Deserializable, DeserializationError, Serializable},
     };
 
     const LEAVES: [Word; 7] = [
@@ -807,7 +816,7 @@ mod tests {
     fn test_partial_mmr_apply_delta() {
         // build an MMR with 10 nodes (2 peaks) and a partial MMR based on it
         let mut mmr = Mmr::default();
-        (0..10).for_each(|i| mmr.add(int_to_node(i)));
+        (0..10).for_each(|i| mmr.add(int_to_node(i)).unwrap());
         let mut partial_mmr: PartialMmr = mmr.peaks().into();
 
         // add authentication path for position 1 and 8
@@ -824,11 +833,11 @@ mod tests {
         }
 
         // add 2 more nodes into the MMR and validate apply_delta()
-        (10..12).for_each(|i| mmr.add(int_to_node(i)));
+        (10..12).for_each(|i| mmr.add(int_to_node(i)).unwrap());
         validate_apply_delta(&mmr, &mut partial_mmr);
 
         // add 1 more node to the MMR, validate apply_delta() and start tracking the node
-        mmr.add(int_to_node(12));
+        mmr.add(int_to_node(12)).unwrap();
         validate_apply_delta(&mmr, &mut partial_mmr);
         {
             let node = mmr.get(12).unwrap();
@@ -841,7 +850,7 @@ mod tests {
         // by this point we are tracking authentication paths for positions: 1, 8, and 12
 
         // add 3 more nodes to the MMR (collapses to 1 peak) and validate apply_delta()
-        (13..16).for_each(|i| mmr.add(int_to_node(i)));
+        (13..16).for_each(|i| mmr.add(int_to_node(i)).unwrap());
         validate_apply_delta(&mmr, &mut partial_mmr);
     }
 
@@ -877,7 +886,7 @@ mod tests {
     #[test]
     fn test_partial_mmr_inner_nodes_iterator() {
         // build the MMR
-        let mmr: Mmr = LEAVES.into();
+        let mmr = Mmr::try_from_iter(LEAVES.iter().copied()).unwrap();
         let first_peak = mmr.peaks().peaks()[0];
 
         // -- test single tree ----------------------------
@@ -973,8 +982,8 @@ mod tests {
         let mut partial_mmr = PartialMmr::from_peaks(empty_peaks);
 
         for el in (0..256).map(int_to_node) {
-            mmr.add(el);
-            partial_mmr.add(el, false);
+            mmr.add(el).unwrap();
+            partial_mmr.add(el, false).unwrap();
 
             assert_eq!(mmr.peaks(), partial_mmr.peaks());
             assert_eq!(mmr.forest(), partial_mmr.forest());
@@ -989,8 +998,8 @@ mod tests {
 
         for i in 0..256 {
             let el = int_to_node(i as u64);
-            mmr.add(el);
-            partial_mmr.add(el, true);
+            mmr.add(el).unwrap();
+            partial_mmr.add(el, true).unwrap();
 
             assert_eq!(mmr.peaks(), partial_mmr.peaks());
             assert_eq!(mmr.forest(), partial_mmr.forest());
@@ -1005,7 +1014,7 @@ mod tests {
 
     #[test]
     fn test_partial_mmr_add_existing_track() {
-        let mut mmr = Mmr::from((0..7).map(int_to_node));
+        let mut mmr = Mmr::try_from_iter((0..7).map(int_to_node)).unwrap();
 
         // derive a partial Mmr from it which tracks authentication path to leaf 5
         let mut partial_mmr = PartialMmr::from_peaks(mmr.peaks());
@@ -1015,8 +1024,8 @@ mod tests {
 
         // add a new leaf to both Mmr and partial Mmr
         let leaf_at_7 = int_to_node(7);
-        mmr.add(leaf_at_7);
-        partial_mmr.add(leaf_at_7, false);
+        mmr.add(leaf_at_7).unwrap();
+        partial_mmr.add(leaf_at_7, false).unwrap();
 
         // the openings should be the same
         assert_eq!(mmr.open(5).unwrap(), partial_mmr.open(5).unwrap().unwrap());
@@ -1031,16 +1040,16 @@ mod tests {
 
         // Add leaf 0 with tracking - it's a dangling leaf (forest=1)
         let leaf0 = int_to_node(0);
-        mmr.add(leaf0);
-        partial_mmr.add(leaf0, true);
+        mmr.add(leaf0).unwrap();
+        partial_mmr.add(leaf0, true).unwrap();
 
         // Both should produce the same proof (empty path, leaf is a peak)
         assert_eq!(mmr.open(0).unwrap(), partial_mmr.open(0).unwrap().unwrap());
 
         // Add leaf 1 WITHOUT tracking - triggers merge, leaf 0 gets a sibling
         let leaf1 = int_to_node(1);
-        mmr.add(leaf1);
-        partial_mmr.add(leaf1, false);
+        mmr.add(leaf1).unwrap();
+        partial_mmr.add(leaf1, false).unwrap();
 
         // Leaf 0 should still be tracked with correct proof after merge
         assert!(partial_mmr.is_tracked(0));
@@ -1050,7 +1059,7 @@ mod tests {
 
     #[test]
     fn test_partial_mmr_serialization() {
-        let mmr = Mmr::from((0..7).map(int_to_node));
+        let mmr = Mmr::try_from_iter((0..7).map(int_to_node)).unwrap();
         let partial_mmr = PartialMmr::from_peaks(mmr.peaks());
 
         let bytes = partial_mmr.to_bytes();
@@ -1059,10 +1068,21 @@ mod tests {
         assert_eq!(partial_mmr, decoded);
     }
 
+    #[test]
+    fn test_partial_mmr_deserialization_rejects_large_forest() {
+        let mut bytes = (Forest::MAX_LEAVES + 1).to_bytes();
+        bytes.extend_from_slice(&0usize.to_bytes()); // empty peaks vec
+        bytes.extend_from_slice(&0usize.to_bytes()); // empty nodes map
+        bytes.extend_from_slice(&0usize.to_bytes()); // empty tracked vec
+
+        let result = PartialMmr::read_from_bytes(&bytes);
+        assert!(matches!(result, Err(DeserializationError::InvalidValue(_))));
+    }
+
     #[test]
     fn test_partial_mmr_untrack() {
         // build the MMR
-        let mmr: Mmr = LEAVES.into();
+        let mmr = Mmr::try_from_iter(LEAVES.iter().copied()).unwrap();
 
         // get path and node for position 1
         let node1 = mmr.get(1).unwrap();
@@ -1090,7 +1110,7 @@ mod tests {
     #[test]
     fn test_partial_mmr_untrack_returns_removed_nodes() {
         // build the MMR
-        let mmr: Mmr = LEAVES.into();
+        let mmr = Mmr::try_from_iter(LEAVES.iter().copied()).unwrap();
 
         // get path and node for position 1
         let node1 = mmr.get(1).unwrap();
@@ -1120,7 +1140,7 @@ mod tests {
     #[test]
     fn test_partial_mmr_untrack_shared_nodes() {
         // build the MMR
-        let mmr: Mmr = LEAVES.into();
+        let mmr = Mmr::try_from_iter(LEAVES.iter().copied()).unwrap();
 
         // track two sibling leaves (positions 0 and 1)
         let node0 = mmr.get(0).unwrap();
@@ -1171,7 +1191,7 @@ mod tests {
     #[test]
     fn test_partial_mmr_untrack_preserves_upper_siblings() {
         let mut mmr = Mmr::default();
-        (0..8).for_each(|i| mmr.add(int_to_node(i)));
+        (0..8).for_each(|i| mmr.add(int_to_node(i)).unwrap());
 
         let mut partial_mmr: PartialMmr = mmr.peaks().into();
         for pos in [0, 2] {
@@ -1190,7 +1210,7 @@ mod tests {
     #[test]
     fn test_partial_mmr_deserialize_missing_marker_fails() {
         let mut mmr = Mmr::default();
-        (0..3).for_each(|i| mmr.add(int_to_node(i)));
+        (0..3).for_each(|i| mmr.add(int_to_node(i)).unwrap());
         let peaks = mmr.peaks();
 
         let mut bytes = Vec::new();
@@ -1203,7 +1223,7 @@ mod tests {
     #[test]
     fn test_partial_mmr_deserialize_invalid_marker_fails() {
         let mut mmr = Mmr::default();
-        (0..3).for_each(|i| mmr.add(int_to_node(i)));
+        (0..3).for_each(|i| mmr.add(int_to_node(i)).unwrap());
         let peaks = mmr.peaks();
 
         let mut bytes = Vec::new();
@@ -1219,7 +1239,7 @@ mod tests {
     #[test]
     fn test_partial_mmr_open_returns_proof_with_leaf() {
         // build the MMR
-        let mmr: Mmr = LEAVES.into();
+        let mmr = Mmr::try_from_iter(LEAVES.iter().copied()).unwrap();
 
         // get leaf and proof for position 1
         let leaf1 = mmr.get(1).unwrap();
@@ -1249,9 +1269,9 @@ mod tests {
         let leaf1 = int_to_node(1);
         let leaf2 = int_to_node(2);
 
-        partial_mmr.add(leaf0, true); // track
-        partial_mmr.add(leaf1, false); // don't track
-        partial_mmr.add(leaf2, true); // track
+        partial_mmr.add(leaf0, true).unwrap(); // track
+        partial_mmr.add(leaf1, false).unwrap(); // don't track
+        partial_mmr.add(leaf2, true).unwrap(); // track
 
         // verify tracked leaves can be opened
         let proof0 = partial_mmr.open(0).unwrap();
@@ -1281,7 +1301,7 @@ mod tests {
     fn test_partial_mmr_track_dangling_leaf() {
         // Single-leaf MMR: forest = 1, leaf 0 is a peak with an empty path.
         let mut mmr = Mmr::default();
-        mmr.add(int_to_node(0));
+        mmr.add(int_to_node(0)).unwrap();
         let mut partial_mmr: PartialMmr = mmr.peaks().into();
 
         let leaf0 = mmr.get(0).unwrap();
@@ -1303,7 +1323,7 @@ mod tests {
         use super::InOrderIndex;
 
         // Build a valid MMR with 7 leaves
-        let mmr: Mmr = LEAVES.into();
+        let mmr = Mmr::try_from_iter(LEAVES.iter().copied()).unwrap();
         let peaks = mmr.peaks();
 
         // Valid case: empty nodes and empty tracked_leaves
@@ -1381,7 +1401,7 @@ mod tests {
     #[test]
     fn test_from_parts_validation_deserialization() {
         // Build an MMR with 7 leaves
-        let mmr: Mmr = LEAVES.into();
+        let mmr = Mmr::try_from_iter(LEAVES.iter().copied()).unwrap();
         let partial_mmr = PartialMmr::from_peaks(mmr.peaks());
 
         // Valid serialization/deserialization
@@ -1429,7 +1449,7 @@ mod tests {
         use alloc::collections::BTreeMap;
 
         // Build a valid MMR
-        let mmr: Mmr = LEAVES.into();
+        let mmr = Mmr::try_from_iter(LEAVES.iter().copied()).unwrap();
         let peaks = mmr.peaks();
 
         // from_parts_unchecked should not validate and always succeed
```

### miden-crypto/src/merkle/mmr/peaks.rs
```diff
@@ -57,8 +57,15 @@ impl MmrPeaks {
     /// leaves in the underlying MMR.
     ///
     /// # Errors
-    /// Returns an error if the number of leaves and the number of peaks are inconsistent.
+    /// Returns an error if the number of leaves and the number of peaks are inconsistent, or if
+    /// the forest exceeds the maximum supported size.
     pub fn new(forest: Forest, peaks: Vec<Word>) -> Result<Self, MmrError> {
+        if !Forest::is_valid_size(forest.num_leaves()) {
+            return Err(MmrError::ForestSizeExceeded {
+                requested: forest.num_leaves(),
+                max: Forest::MAX_LEAVES,
+            });
+        }
         if forest.num_trees() != peaks.len() {
             return Err(MmrError::InvalidPeaks(format!(
                 "number of one bits in leaves is {} which does not equal peak length {}",
```

### miden-crypto/src/merkle/mmr/proof.rs
```diff
@@ -180,7 +180,7 @@ mod tests {
     #[test]
     fn test_peak_index() {
         // --- single peak forest ---------------------------------------------
-        let forest = Forest::new(11);
+        let forest = Forest::new(11).unwrap();
 
         // the first 4 leaves belong to peak 0
         for position in 0..8 {
@@ -189,7 +189,7 @@ mod tests {
         }
 
         // --- forest with non-consecutive peaks ------------------------------
-        let forest = Forest::new(11);
+        let forest = Forest::new(11).unwrap();
 
         // the first 8 leaves belong to peak 0
         for position in 0..8 {
@@ -208,7 +208,7 @@ mod tests {
         assert_eq!(proof.peak_index(), 2);
 
         // --- forest with consecutive peaks ----------------------------------
-        let forest = Forest::new(7);
+        let forest = Forest::new(7).unwrap();
 
         // the first 4 leaves belong to peak 0
         for position in 0..4 {
@@ -237,14 +237,14 @@ mod tests {
         // Create an MMR with 5 leaves
         let mut small_mmr = Mmr::new();
         for i in 0..5 {
-            small_mmr.add(int_to_node(i));
+            small_mmr.add(int_to_node(i)).unwrap();
         }
         let small_forest = small_mmr.forest();
 
         // Clone and add 5 more leaves to create larger MMR
         let mut large_mmr = small_mmr.clone();
         for i in 5..10 {
-            large_mmr.add(int_to_node(i));
+            large_mmr.add(int_to_node(i)).unwrap();
         }
 
         // Get proof for position 2 from the larger MMR
@@ -273,17 +273,17 @@ mod tests {
         // Create a MMR with 7 leaves
         let mut mmr = Mmr::new();
         for i in 0..7 {
-            mmr.add(int_to_node(i));
+            mmr.add(int_to_node(i)).unwrap();
         }
         let proof = mmr.open(2).unwrap();
         let path = proof.path();
 
         // Error: target forest doesn't include position
-        let small_forest = Forest::new(2);
+        let small_forest = Forest::new(2).unwrap();
         assert!(path.with_forest(small_forest).is_err());
 
         // Error: target forest is larger than current
-        let large_forest = Forest::new(15);
+        let large_forest = Forest::new(15).unwrap();
         assert!(path.with_forest(large_forest).is_err());
 
         // Same forest should work
```

### miden-crypto/src/merkle/mmr/tests.rs
```diff
@@ -4,7 +4,7 @@ use assert_matches::assert_matches;
 
 use super::{
     super::{InnerNodeInfo, Poseidon2, Word},
-    Mmr, MmrError, MmrPeaks, PartialMmr,
+    Mmr, MmrError, MmrPeaks, PartialMmr, nodes_from_mask,
 };
 use crate::{
     Felt,
@@ -91,11 +91,11 @@ fn test_leaf_to_corresponding_tree() {
 
 #[test]
 fn test_high_bitmask() {
-    assert_eq!(high_bitmask(0), Forest::new(usize::MAX));
-    assert_eq!(high_bitmask(1), Forest::new(usize::MAX << 1));
-    assert_eq!(high_bitmask(usize::BITS - 2), Forest::new(0b11usize.rotate_right(2)));
-    assert_eq!(high_bitmask(usize::BITS - 1), Forest::new(0b1usize.rotate_right(1)));
-    assert_eq!(high_bitmask(usize::BITS), Forest::empty(), "overflow should be handled");
+    assert_eq!(high_bitmask(0), usize::MAX);
+    assert_eq!(high_bitmask(1), usize::MAX << 1);
+    assert_eq!(high_bitmask(usize::BITS - 2), 0b11usize.rotate_right(2));
+    assert_eq!(high_bitmask(usize::BITS - 1), 0b1usize.rotate_right(1));
+    assert_eq!(high_bitmask(usize::BITS), 0, "overflow should be handled");
 }
 
 #[test]
@@ -121,28 +121,213 @@ fn test_nodes_in_forest_single_bit() {
     assert_eq!(nodes_in_forest(2usize.pow(2)), 2usize.pow(3) - 1);
     assert_eq!(nodes_in_forest(2usize.pow(3)), 2usize.pow(4) - 1);
 
-    for bit in 0..(usize::BITS - 1) {
-        let size = 2usize.pow(bit + 1) - 1;
-        assert_eq!(nodes_in_forest(1usize << bit), size);
+    let mut bit = 0u32;
+    while let Some(leaves) = 1usize.checked_shl(bit) {
+        if leaves > Forest::MAX_LEAVES {
+            break;
+        }
+
+        if leaves > usize::MAX / 2 {
+            break;
+        }
+
+        let size = leaves * 2 - 1;
+        assert_eq!(nodes_in_forest(leaves), size);
+        bit += 1;
+    }
+
+    if Forest::MAX_LEAVES.is_power_of_two() {
+        let expected = (Forest::MAX_LEAVES as u128).saturating_mul(2).saturating_sub(1);
+        let actual = nodes_in_forest(Forest::MAX_LEAVES) as u128;
+        assert_eq!(actual, expected);
     }
 }
 
 #[test]
 fn test_forest_largest_smallest_tree() {
     // largest_tree and smallest_tree return correct results
-    let forest = Forest::new(0b1101_0100);
-    let largest = Forest::new(0b1000_0000);
-    let smallest = Forest::new(0b0000_0100);
+    let forest = Forest::new(0b1101_0100).unwrap();
+    let largest = Forest::new(0b1000_0000).unwrap();
+    let smallest = Forest::new(0b0000_0100).unwrap();
 
     assert_eq!(forest.largest_tree(), largest);
     assert_eq!(forest.smallest_tree(), smallest);
 
     // no trees in an empty forest
-    let empty_forest = Forest::new(0);
+    let empty_forest = Forest::new(0).unwrap();
     assert_eq!(empty_forest.largest_tree(), empty_forest);
     assert_eq!(empty_forest.smallest_tree(), empty_forest);
 }
 
+#[test]
+fn test_forest_append_leaf_limit() {
+    let mut forest = Forest::new(Forest::MAX_LEAVES).unwrap();
+    assert_matches!(
+        forest.append_leaf(),
+        Err(MmrError::ForestSizeExceeded { requested, max }) if
+            requested == Forest::MAX_LEAVES + 1 && max == Forest::MAX_LEAVES
+    );
+}
+
+#[test]
+fn test_forest_new_limit() {
+    assert!(Forest::new(Forest::MAX_LEAVES).is_ok());
+    assert!(Forest::new(Forest::MAX_LEAVES + 1).is_err());
+}
+
+#[cfg(feature = "serde")]
+#[test]
+fn test_forest_serde_rejects_large_value() {
+    use serde::{Deserialize, de::value::UsizeDeserializer};
+
+    let result = Forest::deserialize(UsizeDeserializer::<serde::de::value::Error>::new(
+        Forest::MAX_LEAVES + 1,
+    ));
+    assert!(result.is_err());
+}
+
+#[test]
+fn test_forest_with_single_leaf_limit() {
+    let forest = Forest::new(Forest::MAX_LEAVES).unwrap();
+    let result = forest.with_single_leaf();
+    assert_eq!(result.num_leaves(), Forest::MAX_LEAVES);
+}
+
+#[test]
+fn test_forest_bitxor_within_limit() {
+    let high = Forest::new(Forest::MAX_LEAVES).unwrap();
+    let low = Forest::new(Forest::MAX_LEAVES - 1).unwrap();
+    let result = high ^ low;
+    assert!(result.num_leaves() <= Forest::MAX_LEAVES);
+}
+
+#[test]
+fn test_forest_bitor_within_limit() {
+    let high = Forest::new(Forest::MAX_LEAVES).unwrap();
+    let low = Forest::new(1).unwrap();
+    let result = high | low;
+    assert!(result.num_leaves() <= Forest::MAX_LEAVES);
+}
+
+#[test]
+fn test_forest_without_trees_does_not_add_bits() {
+    let forest = Forest::new(0b1000).unwrap();
+    let other = Forest::new(0b0001).unwrap();
+    let result = forest.without_trees(other);
+    assert_eq!(result, forest);
+}
+
+#[test]
+fn test_mmr_add_limit_prevents_mutation() {
+    let mut mmr = Mmr {
+        forest: Forest::new(Forest::MAX_LEAVES).unwrap(),
+        nodes: Vec::new(),
+    };
+    let result = mmr.add(Word::empty());
+    assert_matches!(result, Err(MmrError::ForestSizeExceeded { .. }));
+    assert_eq!(mmr.nodes.len(), 0);
+    assert_eq!(mmr.forest.num_leaves(), Forest::MAX_LEAVES);
+}
+
+#[test]
+fn test_mmr_try_from_iter_accepts_oversize_upper_hint() {
+    struct OversizeIter;
+
+    impl Iterator for OversizeIter {
+        type Item = Word;
+
+        fn next(&mut self) -> Option<Self::Item> {
+            None
+        }
+
+        fn size_hint(&self) -> (usize, Option<usize>) {
+            (0, Some(Forest::MAX_LEAVES + 1))
+        }
+    }
+
+    let result = Mmr::try_from_iter(OversizeIter);
+    assert!(result.is_ok());
+}
+
+#[test]
+fn test_mmr_try_from_iter_rejects_oversize_lower_bound() {
+    struct OversizeLowerIter {
+        remaining: usize,
+    }
+
+    impl Iterator for OversizeLowerIter {
+        type Item = Word;
+
+        fn next(&mut self) -> Option<Self::Item> {
+            if self.remaining == 0 {
+                None
+            } else {
+                self.remaining -= 1;
+                Some(Word::empty())
+            }
+        }
+
+        fn size_hint(&self) -> (usize, Option<usize>) {
+            (self.remaining, Some(self.remaining))
+        }
+    }
+
+    let result = Mmr::try_from_iter(OversizeLowerIter { remaining: Forest::MAX_LEAVES + 1 });
+    assert_matches!(result, Err(MmrError::ForestSizeExceeded { .. }));
+}
+
+#[test]
+fn test_mmr_try_from_iter_rejects_oversize_actual() {
+    let max_leaves = 8;
+
+    struct OversizeActualIter {
+        remaining: usize,
+    }
+
+    impl Iterator for OversizeActualIter {
+        type Item = Word;
+
+        fn next(&mut self) -> Option<Self::Item> {
+            if self.remaining == 0 {
+                None
+            } else {
+                self.remaining -= 1;
+                Some(Word::empty())
+            }
+        }
+
+        fn size_hint(&self) -> (usize, Option<usize>) {
+            (0, None)
+        }
+    }
+
+    let result =
+        Mmr::try_from_iter_with_limit(OversizeActualIter { remaining: max_leaves + 1 }, max_leaves);
+    assert_matches!(
+        result,
+        Err(MmrError::ForestSizeExceeded { requested, max }) if
+            requested == max_leaves + 1 && max == max_leaves
+    );
+}
+
+#[test]
+fn test_partial_mmr_add_limit_prevents_mutation() {
+    let mut partial = PartialMmr {
+        forest: Forest::new(Forest::MAX_LEAVES).unwrap(),
+        ..Default::default()
+    };
+    let before_peaks = partial.peaks.clone();
+    let before_nodes = partial.nodes.clone();
+    let before_tracked = partial.tracked_leaves.clone();
+
+    let result = partial.add(Word::empty(), true);
+    assert_matches!(result, Err(MmrError::ForestSizeExceeded { .. }));
+    assert_eq!(partial.forest.num_leaves(), Forest::MAX_LEAVES);
+    assert_eq!(partial.peaks, before_peaks);
+    assert_eq!(partial.nodes, before_nodes);
+    assert_eq!(partial.tracked_leaves, before_tracked);
+}
+
 #[test]
 fn test_forest_to_root_index() {
     fn idx(pos: usize) -> InOrderIndex {
@@ -151,22 +336,22 @@ fn test_forest_to_root_index() {
 
     // When there is a single tree in the forest, the index is equivalent to the number of
     // leaves in that tree, which is `2^n`.
-    assert_eq!(Forest::new(0b0001).root_in_order_index(), idx(1));
-    assert_eq!(Forest::new(0b0010).root_in_order_index(), idx(2));
-    assert_eq!(Forest::new(0b0100).root_in_order_index(), idx(4));
-    assert_eq!(Forest::new(0b1000).root_in_order_index(), idx(8));
-
-    assert_eq!(Forest::new(0b0011).root_in_order_index(), idx(5));
-    assert_eq!(Forest::new(0b0101).root_in_order_index(), idx(9));
-    assert_eq!(Forest::new(0b1001).root_in_order_index(), idx(17));
-    assert_eq!(Forest::new(0b0111).root_in_order_index(), idx(13));
-    assert_eq!(Forest::new(0b1011).root_in_order_index(), idx(21));
-    assert_eq!(Forest::new(0b1111).root_in_order_index(), idx(29));
-
-    assert_eq!(Forest::new(0b0110).root_in_order_index(), idx(10));
-    assert_eq!(Forest::new(0b1010).root_in_order_index(), idx(18));
-    assert_eq!(Forest::new(0b1100).root_in_order_index(), idx(20));
-    assert_eq!(Forest::new(0b1110).root_in_order_index(), idx(26));
+    assert_eq!(Forest::new(0b0001).unwrap().root_in_order_index(), idx(1));
+    assert_eq!(Forest::new(0b0010).unwrap().root_in_order_index(), idx(2));
+    assert_eq!(Forest::new(0b0100).unwrap().root_in_order_index(), idx(4));
+    assert_eq!(Forest::new(0b1000).unwrap().root_in_order_index(), idx(8));
+
+    assert_eq!(Forest::new(0b0011).unwrap().root_in_order_index(), idx(5));
+    assert_eq!(Forest::new(0b0101).unwrap().root_in_order_index(), idx(9));
+    assert_eq!(Forest::new(0b1001).unwrap().root_in_order_index(), idx(17));
+    assert_eq!(Forest::new(0b0111).unwrap().root_in_order_index(), idx(13));
+    assert_eq!(Forest::new(0b1011).unwrap().root_in_order_index(), idx(21));
+    assert_eq!(Forest::new(0b1111).unwrap().root_in_order_index(), idx(29));
+
+    assert_eq!(Forest::new(0b0110).unwrap().root_in_order_index(), idx(10));
+    assert_eq!(Forest::new(0b1010).unwrap().root_in_order_index(), idx(18));
+    assert_eq!(Forest::new(0b1100).unwrap().root_in_order_index(), idx(20));
+    assert_eq!(Forest::new(0b1110).unwrap().root_in_order_index(), idx(26));
 }
 
 #[test]
@@ -177,26 +362,26 @@ fn test_forest_to_rightmost_index() {
 
     for forest in 1..256 {
         assert!(
-            Forest::new(forest).rightmost_in_order_index().inner() % 2 == 1,
+            Forest::new(forest).unwrap().rightmost_in_order_index().inner() % 2 == 1,
             "Leaves are always odd"
         );
     }
 
-    assert_eq!(Forest::new(0b0001).rightmost_in_order_index(), idx(1));
-    assert_eq!(Forest::new(0b0010).rightmost_in_order_index(), idx(3));
-    assert_eq!(Forest::new(0b0011).rightmost_in_order_index(), idx(5));
-    assert_eq!(Forest::new(0b0100).rightmost_in_order_index(), idx(7));
-    assert_eq!(Forest::new(0b0101).rightmost_in_order_index(), idx(9));
-    assert_eq!(Forest::new(0b0110).rightmost_in_order_index(), idx(11));
-    assert_eq!(Forest::new(0b0111).rightmost_in_order_index(), idx(13));
-    assert_eq!(Forest::new(0b1000).rightmost_in_order_index(), idx(15));
-    assert_eq!(Forest::new(0b1001).rightmost_in_order_index(), idx(17));
-    assert_eq!(Forest::new(0b1010).rightmost_in_order_index(), idx(19));
-    assert_eq!(Forest::new(0b1011).rightmost_in_order_index(), idx(21));
-    assert_eq!(Forest::new(0b1100).rightmost_in_order_index(), idx(23));
-    assert_eq!(Forest::new(0b1101).rightmost_in_order_index(), idx(25));
-    assert_eq!(Forest::new(0b1110).rightmost_in_order_index(), idx(27));
-    assert_eq!(Forest::new(0b1111).rightmost_in_order_index(), idx(29));
+    assert_eq!(Forest::new(0b0001).unwrap().rightmost_in_order_index(), idx(1));
+    assert_eq!(Forest::new(0b0010).unwrap().rightmost_in_order_index(), idx(3));
+    assert_eq!(Forest::new(0b0011).unwrap().rightmost_in_order_index(), idx(5));
+    assert_eq!(Forest::new(0b0100).unwrap().rightmost_in_order_index(), idx(7));
+    assert_eq!(Forest::new(0b0101).unwrap().rightmost_in_order_index(), idx(9));
+    assert_eq!(Forest::new(0b0110).unwrap().rightmost_in_order_index(), idx(11));
+    assert_eq!(Forest::new(0b0111).unwrap().rightmost_in_order_index(), idx(13));
+    assert_eq!(Forest::new(0b1000).unwrap().rightmost_in_order_index(), idx(15));
+    assert_eq!(Forest::new(0b1001).unwrap().rightmost_in_order_index(), idx(17));
+    assert_eq!(Forest::new(0b1010).unwrap().rightmost_in_order_index(), idx(19));
+    assert_eq!(Forest::new(0b1011).unwrap().rightmost_in_order_index(), idx(21));
+    assert_eq!(Forest::new(0b1100).unwrap().rightmost_in_order_index(), idx(23));
+    assert_eq!(Forest::new(0b1101).unwrap().rightmost_in_order_index(), idx(25));
+    assert_eq!(Forest::new(0b1110).unwrap().rightmost_in_order_index(), idx(27));
+    assert_eq!(Forest::new(0b1111).unwrap().rightmost_in_order_index(), idx(29));
 }
 
 #[test]
@@ -211,20 +396,20 @@ fn test_is_valid_in_order_index() {
 
     // Single tree forests (power of 2 leaves) have no separators
     // Forest with 1 leaf: valid indices are just 1
-    let forest_1 = Forest::new(0b0001);
+    let forest_1 = Forest::new(0b0001).unwrap();
     assert!(!forest_1.is_valid_in_order_index(&idx(2)), "index 2 is invalid");
     assert!(forest_1.is_valid_in_order_index(&idx(1)));
     assert!(!forest_1.is_valid_in_order_index(&idx(2)), "beyond bounds");
 
     // Forest with 2 leaves: valid indices are 1, 2, 3
-    let forest_2 = Forest::new(0b0010);
+    let forest_2 = Forest::new(0b0010).unwrap();
     assert!(forest_2.is_valid_in_order_index(&idx(1)));
     assert!(forest_2.is_valid_in_order_index(&idx(2)));
     assert!(forest_2.is_valid_in_order_index(&idx(3)));
     assert!(!forest_2.is_valid_in_order_index(&idx(4)), "beyond bounds");
 
     // Forest with 4 leaves: valid indices are 1-7
-    let forest_4 = Forest::new(0b0100);
+    let forest_4 = Forest::new(0b0100).unwrap();
     for i in 1..=7 {
         assert!(forest_4.is_valid_in_order_index(&idx(i)), "index {} should be valid", i);
     }
@@ -236,7 +421,7 @@ fn test_is_valid_in_order_index() {
     // Tree 2 (2 leaves): indices 9-11
     // Separator: index 12
     // Tree 3 (1 leaf): index 13
-    let forest_7 = Forest::new(0b0111);
+    let forest_7 = Forest::new(0b0111).unwrap();
 
     // Valid indices in first tree (4 leaves, 7 nodes)
     for i in 1..=7 {
@@ -275,7 +460,7 @@ fn test_is_valid_in_order_index() {
     // Tree 1 (4 leaves): indices 1-7
     // Separator: index 8
     // Tree 2 (2 leaves): indices 9-11
-    let forest_6 = Forest::new(0b0110);
+    let forest_6 = Forest::new(0b0110).unwrap();
     for i in 1..=7 {
         assert!(forest_6.is_valid_in_order_index(&idx(i)), "index {} should be valid", i);
     }
@@ -292,48 +477,50 @@ fn test_bit_position_iterator() {
     assert_eq!(TreeSizeIterator::new(Forest::empty()).rev().count(), 0);
 
     assert_eq!(
-        TreeSizeIterator::new(Forest::new(1)).collect::<Vec<Forest>>(),
-        vec![Forest::new(1)]
+        TreeSizeIterator::new(Forest::new(1).unwrap()).collect::<Vec<Forest>>(),
+        vec![Forest::new(1).unwrap()]
     );
     assert_eq!(
-        TreeSizeIterator::new(Forest::new(1)).rev().collect::<Vec<Forest>>(),
-        vec![Forest::new(1)],
+        TreeSizeIterator::new(Forest::new(1).unwrap()).rev().collect::<Vec<Forest>>(),
+        vec![Forest::new(1).unwrap()],
     );
 
     assert_eq!(
-        TreeSizeIterator::new(Forest::new(2)).collect::<Vec<Forest>>(),
-        vec![Forest::new(2)]
+        TreeSizeIterator::new(Forest::new(2).unwrap()).collect::<Vec<Forest>>(),
+        vec![Forest::new(2).unwrap()]
     );
     assert_eq!(
-        TreeSizeIterator::new(Forest::new(2)).rev().collect::<Vec<Forest>>(),
-        vec![Forest::new(2)],
+        TreeSizeIterator::new(Forest::new(2).unwrap()).rev().collect::<Vec<Forest>>(),
+        vec![Forest::new(2).unwrap()],
     );
 
     assert_eq!(
-        TreeSizeIterator::new(Forest::new(3)).collect::<Vec<Forest>>(),
-        vec![Forest::new(1), Forest::new(2)],
+        TreeSizeIterator::new(Forest::new(3).unwrap()).collect::<Vec<Forest>>(),
+        vec![Forest::new(1).unwrap(), Forest::new(2).unwrap()],
     );
     assert_eq!(
-        TreeSizeIterator::new(Forest::new(3)).rev().collect::<Vec<Forest>>(),
-        vec![Forest::new(2), Forest::new(1)],
+        TreeSizeIterator::new(Forest::new(3).unwrap()).rev().collect::<Vec<Forest>>(),
+        vec![Forest::new(2).unwrap(), Forest::new(1).unwrap()],
     );
 
     assert_eq!(
-        TreeSizeIterator::new(Forest::new(0b11010101)).collect::<Vec<Forest>>(),
+        TreeSizeIterator::new(Forest::new(0b11010101).unwrap()).collect::<Vec<Forest>>(),
         vec![0, 2, 4, 6, 7]
             .into_iter()
-            .map(|bit| Forest::new(1 << bit))
+            .map(|bit| Forest::new(1 << bit).unwrap())
             .collect::<Vec<_>>()
     );
     assert_eq!(
-        TreeSizeIterator::new(Forest::new(0b11010101)).rev().collect::<Vec<Forest>>(),
+        TreeSizeIterator::new(Forest::new(0b11010101).unwrap())
+            .rev()
+            .collect::<Vec<Forest>>(),
         vec![7, 6, 4, 2, 0]
             .into_iter()
-            .map(|bit| Forest::new(1 << bit))
+            .map(|bit| Forest::new(1 << bit).unwrap())
             .collect::<Vec<_>>()
     );
 
-    let forest = Forest::new(0b1101_0101);
+    let forest = Forest::new(0b1101_0101).unwrap();
     let mut it = TreeSizeIterator::new(forest);
 
     // 0b1101_0101
@@ -409,7 +596,7 @@ fn test_mmr_simple() {
     assert_eq!(mmr.forest().num_leaves(), 0);
     assert_eq!(mmr.nodes.len(), 0);
 
-    mmr.add(LEAVES[0]);
+    mmr.add(LEAVES[0]).unwrap();
     assert_eq!(mmr.forest().num_leaves(), 1);
     assert_eq!(mmr.nodes.len(), 1);
     assert_eq!(mmr.nodes.as_slice(), &postorder[0..mmr.nodes.len()]);
@@ -418,7 +605,7 @@ fn test_mmr_simple() {
     assert_eq!(acc.num_leaves(), 1);
     assert_eq!(acc.peaks(), &[postorder[0]]);
 
-    mmr.add(LEAVES[1]);
+    mmr.add(LEAVES[1]).unwrap();
     assert_eq!(mmr.forest().num_leaves(), 2);
     assert_eq!(mmr.nodes.len(), 3);
     assert_eq!(mmr.nodes.as_slice(), &postorder[0..mmr.nodes.len()]);
@@ -427,7 +614,7 @@ fn test_mmr_simple() {
     assert_eq!(acc.num_leaves(), 2);
     assert_eq!(acc.peaks(), &[postorder[2]]);
 
-    mmr.add(LEAVES[2]);
+    mmr.add(LEAVES[2]).unwrap();
     assert_eq!(mmr.forest().num_leaves(), 3);
     assert_eq!(mmr.nodes.len(), 4);
     assert_eq!(mmr.nodes.as_slice(), &postorder[0..mmr.nodes.len()]);
@@ -436,7 +623,7 @@ fn test_mmr_simple() {
     assert_eq!(acc.num_leaves(), 3);
     assert_eq!(acc.peaks(), &[postorder[2], postorder[3]]);
 
-    mmr.add(LEAVES[3]);
+    mmr.add(LEAVES[3]).unwrap();
     assert_eq!(mmr.forest().num_leaves(), 4);
     assert_eq!(mmr.nodes.len(), 7);
     assert_eq!(mmr.nodes.as_slice(), &postorder[0..mmr.nodes.len()]);
@@ -445,7 +632,7 @@ fn test_mmr_simple() {
     assert_eq!(acc.num_leaves(), 4);
     assert_eq!(acc.peaks(), &[postorder[6]]);
 
-    mmr.add(LEAVES[4]);
+    mmr.add(LEAVES[4]).unwrap();
     assert_eq!(mmr.forest().num_leaves(), 5);
     assert_eq!(mmr.nodes.len(), 8);
     assert_eq!(mmr.nodes.as_slice(), &postorder[0..mmr.nodes.len()]);
@@ -454,7 +641,7 @@ fn test_mmr_simple() {
     assert_eq!(acc.num_leaves(), 5);
     assert_eq!(acc.peaks(), &[postorder[6], postorder[7]]);
 
-    mmr.add(LEAVES[5]);
+    mmr.add(LEAVES[5]).unwrap();
     assert_eq!(mmr.forest().num_leaves(), 6);
     assert_eq!(mmr.nodes.len(), 10);
     assert_eq!(mmr.nodes.as_slice(), &postorder[0..mmr.nodes.len()]);
@@ -463,7 +650,7 @@ fn test_mmr_simple() {
     assert_eq!(acc.num_leaves(), 6);
     assert_eq!(acc.peaks(), &[postorder[6], postorder[9]]);
 
-    mmr.add(LEAVES[6]);
+    mmr.add(LEAVES[6]).unwrap();
     assert_eq!(mmr.forest().num_leaves(), 7);
     assert_eq!(mmr.nodes.len(), 11);
     assert_eq!(mmr.nodes.as_slice(), &postorder[0..mmr.nodes.len()]);
@@ -475,7 +662,7 @@ fn test_mmr_simple() {
 
 #[test]
 fn test_mmr_open() {
-    let mmr: Mmr = LEAVES.into();
+    let mmr = Mmr::try_from_iter(LEAVES.iter().copied()).unwrap();
     let h01 = merge(LEAVES[0], LEAVES[1]);
     let h23 = merge(LEAVES[2], LEAVES[3]);
 
@@ -551,15 +738,15 @@ fn test_mmr_open() {
 
 #[test]
 fn test_mmr_open_older_version() {
-    let mmr: Mmr = LEAVES.into();
+    let mmr = Mmr::try_from_iter(LEAVES.iter().copied()).unwrap();
 
     fn is_even(v: &usize) -> bool {
         v & 1 == 0
     }
 
     // merkle path of a node is empty if there are no elements to pair with it
     for pos in (0..mmr.forest().num_leaves()).filter(is_even) {
-        let forest = Forest::new(pos + 1);
+        let forest = Forest::new(pos + 1).unwrap();
         let proof = mmr.open_at(pos, forest).unwrap();
         assert_eq!(proof.path().forest(), forest);
         assert_eq!(proof.path().merkle_path().nodes(), []);
@@ -569,7 +756,7 @@ fn test_mmr_open_older_version() {
     // openings match that of a merkle tree
     let mtree: MerkleTree = LEAVES[..4].try_into().unwrap();
     for forest in 4..=LEAVES.len() {
-        let forest = Forest::new(forest);
+        let forest = Forest::new(forest).unwrap();
         for pos in 0..4 {
             let idx = NodeIndex::new(2, pos).unwrap();
             let path = mtree.get_path(idx).unwrap();
@@ -579,7 +766,7 @@ fn test_mmr_open_older_version() {
     }
     let mtree: MerkleTree = LEAVES[4..6].try_into().unwrap();
     for forest in 6..=LEAVES.len() {
-        let forest = Forest::new(forest);
+        let forest = Forest::new(forest).unwrap();
         for pos in 0..2 {
             let idx = NodeIndex::new(1, pos).unwrap();
             let path = mtree.get_path(idx).unwrap();
@@ -606,8 +793,8 @@ fn test_mmr_open_eight() {
     ];
 
     let mtree: MerkleTree = leaves.as_slice().try_into().unwrap();
-    let forest = Forest::new(leaves.len());
-    let mmr: Mmr = leaves.into();
+    let forest = Forest::new(leaves.len()).unwrap();
+    let mmr = Mmr::try_from_iter(leaves.iter().copied()).unwrap();
     let root = mtree.root();
 
     let position = 0;
@@ -745,8 +932,8 @@ fn test_mmr_open_seven() {
     let mtree1: MerkleTree = LEAVES[..4].try_into().unwrap();
     let mtree2: MerkleTree = LEAVES[4..6].try_into().unwrap();
 
-    let forest = Forest::new(LEAVES.len());
-    let mmr: Mmr = LEAVES.into();
+    let forest = Forest::new(LEAVES.len()).unwrap();
+    let mmr = Mmr::try_from_iter(LEAVES.iter().copied()).unwrap();
 
     let position = 0;
     let proof = mmr.open(position).unwrap();
@@ -818,7 +1005,7 @@ fn test_mmr_open_seven() {
 
 #[test]
 fn test_mmr_get() {
-    let mmr: Mmr = LEAVES.into();
+    let mmr = Mmr::try_from_iter(LEAVES.iter().copied()).unwrap();
     assert_eq!(mmr.get(0).unwrap(), LEAVES[0], "value at pos 0 must correspond");
     assert_eq!(mmr.get(1).unwrap(), LEAVES[1], "value at pos 1 must correspond");
     assert_eq!(mmr.get(2).unwrap(), LEAVES[2], "value at pos 2 must correspond");
@@ -833,7 +1020,7 @@ fn test_mmr_get() {
 fn test_mmr_invariants() {
     let mut mmr = Mmr::new();
     for v in 1..=1028 {
-        mmr.add(int_to_node(v));
+        mmr.add(int_to_node(v)).unwrap();
         let accumulator = mmr.peaks();
         assert_eq!(
             v as usize,
@@ -865,7 +1052,7 @@ fn test_mmr_invariants() {
 
 #[test]
 fn test_mmr_inner_nodes() {
-    let mmr: Mmr = LEAVES.into();
+    let mmr = Mmr::try_from_iter(LEAVES.iter().copied()).unwrap();
     let nodes: Vec<InnerNodeInfo> = mmr.inner_nodes().collect();
 
     let h01 = Poseidon2::merge(&[LEAVES[0], LEAVES[1]]);
@@ -896,47 +1083,47 @@ fn test_mmr_inner_nodes() {
 
 #[test]
 fn test_mmr_peaks() {
-    let mmr: Mmr = LEAVES.into();
+    let mmr = Mmr::try_from_iter(LEAVES.iter().copied()).unwrap();
 
-    let forest = Forest::new(0b0001);
+    let forest = Forest::new(0b0001).unwrap();
     let acc = mmr.peaks_at(forest).unwrap();
     assert_eq!(acc.num_leaves(), forest.num_leaves());
     assert_eq!(acc.peaks(), &[mmr.nodes[0]]);
 
-    let forest = Forest::new(0b0010);
+    let forest = Forest::new(0b0010).unwrap();
     let acc = mmr.peaks_at(forest).unwrap();
     assert_eq!(acc.num_leaves(), forest.num_leaves());
     assert_eq!(acc.peaks(), &[mmr.nodes[2]]);
 
-    let forest = Forest::new(0b0011);
+    let forest = Forest::new(0b0011).unwrap();
     let acc = mmr.peaks_at(forest).unwrap();
     assert_eq!(acc.num_leaves(), forest.num_leaves());
     assert_eq!(acc.peaks(), &[mmr.nodes[2], mmr.nodes[3]]);
 
-    let forest = Forest::new(0b0100);
+    let forest = Forest::new(0b0100).unwrap();
     let acc = mmr.peaks_at(forest).unwrap();
     assert_eq!(acc.num_leaves(), forest.num_leaves());
     assert_eq!(acc.peaks(), &[mmr.nodes[6]]);
 
-    let forest = Forest::new(0b0101);
+    let forest = Forest::new(0b0101).unwrap();
     let acc = mmr.peaks_at(forest).unwrap();
     assert_eq!(acc.num_leaves(), forest.num_leaves());
     assert_eq!(acc.peaks(), &[mmr.nodes[6], mmr.nodes[7]]);
 
-    let forest = Forest::new(0b0110);
+    let forest = Forest::new(0b0110).unwrap();
     let acc = mmr.peaks_at(forest).unwrap();
     assert_eq!(acc.num_leaves(), forest.num_leaves());
     assert_eq!(acc.peaks(), &[mmr.nodes[6], mmr.nodes[9]]);
 
-    let forest = Forest::new(0b0111);
+    let forest = Forest::new(0b0111).unwrap();
     let acc = mmr.peaks_at(forest).unwrap();
     assert_eq!(acc.num_leaves(), forest.num_leaves());
     assert_eq!(acc.peaks(), &[mmr.nodes[6], mmr.nodes[9], mmr.nodes[10]]);
 }
 
 #[test]
 fn test_mmr_hash_peaks() {
-    let mmr: Mmr = LEAVES.into();
+    let mmr = Mmr::try_from_iter(LEAVES.iter().copied()).unwrap();
     let peaks = mmr.peaks();
 
     let first_peak = Poseidon2::merge(&[
@@ -962,7 +1149,7 @@ fn test_mmr_peaks_hash_less_than_16() {
     for i in 0..16 {
         peaks.push(int_to_node(i));
 
-        let forest = Forest::new(1 << peaks.len()).all_smaller_trees().unwrap();
+        let forest = Forest::new(1 << peaks.len()).unwrap().all_smaller_trees().unwrap();
         let accumulator = MmrPeaks::new(forest, peaks.clone()).unwrap();
 
         // minimum length is 16
@@ -979,7 +1166,7 @@ fn test_mmr_peaks_hash_less_than_16() {
 fn test_mmr_peaks_hash_odd() {
     let peaks: Vec<_> = (0..=17).map(int_to_node).collect();
 
-    let forest = Forest::new(1 << peaks.len()).all_smaller_trees_unchecked();
+    let forest = Forest::new(1 << peaks.len()).unwrap().all_smaller_trees_unchecked();
     let accumulator = MmrPeaks::new(forest, peaks.clone()).unwrap();
 
     // odd length bigger than 16 is padded to the next even number
@@ -993,59 +1180,62 @@ fn test_mmr_peaks_hash_odd() {
 
 #[test]
 fn test_mmr_delta() {
-    let mmr: Mmr = LEAVES.into();
+    let mmr = Mmr::try_from_iter(LEAVES.iter().copied()).unwrap();
     let acc = mmr.peaks();
 
     // original_forest can't have more elements
     assert!(
-        mmr.get_delta(Forest::new(LEAVES.len() + 1), mmr.forest()).is_err(),
+        mmr.get_delta(Forest::new(LEAVES.len() + 1).unwrap(), mmr.forest()).is_err(),
         "Can not provide updates for a newer Mmr"
     );
 
     // if the number of elements is the same there is no change
     assert!(
-        mmr.get_delta(Forest::new(LEAVES.len()), mmr.forest()).unwrap().data.is_empty(),
+        mmr.get_delta(Forest::new(LEAVES.len()).unwrap(), mmr.forest())
+            .unwrap()
+            .data
+            .is_empty(),
         "There are no updates for the same Mmr version"
     );
 
     // missing the last element added, which is itself a tree peak
     assert_eq!(
-        mmr.get_delta(Forest::new(6), mmr.forest()).unwrap().data,
+        mmr.get_delta(Forest::new(6).unwrap(), mmr.forest()).unwrap().data,
         vec![acc.peaks()[2]],
         "one peak"
     );
 
     // missing the sibling to complete the tree of depth 2, and the last element
     assert_eq!(
-        mmr.get_delta(Forest::new(5), mmr.forest()).unwrap().data,
+        mmr.get_delta(Forest::new(5).unwrap(), mmr.forest()).unwrap().data,
         vec![LEAVES[5], acc.peaks()[2]],
         "one sibling, one peak"
     );
 
     // missing the whole last two trees, only send the peaks
     assert_eq!(
-        mmr.get_delta(Forest::new(4), mmr.forest()).unwrap().data,
+        mmr.get_delta(Forest::new(4).unwrap(), mmr.forest()).unwrap().data,
         vec![acc.peaks()[1], acc.peaks()[2]],
         "two peaks"
     );
 
     // missing the sibling to complete the first tree, and the two last trees
     assert_eq!(
-        mmr.get_delta(Forest::new(3), mmr.forest()).unwrap().data,
+        mmr.get_delta(Forest::new(3).unwrap(), mmr.forest()).unwrap().data,
         vec![LEAVES[3], acc.peaks()[1], acc.peaks()[2]],
         "one sibling, two peaks"
     );
 
     // missing half of the first tree, only send the computed element (not the leaves), and the new
     // peaks
     assert_eq!(
-        mmr.get_delta(Forest::new(2), mmr.forest()).unwrap().data,
+        mmr.get_delta(Forest::new(2).unwrap(), mmr.forest()).unwrap().data,
         vec![mmr.nodes[5], acc.peaks()[1], acc.peaks()[2]],
         "one sibling, two peaks"
     );
 
     assert_eq!(
-        mmr.get_delta(Forest::new(1), mmr.forest()).unwrap().data,
+        mmr.get_delta(Forest::new(1).unwrap(), mmr.forest()).unwrap().data,
         vec![LEAVES[1], mmr.nodes[5], acc.peaks()[1], acc.peaks()[2]],
         "one sibling, two peaks"
     );
@@ -1059,16 +1249,19 @@ fn test_mmr_delta() {
 
 #[test]
 fn test_mmr_delta_old_forest() {
-    let mmr: Mmr = LEAVES.into();
+    let mmr = Mmr::try_from_iter(LEAVES.iter().copied()).unwrap();
 
     // from_forest must be smaller-or-equal to to_forest
     for version in 1..=mmr.forest().num_leaves() {
-        assert!(mmr.get_delta(Forest::new(version + 1), Forest::new(version)).is_err());
+        assert!(
+            mmr.get_delta(Forest::new(version + 1).unwrap(), Forest::new(version).unwrap())
+                .is_err()
+        );
     }
 
     // when from_forest and to_forest are equal, there are no updates
     for version in 1..=mmr.forest().num_leaves() {
-        let version = Forest::new(version);
+        let version = Forest::new(version).unwrap();
         let delta = mmr.get_delta(version, version).unwrap();
         assert!(delta.data.is_empty());
         assert_eq!(delta.forest, version);
@@ -1078,8 +1271,8 @@ fn test_mmr_delta_old_forest() {
     for count in 0..(mmr.forest().num_leaves() / 2) {
         // *2 because every iteration tests a pair
         // +1 because the Mmr is 1-indexed
-        let from_forest = Forest::new((count * 2) + 1);
-        let to_forest = Forest::new((count * 2) + 2);
+        let from_forest = Forest::new((count * 2) + 1).unwrap();
+        let to_forest = Forest::new((count * 2) + 2).unwrap();
         let delta = mmr.get_delta(from_forest, to_forest).unwrap();
 
         // *2 because every iteration tests a pair
@@ -1089,20 +1282,20 @@ fn test_mmr_delta_old_forest() {
         assert_eq!(delta.forest, to_forest);
     }
 
-    let version = Forest::new(4);
-    let delta = mmr.get_delta(Forest::new(1), version).unwrap();
+    let version = Forest::new(4).unwrap();
+    let delta = mmr.get_delta(Forest::new(1).unwrap(), version).unwrap();
     assert_eq!(delta.data, [mmr.nodes[1], mmr.nodes[5]]);
     assert_eq!(delta.forest, version);
 
-    let version = Forest::new(5);
-    let delta = mmr.get_delta(Forest::new(1), version).unwrap();
+    let version = Forest::new(5).unwrap();
+    let delta = mmr.get_delta(Forest::new(1).unwrap(), version).unwrap();
     assert_eq!(delta.data, [mmr.nodes[1], mmr.nodes[5], mmr.nodes[7]]);
     assert_eq!(delta.forest, version);
 }
 
 #[test]
 fn test_partial_mmr_simple() {
-    let mmr: Mmr = LEAVES.into();
+    let mmr = Mmr::try_from_iter(LEAVES.iter().copied()).unwrap();
     let peaks = mmr.peaks();
     let mut partial: PartialMmr = peaks.clone().into();
 
@@ -1153,7 +1346,7 @@ fn test_partial_mmr_simple() {
 fn test_partial_mmr_update_single() {
     let mut full = Mmr::new();
     let zero = int_to_node(0);
-    full.add(zero);
+    full.add(zero).unwrap();
     let mut partial: PartialMmr = full.peaks().into();
 
     let proof = full.open(0).unwrap();
@@ -1163,7 +1356,7 @@ fn test_partial_mmr_update_single() {
 
     for i in 1..100 {
         let node = int_to_node(i as u64);
-        full.add(node);
+        full.add(node).unwrap();
         let delta = full.get_delta(partial.forest(), full.forest()).unwrap();
         partial.apply(delta).unwrap();
 
@@ -1181,7 +1374,7 @@ fn test_partial_mmr_update_single() {
 
 #[test]
 fn test_mmr_add_invalid_odd_leaf() {
-    let mmr: Mmr = LEAVES.into();
+    let mmr = Mmr::try_from_iter(LEAVES.iter().copied()).unwrap();
     let acc = mmr.peaks();
     let mut partial: PartialMmr = acc.clone().into();
 
@@ -1197,16 +1390,57 @@ fn test_mmr_add_invalid_odd_leaf() {
     assert!(result.is_ok());
 }
 
+#[test]
+fn test_partial_track_rejects_path_depth_too_large() {
+    let leaf = int_to_node(1);
+    let mut full = Mmr::new();
+    full.add(leaf).unwrap();
+    let mut partial: PartialMmr = full.peaks().into();
+
+    let deep_path = MerklePath::new(vec![Word::empty(); u8::MAX as usize]);
+    let result = partial.track(0, leaf, &deep_path);
+    assert_matches!(result, Err(MmrError::UnknownPeak(depth)) if depth == u8::MAX);
+}
+
+#[test]
+fn test_get_delta_and_apply_never_return_forest_size_exceeded_for_valid_forests() {
+    let mut full = Mmr::new();
+    full.add(int_to_node(0)).unwrap();
+    let mut partial: PartialMmr = full.peaks().into();
+
+    for i in 1..256 {
+        full.add(int_to_node(i as u64)).unwrap();
+
+        let delta = match full.get_delta(partial.forest(), full.forest()) {
+            Ok(delta) => delta,
+            Err(MmrError::ForestSizeExceeded { .. }) => {
+                panic!("valid get_delta range should not exceed forest bounds")
+            },
+            Err(err) => panic!("unexpected get_delta error: {err}"),
+        };
+
+        if let Err(err) = partial.apply(delta) {
+            match err {
+                MmrError::ForestSizeExceeded { .. } => {
+                    panic!("applying a valid delta should not exceed forest bounds")
+                },
+                _ => panic!("unexpected apply error: {err}"),
+            }
+        }
+    }
+}
+
 /// Tests that a proof whose peak count exceeds the peak count of the MMR returns an error.
 ///
 /// Here we manipulate the proof to return a peak index of 1 while the MMR only has 1 peak (with
 /// index 0).
 #[test]
 fn test_mmr_proof_num_peaks_exceeds_current_num_peaks() {
-    let mmr: Mmr = LEAVES[0..4].iter().cloned().into();
+    let mmr = Mmr::try_from_iter(LEAVES[0..4].iter().cloned()).unwrap();
     let original_proof = mmr.open(3).unwrap();
     // Create an invalid proof with wrong forest and position
-    let invalid_path = MmrPath::new(Forest::new(5), 4, original_proof.path().merkle_path().clone());
+    let invalid_path =
+        MmrPath::new(Forest::new(5).unwrap(), 4, original_proof.path().merkle_path().clone());
     let invalid_proof = MmrProof::new(invalid_path, original_proof.leaf());
     let err = mmr.peaks().verify(LEAVES[3], invalid_proof).unwrap_err();
     assert_matches!(
@@ -1224,13 +1458,13 @@ fn test_mmr_proof_num_peaks_exceeds_current_num_peaks() {
 #[test]
 fn test_mmr_old_proof_num_peaks_exceeds_current_num_peaks() {
     let leaves_len = 3;
-    let mut mmr = Mmr::from(LEAVES[0..leaves_len].iter().cloned());
+    let mut mmr = Mmr::try_from_iter(LEAVES[0..leaves_len].iter().cloned()).unwrap();
 
     let leaf_idx = leaves_len - 1;
     let proof = mmr.open(leaf_idx).unwrap();
     assert!(mmr.peaks().verify(LEAVES[leaf_idx], proof.clone()).is_ok());
 
-    mmr.add(LEAVES[leaves_len]);
+    mmr.add(LEAVES[leaves_len]).unwrap();
     let err = mmr.peaks().verify(LEAVES[leaf_idx], proof).unwrap_err();
     assert_matches!(
         err,
@@ -1242,11 +1476,11 @@ fn test_mmr_old_proof_num_peaks_exceeds_current_num_peaks() {
 mod property_tests {
     use proptest::prelude::*;
 
-    use super::leaf_to_corresponding_tree;
+    use super::{Forest, leaf_to_corresponding_tree};
 
     proptest! {
         #[test]
-        fn test_last_position_is_always_contained_in_the_last_tree(leaves in any::<usize>().prop_filter("can't have an empty tree", |v| *v != 0)) {
+        fn test_last_position_is_always_contained_in_the_last_tree(leaves in 1..=Forest::MAX_LEAVES) {
             let last_pos = leaves - 1;
             let lowest_bit = leaves.trailing_zeros();
 
@@ -1259,7 +1493,7 @@ mod property_tests {
 
     proptest! {
         #[test]
-        fn test_contained_tree_is_always_power_of_two((leaves, pos) in any::<usize>().prop_flat_map(|v| (Just(v), 0..v))) {
+        fn test_contained_tree_is_always_power_of_two((leaves, pos) in (1..=Forest::MAX_LEAVES).prop_flat_map(|v| (Just(v), 0..v))) {
             let tree_bit = leaf_to_corresponding_tree(pos, leaves).expect("pos is smaller than leaves, there should always be a corresponding tree");
             let mask = 1usize << tree_bit;
 
@@ -1284,10 +1518,10 @@ fn merge(l: Word, r: Word) -> Word {
 /// Given a leaf index and the current forest, return the tree number responsible for
 /// the position.
 fn leaf_to_corresponding_tree(leaf_idx: usize, forest: usize) -> Option<u32> {
-    Forest::new(forest).leaf_to_corresponding_tree(leaf_idx)
+    Forest::new(forest).unwrap().leaf_to_corresponding_tree(leaf_idx)
 }
 
 /// Return the total number of nodes of a given forest
-const fn nodes_in_forest(forest: usize) -> usize {
-    Forest::new(forest).num_nodes()
+fn nodes_in_forest(forest: usize) -> usize {
+    nodes_from_mask(forest)
 }
```
