# [?] fix modulo soundness due to overflow (#999)

## Summary
Severity: Unknown
Chain: ZK
Component: privacy-ethereum/zkevm-circuits
Published: 2022-12-29
Source: https://github.com/privacy-ethereum/zkevm-circuits/commit/b51ededfe930ecdf449f31e22ec35986fd59363f
Type: security-commit

## Details
fix modulo soundness due to overflow (#999)

* fix modulo soundness due to overflow

* misc comment

Co-authored-by: Wu Sung Ming <wusm@sea.com>

## Patch
### zkevm-circuits/src/evm_circuit/execution/mulmod.rs
```diff
@@ -120,8 +120,12 @@ impl<F: Field> ExecutionGadget<F> for MulModGadget<F> {
         self.words[1].assign(region, offset, Some(b.to_le_bytes()))?;
         self.words[2].assign(region, offset, Some(n.to_le_bytes()))?;
         self.words[3].assign(region, offset, Some(r.to_le_bytes()))?;
-        // 1. Reduction of a mod n
-        let a_reduced = if n.is_zero() { U256::zero() } else { a % n };
+        // 1. quotient and reduction of a mod n
+        let (k1, a_reduced) = if n.is_zero() {
+            (U256::zero(), U256::zero())
+        } else {
+            a.div_mod(n)
+        };
 
         // 2. Compute r = a*b mod n
         let prod = a_reduced.full_mul(b);
@@ -130,25 +134,25 @@ impl<F: Field> ExecutionGadget<F> for MulModGadget<F> {
         let d = U256::from_little_endian(&prod_bytes[32..64]);
         let e = U256::from_little_endian(&prod_bytes[0..32]);
 
-        let (r, k) = if n.is_zero() {
+        let (r, k2) = if n.is_zero() {
             (U256::zero(), U256::zero())
         } else {
             // k2 <= b , always fits in U256
             (r, U256::try_from(prod / n).unwrap())
         };
 
-        self.k.assign(region, offset, Some(k.to_le_bytes()))?;
+        self.k.assign(region, offset, Some(k2.to_le_bytes()))?;
         self.a_reduced
             .assign(region, offset, Some(a_reduced.to_le_bytes()))?;
         self.d.assign(region, offset, Some(d.to_le_bytes()))?;
         self.e.assign(region, offset, Some(e.to_le_bytes()))?;
 
         self.modword
-            .assign(region, offset, a, n, a_reduced, block.randomness)?;
+            .assign(region, offset, a, n, a_reduced, k1, block.randomness)?;
         self.mul512_left
             .assign(region, offset, [a_reduced, b, d, e], None)?;
         self.mul512_right
-            .assign(region, offset, [k, n, d, e], Some(r))?;
+            .assign(region, offset, [k2, n, d, e], Some(r))?;
 
         self.lt.assign(region, offset, r, n)?;
 
```

### zkevm-circuits/src/evm_circuit/util/math_gadget/modulo.rs
```diff
@@ -20,7 +20,7 @@ use halo2_proofs::plonk::Error;
 pub(crate) struct ModGadget<F> {
     k: util::Word<F>,
     a_or_zero: util::Word<F>,
-    mul: MulAddWordsGadget<F>,
+    mul_add_words: MulAddWordsGadget<F>,
     n_is_zero: IsZeroGadget<F>,
     a_or_is_zero: IsZeroGadget<F>,
     eq: IsEqualGadget<F>,
@@ -33,11 +33,11 @@ impl<F: Field> ModGadget<F> {
         let a_or_zero = cb.query_word();
         let n_is_zero = IsZeroGadget::construct(cb, sum::expr(&n.cells));
         let a_or_is_zero = IsZeroGadget::construct(cb, sum::expr(&a_or_zero.cells));
-        let mul = MulAddWordsGadget::construct(cb, [&k, n, r, &a_or_zero]);
+        let mul_add_words = MulAddWordsGadget::construct(cb, [&k, n, r, &a_or_zero]);
         let eq = IsEqualGadget::construct(cb, a.expr(), a_or_zero.expr());
         let lt = LtWordGadget::construct(cb, r, n);
-        // Constraint the aux variable a_or_zero to be =a or =0 if n==0:
-        // (a == a_zero) ^ (n == 0 & a_or_zero == 0)
+        // Constrain the aux variable a_or_zero to be =a or =0 if n==0:
+        // (a == a_or_zero) ^ (n == 0 & a_or_zero == 0)
         cb.add_constraint(
             " (1 - (a == a_or_zero)) * ( 1 - (n == 0) * (a_or_zero == 0)",
             (1.expr() - eq.expr()) * (1.expr() - n_is_zero.expr() * a_or_is_zero.expr()),
@@ -49,27 +49,31 @@ impl<F: Field> ModGadget<F> {
             1.expr() - lt.expr() - n_is_zero.expr(),
         );
 
+        // Constrain k * n + r no overflow
+        cb.add_constraint("overflow == 0 for k * n + r", mul_add_words.overflow());
+
         Self {
             k,
             a_or_zero,
-            mul,
+            mul_add_words,
             n_is_zero,
             a_or_is_zero,
             eq,
             lt,
         }
     }
 
+    #[allow(clippy::too_many_arguments)]
     pub(crate) fn assign(
         &self,
         region: &mut CachedRegion<'_, '_, F>,
         offset: usize,
         a: Word,
         n: Word,
         r: Word,
+        k: Word,
         randomness: F,
     ) -> Result<(), Error> {
-        let k = if n.is_zero() { Word::zero() } else { a / n };
         let a_or_zero = if n.is_zero() { Word::zero() } else { a };
 
         self.k.assign(region, offset, Some(k.to_le_bytes()))?;
@@ -80,7 +84,8 @@ impl<F: Field> ModGadget<F> {
         self.n_is_zero.assign(region, offset, F::from(n_sum))?;
         self.a_or_is_zero
             .assign(region, offset, F::from(a_or_zero_sum))?;
-        self.mul.assign(region, offset, [k, n, r, a_or_zero])?;
+        self.mul_add_words
+            .assign(region, offset, [k, n, r, a_or_zero])?;
         self.lt.assign(region, offset, r, n)?;
         self.eq.assign(
             region,
@@ -97,7 +102,7 @@ impl<F: Field> ModGadget<F> {
 mod tests {
     use super::test_util::*;
     use super::*;
-    use eth_types::Word;
+    use eth_types::{Word, U256, U512};
     use halo2_proofs::halo2curves::bn256::Fr;
     use halo2_proofs::plonk::Error;
 
@@ -131,14 +136,20 @@ mod tests {
         ) -> Result<(), Error> {
             let a = witnesses[0];
             let n = witnesses[1];
-            let a_reduced = witnesses[2];
+            let r = witnesses[2];
+            let k =
+                witnesses
+                    .get(3)
+                    .copied()
+                    .unwrap_or(if n.is_zero() { Word::zero() } else { a / n });
+
             let offset = 0;
 
             self.a.assign(region, offset, Some(a.to_le_bytes()))?;
             self.n.assign(region, offset, Some(n.to_le_bytes()))?;
-            self.r
-                .assign(region, offset, Some(a_reduced.to_le_bytes()))?;
-            self.mod_gadget.assign(region, 0, a, n, a_reduced, F::one())
+            self.r.assign(region, offset, Some(r.to_le_bytes()))?;
+
+            self.mod_gadget.assign(region, 0, a, n, r, k, F::one())
         }
     }
 
@@ -183,6 +194,25 @@ mod tests {
 
     #[test]
     fn test_mod_n_unexpected_rem() {
+        // test soundness by manipulating k to make a' = k * n + r and a' >=
+        // 2^256 cause overflow and trigger soundness bug: (a' != a) ^ a' ≡ a
+        // (mod 2^256)
+        // Here, the attacker tries to convince you of a false statement `2 % 3 = 0` by
+        // showing you `2 = ((2^256 + 2) / 3) * 3 + 0`. In the `MulAddWordsGadget`, `k *
+        // n + r = a  (modulo 2**256)` would have been a valid statement. But the gadget
+        // would have the overflow = 1. Since we constrain the overflow to be 0 in the
+        // ModGadget, the statement would be invalid in the ModGadget.
+        try_test!(
+            ModGadgetTestContainer<Fr>,
+            vec![
+                Word::from(2),
+                Word::from(3),
+                Word::from(0),
+                /* magic number (2^256 + 2) / 3, and 2^256 + 2 is divisible by 3 */
+                U256::try_from(U512([2, 0, 0, 0, 1, 0, 0, 0]) / U512::from(3)).unwrap(),
+            ],
+            false,
+        );
         try_test!(
             ModGadgetTestContainer<Fr>,
             vec![Word::from(1), Word::from(1), Word::from(1)],
```

### zkevm-circuits/src/evm_circuit/util/math_gadget/mul_add_words.rs
```diff
@@ -124,8 +124,8 @@ impl<F: Field> MulAddWordsGadget<F> {
             + a_limbs[2] * b_limbs[1]
             + a_limbs[3] * b_limbs[0];
 
-        let carry_lo = (t0 + (t1 << 64) + c_lo - d_lo) >> 128;
-        let carry_hi = (t2 + (t3 << 64) + c_hi + carry_lo - d_hi) >> 128;
+        let carry_lo = (t0 + (t1 << 64) + c_lo).saturating_sub(d_lo) >> 128;
+        let carry_hi = (t2 + (t3 << 64) + c_hi + carry_lo).saturating_sub(d_hi) >> 128;
 
         self.carry_lo
             .iter()
@@ -347,7 +347,20 @@ mod tests {
             false,
         );
 
-        // 100 * 54 + low_max == low_max + 5400, no overflow
+        // 1 * 1 + 1 != word_max, no underflow
+        try_test!(
+            MulAddGadgetContainer<Fr>,
+            vec![
+                Word::from(1),
+                Word::from(1),
+                Word::from(1),
+                Word::MAX,
+                Word::from(0)
+            ],
+            false,
+        );
+
+        // 100 * 54 + high_max == high_max + 5400, no overflow
         try_test!(
             MulAddGadgetContainer<Fr>,
             vec![
@@ -360,7 +373,7 @@ mod tests {
             false,
         );
 
-        // high_max + low_max + 1 == 0 with overflow 1
+        // (low_max + 1) * 1 + high_max == 0 with overflow 1
         try_test!(
             MulAddGadgetContainer<Fr>,
             vec![
```
