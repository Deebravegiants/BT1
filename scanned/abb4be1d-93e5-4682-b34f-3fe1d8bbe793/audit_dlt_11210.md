# [?] small fix to outer to avoid overflow (#1032)

## Summary
Severity: Unknown
Chain: ZK
Component: a16z/jolt
Published: 2025-10-21
Source: https://github.com/a16z/jolt/commit/cdcdeee2f63f49106bfebd95d54a5276b65729f8
Type: security-commit

## Details
small fix to outer to avoid overflow (#1032)

## Patch
### jolt-core/src/field/mod.rs
```diff
@@ -1,5 +1,5 @@
 use allocative::Allocative;
-use ark_ff::UniformRand;
+use ark_ff::{BigInt, UniformRand};
 use num_traits::{One, Zero};
 use std::fmt::{Debug, Display};
 use std::hash::Hash;
@@ -124,6 +124,7 @@ pub trait JoltField:
         + Ord
         + From<u128>
         + From<[u64; N]>
+        + From<BigInt<N>>
         + Zero
         + FmaddTrunc<Other<2> = Self::Unreduced<2>, Acc<7> = Self::Unreduced<7>>
         + FmaddTrunc<Other<2> = Self::Unreduced<2>, Acc<8> = Self::Unreduced<8>>
```

### jolt-core/src/utils/accumulation.rs
```diff
@@ -419,9 +419,7 @@ impl<F: JoltField> AccumulateInPlace<F, S160> for Acc7S<F> {
         if other.is_zero() {
             return;
         }
-        let lo = other.magnitude_lo();
-        let hi = other.magnitude_hi() as u64;
-        let mag = <F as JoltField>::Unreduced::from([lo[0], lo[1], hi]);
+        let mag = <F as JoltField>::Unreduced::from(other.magnitude_as_bigint_nplus1());
         let field_bigint = field.as_unreduced_ref();
         if other.is_positive() {
             field_bigint.fmadd_trunc::<3, 7>(&mag, &mut self.pos);
@@ -446,8 +444,7 @@ impl<F: JoltField> AccumulateInPlace<F, S192> for Acc7S<F> {
         if other.magnitude_limbs() == [0u64; 3] {
             return;
         }
-        let limbs = other.magnitude_limbs();
-        let mag = <F as JoltField>::Unreduced::from([limbs[0], limbs[1], limbs[2]]);
+        let mag = <F as JoltField>::Unreduced::from(other.magnitude);
         let field_bigint = field.as_unreduced_ref();
         if other.sign() {
             field_bigint.fmadd_trunc::<3, 7>(&mag, &mut self.pos);
@@ -467,56 +464,134 @@ impl<F: JoltField> AccumulateInPlace<F, S192> for Acc7S<F> {
 }
 
 // ------------------------------
-// 8-limb Montgomery accumulators (Signed Acc8) for SVO / round-compression
+// 8-limb Montgomery accumulators (Acc8U/Acc8S) for SVO / round-compression
 // NOTE:
-// - reduce_to_field uses Montgomery reduction (faster than Barrett) and yields
-//   Montgomery-form field elements. Callers must account for the Montgomery factor
-//   (e.g., multiply by F::MONTGOMERY_R_SQUARE elsewhere if converting conventions).
+// - reduce() uses Montgomery reduction (faster than Barrett) and yields canonical field elements.
 // - Accumulator safety: fmadd_trunc performs bounded modular folding. Ensure the
 //   number of fmadd calls per accumulator instance matches the bounds guaranteed
 //   by the implementation; otherwise periodically reduce and re-accumulate.
 // ------------------------------
 
-pub type Acc8SignedAccumulator<F> = <F as JoltField>::Unreduced<8>;
-
 #[derive(Clone, Copy, Debug, PartialEq, Eq)]
-pub struct Acc8Signed<F: JoltField> {
-    pub pos: Acc8SignedAccumulator<F>,
-    pub neg: Acc8SignedAccumulator<F>,
+pub struct Acc8U<F: JoltField> {
+    pub word: <F as JoltField>::Unreduced<8>,
 }
 
-impl<F: JoltField> Default for Acc8Signed<F> {
+impl<F: JoltField> Default for Acc8U<F> {
+    #[inline(always)]
     fn default() -> Self {
         Self {
-            pos: <F as JoltField>::Unreduced::<8>::from([0u64; 8]),
-            neg: <F as JoltField>::Unreduced::<8>::from([0u64; 8]),
+            word: <F as JoltField>::Unreduced::<8>::from([0u64; 8]),
         }
     }
 }
 
-impl<F: JoltField> Acc8Signed<F> {
+impl<F: JoltField> Acc8U<F> {
     #[inline(always)]
     pub fn new() -> Self {
         Self::default()
     }
+    #[inline(always)]
+    pub fn reduce(&self) -> F {
+        F::from_montgomery_reduce(self.word)
+    }
+}
 
+impl<F: JoltField> AccumulateInPlace<F, u128> for Acc8U<F> {
     #[inline(always)]
-    pub fn fmadd_s128(&mut self, field: &F, v: S128) {
-        if v.is_zero() {
+    fn fmadd(&mut self, field: &F, other: &u128) {
+        if *other == 0 {
             return;
         }
-        let limbs = v.magnitude_as_u128();
-        let result = field.mul_u128_unreduced(limbs);
-        if v.is_positive {
-            self.pos += result;
-        } else {
-            self.neg += result;
+        self.word += field.mul_u128_unreduced(*other);
+    }
+    #[inline(always)]
+    fn reduce(&self) -> F {
+        Acc8U::<F>::reduce(self)
+    }
+    #[inline(always)]
+    fn combine(&mut self, other: &Self) {
+        self.word += other.word;
+    }
+}
+
+impl<F: JoltField> AccumulateInPlace<F, u64> for Acc8U<F> {
+    #[inline(always)]
+    fn fmadd(&mut self, field: &F, other: &u64) {
+        if *other == 0 {
+            return;
         }
+        self.word += field.mul_u64_unreduced(*other);
+    }
+    #[inline(always)]
+    fn reduce(&self) -> F {
+        Acc8U::<F>::reduce(self)
+    }
+    #[inline(always)]
+    fn combine(&mut self, other: &Self) {
+        self.word += other.word;
     }
+}
+
+impl<F: JoltField> AccumulateInPlace<F, u8> for Acc8U<F> {
+    #[inline(always)]
+    fn fmadd(&mut self, field: &F, other: &u8) {
+        let v = *other as u64;
+        if v == 0 {
+            return;
+        }
+        self.word += field.mul_u64_unreduced(v);
+    }
+    #[inline(always)]
+    fn reduce(&self) -> F {
+        Acc8U::<F>::reduce(self)
+    }
+    #[inline(always)]
+    fn combine(&mut self, other: &Self) {
+        self.word += other.word;
+    }
+}
+
+impl<F: JoltField> AccumulateInPlace<F, bool> for Acc8U<F> {
+    #[inline(always)]
+    fn fmadd(&mut self, field: &F, other: &bool) {
+        if *other {
+            self.word += *field.as_unreduced_ref();
+        }
+    }
+    #[inline(always)]
+    fn reduce(&self) -> F {
+        Acc8U::<F>::reduce(self)
+    }
+    #[inline(always)]
+    fn combine(&mut self, other: &Self) {
+        self.word += other.word;
+    }
+}
+
+#[derive(Clone, Copy, Debug, PartialEq, Eq)]
+pub struct Acc8S<F: JoltField> {
+    pub pos: <F as JoltField>::Unreduced<8>,
+    pub neg: <F as JoltField>::Unreduced<8>,
+}
 
-    /// Reduce accumulated value to a field element (pos - neg) using Montgomery reduction.
+impl<F: JoltField> Default for Acc8S<F> {
     #[inline(always)]
-    pub fn reduce_to_field(&self) -> F {
+    fn default() -> Self {
+        Self {
+            pos: <F as JoltField>::Unreduced::<8>::from([0u64; 8]),
+            neg: <F as JoltField>::Unreduced::<8>::from([0u64; 8]),
+        }
+    }
+}
+
+impl<F: JoltField> Acc8S<F> {
+    #[inline(always)]
+    pub fn new() -> Self {
+        Self::default()
+    }
+    #[inline(always)]
+    pub fn reduce(&self) -> F {
         let result = if self.pos >= self.neg {
             F::from_montgomery_reduce(self.pos - self.neg)
         } else {
@@ -532,17 +607,77 @@ impl<F: JoltField> Acc8Signed<F> {
     }
 }
 
-#[inline(always)]
-pub fn acc8s_fmadd_s256<F: JoltField>(acc: &mut Acc8Signed<F>, field: &F, v: S256) {
-    if v.magnitude_limbs() == [0u64; 4] {
-        return;
+impl<F: JoltField> AccumulateInPlace<F, S128> for Acc8S<F> {
+    #[inline(always)]
+    fn fmadd(&mut self, field: &F, other: &S128) {
+        if other.is_zero() {
+            return;
+        }
+        let limbs = other.magnitude_as_u128();
+        let term = field.mul_u128_unreduced(limbs);
+        if other.is_positive {
+            self.pos += term;
+        } else {
+            self.neg += term;
+        }
+    }
+    #[inline(always)]
+    fn reduce(&self) -> F {
+        Acc8S::<F>::reduce(self)
+    }
+    #[inline(always)]
+    fn combine(&mut self, other: &Self) {
+        self.pos += other.pos;
+        self.neg += other.neg;
+    }
+}
+
+impl<F: JoltField> AccumulateInPlace<F, S192> for Acc8S<F> {
+    #[inline(always)]
+    fn fmadd(&mut self, field: &F, other: &S192) {
+        if other.magnitude_limbs() == [0u64; 3] {
+            return;
+        }
+        let mag = <F as JoltField>::Unreduced::from(other.magnitude);
+        let field_bigint = field.as_unreduced_ref();
+        if other.sign() {
+            field_bigint.fmadd_trunc::<3, 8>(&mag, &mut self.pos);
+        } else {
+            field_bigint.fmadd_trunc::<3, 8>(&mag, &mut self.neg);
+        }
+    }
+    #[inline(always)]
+    fn reduce(&self) -> F {
+        Acc8S::<F>::reduce(self)
+    }
+    #[inline(always)]
+    fn combine(&mut self, other: &Self) {
+        self.pos += other.pos;
+        self.neg += other.neg;
     }
-    let limbs = v.magnitude_limbs(); // [l0, l1, l2, l3]
-    let mag = <F as JoltField>::Unreduced::from([limbs[0], limbs[1], limbs[2], limbs[3]]);
-    let field_bigint = field.as_unreduced_ref();
-    if v.sign() {
-        field_bigint.fmadd_trunc::<4, 8>(&mag, &mut acc.pos);
-    } else {
-        field_bigint.fmadd_trunc::<4, 8>(&mag, &mut acc.neg);
+}
+
+impl<F: JoltField> AccumulateInPlace<F, S256> for Acc8S<F> {
+    #[inline(always)]
+    fn fmadd(&mut self, field: &F, other: &S256) {
+        if other.magnitude_limbs() == [0u64; 4] {
+            return;
+        }
+        let mag = <F as JoltField>::Unreduced::from(other.magnitude);
+        let field_bigint = field.as_unreduced_ref();
+        if other.sign() {
+            field_bigint.fmadd_trunc::<4, 8>(&mag, &mut self.pos);
+        } else {
+            field_bigint.fmadd_trunc::<4, 8>(&mag, &mut self.neg);
+        }
+    }
+    #[inline(always)]
+    fn reduce(&self) -> F {
+        Acc8S::<F>::reduce(self)
+    }
+    #[inline(always)]
+    fn combine(&mut self, other: &Self) {
+        self.pos += other.pos;
+        self.neg += other.neg;
     }
 }
```

### jolt-core/src/zkvm/spartan/outer.rs
```diff
@@ -21,7 +21,7 @@ use crate::subprotocols::univariate_skip::{
     build_uniskip_first_round_poly, uniskip_targets, UniSkipState,
 };
 use crate::transcripts::Transcript;
-use crate::utils::accumulation::Acc7S;
+use crate::utils::accumulation::Acc8S;
 use crate::utils::math::Math;
 #[cfg(feature = "allocative")]
 use crate::utils::profiling::print_data_structure_heap_usage;
@@ -153,8 +153,11 @@ impl<F: JoltField> OuterUniSkipInstance<F> {
 
         let m = tau_low.len() / 2;
         let (tau_out, tau_in) = tau_low.split_at(m);
+        // Compute the split eq polynomial, one scaled by R^2 in order to balance against
+        // Montgomery (not Barrett) reduction later on in 8-limb signed accumulation
+        // of e_in * (az * bz)
         let (E_out, E_in) = rayon::join(
-            || EqPolynomial::evals(tau_out),
+            || EqPolynomial::evals_with_scaling(tau_out, Some(F::MONTGOMERY_R_SQUARE)),
             || EqPolynomial::evals(tau_in),
         );
 
@@ -188,8 +191,8 @@ impl<F: JoltField> OuterUniSkipInstance<F> {
                     [F::zero(); UNIVARIATE_SKIP_DEGREE];
 
                 for x_out_val in x_out_start..x_out_end {
-                    let mut inner_acc: [Acc7S<F>; UNIVARIATE_SKIP_DEGREE] =
-                        [Acc7S::<F>::new(); UNIVARIATE_SKIP_DEGREE];
+                    let mut inner_acc: [Acc8S<F>; UNIVARIATE_SKIP_DEGREE] =
+                        [Acc8S::<F>::new(); UNIVARIATE_SKIP_DEGREE];
                     for x_in_prime in 0..num_x_in_half {
                         // Materialize row once for both groups (ignores last bit)
                         let base_step_idx = (x_out_val << iter_num_x_in_prime_vars) | x_in_prime;
@@ -270,7 +273,7 @@ impl<F: JoltField> OuterUniSkipInstance<F> {
                             let coeffs = &coeffs_per_j[j];
                             // (sum_i c_i * Az1_i) * (sum_i c_i * Bz1_i)
                             let mut sum_c_az1_i64: i64 = 0;
-                            let mut sum_bz1_s160 = S160::from(0i128);
+                            let mut sum_bz1_s192 = S192::from(0i128);
                             for i in 0..UNIVARIATE_SKIP_DOMAIN_SIZE {
                                 let c = coeffs[i] as i64;
 
@@ -280,18 +283,17 @@ impl<F: JoltField> OuterUniSkipInstance<F> {
                                     // Optimization: if az is non-zero then bz must be zero
                                     // so we can skip the bz multiplication
                                 } else {
-                                    let c_s160 = S160::from(c);
-                                    let term: S160 = (&c_s160) * (&bz1_s160_padded[i]);
-                                    sum_bz1_s160 += term;
+                                    let term: S192 = S192::from(c)
+                                        * bz1_s160_padded[i].to_signed_bigint_nplus1::<3>();
+                                    sum_bz1_s192 += term;
                                 }
                             }
                             // Convert S160 -> S192 once outside summation, then S64 * S192 -> S192
-                            let sum_bz1_s192: S192 = sum_bz1_s160.to_signed_bigint_nplus1::<3>();
                             let sum_az1_s64 = S64::from_i64(sum_c_az1_i64);
-                            let prod_s192 = sum_az1_s64.mul_trunc::<3, 3>(&sum_bz1_s192);
+                            let prod_s256 = sum_az1_s64.mul_trunc::<3, 4>(&sum_bz1_s192);
 
                             // Fold E_in (odd) into 7-limb signed accumulator for this j
-                            inner_acc[j].fmadd(&e_in_odd, &prod_s192);
+                            inner_acc[j].fmadd(&e_in_odd, &prod_s256);
                         }
                     }
                     let e_out = E_out[x_out_val];
```

### jolt-core/src/zkvm/spartan/product.rs
```diff
@@ -3,7 +3,7 @@ use ark_std::Zero;
 use std::cell::RefCell;
 use std::rc::Rc;
 
-use crate::field::JoltField;
+use crate::field::{AccumulateInPlace, JoltField};
 use crate::poly::commitment::commitment_scheme::CommitmentScheme;
 use crate::poly::dense_mlpoly::DensePolynomial;
 use crate::poly::eq_poly::EqPolynomial;
@@ -19,7 +19,7 @@ use crate::subprotocols::univariate_skip::{
     build_uniskip_first_round_poly, uniskip_targets, UniSkipState,
 };
 use crate::transcripts::Transcript;
-use crate::utils::accumulation::{acc8s_fmadd_s256, Acc8Signed};
+use crate::utils::accumulation::Acc8S;
 use crate::utils::math::Math;
 #[cfg(feature = "allocative")]
 use crate::utils::profiling::print_data_structure_heap_usage;
@@ -181,7 +181,8 @@ impl<F: JoltField> ProductVirtualUniSkipInstance<F> {
         let m = tau_low.len() / 2;
         let (tau_out, tau_in) = tau_low.split_at(m);
         // Compute the split eq polynomial, one scaled by R^2 in order to balance against
-        // Montgomery (not Barrett) reduction later on in signed accumulation of e_in * (left * right)
+        // Montgomery (not Barrett) reduction later on in 8-limb signed accumulation
+        // of e_in * (left * right)
         let (E_out, E_in) = rayon::join(
             || EqPolynomial::evals_with_scaling(tau_out, Some(F::MONTGOMERY_R_SQUARE)),
             || EqPolynomial::evals(tau_in),
@@ -229,8 +230,8 @@ impl<F: JoltField> ProductVirtualUniSkipInstance<F> {
                 for x_out_val in x_out_start..x_out_end {
                     let e_out = E_out[x_out_val];
                     // Accumulate across x_in using 8-limb signed accumulators per j
-                    let mut inner_acc: [Acc8Signed<F>; PRODUCT_VIRTUAL_UNIVARIATE_SKIP_DEGREE] =
-                        [Acc8Signed::<F>::new(); PRODUCT_VIRTUAL_UNIVARIATE_SKIP_DEGREE];
+                    let mut inner_acc: [Acc8S<F>; PRODUCT_VIRTUAL_UNIVARIATE_SKIP_DEGREE] =
+                        [Acc8S::<F>::new(); PRODUCT_VIRTUAL_UNIVARIATE_SKIP_DEGREE];
                     for x_in_val in 0..num_x_in_vals {
                         let e_in = if num_x_in_vals == 1 {
                             E_in[0]
@@ -297,13 +298,13 @@ impl<F: JoltField> ProductVirtualUniSkipInstance<F> {
                             let prod_s256 = left_s128.mul_trunc::<2, 4>(&right_s128);
 
                             // Fold e_in into signed 8-limb accumulator for this j
-                            acc8s_fmadd_s256(&mut inner_acc[j], &e_in, prod_s256);
+                            inner_acc[j].fmadd(&e_in, &prod_s256);
                         }
                     }
                     // Reduce inner accumulators (pos-neg Montgomery) and multiply by E_out
                     // NOTE: needs a R^2 correction factor, applied when initializing E_out
                     for j in 0..PRODUCT_VIRTUAL_UNIVARIATE_SKIP_DEGREE {
-                        let reduced = inner_acc[j].reduce_to_field();
+                        let reduced = inner_acc[j].reduce();
                         local_acc_unr[j] += e_out.mul_unreduced::<9>(reduced);
                     }
                 }
```
