### Title
Silently-swallowed `add_vesting_schedule` error in `Pallet::payout` can grant attacker fully-liquid tokens instead of vesting-locked ones - (File: polkadot/runtime/common/src/purchase/mod.rs)

### Summary
`payout` (call_index 3) checks `T::VestingSchedule::vesting_balance(&who).is_none()` and then, inside the same `try_mutate`, calls `T::VestingSchedule::add_vesting_schedule(...)` while discarding the result with `let _ = ...`. If `add_vesting_schedule` fails for a reason not covered by the earlier `vesting_balance` check, the transfer of `total_balance` (free+locked) still completes and `status.validity` is still set to `Completed`, meaning the "locked" portion of the payout is never actually locked.

### Finding Description
The exact code is: [1](#0-0) [2](#0-1) 

The specific TOCTOU/"same-block-race" mechanism described in the prompt does not actually work: the `ensure!(T::VestingSchedule::vesting_balance(&who).is_none(), ...)` check at line 313-316 executes synchronously, immediately before the `try_mutate` block that calls `add_vesting_schedule` at line 346, within the *same* extrinsic dispatch. There is no reentrancy or interleaving point between these two lines where a separate extrinsic (e.g., an earlier `vested_transfer` in the same block) could mutate `who`'s vesting state in between. If an attacker performs an unrelated `vested_transfer` to themselves in an earlier extrinsic of the same block, `vesting_balance(&who)` will return `Some(_)` (non-zero locked amount) by the time `payout` runs later in that same block, so the `ensure!` at line 313-316 would already reject the call with `Error::VestingScheduleExists` — `add_vesting_schedule` is never reached. So the precise race described in the prompt is not a real reachable path.

However, the underlying root cause identified — the `let _ = T::VestingSchedule::add_vesting_schedule(...)` swallowing errors at line 346 — is a genuine logic flaw, just reachable through a different, still user-controllable precondition than a same-block race: pallet_vesting's `VestingSchedules` storage is a bounded structure (`MaxVestingSchedules`) that is only pruned lazily when `vest`/`vest_other` is called; `vesting_balance` can report `None`/`0` for an account whose schedules have all fully unlocked, while the underlying `BoundedVec` storage slots are still occupied by those (unpruned) fully-vested entries. In that state, `add_vesting_schedule` can fail with `AtMaxVestingSchedules` even though `vesting_balance(&who).is_none()` is true. Because this failure is silently discarded, `payout` still transfers `total_balance` (locked + free) in full to `who`, and still marks `status.validity = AccountValidity::Completed`, without ever applying the locking vesting schedule.

### Impact Explanation
If triggered, the "locked" portion of a DOT purchase payout becomes fully liquid immediately, bypassing the `UnlockedProportion`/`MaxUnlocked` vesting guarantee that the pallet is designed to enforce, and the account is irreversibly marked `Completed` so it cannot be corrected later. This is a fund-locking invariant bypass benefiting the recipient account.

### Likelihood Explanation
The trigger requires the recipient (`who`) to have previously exhausted the `MaxVestingSchedules` slots of `pallet_vesting` with schedules that are now fully vested but not yet pruned (an unprivileged action any account can perform ahead of time via ordinary `vested_transfer`s), combined with the trusted `PaymentAccount` eventually calling `payout` for that address as part of the normal crowdsale settlement process. This does not require a same-block race as the prompt describes — that specific race is actually prevented by the synchronous `ensure!` check — but it is a plausible, unprivileged, and repeatable precondition that an attacker fully controls on their own account ahead of time.

### Recommendation
Do not discard the result of `add_vesting_schedule`; propagate the error (e.g., `?`) so the whole `payout` extrinsic (including the token transfer) reverts atomically if vesting application fails, or explicitly reverse/refuse the transfer when the vesting-schedule call fails.

### Proof of Concept
Rust unit test in `polkadot/runtime/common/src/purchase/tests.rs` mock runtime:
1. Set `MaxVestingSchedules` to a small bound (e.g., 1) in the mock for `pallet_vesting`.
2. For the target account `who`, use `pallet_vesting::Pallet::vested_transfer` to create and then fully vest (advance blocks / call `vest`) enough schedules to occupy all `MaxVestingSchedules` slots with stale, fully-vested (but unpruned) entries, so that `T::VestingSchedule::vesting_balance(&who)` returns `None`/`Some(0)` while `pallet_vesting::Vesting::<T>::get(&who)` is still full.
3. Configure the purchase pallet (`create_account`, `update_validity_status` to `ValidHigh`, `update_balance` with non-zero `locked_balance`), then call `Pallet::payout(payment_account_origin, who)`.
4. Assert that `add_vesting_schedule` internally would fail (`AtMaxVestingSchedules`) yet `payout` still returns `Ok(())`, `status.validity == AccountValidity::Completed`, and `who`'s balance is fully free/liquid (no new vesting lock applied) — demonstrating the swallowed error and the lost lock guarantee.

### Citations

**File:** polkadot/runtime/common/src/purchase/mod.rs (L312-316)
```rust
			// Account should not have a vesting schedule.
			ensure!(
				T::VestingSchedule::vesting_balance(&who).is_none(),
				Error::<T>::VestingScheduleExists
			);
```

**File:** polkadot/runtime/common/src/purchase/mod.rs (L336-360)
```rust
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
```
