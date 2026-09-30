# [?] Fix overflow for large round numbers (#1817)

## Summary
Severity: Unknown
Chain: Moonbeam
Component: moonbeam-foundation/moonbeam
Published: 2022-09-21
Source: https://github.com/moonbeam-foundation/moonbeam/commit/eb6024cde33ab0592f14fac622c411e8b415a0a2
Type: security-commit

## Details
Fix overflow for large round numbers (#1817)

Signed-off-by: Adam Reif <Garandor@manta.network>

Signed-off-by: Adam Reif <Garandor@manta.network>

## Patch
### pallets/parachain-staking/src/inflation.rs
```diff
@@ -24,7 +24,7 @@ use serde::{Deserialize, Serialize};
 use sp_runtime::PerThing;
 use sp_runtime::{Perbill, RuntimeDebug};
 use substrate_fixed::transcendental::pow as floatpow;
-use substrate_fixed::types::{I32F32, I64F64};
+use substrate_fixed::types::I64F64;
 
 const SECONDS_PER_YEAR: u32 = 31557600;
 const SECONDS_PER_BLOCK: u32 = 12;
@@ -66,10 +66,10 @@ pub fn perbill_annual_to_perbill_round(
 	annual: Range<Perbill>,
 	rounds_per_year: u32,
 ) -> Range<Perbill> {
-	let exponent = I32F32::from_num(1) / I32F32::from_num(rounds_per_year);
+	let exponent = I64F64::from_num(1) / I64F64::from_num(rounds_per_year);
 	let annual_to_round = |annual: Perbill| -> Perbill {
-		let x = I32F32::from_num(annual.deconstruct()) / I32F32::from_num(Perbill::ACCURACY);
-		let y: I64F64 = floatpow(I32F32::from_num(1) + x, exponent)
+		let x = I64F64::from_num(annual.deconstruct()) / I64F64::from_num(Perbill::ACCURACY);
+		let y: I64F64 = floatpow(I64F64::from_num(1) + x, exponent)
 			.expect("Cannot overflow since rounds_per_year is u32 so worst case 0; QED");
 		Perbill::from_parts(
 			((y - I64F64::from_num(1)) * I64F64::from_num(Perbill::ACCURACY))
@@ -211,4 +211,18 @@ mod tests {
 			mock_round_issuance_range(10_000_000, mock_annual_to_round(schedule, 8766))
 		);
 	}
+	#[test]
+	fn inflation_does_not_panic_at_round_number_limit() {
+		let schedule = Range {
+			min: Perbill::from_percent(100),
+			ideal: Perbill::from_percent(100),
+			max: Perbill::from_percent(100),
+		};
+		mock_round_issuance_range(u32::MAX.into(), mock_annual_to_round(schedule, u32::MAX));
+		mock_round_issuance_range(u64::MAX.into(), mock_annual_to_round(schedule, u32::MAX));
+		mock_round_issuance_range(u128::MAX.into(), mock_annual_to_round(schedule, u32::MAX));
+		mock_round_issuance_range(u32::MAX.into(), mock_annual_to_round(schedule, 1));
+		mock_round_issuance_range(u64::MAX.into(), mock_annual_to_round(schedule, 1));
+		mock_round_issuance_range(u128::MAX.into(), mock_annual_to_round(schedule, 1));
+	}
 }
```
