# [?] Fix stack overflow

## Summary
Severity: Unknown
Chain: ZK
Component: 0xPolygonZero/plonky2
Published: 2023-01-11
Source: https://github.com/0xPolygonZero/plonky2/commit/be7a489c6ea1509c30b6de70ff4c323ef8309f55
Type: security-commit

## Details
Fix stack overflow

## Patch
### evm/src/keccak/keccak_stark.rs
```diff
@@ -74,11 +74,8 @@ impl<F: RichField + Extendable<D>, const D: usize> KeccakStark<F, D> {
         rows
     }
 
-    fn generate_trace_rows_for_perm(
-        &self,
-        input: [u64; NUM_INPUTS],
-    ) -> [[F; NUM_COLUMNS]; NUM_ROUNDS] {
-        let mut rows = [[F::ZERO; NUM_COLUMNS]; NUM_ROUNDS];
+    fn generate_trace_rows_for_perm(&self, input: [u64; NUM_INPUTS]) -> Vec<[F; NUM_COLUMNS]> {
+        let mut rows = vec![[F::ZERO; NUM_COLUMNS]; NUM_ROUNDS];
 
         // Populate the preimage for each row.
         for round in 0..24 {
```
