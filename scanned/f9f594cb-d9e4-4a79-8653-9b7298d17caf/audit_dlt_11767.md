# [?] Avoid panic in reindex_by_subdomain

## Summary
Severity: Unknown
Chain: Aleo
Component: AleoNet/snarkVM-test
Published: 2024-01-12
Source: https://github.com/AleoNet/snarkVM-test/commit/11f69bac85c80657676cf6e668c6bb5f291888da
Type: security-commit

## Details
Avoid panic in reindex_by_subdomain

## Patch
### algorithms/src/fft/domain.rs
```diff
@@ -319,7 +319,7 @@ impl<F: FftField> EvaluationDomain<F> {
     /// Given an index in the `other` subdomain, return an index into this domain `self`
     /// This assumes the `other`'s elements are also `self`'s first elements
     pub fn reindex_by_subdomain(&self, other: &Self, index: usize) -> Result<usize> {
-        ensure!(self.size() >= other.size(), "other.size() must be smaller than self.size()");
+        ensure!(self.size() > other.size(), "other.size() must be smaller than self.size()");
 
         // Let this subgroup be G, and the subgroup we're re-indexing by be S.
         // Since its a subgroup, the 0th element of S is at index 0 in G, the first element of S is at
```
