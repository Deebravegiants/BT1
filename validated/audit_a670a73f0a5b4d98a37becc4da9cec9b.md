Audit Report

## Title
Nomination pool internal reward split dilutes long-term members via a batch, non-time-weighted `current_reward_counter` calculation - (File: `substrate/frame/nomination-pools/src/lib.rs`)

## Summary
`pallet-nomination-pools` distributes reward-account balance increases among the pool's *current* `bonded_points` in `current_reward_counter`, rather than weighting by how long those points existed while the reward was being earned. This allows an account to `join` the pool after a staking-era reward has already been fixed by `pallet-staking`'s exposure snapshot but before that reward is transferred into the pool's reward account and recorded, and subsequently claim a pro-rata share of a reward it did not help earn, at the expense of existing members.

## Finding Description
The reward split is computed in `current_reward_counter`, dividing `new_pending_rewards` by the `bonded_points` argument passed at call time: [1](#0-0) . `update_records`/`current_reward_counter` is invoked from `do_reward_payout` using the pool's *current* `bonded_pool.points` at the moment a member calls `claim_payout`: [2](#0-1) .

`join()` does call `update_records` with the *old* `bonded_pool.points` before adding the new member's points, which correctly settles any balance already present in the reward account against the old point base at join time: [3](#0-2) . This guard, however, only protects the instant of joining — it does not, and cannot, prevent a subsequent race: if the attacker joins *before* the era reward balance actually lands in the reward account (via a later, permissionless `payout_stakers`/`payout_stakers_by_page` call, confirmed permissionless by `payout_to_any_account_works`), then at the time `claim_payout` is eventually called, `bonded_pool.points` already includes the attacker's newly joined stake, and the freshly-landed reward balance is divided across that larger point total.

This is a structurally real characteristic of the pool's batch/lump-sum reward accounting model: rewards are split according to point-ownership at the moment the balance-increase is recorded, not weighted by exposure at the underlying era for which the reward was earned.

## Impact Explanation
If exploitable, this would let a newly joined member capture a share of rewards legitimately earned by long-term members' historical stake, diluting existing depositors. This is a value-misallocation issue between members, not a fund-safety break — no tokens are created or destroyed. This matches the impact class described in the claim (analogous to the Acala M-02 finding), bounded at most to a Medium-severity griefing/dilution issue rather than a critical fund-loss bug.

## Likelihood Explanation
Exploitation requires precise sequencing: the attacker must `join` with capital sized relative to the pool, before `payout_stakers`/`payout_stakers_by_page` is called for an already-fixed era reward, and then call `claim_payout` before other members do. The capital must actually be bonded through the pool's `join` extrinsic (unlike a flash loan), and while claiming the diluted reward itself requires no unbonding wait, fully exiting the position later requires the normal `unbond` + `bonding_duration` delay, incurring slashing/market exposure during that period. This mirrors the same economic caveats raised for the original Acala finding and is a real, though narrow and capital-constrained, dilution vector rather than a low-cost repeatable exploit.

I was not able to find any documentation, code comment, or existing test in the repository that explicitly acknowledges or excludes this specific "join before payout lands" race as intended behavior, nor a test that reproduces the exact sequence (`join` → `payout_stakers` → `claim_payout`) to confirm the magnitude of dilution in practice. The claim's code citations for `current_reward_counter`, `do_reward_payout`, and `join`'s `update_records` ordering are accurate and verified against the current source.

## Recommendation
Track a time- or era-boundary-aware contribution measure for `bonded_points`, so that a member's share of a specific reward increment is proportional to points held while that increment was being earned by the underlying `pallet-staking` exposure, rather than points present when the increment is recorded by `current_reward_counter`/`update_records`. Alternatively, delay new joiners' points from counting toward reward-splitting until the next era boundary after joining, mirroring how `pallet-staking`'s own era exposure snapshot already excludes late joiners from that era's payout.

## Proof of Concept
1. Pool has member A with `points = P`; reward pool balance is `0`; `last_recorded_total_payouts = X`.
2. An era's staking reward `R`, earned entirely by A's historical exposure, is fixed by `pallet-staking`'s exposure snapshot (`EraInfo::<T>::get_paged_exposure`) but not yet paid into the pool's reward account.
3. Attacker calls `join(amount = P)`, doubling `bonded_pool.points` to `2P`; `update_records` runs first with the old `P` and a zero pending balance, so no dilution occurs at this step (confirmed at `substrate/frame/nomination-pools/src/lib.rs` L2139-2149).
4. Anyone (permissionless, per `payout_to_any_account_works`) calls `payout_stakers`/`payout_stakers_by_page` for the previously fixed era, transferring `R` into the pool's reward account.
5. Attacker calls `claim_payout`, triggering `do_reward_payout` → `current_reward_counter`, which computes `new_pending_rewards ≈ R` and divides by `bonded_points = 2P` (now including the attacker), crediting the attacker ~`R/2` despite having zero exposure during the era `R` was earned in (confirmed at `substrate/frame/nomination-pools/src/lib.rs` L1450-1511 and L3527-3546).

A concrete unit test reproducing steps 1–5 in the `pallet-nomination-pools` mock runtime (bond A, advance era, compute era payout, `join` with attacker, call `payout_stakers_by_page`, call `claim_payout` from attacker, and assert the attacker's received amount is non-trivially greater than what their post-join exposure alone would justify) would be required to fully confirm the magnitude and repeatability of this dilution in practice.

### Citations

**File:** substrate/frame/nomination-pools/src/lib.rs (L1450-1467)
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
```

**File:** substrate/frame/nomination-pools/src/lib.rs (L2139-2149)
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
			let points_issued = bonded_pool.try_bond_funds(&who, amount, BondType::Extra)?;
```

**File:** substrate/frame/nomination-pools/src/lib.rs (L3527-3546)
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
```
