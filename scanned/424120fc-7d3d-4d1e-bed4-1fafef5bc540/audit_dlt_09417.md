# [?] fix cargo fmt in emission gate underflow test

## Summary
Severity: Unknown
Chain: Bittensor
Component: RaoFoundation/subtensor
Published: 2026-07-27
Source: https://github.com/RaoFoundation/subtensor/commit/b56ddbbdb29cb78bca3189130d4dcbc01c787b06
Type: security-commit

## Details
fix cargo fmt in emission gate underflow test

Co-authored-by: Cursor <cursoragent@cursor.com>

## Patch
### pallets/subtensor/src/tests/subnet_emissions.rs
```diff
@@ -279,9 +279,8 @@ fn emission_gate_underflow_restores_ungated_shares() {
         EmissionGateExponent::<Test>::set(u64f64(8.0));
 
         let equal = u64f64(1.0 / 256.0);
-        let mut shares: BTreeMap<NetUid, U64F64> = (1u16..=256)
-            .map(|i| (NetUid::from(i), equal))
-            .collect();
+        let mut shares: BTreeMap<NetUid, U64F64> =
+            (1u16..=256).map(|i| (NetUid::from(i), equal)).collect();
 
         SubtensorModule::apply_emission_gate(&mut shares);
 
```
