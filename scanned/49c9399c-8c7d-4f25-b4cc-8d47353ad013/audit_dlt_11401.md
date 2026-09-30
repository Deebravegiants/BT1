# [?] fix/keccak-decode-overflow: calculate with bitshifts in u64 (#1262)

## Summary
Severity: Unknown
Chain: ZK
Component: privacy-ethereum/zkevm-circuits
Published: 2023-02-27
Source: https://github.com/privacy-ethereum/zkevm-circuits/commit/35c4f5c7324a3ef3212c5f8e5fcbeb731d40dff2
Type: security-commit

## Details
fix/keccak-decode-overflow: calculate with bitshifts in u64 (#1262)

### Description

With `KECCAK_DEGREE=19`, `get_num_bits_per_absorb_lookup()` is 11. In
some places, `2**3**11` overflows `u32`.

Replace with `u64`. Also use faster bitshifts like Axiom’s version.

### Issue Link

Port fix from Scroll
https://github.com/scroll-tech/zkevm-circuits/pull/335

### Type of change

- [x] Bug fix (non-breaking change which fixes an issue)
- [ ] New feature (non-breaking change which adds functionality)
- [ ] Breaking change (fix or feature that would cause existing
functionality to not work as expected)
- [ ] This change requires a documentation update

### Contents

- Compute in `u64`

### How Has This Been Tested?

    cargo test -p zkevm-circuits --features test --release -- keccak

Co-authored-by: Aurélien Nicolas <info@nau.re>

## Patch
### zkevm-circuits/src/keccak_circuit/keccak_packed_multi.rs
```diff
@@ -105,20 +105,20 @@ impl<F: FieldExt> KeccakRegion<F> {
 /// Recombines parts back together
 pub(crate) mod decode {
     use super::{Part, PartValue};
-    use crate::keccak_circuit::param::BIT_SIZE;
+    use crate::keccak_circuit::param::BIT_COUNT;
     use crate::util::Expr;
     use eth_types::Field;
     use halo2_proofs::plonk::Expression;
 
     pub(crate) fn expr<F: Field>(parts: Vec<Part<F>>) -> Expression<F> {
         parts.iter().rev().fold(0.expr(), |acc, part| {
-            acc * F::from((BIT_SIZE as u32).pow(part.num_bits as u32) as u64) + part.expr.clone()
+            acc * F::from(1u64 << (BIT_COUNT * part.num_bits)) + part.expr.clone()
         })
     }
 
     pub(crate) fn value<F: Field>(parts: Vec<PartValue<F>>) -> F {
         parts.iter().rev().fold(F::zero(), |acc, part| {
-            acc * F::from((BIT_SIZE as u32).pow(part.num_bits as u32) as u64) + part.value
+            acc * F::from(1u64 << (BIT_COUNT * part.num_bits)) + part.value
         })
     }
 }
@@ -197,8 +197,8 @@ pub(crate) mod split {
 // table layout in `output_cells` regardless of rotation.
 pub(crate) mod split_uniform {
     use super::{decode, target_part_sizes, Cell, CellManager, KeccakRegion, Part, PartValue};
+    use crate::keccak_circuit::param::BIT_COUNT;
     use crate::keccak_circuit::util::{pack, pack_part, rotate, rotate_rev, unpack, WordParts};
-    use crate::keccak_circuit::BIT_SIZE;
     use crate::{evm_circuit::util::constraint_builder::BaseConstraintBuilder, util::Expr};
     use eth_types::Field;
     use halo2_proofs::plonk::{ConstraintSystem, Expression};
@@ -248,8 +248,7 @@ pub(crate) mod split_uniform {
 
                 // Make sure the parts combined equal the value in the uniform output
                 let expr = part_a.expr()
-                    + part_b.expr()
-                        * F::from((BIT_SIZE as u32).pow(word_part.bits.len() as u32) as u64);
+                    + part_b.expr() * F::from(1u64 << (BIT_COUNT * word_part.bits.len()));
                 cb.require_equal("rot part", expr, output_cells[counter].expr());
 
                 // Input needs the two parts because it needs to be able to undo the rotation
@@ -332,7 +331,7 @@ pub(crate) mod split_uniform {
                 part_a.assign(region, 0, F::from(value_a));
                 part_b.assign(region, 0, F::from(value_b));
 
-                let value = value_a + value_b * (BIT_SIZE as u64).pow(word_part.bits.len() as u32);
+                let value = value_a + value_b * (1u64 << (BIT_COUNT * word_part.bits.len()));
 
                 output_cells[counter].assign(region, 0, F::from(value));
 
```
