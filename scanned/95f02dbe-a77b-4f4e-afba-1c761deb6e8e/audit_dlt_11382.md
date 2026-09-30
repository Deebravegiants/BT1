# [?] fix overflow dot_product_5 neon (#1429)

## Summary
Severity: Unknown
Chain: ZK
Component: Plonky3/Plonky3
Published: 2026-03-12
Source: https://github.com/Plonky3/Plonky3/commit/5c2650786bfe1ccec09da0363c3bf397e152c791
Type: security-commit

## Details
fix overflow dot_product_5 neon (#1429)

* fix overflow dot_product_5 neon

* fmt

* monty31: optimize dot_product_5 with 3+2 split and add generic overflow test

Use a 3+2 group split instead of overflow detection to handle 5*(P-1)^2 > u64:
- Group A (3 terms): safe, c_hi < 2P → 1 conditional sub
- Group B (2 terms): safe, c_hi < P → no reduction
- Merge via carry propagation with ILP-friendly ordering
- Single Montgomery reduction (same as dot_product_4)

Also:
- Add N=8 routing in general_dot_product to dispatch to dot_product_8
- Move dot_product overflow test into test_packed_field macro (all packed types)
- Remove KoalaBear-specific overflow test (now covered generically)

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>

* fmt

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>

* restore missing safety doc on dot_product_5

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>

---------

Co-authored-by: Tom Wambsgans <TomWambsgans@users.noreply.github.com>
Co-authored-by: Thomas Coratger <thomas.coratger@gmail.com>
Co-authored-by: Claude Opus 4.6 <noreply@anthropic.com>

## Patch
### field-testing/src/packedfield_testing.rs
```diff
@@ -397,6 +397,51 @@ where
     );
 }
 
+/// Test dot products with maximum field values (P-1) to catch overflow bugs.
+///
+/// This verifies that SIMD dot product implementations handle the edge case where
+/// `N*(P-1)^2` can overflow `u64` (which happens for N >= 5 with 31-bit primes).
+pub fn test_dot_product_boundary<PF>()
+where
+    PF: PackedField + Eq,
+{
+    let big = PF::from(PF::Scalar::NEG_ONE);
+    let scalar_big = PF::Scalar::NEG_ONE;
+
+    // Test dot_product for N = 1..=16 with all-maximum inputs.
+    macro_rules! test_dot_n {
+        ($n:literal) => {
+            let packed_result = PF::dot_product::<$n>(&[big; $n], &[big; $n]);
+            let scalar_result = PF::Scalar::dot_product::<$n>(&[scalar_big; $n], &[scalar_big; $n]);
+            for lane in 0..PF::WIDTH {
+                assert_eq!(
+                    packed_result.as_slice()[lane],
+                    scalar_result,
+                    "dot_product::<{}> overflow mismatch at lane {}",
+                    $n,
+                    lane,
+                );
+            }
+        };
+    }
+    test_dot_n!(1);
+    test_dot_n!(2);
+    test_dot_n!(3);
+    test_dot_n!(4);
+    test_dot_n!(5);
+    test_dot_n!(6);
+    test_dot_n!(7);
+    test_dot_n!(8);
+    test_dot_n!(9);
+    test_dot_n!(10);
+    test_dot_n!(11);
+    test_dot_n!(12);
+    test_dot_n!(13);
+    test_dot_n!(14);
+    test_dot_n!(15);
+    test_dot_n!(16);
+}
+
 #[macro_export]
 macro_rules! test_packed_field {
     ($packedfield:ty, $zeros:expr, $ones:expr, $specials:expr) => {
@@ -425,6 +470,10 @@ macro_rules! test_packed_field {
             fn test_multiplicative_inverse() {
                 $crate::test_multiplicative_inverse::<$packedfield>();
             }
+            #[test]
+            fn test_dot_product_boundary() {
+                $crate::test_dot_product_boundary::<$packedfield>();
+            }
         }
     };
 }
```

### koala-bear/src/aarch64_neon/packing.rs
```diff
@@ -17,6 +17,7 @@ pub type PackedKoalaBearNeon = PackedMontyField31Neon<KoalaBearParameters>;
 
 #[cfg(test)]
 mod tests {
+    use p3_field::{PackedValue, PrimeCharacteristicRing};
     use p3_field_testing::test_packed_field;
 
     use super::WIDTH;
```

### monty-31/src/aarch64_neon/packing.rs
```diff
@@ -761,6 +761,22 @@ where
                 &[rhs[0], rhs[1], rhs[2], rhs[3]],
             )
         },
+        5 => unsafe {
+            dot_product_5(
+                &[lhs[0], lhs[1], lhs[2], lhs[3], lhs[4]],
+                &[rhs[0], rhs[1], rhs[2], rhs[3], rhs[4]],
+            )
+        },
+        8 => unsafe {
+            dot_product_8(
+                &[
+                    lhs[0], lhs[1], lhs[2], lhs[3], lhs[4], lhs[5], lhs[6], lhs[7],
+                ],
+                &[
+                    rhs[0], rhs[1], rhs[2], rhs[3], rhs[4], rhs[5], rhs[6], rhs[7],
+                ],
+            )
+        },
         64 => {
             let sum_4s: [PackedMontyField31Neon<P>; 16] = core::array::from_fn(|i| {
                 let start = i * 4;
@@ -951,8 +967,6 @@ where
     RHS: IntoVec<P>,
 {
     unsafe {
-        // Accumulate the full 64-bit sum C = Σ lhs_i ⋅ rhs_i (5 terms).
-
         // Materialize all vectors once.
         let lhs0 = lhs[0].into_vec();
         let rhs0 = rhs[0].into_vec();
@@ -965,60 +979,88 @@ where
         let lhs4 = lhs[4].into_vec();
         let rhs4 = rhs[4].into_vec();
 
+        // Group A: accumulate terms 0-2 in wide form. Safe: 3*(P-1)^2 < 2^64.
+
         // Low half (Lanes 0 & 1)
-        let mut sum_l =
+        let mut sum_al =
             aarch64::vmull_u32(aarch64::vget_low_u32(lhs0), aarch64::vget_low_u32(rhs0));
-        sum_l = aarch64::vmlal_u32(
-            sum_l,
+        sum_al = aarch64::vmlal_u32(
+            sum_al,
             aarch64::vget_low_u32(lhs1),
             aarch64::vget_low_u32(rhs1),
         );
-        sum_l = aarch64::vmlal_u32(
-            sum_l,
+        sum_al = aarch64::vmlal_u32(
+            sum_al,
             aarch64::vget_low_u32(lhs2),
             aarch64::vget_low_u32(rhs2),
         );
-        sum_l = aarch64::vmlal_u32(
-            sum_l,
-            aarch64::vget_low_u32(lhs3),
-            aarch64::vget_low_u32(rhs3),
-        );
-        sum_l = aarch64::vmlal_u32(
-            sum_l,
+
+        // High half (Lanes 2 & 3)
+        let mut sum_ah = aarch64::vmull_high_u32(lhs0, rhs0);
+        sum_ah = aarch64::vmlal_high_u32(sum_ah, lhs1, rhs1);
+        sum_ah = aarch64::vmlal_high_u32(sum_ah, lhs2, rhs2);
+
+        // Group B: accumulate terms 3-4 in wide form. Safe: 2*(P-1)^2 < 2^64.
+
+        // Low half (Lanes 0 & 1)
+        let mut sum_bl =
+            aarch64::vmull_u32(aarch64::vget_low_u32(lhs3), aarch64::vget_low_u32(rhs3));
+        sum_bl = aarch64::vmlal_u32(
+            sum_bl,
             aarch64::vget_low_u32(lhs4),
             aarch64::vget_low_u32(rhs4),
         );
 
         // High half (Lanes 2 & 3)
-        let mut sum_h = aarch64::vmull_high_u32(lhs0, rhs0);
-        sum_h = aarch64::vmlal_high_u32(sum_h, lhs1, rhs1);
-        sum_h = aarch64::vmlal_high_u32(sum_h, lhs2, rhs2);
-        sum_h = aarch64::vmlal_high_u32(sum_h, lhs3, rhs3);
-        sum_h = aarch64::vmlal_high_u32(sum_h, lhs4, rhs4);
+        let mut sum_bh = aarch64::vmull_high_u32(lhs3, rhs3);
+        sum_bh = aarch64::vmlal_high_u32(sum_bh, lhs4, rhs4);
 
-        // Split C into 32-bit halves per lane:
-        // - c_lo = C mod 2^{32},
-        // - c_hi = C >> 32.
-        let c_lo = aarch64::vuzp1q_u32(
-            aarch64::vreinterpretq_u32_u64(sum_l),
-            aarch64::vreinterpretq_u32_u64(sum_h),
+        // Split each group into 32-bit c_lo, c_hi.
+        let c_lo_a = aarch64::vuzp1q_u32(
+            aarch64::vreinterpretq_u32_u64(sum_al),
+            aarch64::vreinterpretq_u32_u64(sum_ah),
         );
-        let c_hi = aarch64::vuzp2q_u32(
-            aarch64::vreinterpretq_u32_u64(sum_l),
-            aarch64::vreinterpretq_u32_u64(sum_h),
+        let c_hi_a = aarch64::vuzp2q_u32(
+            aarch64::vreinterpretq_u32_u64(sum_al),
+            aarch64::vreinterpretq_u32_u64(sum_ah),
+        );
+        let c_lo_b = aarch64::vuzp1q_u32(
+            aarch64::vreinterpretq_u32_u64(sum_bl),
+            aarch64::vreinterpretq_u32_u64(sum_bh),
+        );
+        let c_hi_b = aarch64::vuzp2q_u32(
+            aarch64::vreinterpretq_u32_u64(sum_bl),
+            aarch64::vreinterpretq_u32_u64(sum_bh),
         );
 
-        // Since C < 5P^2 and P < 2^{31}, we have c_hi < 3P.
-        // Reduce c_hi from [0, 3P) to [0, P) in two steps via conditional subtraction.
-        let c_hi_sub1 = aarch64::vsubq_u32(c_hi, P::PACKED_P);
-        let c_hi_1 = aarch64::vminq_u32(c_hi, c_hi_sub1);
-        let c_hi_sub2 = aarch64::vsubq_u32(c_hi_1, P::PACKED_P);
-        let c_hi_prime = aarch64::vminq_u32(c_hi_1, c_hi_sub2);
+        // Reduce group A's c_hi from [0, 2P) to [0, P). Group B's c_hi < P needs no reduction.
+        let c_hi_a_sub = aarch64::vsubq_u32(c_hi_a, P::PACKED_P);
+        let c_hi_a_red = aarch64::vminq_u32(c_hi_a, c_hi_a_sub);
 
-        // q ≡ c_lo ⋅ μ (mod 2^{32}), with μ = −P^{-1} (mod 2^{32}).
+        // Merge the two groups with carry propagation.
+        //
+        // c_lo = c_lo_a + c_lo_b (wrapping u32 add).
+        let c_lo = aarch64::vaddq_u32(c_lo_a, c_lo_b);
+        // carry = -1 (all 1s) if c_lo wrapped, 0 otherwise.
+        let carry = aarch64::vcltq_u32(c_lo, c_lo_a);
+
+        // Reduce c_hi_sum BEFORE incorporating carry for better ILP.
+        // c_hi_sum = c_hi_a' + c_hi_b ∈ [0, 2P-2] (both < P).
+        let c_hi_sum = aarch64::vaddq_u32(c_hi_a_red, c_hi_b);
+        let c_hi_sub = aarch64::vsubq_u32(c_hi_sum, P::PACKED_P);
+        let c_hi_red = aarch64::vminq_u32(c_hi_sum, c_hi_sub);
+
+        // Now incorporate carry: c_hi_red ∈ [0, P-2] (max is 2P-2 reduced to P-2).
+        // Adding carry (0 or 1) gives at most P-1, so no further reduction needed.
+        // Subtracting -1 adds 1; subtracting 0 is a no-op.
+        let c_hi_prime = aarch64::vsubq_u32(c_hi_red, carry);
+
+        // Montgomery reduction (identical to dot_product_4).
+        //
+        // q ≡ c_lo ⋅ μ (mod 2^{32}).
         let q = aarch64::vmulq_u32(c_lo, aarch64::vreinterpretq_u32_s32(P::PACKED_MU));
 
-        // Compute (q⋅P)_hi = high 32 bits of q⋅P per lane (exact unsigned widening multiply).
+        // (q⋅P)_hi = high 32 bits of q⋅P.
         let qp_l = aarch64::vmull_u32(aarch64::vget_low_u32(q), aarch64::vget_low_u32(P::PACKED_P));
         let qp_h = aarch64::vmull_high_u32(q, P::PACKED_P);
         let qp_hi = aarch64::vuzp2q_u32(
```
