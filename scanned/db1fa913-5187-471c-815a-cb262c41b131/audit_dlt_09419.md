# [?] Merge pull request #2786 from opentensor/fix-crowdloan-reentrancy

## Summary
Severity: Unknown
Chain: Bittensor
Component: RaoFoundation/subtensor
Published: 2026-06-30
Source: https://github.com/RaoFoundation/subtensor/commit/1d5ccecd9d9d61871e0a463c4883fa1ce1058660
Type: security-commit

## Details
Merge pull request #2786 from opentensor/fix-crowdloan-reentrancy

Fix crowdloan reentrancy bug

## Patch
### pallets/crowdloan/src/lib.rs
```diff
@@ -265,6 +265,8 @@ pub mod pallet {
         InvalidOrigin,
         /// The crowdloan has already been finalized.
         AlreadyFinalized,
+        /// A crowdloan finalization is already in progress.
+        AlreadyFinalizing,
         /// The crowdloan contribution period has not ended yet.
         ContributionPeriodNotEnded,
         /// The contributor has no contribution for this crowdloan.
@@ -619,6 +621,13 @@ pub mod pallet {
             ensure!(who == crowdloan.creator, Error::<T>::InvalidOrigin);
             ensure!(crowdloan.raised == crowdloan.cap, Error::<T>::CapNotRaised);
             ensure!(!crowdloan.finalized, Error::<T>::AlreadyFinalized);
+            ensure!(
+                CurrentCrowdloanId::<T>::get().is_none(),
+                Error::<T>::AlreadyFinalizing
+            );
+
+            crowdloan.finalized = true;
+            Crowdloans::<T>::insert(crowdloan_id, &crowdloan);
 
             match (&crowdloan.call, &crowdloan.target_address) {
                 (Some(call), None) => {
@@ -659,9 +668,6 @@ pub mod pallet {
                 }
             }
 
-            crowdloan.finalized = true;
-            Crowdloans::<T>::insert(crowdloan_id, &crowdloan);
-
             Self::deposit_event(Event::<T>::Finalized { crowdloan_id });
 
             Ok(())
```

### pallets/crowdloan/src/tests.rs
```diff
@@ -1875,6 +1875,206 @@ fn test_finalize_fails_if_call_fails() {
         });
 }
 
+#[test]
+fn test_finalize_fails_if_another_finalize_is_in_progress() {
+    TestState::default()
+        .with_balance(U256::from(1), 300.into())
+        .with_balance(U256::from(2), 300.into())
+        .build_and_execute(|| {
+            let creator: AccountOf<Test> = U256::from(1);
+            let contributor: AccountOf<Test> = U256::from(2);
+            let deposit: BalanceOf<Test> = 50.into();
+            let min_contribution: BalanceOf<Test> = 10.into();
+            let cap: BalanceOf<Test> = 100.into();
+            let end: BlockNumberFor<Test> = 50;
+            let first_crowdloan_id: CrowdloanId = 0;
+            let second_crowdloan_id: CrowdloanId = 1;
+
+            let nested_finalize_call = Box::new(RuntimeCall::Crowdloan(pallet_crowdloan::Call::<
+                Test,
+            >::finalize {
+                crowdloan_id: second_crowdloan_id,
+            }));
+
+            assert_ok!(Crowdloan::create(
+                RuntimeOrigin::signed(creator),
+                deposit,
+                min_contribution,
+                cap,
+                end,
+                Some(nested_finalize_call),
+                None,
+            ));
+            assert_ok!(Crowdloan::create(
+                RuntimeOrigin::signed(creator),
+                deposit,
+                min_contribution,
+                cap,
+                end,
+                Some(noop_call()),
+                None,
+            ));
+
+            run_to_block(10);
+
+            assert_ok!(Crowdloan::contribute(
+                RuntimeOrigin::signed(contributor),
+                first_crowdloan_id,
+                50.into()
+            ));
+            assert_ok!(Crowdloan::contribute(
+                RuntimeOrigin::signed(contributor),
+                second_crowdloan_id,
+                50.into()
+            ));
+
+            run_to_block(60);
+
+            assert_err!(
+                Crowdloan::finalize(RuntimeOrigin::signed(creator), first_crowdloan_id),
+                pallet_crowdloan::Error::<Test>::AlreadyFinalizing
+            );
+
+            assert_eq!(pallet_crowdloan::CurrentCrowdloanId::<Test>::get(), None);
+            assert!(
+                pallet_crowdloan::Crowdloans::<Test>::get(first_crowdloan_id)
+                    .is_some_and(|c| !c.finalized)
+            );
+            assert!(
+                pallet_crowdloan::Crowdloans::<Test>::get(second_crowdloan_id)
+                    .is_some_and(|c| !c.finalized)
+            );
+        });
+}
+
+// The finalize `call` cannot re-enter `withdraw` on the same crowdloan: it is rejected and
+// the extrinsic reverts, so no funds move and `raised` stays consistent with the real balance.
+#[test]
+fn test_finalize_blocks_reentrant_withdraw() {
+    TestState::default()
+        .with_balance(U256::from(1), 200.into()) // creator
+        .with_balance(U256::from(2), 200.into()) // contributor
+        .build_and_execute(|| {
+            let creator: AccountOf<Test> = U256::from(1);
+            let contributor: AccountOf<Test> = U256::from(2);
+            let deposit: BalanceOf<Test> = 50.into();
+            let min_contribution: BalanceOf<Test> = 10.into();
+            let cap: BalanceOf<Test> = 100.into();
+            let end: BlockNumberFor<Test> = 50;
+            let crowdloan_id: CrowdloanId = 0;
+
+            // The finalize call re-enters `withdraw` on the same crowdloan.
+            let reentrant_call = Box::new(RuntimeCall::Crowdloan(
+                pallet_crowdloan::Call::<Test>::withdraw { crowdloan_id },
+            ));
+
+            assert_ok!(Crowdloan::create(
+                RuntimeOrigin::signed(creator),
+                deposit,
+                min_contribution,
+                cap,
+                end,
+                Some(reentrant_call),
+                None,
+            ));
+            run_to_block(10);
+
+            // Creator contributes 30 over the deposit (total 80); contributor fills the cap.
+            assert_ok!(Crowdloan::contribute(
+                RuntimeOrigin::signed(creator),
+                crowdloan_id,
+                30.into()
+            ));
+            assert_ok!(Crowdloan::contribute(
+                RuntimeOrigin::signed(contributor),
+                crowdloan_id,
+                20.into()
+            ));
+
+            let funds_account = pallet_crowdloan::Pallet::<Test>::funds_account(crowdloan_id);
+            assert_eq!(Balances::free_balance(funds_account), cap);
+            let creator_balance_before = Balances::free_balance(creator);
+
+            run_to_block(60);
+
+            // Finalize dispatches the re-entrant withdraw, which is rejected with
+            // `AlreadyFinalized`. Wrap in a storage layer to model the per-extrinsic
+            // transaction the runtime applies in production, so the revert is observable.
+            let outcome = frame_support::storage::with_storage_layer(|| {
+                Crowdloan::finalize(RuntimeOrigin::signed(creator), crowdloan_id)
+            });
+            assert_err!(outcome, pallet_crowdloan::Error::<Test>::AlreadyFinalized);
+
+            // No funds were extracted and accounting is intact.
+            assert_eq!(Balances::free_balance(creator), creator_balance_before);
+            assert_eq!(Balances::free_balance(funds_account), cap);
+            assert_eq!(pallet_crowdloan::CurrentCrowdloanId::<Test>::get(), None);
+            let crowdloan = pallet_crowdloan::Crowdloans::<Test>::get(crowdloan_id).unwrap();
+            assert!(!crowdloan.finalized);
+            assert_eq!(crowdloan.raised, cap);
+
+            // Contributor funds are not frozen: the contributor can still withdraw.
+            assert_ok!(Crowdloan::withdraw(
+                RuntimeOrigin::signed(contributor),
+                crowdloan_id
+            ));
+            assert_eq!(Balances::free_balance(contributor), 200.into());
+        });
+}
+
+// A re-entrant `refund` embedded as the finalize call is likewise rejected before moving funds.
+#[test]
+fn test_finalize_blocks_reentrant_refund() {
+    TestState::default()
+        .with_balance(U256::from(1), 200.into()) // creator
+        .with_balance(U256::from(2), 200.into()) // contributor
+        .build_and_execute(|| {
+            let creator: AccountOf<Test> = U256::from(1);
+            let contributor: AccountOf<Test> = U256::from(2);
+            let deposit: BalanceOf<Test> = 50.into();
+            let min_contribution: BalanceOf<Test> = 10.into();
+            let cap: BalanceOf<Test> = 100.into();
+            let end: BlockNumberFor<Test> = 50;
+            let crowdloan_id: CrowdloanId = 0;
+
+            let reentrant_call = Box::new(RuntimeCall::Crowdloan(
+                pallet_crowdloan::Call::<Test>::refund { crowdloan_id },
+            ));
+
+            assert_ok!(Crowdloan::create(
+                RuntimeOrigin::signed(creator),
+                deposit,
+                min_contribution,
+                cap,
+                end,
+                Some(reentrant_call),
+                None,
+            ));
+            run_to_block(10);
+
+            assert_ok!(Crowdloan::contribute(
+                RuntimeOrigin::signed(creator),
+                crowdloan_id,
+                30.into()
+            ));
+            assert_ok!(Crowdloan::contribute(
+                RuntimeOrigin::signed(contributor),
+                crowdloan_id,
+                20.into()
+            ));
+
+            let funds_account = pallet_crowdloan::Pallet::<Test>::funds_account(crowdloan_id);
+            run_to_block(60);
+
+            // The re-entrant refund hits the `finalized` guard before transferring anything.
+            assert_err!(
+                Crowdloan::finalize(RuntimeOrigin::signed(creator), crowdloan_id),
+                pallet_crowdloan::Error::<Test>::AlreadyFinalized
+            );
+            assert_eq!(Balances::free_balance(funds_account), cap);
+        });
+}
+
 #[test]
 fn test_refund_succeeds() {
     TestState::default()
```

