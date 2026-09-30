# [?] Fix overflow issue for Uint128

## Summary
Severity: Unknown
Chain: Cosmos
Component: CosmWasm/cosmwasm
Published: 2021-06-09
Source: https://github.com/CosmWasm/cosmwasm/commit/f5a6f29300969b8ca1b66f4a31355d1b38e69677
Type: security-commit

## Details
Fix overflow issue for Uint128

## Patch
### CHANGELOG.md
```diff
@@ -13,6 +13,8 @@ and this project adheres to
 - cosmwasm-std: Implement `std::ops::Sub` for `math::Decimal`
 - cosmwasm-std: Add `Timestamp::seconds` and `Timestamp::subsec_nanos`.
 - cosmwasm-std: Implement division for `Decimal / Uint128`
+- cosmwasm-std: Fix `Uint64::multiply_ratio` and `Uint128::multiply_ratio`
+  so that internal multiplication cannot cause an unnecessary overflow. ([#920])
 
 ## [0.14.0] - 2021-05-03
 
```

### Cargo.lock
```diff
@@ -241,6 +241,8 @@ dependencies = [
  "cosmwasm-schema",
  "hex",
  "hex-literal",
+ "num-bigint",
+ "num-traits",
  "schemars",
  "serde",
  "serde-json-wasm",
@@ -904,6 +906,17 @@ version = "0.2.1"
 source = "registry+https://github.com/rust-lang/crates.io-index"
 checksum = "0debeb9fcf88823ea64d64e4a815ab1643f33127d995978e099942ce38f25238"
 
+[[package]]
+name = "num-bigint"
+version = "0.4.0"
+source = "registry+https://github.com/rust-lang/crates.io-index"
+checksum = "4e0d047c1062aa51e256408c560894e5251f08925980e53cf1aa5bd00eec6512"
+dependencies = [
+ "autocfg",
+ "num-integer",
+ "num-traits",
+]
+
 [[package]]
 name = "num-integer"
 version = "0.1.44"
```

### packages/std/Cargo.toml
```diff
@@ -34,6 +34,8 @@ serde-json-wasm = { version = "0.3.1" }
 schemars = "0.8.1"
 serde = { version = "1.0.103", default-features = false, features = ["derive", "alloc"] }
 thiserror = "1.0"
+num-bigint = "0.4.0"
+num-traits = "0.2.14"
 
 [target.'cfg(not(target_arch = "wasm32"))'.dependencies]
 cosmwasm-crypto = { path = "../crypto", version = "0.14.0" }
```

### packages/std/src/math/uint128.rs
```diff
@@ -1,3 +1,5 @@
+use num_bigint::BigUint;
+use num_traits::cast::ToPrimitive;
 use schemars::JsonSchema;
 use serde::{de, ser, Deserialize, Deserializer, Serialize};
 use std::convert::TryFrom;
@@ -227,13 +229,15 @@ impl Uint128 {
         numerator: A,
         denominator: B,
     ) -> Uint128 {
+        let base: BigUint = self.u128().into();
         let numerator: u128 = numerator.into();
         let denominator: u128 = denominator.into();
         if denominator == 0 {
             panic!("Denominator must not be zero");
         }
-        // TODO: avoid overflow in multiplication (https://github.com/CosmWasm/cosmwasm/issues/920)
-        let val = self.u128() * numerator / denominator;
+        let val = (base * numerator / denominator)
+            .to_u128()
+            .expect("multiplication overflow");
         Uint128::from(val)
     }
 }
@@ -430,6 +434,23 @@ mod tests {
         assert_eq!(base.multiply_ratio(100u128, 120u128), Uint128(416));
     }
 
+    #[test]
+    fn uint128_multiply_ratio_does_not_overflow_when_result_fits() {
+        // Almost max value for Uint64.
+        let base = Uint128(340282366920938463463374607431768211446);
+
+        assert_eq!(base.multiply_ratio(2u128, 2u128), base);
+    }
+
+    #[test]
+    #[should_panic]
+    fn uint128_multiply_ratio_panicks_on_overflow() {
+        // Almost max value for Uint64.
+        let base = Uint128(340282366920938463463374607431768211446);
+
+        assert_eq!(base.multiply_ratio(2u128, 1u128), base);
+    }
+
     #[test]
     #[should_panic(expected = "Denominator must not be zero")]
     fn uint128_multiply_ratio_panics_for_zero_denominator() {
```
