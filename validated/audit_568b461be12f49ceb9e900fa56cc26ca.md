Audit Report

## Title
Reward accrual in `pallet-asset-rewards` can be forced to permanently truncate to zero via single-block `reward_per_token` spam - (File: `substrate/frame/asset-rewards/src/lib.rs`)

## Summary
`reward_per_token` computes `reward_per_token_stored + reward_rate_per_block * rewardable_blocks_elapsed * PRECISION_SCALING_FACTOR / total_tokens_staked` using floor integer division, and `last_update_block` is reset to `now` on every call to `update_pool_rewards`, which is invoked from every `stake`, `unstake`, and `harvest_rewards` extrinsic. An unprivileged account can call `stake(pool_id, 0)` (a legal no-op) or `harvest_rewards` every block to keep `rewardable_blocks_elapsed` pinned at `1`, and whenever `reward_rate_per_block * 1 * PRECISION_SCALING_FACTOR < total_tokens_staked`, the reward increment truncates to zero, halting reward accrual for as long as the spam continues.

## Finding Description
`reward_per_token` is defined at [1](#0-0) , computing the elapsed-block delta and multiplying by a fixed `PRECISION_SCALING_FACTOR` of `4096` before dividing by `total_tokens_staked`, using `ensure_mul`/`ensure_div`, which perform standard (floor/truncating) integer arithmetic. `update_pool_rewards` resets `last_update_block` to the current block on every invocation [2](#0-1) , and this is called from `update_pool_and_staker_rewards`, which itself is invoked unconditionally at the start of `stake` [3](#0-2)  and `harvest_rewards` [4](#0-3) . Neither extrinsic enforces a minimum `amount` or minimum call interval — `stake` accepts `amount = 0` from any signed account, and `harvest_rewards` can be called by the staker themselves on every block without restriction. Consequently, an attacker can force `rewardable_blocks_elapsed` to always equal `1`, and when `reward_rate_per_block * 4096 < total_tokens_staked`, the added term in `reward_per_token` floors to `0`, so `reward_per_token_stored` never advances while the spam continues. This directly parallels the cited `LiquidityGauge._checkpoint` rounding-to-zero pattern, substituting `dt` (time delta) with `rewardable_blocks_elapsed` (block delta).

## Impact Explanation
While the attacker sustains per-block calls, all stakers in an affected pool (one where `reward_rate_per_block * 4096 < total_tokens_staked`, an easily reachable configuration for pools with modest reward rates or large stake totals) receive zero reward accrual, confirmed by `derive_rewards`'s dependence on the frozen `reward_per_token` value [5](#0-4) . This is a real accounting/availability defect in the pallet's reward-distribution logic, not a hypothetical rounding nuance, since the effect is deterministic and reproducible given the stated configuration.

## Likelihood Explanation
The attack requires no privileged role — `stake` and `harvest_rewards` are plain signed extrinsics reachable by any account — and costs only ordinary per-block transaction fees, which must be paid continuously for the freeze to persist (the freeze ends as soon as the attacker stops submitting transactions, since `rewardable_blocks_elapsed` will then exceed 1 and the reward calculation resumes normal accrual). This makes the attack a sustained-cost griefing vector rather than a one-time exploit, but it remains realistically executable by any account against pools with the described rate/stake ratio, which is plausible in normal pool configurations since `PRECISION_SCALING_FACTOR` is fixed at a small `4096` rather than a high-precision fixed-point scale (contrast with `pallet-nomination-pools`'s `FixedU128`-based reward counter).

## Recommendation
Short term: increase `PRECISION_SCALING_FACTOR` substantially (e.g., to a `FixedU128`-comparable magnitude) or switch `reward_per_token` accounting to a fixed-point type as used in `pallet-nomination-pools`'s `current_reward_counter`, so single-block increments do not systematically truncate to zero for realistic `reward_rate_per_block` / `total_tokens_staked` ratios. Consider also carrying forward truncation remainders (a "dust" accumulator) so no reward is permanently lost even under adversarial per-block interaction patterns.

Long term: add tests that specifically simulate an attacker calling `stake(pool_id, 0)` / `harvest_rewards` every block over long durations and assert that `reward_per_token_stored` still converges to the expected value.

## Proof of Concept
1. Call `create_pool` with `reward_rate_per_block = R` and stake such that `total_tokens_staked = S` satisfies `R * 4096 < S` (e.g., `R = 1`, `S = 5000`).
2. Have any signed account call `stake(pool_id, 0)` (or `harvest_rewards`) in every subsequent block.
3. Because `update_pool_and_staker_rewards` resets `last_update_block` to `now` each call, `rewardable_blocks_elapsed` in `reward_per_token` is always `1`, and `reward_rate_per_block * 1 * 4096 / total_tokens_staked` floors to `0` per the code at `substrate/frame/asset-rewards/src/lib.rs:803-809`.
4. `reward_per_token_stored` never increases while the spam continues; legitimate stakers calling `harvest_rewards` receive `0` per `derive_rewards` at `substrate/frame/asset-rewards/src/lib.rs:815-824`.
5. A unit test asserting `Pools::<T>::get(pool_id).reward_per_token_stored` remains unchanged across N simulated blocks of `stake(pool_id, 0)` calls, followed by resumed accrual once spam stops, would demonstrate the effect.

### Citations

**File:** substrate/frame/asset-rewards/src/lib.rs (L472-502)
```rust
		#[pallet::call_index(1)]
		pub fn stake(origin: OriginFor<T>, pool_id: PoolId, amount: T::Balance) -> DispatchResult {
			let staker = ensure_signed(origin)?;

			// Always start by updating staker and pool rewards.
			let pool_info = Pools::<T>::get(pool_id).ok_or(Error::<T>::NonExistentPool)?;
			let staker_info = PoolStakers::<T>::get(pool_id, &staker).unwrap_or_default();
			let (mut pool_info, mut staker_info) =
				Self::update_pool_and_staker_rewards(&pool_info, &staker_info)?;

			T::AssetsFreezer::increase_frozen(
				pool_info.staked_asset_id.clone(),
				&FreezeReason::Staked.into(),
				&staker,
				amount,
			)?;

			// Update Pools.
			pool_info.total_tokens_staked.ensure_add_assign(amount)?;

			Pools::<T>::insert(pool_id, pool_info);

			// Update PoolStakers.
			staker_info.amount.ensure_add_assign(amount)?;
			PoolStakers::<T>::insert(pool_id, &staker, staker_info);

			// Emit event.
			Self::deposit_event(Event::Staked { staker, pool_id, amount });

			Ok(())
		}
```

**File:** substrate/frame/asset-rewards/src/lib.rs (L568-585)
```rust
		#[pallet::call_index(3)]
		pub fn harvest_rewards(
			origin: OriginFor<T>,
			pool_id: PoolId,
			staker: Option<T::AccountId>,
		) -> DispatchResult {
			let caller = ensure_signed(origin)?;
			let staker = staker.unwrap_or(caller.clone());

			// Always start by updating the pool and staker rewards.
			let pool_info = Pools::<T>::get(pool_id).ok_or(Error::<T>::NonExistentPool)?;
			let now = T::BlockNumberProvider::current_block_number();
			ensure!(now > pool_info.expiry_block || caller == staker, BadOrigin);

			let staker_info =
				PoolStakers::<T>::get(pool_id, &staker).ok_or(Error::<T>::NonExistentStaker)?;
			let (pool_info, mut staker_info) =
				Self::update_pool_and_staker_rewards(&pool_info, &staker_info)?;
```

**File:** substrate/frame/asset-rewards/src/lib.rs (L775-784)
```rust
		pub fn update_pool_rewards(
			pool_info: &PoolInfoFor<T>,
			reward_per_token: T::Balance,
		) -> Result<PoolInfoFor<T>, DispatchError> {
			let mut new_pool_info = pool_info.clone();
			new_pool_info.last_update_block = T::BlockNumberProvider::current_block_number();
			new_pool_info.reward_per_token_stored = reward_per_token;

			Ok(new_pool_info)
		}
```

**File:** substrate/frame/asset-rewards/src/lib.rs (L786-810)
```rust
		/// Derives the current reward per token for this pool.
		pub(super) fn reward_per_token(
			pool_info: &PoolInfoFor<T>,
		) -> Result<T::Balance, DispatchError> {
			if pool_info.total_tokens_staked.is_zero() {
				return Ok(pool_info.reward_per_token_stored);
			}

			let rewardable_blocks_elapsed: u32 =
				match Self::last_block_reward_applicable(pool_info.expiry_block)
					.ensure_sub(pool_info.last_update_block)?
					.try_into()
				{
					Ok(b) => b,
					Err(_) => return Err(Error::<T>::BlockNumberConversionError.into()),
				};

			Ok(pool_info.reward_per_token_stored.ensure_add(
				pool_info
					.reward_rate_per_block
					.ensure_mul(rewardable_blocks_elapsed.into())?
					.ensure_mul(PRECISION_SCALING_FACTOR.into())?
					.ensure_div(pool_info.total_tokens_staked)?,
			)?)
		}
```

**File:** substrate/frame/asset-rewards/src/lib.rs (L812-824)
```rust
		/// Derives the amount of rewards earned by a staker.
		///
		/// This is a helper function for `update_pool_rewards` and should not be called directly.
		fn derive_rewards(
			staker_info: &PoolStakerInfo<T::Balance>,
			reward_per_token: &T::Balance,
		) -> Result<T::Balance, DispatchError> {
			Ok(staker_info
				.amount
				.ensure_mul(reward_per_token.ensure_sub(staker_info.reward_per_token_paid)?)?
				.ensure_div(PRECISION_SCALING_FACTOR.into())?
				.ensure_add(staker_info.rewards)?)
		}
```
