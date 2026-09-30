# [?] fix: notify caller of `hypercube_iter` panic

## Summary
Severity: Unknown
Chain: ZK
Component: succinctlabs/sp1
Published: 2025-09-22
Source: https://github.com/succinctlabs/sp1/commit/14c3b6da2d315c4f439364161df7629e1d6645c1
Type: security-commit

## Details
fix: notify caller of `hypercube_iter` panic

## Patch
### slop/crates/multilinear/src/mle.rs
```diff
@@ -257,13 +257,20 @@ impl<T> Mle<T, CpuBackend> {
 
     /// Returns an iterator over the evaluations of the MLE on the Boolean hypercube.
     ///
+    /// Panics
+    ///
+    /// If self.num_non_zero_entries() != 1 << self.num_variables()
+    ///
     /// The iterator yields a slice for each index of the Boolean hypercube.
     pub fn hypercube_iter(&self) -> impl Iterator<Item = &[T]>
     where
         T: AbstractField,
     {
         let width = self.num_polynomials();
         let height = self.num_variables();
+
+        assert_eq!(self.num_non_zero_entries(), 1 << height);
+
         (0..(1 << height)).map(move |i| &self.guts.as_slice()[i * width..(i + 1) * width])
     }
 
```
