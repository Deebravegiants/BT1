Based on my investigation, I found a genuine analog of this vulnerability class in the codebase, though I was unable to fully confirm whether the `pallet-purchase` module is actually wired into a live Polkadot/Kusama runtime before the tool budget ran out (I could not find `Purchase` in any `polkadot/runtime/*/lib.rs` in the searches I ran, and my file-read attempts failed due to a parameter error before I could inspect `do_vest`/`write_vesting` directly). I'll present the finding with that caveat.

### Title
Permissionless `vested_transfer` can be used to griefing-lock `purchase::payout` via a pre-existing vesting schedule check - (File: `polkadot/runtime/common/src/purchase/mod.rs`)

### Summary
`pallet_purchase::payout` gates the final crowdloan-payout transfer on the target account having **no** vesting schedule at all: `ensure!(T::VestingSchedule::vesting_balance(&who).is_none(), Error::<T>::VestingScheduleExists)` [1](#0-0) . `Vesting::vested_transfer` is a fully permissionless, signed extrinsic that lets **any** account create a vesting schedule targeting **any other** account, as long as the transferred amount meets `MinVestedTransfer` [2](#0-1) . This mirrors the report's pattern: a permission-less "lock for anyone" primitive (`AuraLocker.lock(strategy, amount)`) is used to poison a strict "must have zero locked balance" precondition (`LOCKER.balanceOf(strategy) == 0`) gating a privileged fund-movement operation (`_withdrawAll` / migration).

### Finding Description
- `payout` is only callable by the configured `PaymentAccount` origin, but the account it checks (`who`, the purchaser) is an arbitrary, attacker-choosable target [3](#0-2) .
- `VestingSchedule::vesting_balance` returns `Some(_)` whenever a `Vesting` storage entry exists for that account, regardless of how small the locked amount is or how quickly it vests [4](#0-3) .
- Anyone can call `Vesting::vested_transfer(origin, who, schedule)` with `who` set to the victim purchase account, transferring only the pallet's `MinVestedTransfer` minimum, thereby creating a `Vesting` entry for `who` [2](#0-1) [5](#0-4) .
- Once that entry exists, `payout` will revert with `VestingScheduleExists` for that account until the schedule is fully consumed *and* the entry is cleared via `vest`/`vest_other`, which the victim account (or anyone via `vest_other`) can call — but only after the vesting period elapses [6](#0-5) .

### Impact Explanation
This blocks the `PaymentAccount`'s ability to complete the crowdloan/DOT-purchase payout for any specific account an attacker chooses to target, denying the purchaser their funds (or delaying it for the duration of an attacker-chosen vesting schedule). Unlike the original Badger report where end-users could still withdraw via a fallback path, here the affected user's ability to receive payout is fully gated by this pallet-level check with no bypass exposed in the code I reviewed (I did not find a `force_remove_vesting_schedule`-equivalent call reachable by `PaymentAccount`, though `force_remove_vesting_schedule` exists and is Root-only, per the tests I found using `RawOrigin::Root` [7](#0-6) ). Root/governance intervention would be required to unblock, similar to the "no strategy migration is possible" acknowledgment in the original finding.

### Likelihood Explanation
Likelihood is high in principle — `vested_transfer` is unauthenticated with respect to the target and only requires the caller to have `MinVestedTransfer` funds, which is typically small on a runtime. **However**, I could not confirm that `pallet_purchase` is actually included/instantiated in any currently deployed Polkadot or Kusama runtime in this snapshot — my searches for `Purchase`/`pallet_purchase` wiring in `polkadot/runtime/*/lib.rs` returned no matches, and I ran out of tool budget before I could verify this further or inspect `do_vest` to confirm exactly how/when the `Vesting` storage entry is cleared. This pallet may be legacy/unused code, in which case there is no reachable attacker-controlled entry path in a live runtime, which would disqualify this per the "no reachable attacker-controlled entry path" rule.

### Recommendation
If `pallet_purchase` (or a similar consumer of `VestingSchedule::vesting_balance`) is active in a deployed runtime, `payout` should not treat "any vesting schedule exists" as a hard blocker attributable entirely to attacker-triggerable state. Options: (a) allow `PaymentAccount` to force-clear/ignore vesting schedules it did not itself create when paying out, (b) check that the *locked amount* is below a negligible threshold rather than merely `is_none()`, or (c) require that vesting schedules affecting purchase accounts can only originate from a trusted origin (e.g., `force_vested_transfer`), not the permissionless `vested_transfer`.

### Proof of Concept
Given a purchase account `who` that has not yet been paid out:
1. Attacker (any signed account with `MinVestedTransfer` funds) calls `Vesting::vested_transfer(attacker, who, VestingInfo::new(MinVestedTransfer, 1, far_future_block))`.
2. `PaymentAccount` calls `Purchase::payout(who)`.
3. `ensure!(T::VestingSchedule::vesting_balance(&who).is_none(), Error::<T>::VestingScheduleExists)` fails because `Vesting::<T>::get(who)` is `Some(_)` [1](#0-0) .
4. `payout` reverts, and remains blocked until the schedule fully vests and is manually cleared.

**Note on confidence**: This is presented as a plausible analog rather than a fully proven, in-scope finding, because I was unable to verify (within the remaining tool budget) whether `pallet_purchase` is actually part of any live runtime configuration in this codebase snapshot. If it is dead/unused code not compiled into Polkadot/Kusama runtimes, this finding should be disqualified per the "bridge-only/node-only/otherwise outside active program focus" exclusion rule, and I recommend verifying this with a `grep` for `Purchase` across `polkadot/runtime/*/src/lib.rs` and `Cargo.toml` dependency graphs before treating this as reportable.

### Citations

**File:** polkadot/runtime/common/src/purchase/mod.rs (L298-317)
```rust
		/// Pay the user and complete the purchase process.
		///
		/// We reverify all assumptions about the state of an account, and complete the process.
		///
		/// Origin must match the configured `PaymentAccount` (if it is not configured then this
		/// will always fail with `BadOrigin`).
		#[pallet::call_index(3)]
		#[pallet::weight(T::DbWeight::get().reads_writes(4, 2))]
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

```

**File:** substrate/frame/vesting/src/lib.rs (L368-380)
```rust
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

**File:** substrate/frame/vesting/src/lib.rs (L552-586)
```rust
	// Execute a vested transfer from `source` to `target` with the given `schedule`.
	fn do_vested_transfer(
		source: &T::AccountId,
		target: &T::AccountId,
		schedule: VestingInfo<BalanceOf<T>, BlockNumberFor<T>>,
	) -> DispatchResult {
		// Validate user inputs.
		ensure!(schedule.locked() >= T::MinVestedTransfer::get(), Error::<T>::AmountLow);
		if !schedule.is_valid() {
			return Err(Error::<T>::InvalidScheduleParams.into());
		};

		// Check we can add to this account prior to any storage writes.
		Self::can_add_vesting_schedule(
			target,
			schedule.locked(),
			schedule.per_block(),
			schedule.starting_block(),
		)?;

		T::Currency::transfer(source, target, schedule.locked(), ExistenceRequirement::AllowDeath)?;

		// We can't let this fail because the currency transfer has already happened.
		// Must be successful as it has been checked before.
		// Better to return error on failure anyway.
		let res = Self::add_vesting_schedule(
			target,
			schedule.locked(),
			schedule.per_block(),
			schedule.starting_block(),
		);
		debug_assert!(res.is_ok(), "Failed to add a schedule when we had to succeed.");

		Ok(())
	}
```

**File:** substrate/frame/vesting/src/lib.rs (L620-633)
```rust
	/// Write an accounts updated vesting lock to storage.
	fn write_lock(who: &T::AccountId, total_locked_now: BalanceOf<T>) {
		if total_locked_now.is_zero() {
			T::Currency::remove_lock(VESTING_ID, who);
			Self::deposit_event(Event::<T>::VestingCompleted { account: who.clone() });
		} else {
			let reasons = WithdrawReasons::except(T::UnvestedFundsAllowedWithdrawReasons::get());
			T::Currency::set_lock(VESTING_ID, who, total_locked_now, reasons);
			Self::deposit_event(Event::<T>::VestingUpdated {
				account: who.clone(),
				unvested: total_locked_now,
			});
		};
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

**File:** substrate/frame/vesting/src/tests.rs (L1208-1211)
```rust
		// Verify only root can call.
		assert_noop!(Vesting::force_remove_vesting_schedule(Some(4).into(), 4, 0), BadOrigin);
		// Verify that root can remove the schedule.
		assert_ok!(Vesting::force_remove_vesting_schedule(RawOrigin::Root.into(), 4, 0));
```
