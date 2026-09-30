# [?] add safety checks to prevent panics

## Summary
Severity: Unknown
Chain: Hydration
Component: galacticcouncil/hydration-node
Published: 2024-04-05
Source: https://github.com/galacticcouncil/hydration-node/commit/3947b3eb3ccf8f90898c29dbf1deb7882bc4eb68
Type: security-commit

## Details
add safety checks to prevent panics

## Patch
### math/src/stableswap/math.rs
```diff
@@ -684,7 +684,7 @@ pub fn calculate_share_price<const D: u8>(
 	provided_d: Option<Balance>,
 ) -> Option<(Balance, Balance)> {
 	let n = reserves.len() as u128;
-	if n <= 1 {
+	if n <= 1 || asset_idx >= reserves.len() {
 		return None;
 	}
 	let d = if let Some(v) = provided_d {
@@ -737,7 +737,7 @@ pub fn calculate_spot_price(
 	asset_out_idx: usize,
 ) -> Option<(Balance, Balance)> {
 	let n = reserves.len();
-	if n <= 1 || asset_in_idx > n || asset_out_idx > n {
+	if n <= 1 || asset_in_idx >= n || asset_out_idx >= n {
 		return None;
 	}
 	let ann = calculate_ann(n, amplification)?;
@@ -834,4 +834,32 @@ mod tests {
 			)
 		);
 	}
+
+	#[test]
+	fn spot_price_calculation_should_fail_gracefully_with_invalid_indexes() {
+		let reserves = vec![
+			AssetReserve::new(478_626_000_000_000_000_000, 12),
+			AssetReserve::new(487_626_000_000_000_000_000, 12),
+			AssetReserve::new(866_764_000_000_000_000_000, 12),
+			AssetReserve::new(518_696_000_000_000_000_000, 12),
+		];
+		let amp = 10u128;
+		let d = calculate_d::<MAX_D_ITERATIONS>(&reserves, amp).unwrap();
+
+		assert!(calculate_spot_price(&reserves, amp, d, 4, 1).is_none());
+		assert!(calculate_spot_price(&reserves, amp, d, 1, 4).is_none());
+	}
+
+	#[test]
+	fn share_price_calculation_should_fail_gracefully_with_invalid_indexes() {
+		let reserves = vec![
+			AssetReserve::new(478_626_000_000_000_000_000, 12),
+			AssetReserve::new(487_626_000_000_000_000_000, 12),
+			AssetReserve::new(866_764_000_000_000_000_000, 12),
+			AssetReserve::new(518_696_000_000_000_000_000, 12),
+		];
+		let amp = 10u128;
+
+		assert!(calculate_share_price::<MAX_D_ITERATIONS>(&reserves, amp, 1000000000000000, 4, None).is_none());
+	}
 }
```
