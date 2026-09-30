# [?] Fix try_into so that it won't panic. (#4874)

## Summary
Severity: Unknown
Chain: Starknet
Component: starkware-libs/cairo
Published: 2024-01-23
Source: https://github.com/starkware-libs/cairo/commit/c2d1ed18d6af87fc89ab7ed88c1c304d8d536619
Type: security-commit

## Details
Fix try_into so that it won't panic. (#4874)

## Patch
### corelib/src/integer.cairo
```diff
@@ -157,7 +157,7 @@ fn u128_try_as_non_zero(a: u128) -> Option<NonZero<u128>> nopanic {
 
 pub(crate) impl U128TryIntoNonZero of TryInto<u128, NonZero<u128>> {
     fn try_into(self: u128) -> Option<NonZero<u128>> {
-        Option::Some(u128_as_non_zero(self))
+        u128_try_as_non_zero(self)
     }
 }
 
@@ -395,7 +395,7 @@ fn u8_try_as_non_zero(a: u8) -> Option<NonZero<u8>> nopanic {
 
 impl U8TryIntoNonZero of TryInto<u8, NonZero<u8>> {
     fn try_into(self: u8) -> Option<NonZero<u8>> {
-        Option::Some(u8_as_non_zero(self))
+        u8_try_as_non_zero(self)
     }
 }
 
@@ -592,7 +592,7 @@ fn u16_try_as_non_zero(a: u16) -> Option<NonZero<u16>> nopanic {
 
 impl U16TryIntoNonZero of TryInto<u16, NonZero<u16>> {
     fn try_into(self: u16) -> Option<NonZero<u16>> {
-        Option::Some(u16_as_non_zero(self))
+        u16_try_as_non_zero(self)
     }
 }
 
@@ -789,7 +789,7 @@ fn u32_try_as_non_zero(a: u32) -> Option<NonZero<u32>> nopanic {
 
 pub(crate) impl U32TryIntoNonZero of TryInto<u32, NonZero<u32>> {
     fn try_into(self: u32) -> Option<NonZero<u32>> {
-        Option::Some(u32_as_non_zero(self))
+        u32_try_as_non_zero(self)
     }
 }
 
@@ -986,7 +986,7 @@ fn u64_try_as_non_zero(a: u64) -> Option<NonZero<u64>> nopanic {
 
 impl U64TryIntoNonZero of TryInto<u64, NonZero<u64>> {
     fn try_into(self: u64) -> Option<NonZero<u64>> {
-        Option::Some(u64_as_non_zero(self))
+        u64_try_as_non_zero(self)
     }
 }
 
@@ -1255,7 +1255,7 @@ fn u256_try_as_non_zero(a: u256) -> Option<NonZero<u256>> nopanic {
 
 pub(crate) impl U256TryIntoNonZero of TryInto<u256, NonZero<u256>> {
     fn try_into(self: u256) -> Option<NonZero<u256>> {
-        Option::Some(u256_as_non_zero(self))
+        u256_try_as_non_zero(self)
     }
 }
 
```

### corelib/src/test/integer_test.cairo
```diff
@@ -100,7 +100,7 @@ fn test_u8_mul_overflow_3() {
 }
 
 #[test]
-#[should_panic]
+#[should_panic(expected: ('Division by 0',))]
 fn test_u8_div_by_0() {
     2_u8 / 0_u8;
 }
@@ -203,7 +203,7 @@ fn test_u16_mul_overflow_3() {
 }
 
 #[test]
-#[should_panic]
+#[should_panic(expected: ('Division by 0',))]
 fn test_u16_div_by_0() {
     2_u16 / 0_u16;
 }
@@ -306,7 +306,7 @@ fn test_u32_mul_overflow_3() {
 }
 
 #[test]
-#[should_panic]
+#[should_panic(expected: ('Division by 0',))]
 fn test_u32_div_by_0() {
     2_u32 / 0_u32;
 }
@@ -411,7 +411,7 @@ fn test_u64_mul_overflow_3() {
 }
 
 #[test]
-#[should_panic]
+#[should_panic(expected: ('Division by 0',))]
 fn test_u64_div_by_0() {
     2_u64 / 0_u64;
 }
@@ -561,7 +561,7 @@ fn test_u128_mul_overflow_3() {
 }
 
 #[test]
-#[should_panic]
+#[should_panic(expected: ('Division by 0',))]
 fn test_u128_div_by_0() {
     2_u128 / 0_u128;
 }
```

### crates/cairo-lang-starknet/cairo_level_tests/abi_dispatchers_tests.cairo
```diff
@@ -127,7 +127,7 @@ fn test_validate_gas_cost() {
     assert!(
         call_building_gas_usage == 6050
             && serialization_gas_usage == 85750
-            && entry_point_gas_usage == 354130,
+            && entry_point_gas_usage == 339730,
         "Unexpected gas_usage:
      call_building: `{call_building_gas_usage}`.
      serialization: `{serialization_gas_usage}`.
```

### crates/cairo-lang-starknet/cairo_level_tests/interoperability.cairo
```diff
@@ -90,7 +90,7 @@ fn test_flow_safe_dispatcher() {
 }
 
 #[test]
-#[available_gas(1170000)]
+#[available_gas(1160000)]
 #[should_panic(expected: ('Out of gas', 'ENTRYPOINT_FAILED',))]
 fn test_flow_out_of_gas() {
     // Set up.
```
