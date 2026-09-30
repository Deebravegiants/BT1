# [?] Merge rust-bitcoin/rust-bitcoin#5501: pow: Fix U256::overflowing_mul

## Summary
Severity: Unknown
Chain: Bitcoin
Component: rust-bitcoin/rust-bitcoin
Published: 2026-01-21
Source: https://github.com/rust-bitcoin/rust-bitcoin/commit/73809ff34eccaf25f38bf013ab26c8c01f0fc79f
Type: security-commit

## Details
Merge rust-bitcoin/rust-bitcoin#5501: pow: Fix U256::overflowing_mul

0942a57ac9f244e3c7a33a8bc9da0a00151f900f pow: Fix U256::overflowing_mul (Mitchell Bagot)

Pull request description:

  The overflowing_mul function in U256 doesn't compute correct values. This can be obviously seen by the current single test case that exists, which checks against an incorrect value and asserts an incorrect overflow state.
  
  Fix the implementation of overflowing_mul and add tests to check edge cases.


ACKs for top commit:
  tcharding:
    ACK 0942a57ac9f244e3c7a33a8bc9da0a00151f900f
  apoelstra:
    ACK 0942a57ac9f244e3c7a33a8bc9da0a00151f900f; successfully ran local tests and reasoned through the new algorithm and the test vectors


Tree-SHA512: 427eb5a1d0f7d47d17b09f635df5223d6fa5a2836dd07ff861de2649afff667a2df9e57e98d896465b6bfb4b18054cc742f58b6f4b4bc9f541bf7927984eaba3

## Patch
### bitcoin/src/pow.rs
```diff
@@ -394,7 +394,7 @@ internal_macros::define_extension_trait! {
             let prev_target: Target = last.into();
             let maximum_retarget = prev_target.max_transition_threshold(params); // bnPowLimit
             let retarget = prev_target.0; // bnNew
-            let retarget = retarget.mul(u128::try_from(actual_timespan).expect("clamped value won't be negative").into());
+            let (retarget, _) = retarget.mul_u64(u64::try_from(actual_timespan).expect("clamped value won't be negative"));
             let retarget = retarget.div(params.pow_target_timespan.into());
             let retarget = Target(retarget);
             if retarget.ge(&maximum_retarget) {
@@ -701,18 +701,19 @@ impl U256 {
         let mut ret = Self::ZERO;
         let mut ret_overflow = false;
 
-        for i in 0..3 {
+        for i in 0..=3 {
             let to_mul = (rhs >> (64 * i)).low_u64();
-            let (mul_res, _) = self.mul_u64(to_mul);
-            ret = ret.wrapping_add(mul_res << (64 * i));
-        }
+            let (mul_res, overflow) = self.mul_u64(to_mul);
+            ret_overflow |= overflow; // If multiplying lhs by the u64 overflowed, that's an overflow
 
-        let to_mul = (rhs >> 192).low_u64();
-        let (mul_res, overflow) = self.mul_u64(to_mul);
-        ret_overflow |= overflow;
-        let (sum, overflow) = ret.overflowing_add(mul_res);
-        ret = sum;
-        ret_overflow |= overflow;
+            // Calculate the bits that will overflow during the shift below.
+            let overflow_bits = if i > 0 { mul_res >> (256 - (64 * i)) } else { Self::ZERO };
+            ret_overflow |= overflow_bits > Self::ZERO; // If there are bits that will be shifted out below, that's an overflow
+
+            let (sum, overflow) = ret.overflowing_add(mul_res << (64 * i));
+            ret = sum;
+            ret_overflow |= overflow; // If adding the mul_u64 result overflowed, that's an overflow
+        }
 
         (ret, ret_overflow)
     }
@@ -1555,13 +1556,59 @@ mod tests {
         let (got, overflow) = x.overflowing_mul(y);
 
         let want = U256(
-            0x0000_0000_0000_0008_0000_0000_0000_0008,
-            0x0000_0000_0000_0006_0000_0000_0000_0004,
+            0x0000_0000_0000_0008_0000_0000_0000_0006,
+            0x0000_0000_0000_0004_0000_0000_0000_0002,
         );
-        assert!(!overflow);
+        assert!(overflow);
         assert_eq!(got, want)
     }
 
+   #[test]
+    fn u256_overflowing_mul() {
+        let a = U256(u128::MAX, 0);
+        let b = U256(1 << 65 | 1, 0);
+        let (res, overflow) = a.overflowing_mul(b);
+        assert_eq!(res, U256::ZERO);
+        assert!(overflow);
+
+        let a = U256(1 << 64, 0);
+        let b = U256(1, 0);
+        let (res, overflow) = a.overflowing_mul(b);
+        assert_eq!(res, U256::ZERO);
+        assert!(overflow);
+
+        let a = U256(0, 1 << 63);
+        let b = U256(1, 0);
+        let (res, overflow) = a.overflowing_mul(b);
+        assert_eq!(res, b << 63);
+        assert!(!overflow);
+
+        let (res, overflow) = U256::ONE.overflowing_mul(U256::ONE);
+        assert_eq!(res, U256::ONE);
+        assert!(!overflow);
+
+        // Simple case near upper edge
+        let a = U256(1 << 125, 0);
+        let b = U256(0, 4);
+        let (res, overflow) = a.overflowing_mul(b);
+        assert_eq!(res, U256(1 << 127, 0));
+        assert!(!overflow);
+
+        // Check case where bits overflow during shift. Kills * -> + and - -> + mutants.
+        let a = U256::ONE << 2;
+        let b = U256::ONE << 254;
+        let (res, overflow) = a.overflowing_mul(b);
+        assert_eq!(res, U256::ZERO);
+        assert!(overflow);
+
+        // mul_u64 overflows twice but no other overflows. Kills |= -> ^= mutant.
+        let a = U256::ONE << 255;
+        let b = U256(1<<1 | 1<<65, 0);
+        let (res, overflow) = a.overflowing_mul(b);
+        assert_eq!(res, U256::ZERO);
+        assert!(overflow);
+    }
+
     #[test]
     fn u256_increment() {
         let mut val = U256(
```
