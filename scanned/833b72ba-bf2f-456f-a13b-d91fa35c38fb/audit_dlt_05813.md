# [?] Fix reentrancy of FrozenBalance::died hook (#10473)

## Summary
Severity: Unknown
Chain: Polkadot
Component: paritytech/substrate
Published: 2022-02-11
Source: https://github.com/paritytech/substrate/commit/a9020646e784170050a4e6324dd067ab0e5af448
Type: security-commit

## Details
Fix reentrancy of FrozenBalance::died hook (#10473)

* assets: execute `died` hook outside of mutate

Signed-off-by: Oliver Tale-Yazdi <oliver@tasty.limo>

* assets: extend tests for `died` hook

Signed-off-by: Oliver Tale-Yazdi <oliver@tasty.limo>

* assets: update doc of FrozenBalance::died

Signed-off-by: Oliver Tale-Yazdi <oliver@tasty.limo>

* assets: review fixes

- fix cases where `died` should not have been called
- use `Option<DeadConsequence>` instead of `DeadConsequence`

Signed-off-by: Oliver Tale-Yazdi <oliver@tasty.limo>

* assets: update comment in mock.rs

Signed-off-by: Oliver Tale-Yazdi <oliver@tasty.limo>

* assets: return `Remove` in dead_account

The return value is ignored in the only case that it is produced
by a call, but having it this way makes it more understandable.

Signed-off-by: Oliver Tale-Yazdi <oliver@tasty.limo>

## Patch
### frame/assets/src/functions.rs
```diff
@@ -84,13 +84,11 @@ impl<T: Config<I>, I: 'static> Pallet<T, I> {
 	}
 
 	pub(super) fn dead_account(
-		what: T::AssetId,
 		who: &T::AccountId,
 		d: &mut AssetDetails<T::Balance, T::AccountId, DepositBalanceOf<T, I>>,
 		reason: &ExistenceReason<DepositBalanceOf<T, I>>,
 		force: bool,
 	) -> DeadConsequence {
-		let mut result = Remove;
 		match *reason {
 			ExistenceReason::Consumer => frame_system::Pallet::<T>::dec_consumers(who),
 			ExistenceReason::Sufficient => {
@@ -99,11 +97,10 @@ impl<T: Config<I>, I: 'static> Pallet<T, I> {
 			},
 			ExistenceReason::DepositRefunded => {},
 			ExistenceReason::DepositHeld(_) if !force => return Keep,
-			ExistenceReason::DepositHeld(_) => result = Keep,
+			ExistenceReason::DepositHeld(_) => {},
 		}
 		d.accounts = d.accounts.saturating_sub(1);
-		T::Freezer::died(what, who);
-		result
+		Remove
 	}
 
 	pub(super) fn can_increase(
@@ -323,12 +320,14 @@ impl<T: Config<I>, I: 'static> Pallet<T, I> {
 
 		T::Currency::unreserve(&who, deposit);
 
-		if let Remove = Self::dead_account(id, &who, &mut details, &account.reason, false) {
+		if let Remove = Self::dead_account(&who, &mut details, &account.reason, false) {
 			Account::<T, I>::remove(id, &who);
 		} else {
 			debug_assert!(false, "refund did not result in dead account?!");
 		}
 		Asset::<T, I>::insert(&id, details);
+		// Executing a hook here is safe, since it is not in a `mutate`.
+		T::Freezer::died(id, &who);
 		Ok(())
 	}
 
@@ -461,6 +460,7 @@ impl<T: Config<I>, I: 'static> Pallet<T, I> {
 		}
 
 		let actual = Self::prep_debit(id, target, amount, f)?;
+		let mut target_died: Option<DeadConsequence> = None;
 
 		Asset::<T, I>::try_mutate(id, |maybe_details| -> DispatchResult {
 			let mut details = maybe_details.as_mut().ok_or(Error::<T, I>::Unknown)?;
@@ -475,9 +475,9 @@ impl<T: Config<I>, I: 'static> Pallet<T, I> {
 				account.balance = account.balance.saturating_sub(actual);
 				if account.balance < details.min_balance {
 					debug_assert!(account.balance.is_zero(), "checked in prep; qed");
-					if let Remove =
-						Self::dead_account(id, target, &mut details, &account.reason, false)
-					{
+					target_died =
+						Some(Self::dead_account(target, &mut details, &account.reason, false));
+					if let Some(Remove) = target_died {
 						return Ok(())
 					}
 				};
@@ -488,6 +488,10 @@ impl<T: Config<I>, I: 'static> Pallet<T, I> {
 			Ok(())
 		})?;
 
+		// Execute hook outside of `mutate`.
+		if let Some(Remove) = target_died {
+			T::Freezer::died(id, target);
+		}
 		Ok(actual)
 	}
 
@@ -507,6 +511,24 @@ impl<T: Config<I>, I: 'static> Pallet<T, I> {
 		maybe_need_admin: Option<T::AccountId>,
 		f: TransferFlags,
 	) -> Result<T::Balance, DispatchError> {
+		let (balance, died) =
+			Self::transfer_and_die(id, source, dest, amount, maybe_need_admin, f)?;
+		if let Some(Remove) = died {
+			T::Freezer::died(id, source);
+		}
+		Ok(balance)
+	}
+
+	/// Same as `do_transfer` but it does not execute the `FrozenBalance::died` hook and
+	/// instead returns whether and how the `source` account died in this operation.
+	fn transfer_and_die(
+		id: T::AssetId,
+		source: &T::AccountId,
+		dest: &T::AccountId,
+		amount: T::Balance,
+		maybe_need_admin: Option<T::AccountId>,
+		f: TransferFlags,
+	) -> Result<(T::Balance, Option<DeadConsequence>), DispatchError> {
 		// Early exist if no-op.
 		if amount.is_zero() {
 			Self::deposit_event(Event::Transferred {
@@ -515,7 +537,7 @@ impl<T: Config<I>, I: 'static> Pallet<T, I> {
 				to: dest.clone(),
 				amount,
 			});
-			return Ok(amount)
+			return Ok((amount, None))
 		}
 
 		// Figure out the debit and credit, together with side-effects.
@@ -524,6 +546,7 @@ impl<T: Config<I>, I: 'static> Pallet<T, I> {
 
 		let mut source_account =
 			Account::<T, I>::get(id, &source).ok_or(Error::<T, I>::NoAccount)?;
+		let mut source_died: Option<DeadConsequence> = None;
 
 		Asset::<T, I>::try_mutate(id, |maybe_details| -> DispatchResult {
 			let details = maybe_details.as_mut().ok_or(Error::<T, I>::Unknown)?;
@@ -576,9 +599,9 @@ impl<T: Config<I>, I: 'static> Pallet<T, I> {
 			// Remove source account if it's now dead.
 			if source_account.balance < details.min_balance {
 				debug_assert!(source_account.balance.is_zero(), "checked in prep; qed");
-				if let Remove =
-					Self::dead_account(id, &source, details, &source_account.reason, false)
-				{
+				source_died =
+					Some(Self::dead_account(&source, details, &source_account.reason, false));
+				if let Some(Remove) = source_died {
 					Account::<T, I>::remove(id, &source);
 					return Ok(())
 				}
@@ -593,7 +616,7 @@ impl<T: Config<I>, I: 'static> Pallet<T, I> {
 			to: dest.clone(),
 			amount: credit,
 		});
-		Ok(credit)
+		Ok((credit, source_died))
 	}
 
 	/// Create a new asset without taking a deposit.
@@ -646,41 +669,53 @@ impl<T: Config<I>, I: 'static> Pallet<T, I> {
 		witness: DestroyWitness,
 		maybe_check_owner: Option<T::AccountId>,
 	) -> Result<DestroyWitness, DispatchError> {
-		Asset::<T, I>::try_mutate_exists(id, |maybe_details| {
-			let mut details = maybe_details.take().ok_or(Error::<T, I>::Unknown)?;
-			if let Some(check_owner) = maybe_check_owner {
-				ensure!(details.owner == check_owner, Error::<T, I>::NoPermission);
-			}
-			ensure!(details.accounts <= witness.accounts, Error::<T, I>::BadWitness);
-			ensure!(details.sufficients <= witness.sufficients, Error::<T, I>::BadWitness);
-			ensure!(details.approvals <= witness.approvals, Error::<T, I>::BadWitness);
-
-			for (who, v) in Account::<T, I>::drain_prefix(id) {
-				// We have to force this as it's destroying the entire asset class.
-				// This could mean that some accounts now have irreversibly reserved
-				// funds.
-				let _ = Self::dead_account(id, &who, &mut details, &v.reason, true);
-			}
-			debug_assert_eq!(details.accounts, 0);
-			debug_assert_eq!(details.sufficients, 0);
+		let mut dead_accounts: Vec<T::AccountId> = vec![];
 
-			let metadata = Metadata::<T, I>::take(&id);
-			T::Currency::unreserve(
-				&details.owner,
-				details.deposit.saturating_add(metadata.deposit),
-			);
+		let result_witness: DestroyWitness = Asset::<T, I>::try_mutate_exists(
+			id,
+			|maybe_details| -> Result<DestroyWitness, DispatchError> {
+				let mut details = maybe_details.take().ok_or(Error::<T, I>::Unknown)?;
+				if let Some(check_owner) = maybe_check_owner {
+					ensure!(details.owner == check_owner, Error::<T, I>::NoPermission);
+				}
+				ensure!(details.accounts <= witness.accounts, Error::<T, I>::BadWitness);
+				ensure!(details.sufficients <= witness.sufficients, Error::<T, I>::BadWitness);
+				ensure!(details.approvals <= witness.approvals, Error::<T, I>::BadWitness);
+
+				for (who, v) in Account::<T, I>::drain_prefix(id) {
+					// We have to force this as it's destroying the entire asset class.
+					// This could mean that some accounts now have irreversibly reserved
+					// funds.
+					let _ = Self::dead_account(&who, &mut details, &v.reason, true);
+					dead_accounts.push(who);
+				}
+				debug_assert_eq!(details.accounts, 0);
+				debug_assert_eq!(details.sufficients, 0);
 
-			for ((owner, _), approval) in Approvals::<T, I>::drain_prefix((&id,)) {
-				T::Currency::unreserve(&owner, approval.deposit);
-			}
-			Self::deposit_event(Event::Destroyed { asset_id: id });
+				let metadata = Metadata::<T, I>::take(&id);
+				T::Currency::unreserve(
+					&details.owner,
+					details.deposit.saturating_add(metadata.deposit),
+				);
 
-			Ok(DestroyWitness {
-				accounts: details.accounts,
-				sufficients: details.sufficients,
-				approvals: details.approvals,
-			})
-		})
+				for ((owner, _), approval) in Approvals::<T, I>::drain_prefix((&id,)) {
+					T::Currency::unreserve(&owner, approval.deposit);
+				}
+				Self::deposit_event(Event::Destroyed { asset_id: id });
+
+				Ok(DestroyWitness {
+					accounts: details.accounts,
+					sufficients: details.sufficients,
+					approvals: details.approvals,
+				})
+			},
+		)?;
+
+		// Execute hooks outside of `mutate`.
+		for who in dead_accounts {
+			T::Freezer::died(id, &who);
+		}
+		Ok(result_witness)
 	}
 
 	/// Creates an approval from `owner` to spend `amount` of asset `id` tokens by 'delegate'
@@ -742,6 +777,8 @@ impl<T: Config<I>, I: 'static> Pallet<T, I> {
 		destination: &T::AccountId,
 		amount: T::Balance,
 	) -> DispatchResult {
+		let mut owner_died: Option<DeadConsequence> = None;
+
 		Approvals::<T, I>::try_mutate_exists(
 			(id, &owner, delegate),
 			|maybe_approved| -> DispatchResult {
@@ -750,7 +787,7 @@ impl<T: Config<I>, I: 'static> Pallet<T, I> {
 					approved.amount.checked_sub(&amount).ok_or(Error::<T, I>::Unapproved)?;
 
 				let f = TransferFlags { keep_alive: false, best_effort: false, burn_dust: false };
-				Self::do_transfer(id, &owner, &destination, amount, None, f)?;
+				owner_died = Self::transfer_and_die(id, &owner, &destination, amount, None, f)?.1;
 
 				if remaining.is_zero() {
 					T::Currency::unreserve(&owner, approved.deposit);
@@ -766,6 +803,11 @@ impl<T: Config<I>, I: 'static> Pallet<T, I> {
 				Ok(())
 			},
 		)?;
+
+		// Execute hook outside of `mutate`.
+		if let Some(Remove) = owner_died {
+			T::Freezer::died(id, owner);
+		}
 		Ok(())
 	}
 
```

### frame/assets/src/mock.rs
```diff
@@ -120,19 +120,27 @@ impl FrozenBalance<u32, u64, u64> for TestFreezer {
 
 	fn died(asset: u32, who: &u64) {
 		HOOKS.with(|h| h.borrow_mut().push(Hook::Died(asset, who.clone())));
+		// Sanity check: dead accounts have no balance.
+		assert!(Assets::balance(asset, *who).is_zero());
 	}
 }
 
 pub(crate) fn set_frozen_balance(asset: u32, who: u64, amount: u64) {
 	FROZEN.with(|f| f.borrow_mut().insert((asset, who), amount));
 }
+
 pub(crate) fn clear_frozen_balance(asset: u32, who: u64) {
 	FROZEN.with(|f| f.borrow_mut().remove(&(asset, who)));
 }
+
 pub(crate) fn hooks() -> Vec<Hook> {
 	HOOKS.with(|h| h.borrow().clone())
 }
 
+pub(crate) fn take_hooks() -> Vec<Hook> {
+	HOOKS.with(|h| h.take())
+}
+
 pub(crate) fn new_test_ext() -> sp_io::TestExternalities {
 	let mut storage = frame_system::GenesisConfig::default().build_storage::<Test>().unwrap();
 
@@ -154,6 +162,8 @@ pub(crate) fn new_test_ext() -> sp_io::TestExternalities {
 	config.assimilate_storage(&mut storage).unwrap();
 
 	let mut ext: sp_io::TestExternalities = storage.into();
+	// Clear thread local vars for https://github.com/paritytech/substrate/issues/10479.
+	ext.execute_with(|| take_hooks());
 	ext.execute_with(|| System::set_block_number(1));
 	ext
 }
```

### frame/assets/src/tests.rs
```diff
@@ -125,6 +125,21 @@ fn refunding_asset_deposit_without_burn_should_work() {
 	});
 }
 
+/// Refunding reaps an account and calls the `FrozenBalance::died` hook.
+#[test]
+fn refunding_calls_died_hook() {
+	new_test_ext().execute_with(|| {
+		assert_ok!(Assets::force_create(Origin::root(), 0, 1, false, 1));
+		Balances::make_free_balance_be(&1, 100);
+		assert_ok!(Assets::touch(Origin::signed(1), 0));
+		assert_ok!(Assets::mint(Origin::signed(1), 0, 1, 100));
+		assert_ok!(Assets::refund(Origin::signed(1), 0, true));
+
+		assert_eq!(Asset::<Test>::get(0).unwrap().accounts, 0);
+		assert_eq!(hooks(), vec![Hook::Died(0, 1)]);
+	});
+}
+
 #[test]
 fn approval_lifecycle_works() {
 	new_test_ext().execute_with(|| {
@@ -389,19 +404,32 @@ fn min_balance_should_work() {
 		);
 
 		// When deducting from an account to below minimum, it should be reaped.
+		// Death by `transfer`.
 		assert_ok!(Assets::transfer(Origin::signed(1), 0, 2, 91));
 		assert!(Assets::maybe_balance(0, 1).is_none());
 		assert_eq!(Assets::balance(0, 2), 100);
 		assert_eq!(Asset::<Test>::get(0).unwrap().accounts, 1);
+		assert_eq!(take_hooks(), vec![Hook::Died(0, 1)]);
 
+		// Death by `force_transfer`.
 		assert_ok!(Assets::force_transfer(Origin::signed(1), 0, 2, 1, 91));
 		assert!(Assets::maybe_balance(0, 2).is_none());
 		assert_eq!(Assets::balance(0, 1), 100);
 		assert_eq!(Asset::<Test>::get(0).unwrap().accounts, 1);
+		assert_eq!(take_hooks(), vec![Hook::Died(0, 2)]);
 
+		// Death by `burn`.
 		assert_ok!(Assets::burn(Origin::signed(1), 0, 1, 91));
 		assert!(Assets::maybe_balance(0, 1).is_none());
 		assert_eq!(Asset::<Test>::get(0).unwrap().accounts, 0);
+		assert_eq!(take_hooks(), vec![Hook::Died(0, 1)]);
+
+		// Death by `transfer_approved`.
+		assert_ok!(Assets::mint(Origin::signed(1), 0, 1, 100));
+		Balances::make_free_balance_be(&1, 1);
+		assert_ok!(Assets::approve_transfer(Origin::signed(1), 0, 2, 100));
+		assert_ok!(Assets::transfer_approved(Origin::signed(2), 0, 1, 3, 91));
+		assert_eq!(take_hooks(), vec![Hook::Died(0, 1)]);
 	});
 }
 
@@ -448,6 +476,7 @@ fn transferring_enough_to_kill_source_when_keep_alive_should_fail() {
 		assert_ok!(Assets::transfer_keep_alive(Origin::signed(1), 0, 2, 90));
 		assert_eq!(Assets::balance(0, 1), 10);
 		assert_eq!(Assets::balance(0, 2), 90);
+		assert!(hooks().is_empty());
 	});
 }
 
@@ -684,6 +713,24 @@ fn set_metadata_should_work() {
 	});
 }
 
+/// Destroying an asset calls the `FrozenBalance::died` hooks of all accounts.
+#[test]
+fn destroy_calls_died_hooks() {
+	new_test_ext().execute_with(|| {
+		assert_ok!(Assets::force_create(Origin::root(), 0, 1, true, 50));
+		// Create account 1 and 2.
+		assert_ok!(Assets::mint(Origin::signed(1), 0, 1, 100));
+		assert_ok!(Assets::mint(Origin::signed(1), 0, 2, 100));
+		// Destroy the asset.
+		let w = Asset::<Test>::get(0).unwrap().destroy_witness();
+		assert_ok!(Assets::destroy(Origin::signed(1), 0, w));
+
+		// Asset is gone and accounts 1 and 2 died.
+		assert!(Asset::<Test>::get(0).is_none());
+		assert_eq!(hooks(), vec![Hook::Died(0, 1), Hook::Died(0, 2)]);
+	})
+}
+
 #[test]
 fn freezer_should_work() {
 	new_test_ext().execute_with(|| {
```

### frame/assets/src/types.rs
```diff
@@ -172,13 +172,9 @@ pub trait FrozenBalance<AssetId, AccountId, Balance> {
 	/// If `None` is returned, then nothing special is enforced.
 	fn frozen_balance(asset: AssetId, who: &AccountId) -> Option<Balance>;
 
-	/// Called when an account has been removed.
+	/// Called after an account has been removed.
 	///
-	/// # Warning
-	///
-	/// This function must never access storage of pallet asset. This function is called while some
-	/// change are pending. Calling into the pallet asset in this function can result in unexpected
-	/// state.
+	/// NOTE: It is possible that the asset does no longer exist when this hook is called.
 	fn died(asset: AssetId, who: &AccountId);
 }
 
```
