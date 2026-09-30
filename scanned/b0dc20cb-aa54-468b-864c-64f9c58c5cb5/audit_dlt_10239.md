# [?] Fix overflow in FixedPointConvert

## Summary
Severity: Unknown
Chain: Phala
Component: Phala-Network/phala-blockchain
Published: 2023-01-04
Source: https://github.com/Phala-Network/phala-blockchain/commit/46e8096b4ebf1fc3cb24fd80f78fc0f63f3d7560
Type: security-commit

## Details
Fix overflow in FixedPointConvert

## Patch
### pallets/phala/src/utils/balance_convert.rs
```diff
@@ -1,26 +1,24 @@
-use fixed::types::U64F64;
-use fixed_macro::fixed;
-use U64F64 as FixedPoint;
+use fixed::types::{U64F64 as FixedPoint, U80F48};
 
 pub trait FixedPointConvert {
 	fn from_bits(bits: u128) -> Self;
 	fn from_fixed(v: &FixedPoint) -> Self;
 	fn to_fixed(&self) -> FixedPoint;
 }
 
-const FIXED_1E12: FixedPoint = fixed!(1_000_000_000_000: U64F64);
+const PHA: u128 = 1_000_000_000_000;
 
 // 12 decimals u128 conversion
 impl FixedPointConvert for u128 {
 	fn from_bits(bits: u128) -> Self {
 		Self::from_fixed(&FixedPoint::from_bits(bits))
 	}
 	fn from_fixed(v: &FixedPoint) -> Self {
-		v.saturating_mul(FIXED_1E12).to_num()
+		U80F48::unwrapped_from_num(*v).unwrapped_mul_int(PHA).to_num()
 	}
 	fn to_fixed(&self) -> FixedPoint {
-		let v = FixedPoint::from_num(*self);
-		v.saturating_div(FIXED_1E12)
+		let v = U80F48::unwrapped_from_num(*self);
+		FixedPoint::unwrapped_from_num(v.unwrapped_div_int(PHA))
 	}
 }
 
```