### pallets/crowdloan/src/weights.rs
```diff
@@ -2,9 +2,9 @@
 //! Autogenerated weights for `pallet_crowdloan`
 //!
 //! THIS FILE WAS AUTO-GENERATED USING THE SUBSTRATE BENCHMARK CLI VERSION 49.1.0
-//! DATE: 2026-05-31, STEPS: `50`, REPEAT: `20`, LOW RANGE: `[]`, HIGH RANGE: `[]`
+//! DATE: 2026-06-30, STEPS: `50`, REPEAT: `20`, LOW RANGE: `[]`, HIGH RANGE: `[]`
 //! WORST CASE MAP SIZE: `1000000`
-//! HOSTNAME: `runnervm3jyl0`, CPU: `AMD EPYC 9V74 80-Core Processor`
+//! HOSTNAME: `runnervmmklqx`, CPU: `AMD EPYC 9V74 80-Core Processor`
 //! WASM-EXECUTION: `Compiled`, CHAIN: `None`, DB CACHE: `1024`
 
 // Executed Command:
@@ -22,7 +22,7 @@
 // --no-storage-info
 // --no-min-squares
 // --no-median-slopes
-// --output=/tmp/tmp.QLzNE9hOoG
+// --output=/tmp/tmp.CWtPZcdN9i
 // --template=/home/runner/work/subtensor/subtensor/.maintain/frame-weight-template.hbs
 
 #![cfg_attr(rustfmt, rustfmt_skip)]
@@ -63,8 +63,8 @@ impl<T: frame_system::Config> WeightInfo for SubstrateWeight<T> {
 		// Proof Size summary in bytes:
 		//  Measured:  `119`
 		//  Estimated: `6148`
-		// Minimum execution time: 58_307_000 picoseconds.
-		Weight::from_parts(59_829_000, 6148)
+		// Minimum execution time: 59_888_000 picoseconds.
+		Weight::from_parts(61_110_000, 6148)
 			.saturating_add(T::DbWeight::get().reads(3_u64))
 			.saturating_add(T::DbWeight::get().writes(5_u64))
 	}
@@ -80,8 +80,8 @@ impl<T: frame_system::Config> WeightInfo for SubstrateWeight<T> {
 		// Proof Size summary in bytes:
 		//  Measured:  `448`
 		//  Estimated: `6148`
-		// Minimum execution time: 65_557_000 picoseconds.
-		Weight::from_parts(66_609_000, 6148)
+		// Minimum execution time: 65_807_000 picoseconds.
+		Weight::from_parts(66_819_000, 6148)
 			.saturating_add(T::DbWeight::get().reads(5_u64))
 			.saturating_add(T::DbWeight::get().writes(4_u64))
 	}
@@ -95,28 +95,28 @@ impl<T: frame_system::Config> WeightInfo for SubstrateWeight<T> {
 		// Proof Size summary in bytes:
 		//  Measured:  `408`
 		//  Estimated: `6148`
-		// Minimum execution time: 59_438_000 picoseconds.
-		Weight::from_parts(60_259_000, 6148)
+		// Minimum execution time: 59_447_000 picoseconds.
+		Weight::from_parts(61_220_000, 6148)
 			.saturating_add(T::DbWeight::get().reads(4_u64))
 			.saturating_add(T::DbWeight::get().writes(4_u64))
 	}
 	/// Storage: `Crowdloan::Crowdloans` (r:1 w:1)
 	/// Proof: `Crowdloan::Crowdloans` (`max_values`: None, `max_size`: Some(282), added: 2757, mode: `MaxEncodedLen`)
+	/// Storage: `Crowdloan::CurrentCrowdloanId` (r:1 w:1)
+	/// Proof: `Crowdloan::CurrentCrowdloanId` (`max_values`: Some(1), `max_size`: Some(4), added: 499, mode: `MaxEncodedLen`)
 	/// Storage: `Preimage::PreimageFor` (r:1 w:0)
 	/// Proof: `Preimage::PreimageFor` (`max_values`: None, `max_size`: Some(4194344), added: 4196819, mode: `MaxEncodedLen`)
 	/// Storage: `SafeMode::EnteredUntil` (r:1 w:0)
 	/// Proof: `SafeMode::EnteredUntil` (`max_values`: Some(1), `max_size`: Some(4), added: 499, mode: `MaxEncodedLen`)
 	/// Storage: `SubtensorModule::ColdkeySwapAnnouncements` (r:1 w:0)
 	/// Proof: `SubtensorModule::ColdkeySwapAnnouncements` (`max_values`: None, `max_size`: None, mode: `Measured`)
-	/// Storage: `Crowdloan::CurrentCrowdloanId` (r:0 w:1)
-	/// Proof: `Crowdloan::CurrentCrowdloanId` (`max_values`: Some(1), `max_size`: Some(4), added: 499, mode: `MaxEncodedLen`)
 	fn finalize() -> Weight {
 		// Proof Size summary in bytes:
 		//  Measured:  `1181`
 		//  Estimated: `4197809`
-		// Minimum execution time: 30_264_000 picoseconds.
-		Weight::from_parts(31_507_000, 4197809)
-			.saturating_add(T::DbWeight::get().reads(4_u64))
+		// Minimum execution time: 32_548_000 picoseconds.
+		Weight::from_parts(34_110_000, 4197809)
+			.saturating_add(T::DbWeight::get().reads(5_u64))
 			.saturating_add(T::DbWeight::get().writes(2_u64))
 	}
 	/// Storage: `Crowdloan::Crowdloans` (r:1 w:1)
@@ -130,10 +130,10 @@ impl<T: frame_system::Config> WeightInfo for SubstrateWeight<T> {
 		// Proof Size summary in bytes:
 		//  Measured:  `324 + k * (46 ±0)`
 		//  Estimated: `3747 + k * (2579 ±0)`
-		// Minimum execution time: 108_910_000 picoseconds.
-		Weight::from_parts(110_703_000, 3747)
-			// Standard Error: 96_515
-			.saturating_add(Weight::from_parts(39_503_253, 0).saturating_mul(k.into()))
+		// Minimum execution time: 109_320_000 picoseconds.
+		Weight::from_parts(110_392_000, 3747)
+			// Standard Error: 94_672
+			.saturating_add(Weight::from_parts(39_822_919, 0).saturating_mul(k.into()))
 			.saturating_add(T::DbWeight::get().reads(2_u64))
 			.saturating_add(T::DbWeight::get().reads((2_u64).saturating_mul(k.into())))
 			.saturating_add(T::DbWeight::get().writes((2_u64).saturating_mul(k.into())))
@@ -151,8 +151,8 @@ impl<T: frame_system::Config> WeightInfo for SubstrateWeight<T> {
 		// Proof Size summary in bytes:
 		//  Measured:  `370`
 		//  Estimated: `6148`
-		// Minimum execution time: 66_138_000 picoseconds.
-		Weight::from_parts(66_939_000, 6148)
+		// Minimum execution time: 69_442_000 picoseconds.
+		Weight::from_parts(70_724_000, 6148)
 			.saturating_add(T::DbWeight::get().reads(4_u64))
 			.saturating_add(T::DbWeight::get().writes(5_u64))
 	}
@@ -164,8 +164,8 @@ impl<T: frame_system::Config> WeightInfo for SubstrateWeight<T> {
 		// Proof Size summary in bytes:
 		//  Measured:  `229`
 		//  Estimated: `3747`
-		// Minimum execution time: 12_639_000 picoseconds.
-		Weight::from_parts(13_259_000, 3747)
+		// Minimum execution time: 13_049_000 picoseconds.
+		Weight::from_parts(13_510_000, 3747)
 			.saturating_add(T::DbWeight::get().reads(2_u64))
 			.saturating_add(T::DbWeight::get().writes(1_u64))
 	}
@@ -175,8 +175,8 @@ impl<T: frame_system::Config> WeightInfo for SubstrateWeight<T> {
 		// Proof Size summary in bytes:
 		//  Measured:  `229`
 		//  Estimated: `3747`
-		// Minimum execution time: 11_637_000 picoseconds.
-		Weight::from_parts(12_048_000, 3747)
+		// Minimum execution time: 11_557_000 picoseconds.
+		Weight::from_parts(12_318_000, 3747)
 			.saturating_add(T::DbWeight::get().reads(1_u64))
 			.saturating_add(T::DbWeight::get().writes(1_u64))
 	}
@@ -186,8 +186,8 @@ impl<T: frame_system::Config> WeightInfo for SubstrateWeight<T> {
 		// Proof Size summary in bytes:
 		//  Measured:  `229`
 		//  Estimated: `3747`
-		// Minimum execution time: 11_026_000 picoseconds.
-		Weight::from_parts(11_357_000, 3747)
+		// Minimum execution time: 11_386_000 picoseconds.
+		Weight::from_parts(11_797_000, 3747)
 			.saturating_add(T::DbWeight::get().reads(1_u64))
 			.saturating_add(T::DbWeight::get().writes(1_u64))
 	}
@@ -201,8 +201,8 @@ impl<T: frame_system::Config> WeightInfo for SubstrateWeight<T> {
 		// Proof Size summary in bytes:
 		//  Measured:  `293`
 		//  Estimated: `3747`
-		// Minimum execution time: 15_263_000 picoseconds.
-		Weight::from_parts(16_024_000, 3747)
+		// Minimum execution time: 15_924_000 picoseconds.
+		Weight::from_parts(16_805_000, 3747)
 			.saturating_add(T::DbWeight::get().reads(2_u64))
 			.saturating_add(T::DbWeight::get().writes(1_u64))
 	}
@@ -222,8 +222,8 @@ impl WeightInfo for () {
 		// Proof Size summary in bytes:
 		//  Measured:  `119`
 		//  Estimated: `6148`
-		// Minimum execution time: 58_307_000 picoseconds.
-		Weight::from_parts(59_829_000, 6148)
+		// Minimum execution time: 59_888_000 picoseconds.
+		Weight::from_parts(61_110_000, 6148)
 			.saturating_add(RocksDbWeight::get().reads(3_u64))
 			.saturating_add(RocksDbWeight::get().writes(5_u64))
 	}
@@ -239,8 +239,8 @@ impl WeightInfo for () {
 		// Proof Size summary in bytes:
 		//  Measured:  `448`
 		//  Estimated: `6148`
-		// Minimum execution time: 65_557_000 picoseconds.
-		Weight::from_parts(66_609_000, 6148)
+		// Minimum execution time: 65_807_000 picoseconds.
+		Weight::from_parts(66_819_000, 6148)
 			.saturating_add(RocksDbWeight::get().reads(5_u64))
 			.saturating_add(RocksDbWeight::get().writes(4_u64))
 	}
@@ -254,28 +254,28 @@ impl WeightInfo for () {
 		// Proof Size summary in bytes:
 		//  Measured:  `408`
 		//  Estimated: `6148`
-		// Minimum execution time: 59_438_000 picoseconds.
-		Weight::from_parts(60_259_000, 6148)
+		// Minimum execution time: 59_447_000 picoseconds.
+		Weight::from_parts(61_220_000, 6148)
 			.saturating_add(RocksDbWeight::get().reads(4_u64))
 			.saturating_add(RocksDbWeight::get().writes(4_u64))
 	}
 	/// Storage: `Crowdloan::Crowdloans` (r:1 w:1)
 	/// Proof: `Crowdloan::Crowdloans` (`max_values`: None, `max_size`: Some(282), added: 2757, mode: `MaxEncodedLen`)
+	/// Storage: `Crowdloan::CurrentCrowdloanId` (r:1 w:1)
+	/// Proof: `Crowdloan::CurrentCrowdloanId` (`max_values`: Some(1), `max_size`: Some(4), added: 499, mode: `MaxEncodedLen`)
 	/// Storage: `Preimage::PreimageFor` (r:1 w:0)
 	/// Proof: `Preimage::PreimageFor` (`max_values`: None, `max_size`: Some(4194344), added: 4196819, mode: `MaxEncodedLen`)
 	/// Storage: `SafeMode::EnteredUntil` (r:1 w:0)
 	/// Proof: `SafeMode::EnteredUntil` (`max_values`: Some(1), `max_size`: Some(4), added: 499, mode: `MaxEncodedLen`)
 	/// Storage: `SubtensorModule::ColdkeySwapAnnouncements` (r:1 w:0)
 	/// Proof: `SubtensorModule::ColdkeySwapAnnouncements` (`max_values`: None, `max_size`: None, mode: `Measured`)
-	/// Storage: `Crowdloan::CurrentCrowdloanId` (r:0 w:1)
-	/// Proof: `Crowdloan::CurrentCrowdloanId` (`max_values`: Some(1), `max_size`: Some(4), added: 499, mode: `MaxEncodedLen`)
 	fn finalize() -> Weight {
 		// Proof Size summary in bytes:
 		//  Measured:  `1181`
 		//  Estimated: `4197809`
-		// Minimum execution time: 30_264_000 picoseconds.
-		Weight::from_parts(31_507_000, 4197809)
-			.saturating_add(RocksDbWeight::get().reads(4_u64))
+		// Minimum execution time: 32_548_000 picoseconds.
+		Weight::from_parts(34_110_000, 4197809)
+			.saturating_add(RocksDbWeight::get().reads(5_u64))
 			.saturating_add(RocksDbWeight::get().writes(2_u64))
 	}
 	/// Storage: `Crowdloan::Crowdloans` (r:1 w:1)
@@ -289,10 +289,10 @@ impl WeightInfo for () {
 		// Proof Size summary in bytes:
 		//  Measured:  `324 + k * (46 ±0)`
 		//  Estimated: `3747 + k * (2579 ±0)`
-		// Minimum execution time: 108_910_000 picoseconds.
-		Weight::from_parts(110_703_000, 3747)
-			// Standard Error: 96_515
-			.saturating_add(Weight::from_parts(39_503_253, 0).saturating_mul(k.into()))
+		// Minimum execution time: 109_320_000 picoseconds.
+		Weight::from_parts(110_392_000, 3747)
+			// Standard Error: 94_672
+			.saturating_add(Weight::from_parts(39_822_919, 0).saturating_mul(k.into()))
 			.saturating_add(RocksDbWeight::get().reads(2_u64))
 			.saturating_add(RocksDbWeight::get().reads((2_u64).saturating_mul(k.into())))
 			.saturating_add(RocksDbWeight::get().writes((2_u64).saturating_mul(k.into())))
@@ -310,8 +310,8 @@ impl WeightInfo for () {
 		// Proof Size summary in bytes:
 		//  Measured:  `370`
 		//  Estimated: `6148`
-		// Minimum execution time: 66_138_000 picoseconds.
-		Weight::from_parts(66_939_000, 6148)
+		// Minimum execution time: 69_442_000 picoseconds.
+		Weight::from_parts(70_724_000, 6148)
 			.saturating_add(RocksDbWeight::get().reads(4_u64))
 			.saturating_add(RocksDbWeight::get().writes(5_u64))
 	}
@@ -323,8 +323,8 @@ impl WeightInfo for () {
 		// Proof Size summary in bytes:
 		//  Measured:  `229`
 		//  Estimated: `3747`
-		// Minimum execution time: 12_639_000 picoseconds.
-		Weight::from_parts(13_259_000, 3747)
+		// Minimum execution time: 13_049_000 picoseconds.
+		Weight::from_parts(13_510_000, 3747)
 			.saturating_add(RocksDbWeight::get().reads(2_u64))
 			.saturating_add(RocksDbWeight::get().writes(1_u64))
 	}
@@ -334,8 +334,8 @@ impl WeightInfo for () {
 		// Proof Size summary in bytes:
 		//  Measured:  `229`
 		//  Estimated: `3747`
-		// Minimum execution time: 11_637_000 picoseconds.
-		Weight::from_parts(12_048_000, 3747)
+		// Minimum execution time: 11_557_000 picoseconds.
+		Weight::from_parts(12_318_000, 3747)
 			.saturating_add(RocksDbWeight::get().reads(1_u64))
 			.saturating_add(RocksDbWeight::get().writes(1_u64))
 	}
@@ -345,8 +345,8 @@ impl WeightInfo for () {
 		// Proof Size summary in bytes:
 		//  Measured:  `229`
 		//  Estimated: `3747`
-		// Minimum execution time: 11_026_000 picoseconds.
-		Weight::from_parts(11_357_000, 3747)
+		// Minimum execution time: 11_386_000 picoseconds.
+		Weight::from_parts(11_797_000, 3747)
 			.saturating_add(RocksDbWeight::get().reads(1_u64))
 			.saturating_add(RocksDbWeight::get().writes(1_u64))
 	}
@@ -360,8 +360,8 @@ impl WeightInfo for () {
 		// Proof Size summary in bytes:
 		//  Measured:  `293`
 		//  Estimated: `3747`
-		// Minimum execution time: 15_263_000 picoseconds.
-		Weight::from_parts(16_024_000, 3747)
+		// Minimum execution time: 15_924_000 picoseconds.
+		Weight::from_parts(16_805_000, 3747)
 			.saturating_add(RocksDbWeight::get().reads(2_u64))
 			.saturating_add(RocksDbWeight::get().writes(1_u64))
 	}
```

