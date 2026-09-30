# [?] fix: avoid an overflow when summing batch sizes

## Summary
Severity: Unknown
Chain: Aleo
Component: AleoNet/snarkVM-test
Published: 2024-01-11
Source: https://github.com/AleoNet/snarkVM-test/commit/50886d5578ebfeab7817d60f33fe810658ac15e0
Type: security-commit

## Details
fix: avoid an overflow when summing batch sizes

Signed-off-by: ljedrz <ljedrz@gmail.com>

## Patch
### algorithms/src/snark/varuna/data_structures/proof.rs
```diff
@@ -88,7 +88,7 @@ impl<E: PairingEngine> Commitments<E> {
         compress: Compress,
         validate: Validate,
     ) -> Result<Self, snarkvm_utilities::SerializationError> {
-        let mut w = Vec::with_capacity(batch_sizes.iter().sum());
+        let mut w = Vec::new();
         for batch_size in batch_sizes {
             w.extend(deserialize_vec_without_len(&mut reader, compress, validate, *batch_size)?);
         }
@@ -261,7 +261,11 @@ impl<E: PairingEngine> Proof<E> {
 
     /// Check that the number of messages is consistent with our batch size
     pub fn check_batch_sizes(&self) -> Result<(), SNARKError> {
-        let total_instances = self.batch_sizes.iter().sum::<usize>();
+        let total_instances = self
+            .batch_sizes
+            .iter()
+            .try_fold(0usize, |acc, &size| acc.checked_add(size))
+            .ok_or(SNARKError::BatchSizeMismatch)?;
         if self.commitments.witness_commitments.len() != total_instances {
             return Err(SNARKError::BatchSizeMismatch);
         }
```
