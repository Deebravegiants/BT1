The code exactly matches the claim. I now have sufficient evidence to confirm all the cited code paths.

Audit Report

## Title
Reward Tokens Permanently Lost When Pool Has Zero Staked Tokens - (File: `substrate/frame/asset-rewards/src/lib.rs`)

## Summary
`pallet-asset-rewards` explicitly ports the Synthetix `StakingRewards.sol` reward algorithm, as documented in the pallet's module docs [1](#0-0) . Its `reward_per_token` function has the same zero-total-stake gap: when `pool_info.total_tokens_staked.is_zero()`, it returns the stale `reward_per_token_stored` without accruing anything for elapsed blocks, while `update_pool_rewards` unconditionally fast-forwards `last_update_block` to the current block [2](#0-1) . Since `last_block_reward_applicable` caps accrual only at the fixed `expiry_block` (never paused for zero-stake windows) [3](#0-2) , any block range with zero stakers silently and irrecoverably consumes part of the pool's reward budget without crediting any staker.

## Finding Description
The root cause is in `reward_per_token`: when `total_tokens_staked` is zero, the function short-circuits and returns `pool_info.reward_per_token_stored` unchanged, skipping the reward-per-token increment computation entirely [4](#0-3) . However, `update_pool_and_staker_rewards` — invoked on `stake`, `unstake`, and `harvest_rewards` — always calls `update_pool_rewards` with this returned value, which unconditionally sets `new_pool_info.last_update_block = T::BlockNumberProvider::current_block_number()` [5](#0-4) . This means the "clock" for reward accrual jumps forward through the zero-stake window with no compensating adjustment.

Because `last_block_reward_applicable` bounds the elapsed-blocks calculation only by the fixed `expiry_block` set at pool creation (extendable but never auto-adjusted for zero-participation spans) [3](#0-2) , the total reward budget implied by `reward_rate_per_block * (blocks between creation and expiry)` is fixed regardless of actual participation. The only recovery mechanism, `cleanup_pool`, requires zero stakers and returns the pool's *entire* reducible balance to the admin only after full pool teardown [6](#0-5)  — it does not correct accounting for zero-stake windows that occurred while the pool was still active with stakers coming and going.

## Impact Explanation
This causes a portion of reward-asset tokens deposited into a pool (via `deposit_reward_tokens` or direct transfer) to become unaccounted-for/stranded whenever `total_tokens_staked` is zero for any span of blocks before `expiry_block`. This directly reduces payouts below the advertised `reward_rate_per_block * duration`, resulting in a real accounting mismatch and fund loss for the pool admin/creator relative to the pool's promised distribution, without any recovery path short of fully draining and recreating the pool.

## Likelihood Explanation
Both `stake` and `unstake` are permissionless extrinsics available to any signed account (pool creation/administration is origin-restricted per the pallet's own docs, but staking/unstaking are not) [7](#0-6) . Any staker, including the last remaining one, can trigger `total_tokens_staked == 0` at will via `unstake`, and a freshly created pool naturally starts with zero stakers before anyone stakes. This makes the zero-stake condition a normal, easily and repeatably reachable state requiring no special privilege or unrealistic assumptions.

## Recommendation
Avoid letting `last_update_block` advance through zero-stake spans without accruing rewards — e.g., only update `last_update_block` when `total_tokens_staked` is non-zero (leaving it pinned at the block when stake last hit zero), or dynamically extend `expiry_block` by the length of any zero-stake span, or provide an accounting mechanism to reclaim exactly the unaccrued reward-budget portion attributable to zero-participation windows rather than requiring full pool teardown via `cleanup_pool`.

## Proof of Concept
1. Admin calls `create_pool` with `reward_rate_per_block = R` and `expiry_block = E`, then deposits reward tokens via `deposit_reward_tokens`.
2. No one stakes for `N` blocks, so `total_tokens_staked` remains `0`.
3. Alice calls `stake(pool_id, amount)`, invoking `update_pool_and_staker_rewards` → `reward_per_token()`. Since `total_tokens_staked` was `0`, `reward_per_token_stored` is unchanged, but `update_pool_rewards` sets `last_update_block` to the current block, skipping the `N`-block gap [8](#0-7) .
4. Once the pool reaches `expiry_block`, sum the rewards claimable by all stakers across the pool's lifetime (via `harvest_rewards`); this total will be short of `R * (E - creation_block)` by exactly `R * N`, and that `R * N` worth of reward-asset tokens remain in the pool account unaccounted for by any staker's storage record, recoverable only via admin-initiated `cleanup_pool` after full pool teardown.

### Citations

**File:** substrate/frame/asset-rewards/src/lib.rs (L47-51)
```rust
//! ## Permissioning
//!
//! Currently, pool creation and management restricted to a configured Origin.
//!
//! Future iterations of this pallet may allow permissionless creation and management of pools.
```

**File:** substrate/frame/asset-rewards/src/lib.rs (L65-68)
```rust
//! ## Rewards Algorithm
//!
//! The rewards algorithm is based on the Synthetix [StakingRewards.sol](https://web.archive.org/web/20251223190741/https://github.com/Synthetixio/synthetix/blob/develop/contracts/StakingRewards.sol)
//! smart contract.
```

**File:** substrate/frame/asset-rewards/src/lib.rs (L697-729)
```rust
		pub fn cleanup_pool(origin: OriginFor<T>, pool_id: PoolId) -> DispatchResult {
			let who = ensure_signed(origin)?;

			let pool_info = Pools::<T>::get(pool_id).ok_or(Error::<T>::NonExistentPool)?;
			ensure!(pool_info.admin == who, BadOrigin);

			let stakers = PoolStakers::<T>::iter_key_prefix(pool_id).next();
			ensure!(stakers.is_none(), Error::<T>::NonEmptyPool);

			let pool_balance = T::Assets::reducible_balance(
				pool_info.reward_asset_id.clone(),
				&pool_info.account,
				Preservation::Expendable,
				Fortitude::Polite,
			);
			T::Assets::transfer(
				pool_info.reward_asset_id,
				&pool_info.account,
				&pool_info.admin,
				pool_balance,
				Preservation::Expendable,
			)?;

			if let Some((who, cost)) = PoolCost::<T>::take(pool_id) {
				T::Consideration::drop(cost, &who)?;
			}

			Pools::<T>::remove(pool_id);

			Self::deposit_event(Event::PoolCleanedUp { pool_id });

			Ok(())
		}
```

**File:** substrate/frame/asset-rewards/src/lib.rs (L754-810)
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
```

**File:** substrate/frame/asset-rewards/src/lib.rs (L826-833)
```rust
		fn last_block_reward_applicable(pool_expiry_block: BlockNumberFor<T>) -> BlockNumberFor<T> {
			let now = T::BlockNumberProvider::current_block_number();
			if now < pool_expiry_block {
				now
			} else {
				pool_expiry_block
			}
		}
```
