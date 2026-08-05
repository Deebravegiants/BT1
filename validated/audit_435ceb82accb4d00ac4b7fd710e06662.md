Audit Report

## Title
Lost/misallocated rewards when `total_tokens_staked` is `0` in `pallet-asset-rewards` - (File: substrate/frame/asset-rewards/src/lib.rs)

## Summary
`pallet-asset-rewards`'s `reward_per_token()` freezes `reward_per_token_stored` when `total_tokens_staked` is zero, but `update_pool_rewards()` unconditionally advances `last_update_block` to the current block regardless of whether any tokens were staked. This desynchronizes the two state variables and causes any reward emission accrued during a zero-stake window to be permanently skipped rather than deferred.

## Finding Description
The root cause is confirmed directly in the code. `reward_per_token()` short-circuits and returns the stored value unchanged when supply is zero: [1](#0-0) 

But `update_pool_and_staker_rewards()` always calls `update_pool_rewards()` next, which unconditionally sets `last_update_block` to the current block irrespective of the zero-stake short-circuit: [2](#0-1) 

`create_pool()` initializes `total_tokens_staked: 0`, `reward_per_token_stored: 0`, `last_update_block: 0` while immediately setting a non-zero `reward_rate_per_block` and future `expiry_block`, with no requirement that staking begin immediately: [3](#0-2) 

`set_pool_reward_rate_per_block()` follows the identical `reward_per_token` → `update_pool_rewards` pattern with the same flaw: [4](#0-3) 

There is no guard in `create_pool`, `stake`, or `set_pool_reward_rate_per_block` requiring `total_tokens_staked > 0` before reward accrual is considered active, nor any mechanism to defer/reset `last_update_block` to the point of first stake. This matches the classic Synthetix/MasterChef-style "reward-per-token" pattern flaw where `lastUpdateBlock` advancing without corresponding `rewardPerTokenStored` accrual causes reward loss for that window.

## Impact Explanation
Any reward emission that would have accrued during a window where `total_tokens_staked == 0` (e.g., between `create_pool` and the first `stake`, or after all stakers fully unstake and before the next stake) is never reflected in `reward_per_token_stored`, and thus can never be credited to any staker via `derive_rewards`/`harvest_rewards`. The reward tokens intended for that window remain stranded in the pool's pot account (`pool_info.account`). Recovery via `cleanup_pool` requires zero stakers: [5](#0-4) 
Once a staker joins, this recovery path is unavailable until the pool empties again, so the tokens are effectively stuck/misallocated for the pool's remaining lifetime. This is an accounting/fairness defect resulting in stuck funds and unfair reward distribution, not a direct fund-theft or insolvency vector.

## Likelihood Explanation
This does not require an attacker; it is triggered by ordinary, expected operational sequencing. Any pool where `reward_rate_per_block` is configured at creation before the first staker arrives (a normal onboarding gap), or any pool that is fully unstaked and later re-staked, will trigger the loss. No privileged bypass or unusual configuration is needed on the staking side (`stake` is open to any account), only that pool creation/admin-rate-setting (permissioned) precedes staker activity, which is the typical lifecycle for such reward pools.

## Recommendation
Do not advance `last_update_block` when `total_tokens_staked.is_zero()`, so the reward window is deferred rather than lost — i.e., mirror the freeze of `reward_per_token_stored` by also freezing `last_update_block` in `update_pool_rewards` (or handle this specifically in `reward_per_token`/`update_pool_rewards` for the zero-supply case). This covers both the initial-deposit gap and the "everyone unstakes mid-life" case.

## Proof of Concept
1. Privileged account calls `create_pool` with `reward_rate_per_block = R` and `expiry_block = E` at block `N`; pool state becomes `total_tokens_staked = 0`, `reward_per_token_stored = 0`, `last_update_block = N` (per `create_pool`, lines 870-884).
2. No stake occurs for `K` blocks.
3. At block `N+K`, a staker calls `stake()`, invoking `update_pool_and_staker_rewards` → `reward_per_token()`, which returns unchanged `reward_per_token_stored = 0` (lines 790-792) since `total_tokens_staked.is_zero()`; then `update_pool_rewards` sets `last_update_block = N+K` (line 780).
4. The `K` blocks' worth of `R * K` reward tokens are never reflected in `reward_per_token_stored` and can never be claimed by any staker; they remain in `pool_info.account`, unrecoverable via `cleanup_pool` once a staker is present (lines 696-704).

### Citations

**File:** substrate/frame/asset-rewards/src/lib.rs (L696-704)
```rust
		#[pallet::call_index(8)]
		pub fn cleanup_pool(origin: OriginFor<T>, pool_id: PoolId) -> DispatchResult {
			let who = ensure_signed(origin)?;

			let pool_info = Pools::<T>::get(pool_id).ok_or(Error::<T>::NonExistentPool)?;
			ensure!(pool_info.admin == who, BadOrigin);

			let stakers = PoolStakers::<T>::iter_key_prefix(pool_id).next();
			ensure!(stakers.is_none(), Error::<T>::NonEmptyPool);
```

**File:** substrate/frame/asset-rewards/src/lib.rs (L754-784)
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
```

**File:** substrate/frame/asset-rewards/src/lib.rs (L786-792)
```rust
		/// Derives the current reward per token for this pool.
		pub(super) fn reward_per_token(
			pool_info: &PoolInfoFor<T>,
		) -> Result<T::Balance, DispatchError> {
			if pool_info.total_tokens_staked.is_zero() {
				return Ok(pool_info.reward_per_token_stored);
			}
```

**File:** substrate/frame/asset-rewards/src/lib.rs (L870-884)
```rust
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

		// Insert it into storage.
		Pools::<T>::insert(pool_id, pool);
```

**File:** substrate/frame/asset-rewards/src/lib.rs (L900-917)
```rust
	fn set_pool_reward_rate_per_block(
		admin: &T::AccountId,
		pool_id: PoolId,
		new_reward_rate_per_block: T::Balance,
	) -> DispatchResult {
		let pool_info = Pools::<T>::get(pool_id).ok_or(Error::<T>::NonExistentPool)?;
		ensure!(pool_info.admin == *admin, BadOrigin);
		ensure!(
			new_reward_rate_per_block > pool_info.reward_rate_per_block,
			Error::<T>::RewardRateCut
		);

		// Always start by updating the pool rewards.
		let rewards_per_token = Self::reward_per_token(&pool_info)?;
		let mut pool_info = Self::update_pool_rewards(&pool_info, rewards_per_token)?;

		pool_info.reward_rate_per_block = new_reward_rate_per_block;
		Pools::<T>::insert(pool_id, pool_info);
```
