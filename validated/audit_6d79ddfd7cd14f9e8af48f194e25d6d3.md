### Title
Reward-per-token calculation underflows and permanently reverts `stake`/`unstake`/`harvest_rewards` after pool expiry — `pallet-asset-rewards` (File: `substrate/frame/asset-rewards/src/lib.rs`)

### Summary
`pallet-asset-rewards`'s `reward_per_token()` computes elapsed blocks as `last_block_reward_applicable(expiry_block).ensure_sub(last_update_block)`, where `last_block_reward_applicable` caps the "now" value at `expiry_block`, but `last_update_block` is *not* capped when it is written. Once any account interacts with a pool after `expiry_block` has passed (without the admin extending it), `last_update_block` is set to the true current block, which is now greater than `expiry_block`. Any subsequent call to `stake`, `unstake`, or `harvest_rewards` computes `expiry_block - last_update_block` and underflows, causing the extrinsic to fail. This is the same root-cause pattern as the reported Solidity bug (`Math.min(block.timestamp, periodFinish) - lastUpdateTime` underflowing once `lastUpdateTime > periodFinish`).

### Finding Description
`update_pool_rewards` unconditionally stamps `last_update_block` with the real current block number, not the block capped at `expiry_block`: [1](#0-0) 

`reward_per_token` then computes elapsed blocks as the *expiry-capped* "now" minus `last_update_block`: [2](#0-1) 

and `last_block_reward_applicable` returns `min(now, expiry_block)`: [3](#0-2) 

Sequence that triggers the bug (pool not extended by admin):
1. Pool has `expiry_block = E`, `last_update_block = L1` where `L1 < E`, and non-zero `total_tokens_staked`.
2. After `E` has passed, account A calls `harvest_rewards`/`stake`/`unstake`. `reward_per_token` computes `min(now, E) - L1 = E - L1` (valid, no underflow), then `update_pool_rewards` sets `last_update_block = now` (which is `> E`). This call succeeds.
3. Any subsequent call to `stake`/`unstake`/`harvest_rewards` by account A or any other staker recomputes `reward_per_token`: `last_block_reward_applicable(E) = min(now, E) = E` (since `E` is unchanged and `now > E`), and `E.ensure_sub(last_update_block)` underflows because `last_update_block > E`. The `?` propagates an `ArithmeticError`, aborting the extrinsic.

This mirrors the reported issue precisely: the "capped-now minus stored last-update" subtraction is safe only as long as `last_update_block <= expiry`, and that invariant is broken the moment any interaction stamps `last_update_block` past `expiry_block` without a corresponding extension of `expiry_block`.

All three of `stake`, `unstake`, and `harvest_rewards` call `update_pool_and_staker_rewards` → `reward_per_token` before doing anything else: [4](#0-3) [5](#0-4) [6](#0-5) 

Because `ensure_sub` returns a checked `Result` rather than panicking, the failure surfaces as a normal `DispatchError` (no panic/chain-halt), but it still blocks every affected call.

### Impact Explanation
This is more severe than the original Solidity report because it doesn't just block reward *harvesting* — it also blocks `unstake`, since `unstake` performs the same `update_pool_and_staker_rewards` call before releasing the freeze on staked tokens: [7](#0-6) 

Once the underflow condition is triggered, every staker in the pool (not just the one who triggered it) is unable to `stake`, `unstake`, or `harvest_rewards` until the pool admin calls `set_pool_expiry_block` to push `expiry_block` beyond the stamped `last_update_block` (which itself also calls `reward_per_token`/`update_pool_rewards` and would need to succeed first, or would itself need to be called before anyone else touches the pool). This can effectively freeze user funds (frozen/staked assets) and unclaimed rewards in the pool until an admin intervenes, or indefinitely if the admin is unresponsive/adversarial toward that specific pool's users.

### Likelihood Explanation
This is highly likely to occur in practice: any pool with a finite `expiry_block` that is not proactively extended before it lapses will hit this once a single account interacts with it post-expiry (which is a completely normal, expected, unprivileged action — anyone can call `stake`, `unstake`, or `harvest_rewards`). No special permissions or preconditions are required beyond having non-zero `total_tokens_staked` in the pool at expiry, which is the common case.

### Recommendation
Cap `last_update_block` at `expiry_block` (or equivalently, use the same `last_block_reward_applicable` value) when recording the pool state, so the stored `last_update_block` can never exceed `expiry_block`:

```rust
pub fn update_pool_rewards(
    pool_info: &PoolInfoFor<T>,
    reward_per_token: T::Balance,
) -> Result<PoolInfoFor<T>, DispatchError> {
    let mut new_pool_info = pool_info.clone();
    new_pool_info.last_update_block = Self::last_block_reward_applicable(pool_info.expiry_block);
    new_pool_info.reward_per_token_stored = reward_per_token;
    Ok(new_pool_info)
}
```

Alternatively/additionally, replace the `ensure_sub` in `reward_per_token` with a saturating subtraction (`saturating_sub`) so that if `last_update_block` is ever ahead of the capped "now" (e.g., due to any other edge case), elapsed blocks are simply treated as `0` rather than reverting the call.

### Proof of Concept
Given a pool created with `reward_rate_per_block = R`, `expiry_block = E`, staker `A` already staked (`total_tokens_staked > 0`):

1. `System::set_block_number(E + 5)` (past expiry, not extended).
2. `StakingRewards::harvest_rewards(RuntimeOrigin::signed(A), pool_id, None)` — succeeds; internally sets `Pools[pool_id].last_update_block = E + 5`, leaving `expiry_block = E`.
3. `System::set_block_number(E + 10)`.
4. `StakingRewards::unstake(RuntimeOrigin::signed(A), pool_id, amount, None)` (or `stake`, or `harvest_rewards` again, from `A` or any other staker `B`) — fails, because `reward_per_token` computes `last_block_reward_applicable(E) = E` and then `E.ensure_sub(E + 5)` underflows, returning an `ArithmeticError` and reverting the extrinsic.

This confirms that after the first post-expiry interaction, the pool is bricked for all further `stake`/`unstake`/`harvest_rewards` calls until the admin extends `expiry_block` via `set_pool_expiry_block` to a value beyond the stamped `last_update_block`.

### Citations

**File:** substrate/frame/asset-rewards/src/lib.rs (L513-530)
```rust
		#[pallet::call_index(2)]
		pub fn unstake(
			origin: OriginFor<T>,
			pool_id: PoolId,
			amount: T::Balance,
			staker: Option<T::AccountId>,
		) -> DispatchResult {
			let caller = ensure_signed(origin)?;
			let staker = staker.unwrap_or(caller.clone());

			// Always start by updating the pool rewards.
			let pool_info = Pools::<T>::get(pool_id).ok_or(Error::<T>::NonExistentPool)?;
			let now = T::BlockNumberProvider::current_block_number();
			ensure!(now > pool_info.expiry_block || caller == staker, BadOrigin);

			let staker_info = PoolStakers::<T>::get(pool_id, &staker).unwrap_or_default();
			let (mut pool_info, mut staker_info) =
				Self::update_pool_and_staker_rewards(&pool_info, &staker_info)?;
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

**File:** substrate/frame/asset-rewards/src/lib.rs (L786-801)
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
