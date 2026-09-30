# [?] Merge pull request #1137 from topos-protocol/fix-kernel-panic

## Summary
Severity: Unknown
Chain: ZK
Component: 0xPolygonZero/plonky2
Published: 2023-07-17
Source: https://github.com/0xPolygonZero/plonky2/commit/152e395903e35eb8a70375590d1ca32d40dcab0b
Type: security-commit

## Details
Merge pull request #1137 from topos-protocol/fix-kernel-panic

Change context used in `bignum_modmul`

## Patch
### evm/src/generation/prover_input.rs
```diff
@@ -192,11 +192,12 @@ impl<F: Field> GenerationState<F> {
         b_start_loc: usize,
         m_start_loc: usize,
     ) -> (Vec<U256>, Vec<U256>) {
-        let a = &self.memory.contexts[0].segments[Segment::KernelGeneral as usize].content
+        let n = self.memory.contexts.len();
+        let a = &self.memory.contexts[n - 1].segments[Segment::KernelGeneral as usize].content
             [a_start_loc..a_start_loc + len];
-        let b = &self.memory.contexts[0].segments[Segment::KernelGeneral as usize].content
+        let b = &self.memory.contexts[n - 1].segments[Segment::KernelGeneral as usize].content
             [b_start_loc..b_start_loc + len];
-        let m = &self.memory.contexts[0].segments[Segment::KernelGeneral as usize].content
+        let m = &self.memory.contexts[n - 1].segments[Segment::KernelGeneral as usize].content
             [m_start_loc..m_start_loc + len];
 
         let a_biguint = mem_vec_to_biguint(a);
```
