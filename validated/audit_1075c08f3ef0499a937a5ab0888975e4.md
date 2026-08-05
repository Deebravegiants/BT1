Audit Report

## Title
Permanent underflow DoS in `pallet-asset-rewards` freezes all staked funds and rewards once a pool's `last_update_block` is updated past `expiry_block` — (File: `substrate/frame/asset-rewards/src/lib.rs`)

## Summary
`update_pool_rewards` unconditionally sets `last_update_block` to the current, unbounded block number rather than clamping it to `expiry_block`, while `reward_per_token` computes elapsed blocks as `last_block_reward_applicable(expiry_block).ensure_sub(last_update_block)`, which is only valid when `last_update_block <= expiry_block`. Once any call to a pool-mutating extrinsic occurs after `expiry_block`, `last_update_block` is pushed past `expiry_block`, and every subsequent call on that pool permanently underflows and reverts — including `unstake` and the admin's own recovery calls.

## Finding Description
`update_pool_rewards` sets the checkpoint to the raw current block number with no cap: [1](#0-0) 

`reward_per_token` computes `rewardable_blocks_elapsed` via `last_block_reward_applicable(pool_info.expiry_block).ensure_sub(pool_info.last_update_block)?`, and `last_block_reward_applicable` clamps `now` to `expiry_block` but does nothing to protect against `last_update_block` itself exceeding `expiry_block`: [2](#0-1) 

This is called by `update_pool_and_staker_rewards`, which every mutating dispatchable invokes as its first step: [3](#0-2) 

Trace of the bug:
1. Pool has `expiry_block = E`. A call at block `L0 <= E` sets `last_update_block = L0` (valid state).
2. First post-expiry call (e.g., `unstake` with a partial amount, keeping `total_tokens_staked > 0`) at block `N1 > E` computes `E.ensure_sub(L0)` (valid, since `L0 <= E`), succeeds, and then `update_pool_rewards` sets `last_update_block = N1` (uncapped, `> E`).
3. Any subsequent call at block `N2 > N1` on the same pool (while `total_tokens_staked` remains nonzero) computes `last_block_reward_applicable(E) = E` again, then `E.ensure_sub(N1)` — since `N1 > E`, this underflows and returns `Err(ArithmeticError)`, aborting the entire extrinsic.

All mutating entry points funnel through this same path: `stake` [4](#0-3) , `unstake` [5](#0-4) , and `harvest_rewards` [6](#0-5) . Critically, the admin's `set_pool_expiry_block` — the only conceivable in-protocol remedy — also calls `reward_per_token`/`update_pool_rewards` first and would itself revert with the same underflow: [7](#0-6) 

The only guard against the underflow is the early return when `total_tokens_staked.is_zero()` [8](#0-7) , which does not help any pool that retains nonzero staked tokens after the triggering call (e.g., a partial unstake, or any stake/unstake by other stakers, or a full unstake by only one of several stakers).

## Impact Explanation
Since `unstake` goes through the exact same reverting code path as `stake` and `harvest_rewards`, once triggered: all staked tokens for that pool remain frozen via `AssetsFreezer` with no way to unstake, and accrued/pending reward-asset balances become unreachable via `harvest_rewards`. The admin cannot recover the pool through `set_pool_reward_rate_per_block` or `set_pool_expiry_block` since these also call `reward_per_token` first and hit the identical underflow. This is a permanent, complete denial of service and fund lock for any affected pool, exceeding the impact of the referenced Mute Amplifier bug (where only fees, not principal, were trapped).

## Likelihood Explanation
No privileged role or special setup is required. Any unprivileged staker performing ordinary interactions with an expired pool — e.g., a partial `unstake` or repeated `stake`/`unstake`/`harvest_rewards` calls after `expiry_block` while `total_tokens_staked` remains nonzero — naturally advances `last_update_block` past `expiry_block` and triggers the permanent underflow on the next call. This is expected usage of a pool that isn't drained to zero total stake in a single atomic action immediately at/after expiry, making organic triggering highly likely for any long-lived pool with multiple stakers or partial unstakes.

## Recommendation
In `update_pool_rewards`, clamp the stored `last_update_block` to `Self::last_block_reward_applicable(pool_info.expiry_block)` rather than the raw current block number, mirroring the clamp already used in `reward_per_token`, so that `last_update_block` never exceeds `expiry_block`.

## Proof of Concept
1. `create_pool` with `expiry_block = E` (e.g., block 25, per the existing test suite's `DEFAULT_EXPIRE_AFTER` setup as shown in `extends_reward_accumulation`).
2. Two stakers stake tokens before expiry so `total_tokens_staked > 0`.
3. Advance `System::set_block_number` past `E` (e.g., to 30) and have staker A call `unstake` for a partial amount — this succeeds (computes `E - L0`, valid) and sets `PoolInfo.last_update_block = 30`; `total_tokens_staked` remains `> 0` due to staker B's remaining stake.
4. Advance to block 40 and call `stake`, `unstake`, `harvest_rewards`, or `set_pool_expiry_block` on the same pool — `reward_per_token`'s `last_block_reward_applicable(25).ensure_sub(30)` underflows (`25 - 30`), returning `Err(ArithmeticError)`, reverting the call.
5. Repeat step 4 with any account, including the pool admin's `set_pool_expiry_block` call — all revert identically, permanently locking staked funds and reward-asset balances in the pool. This should be added as a unit test in `substrate/frame/asset-rewards/src/tests.rs` alongside the existing `extends_reward_accumulation` test to demonstrate the underflow and resulting `Err` on subsequent calls.

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

**File:** substrate/frame/asset-rewards/src/lib.rs (L953-958)
```rust
		// Always start by updating the pool rewards.
		let reward_per_token = Self::reward_per_token(&pool_info)?;
		let mut pool_info = Self::update_pool_rewards(&pool_info, reward_per_token)?;

		pool_info.expiry_block = new_expiry_block;
		Pools::<T>::insert(pool_id, pool_info);
```
