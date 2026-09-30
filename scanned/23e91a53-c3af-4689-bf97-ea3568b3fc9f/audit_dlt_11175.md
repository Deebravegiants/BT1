# [?] fix: validate forest in Mmr::open_at to prevent OOB access (#553)

## Summary
Severity: Unknown
Chain: Miden
Component: 0xMiden/miden-vm
Published: 2025-09-30
Source: https://github.com/0xMiden/miden-vm/commit/6a53a6e7a86b0cc035a607e6a3096acf0e617990
Type: security-commit

## Details
fix: validate forest in Mmr::open_at to prevent OOB access (#553)

## Patch
### miden-crypto/src/merkle/mmr/error.rs
```diff
@@ -10,6 +10,8 @@ pub enum MmrError {
     PositionNotFound(usize),
     #[error("mmr peaks are invalid: {0}")]
     InvalidPeaks(String),
+    #[error("mmr forest is out of bounds: requested {0} > current {1}")]
+    ForestOutOfBounds(usize, usize),
     #[error("mmr peak does not match the computed merkle root of the provided authentication path")]
     PeakPathMismatch,
     #[error("requested peak index is {peak_idx} but the number of peaks is {peaks_len}")]
```

### miden-crypto/src/merkle/mmr/full.rs
```diff
@@ -97,6 +97,9 @@ impl Mmr {
     /// - The specified leaf position is out of bounds for this MMR.
     /// - The specified `forest` value is not valid for this MMR.
     pub fn open_at(&self, pos: usize, forest: Forest) -> Result<MmrProof, MmrError> {
+        if forest > self.forest {
+            return Err(MmrError::ForestOutOfBounds(forest.num_leaves(), self.forest.num_leaves()));
+        }
         let (_, path) = self.collect_merkle_path_and_value(pos, forest)?;
 
         Ok(MmrProof {
@@ -150,10 +153,7 @@ impl Mmr {
     /// Returns an error if the specified `forest` value is not valid for this MMR.
     pub fn peaks_at(&self, forest: Forest) -> Result<MmrPeaks, MmrError> {
         if forest > self.forest {
-            return Err(MmrError::InvalidPeaks(format!(
-                "requested forest {forest} exceeds current forest {}",
-                self.forest
-            )));
+            return Err(MmrError::ForestOutOfBounds(forest.num_leaves(), self.forest.num_leaves()));
         }
 
         let peaks: Vec<Word> = TreeSizeIterator::new(forest)
@@ -177,11 +177,17 @@ impl Mmr {
     /// The result is a packed sequence of the authentication elements required to update the trees
     /// that have been merged together, followed by the new peaks of the [Mmr].
     pub fn get_delta(&self, from_forest: Forest, to_forest: Forest) -> Result<MmrDelta, MmrError> {
-        if to_forest > self.forest || from_forest > to_forest {
-            return Err(MmrError::InvalidPeaks(format!(
-                "to_forest {to_forest} exceeds the current forest {} or from_forest {from_forest} exceeds to_forest",
-                self.forest
-            )));
+        if to_forest > self.forest {
+            return Err(MmrError::ForestOutOfBounds(
+                to_forest.num_leaves(),
+                self.forest.num_leaves(),
+            ));
+        }
+        if from_forest > to_forest {
+            return Err(MmrError::ForestOutOfBounds(
+                from_forest.num_leaves(),
+                to_forest.num_leaves(),
+            ));
         }
 
         if from_forest == to_forest {
```