### pallets/proxy/src/weights.rs
```diff
@@ -2,9 +2,9 @@
 //! Autogenerated weights for `pallet_subtensor_proxy`
 //!
 //! THIS FILE WAS AUTO-GENERATED USING THE SUBSTRATE BENCHMARK CLI VERSION 49.1.0
-//! DATE: 2026-06-24, STEPS: `50`, REPEAT: `20`, LOW RANGE: `[]`, HIGH RANGE: `[]`
+//! DATE: 2026-06-30, STEPS: `50`, REPEAT: `20`, LOW RANGE: `[]`, HIGH RANGE: `[]`
 //! WORST CASE MAP SIZE: `1000000`
-//! HOSTNAME: `runnervm7b5n9`, CPU: `AMD EPYC 7763 64-Core Processor`
+//! HOSTNAME: `runnervmmklqx`, CPU: `AMD EPYC 9V74 80-Core Processor`
 //! WASM-EXECUTION: `Compiled`, CHAIN: `None`, DB CACHE: `1024`
 
 // Executed Command:
@@ -22,7 +22,7 @@
 // --no-storage-info
 // --no-min-squares
 // --no-median-slopes
-// --output=/tmp/tmp.y2xrvMbiMs
+// --output=/tmp/tmp.WnI3UJn7lR
 // --template=/home/runner/work/subtensor/subtensor/.maintain/frame-weight-template.hbs
 
 #![cfg_attr(rustfmt, rustfmt_skip)]
@@ -66,10 +66,10 @@ impl<T: frame_system::Config> WeightInfo for SubstrateWeight<T> {
 		// Proof Size summary in bytes:
 		//  Measured:  `637 + p * (37 ±0)`
 		//  Estimated: `4254 + p * (37 ±0)`
-		// Minimum execution time: 26_189_000 picoseconds.
-		Weight::from_parts(27_505_550, 4254)
-			// Standard Error: 4_793
-			.saturating_add(Weight::from_parts(69_619, 0).saturating_mul(p.into()))
+		// Minimum execution time: 23_404_000 picoseconds.
+		Weight::from_parts(24_775_699, 4254)
+			// Standard Error: 3_659
+			.saturating_add(Weight::from_parts(36_370, 0).saturating_mul(p.into()))
 			.saturating_add(T::DbWeight::get().reads(3_u64))
 			.saturating_add(T::DbWeight::get().writes(1_u64))
 			.saturating_add(Weight::from_parts(0, 37).saturating_mul(p.into()))
@@ -92,12 +92,12 @@ impl<T: frame_system::Config> WeightInfo for SubstrateWeight<T> {
 		// Proof Size summary in bytes:
 		//  Measured:  `894 + a * (68 ±0) + p * (37 ±0)`
 		//  Estimated: `8615 + a * (68 ±0) + p * (37 ±0)`
-		// Minimum execution time: 50_874_000 picoseconds.
-		Weight::from_parts(52_716_407, 8615)
-			// Standard Error: 2_189
-			.saturating_add(Weight::from_parts(213_947, 0).saturating_mul(a.into()))
-			// Standard Error: 8_769
-			.saturating_add(Weight::from_parts(39_570, 0).saturating_mul(p.into()))
+		// Minimum execution time: 48_461_000 picoseconds.
+		Weight::from_parts(50_907_754, 8615)
+			// Standard Error: 1_796
+			.saturating_add(Weight::from_parts(193_963, 0).saturating_mul(a.into()))
+			// Standard Error: 7_193
+			.saturating_add(Weight::from_parts(31_645, 0).saturating_mul(p.into()))
 			.saturating_add(T::DbWeight::get().reads(5_u64))
 			.saturating_add(T::DbWeight::get().writes(3_u64))
 			.saturating_add(Weight::from_parts(0, 68).saturating_mul(a.into()))
@@ -113,12 +113,12 @@ impl<T: frame_system::Config> WeightInfo for SubstrateWeight<T> {
 		// Proof Size summary in bytes:
 		//  Measured:  `299 + a * (68 ±0)`
 		//  Estimated: `8615`
-		// Minimum execution time: 24_646_000 picoseconds.
-		Weight::from_parts(25_351_648, 8615)
-			// Standard Error: 1_263
-			.saturating_add(Weight::from_parts(202_639, 0).saturating_mul(a.into()))
-			// Standard Error: 5_058
-			.saturating_add(Weight::from_parts(17_145, 0).saturating_mul(p.into()))
+		// Minimum execution time: 23_364_000 picoseconds.
+		Weight::from_parts(23_739_396, 8615)
+			// Standard Error: 1_621
+			.saturating_add(Weight::from_parts(202_628, 0).saturating_mul(a.into()))
+			// Standard Error: 6_495
+			.saturating_add(Weight::from_parts(56_059, 0).saturating_mul(p.into()))
 			.saturating_add(T::DbWeight::get().reads(2_u64))
 			.saturating_add(T::DbWeight::get().writes(2_u64))
 	}
@@ -132,12 +132,12 @@ impl<T: frame_system::Config> WeightInfo for SubstrateWeight<T> {
 		// Proof Size summary in bytes:
 		//  Measured:  `299 + a * (68 ±0)`
 		//  Estimated: `8615`
-		// Minimum execution time: 24_686_000 picoseconds.
-		Weight::from_parts(25_447_040, 8615)
-			// Standard Error: 1_204
-			.saturating_add(Weight::from_parts(197_519, 0).saturating_mul(a.into()))
-			// Standard Error: 4_824
-			.saturating_add(Weight::from_parts(26_426, 0).saturating_mul(p.into()))
+		// Minimum execution time: 23_735_000 picoseconds.
+		Weight::from_parts(24_366_666, 8615)
+			// Standard Error: 1_017
+			.saturating_add(Weight::from_parts(180_283, 0).saturating_mul(a.into()))
+			// Standard Error: 4_075
+			.saturating_add(Weight::from_parts(57_043, 0).saturating_mul(p.into()))
 			.saturating_add(T::DbWeight::get().reads(2_u64))
 			.saturating_add(T::DbWeight::get().writes(2_u64))
 	}
@@ -153,12 +153,12 @@ impl<T: frame_system::Config> WeightInfo for SubstrateWeight<T> {
 		// Proof Size summary in bytes:
 		//  Measured:  `308 + a * (68 ±0) + p * (37 ±0)`
 		//  Estimated: `8615`
-		// Minimum execution time: 32_170_000 picoseconds.
-		Weight::from_parts(32_440_222, 8615)
-			// Standard Error: 1_515
-			.saturating_add(Weight::from_parts(200_631, 0).saturating_mul(a.into()))
-			// Standard Error: 6_071
-			.saturating_add(Weight::from_parts(68_700, 0).saturating_mul(p.into()))
+		// Minimum execution time: 30_245_000 picoseconds.
+		Weight::from_parts(30_956_665, 8615)
+			// Standard Error: 1_239
+			.saturating_add(Weight::from_parts(208_387, 0).saturating_mul(a.into()))
+			// Standard Error: 4_964
+			.saturating_add(Weight::from_parts(40_268, 0).saturating_mul(p.into()))
 			.saturating_add(T::DbWeight::get().reads(3_u64))
 			.saturating_add(T::DbWeight::get().writes(2_u64))
 	}
@@ -169,10 +169,10 @@ impl<T: frame_system::Config> WeightInfo for SubstrateWeight<T> {
 		// Proof Size summary in bytes:
 		//  Measured:  `119 + p * (37 ±0)`
 		//  Estimated: `4254`
-		// Minimum execution time: 23_795_000 picoseconds.
-		Weight::from_parts(24_685_958, 4254)
-			// Standard Error: 3_450
-			.saturating_add(Weight::from_parts(80_991, 0).saturating_mul(p.into()))
+		// Minimum execution time: 22_062_000 picoseconds.
+		Weight::from_parts(22_896_760, 4254)
+			// Standard Error: 1_967
+			.saturating_add(Weight::from_parts(62_251, 0).saturating_mul(p.into()))
 			.saturating_add(T::DbWeight::get().reads(1_u64))
 			.saturating_add(T::DbWeight::get().writes(1_u64))
 	}
@@ -185,10 +185,10 @@ impl<T: frame_system::Config> WeightInfo for SubstrateWeight<T> {
 		// Proof Size summary in bytes:
 		//  Measured:  `119 + p * (37 ±0)`
 		//  Estimated: `4254`
-		// Minimum execution time: 25_578_000 picoseconds.
-		Weight::from_parts(26_614_984, 4254)
-			// Standard Error: 3_099
-			.saturating_add(Weight::from_parts(59_205, 0).saturating_mul(p.into()))
+		// Minimum execution time: 23_534_000 picoseconds.
+		Weight::from_parts(24_759_349, 4254)
+			// Standard Error: 2_839
+			.saturating_add(Weight::from_parts(54_772, 0).saturating_mul(p.into()))
 			.saturating_add(T::DbWeight::get().reads(1_u64))
 			.saturating_add(T::DbWeight::get().writes(2_u64))
 	}
@@ -199,10 +199,10 @@ impl<T: frame_system::Config> WeightInfo for SubstrateWeight<T> {
 		// Proof Size summary in bytes:
 		//  Measured:  `119 + p * (37 ±0)`
 		//  Estimated: `4254`
-		// Minimum execution time: 25_367_000 picoseconds.
-		Weight::from_parts(26_441_977, 4254)
-			// Standard Error: 4_077
-			.saturating_add(Weight::from_parts(46_473, 0).saturating_mul(p.into()))
+		// Minimum execution time: 23_394_000 picoseconds.
+		Weight::from_parts(24_696_087, 4254)
+			// Standard Error: 3_088
+			.saturating_add(Weight::from_parts(16_241, 0).saturating_mul(p.into()))
 			.saturating_add(T::DbWeight::get().reads(1_u64))
 			.saturating_add(T::DbWeight::get().writes(1_u64))
 	}
@@ -213,10 +213,10 @@ impl<T: frame_system::Config> WeightInfo for SubstrateWeight<T> {
 		// Proof Size summary in bytes:
 		//  Measured:  `139`
 		//  Estimated: `4254`
-		// Minimum execution time: 25_557_000 picoseconds.
-		Weight::from_parts(26_686_208, 4254)
-			// Standard Error: 3_588
-			.saturating_add(Weight::from_parts(27_191, 0).saturating_mul(p.into()))
+		// Minimum execution time: 23_624_000 picoseconds.
+		Weight::from_parts(24_522_616, 4254)
+			// Standard Error: 2_148
+			.saturating_add(Weight::from_parts(26_274, 0).saturating_mul(p.into()))
 			.saturating_add(T::DbWeight::get().reads(1_u64))
 			.saturating_add(T::DbWeight::get().writes(1_u64))
 	}
@@ -227,10 +227,10 @@ impl<T: frame_system::Config> WeightInfo for SubstrateWeight<T> {
 		// Proof Size summary in bytes:
 		//  Measured:  `156 + p * (37 ±0)`
 		//  Estimated: `4254`
-		// Minimum execution time: 24_695_000 picoseconds.
-		Weight::from_parts(25_826_161, 4254)
-			// Standard Error: 3_578
-			.saturating_add(Weight::from_parts(40_613, 0).saturating_mul(p.into()))
+		// Minimum execution time: 22_533_000 picoseconds.
+		Weight::from_parts(23_190_575, 4254)
+			// Standard Error: 5_507
+			.saturating_add(Weight::from_parts(140_005, 0).saturating_mul(p.into()))
 			.saturating_add(T::DbWeight::get().reads(1_u64))
 			.saturating_add(T::DbWeight::get().writes(1_u64))
 	}
@@ -244,8 +244,8 @@ impl<T: frame_system::Config> WeightInfo for SubstrateWeight<T> {
 		// Proof Size summary in bytes:
 		//  Measured:  `412`
 		//  Estimated: `8615`
-		// Minimum execution time: 43_431_000 picoseconds.
-		Weight::from_parts(44_262_000, 8615)
+		// Minimum execution time: 43_273_000 picoseconds.
+		Weight::from_parts(44_405_000, 8615)
 			.saturating_add(T::DbWeight::get().reads(3_u64))
 			.saturating_add(T::DbWeight::get().writes(3_u64))
 	}
@@ -258,10 +258,10 @@ impl<T: frame_system::Config> WeightInfo for SubstrateWeight<T> {
 		// Proof Size summary in bytes:
 		//  Measured:  `119 + p * (37 ±0)`
 		//  Estimated: `4254`
-		// Minimum execution time: 13_275_000 picoseconds.
-		Weight::from_parts(14_036_984, 4254)
-			// Standard Error: 2_451
-			.saturating_add(Weight::from_parts(40_086, 0).saturating_mul(p.into()))
+		// Minimum execution time: 12_107_000 picoseconds.
+		Weight::from_parts(12_805_973, 4254)
+			// Standard Error: 1_732
+			.saturating_add(Weight::from_parts(34_485, 0).saturating_mul(p.into()))
 			.saturating_add(T::DbWeight::get().reads(1_u64))
 			.saturating_add(T::DbWeight::get().writes(1_u64))
 	}
@@ -282,10 +282,10 @@ impl WeightInfo for () {
 		// Proof Size summary in bytes:
 		//  Measured:  `637 + p * (37 ±0)`
 		//  Estimated: `4254 + p * (37 ±0)`
-		// Minimum execution time: 26_189_000 picoseconds.
-		Weight::from_parts(27_505_550, 4254)
-			// Standard Error: 4_793
-			.saturating_add(Weight::from_parts(69_619, 0).saturating_mul(p.into()))
+		// Minimum execution time: 23_404_000 picoseconds.
+		Weight::from_parts(24_775_699, 4254)
+			// Standard Error: 3_659
+			.saturating_add(Weight::from_parts(36_370, 0).saturating_mul(p.into()))
 			.saturating_add(RocksDbWeight::get().reads(3_u64))
 			.saturating_add(RocksDbWeight::get().writes(1_u64))
 			.saturating_add(Weight::from_parts(0, 37).saturating_mul(p.into()))
@@ -308,12 +308,12 @@ impl WeightInfo for () {
 		// Proof Size summary in bytes:
 		//  Measured:  `894 + a * (68 ±0) + p * (37 ±0)`
 		//  Estimated: `8615 + a * (68 ±0) + p * (37 ±0)`
-		// Minimum execution time: 50_874_000 picoseconds.
-		Weight::from_parts(52_716_407, 8615)
-			// Standard Error: 2_189
-			.saturating_add(Weight::from_parts(213_947, 0).saturating_mul(a.into()))
-			// Standard Error: 8_769
-			.saturating_add(Weight::from_parts(39_570, 0).saturating_mul(p.into()))
+		// Minimum execution time: 48_461_000 picoseconds.
+		Weight::from_parts(50_907_754, 8615)
+			// Standard Error: 1_796
+			.saturating_add(Weight::from_parts(193_963, 0).saturating_mul(a.into()))
+			// Standard Error: 7_193
+			.saturating_add(Weight::from_parts(31_645, 0).saturating_mul(p.into()))
 			.saturating_add(RocksDbWeight::get().reads(5_u64))
 			.saturating_add(RocksDbWeight::get().writes(3_u64))
 			.saturating_add(Weight::from_parts(0, 68).saturating_mul(a.into()))
@@ -329,12 +329,12 @@ impl WeightInfo for () {
 		// Proof Size summary in bytes:
 		//  Measured:  `299 + a * (68 ±0)`
 		//  Estimated: `8615`
-		// Minimum execution time: 24_646_000 picoseconds.
-		Weight::from_parts(25_351_648, 8615)
-			// Standard Error: 1_263
-			.saturating_add(Weight::from_parts(202_639, 0).saturating_mul(a.into()))
-			// Standard Error: 5_058
-			.saturating_add(Weight::from_parts(17_145, 0).saturating_mul(p.into()))
+		// Minimum execution time: 23_364_000 picoseconds.
+		Weight::from_parts(23_739_396, 8615)
+			// Standard Error: 1_621
+			.saturating_add(Weight::from_parts(202_628, 0).saturating_mul(a.into()))
+			// Standard Error: 6_495
+			.saturating_add(Weight::from_parts(56_059, 0).saturating_mul(p.into()))
 			.saturating_add(RocksDbWeight::get().reads(2_u64))
 			.saturating_add(RocksDbWeight::get().writes(2_u64))
 	}
@@ -348,12 +348,12 @@ impl WeightInfo for () {
 		// Proof Size summary in bytes:
 		//  Measured:  `299 + a * (68 ±0)`
 		//  Estimated: `8615`
-		// Minimum execution time: 24_686_000 picoseconds.
-		Weight::from_parts(25_447_040, 8615)
-			// Standard Error: 1_204
-			.saturating_add(Weight::from_parts(197_519, 0).saturating_mul(a.into()))
-			// Standard Error: 4_824
-			.saturating_add(Weight::from_parts(26_426, 0).saturating_mul(p.into()))
+		// Minimum execution time: 23_735_000 picoseconds.
+		Weight::from_parts(24_366_666, 8615)
+			// Standard Error: 1_017
+			.saturating_add(Weight::from_parts(180_283, 0).saturating_mul(a.into()))
+			// Standard Error: 4_075
+			.saturating_add(Weight::from_parts(57_043, 0).saturating_mul(p.into()))
 			.saturating_add(RocksDbWeight::get().reads(2_u64))
 			.saturating_add(RocksDbWeight::get().writes(2_u64))
 	}
@@ -369,12 +369,12 @@ impl WeightInfo for () {
 		// Proof Size summary in bytes:
 		//  Measured:  `308 + a * (68 ±0) + p * (37 ±0)`
 		//  Estimated: `8615`
-		// Minimum execution time: 32_170_000 picoseconds.
-		Weight::from_parts(32_440_222, 8615)
-			// Standard Error: 1_515
-			.saturating_add(Weight::from_parts(200_631, 0).saturating_mul(a.into()))
-			// Standard Error: 6_071
-			.saturating_add(Weight::from_parts(68_700, 0).saturating_mul(p.into()))
+		// Minimum execution time: 30_245_000 picoseconds.
+		Weight::from_parts(30_956_665, 8615)
+			// Standard Error: 1_239
+			.saturating_add(Weight::from_parts(208_387, 0).saturating_mul(a.into()))
+			// Standard Error: 4_964
+			.saturating_add(Weight::from_parts(40_268, 0).saturating_mul(p.into()))
 			.saturating_add(RocksDbWeight::get().reads(3_u64))
 			.saturating_add(RocksDbWeight::get().writes(2_u64))
 	}
@@ -385,10 +385,10 @@ impl WeightInfo for () {
 		// Proof Size summary in bytes:
 		//  Measured:  `119 + p * (37 ±0)`
 		//  Estimated: `4254`
-		// Minimum execution time: 23_795_000 picoseconds.
-		Weight::from_parts(24_685_958, 4254)
-			// Standard Error: 3_450
-			.saturating_add(Weight::from_parts(80_991, 0).saturating_mul(p.into()))
+		// Minimum execution time: 22_062_000 picoseconds.
+		Weight::from_parts(22_896_760, 4254)
+			// Standard Error: 1_967
+			.saturating_add(Weight::from_parts(62_251, 0).saturating_mul(p.into()))
 			.saturating_add(RocksDbWeight::get().reads(1_u64))
 			.saturating_add(RocksDbWeight::get().writes(1_u64))
 	}
@@ -401,10 +401,10 @@ impl WeightInfo for () {
 		// Proof Size summary in bytes:
 		//  Measured:  `119 + p * (37 ±0)`
 		//  Estimated: `4254`
-		// Minimum execution time: 25_578_000 picoseconds.
-		Weight::from_parts(26_614_984, 4254)
-			// Standard Error: 3_099
-			.saturating_add(Weight::from_parts(59_205, 0).saturating_mul(p.into()))
+		// Minimum execution time: 23_534_000 picoseconds.
+		Weight::from_parts(24_759_349, 4254)
+			// Standard Error: 2_839
+			.saturating_add(Weight::from_parts(54_772, 0).saturating_mul(p.into()))
 			.saturating_add(RocksDbWeight::get().reads(1_u64))
 			.saturating_add(RocksDbWeight::get().writes(2_u64))
 	}
@@ -415,10 +415,10 @@ impl WeightInfo for () {
 		// Proof Size summary in bytes:
 		//  Measured:  `119 + p * (37 ±0)`
 		//  Estimated: `4254`
-		// Minimum execution time: 25_367_000 picoseconds.
-		Weight::from_parts(26_441_977, 4254)
-			// Standard Error: 4_077
-			.saturating_add(Weight::from_parts(46_473, 0).saturating_mul(p.into()))
+		// Minimum execution time: 23_394_000 picoseconds.
+		Weight::from_parts(24_696_087, 4254)
+			// Standard Error: 3_088
+			.saturating_add(Weight::from_parts(16_241, 0).saturating_mul(p.into()))
 			.saturating_add(RocksDbWeight::get().reads(1_u64))
 			.saturating_add(RocksDbWeight::get().writes(1_u64))
 	}
@@ -429,10 +429,10 @@ impl WeightInfo for () {
 		// Proof Size summary in bytes:
 		//  Measured:  `139`
 		//  Estimated: `4254`
-		// Minimum execution time: 25_557_000 picoseconds.
-		Weight::from_parts(26_686_208, 4254)
-			// Standard Error: 3_588
-			.saturating_add(Weight::from_parts(27_191, 0).saturating_mul(p.into()))
+		// Minimum execution time: 23_624_000 picoseconds.
+		Weight::from_parts(24_522_616, 4254)
+			// Standard Error: 2_148
+			.saturating_add(Weight::from_parts(26_274, 0).saturating_mul(p.into()))
 			.saturating_add(RocksDbWeight::get().reads(1_u64))
 			.saturating_add(RocksDbWeight::get().writes(1_u64))
 	}
@@ -443,10 +443,10 @@ impl WeightInfo for () {
 		// Proof Size summary in bytes:
 		//  Measured:  `156 + p * (37 ±0)`
 		//  Estimated: `4254`
-		// Minimum execution time: 24_695_000 picoseconds.
-		Weight::from_parts(25_826_161, 4254)
-			// Standard Error: 3_578
-			.saturating_add(Weight::from_parts(40_613, 0).saturating_mul(p.into()))
+		// Minimum execution time: 22_533_000 picoseconds.
+		Weight::from_parts(23_190_575, 4254)
+			// Standard Error: 5_507
+			.saturating_add(Weight::from_parts(140_005, 0).saturating_mul(p.into()))
 			.saturating_add(RocksDbWeight::get().reads(1_u64))
 			.saturating_add(RocksDbWeight::get().writes(1_u64))
 	}
@@ -460,8 +460,8 @@ impl WeightInfo for () {
 		// Proof Size summary in bytes:
 		//  Measured:  `412`
 		//  Estimated: `8615`
-		// Minimum execution time: 43_431_000 picoseconds.
-		Weight::from_parts(44_262_000, 8615)
+		// Minimum execution time: 43_273_000 picoseconds.
+		Weight::from_parts(44_405_000, 8615)
 			.saturating_add(RocksDbWeight::get().reads(3_u64))
 			.saturating_add(RocksDbWeight::get().writes(3_u64))
 	}
@@ -474,10 +474,10 @@ impl WeightInfo for () {
 		// Proof Size summary in bytes:
 		//  Measured:  `119 + p * (37 ±0)`
 		//  Estimated: `4254`
-		// Minimum execution time: 13_275_000 picoseconds.
-		Weight::from_parts(14_036_984, 4254)
-			// Standard Error: 2_451
-			.saturating_add(Weight::from_parts(40_086, 0).saturating_mul(p.into()))
+		// Minimum execution time: 12_107_000 picoseconds.
+		Weight::from_parts(12_805_973, 4254)
+			// Standard Error: 1_732
+			.saturating_add(Weight::from_parts(34_485, 0).saturating_mul(p.into()))
 			.saturating_add(RocksDbWeight::get().reads(1_u64))
 			.saturating_add(RocksDbWeight::get().writes(1_u64))
 	}
```

