# [?] Fix slot_duration divide by zero panic in rococo-parachain runtime (#2612)

## Summary
Severity: Unknown
Chain: Polkadot
Component: paritytech/polkadot-sdk
Published: 2023-12-28
Source: https://github.com/paritytech/polkadot-sdk/commit/201ec44ae43f9dc718434b186a43216d05c632ba
Type: security-commit

## Details
Fix slot_duration divide by zero panic in rococo-parachain runtime (#2612)

Adds the fix in https://github.com/paritytech/polkadot-sdk/pull/2039 to
the rococo-parachain runtime.

## Patch
### cumulus/parachains/runtimes/testing/rococo-parachain/src/lib.rs
```diff
@@ -229,6 +229,9 @@ impl pallet_timestamp::Config for Runtime {
 	/// A timestamp: milliseconds since the unix epoch.
 	type Moment = u64;
 	type OnTimestampSet = Aura;
+	#[cfg(feature = "experimental")]
+	type MinimumPeriod = ConstU64<0>;
+	#[cfg(not(feature = "experimental"))]
 	type MinimumPeriod = ConstU64<{ SLOT_DURATION / 2 }>;
 	type WeightInfo = ();
 }
@@ -757,7 +760,7 @@ impl_runtime_apis! {
 
 	impl sp_consensus_aura::AuraApi<Block, AuraId> for Runtime {
 		fn slot_duration() -> sp_consensus_aura::SlotDuration {
-			sp_consensus_aura::SlotDuration::from_millis(SLOT_DURATION)
+			sp_consensus_aura::SlotDuration::from_millis(Aura::slot_duration())
 		}
 
 		fn authorities() -> Vec<AuraId> {
```
