# [?] Overflow fixes

## Summary
Severity: Unknown
Chain: ZK
Component: 0xPolygonZero/plonky2
Published: 2021-10-05
Source: https://github.com/0xPolygonZero/plonky2/commit/6d601c6113911ba32708cc38b26e251605253d1f
Type: security-commit

## Details
Overflow fixes

## Patch
### src/gadgets/split_join.rs
```diff
@@ -16,7 +16,7 @@ impl<F: RichField + Extendable<D>, const D: usize> CircuitBuilder<F, D> {
         if num_bits == 0 {
             return Vec::new();
         }
-        let bits_per_gate = self.config.num_routed_wires - BaseSumGate::<2>::START_LIMBS;
+        let bits_per_gate = 63.min(self.config.num_routed_wires - BaseSumGate::<2>::START_LIMBS);
         let k = ceil_div_usize(num_bits, bits_per_gate);
         let gates = (0..k)
             .map(|_| self.add_gate(BaseSumGate::<2>::new(bits_per_gate), vec![]))
```

### src/gates/comparison.rs
```diff
@@ -23,6 +23,7 @@ pub struct ComparisonGate<F: PrimeField + Extendable<D>, const D: usize> {
 
 impl<F: RichField + Extendable<D>, const D: usize> ComparisonGate<F, D> {
     pub fn new(num_bits: usize, num_chunks: usize) -> Self {
+        debug_assert!(num_bits < 64);
         Self {
             num_bits,
             num_chunks,
```