### pallets/utility/src/weights.rs
```diff
@@ -2,9 +2,9 @@
 //! Autogenerated weights for `pallet_subtensor_utility`
 //!
 //! THIS FILE WAS AUTO-GENERATED USING THE SUBSTRATE BENCHMARK CLI VERSION 49.1.0
-//! DATE: 2026-06-23, STEPS: `50`, REPEAT: `20`, LOW RANGE: `[]`, HIGH RANGE: `[]`
+//! DATE: 2026-06-30, STEPS: `50`, REPEAT: `20`, LOW RANGE: `[]`, HIGH RANGE: `[]`
 //! WORST CASE MAP SIZE: `1000000`
-//! HOSTNAME: `runnervm7b5n9`, CPU: `AMD EPYC 7763 64-Core Processor`
+//! HOSTNAME: `runnervmmklqx`, CPU: `AMD EPYC 9V74 80-Core Processor`
 //! WASM-EXECUTION: `Compiled`, CHAIN: `None`, DB CACHE: `1024`
 
 // Executed Command:
@@ -22,7 +22,7 @@
 // --no-storage-info
 // --no-min-squares
 // --no-median-slopes
-// --output=/tmp/tmp.cSCDxV4Ihz
+// --output=/tmp/tmp.T2PUHoFjkp
 // --template=/home/runner/work/subtensor/subtensor/.maintain/frame-weight-template.hbs
 
 #![cfg_attr(rustfmt, rustfmt_skip)]
@@ -57,10 +57,10 @@ impl<T: frame_system::Config> WeightInfo for SubstrateWeight<T> {
 		// Proof Size summary in bytes:
 		//  Measured:  `518`
 		//  Estimated: `3983`
-		// Minimum execution time: 5_059_000 picoseconds.
-		Weight::from_parts(17_296_401, 3983)
-			// Standard Error: 1_652
-			.saturating_add(Weight::from_parts(6_062_970, 0).saturating_mul(c.into()))
+		// Minimum execution time: 3_765_000 picoseconds.
+		Weight::from_parts(11_793_039, 3983)
+			// Standard Error: 1_715
+			.saturating_add(Weight::from_parts(5_229_430, 0).saturating_mul(c.into()))
 			.saturating_add(T::DbWeight::get().reads(2_u64))
 	}
 	/// Storage: `SafeMode::EnteredUntil` (r:1 w:0)
@@ -71,8 +71,8 @@ impl<T: frame_system::Config> WeightInfo for SubstrateWeight<T> {
 		// Proof Size summary in bytes:
 		//  Measured:  `518`
 		//  Estimated: `3983`
-		// Minimum execution time: 15_679_000 picoseconds.
-		Weight::from_parts(16_070_000, 3983)
+		// Minimum execution time: 13_370_000 picoseconds.
+		Weight::from_parts(14_050_000, 3983)
 			.saturating_add(T::DbWeight::get().reads(2_u64))
 	}
 	/// Storage: `SafeMode::EnteredUntil` (r:1 w:0)
@@ -84,18 +84,18 @@ impl<T: frame_system::Config> WeightInfo for SubstrateWeight<T> {
 		// Proof Size summary in bytes:
 		//  Measured:  `518`
 		//  Estimated: `3983`
-		// Minimum execution time: 5_100_000 picoseconds.
-		Weight::from_parts(21_219_754, 3983)
-			// Standard Error: 2_134
-			.saturating_add(Weight::from_parts(6_279_706, 0).saturating_mul(c.into()))
+		// Minimum execution time: 3_755_000 picoseconds.
+		Weight::from_parts(3_744_581, 3983)
+			// Standard Error: 3_339
+			.saturating_add(Weight::from_parts(5_492_086, 0).saturating_mul(c.into()))
 			.saturating_add(T::DbWeight::get().reads(2_u64))
 	}
 	fn dispatch_as() -> Weight {
 		// Proof Size summary in bytes:
 		//  Measured:  `0`
 		//  Estimated: `0`
-		// Minimum execution time: 7_184_000 picoseconds.
-		Weight::from_parts(7_484_000, 0)
+		// Minimum execution time: 5_478_000 picoseconds.
+		Weight::from_parts(5_698_000, 0)
 	}
 	/// Storage: `SafeMode::EnteredUntil` (r:1 w:0)
 	/// Proof: `SafeMode::EnteredUntil` (`max_values`: Some(1), `max_size`: Some(4), added: 499, mode: `MaxEncodedLen`)
@@ -106,18 +106,18 @@ impl<T: frame_system::Config> WeightInfo for SubstrateWeight<T> {
 		// Proof Size summary in bytes:
 		//  Measured:  `518`
 		//  Estimated: `3983`
-		// Minimum execution time: 5_070_000 picoseconds.
-		Weight::from_parts(21_829_014, 3983)
-			// Standard Error: 2_304
-			.saturating_add(Weight::from_parts(6_047_455, 0).saturating_mul(c.into()))
+		// Minimum execution time: 3_765_000 picoseconds.
+		Weight::from_parts(12_784_545, 3983)
+			// Standard Error: 1_553
+			.saturating_add(Weight::from_parts(5_224_136, 0).saturating_mul(c.into()))
 			.saturating_add(T::DbWeight::get().reads(2_u64))
 	}
 	fn dispatch_as_fallible() -> Weight {
 		// Proof Size summary in bytes:
 		//  Measured:  `0`
 		//  Estimated: `0`
-		// Minimum execution time: 7_094_000 picoseconds.
-		Weight::from_parts(7_434_000, 0)
+		// Minimum execution time: 5_368_000 picoseconds.
+		Weight::from_parts(5_718_000, 0)
 	}
 	/// Storage: `SafeMode::EnteredUntil` (r:1 w:0)
 	/// Proof: `SafeMode::EnteredUntil` (`max_values`: Some(1), `max_size`: Some(4), added: 499, mode: `MaxEncodedLen`)
@@ -127,8 +127,8 @@ impl<T: frame_system::Config> WeightInfo for SubstrateWeight<T> {
 		// Proof Size summary in bytes:
 		//  Measured:  `518`
 		//  Estimated: `3983`
-		// Minimum execution time: 22_653_000 picoseconds.
-		Weight::from_parts(23_143_000, 3983)
+		// Minimum execution time: 18_738_000 picoseconds.
+		Weight::from_parts(19_048_000, 3983)
 			.saturating_add(T::DbWeight::get().reads(2_u64))
 	}
 }
@@ -144,10 +144,10 @@ impl WeightInfo for () {
 		// Proof Size summary in bytes:
 		//  Measured:  `518`
 		//  Estimated: `3983`
-		// Minimum execution time: 5_059_000 picoseconds.
-		Weight::from_parts(17_296_401, 3983)
-			// Standard Error: 1_652
-			.saturating_add(Weight::from_parts(6_062_970, 0).saturating_mul(c.into()))
+		// Minimum execution time: 3_765_000 picoseconds.
+		Weight::from_parts(11_793_039, 3983)
+			// Standard Error: 1_715
+			.saturating_add(Weight::from_parts(5_229_430, 0).saturating_mul(c.into()))
 			.saturating_add(RocksDbWeight::get().reads(2_u64))
 	}
 	/// Storage: `SafeMode::EnteredUntil` (r:1 w:0)
@@ -158,8 +158,8 @@ impl WeightInfo for () {
 		// Proof Size summary in bytes:
 		//  Measured:  `518`
 		//  Estimated: `3983`
-		// Minimum execution time: 15_679_000 picoseconds.
-		Weight::from_parts(16_070_000, 3983)
+		// Minimum execution time: 13_370_000 picoseconds.
+		Weight::from_parts(14_050_000, 3983)
 			.saturating_add(RocksDbWeight::get().reads(2_u64))
 	}
 	/// Storage: `SafeMode::EnteredUntil` (r:1 w:0)
@@ -171,18 +171,18 @@ impl WeightInfo for () {
 		// Proof Size summary in bytes:
 		//  Measured:  `518`
 		//  Estimated: `3983`
-		// Minimum execution time: 5_100_000 picoseconds.
-		Weight::from_parts(21_219_754, 3983)
-			// Standard Error: 2_134
-			.saturating_add(Weight::from_parts(6_279_706, 0).saturating_mul(c.into()))
+		// Minimum execution time: 3_755_000 picoseconds.
+		Weight::from_parts(3_744_581, 3983)
+			// Standard Error: 3_339
+			.saturating_add(Weight::from_parts(5_492_086, 0).saturating_mul(c.into()))
 			.saturating_add(RocksDbWeight::get().reads(2_u64))
 	}
 	fn dispatch_as() -> Weight {
 		// Proof Size summary in bytes:
 		//  Measured:  `0`
 		//  Estimated: `0`
-		// Minimum execution time: 7_184_000 picoseconds.
-		Weight::from_parts(7_484_000, 0)
+		// Minimum execution time: 5_478_000 picoseconds.
+		Weight::from_parts(5_698_000, 0)
 	}
 	/// Storage: `SafeMode::EnteredUntil` (r:1 w:0)
 	/// Proof: `SafeMode::EnteredUntil` (`max_values`: Some(1), `max_size`: Some(4), added: 499, mode: `MaxEncodedLen`)
@@ -193,18 +193,18 @@ impl WeightInfo for () {
 		// Proof Size summary in bytes:
 		//  Measured:  `518`
 		//  Estimated: `3983`
-		// Minimum execution time: 5_070_000 picoseconds.
-		Weight::from_parts(21_829_014, 3983)
-			// Standard Error: 2_304
-			.saturating_add(Weight::from_parts(6_047_455, 0).saturating_mul(c.into()))
+		// Minimum execution time: 3_765_000 picoseconds.
+		Weight::from_parts(12_784_545, 3983)
+			// Standard Error: 1_553
+			.saturating_add(Weight::from_parts(5_224_136, 0).saturating_mul(c.into()))
 			.saturating_add(RocksDbWeight::get().reads(2_u64))
 	}
 	fn dispatch_as_fallible() -> Weight {
 		// Proof Size summary in bytes:
 		//  Measured:  `0`
 		//  Estimated: `0`
-		// Minimum execution time: 7_094_000 picoseconds.
-		Weight::from_parts(7_434_000, 0)
+		// Minimum execution time: 5_368_000 picoseconds.
+		Weight::from_parts(5_718_000, 0)
 	}
 	/// Storage: `SafeMode::EnteredUntil` (r:1 w:0)
 	/// Proof: `SafeMode::EnteredUntil` (`max_values`: Some(1), `max_size`: Some(4), added: 499, mode: `MaxEncodedLen`)
@@ -214,8 +214,8 @@ impl WeightInfo for () {
 		// Proof Size summary in bytes:
 		//  Measured:  `518`
 		//  Estimated: `3983`
-		// Minimum execution time: 22_653_000 picoseconds.
-		Weight::from_parts(23_143_000, 3983)
+		// Minimum execution time: 18_738_000 picoseconds.
+		Weight::from_parts(19_048_000, 3983)
 			.saturating_add(RocksDbWeight::get().reads(2_u64))
 	}
 }
```

### runtime/src/lib.rs
```diff
@@ -234,7 +234,7 @@ pub const VERSION: RuntimeVersion = RuntimeVersion {
     //   `spec_version`, and `authoring_version` are the same between Wasm and native.
     // This value is set to 100 to notify Polkadot-JS App (https://polkadot.js.org/apps) to use
     //   the compatible custom types.
-    spec_version: 423,
+    spec_version: 424,
     impl_version: 1,
     apis: RUNTIME_API_VERSIONS,
     transaction_version: 1,
```
