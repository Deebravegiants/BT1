Based on my investigation, I found a genuine structural analog of the Acala M-02 accounting flaw in `pallet-nomination-pools`, distinct from `pallet-asset-rewards` (which is immune because it uses genuine Synthetix-style continuous per-block accrual that locks in `reward_per_token` *before* any stake change is applied — see `update_pool_and_staker_rewards` at [1](#0-0) ).

### Title
Nomination pool internal reward split dilutes long-term members with a batch, non-time-weighted `current_reward_counter` calculation - (File: `substrate/frame/nomination-pools/src/lib.rs`)

### Summary
`pallet-nomination-pools` wraps a single bonded/nominating account whose era-level staking payout is fixed by the underlying `pallet-staking` exposure snapshot taken at era start, and cannot itself be sandwiched [2](#0-1) . However, once that fixed era payout lands as a lump balance increase in the pool's *reward account*, the pool's internal distribution logic (`RewardPool::current_reward_counter` / `update_records`) splits the newly-observed balance increase among whichever `bonded_points` exist at the moment the split is computed — not weighted by how long those points existed while the reward was actually being earned.

### Finding Description
The core division happens in `current_reward_counter`: [3](#0-2) 

```
let current_payout_balance = balance...saturating_sub(self.last_recorded_total_payouts);
...
let new_pending_rewards = current_payout_balance.saturating_sub(new_pending_commission);
```
and [4](#0-3) 

`new_pending_rewards` is divided by `bonded_points`, the *current* total points argument passed in at call time, exactly analogous to Acala's `total_shares` denominator in `accumulate_incentives`.

`update_records` is invoked from every points-changing extrinsic (`join`, `bond_extra`, `unbond`) using the points value that existed *before* the caller's own change is applied — e.g. in `join()`: [5](#0-4) 

This correctly excludes the *joining* call's own new points from that specific division. But it does **not** protect against the general race: between the moment `pallet-staking`'s era exposure is snapshotted (fixing who "earned" that era's reward) and the moment the pool's `payout_stakers`/`payout_stakers_by_page` call actually transfers that era reward into the pool's reward account [6](#0-5) , any account can permissionlessly `join` the pool. Since `payout_stakers`/`payout_stakers_by_page` is itself callable by anyone (see `payout_to_any_account_works` test) [7](#0-6) , an attacker can:

1. `join` the pool with a large deposit (their stake is *not* part of the already-snapshotted era exposure, so it doesn't add to the payout amount).
2. Immediately trigger `payout_stakers`/`payout_stakers_by_page` to push the fixed era reward into the pool's reward account.
3. Call an action that triggers `do_reward_payout` (e.g. `claim_payout`), where `current_reward_counter` splits that just-landed balance across `bonded_pool.points`, which now includes the attacker's freshly-added stake: [8](#0-7) 

The attacker thereby captures a pro-rata share of a reward that was earned entirely by pre-existing members' historical stake, diluting long-term depositors — the same accounting pattern as Acala's `accumulate_incentives`/`total_shares` split.

### Impact Explanation
Long-term pool members receive a smaller share of legitimately earned staking rewards because newly-joined capital, contributed only after the reward-generating era's exposure was fixed, is counted in the denominator at payout-recording time. This is a value leak/MEV-style griefing vector against nomination-pool depositors, not a fund-safety break (no funds are created or destroyed, only misallocated between members) — matching the "Medium" classification given to the original Acala finding.

### Likelihood Explanation
Exploitation requires: (a) capital sized relative to the pool to meaningfully dilute the split, (b) `join`/`payout_stakers`/`claim_payout` calls executed in quick succession, and (c) the attacker's capital being briefly bonded to the underlying staking system via the pool (no unbonding period is required to *earn* the diluted share via `claim_payout`, only to fully exit). Unlike a flash loan, funds must be actually bonded through nomination-pools' `join`, and exiting later requires the normal `unbond` + `bonding_duration` wait, similar to the economic-cost caveats Acala's team raised in their dispute of the original M-02 (capital lockup, opportunity cost, price/slashing exposure). This mirrors exactly the reasoning that led the original finding to be judged a valid, but bounded, Medium rather than Critical/High severity.

### Recommendation
Track a time-weighted (or era-boundary-aware) contribution measure for `bonded_points` so that a member's share of a specific reward increment is proportional to the points they held while that increment was being earned, rather than the points present at the moment the increment is recorded. Alternatively, gate `update_records`/reward crediting so that newly bonded points only start accruing from the *next* era boundary after joining, consistent with how `pallet-staking`'s own exposure snapshot already excludes late joiners from that era's payout — closing the internal-accounting gap that currently lets pool-level points dilute rewards earned before they existed.

### Proof of Concept
Conceptually (mirroring the Acala PoC's diff pattern):
1. Pool has member A with `points = P`, reward pool balance `= 0`, `last_recorded_total_payouts = X`.
2. Attacker calls `join` with `amount = P` (doubling `bonded_pool.points` to `2P`); `update_records` runs first with the *old* `P`, so no dilution yet, `last_recorded_reward_counter` unaffected (balance hasn't changed).
3. Anyone calls `payout_stakers`/`payout_stakers_by_page` for a previously-fixed era exposure (earned entirely by A's historical stake) — reward account balance increases by `R`.
4. Attacker calls `claim_payout` (triggers `do_reward_payout` → `current_reward_counter`), which computes `new_pending_rewards = R`, divides by `bonded_points = 2P` (now including attacker), crediting attacker `~R/2` despite having zero historical exposure for era `R` was earned in. [9](#0-8) [10](#0-9)

### Citations

**File:** substrate/frame/asset-rewards/src/lib.rs (L746-765)
```rust
		/// Computes update pool and staker reward state.
		///
		/// Should be called prior to any operation involving a staker.
		///
		/// Returns the updated pool and staker info.
		///
		/// NOTE: this function has no side-effects. Side-effects such as storage modifications are
		/// the responsibility of the caller.
		pub fn update_pool_and_staker_rewards(
			pool_info: &PoolInfoFor<T>,
			staker_info: &PoolStakerInfo<T::Balance>,
		) -> Result<(PoolInfoFor<T>, PoolStakerInfo<T::Balance>), DispatchError> {
			let reward_per_token = Self::reward_per_token(&pool_info)?;
			let pool_info = Self::update_pool_rewards(pool_info, reward_per_token)?;

			let mut new_staker_info = staker_info.clone();
			new_staker_info.rewards = Self::derive_rewards(&staker_info, &reward_per_token)?;
			new_staker_info.reward_per_token_paid = pool_info.reward_per_token_stored;
			return Ok((pool_info, new_staker_info));
		}
```

**File:** substrate/frame/staking/src/pallet/impls.rs (L253-282)
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

```

**File:** substrate/frame/staking/src/pallet/impls.rs (L307-322)
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
```

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

**File:** substrate/frame/nomination-pools/src/lib.rs (L2139-2148)
```rust
			let mut reward_pool = RewardPools::<T>::get(pool_id)
				.defensive_ok_or::<Error<T>>(DefensiveError::RewardPoolNotFound.into())?;
			// IMPORTANT: reward pool records must be updated with the old points.
			reward_pool.update_records(
				pool_id,
				bonded_pool.points,
				bonded_pool.commission.current(),
			)?;

			bonded_pool.try_inc_members()?;
```

**File:** substrate/frame/nomination-pools/src/lib.rs (L3527-3571)
```rust
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

**File:** substrate/frame/staking/src/tests.rs (L4412-4438)
```rust
#[test]
fn payout_to_any_account_works() {
	ExtBuilder::default().has_stakers(false).build_and_execute(|| {
		let balance = 1000;
		// Create a validator:
		bond_validator(11, balance); // Default(64)

		// Create a stash/controller pair
		bond_nominator(1234, 100, vec![11]);

		// Update payout location
		assert_ok!(Staking::set_payee(RuntimeOrigin::signed(1234), RewardDestination::Account(42)));

		// Reward Destination account doesn't exist
		assert_eq!(asset::stakeable_balance::<Test>(&42), 0);

		mock::start_active_era(1);
		Staking::reward_by_ids(vec![(11, 1)]);
		// compute and ensure the reward amount is greater than zero.
		let _ = current_total_payout_for_duration(reward_time_per_era());
		mock::start_active_era(2);
		assert_ok!(Staking::payout_stakers_by_page(RuntimeOrigin::signed(1337), 11, 1, 0));

		// Payment is successful
		assert!(asset::stakeable_balance::<Test>(&42) > 0);
	})
}
```
