### Title
Withdrawing a fully unbonded stash permanently forfeits unclaimed era staking rewards ([File: substrate/frame/staking/src/pallet/impls.rs], [File: substrate/frame/staking-async/src/pallet/impls.rs])

### Summary
In both `pallet-staking` and `pallet-staking-async`, a nominator/validator who fully unbonds and calls `withdraw_unbonded` (or is `reap_stash`-ed) has their `Ledger`, `Bonded`, and `Payee` entries deleted via `kill_stash`. If the staker had not yet claimed rewards for one or more past eras (still within `HistoryDepth`) before this happens, those rewards become permanently unclaimable because `payout_stakers`/`do_payout_stakers_by_page` requires a live `Ledger` entry for the stash and returns `Error::NotStash` once it is gone. This mirrors the reported Alchemix `Voter.sol` pattern: an account-destroying withdrawal action executes without first flushing/auto-claiming outstanding rewards, permanently freezing them.

### Finding Description
`do_withdraw_unbonded` kills the stash's staking state once the active bonded balance drops below the existential deposit and no unlocking chunks remain: [1](#0-0) 

`kill_stash` removes `Ledger`, `Bonded`, and `Payee` for the stash: [2](#0-1) 

Claiming a past era's reward via `payout_stakers` explicitly requires resolving the stash's `Ledger`, and fails with `Error::NotStash` if it no longer exists: [3](#0-2) 

The same pattern exists in the async staking pallet: `do_withdraw_unbonded` calls `kill_stash`, which calls `StakingLedger::kill`, removing `Ledger`/`Bonded`/`Payee`: [4](#0-3) [5](#0-4) 

And `do_payout_stakers_by_page` in staking-async performs the identical ledger-existence check that fails with `Error::NotStash` post-kill: [6](#0-5) 

Neither `withdraw_unbonded` nor `reap_stash` attempts to auto-claim (or block if there are) outstanding unclaimed era rewards before destroying the ledger — analogous to how `VotingEscrow.sol::withdraw` burns the veLACX NFT (`_removeTokenFrom`) without first forcing/auto-claiming bribes, after which `Voter.sol::claimBribes`'s `isApprovedOrOwner` check can never succeed again.

### Impact Explanation
A staker who unbonds fully, waits out the bonding duration, and calls `withdraw_unbonded` before claiming rewards for one or more of the eras they were exposed in (eras still inside `HistoryDepth`) permanently loses the ability to claim those rewards — for either themselves (nominator) or, more severely, for every nominator behind a validator stash that gets killed, since `payout_stakers`/`payout_stakers_by_page` is the sole avenue to claim any of that era's stakers' rewards for that validator. This is a permanent freezing/loss of already-accrued, unclaimed yield.

### Likelihood Explanation
This requires no privileged role and is directly reachable by any ordinary nominator/validator: `unbond` → wait `BondingDuration` → `withdraw_unbonded` (or anyone can call `reap_stash` once the stash balance is below ED). It is a realistic and easy sequence for a normal, unprivileged user (or automated wallet/bot doing routine unbonding) to trigger inadvertently by simply not calling `payout_stakers` for all outstanding eras first, exactly paralleling the referenced report's root cause (destructive withdraw without auto-claim).

### Recommendation
Before killing a stash in `do_withdraw_unbonded`/`reap_stash` (in both `pallet-staking` and `pallet-staking-async`), either (a) automatically flush/claim all outstanding claimable era rewards for the stash within `HistoryDepth`, or (b) block the kill/reap path (return an error) while unclaimed reward pages remain for eras still within the claim window, requiring the caller (or a permissionless caller) to call `payout_stakers` for those eras first.

### Proof of Concept
1. Bond stash `S`, nominate a validator, and let `S` earn rewards for eras `E1` and `E2` (do not call `payout_stakers` for either).
2. Call `unbond` for the full active amount from `S` (this auto-chills if `S` is a nominator/validator).
3. Advance chain state past `BondingDuration` eras.
4. Call `withdraw_unbonded(0)` — since `ledger.active < ExistentialDeposit` and `unlocking` is now empty, `kill_stash` executes, removing `Ledger`, `Bonded`, `Payee` for `S` (see `do_withdraw_unbonded` at [1](#0-0)  and `kill_stash` at [2](#0-1) ).
5. Attempt `payout_stakers(S, E1)` (still within `HistoryDepth`): this fails with `Error::NotStash` because `Self::ledger(StakingAccount::Stash(S))` no longer resolves, as shown at [3](#0-2) . The rewards for `E1`/`E2` are now permanently unclaimable for `S` and any nominators exposed through it.

### Citations

**File:** substrate/frame/staking/src/pallet/impls.rs (L204-219)
```rust
		let ed = asset::existential_deposit::<T>();
		let used_weight =
			if ledger.unlocking.is_empty() && (ledger.active < ed || ledger.active.is_zero()) {
				// This account must have called `unbond()` with some value that caused the active
				// portion to fall below existential deposit + will have no more unlocking chunks
				// left. We can now safely remove all staking-related information.
				Self::kill_stash(&ledger.stash, num_slashing_spans)?;

				T::WeightInfo::withdraw_unbonded_kill(num_slashing_spans)
			} else {
				// This was the consequence of a partial unbond. just update the ledger and move on.
				ledger.update()?;

				// This is only an update, so we use less overall weight.
				T::WeightInfo::withdraw_unbonded_update(num_slashing_spans)
			};
```

**File:** substrate/frame/staking/src/pallet/impls.rs (L283-290)
```rust
		let account = StakingAccount::Stash(validator_stash.clone());
		let mut ledger = Self::ledger(account.clone()).or_else(|_| {
			if StakingLedger::<T>::is_bonded(account) {
				Err(Error::<T>::NotController.into())
			} else {
				Err(Error::<T>::NotStash.with_weight(T::WeightInfo::payout_stakers_alive_staked(0)))
			}
		})?;
```

**File:** substrate/frame/staking/src/pallet/impls.rs (L787-798)
```rust
	pub(crate) fn kill_stash(stash: &T::AccountId, num_slashing_spans: u32) -> DispatchResult {
		slashing::clear_stash_metadata::<T>(&stash, num_slashing_spans)?;

		// removes controller from `Bonded` and staking ledger from `Ledger`, as well as reward
		// setting of the stash in `Payee`.
		StakingLedger::<T>::kill(&stash)?;

		Self::do_remove_validator(&stash);
		Self::do_remove_nominator(&stash);

		Ok(())
	}
```

**File:** substrate/frame/staking-async/src/pallet/impls.rs (L288-317)
```rust
		let ed = asset::existential_deposit::<T>();
		let used_weight =
			if ledger.unlocking.is_empty() && (ledger.active < ed || ledger.active.is_zero()) {
				// This account must have called `unbond()` with some value that caused the active
				// portion to fall below the existential deposit + will have no more unlocking
				// chunks left. We can now safely remove all staking-related information.
				Self::kill_stash(&ledger.stash)?;

				T::WeightInfo::withdraw_unbonded_kill()
			} else {
				// This was the consequence of a partial unbond. just update the ledger and move on.
				ledger.update()?;

				// This is only an update, so we use less overall weight.
				T::WeightInfo::withdraw_unbonded_update()
			};

		// `old_total` should never be less than the new total because
		// `consolidate_unlocked` strictly subtracts balance.
		if new_total < old_total {
			// Already checked that this won't overflow by entry condition.
			let value = old_total.defensive_saturating_sub(new_total);
			Self::deposit_event(Event::<T>::Withdrawn { stash, amount: value });

			// notify listeners.
			T::EventListeners::on_withdraw(controller, value);
		}

		Ok(used_weight)
	}
```

**File:** substrate/frame/staking-async/src/pallet/impls.rs (L368-375)
```rust
		let account = StakingAccount::Stash(validator_stash.clone());
		let ledger = Self::ledger(account.clone()).or_else(|_| {
			if StakingLedger::<T>::is_bonded(account) {
				Err(Error::<T>::NotController.into())
			} else {
				Err(Error::<T>::NotStash.with_weight(T::WeightInfo::payout_stakers_alive_staked(0)))
			}
		})?;
```

**File:** substrate/frame/staking-async/src/ledger.rs (L320-338)
```rust
	pub(crate) fn kill(stash: &T::AccountId) -> DispatchResult {
		let controller = <Bonded<T>>::get(stash).ok_or(Error::<T>::NotStash)?;

		<Ledger<T>>::get(&controller).ok_or(Error::<T>::NotController).map(|ledger| {
			Ledger::<T>::remove(controller);
			<Bonded<T>>::remove(&stash);
			<Payee<T>>::remove(&stash);

			// kill virtual staker if it exists.
			if <VirtualStakers<T>>::take(&ledger.stash).is_none() {
				// if not virtual staker, clear locks.
				asset::kill_stake::<T>(&ledger.stash)?;
			}
			Pallet::<T>::deposit_event(crate::Event::<T>::StakerRemoved {
				stash: ledger.stash.clone(),
			});
			Ok(())
		})?
	}
```
