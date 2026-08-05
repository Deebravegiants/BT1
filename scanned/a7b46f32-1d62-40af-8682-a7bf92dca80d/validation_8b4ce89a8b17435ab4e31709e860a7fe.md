Based on my analysis, I found a direct analog of the Biconomy precision-loss vulnerability in the `pallet-asset-rewards` pallet.

### Title
Reward-per-token calculation loses rewards to precision truncation when `total_tokens_staked` is large relative to `reward_rate_per_block` - (File: `substrate/frame/asset-rewards/src/lib.rs`)

### Summary
`pallet-asset-rewards` computes a running `reward_per_token_stored` accumulator, analogous to Biconomy's `accTokenPerShare`. The accumulator update divides `reward_rate_per_block * blocks_elapsed * PRECISION_SCALING_FACTOR` by `total_tokens_staked`, where `PRECISION_SCALING_FACTOR` is a fixed constant of only `4096`. [1](#0-0)  Because the scaling factor is a small fixed constant independent of the token's decimals or the size of the stake, once `total_tokens_staked` grows large relative to the per-block reward numerator, integer division rounds the result down to `0`, exactly the same failure mode described in the Biconomy report where `ACC_TOKEN_PRECISION / totalSharesStaked` rounds to zero.

### Finding Description
The core computation is in `reward_per_token`:

