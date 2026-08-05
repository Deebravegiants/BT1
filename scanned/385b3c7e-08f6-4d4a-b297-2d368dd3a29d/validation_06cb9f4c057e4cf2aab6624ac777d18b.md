### Title
`Pallet::payout` unconditionally rejects any account that already carries a `pallet_vesting` schedule, letting a user permanently trap their own owed purchase balance - ([File: polkadot/runtime/common/src/purchase/mod.rs])

### Summary
`payout` re-checks `T::VestingSchedule::vesting_balance(&who).is_none()` right before crediting a purchaser [1](#0-0) . Because `pallet_vesting::vested_transfer` (or any other vesting-creating call) is a normal, unprivileged extrinsic that anyone can invoke against an arbitrary target account, a user (or even a third party) can create a vesting schedule on the purchase-tracked account after `update_balance` has fixed the entitlement but before `PaymentAccount` calls `payout`, causing `payout` to fail with `Error::VestingScheduleExists` for as long as that externally-created schedule remains in storage.

### Finding Description
The purchase flow is: `create_account` -> `update_validity_status` -> `update_balance` (fixes `free_balance`/`locked_balance` in `Accounts<T>`) -> `payout` (called only by the fixed `PaymentAccount`) [2](#0-1) . `create_account` checks for an absent vesting schedule up front [3](#0-2) , but nothing in `update_validity_status` or `update_balance` re-checks this, and there is a real window between the account being marked valid/funded and `PaymentAccount` actually executing `payout`.

`payout` performs the same `vesting_balance(&who).is_none()` guard again [1](#0-0) , and returns `Error::VestingScheduleExists` if it fails - this happens *before* the `Accounts::<T>::try_mutate` block that would set `status.validity = AccountValidity::Completed` [4](#0-3) . `pallet_vesting::vested_transfer` is a plain signed extrinsic; any account (the victim themselves, or literally any third party who wants to grief the victim) can send a `vested_transfer` to the target `who`, creating a `Vesting` storage entry for that account. `pallet_vesting`'s `vesting_balance` returns `Some(_)` (not `None`) for any account that has a `Vesting` entry, even if the locked amount computed is currently zero - the entry is only cleared by an explicit, separate `vest`/`vest_other` call once the schedule has fully elapsed.

There is no code path in `purchase::mod.rs` that lets `PaymentAccount`, `ConfigurationOrigin`, or anyone else clear/override this condition, force-migrate the account back to a payable state, or bypass the vesting check. Once `payout` fails this way, `Accounts<T>` retains the computed `free_balance`/`locked_balance` and `validity` stays non-`Completed` indefinitely, i.e. until the externally-created vesting schedule itself finishes vesting and someone separately calls `vest`/`vest_other` to purge that `Vesting` entry - an event that is fully outside the purchase pallet's control and can be engineered by the attacker to take an arbitrarily long time (e.g. by choosing a low `per_block` value relative to `locked`).

### Impact Explanation
A purchase participant's already-approved, already-funded entitlement (`free_balance` + `locked_balance` in `Accounts<T>`) becomes unspendable via the intended `payout` path for as long as any vesting schedule exists on that account, with no privileged or unprivileged reset function exposed by the pallet. This matches the scoped self-DoS impact and also generalizes to third-party griefing, since `vested_transfer` can target *any* account, not just the caller's own - meaning any unprivileged attacker can block another user's pending purchase payout by sending them a minimal vested transfer.

### Likelihood Explanation
Fully reachable with unprivileged extrinsics: `pallet_vesting::vested_transfer` requires no special origin beyond being signed and meeting `MinVestedTransfer`. The purchase-side preconditions (`create_account`, `update_validity_status(ValidLow/ValidHigh)`, `update_balance`) are performed by `ValidityOrigin` in the normal flow, and the race window between `update_balance` and `payout` is realistically exploitable since `payout` is a separate, later transaction. The attack requires no chain-level races or privileged access - only a normal signed call.

### Recommendation
Do not treat pre-existing vesting schedules as a hard blocker inside `payout`. Options: (a) remove the redundant `vesting_balance` check from `payout` and instead have `add_vesting_schedule` fail gracefully by merging/queuing (or transferring the free portion immediately and only holding back the locked/vesting portion), (b) allow `PaymentAccount`/`ConfigurationOrigin` to force a compensating action (e.g. transfer `free_balance` unconditionally and merge the locked schedule via `T::VestingSchedule::add_vesting_schedule` even if one exists, using the currency's existing multi-schedule merge behavior rather than erroring), or (c) add an explicit unprivileged/self-service `retry_payout` or "merge vesting" call so a legitimately-owed balance is never left permanently gated behind an unrelated pallet's state.

### Proof of Concept
Rust integration test in `polkadot/runtime/common/src/purchase/tests.rs` (extending the existing mock which wires in `pallet_vesting`):
1. Run through `create_account`, `update_validity_status(who, ValidLow)`, `update_balance(who, free, locked, vat)` for `who`.
2. As `who` (unprivileged), call `Vesting::vested_transfer(RuntimeOrigin::signed(who), who, VestingInfo::new(min_transfer, 1, current_block))` (or have a third party target `who`).
3. As `PaymentAccount`, call `Purchase::payout(RuntimeOrigin::signed(payment_account), who)`.
4. Assert the call returns `Error::<Test>::VestingScheduleExists`.
5. Assert `Accounts::<Test>::get(who)` still has `validity != Completed` and unchanged `free_balance`/`locked_balance`.
6. Repeat `payout` after advancing blocks past the schedule's `starting_block + locked/per_block` without calling `vest`/`vest_other`, and assert it still fails (demonstrating the entry isn't self-clearing), confirming the payout stays blocked until an unrelated, externally-triggered `vest`/`vest_other` call is made.

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

**File:** polkadot/runtime/common/src/purchase/mod.rs (L261-296)
```rust
		/// Update the balance of a valid account.
		///
		/// We check that the account is valid for a balance transfer at this point.
		///
		/// Origin must match the `ValidityOrigin`.
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

**File:** polkadot/runtime/common/src/purchase/mod.rs (L312-316)
```rust
			// Account should not have a vesting schedule.
			ensure!(
				T::VestingSchedule::vesting_balance(&who).is_none(),
				Error::<T>::VestingScheduleExists
			);
```

**File:** polkadot/runtime/common/src/purchase/mod.rs (L318-367)
```rust
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
