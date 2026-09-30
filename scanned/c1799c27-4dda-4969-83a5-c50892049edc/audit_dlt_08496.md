# [?] cumulus: fix test runtimes panic (#2039)

## Summary
Severity: Unknown
Chain: Polkadot
Component: paritytech/polkadot-sdk
Published: 2023-10-26
Source: https://github.com/paritytech/polkadot-sdk/commit/1b08bdd2dd3f1c2fe623c6cc7df45714e6256362
Type: security-commit

## Details
cumulus: fix test runtimes panic (#2039)

the min slot duration should be 0 only if the `experimental` feature is
enabled. otherwise, the runtime will panic on a division by 0.

## Patch
### cumulus/parachains/runtimes/glutton/glutton-kusama/src/lib.rs
```diff
@@ -224,7 +224,10 @@ impl cumulus_pallet_aura_ext::Config for Runtime {}
 impl pallet_timestamp::Config for Runtime {
 	type Moment = u64;
 	type OnTimestampSet = Aura;
+	#[cfg(feature = "experimental")]
 	type MinimumPeriod = ConstU64<0>;
+	#[cfg(not(feature = "experimental"))]
+	type MinimumPeriod = ConstU64<{ SLOT_DURATION / 2 }>;
 	type WeightInfo = weights::pallet_timestamp::WeightInfo<Runtime>;
 }
 
@@ -355,7 +358,7 @@ impl_runtime_apis! {
 
 	impl sp_consensus_aura::AuraApi<Block, AuraId> for Runtime {
 		fn slot_duration() -> sp_consensus_aura::SlotDuration {
-			sp_consensus_aura::SlotDuration::from_millis(SLOT_DURATION)
+			sp_consensus_aura::SlotDuration::from_millis(Aura::slot_duration())
 		}
 
 		fn authorities() -> Vec<AuraId> {
```

### cumulus/parachains/runtimes/starters/seedling/src/lib.rs
```diff
@@ -216,7 +216,10 @@ impl pallet_aura::Config for Runtime {
 impl pallet_timestamp::Config for Runtime {
 	type Moment = u64;
 	type OnTimestampSet = Aura;
+	#[cfg(feature = "experimental")]
 	type MinimumPeriod = ConstU64<0>;
+	#[cfg(not(feature = "experimental"))]
+	type MinimumPeriod = ConstU64<{ parachains_common::SLOT_DURATION / 2 }>;
 	type WeightInfo = ();
 }
 
```

### cumulus/parachains/runtimes/starters/shell/src/lib.rs
```diff
@@ -219,7 +219,10 @@ impl pallet_aura::Config for Runtime {
 impl pallet_timestamp::Config for Runtime {
 	type Moment = u64;
 	type OnTimestampSet = Aura;
+	#[cfg(feature = "experimental")]
 	type MinimumPeriod = ConstU64<0>;
+	#[cfg(not(feature = "experimental"))]
+	type MinimumPeriod = ConstU64<{ parachains_common::SLOT_DURATION / 2 }>;
 	type WeightInfo = ();
 }
 
```

### substrate/frame/aura/src/lib.rs
```diff
@@ -408,8 +408,9 @@ impl<T: Config> OnTimestampSet<T::Moment> for Pallet<T> {
 		let timestamp_slot = moment / slot_duration;
 		let timestamp_slot = Slot::from(timestamp_slot.saturated_into::<u64>());
 
-		assert!(
-			CurrentSlot::<T>::get() == timestamp_slot,
+		assert_eq!(
+			CurrentSlot::<T>::get(),
+			timestamp_slot,
 			"Timestamp slot must match `CurrentSlot`"
 		);
 	}
```

### substrate/frame/babe/src/lib.rs
```diff
@@ -900,8 +900,9 @@ impl<T: Config> OnTimestampSet<T::Moment> for Pallet<T> {
 		let timestamp_slot = moment / slot_duration;
 		let timestamp_slot = Slot::from(timestamp_slot.saturated_into::<u64>());
 
-		assert!(
-			CurrentSlot::<T>::get() == timestamp_slot,
+		assert_eq!(
+			CurrentSlot::<T>::get(),
+			timestamp_slot,
 			"Timestamp slot must match `CurrentSlot`"
 		);
 	}
```
