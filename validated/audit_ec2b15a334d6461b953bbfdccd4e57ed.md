Audit Report

## Title
Reward-per-token underflow after pool expiry locks out subsequent stakers - (File: `substrate/frame/asset-rewards/src/lib.rs`)

## Summary
`update_pool_rewards` unconditionally persists `last_update_block = T::BlockNumberProvider::current_block_number()` without clamping it to `pool_info.expiry_block`, while `reward_per_token` computes `Self::last_block_reward_applicable(pool_info.expiry_block).ensure_sub(pool_info.last_update_block)`, which clamps the *current* side to `expiry_block` but relies on the stored `last_update_block` never exceeding it. Once a pool has expired and any single account triggers a reward update (via `stake`, `unstake`, or `harvest_rewards`), `last_update_block` becomes `> expiry_block`, and every subsequent call to any of these extrinsics for that pool underflows and fails with `ArithmeticError::Underflow`.

## Finding Description
`reward_per_token` at [1](#0-0)  computes elapsed blocks as `last_block_reward_applicable(pool_info.expiry_block).ensure_sub(pool_info.last_update_block)`. `last_block_reward_applicable` clamps to `min(now, expiry_block)` [2](#0-1) , but `update_pool_rewards` stores the raw current block number as `last_update_block` with no clamp to `expiry_block` [3](#0-2) .

Both `harvest_rewards` [4](#0-3)  and, per the pallet's call surface, `stake`/`unstake` all route through `update_pool_and_staker_rewards`, which calls `reward_per_token` then `update_pool_rewards` [5](#0-4) . On the first call after `expiry_block` has passed, `pool_info.last_update_block` is still `<= expiry_block`, so `reward_per_token` succeeds; `update_pool_rewards` then stores `last_update_block = now > expiry_block`. On any later call (by any staker), `last_block_reward_applicable(expiry_block)` returns `expiry_block` (since `now >= expiry_block`), and `expiry_block.ensure_sub(last_update_block)` underflows because `last_update_block > expiry_block`, returning `Err(ArithmeticError::Underflow)` and aborting the extrinsic.

I confirmed this code path directly in the repository: `update_pool_rewards` has no clamping logic, and `reward_per_token`'s subtraction has no guard against `last_update_block` exceeding `expiry_block`. This is a genuine, unpatched logic bug in the reviewed code.

## Impact Explanation
For any pool that reaches expiry with more than one active staker, only the first account to interact with the pool after expiry can successfully call `harvest_rewards`, `stake`, or `unstake`; every other staker's calls to these functions will unconditionally revert with an arithmetic error. Because `unstake` also invokes the same reward-update path first, affected stakers are blocked from withdrawing their staked assets through the normal extrinsic, and blocked from harvesting any accrued rewards, for that specific pool — a real fund-availability impact confined to reward pools that have expired, recoverable only via admin intervention (`set_pool_reward_rate_per_block`/`set_pool_expiry_block`), which itself does not permanently fix the root cause since it can resurface at the next expiry.

## Likelihood Explanation
This is triggered under entirely ordinary, expected pallet usage — pools are explicitly designed to expire (see `cleanup_pool`) — and requires no privileged role, special configuration, or attacker capability beyond having more than one staker in a pool that is allowed to reach its `expiry_block`. Any unprivileged account calling `harvest_rewards`, `stake`, or `unstake` after expiry can trigger the poisoning, and any other unprivileged staker calling the same functions afterward hits the underflow deterministically and reproducibly.

## Recommendation
Clamp `last_update_block` to `pool_info.expiry_block` when persisting it in `update_pool_rewards`:
```rust
new_pool_info.last_update_block = Self::last_block_reward_applicable(pool_info.expiry_block);
```
This ensures `last_update_block` never exceeds the value used in the subsequent clamp inside `reward_per_token`, eliminating the underflow for all callers regardless of ordering.

## Proof of Concept
1. Create a pool with `expiry_block = now + N`.
2. Have two accounts, `alice` and `bob`, `stake` into the pool.
3. Advance the chain past `expiry_block`.
4. `alice` calls `harvest_rewards` (or `stake`/`unstake`) — succeeds; internally `Pools::<T>::get(pool_id).last_update_block` becomes `current_block_number()`, which is `> expiry_block`.
5. `bob` calls `harvest_rewards` (or `unstake`) — `reward_per_token` computes `last_block_reward_applicable(expiry_block) = expiry_block`, then `expiry_block.ensure_sub(last_update_block)` underflows, returning `Err(ArithmeticError::Underflow)`, and `bob`'s extrinsic fails. This can be added as a unit test in `substrate/frame/asset-rewards/src/tests.rs` following the existing test harness pattern for pool creation, staking, and block advancement.

### Citations

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

**File:** substrate/frame/asset-rewards/src/lib.rs (L754-765)
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

**File:** substrate/frame/asset-rewards/src/lib.rs (L794-801)
```rust
			let rewardable_blocks_elapsed: u32 =
				match Self::last_block_reward_applicable(pool_info.expiry_block)
					.ensure_sub(pool_info.last_update_block)?
					.try_into()
				{
					Ok(b) => b,
					Err(_) => return Err(Error::<T>::BlockNumberConversionError.into()),
				};
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
