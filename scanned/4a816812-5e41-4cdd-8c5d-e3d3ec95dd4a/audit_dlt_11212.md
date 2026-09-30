# [?] fix: prevent overflow in negative i64/i128 field conversions (#894)

## Summary
Severity: Unknown
Chain: ZK
Component: a16z/jolt
Published: 2025-08-20
Source: https://github.com/a16z/jolt/commit/bdbed9c066fe9c43e360ec99e234cb331ee9926a
Type: security-commit

## Details
fix: prevent overflow in negative i64/i128 field conversions (#894)

## Patch
### jolt-core/src/field/ark.rs
```diff
@@ -70,7 +70,7 @@ impl JoltField for ark_bn254::Fr {
 
     fn from_i64(val: i64) -> Self {
         if val.is_negative() {
-            let val = (-val) as u64;
+            let val = val.unsigned_abs();
             if val <= u16::MAX as u64 {
                 -<Self as JoltField>::from_u16(val as u16)
             } else if val <= u32::MAX as u64 {
@@ -92,7 +92,7 @@ impl JoltField for ark_bn254::Fr {
 
     fn from_i128(val: i128) -> Self {
         if val.is_negative() {
-            let val = (-val) as u128;
+            let val = val.unsigned_abs();
             if val <= u16::MAX as u128 {
                 -<Self as JoltField>::from_u16(val as u16)
             } else if val <= u32::MAX as u128 {
```
