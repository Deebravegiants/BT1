# [?] Fix: pool orderbook panic (#5510)

## Summary
Severity: Unknown
Chain: Chainflip
Component: chainflip-io/chainflip-backend
Published: 2024-12-19
Source: https://github.com/chainflip-io/chainflip-backend/commit/8a523ad4130924ea8a87524d2041fff331f51243
Type: security-commit

## Details
Fix: pool orderbook panic (#5510)

* feat: simplify fix point nth power function

* feat: fixed point nth power fn returns None on overflow

* feat: nth root implemented as binary search

* chore: fix slow nth root tests

* chore: update comments

* chore: fix tests

## Patch
### state-chain/amm/src/common.rs
```diff
@@ -232,60 +232,136 @@ impl SwapDirection for QuoteToBase {
 }
 
 /// Takes a Q128 fixed point number and raises it to the nth power, and returns it as a Q128 fixed
-/// point number. If the result is larger than the maximum U384 this function will panic.
-///
-/// The result will be equal or less than the true value.
-pub(super) fn fixed_point_to_power_as_fixed_point(x: U256, n: u32) -> U512 {
+/// point number. If the result is larger than the maximum U384 this function will return None.
+fn fixed_point_to_power_as_fixed_point(x: U256, n: u32) -> Option<U512> {
 	let x = U512::from(x);
+	let mut result = U512::from(1) << 128;
+
+	// Iterate over bits of the exponent (n) from most to least significant
+	// (starting with the first non-zero bit):
+	for bit_idx in (0..(32 - n.leading_zeros())).rev() {
+		let bit = (n & (0x1 << bit_idx)) >> bit_idx;
+
+		// Square the intermediate result on each iteration:
+		result = result.checked_mul(result)? >> 128;
+		// Additionally multiply by `x` if the bit is set:
+		if bit == 0x1 {
+			result = result.checked_mul(x)? >> 128;
+		}
+	}
 
-	(0..(32 - n.leading_zeros()))
-		.zip(
-			// This is zipped second and therefore it is not polled if there are no more bits, so
-			// we don't calculate x * x one more time than we need, as it may overflow.
-			sp_std::iter::once(x).chain(sp_std::iter::repeat_with({
-				let mut x = x;
-				move || {
-					x = (x * x) >> 128;
-					x
-				}
-			})),
-		)
-		.fold(U512::one() << 128, |total, (i, expo)| {
-			if 0x1 << i == (n & 0x1 << i) {
-				(total * expo) >> 128
-			} else {
-				total
-			}
-		})
+	Some(result)
 }
 
 pub(super) fn nth_root_of_integer_as_fixed_point(x: U256, n: u32) -> U256 {
-	// If n is 1 then many x values aren't representable as a fixed point.
-	assert!(n > 1);
+	// A root of degree 0 does not make sense mathematically:
+	assert!(n > 0);
 
-	let mut root = U256::try_from(
-		(0..n.ilog2()).fold(U512::from(x) << 128, |acc, _| (acc << 128).integer_sqrt()),
-	)
-	.unwrap();
+	// Check for trivial cases first:
+	if x == U256::from(0) {
+		return 0.into();
+	}
+
+	if n == 1 {
+		return x;
+	}
 
 	let x = U512::from(x) << 128;
 
+	let mut root_min = U256::from(0);
+
+	// Compute upper bound as kth root of x where k is the closest power of 2 not exceeding n:
+	let mut root_max =
+		U256::try_from((0..n.ilog2()).fold(x, |acc, _| (acc << 128).integer_sqrt())).unwrap();
+
+	// Upper bound is the root if n is a power of 2:
+	if n.is_power_of_two() {
+		return root_max;
+	}
+
+	// Start binary search:
+	let mut mid = root_min;
+
 	for _ in 0..128 {
-		let f = fixed_point_to_power_as_fixed_point(root, n);
+		mid = (root_max + root_min) / 2;
+
+		let f: U512 = fixed_point_to_power_as_fixed_point(mid, n).unwrap_or(U512::MAX);
+
 		let diff = f.abs_diff(x);
+
 		if diff <= f >> 20 {
-			break
+			break;
+		}
+
+		if f > x {
+			// need to search between root_min and mid
+			root_max = mid;
 		} else {
-			let delta = mul_div_floor(
-				U256::try_from(diff).unwrap(),
-				(U256::one() << 128) / U256::from(n),
-				fixed_point_to_power_as_fixed_point(root, n - 1),
-			);
-			root = if f >= x { root - delta } else { root + delta };
+			// search between mid and root_max
+			root_min = mid
 		}
 	}
 
-	root
+	mid
+}
+
+#[cfg(test)]
+fn fixed_point_to_float(x: U256) -> f64 {
+	x.0.into_iter()
+		.fold(0.0f64, |acc, n| (acc / 2.0f64.powi(64)) + (n as f64) * 2.0f64.powi(64))
+}
+
+#[cfg(test)]
+mod fast_tests {
+
+	use super::*;
+
+	#[test]
+	fn test_fixed_point_to_power_as_fixed_point() {
+		for n in 0..9u32 {
+			for e in 0..9u32 {
+				assert_eq!(
+					Some(U512::from(n.pow(e)) << 128),
+					fixed_point_to_power_as_fixed_point(U256::from(n) << 128, e)
+				);
+			}
+		}
+
+		assert_eq!(
+			U512::from(57),
+			fixed_point_to_power_as_fixed_point(U256::from(3) << 127, 10).unwrap() >> 128
+		);
+
+		assert_eq!(
+			U512::from(1) << 128,
+			fixed_point_to_power_as_fixed_point(U256::from(2) << 128, 128).unwrap() >> 128
+		);
+
+		// Expected to overflow
+		assert_eq!(fixed_point_to_power_as_fixed_point(U256::from(2) << 128, 256), None);
+	}
+
+	#[test]
+	fn extra_tests_for_nth_root() {
+		let cases = [
+			(17, 3),
+			(17, 2),
+			(15251194969974u128, 3),
+			(15251194969974u128, 4251528),
+			(59223190690940610911414, 4251528),
+			// These cases used to fail in the previous implementation:
+			(59223190690940610911414u128, 7),
+			(59223190690940610911414u128, 15),
+			(59223190690940610911414u128, 255),
+		];
+
+		for (n, i) in cases {
+			let root_float = (n as f64).powf(1.0f64 / (i as f64));
+			let root = fixed_point_to_float(nth_root_of_integer_as_fixed_point(n.into(), i));
+
+			assert!((root_float - root).abs() <= root_float * 0.000001f64, "{root_float} {root}");
+		}
+	}
 }
 
 #[cfg(all(test, feature = "slow-tests"))]
@@ -326,43 +402,12 @@ mod test {
 		inner::<QuoteToBase>();
 	}
 
-	#[test]
-	fn test_fixed_point_to_power_as_fixed_point() {
-		for n in 0..9u32 {
-			for e in 0..9u32 {
-				assert_eq!(
-					U512::from(n.pow(e)) << 128,
-					fixed_point_to_power_as_fixed_point(U256::from(n) << 128, e)
-				);
-			}
-		}
-
-		assert_eq!(
-			U512::from(57),
-			fixed_point_to_power_as_fixed_point(U256::from(3) << 127, 10) >> 128
-		);
-		assert_eq!(
-			U512::from(1) << 128,
-			fixed_point_to_power_as_fixed_point(U256::from(2) << 128, 128) >> 128
-		);
-		assert_eq!(
-			U512::from(1) << 255,
-			fixed_point_to_power_as_fixed_point(U256::from(2) << 128, 255) >> 128
-		);
-	}
-
 	#[test]
 	fn test_nth_root_of_integer_as_fixed_point() {
-		fn fixed_point_to_float(x: U256) -> f64 {
-			x.0.into_iter()
-				.fold(0.0f64, |acc, n| (acc / 2.0f64.powi(64)) + (n as f64) * 2.0f64.powi(64))
-		}
-
 		for i in 1..100 {
-			assert_eq!(
-				U256::from(i) << 128,
-				nth_root_of_integer_as_fixed_point(U256::from(i * i), 2)
-			);
+			let result = nth_root_of_integer_as_fixed_point(U256::from(i * i), 2);
+			let expected = U256::from(i) << 128;
+			assert!(result.abs_diff(expected) <= U256::from(1))
 		}
 
 		for n in (0..1000000).step_by(5) {
@@ -382,11 +427,11 @@ mod test {
 			nth_root_of_integer_as_fixed_point(U256::one() << 128, 128)
 		);
 		assert_eq!(
-			U256::from_dec_str("1198547750512063821665753418683415504682").unwrap(),
+			U256::from_dec_str("1198547684143787677818343298015649630110").unwrap(),
 			nth_root_of_integer_as_fixed_point(U256::from(83434), 9)
 		);
 		assert_eq!(
-			U256::from_dec_str("70594317847877622574934944024871574448634").unwrap(),
+			U256::from_dec_str("70594316175327588892648857471146691009115").unwrap(),
 			nth_root_of_integer_as_fixed_point(U256::from(384283294283u128), 5)
 		);
 
@@ -395,7 +440,8 @@ mod test {
 			for e in 2..10 {
 				let root = nth_root_of_integer_as_fixed_point(n, e);
 				let x =
-					U256::try_from(fixed_point_to_power_as_fixed_point(root, e) >> 128).unwrap();
+					U256::try_from(fixed_point_to_power_as_fixed_point(root, e).unwrap() >> 128)
+						.unwrap();
 				assert!((n.saturating_sub(1.into())..=n + 1).contains(&x));
 			}
 		}
```
