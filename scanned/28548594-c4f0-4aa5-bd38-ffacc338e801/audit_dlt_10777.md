# [?] Merge pull request #1095 from Phala-Network/fix-overflow

## Summary
Severity: Unknown
Chain: Phala
Component: Phala-Network/phala-blockchain
Published: 2023-01-04
Source: https://github.com/Phala-Network/phala-blockchain/commit/bb92d75c7c45afe0f4fd5ade9a8a21824e6c92f0
Type: security-commit

## Details
Merge pull request #1095 from Phala-Network/fix-overflow

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
 
@@ -37,3 +35,17 @@ where
 {
 	FixedPointConvert::from_fixed(&(x.to_fixed() / y))
 }
+
+#[cfg(test)]
+mod tests {
+	use super::*;
+
+	#[test]
+	fn max_supply_not_overflow() {
+		#[allow(clippy::inconsistent_digit_grouping)]
+		let balance = 1_000_000_000__000_000_000_000_u128;
+		let f = balance.to_fixed();
+		assert_eq!(f.to_string(), "1000000000");
+		assert_eq!(u128::from_fixed(&f), balance);
+	}
+}
```
