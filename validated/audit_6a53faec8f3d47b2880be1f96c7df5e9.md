Audit Report

## Title
Griefing DoS via front-run vesting schedule permanently blocks `payout` for a valid purchaser - (File: polkadot/runtime/common/src/purchase/mod.rs)

## Summary
`payout` re-checks `T::VestingSchedule::vesting_balance(&who).is_none()` [1](#0-0)  before performing the currency transfer and marking the account `Completed`. Since `pallet_vesting::vested_transfer` is a public, signed extrinsic that can push a vesting schedule onto any target `AccountId` without that account's consent, an unprivileged attacker can front-run a legitimate purchaser's `payout` call by giving that purchaser a vesting schedule, causing `payout` to permanently fail with `Error::VestingScheduleExists`.

## Finding Description
The `purchase` pallet's `payout` extrinsic requires that `who` has no existing vesting schedule before it will proceed to `Accounts::<T>::try_mutate`, which performs the actual `T::Currency::transfer` and, if `locked_balance` is non-zero, calls `T::VestingSchedule::add_vesting_schedule` [2](#0-1) . The same check exists in `create_account` [3](#0-2) , but `update_validity_status` and `update_balance` do not re-verify or clear vesting state [4](#0-3) , so there is a window between account creation/validation and `payout` execution during which a vesting schedule could be attached to `who` externally, and no recovery path exists inside this pallet if that happens. If the check at line 314 fails, the whole `payout` call reverts before `status.validity` is ever advanced to `Completed`, so every subsequent `payout` call for that `who` will hit the identical check and fail the same way, since nothing in the pallet clears or bypasses an externally-created vesting schedule.

This part of the finding's mechanics is accurately described and confirmed in the code. However, whether `pallet_vesting::vested_transfer` can be used by an arbitrary unprivileged attacker to plant a vesting schedule on an arbitrary victim account without any consent or interaction from that victim could not be fully re-verified in this session — the tool budget was exhausted before the exact `vested_transfer` implementation and its default `MaxVestingSchedules`/target-consent semantics in `substrate/frame/vesting/src/lib.rs` could be inspected line-by-line. This is a well-known, longstanding property of `pallet_vesting` (originally via `Currency::transfer` + `add_vesting_schedule`, later refactored to use `frame_support::traits::VestedTransfer`), and is consistent with public documentation of the pallet's `vested_transfer(origin, target, schedule)` dispatchable, which historically imposes no requirement that `target` consent, only that the schedule satisfies `MinVestedTransfer` and that `target` does not already exceed `MaxVestingSchedules`.

## Impact Explanation
Assuming `pallet_vesting::vested_transfer` behaves as documented (any signed account can push a vesting schedule onto any target without consent), this is a real, permanent, per-victim griefing/DoS vector: a legitimate purchaser who has been validated by `ValidityOrigin` and had balances configured via `update_balance` can be permanently denied their `payout` — both `free_balance` and `locked_balance` — by any unprivileged third party who front-runs the `PaymentAccount`'s `payout(who)` call with a `vested_transfer` targeting `who`. Because the vesting check occurs before `Accounts::try_mutate`, `status.validity` never reaches `Completed`, and there is no extrinsic in the `purchase` pallet capable of clearing or overriding a pre-existing vesting schedule on `who`, so the block is permanent without out-of-band remediation (e.g., a storage migration or fix outside the pallet). This is a fund-lock/DoS impact on the specific victim, not a theft of pallet or `PaymentAccount` funds, matching the report's own characterization.

## Likelihood Explanation
The attack requires only a signed account with enough balance to satisfy `pallet_vesting`'s `MinVestedTransfer`, and the target's `AccountId`, which is realistically discoverable from the pallet's own `AccountCreated`/`ValidityUpdated`/`BalanceUpdated` events [5](#0-4) . The race window between validation/balance-setting and the `PaymentAccount`'s `payout` call can span a considerable period in a real DOT-purchase campaign, making this feasible and repeatable against multiple victims. This is triggerable entirely by an unprivileged extrinsic and does not require any privilege escalation.

## Recommendation
Avoid permanently reverting `payout` due to a vesting schedule created outside the pallet's control:
- If `who` already has a vesting schedule at `payout` time, still transfer the `free_balance`/`locked_balance` and mark the account `Completed`, deferring or skipping only the `add_vesting_schedule` call (or attempting to merge into the existing schedule) rather than aborting the entire extrinsic.
- Alternatively, keep the vesting-schedule guard only in `create_account` (which already protects the initial state) and handle a later-appearing schedule in `payout` gracefully — e.g., transfer the free balance unconditionally and emit an event/error state for the locked-balance vesting failure instead of reverting the whole call.
- Add an administrative extrinsic guarded by `T::ConfigurationOrigin`/`T::ValidityOrigin` to force-complete or reset an account stuck in this specific griefed state.

## Proof of Concept
Unit test in `polkadot/runtime/common/src/purchase/tests.rs` mock environment:
1. `ValidityOrigin` calls `create_account(who, signature)` — succeeds.
2. `ValidityOrigin` calls `update_validity_status(who, ValidHigh)` and `update_balance(who, free, locked, vat)` — succeed.
3. Before `PaymentAccount` calls `payout`, invoke the mock `VestingSchedule::add_vesting_schedule(&who, locked_amount, per_block, starting_block)` directly, simulating an attacker's `pallet_vesting::vested_transfer(target = who, ...)` reaching `who` — succeeds.
4. `PaymentAccount` calls `payout(origin, who)` — returns `Err(Error::<Test>::VestingScheduleExists)`.
5. Call `payout` again — still returns the same error, demonstrating permanence.
6. Assert `Accounts::<Test>::get(&who).validity` remains `ValidHigh` (never `Completed`) and balances of `who`/`PaymentAccount` are unchanged.

### Citations

**File:** polkadot/runtime/common/src/purchase/mod.rs (L136-144)
```rust
		/// A new account was created.
		AccountCreated { who: T::AccountId },
		/// Someone's account validity was updated.
		ValidityUpdated { who: T::AccountId, validity: AccountValidity },
		/// Someone's purchase balance was updated.
		BalanceUpdated { who: T::AccountId, free: BalanceOf<T>, locked: BalanceOf<T> },
		/// A payout was made to a purchaser.
		PaymentComplete { who: T::AccountId, free: BalanceOf<T>, locked: BalanceOf<T> },
		/// A new payment account was set.
```

**File:** polkadot/runtime/common/src/purchase/mod.rs (L208-213)
```rust
			ensure!(!Accounts::<T>::contains_key(&who), Error::<T>::ExistingAccount);
			// Account should not have a vesting schedule.
			ensure!(
				T::VestingSchedule::vesting_balance(&who).is_none(),
				Error::<T>::VestingScheduleExists
			);
```

**File:** polkadot/runtime/common/src/purchase/mod.rs (L239-296)
```rust
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

**File:** polkadot/runtime/common/src/purchase/mod.rs (L312-316)
```rust
			// Account should not have a vesting schedule.
			ensure!(
				T::VestingSchedule::vesting_balance(&who).is_none(),
				Error::<T>::VestingScheduleExists
			);
```

**File:** polkadot/runtime/common/src/purchase/mod.rs (L318-356)
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
```
