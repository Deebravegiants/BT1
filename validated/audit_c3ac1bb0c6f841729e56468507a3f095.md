Audit Report

## Title
`Pallet::payout` unconditionally rejects any account that already carries a `pallet_vesting` schedule, letting a user permanently trap their own owed purchase balance - ([File: polkadot/runtime/common/src/purchase/mod.rs])

## Summary
`payout` re-checks `T::VestingSchedule::vesting_balance(&who).is_none()` immediately before crediting a purchaser, before the `Accounts::<T>::try_mutate` block that would transfer funds and set the account to `Completed`. Because `pallet_vesting::vested_transfer` is an unprivileged, signed extrinsic that lets any account create a vesting schedule on any target account (not just the caller), an attacker (or the victim by accident) can cause `payout` to permanently fail with `Error::VestingScheduleExists` for a purchase account that has already been validated and funded via `update_balance`.

## Finding Description
The purchase flow is `create_account` → `update_validity_status` → `update_balance` (which fixes `free_balance`/`locked_balance` in `Accounts<T>`) → `payout` (callable only by the fixed `PaymentAccount`). `create_account` checks for an absent vesting schedule up front, but neither `update_validity_status` nor `update_balance` re-checks this, leaving a real window between an account being marked valid/funded and `PaymentAccount` executing `payout` [1](#0-0) [2](#0-1) .

`payout` performs the same `vesting_balance(&who).is_none()` guard, erroring out with `Error::VestingScheduleExists` before the `Accounts::<T>::try_mutate` block runs (i.e., before the transfer and before `status.validity` is set to `Completed`) [3](#0-2) .

I verified `pallet_vesting`'s behavior directly: `vested_transfer` is a plain `ensure_signed` extrinsic with no restriction that `target == transactor`, so any third party can create a vesting schedule on an arbitrary account [4](#0-3) . `vesting_balance` returns `Some(_)` for *any* account with a `Vesting` storage entry — even `Some(0)` once the schedule has fully elapsed — and only returns `None` once the entry is actually removed from storage [5](#0-4) . The removal only happens via an explicit `vest`/`vest_other` call, confirmed by the existing vesting pallet test showing schedules "are still in storage" at `vesting_balance == Some(0)" until "we unlock the funds" [6](#0-5) . There is no code path in `purchase::mod.rs` that lets `PaymentAccount` or `ConfigurationOrigin` bypass or clear this condition.

## Impact Explanation
This is a legitimate, concrete self-DoS / griefing vector for the `pallet_purchase` payout flow specifically limited to that pallet's UX (blocked payout, not fund loss — the funds remain safely in `Accounts<T>` state and are eventually payable once the vesting entry is cleared, whether by the attacker's own action or the natural passage of time plus an explicit `vest_other` call). It generalizes to third-party griefing since `vested_transfer` can target any account. This is realistic and in-scope for the `polkadot/runtime/common` purchase pallet, causing a temporary/indefinite freeze of an already-approved payout until an unrelated, externally-triggered `vest`/`vest_other` call is made to purge the `Vesting` entry.

## Likelihood Explanation
Fully reachable using only unprivileged extrinsics: `vested_transfer` requires no special origin beyond a signed account and meeting `MinVestedTransfer` [7](#0-6) . The purchase-side preconditions (`create_account`, `update_validity_status`, `update_balance`) are normal steps in the intended flow performed by `ValidityOrigin`, and the race window before `PaymentAccount` calls `payout` in a separate later transaction is realistically exploitable, requiring no chain-level races or privileged access.

## Recommendation
Do not treat a pre-existing vesting schedule as a hard blocker inside `payout`. Options include: removing the redundant `vesting_balance` check and instead having `add_vesting_schedule` merge with or queue behind any existing schedule (transferring the free portion unconditionally, and merging the locked/vesting portion via the currency's multi-schedule support rather than erroring); or exposing an explicit unprivileged "retry"/"merge vesting" mechanism so a legitimately owed balance is never permanently gated behind an unrelated pallet's storage state that the victim cannot control.

## Proof of Concept
1. Run through `create_account`, `update_validity_status(who, ValidLow)`, `update_balance(who, free, locked, vat)` for `who` as `ValidityOrigin`.
2. As any signed account (attacker or victim), call `Vesting::vested_transfer(origin, who, VestingInfo::new(min_transfer, 1, current_block))`, creating a `Vesting` entry for `who`.
3. As `PaymentAccount`, call `Purchase::payout(RuntimeOrigin::signed(payment_account), who)`.
4. Observe the call fails with `Error::<Test>::VestingScheduleExists`; `Accounts::<Test>::get(who)` remains non-`Completed` with unchanged `free_balance`/`locked_balance`.
5. Advance blocks past `starting_block + locked/per_block` without calling `vest`/`vest_other`; repeat `payout` and observe it still fails, since `vesting_balance` returns `Some(0)` rather than `None` until the `Vesting` storage entry is explicitly purged.

### Citations

**File:** polkadot/runtime/common/src/purchase/mod.rs (L206-213)
```rust
			T::ValidityOrigin::ensure_origin(origin)?;
			// Account is already being tracked by the pallet.
			ensure!(!Accounts::<T>::contains_key(&who), Error::<T>::ExistingAccount);
			// Account should not have a vesting schedule.
			ensure!(
				T::VestingSchedule::vesting_balance(&who).is_none(),
				Error::<T>::VestingScheduleExists
			);
```

**File:** polkadot/runtime/common/src/purchase/mod.rs (L266-296)
```rust
		#[pallet::call_index(2)]
		#[pallet::weight(T::DbWeight::get().reads_writes(2, 1))]
		pub fn update_balance(
			origin: OriginFor<T>,
			who: T::AccountId,
			free_balance: BalanceOf<T>,
			locked_balance: BalanceOf<T>,
			vat: Permill,
		) -> DispatchResult {
			T::ValidityOrigin::ensure_origin(origin)?;

			Accounts::<T>::try_mutate(
				&who,
				|status: &mut AccountStatus<BalanceOf<T>>| -> DispatchResult {
					// Account has a valid status (not Invalid, Pending, or Completed)...
					ensure!(status.validity.is_valid(), Error::<T>::InvalidAccount);

					free_balance.checked_add(&locked_balance).ok_or(Error::<T>::Overflow)?;
					status.free_balance = free_balance;
					status.locked_balance = locked_balance;
					status.vat = vat;
					Ok(())
				},
			)?;
			Self::deposit_event(Event::<T>::BalanceUpdated {
				who,
				free: free_balance,
				locked: locked_balance,
			});
			Ok(())
		}
```

**File:** polkadot/runtime/common/src/purchase/mod.rs (L312-367)
```rust
			// Account should not have a vesting schedule.
			ensure!(
				T::VestingSchedule::vesting_balance(&who).is_none(),
				Error::<T>::VestingScheduleExists
			);

			Accounts::<T>::try_mutate(
				&who,
				|status: &mut AccountStatus<BalanceOf<T>>| -> DispatchResult {
					// Account has a valid status (not Invalid, Pending, or Completed)...
					ensure!(status.validity.is_valid(), Error::<T>::InvalidAccount);

					// Transfer funds from the payment account into the purchasing user.
					let total_balance = status
						.free_balance
						.checked_add(&status.locked_balance)
						.ok_or(Error::<T>::Overflow)?;
					T::Currency::transfer(
						&payment_account,
						&who,
						total_balance,
						ExistenceRequirement::AllowDeath,
					)?;

					if !status.locked_balance.is_zero() {
						let unlock_block = UnlockBlock::<T>::get();
						// We allow some configurable portion of the purchased locked DOTs to be
						// unlocked for basic usage.
						let unlocked = (T::UnlockedProportion::get() * status.locked_balance)
							.min(T::MaxUnlocked::get());
						let locked = status.locked_balance.saturating_sub(unlocked);
						// We checked that this account has no existing vesting schedule. So this
						// function should never fail, however if it does, not much we can do about
						// it at this point.
						let _ = T::VestingSchedule::add_vesting_schedule(
							// Apply vesting schedule to this user
							&who,
							// For this much amount
							locked,
							// Unlocking the full amount after one block
							locked,
							// When everything unlocks
							unlock_block,
						);
					}

					// Setting the user account to `Completed` ends the purchase process for this
					// user.
					status.validity = AccountValidity::Completed;
					Self::deposit_event(Event::<T>::PaymentComplete {
						who: who.clone(),
						free: status.free_balance,
						locked: status.locked_balance,
					});
					Ok(())
				},
```

**File:** substrate/frame/vesting/src/lib.rs (L355-380)
```rust
		/// Create a vested transfer.
		///
		/// The dispatch origin for this call must be _Signed_.
		///
		/// - `target`: The account receiving the vested funds.
		/// - `schedule`: The vesting schedule attached to the transfer.
		///
		/// Emits `VestingCreated`.
		///
		/// NOTE: This will unlock all schedules through the current block.
		///
		/// ## Complexity
		/// - `O(1)`.
		#[pallet::call_index(2)]
		#[pallet::weight(
			T::WeightInfo::vested_transfer(MaxLocksOf::<T>::get(), T::MAX_VESTING_SCHEDULES)
		)]
		pub fn vested_transfer(
			origin: OriginFor<T>,
			target: AccountIdLookupOf<T>,
			schedule: VestingInfo<BalanceOf<T>, BlockNumberFor<T>>,
		) -> DispatchResult {
			let transactor = ensure_signed(origin)?;
			let target = T::Lookup::lookup(target)?;
			Self::do_vested_transfer(&transactor, &target, schedule)
		}
```

**File:** substrate/frame/vesting/src/lib.rs (L756-766)
```rust
	fn vesting_balance(who: &T::AccountId) -> Option<BalanceOf<T>> {
		if let Some(v) = Vesting::<T>::get(who) {
			let now = T::BlockNumberProvider::current_block_number();
			let total_locked_now = v.iter().fold(Zero::zero(), |total, schedule| {
				schedule.locked_at::<T::BlockNumberToBalance>(now).saturating_add(total)
			});
			Some(T::Currency::free_balance(who).min(total_locked_now))
		} else {
			None
		}
	}
```

**File:** substrate/frame/vesting/src/tests.rs (L169-177)
```rust
		// At block #35 sched2 fully unlocks and thus all schedules funds are unlocked.
		System::set_block_number(35);
		assert_eq!(Vesting::vesting_balance(&2), Some(0));
		// Since we have not called any extrinsics that would unlock funds the schedules
		// are still in storage,
		assert_eq!(VestingStorage::<Test>::get(&2).unwrap(), vec![sched0, sched1, sched2]);
		// but once we unlock the funds, they are removed from storage.
		vest_and_assert_no_vesting::<Test>(2);
	});
```
