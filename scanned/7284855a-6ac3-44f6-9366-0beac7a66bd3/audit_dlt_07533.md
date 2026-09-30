# [?] Patch staking underflow bug (#502)

## Summary
Severity: Unknown
Chain: Moonbeam
Component: moonbeam-foundation/moonbeam
Published: 2021-06-11
Source: https://github.com/moonbeam-foundation/moonbeam/commit/56eb3eb8be017815333070b7ceb63dbfd0c14aff
Type: security-commit

## Details
Patch staking underflow bug (#502)

* fix

* bump impl versions and staking lib version

* bump version in Cargo lock

* sketch migration idea (#503)

* on runtime upgrade

* line length fmt

* Update pallets/parachain-staking/src/lib.rs

Co-authored-by: Joshy Orndorff <JoshOrndorff@users.noreply.github.com>

* fix version bumps

* Better (but still not good) weight

Co-authored-by: Joshy Orndorff <JoshOrndorff@users.noreply.github.com>

## Patch
### Cargo.lock
```diff
@@ -6636,7 +6636,7 @@ dependencies = [
 
 [[package]]
 name = "parachain-staking"
-version = "1.0.1"
+version = "1.0.2"
 dependencies = [
  "frame-benchmarking",
  "frame-support",
```

### pallets/parachain-staking/Cargo.toml
```diff
@@ -1,6 +1,6 @@
 [package]
 name = "parachain-staking"
-version = "1.0.1"
+version = "1.0.2"
 authors = ["PureStake"]
 edition = "2018"
 description = "parachain staking pallet for collator selection and reward distribution"
```

### pallets/parachain-staking/src/lib.rs
```diff
@@ -73,7 +73,7 @@ pub mod pallet {
 	use frame_system::pallet_prelude::*;
 	use parity_scale_codec::{Decode, Encode};
 	use sp_runtime::{
-		traits::{AtLeast32BitUnsigned, Zero},
+		traits::{AtLeast32BitUnsigned, Saturating, Zero},
 		Perbill, Percent, RuntimeDebug,
 	};
 	use sp_std::{cmp::Ordering, prelude::*};
@@ -507,6 +507,27 @@ pub mod pallet {
 
 	#[pallet::hooks]
 	impl<T: Config> Hooks<BlockNumberFor<T>> for Pallet<T> {
+		// This upgrade fixes a bug that may have led to an incorrect `Total` (total staked)
+		fn on_runtime_upgrade() -> Weight {
+			let old_total = Total::<T>::get();
+			let mut new_total: BalanceOf<T> = 0u32.into();
+
+			for collator_state in CollatorState::<T>::iter_values() {
+				new_total += collator_state.total;
+			}
+
+			Total::<T>::put(new_total);
+
+			log::trace!(
+				target: "staking",
+				"Finished migrating storage.\nOld Total : {:?}\nNew Total : {:?}",
+				old_total,
+				new_total,
+			);
+
+			300_000_000_000 // Three fifths of the max block weight
+		}
+
 		fn on_finalize(n: T::BlockNumber) {
 			let mut round = <Round<T>>::get();
 			if round.should_update(n) {
@@ -890,10 +911,10 @@ pub mod pallet {
 			);
 			T::Currency::reserve(&acc, bond)?;
 			let candidate = Collator::new(acc.clone(), bond);
-			let new_total = <Total<T>>::get() + bond;
-			<Total<T>>::put(new_total);
 			<CollatorState<T>>::insert(&acc, candidate);
 			<CandidatePool<T>>::put(candidates);
+			let new_total = <Total<T>>::get().saturating_add(bond);
+			<Total<T>>::put(new_total);
 			Self::deposit_event(Event::JoinedCollatorCandidates(acc, bond, new_total));
 			Ok(().into())
 		}
@@ -985,6 +1006,8 @@ pub mod pallet {
 				Self::update_active(collator.clone(), state.total);
 			}
 			<CollatorState<T>>::insert(&collator, state);
+			let new_total = <Total<T>>::get().saturating_add(more);
+			<Total<T>>::put(new_total);
 			Self::deposit_event(Event::CollatorBondedMore(collator, before, after));
 			Ok(().into())
 		}
@@ -1010,6 +1033,8 @@ pub mod pallet {
 				Self::update_active(collator.clone(), state.total);
 			}
 			<CollatorState<T>>::insert(&collator, state);
+			let new_total_staked = <Total<T>>::get().saturating_sub(less);
+			<Total<T>>::put(new_total_staked);
 			Self::deposit_event(Event::CollatorBondedLess(collator, before, after));
 			Ok(().into())
 		}
@@ -1119,6 +1144,8 @@ pub mod pallet {
 			}
 			<CollatorState<T>>::insert(&candidate, collator);
 			<NominatorState<T>>::insert(&nominator, nominations);
+			let new_total_staked = <Total<T>>::get().saturating_add(more);
+			<Total<T>>::put(new_total_staked);
 			Self::deposit_event(Event::NominationIncreased(
 				nominator, candidate, before, after,
 			));
@@ -1157,6 +1184,8 @@ pub mod pallet {
 			}
 			<CollatorState<T>>::insert(&candidate, collator);
 			<NominatorState<T>>::insert(&nominator, nominations);
+			let new_total_staked = <Total<T>>::get().saturating_sub(less);
+			<Total<T>>::put(new_total_staked);
 			Self::deposit_event(Event::NominationDecreased(
 				nominator, candidate, before, after,
 			));
@@ -1344,13 +1373,13 @@ pub mod pallet {
 							}
 							// return stake to collator
 							T::Currency::unreserve(&state.id, state.bond);
-							let new_total = <Total<T>>::get() - state.total;
-							<Total<T>>::put(new_total);
 							<CollatorState<T>>::remove(&x.owner);
+							let new_total_staked = <Total<T>>::get().saturating_sub(state.total);
+							<Total<T>>::put(new_total_staked);
 							Self::deposit_event(Event::CollatorLeft(
 								x.owner,
 								state.total,
-								new_total,
+								new_total_staked,
 							));
 						}
 						None
```

### pallets/parachain-staking/src/tests.rs
```diff
@@ -712,7 +712,10 @@ fn collators_bond() {
 				Stake::candidate_bond_more(Origin::signed(6), 50),
 				Error::<Test>::CandidateDNE
 			);
+			let mut total = Stake::total();
 			assert_ok!(Stake::candidate_bond_more(Origin::signed(1), 50));
+			total += 50;
+			assert_eq!(Stake::total(), total);
 			assert_noop!(
 				Stake::candidate_bond_more(Origin::signed(1), 40),
 				DispatchError::Module {
@@ -728,13 +731,21 @@ fn collators_bond() {
 				Error::<Test>::CannotActivateIfLeaving
 			);
 			roll_to(30);
+			total -= 100;
+			assert_eq!(Stake::total(), total);
 			assert_noop!(
 				Stake::candidate_bond_more(Origin::signed(1), 40),
 				Error::<Test>::CandidateDNE
 			);
 			assert_ok!(Stake::candidate_bond_more(Origin::signed(2), 80));
+			total += 80;
+			assert_eq!(Stake::total(), total);
 			assert_ok!(Stake::candidate_bond_less(Origin::signed(2), 90));
+			total -= 90;
+			assert_eq!(Stake::total(), total);
 			assert_ok!(Stake::candidate_bond_less(Origin::signed(3), 10));
+			total -= 10;
+			assert_eq!(Stake::total(), total);
 			assert_noop!(
 				Stake::candidate_bond_less(Origin::signed(2), 11),
 				Error::<Test>::CannotBondLessGEQTotalBond
@@ -752,6 +763,8 @@ fn collators_bond() {
 				Error::<Test>::ValBondBelowMin
 			);
 			assert_ok!(Stake::candidate_bond_less(Origin::signed(4), 10));
+			total -= 10;
+			assert_eq!(Stake::total(), total);
 		});
 }
 
@@ -781,6 +794,7 @@ fn nominators_bond() {
 		.build()
 		.execute_with(|| {
 			roll_to(4);
+			let mut total = Stake::total();
 			assert_noop!(
 				Stake::nominator_bond_more(Origin::signed(1), 2, 50),
 				Error::<Test>::NominatorDNE
@@ -806,6 +820,8 @@ fn nominators_bond() {
 				Error::<Test>::NomBondBelowMin
 			);
 			assert_ok!(Stake::nominator_bond_more(Origin::signed(6), 1, 10));
+			total += 10;
+			assert_eq!(Stake::total(), total);
 			assert_noop!(
 				Stake::nominator_bond_less(Origin::signed(6), 2, 5),
 				Error::<Test>::NominationDNE
@@ -822,7 +838,10 @@ fn nominators_bond() {
 			roll_to(9);
 			assert_eq!(Balances::reserved_balance(&6), 20);
 			assert_ok!(Stake::leave_candidates(Origin::signed(1)));
+			assert_eq!(Stake::total(), total);
 			roll_to(31);
+			total -= 60;
+			assert_eq!(Stake::total(), total);
 			assert!(!Stake::is_nominator(&6));
 			assert_eq!(Balances::reserved_balance(&6), 0);
 			assert_eq!(Balances::free_balance(&6), 100);
```
