### Title
Reward payout marked as claimed before pot transfer succeeds, causing permanent, unrecoverable loss of staking rewards — (`substrate/frame/staking-async/src/pallet/impls.rs`)

### Summary
In `pallet-staking-async`'s DAP (Direct Asset Provisioning) payout path, `do_payout_stakers_by_page` irreversibly marks a validator's reward page as claimed *before* the underlying token transfer from the era reward pot is attempted or confirmed to succeed. If the era's reward pot ends up underfunded relative to the amount owed (which can happen when `snapshot_era_rewards` fails to move the full general-pot balance into the era-specific pot), the subsequent transfer in `make_payout_from_provider` silently fails and returns `None`, dropping the reward — but the "claimed" flag is already set, so the reward can never be retried. This mirrors the Salty.IO `SaltRewards` finding: accounting state (claim status / accrued profits) is finalized independently of whether the value-moving operation actually succeeded, leading to lost rewards for legitimate participants.

### Finding Description
`do_payout_stakers_by_page` calls `Eras::<T>::set_rewards_as_claimed(era, &stash, page)` at [1](#0-0) 
before any reward amount is calculated or transferred. Later, the actual transfer happens through `payout_from_provider` → `make_payout_from_provider`, which moves funds from the era's `staker_rewards_pot` to the payee: [2](#0-1) 

If the transfer errors (e.g. `FundsUnavailable`, or the destination would be left below the existential deposit under `Preservation::Expendable`), the function only logs the error and returns `None` — the caller (`payout_from_provider`) simply skips emitting the `Rewarded` event and the dispatch call still returns `Ok(...)`: [3](#0-2) 

Because the claim flag was already set at line 386, a subsequent call to `payout_stakers`/`payout_stakers_by_page` for the same `(era, stash, page)` is rejected with `AlreadyClaimed`: [4](#0-3) [5](#0-4) 

The underfunded-pot scenario is realistic because the era pot's balance is snapshotted from a *general* pot, and that snapshot transfer itself can fail (logged and silently defaulted to zero moved) without blocking era rotation: [6](#0-5) 

This is the direct analog of the Salty.IO bug: `profitsForPools`/claim accounting is cleared/finalized regardless of whether the corresponding value transfer (WETH→SALT swap in the original report, pot→payee transfer here) actually succeeded.

### Impact Explanation
A validator's and its nominators' entire page of staking rewards for an era can be permanently and silently lost with no way to reclaim them, since the claimed-flag gate makes the loss irreversible. This directly harms honest, unprivileged stakers (nominators/validators) who did nothing wrong — their entitled rewards vanish from the pot without being paid, and re-attempting payout is explicitly blocked by `Error::AlreadyClaimed`.

### Likelihood Explanation
Likelihood is low-to-medium and depends on the era reward pot being underfunded when `payout_stakers` is called — realistically triggered by a transfer failure during `snapshot_era_rewards` (e.g., due to existential-deposit/dust edge cases, holds, or freezes on the general pot account) rather than by direct attacker control. `payout_stakers` itself is a permissionless, unprivileged extrinsic callable by anyone for any validator/era/page, so once the pot is underfunded, any user (attacker or not) triggering payout will cause the loss to be locked in rather than merely delayed.

### Recommendation
Only mark the page as claimed after the transfer(s) in `payout_from_provider`/`make_payout_from_provider` have succeeded (or, if partial payouts must proceed atomically with claiming, revert the whole extrinsic on transfer failure instead of silently continuing). Alternatively, decouple "claimed" state from "paid" state and provide a distinct retry mechanism so a failed transfer can be re-attempted against the pot in a later block once it is refunded, mirroring the recommendation in the original report to make the downstream step dependent on the upstream step's success.

### Proof of Concept
1. Set up an era where `snapshot_era_rewards` fails to move funds into the era's `StakerRewards` pot for validator `V` (e.g., by causing the general pot's `T::Currency::transfer` at `reward.rs:110-121` to error, leaving `actual_staker = Zero::zero()` while `ErasStakersOverview`/`ErasValidatorReward` for the era still record a non-zero payout amount).
2. Call `payout_stakers(V, era)` as any unprivileged account. `do_payout_stakers_by_page` sets `Eras::set_rewards_as_claimed(era, V, page)` at `impls.rs:386`, then attempts `payout_from_provider`, whose `make_payout_from_provider` transfer from the (empty/underfunded) `staker_rewards_pot` fails, logs the error, and returns `None` — no `Rewarded` event, no funds moved, but the call still returns `Ok(...)`.
3. Call `payout_stakers(V, era)` again for the same page: it now fails with `Error::AlreadyClaimed` (`impls.rs:381-384`), proving the reward can never be claimed/distributed — it is permanently lost, analogous to `pools.clearProfitsForPools()` in the original Salty.IO report.

### Citations

**File:** substrate/frame/staking-async/src/pallet/impls.rs (L331-336)
```rust
		let page = Eras::<T>::get_next_claimable_page(era, &validator_stash).ok_or_else(|| {
			Error::<T>::AlreadyClaimed.with_weight(T::WeightInfo::payout_stakers_alive_staked(0))
		})?;

		Self::do_payout_stakers_by_page(validator_stash, era, page)
	}
```

**File:** substrate/frame/staking-async/src/pallet/impls.rs (L381-386)
```rust
		if Eras::<T>::is_rewards_claimed(era, &stash, page) {
			return Err(Error::<T>::AlreadyClaimed
				.with_weight(T::WeightInfo::payout_stakers_alive_staked(0)));
		}

		Eras::<T>::set_rewards_as_claimed(era, &stash, page);
```

**File:** substrate/frame/staking-async/src/pallet/impls.rs (L491-516)
```rust
		if let Some((amount, dest)) = Self::make_payout_from_provider(era, stash, validator_payout)
		{
			Self::deposit_event(Event::<T>::Rewarded { stash: stash.clone(), dest, amount });
		}

		let total_nominator_stake = exposure.total().saturating_sub(overview_own);
		for nominator in exposure.others().iter() {
			let nominator_exposure_part =
				Perbill::from_rational(nominator.value, total_nominator_stake);
			let nominator_reward: BalanceOf<T> =
				nominator_exposure_part.mul_floor(total_nominator_payout);

			if let Some((amount, dest)) =
				Self::make_payout_from_provider(era, &nominator.who, nominator_reward)
			{
				nominator_payout_count.saturating_inc();
				Self::deposit_event(Event::<T>::Rewarded {
					stash: nominator.who.clone(),
					dest,
					amount,
				});
			}
		}

		nominator_payout_count
	}
```

**File:** substrate/frame/staking-async/src/pallet/impls.rs (L598-616)
```rust
		let payout_account = Self::payout_account_for_dest(stash, &dest)?;

		let staker_rewards_pot =
			T::RewardPots::pot_account(RewardPot::Era(era, RewardKind::StakerRewards));
		if let Err(e) = T::Currency::transfer(
			&staker_rewards_pot,
			&payout_account,
			amount,
			Preservation::Expendable,
		) {
			log!(
				error,
				"Failed to transfer reward from pot for era {:?}, stash {:?}: {:?}",
				era,
				stash,
				e
			);
			return None;
		}
```

**File:** substrate/frame/staking-async/src/reward.rs (L109-125)
```rust
		let actual_staker = if !staker_balance.is_zero() {
			match T::Currency::transfer(
				&general_staker_pot,
				&staker_era_pot,
				staker_balance,
				Preservation::Preserve,
			) {
				Ok(_) => staker_balance,
				Err(e) => {
					log!(error, "Era {:?}: staker reward transfer failed: {:?}", era, e);
					defensive!("Failed to transfer staker rewards to era pot");
					Zero::zero()
				},
			}
		} else {
			Zero::zero()
		};
```
