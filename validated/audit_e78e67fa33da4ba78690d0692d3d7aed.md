Audit Report

## Title
Permanent underflow DoS in `pallet-asset-rewards` freezes all staked funds and rewards once a pool's `last_update_block` is updated past `expiry_block` — (File: `substrate/frame/asset-rewards/src/lib.rs`)

## Summary
`update_pool_rewards` unconditionally stamps `last_update_block` with the raw, uncapped current block number, while `reward_per_token` assumes `last_update_block <= expiry_block` when it computes `last_block_reward_applicable(expiry_block).ensure_sub(last_update_block)`. Once any pool-mutating call executes after the pool's `expiry_block` (with nonzero `total_tokens_staked`), `last_update_block` is pushed past `expiry_block`, and every subsequent call to `stake`, `unstake`, `harvest_rewards`, `set_pool_reward_rate_per_block`, or `set_pool_expiry_block` on that pool permanently reverts with an arithmetic underflow.

## Finding Description
`update_pool_rewards` sets the checkpoint to the unclamped current block: [1](#0-0) 

`reward_per_token` computes elapsed blocks as `last_block_reward_applicable(expiry_block).ensure_sub(last_update_block)`, which is only valid while `last_update_block <= expiry_block`; `last_block_reward_applicable` clamps `now` to `expiry_block`: [2](#0-1) 

Trace:
1. Pool has `expiry_block = E`, nonzero `total_tokens_staked`, and `last_update_block = L0 <= E`.
2. First post-expiry call at block `N1 > E` (e.g. `unstake`): `reward_per_token` computes `E - L0` (valid, succeeds), then `update_pool_rewards` sets `last_update_block = N1` (uncapped, `> E`).
3. Any later call at `N2 > N1` on the same pool: `last_block_reward_applicable(E) = E`, then `E.ensure_sub(N1)` underflows because `N1 > E`, returning `Err(ArithmeticError)` and aborting the extrinsic.

All mutating entry points funnel through `reward_per_token`/`update_pool_rewards` before performing any other logic: [3](#0-2) [4](#0-3) [5](#0-4) 

The admin's remedies also call `reward_per_token` first and are equally bricked: [6](#0-5) [7](#0-6) 

The only escape is the early-return guard `if pool_info.total_tokens_staked.is_zero() { return Ok(pool_info.reward_per_token_stored); }`, but that branch is unreachable once the underflow has already blocked every `unstake` call that would reduce `total_tokens_staked` to zero — since even a full unstake first computes `reward_per_token` against the still-nonzero pre-unstake stake amount, which underflows before the stake amount is reduced.

## Impact Explanation
This is a complete, permanent denial of service for any affected pool: staked tokens remain frozen via `AssetsFreezer` with no way to `unstake`, and accrued/pending reward-asset balances become unreachable via `harvest_rewards`. Because the admin-only recovery calls (`set_pool_reward_rate_per_block`, `set_pool_expiry_block`) run through the identical `reward_per_token` path, there is no privileged or unprivileged path to un-stick the pool once triggered. This is a genuine, code-level accounting/arithmetic bug, not a privileged-only or governance-only issue, and results in concrete fund lock.

## Likelihood Explanation
No privilege or special setup is required. Any staker calling `unstake` or `harvest_rewards` after a pool's natural `expiry_block` — normal, expected usage — advances `last_update_block` past `expiry_block` and triggers the bug for all subsequent interactions with that pool. This makes the bug highly likely to occur organically for any pool that isn't manually extended with zero staked tokens/updates during the transition window.

## Recommendation
In `update_pool_rewards`, clamp the stored `last_update_block` to `Self::last_block_reward_applicable(pool_info.expiry_block)` instead of the raw current block number, mirroring the clamp already applied in `reward_per_token`.

## Proof of Concept
1. `create_pool` with `expiry_block = E` (e.g. block 25, matching the existing `DEFAULT_EXPIRE_AFTER` test fixture).
2. Staker `stake`s a nonzero amount before expiry.
3. Advance to a block `N1 > E` (e.g. 30) and call `unstake`/`harvest_rewards` for a partial amount (leaving `total_tokens_staked > 0`) — succeeds, sets `PoolInfo.last_update_block = 30`.
4. Advance to `N2 > N1` (e.g. 40) and call `stake`, `unstake`, `harvest_rewards`, `set_pool_reward_rate_per_block`, or `set_pool_expiry_block` on the same pool — `reward_per_token`'s `last_block_reward_applicable(25).ensure_sub(30)` computes `25 - 30`, underflows, and the call reverts with `ArithmeticError`.
5. Repeat step 4 with any other account or the admin — all calls revert identically, permanently locking staked funds and reward-asset balances in the pool.

This is a fully reachable, unprivileged-triggerable bug confirmed by direct code inspection of `substrate/frame/asset-rewards/src/lib.rs`; the repository's existing test suite does not appear to cover repeated calls spanning multiple blocks past `expiry_block`, so this underflow path is untested.

### Citations

**File:** substrate/frame/asset-rewards/src/lib.rs (L476-480)
```rust
			// Always start by updating staker and pool rewards.
			let pool_info = Pools::<T>::get(pool_id).ok_or(Error::<T>::NonExistentPool)?;
			let staker_info = PoolStakers::<T>::get(pool_id, &staker).unwrap_or_default();
			let (mut pool_info, mut staker_info) =
				Self::update_pool_and_staker_rewards(&pool_info, &staker_info)?;
```

**File:** substrate/frame/asset-rewards/src/lib.rs (L523-530)
```rust
			// Always start by updating the pool rewards.
			let pool_info = Pools::<T>::get(pool_id).ok_or(Error::<T>::NonExistentPool)?;
			let now = T::BlockNumberProvider::current_block_number();
			ensure!(now > pool_info.expiry_block || caller == staker, BadOrigin);

			let staker_info = PoolStakers::<T>::get(pool_id, &staker).unwrap_or_default();
			let (mut pool_info, mut staker_info) =
				Self::update_pool_and_staker_rewards(&pool_info, &staker_info)?;
```

**File:** substrate/frame/asset-rewards/src/lib.rs (L577-585)
```rust
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

**File:** substrate/frame/asset-rewards/src/lib.rs (L786-833)
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

		fn last_block_reward_applicable(pool_expiry_block: BlockNumberFor<T>) -> BlockNumberFor<T> {
			let now = T::BlockNumberProvider::current_block_number();
			if now < pool_expiry_block {
				now
			} else {
				pool_expiry_block
			}
		}
```

**File:** substrate/frame/asset-rewards/src/lib.rs (L912-917)
```rust
		// Always start by updating the pool rewards.
		let rewards_per_token = Self::reward_per_token(&pool_info)?;
		let mut pool_info = Self::update_pool_rewards(&pool_info, rewards_per_token)?;

		pool_info.reward_rate_per_block = new_reward_rate_per_block;
		Pools::<T>::insert(pool_id, pool_info);
```

**File:** substrate/frame/asset-rewards/src/lib.rs (L953-958)
```rust
		// Always start by updating the pool rewards.
		let reward_per_token = Self::reward_per_token(&pool_info)?;
		let mut pool_info = Self::update_pool_rewards(&pool_info, reward_per_token)?;

		pool_info.expiry_block = new_expiry_block;
		Pools::<T>::insert(pool_id, pool_info);
```