```rust
Ok(pool_info.reward_per_token_stored.ensure_add(
    pool_info
        .reward_rate_per_block
        .ensure_mul(rewardable_blocks_elapsed.into())?
        .ensure_mul(PRECISION_SCALING_FACTOR.into())?
        .ensure_div(pool_info.total_tokens_staked)?,
)?)
``` [2](#0-1) 

`total_tokens_staked` is simply the pool's `PoolInfo::total_tokens_staked` field, which increases whenever any unprivileged user calls `stake` on the pool (it is `RewardsPool::total_tokens_staked` maintained inside `PoolInfo`). [3](#0-2)  There is no privileged control over this quantity from the reward-accounting perspective—any staker or combination of stakers increasing the pool's staked balance drives it up.

`ensure_mul`/`ensure_div` only guard against arithmetic *overflow*; they do not guard against precision loss from integer division rounding to zero, so `ensure_div` here happily returns `Ok(0)` when the numerator is smaller than the denominator. This is functionally identical to the Biconomy bug: `PRECISION_SCALING_FACTOR` (4096, i.e. `2^12`) plays the same role as `ACC_TOKEN_PRECISION`, and it is drastically smaller than typical `Balance` magnitudes (`u128`, with staked amounts routinely reaching `1e18`-`1e30` for 18-decimal assets).

The `derive_rewards` function similarly divides by `PRECISION_SCALING_FACTOR` after multiplying by the staker's `amount`, so if `reward_per_token` never advances (stuck at the previous non-zero value because the delta rounds to zero), stakers who join later or accrue over many small blocks can have their entire reward window silently rounded to zero. [4](#0-3) 

### Impact Explanation
When `reward_rate_per_block * rewardable_blocks_elapsed * 4096 < total_tokens_staked`, the incremental `reward_per_token` contribution for that period truncates to `0`. Because `reward_per_token_stored` (and therefore `last_update_block`) is updated regardless of whether the increment was zero, that period's rewards are permanently lost — they are not carried over or recovered in a later update, since the elapsed-block window used to compute the increment has already been consumed. This causes stakers to lose all or a majority of their rewards despite a properly funded pool, matching the "High" severity impact class described in the original report (silent, permanent loss of user funds/rewards due to precision truncation).

### Likelihood Explanation
This does not require any privileged action — any user can call `stake` on a pool to increase `total_tokens_staked`, and the pool creator (also just a permissioned-but-not-privileged-over-users role) sets `reward_rate_per_block` at pool creation. [5](#0-4)  Given `PRECISION_SCALING_FACTOR` is a small fixed constant (`4096`) irrespective of the `Balance` type's magnitude (`u128` values commonly reach `1e18`+ for 18-decimal assets), the rounding-to-zero condition is easily reachable under realistic reward-rate/stake-size combinations, not merely a theoretical edge case.

### Recommendation
Increase `PRECISION_SCALING_FACTOR` substantially (e.g., to `1e18` or similar, scaled relative to the expected `Balance` type range) or switch the reward-per-token computation to a wider intermediate type (e.g., `U256`) analogous to how `pallet-nomination-pools` uses `T::BalanceToU256`/`T::U256ToBalance` conversions in `balance_to_point`/`point_to_balance` to avoid this exact class of truncation. [6](#0-5)  Alternatively, accumulate the un-scaled remainder so it is not silently dropped, or track/report when a reward-per-token increment truncates to zero.

### Proof of Concept
1. Pool created with `reward_rate_per_block = 10 * 10^18` (10 reward tokens/block, 18 decimals).
2. Multiple stakers cumulatively `stake` `1_000_000 * 10^18` staking tokens into the pool (`total_tokens_staked = 1e24`), a realistic amount for an 18-decimal asset.
3. One block elapses; `reward_per_token` computes:
   `numerator = 10e18 * 1 * 4096 = 4.096e22`
   `denominator = 1e24`
   `4.096e22 / 1e24 = 0` (integer division truncates).
4. `reward_per_token_stored` does not advance for that block even though real rewards were emitted into the pool's reward account; the elapsed-block window has been consumed via `last_update_block` advancing, so that reward interval's payout is unrecoverable.
5. Any staker calling `harvest_rewards` (which triggers `update_pool_and_staker_rewards` → `derive_rewards`) receives `0` reward for that period despite holding stake in a funded pool. [7](#0-6)

### Citations

**File:** substrate/frame/asset-rewards/src/lib.rs (L117-118)
```rust
/// Multiplier to maintain precision when calculating rewards.
pub(crate) const PRECISION_SCALING_FACTOR: u16 = 4096;
```

**File:** substrate/frame/asset-rewards/src/lib.rs (L146-167)
```rust
/// The state and configuration of an incentive pool.
#[derive(Debug, Clone, Decode, Encode, Default, PartialEq, Eq, MaxEncodedLen, TypeInfo)]
pub struct PoolInfo<AccountId, AssetId, Balance, BlockNumber> {
	/// The asset staked in this pool.
	staked_asset_id: AssetId,
	/// The asset distributed as rewards by this pool.
	reward_asset_id: AssetId,
	/// The amount of tokens rewarded per block.
	reward_rate_per_block: Balance,
	/// The block the pool will cease distributing rewards.
	expiry_block: BlockNumber,
	/// The account authorized to manage this pool.
	admin: AccountId,
	/// The total amount of tokens staked in this pool.
	total_tokens_staked: Balance,
	/// Total rewards accumulated per token, up to the `last_update_block`.
	reward_per_token_stored: Balance,
	/// Last block number the pool was updated.
	last_update_block: BlockNumber,
	/// The account that holds the pool's rewards.
	account: AccountId,
}
```

**File:** substrate/frame/asset-rewards/src/lib.rs (L754-824)
```rust
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

		/// Computes update pool reward state.
		///
		/// Should be called every time the pool is adjusted, and a staker is not involved.
		///
		/// Returns the updated pool and staker info.
		///
		/// NOTE: this function has no side-effects. Side-effects such as storage modifications are
		/// the responsibility of the caller.
		pub fn update_pool_rewards(
			pool_info: &PoolInfoFor<T>,
			reward_per_token: T::Balance,
		) -> Result<PoolInfoFor<T>, DispatchError> {
			let mut new_pool_info = pool_info.clone();
			new_pool_info.last_update_block = T::BlockNumberProvider::current_block_number();
			new_pool_info.reward_per_token_stored = reward_per_token;

			Ok(new_pool_info)
		}

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

**File:** substrate/frame/asset-rewards/src/lib.rs (L843-881)
```rust
	fn create_pool(
		creator: &T::AccountId,
		staked_asset_id: T::AssetId,
		reward_asset_id: T::AssetId,
		reward_rate_per_block: T::Balance,
		expiry: DispatchTime<BlockNumberFor<T>>,
		admin: &T::AccountId,
	) -> Result<PoolId, DispatchError> {
		// Ensure the assets exist.
		ensure!(T::Assets::asset_exists(staked_asset_id.clone()), Error::<T>::NonExistentAsset);
		ensure!(T::Assets::asset_exists(reward_asset_id.clone()), Error::<T>::NonExistentAsset);

		// Check the expiry block.
		let now = T::BlockNumberProvider::current_block_number();
		let expiry_block = expiry.evaluate(now);
		ensure!(expiry_block > now, Error::<T>::ExpiryBlockMustBeInTheFuture);

		let pool_id = NextPoolId::<T>::try_mutate(|id| -> Result<PoolId, DispatchError> {
			let current_id = *id;
			*id = id.ensure_add(1)?;
			Ok(current_id)
		})?;

		let footprint = Self::pool_creation_footprint();
		let cost = T::Consideration::new(creator, footprint)?;
		PoolCost::<T>::insert(pool_id, (creator.clone(), cost));

		// Create the pool.
		let pool = PoolInfoFor::<T> {
			staked_asset_id: staked_asset_id.clone(),
			reward_asset_id: reward_asset_id.clone(),
			reward_rate_per_block,
			total_tokens_staked: 0u32.into(),
			reward_per_token_stored: 0u32.into(),
			last_update_block: 0u32.into(),
			expiry_block,
			admin: admin.clone(),
			account: Self::pool_account_id(&pool_id),
		};
```

**File:** substrate/frame/nomination-pools/src/lib.rs (L3475-3499)
```rust
	fn balance_to_point(
		current_balance: BalanceOf<T>,
		current_points: BalanceOf<T>,
		new_funds: BalanceOf<T>,
	) -> BalanceOf<T> {
		let u256 = T::BalanceToU256::convert;
		let balance = T::U256ToBalance::convert;
		match (current_balance.is_zero(), current_points.is_zero()) {
			(_, true) => new_funds.saturating_mul(POINTS_TO_BALANCE_INIT_RATIO.into()),
			(true, false) => {
				// The pool was totally slashed.
				// This is the equivalent of `(current_points / 1) * new_funds`.
				new_funds.saturating_mul(current_points)
			},
			(false, false) => {
				// Equivalent to (current_points / current_balance) * new_funds
				balance(
					u256(current_points)
						.saturating_mul(u256(new_funds))
						// We check for zero above
						.div(u256(current_balance)),
				)
			},
		}
	}
```
