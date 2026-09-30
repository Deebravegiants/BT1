# [?] Fix overflow issue for Uint64

## Summary
Severity: Unknown
Chain: Cosmos
Component: CosmWasm/cosmwasm
Published: 2021-06-09
Source: https://github.com/CosmWasm/cosmwasm/commit/04fe94276ee37016c62f03a56e61d0379a1a705c
Type: security-commit

## Details
Fix overflow issue for Uint64

## Patch
### packages/std/src/math/uint64.rs
```diff
@@ -1,6 +1,6 @@
 use schemars::JsonSchema;
 use serde::{de, ser, Deserialize, Deserializer, Serialize};
-use std::convert::TryFrom;
+use std::convert::{TryFrom, TryInto};
 use std::fmt::{self};
 use std::iter::Sum;
 use std::ops;
@@ -216,13 +216,16 @@ impl Uint64 {
         numerator: A,
         denominator: B,
     ) -> Uint64 {
-        let numerator: u64 = numerator.into();
-        let denominator: u64 = denominator.into();
+        let base: u128 = self.u64().into();
+        let numerator: u128 = numerator.into().into();
+        let denominator: u128 = denominator.into().into();
         if denominator == 0 {
             panic!("Denominator must not be zero");
         }
-        // TODO: avoid overflow in multiplication (https://github.com/CosmWasm/cosmwasm/issues/920)
-        let val = self.u64() * numerator / denominator;
+
+        let val: u64 = (base * numerator / denominator)
+            .try_into()
+            .expect("multiplication overflow");
         Uint64::from(val)
     }
 }
@@ -416,6 +419,23 @@ mod tests {
         assert_eq!(base.multiply_ratio(100u64, 120u64), Uint64(416));
     }
 
+    #[test]
+    fn uint64_multiply_ratio_does_not_overflow_when_result_fits() {
+        // Almost max value for Uint64.
+        let base = Uint64(18446744073709551606);
+
+        assert_eq!(base.multiply_ratio(2u64, 2u64), base);
+    }
+
+    #[test]
+    #[should_panic]
+    fn uint64_multiply_ratio_panicks_on_overflow() {
+        // Almost max value for Uint64.
+        let base = Uint64(18446744073709551606);
+
+        assert_eq!(base.multiply_ratio(2u64, 1u64), base);
+    }
+
     #[test]
     #[should_panic(expected = "Denominator must not be zero")]
     fn uint64_multiply_ratio_panics_for_zero_denominator() {
```
