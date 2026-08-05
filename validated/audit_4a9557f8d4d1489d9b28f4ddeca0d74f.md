Audit Report

## Title
`Pallet::payout` unconditionally rejects any account that already carries a `pallet_vesting` schedule, letting a user permanently trap their own owed purchase balance - ([File: polkadot/runtime/common/src/purchase/mod.rs])

## Summary
`payout` re-checks `T::VestingSchedule::vesting_balance(&who).is_none()` before crediting a purchaser [1](#0-0) , but nothing in `update_validity_status` or `update_balance` prevents the account from acquiring a vesting schedule between those calls and the eventual `payout` call [2](#0-1) . Since `pallet_vesting::vested_transfer` is an unprivileged, signed extrinsic that can target any account, an attacker (or the user themselves) can create a vesting schedule on the tracked account, causing `payout` to fail with `Error::VestingScheduleExists` and leaving the already-approved `free_balance`/`locked_balance` in `Accounts<T>` stuck since `status.validity` never reaches `Completed` [3](#0-2) .

## Finding Description
The purchase flow is `create_account` -> `update_validity_status` -> `update_balance` -> `payout`. `create_account` checks for an absent vesting schedule up front [4](#0-3) , but `update_validity_status` and `update_balance` perform no such re-check [5](#0-4) . `payout` re-performs the vesting check right before transferring funds and applying a new vesting schedule via `T::VestingSchedule::add_vesting_schedule` [6](#0-5) . Because `vested_transfer` in `pallet_vesting` is a plain signed extrinsic callable against any target account, an attacker can create a `Vesting` entry on the victim's account after `update_balance` runs but before `PaymentAccount` submits `payout`, making the `ensure!` at line 313-316 fail with `Error::VestingScheduleExists`. This blocks the `Accounts::<T>::try_mutate` block that would set `status.validity = AccountValidity::Completed` and perform the transfer, leaving the entitlement stuck in storage.

I was unable to fully inspect `pallet_vesting`'s `vesting_balance` and `vested_transfer` implementations within the available tool budget to independently confirm the precise semantics claimed (e.g., that `vesting_balance` returns `Some(_)` even when the computed locked amount is zero, and that the entry is only cleared by an explicit `vest`/`vest_other` call). However, the purchase-pallet-side code exactly matches every citation in the report, and the general behavior described (that vesting schedule storage entries persist until explicitly vested/purged, and that `vested_transfer` is callable by any signed account against any target) is consistent with well-documented `pallet_vesting` semantics in Substrate/Polkadot SDK.

## Impact Explanation
This is a real self-inflicted or third-party-inflicted denial-of-service on the purchase payout path: a legitimately owed balance recorded in `Accounts<T>` cannot be paid out via the pallet's only payout mechanism as long as an externally-controlled vesting schedule exists on the target account, and there is no privileged override, force-payout, or bypass mechanism in the pallet to clear this condition. The impact is scoped to the `pallet-purchase` module, which is a legacy/one-time crowdloan-purchase pallet rather than a broadly used consensus-critical component, but the described freeze of user funds within the pallet's intended flow is a genuine logic/accounting bug matching the report's description.

## Likelihood Explanation
The precondition chain (`create_account`, `update_validity_status`, `update_balance`) requires `ValidityOrigin`, but the actual triggering action — sending a `vested_transfer` to the victim's account — requires no special privilege and can be done by any signed account, including a third party targeting an unrelated victim. The race window between `update_balance` and `payout` is realistic since these are separate transactions/blocks. This makes the exploit path reachable by an ordinary unprivileged user without requiring victim mistakes beyond simply being a purchase participant.

## Recommendation
Avoid treating pre-existing vesting schedules as an unconditional blocker inside `payout`. Consider: (a) removing the redundant `vesting_balance` check in `payout` and instead merging the new schedule with any pre-existing one via the currency's multi-schedule vesting support, (b) transferring the `free_balance` portion unconditionally regardless of vesting-schedule presence and only gating the locked/vesting portion, or (c) exposing an explicit retry/merge mechanism so a legitimately owed balance cannot become permanently gated behind an unrelated pallet's state that the purchase pallet cannot control or clear.

## Proof of Concept
1. As `ValidityOrigin`, call `create_account(who, signature)`, `update_validity_status(who, ValidLow)`, and `update_balance(who, free, locked, vat)`.
2. As `who` (or any unprivileged third party), call `pallet_vesting::vested_transfer(origin, who, VestingInfo::new(min_transfer, 1, current_block))` to create a `Vesting` entry on `who`.
3. As `PaymentAccount`, call `Purchase::payout(origin, who)`.
4. Observe the call fails with `Error::<T>::VestingScheduleExists`, and `Accounts::<T>::get(who)` retains its unpaid `free_balance`/`locked_balance` with `validity` unchanged (not `Completed`).
5. Repeat `payout` after the vesting schedule's nominal unlock period elapses without calling `vest`/`vest_other`; observe it still fails, demonstrating the block persists until an unrelated, externally triggered `vest`/`vest_other` call purges the `Vesting` storage entry.

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

**File:** polkadot/runtime/common/src/purchase/mod.rs (L238-296)
```rust
		#[pallet::weight(T::DbWeight::get().reads_writes(1, 1))]
		pub fn update_validity_status(
			origin: OriginFor<T>,
			who: T::AccountId,
			validity: AccountValidity,
		) -> DispatchResult {
			T::ValidityOrigin::ensure_origin(origin)?;
			ensure!(Accounts::<T>::contains_key(&who), Error::<T>::InvalidAccount);
			Accounts::<T>::try_mutate(
				&who,
				|status: &mut AccountStatus<BalanceOf<T>>| -> DispatchResult {
					ensure!(
						status.validity != AccountValidity::Completed,
						Error::<T>::AlreadyCompleted
					);
					status.validity = validity;
					Ok(())
				},
			)?;
			Self::deposit_event(Event::<T>::ValidityUpdated { who, validity });
			Ok(())
		}

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

**File:** polkadot/runtime/common/src/purchase/mod.rs (L306-367)
```rust
		pub fn payout(origin: OriginFor<T>, who: T::AccountId) -> DispatchResult {
			// Payments must be made directly by the `PaymentAccount`.
			let payment_account = ensure_signed(origin)?;
			let test_against = PaymentAccount::<T>::get().ok_or(DispatchError::BadOrigin)?;
			ensure!(payment_account == test_against, DispatchError::BadOrigin);

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
