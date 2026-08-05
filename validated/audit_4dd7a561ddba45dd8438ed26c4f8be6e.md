Audit Report

## Title
Nomination Pool Members Can Front-Run `payout_stakers` by Joining Before Reward Payout Lands, Diluting Earlier Members' Rewards - ([File: substrate/frame/nomination-pools/src/lib.rs])

## Summary
`RewardPool::update_records`/`current_reward_counter` split any newly-arrived balance in a pool's reward account pro-rata across `bonded_pool.points` *as they exist at the moment the split is computed*, not as they existed when the underlying staking reward was actually earned. Because `payout_stakers` (permissionless, in `pallet-staking`) can transfer a lump-sum era reward into the pool's reward account at any time after era-end, and `join`/`bond_extra` (permissionless, in `pallet-nomination-pools`) can increase `bonded_pool.points` at any time before that transfer, an attacker can join with a large bond after an era's exposure is snapshotted but before `payout_stakers` executes, and subsequently claim a slice of a reward their capital did not help earn — at the direct expense of members who were bonded during the reward-earning era.

## Finding Description
The reward-counter mechanism computes the newly accrued reward as the *change in reward-account balance* since the last checkpoint, divided by *current* `bonded_pool.points`: [1](#0-0) 

`join()` calls `reward_pool.update_records(pool_id, bonded_pool.points, ...)` using the *old* point total before adding the new member's points, and sets the new member's `last_recorded_reward_counter` to the resulting value, then increases `bonded_pool.points` with the new points: [2](#0-1) 

Separately, `pallet-staking`'s `do_payout_stakers_by_page` — callable by any signed account for any pool's stash, using an exposure snapshot fixed at era-end — transfers the era's reward into the pool's reward account at whatever time it is called, which is often well after era-end: [3](#0-2) [4](#0-3) 

Exploit sequence:
1. Era `E` ends; validator `V`'s exposure for era `E` is snapshotted and reflects only pre-existing pool stake.
2. Before `payout_stakers(V, E)` is called, attacker calls `join()` with a large bond. `update_records` runs against the *current* (pre-payout) reward-account balance, so `last_recorded_total_payouts`/`last_recorded_reward_counter` are checkpointed at the pre-payout state — the attacker's recorded counter is "caught up" to the state before the lump sum lands. Critically, `bonded_pool.points` is then increased by the attacker's freshly-bonded points, permanently changing the denominator used for all future reward splits.
3. `payout_stakers(V, E)` executes (by anyone), transferring the era-`E` reward into the pool's reward account, computed from the old (pre-attacker) exposure.
4. Attacker calls `claim_payout` → `do_reward_payout`, which recomputes `current_reward_counter` via `RewardPool::current_reward_counter(bonded_pool.points, ...)`. The delta in reward-account balance since step 2's checkpoint (i.e., the entire lump-sum payout) is divided by the *post-join* `bonded_pool.points`, which includes the attacker's newly bonded, reward-blind points: [5](#0-4) 

There is no mechanism that ties a member's eligibility for a given era's reward to whether their points existed at that era's exposure-snapshot time — eligibility is purely a function of `bonded_pool.points` at the moment `update_records`/`current_reward_counter` is evaluated, which is attacker-controllable relative to the (permissionless, timing-uncontrolled) `payout_stakers` call. This does dilute the per-point reward for members who were bonded during era `E`, since the same lump sum is now divided across a larger point total that includes stake contributed after the reward was already earned.

## Impact Explanation
This is a genuine, code-confirmed accounting flaw: the reward-splitting formula in `RewardPool::current_reward_counter` does not time-weight points against when the underlying staking reward was earned, only against when the split is computed. An attacker can capture a portion of yield legitimately earned by other pool members without having contributed capital during the earning period, with the capital risk limited to `BondingDuration` while the reward itself is extracted immediately and irreversibly via `claim_payout`. This constitutes value extraction/dilution against other nomination-pool members — an in-scope accounting/economic-fairness bug in `pallet-nomination-pools`, reachable by any unprivileged, permissionless account.

## Likelihood Explanation
All three calls involved (`join`, `payout_stakers`, `claim_payout`) are permissionless and require no special privilege. The attack's feasibility depends on a real-world timing gap between era-end (exposure snapshot) and the execution of `payout_stakers` for that era — a gap that commonly exists in practice since payouts are not automatic and are frequently claimed hours or days later by pool operators or bots. The attacker also needs sufficient capital to temporarily bond an outsized amount relative to the pool's accrued-but-unclaimed reward, and must accept `BondingDuration` illiquidity on the principal even though the reward itself is captured instantly. This makes the attack realistic but opportunistic — it scales with the size of the delayed, unclaimed reward relative to pool size, rather than being trivially profitable in all cases.

## Recommendation
- Track reward eligibility per bonding-era/checkpoint rather than by "current points at split time," e.g., only allow newly bonded points to participate in reward splits computed from balance increases that occur strictly after the points were added (this already happens correctly for the *pre-join* balance state, but not for lump sums landing shortly after join).
- Alternatively, add a minimum eligibility delay for newly bonded points before they can share in a `payout_stakers` transfer whose underlying era exposure predates the bond.
- Consider requiring/incentivizing prompt `payout_stakers` claims per era to shrink the exploitable window, though this is a weaker mitigation given `payout_stakers` timing is not currently pool-controlled.

## Proof of Concept
1. Pool `P` bonds to validator `V`. Era `E` ends; exposure for era `E` is snapshotted via `EraInfo::<T>::get_paged_exposure`, reflecting only existing pool members' stake.
2. Before anyone calls `Staking::payout_stakers(V, E)`, attacker calls `Pools::join(pool_id, large_amount)`. This runs `RewardPool::update_records` against the pre-payout balance (checkpointing `last_recorded_reward_counter`/`last_recorded_total_payouts`), then adds the attacker's points to `bonded_pool.points`.
3. Anyone calls `Staking::payout_stakers(V, E)`, transferring the era-`E` reward (computed from the exposure snapshot in step 1, excluding attacker's stake) into pool `P`'s reward account.
4. Attacker calls `Pools::claim_payout()`. `do_reward_payout` recomputes `current_reward_counter` using the now-inflated reward-account balance and the post-join `bonded_pool.points` (which include the attacker's points), paying the attacker a pro-rata share of the era-`E` reward.
5. A unit test in `substrate/frame/nomination-pools/src/tests.rs` reproducing this sequence (join before `payout_stakers`, then `claim_payout`, comparing attacker's claimed reward against zero/expected-zero baseline) would concretely demonstrate the dilution and confirm the non-zero payout to the late joiner.

### Citations

**File:** substrate/frame/nomination-pools/src/lib.rs (L1450-1511)
```rust
	fn current_reward_counter(
		&self,
		id: PoolId,
		bonded_points: BalanceOf<T>,
		commission: Perbill,
	) -> Result<(T::RewardCounter, BalanceOf<T>), Error<T>> {
		let balance = Self::current_balance(id);

		// Calculate the current payout balance. The first 3 values of this calculation added
		// together represent what the balance would be if no payouts were made. The
		// `last_recorded_total_payouts` is then subtracted from this value to cancel out previously
		// recorded payouts, leaving only the remaining payouts that have not been claimed.
		let current_payout_balance = balance
			.saturating_add(self.total_rewards_claimed)
			.saturating_add(self.total_commission_claimed)
			.saturating_sub(self.last_recorded_total_payouts);

		// Split the `current_payout_balance` into claimable rewards and claimable commission
		// according to the current commission rate.
		let new_pending_commission = commission * current_payout_balance;
		let new_pending_rewards = current_payout_balance.saturating_sub(new_pending_commission);

		// * accuracy notes regarding the multiplication in `checked_from_rational`:
		// `current_payout_balance` is a subset of the total_issuance at the very worse.
		// `bonded_points` are similarly, in a non-slashed pool, have the same granularity as
		// balance, and are thus below within the range of total_issuance. In the worse case
		// scenario, for `saturating_from_rational`, we have:
		//
		// dot_total_issuance * 10^18 / `minJoinBond`
		//
		// assuming `MinJoinBond == ED`
		//
		// dot_total_issuance * 10^18 / 10^10 = dot_total_issuance * 10^8
		//
		// which, with the current numbers, is a miniscule fraction of the u128 capacity.
		//
		// Thus, adding two values of type reward counter should be safe for ages in a chain like
		// Polkadot. The important note here is that `reward_pool.last_recorded_reward_counter` only
		// ever accumulates, but its semantics imply that it is less than total_issuance, when
		// represented as `FixedU128`, which means it is less than `total_issuance * 10^18`.
		//
		// * accuracy notes regarding `checked_from_rational` collapsing to zero, meaning that no
		//   reward can be claimed:
		//
		// largest `bonded_points`, such that the reward counter is non-zero, with `FixedU128` will
		// be when the payout is being computed. This essentially means `payout/bonded_points` needs
		// to be more than 1/1^18. Thus, assuming that `bonded_points` will always be less than `10
		// * dot_total_issuance`, if the reward_counter is the smallest possible value, the value of
		//   the
		// reward being calculated is:
		//
		// x / 10^20 = 1/ 10^18
		//
		// x = 100
		//
		// which is basically 10^-8 DOTs. See `smallest_claimable_reward` for an example of this.
		let current_reward_counter =
			T::RewardCounter::checked_from_rational(new_pending_rewards, bonded_points)
				.and_then(|ref r| self.last_recorded_reward_counter.checked_add(r))
				.ok_or(Error::<T>::OverflowRisk)?;

		Ok((current_reward_counter, new_pending_commission))
```

**File:** substrate/frame/nomination-pools/src/lib.rs (L2136-2161)
```rust
			let mut bonded_pool = BondedPool::<T>::get(pool_id).ok_or(Error::<T>::PoolNotFound)?;
			bonded_pool.ok_to_join()?;

			let mut reward_pool = RewardPools::<T>::get(pool_id)
				.defensive_ok_or::<Error<T>>(DefensiveError::RewardPoolNotFound.into())?;
			// IMPORTANT: reward pool records must be updated with the old points.
			reward_pool.update_records(
				pool_id,
				bonded_pool.points,
				bonded_pool.commission.current(),
			)?;

			bonded_pool.try_inc_members()?;
			let points_issued = bonded_pool.try_bond_funds(&who, amount, BondType::Extra)?;

			PoolMembers::insert(
				who.clone(),
				PoolMember::<T> {
					pool_id,
					points: points_issued,
					// we just updated `last_known_reward_counter` to the current one in
					// `update_recorded`.
					last_recorded_reward_counter: reward_pool.last_recorded_reward_counter(),
					unbonding_eras: Default::default(),
				},
			);
```

**File:** substrate/frame/nomination-pools/src/lib.rs (L3524-3571)
```rust
	/// If the member has some rewards, transfer a payout from the reward pool to the member.
	// Emits events and potentially modifies pool state if any arithmetic saturates, but does
	// not persist any of the mutable inputs to storage.
	fn do_reward_payout(
		member_account: &T::AccountId,
		member: &mut PoolMember<T>,
		bonded_pool: &mut BondedPool<T>,
		reward_pool: &mut RewardPool<T>,
	) -> Result<BalanceOf<T>, DispatchError> {
		debug_assert_eq!(member.pool_id, bonded_pool.id);
		debug_assert_eq!(&mut PoolMembers::<T>::get(member_account).unwrap(), member);

		// a member who has no skin in the game anymore cannot claim any rewards.
		ensure!(!member.active_points().is_zero(), Error::<T>::FullyUnbonding);

		let (current_reward_counter, _) = reward_pool.current_reward_counter(
			bonded_pool.id,
			bonded_pool.points,
			bonded_pool.commission.current(),
		)?;

		// Determine the pending rewards. In scenarios where commission is 100%, `pending_rewards`
		// will be zero.
		let pending_rewards = member.pending_rewards(current_reward_counter)?;
		if pending_rewards.is_zero() {
			return Ok(pending_rewards);
		}

		// IFF the reward is non-zero alter the member and reward pool info.
		member.last_recorded_reward_counter = current_reward_counter;
		reward_pool.register_claimed_reward(pending_rewards);

		T::Currency::transfer(
			&bonded_pool.reward_account(),
			member_account,
			pending_rewards,
			// defensive: the depositor has put existential deposit into the pool and it stays
			// untouched, reward account shall not die.
			Preservation::Preserve,
		)?;

		Self::deposit_event(Event::<T>::PaidOut {
			member: member_account.clone(),
			pool_id: member.pool_id,
			payout: pending_rewards,
		});
		Ok(pending_rewards)
	}
```

**File:** substrate/frame/staking/src/pallet/impls.rs (L253-298)
```rust
	pub(super) fn do_payout_stakers_by_page(
		validator_stash: T::AccountId,
		era: EraIndex,
		page: Page,
	) -> DispatchResultWithPostInfo {
		// Validate input data
		let current_era = CurrentEra::<T>::get().ok_or_else(|| {
			Error::<T>::InvalidEraToReward
				.with_weight(T::WeightInfo::payout_stakers_alive_staked(0))
		})?;

		let history_depth = T::HistoryDepth::get();
		ensure!(
			era <= current_era && era >= current_era.saturating_sub(history_depth),
			Error::<T>::InvalidEraToReward
				.with_weight(T::WeightInfo::payout_stakers_alive_staked(0))
		);

		ensure!(
			page < EraInfo::<T>::get_page_count(era, &validator_stash),
			Error::<T>::InvalidPage.with_weight(T::WeightInfo::payout_stakers_alive_staked(0))
		);

		// Note: if era has no reward to be claimed, era may be future. It's better to not update
		// `ledger.legacy_claimed_rewards` in this case.
		let era_payout = <ErasValidatorReward<T>>::get(&era).ok_or_else(|| {
			Error::<T>::InvalidEraToReward
				.with_weight(T::WeightInfo::payout_stakers_alive_staked(0))
		})?;

		let account = StakingAccount::Stash(validator_stash.clone());
		let mut ledger = Self::ledger(account.clone()).or_else(|_| {
			if StakingLedger::<T>::is_bonded(account) {
				Err(Error::<T>::NotController.into())
			} else {
				Err(Error::<T>::NotStash.with_weight(T::WeightInfo::payout_stakers_alive_staked(0)))
			}
		})?;

		// clean up older claimed rewards
		ledger
			.legacy_claimed_rewards
			.retain(|&x| x >= current_era.saturating_sub(history_depth));
		ledger.clone().update()?;

		let stash = ledger.stash.clone();
```

**File:** substrate/frame/staking/src/pallet/impls.rs (L307-337)
```rust
		let exposure = EraInfo::<T>::get_paged_exposure(era, &stash, page).ok_or_else(|| {
			Error::<T>::InvalidEraToReward
				.with_weight(T::WeightInfo::payout_stakers_alive_staked(0))
		})?;

		// Input data seems good, no errors allowed after this point

		// Get Era reward points. It has TOTAL and INDIVIDUAL
		// Find the fraction of the era reward that belongs to the validator
		// Take that fraction of the era's rewards to split to nominator and validator
		//
		// Then look at the validator, figure out the proportion of their reward
		// which goes to them and each of their nominators.

		let era_reward_points = <ErasRewardPoints<T>>::get(&era);
		let total_reward_points = era_reward_points.total;
		let validator_reward_points =
			era_reward_points.individual.get(&stash).copied().unwrap_or_else(Zero::zero);

		// Nothing to do if they have no reward points.
		if validator_reward_points.is_zero() {
			return Ok(Some(T::WeightInfo::payout_stakers_alive_staked(0)).into());
		}

		// This is the fraction of the total reward that the validator and the
		// nominators will get.
		let validator_total_reward_part =
			Perbill::from_rational(validator_reward_points, total_reward_points);

		// This is how much validator + nominators are entitled to.
		let validator_total_payout = validator_total_reward_part * era_payout;
```
