### Title
Reward accrual is silently skipped during zero-total-stake periods, permanently forfeiting deposited reward tokens - (`substrate/frame/asset-rewards/src/lib.rs`)

### Summary
`pallet-asset-rewards` (FRAME's staking-rewards pallet) implements a Synthetix-style `rewardPerToken` accumulator model identical in structure to the `BaseRewardPool`/`VE3DRewardPool` pattern from the referenced report. When `total_tokens_staked` is zero, the pool's `reward_per_token()` calculation is short-circuited and returns the stored value unchanged, while the caller (`update_pool_rewards`) unconditionally advances `last_update_block` to the current block. This causes any reward-rate-implied accrual during the zero-stake window to be permanently skipped rather than deferred or redistributed, exactly mirroring the reported vulnerability class.

### Finding Description
The core accumulator logic lives in `reward_per_token`: [1](#0-0) 

If `pool_info.total_tokens_staked.is_zero()`, the function returns `pool_info.reward_per_token_stored` unchanged — no accrual is computed for the elapsed blocks.

This value flows into `update_pool_and_staker_rewards` → `update_pool_rewards`, which unconditionally sets `last_update_block` to the current block regardless of whether any accrual actually happened: [2](#0-1) 

Because `last_update_block` is only ever advanced when a staker interacts with the pool (`stake`, `unstake`, `harvest_rewards`) or the admin adjusts it (`set_pool_reward_rate_per_block`), any span of blocks during which `total_tokens_staked == 0` is retroactively "erased" the moment the next interaction occurs: the elapsed-block window is consumed by `last_block_reward_applicable(...) - last_update_block`, but since the branch taken was the zero-stake early return, that window's implied reward-rate emission (`reward_rate_per_block * elapsed_blocks`) is never added to `reward_per_token_stored`. It is not deferred, refunded, or attributed to any staker — it's simply dropped from the accounting forever.

This can occur in two realistic scenarios:
1. A pool is created (`create_pool`) and reward tokens deposited (`deposit_reward_tokens`) before the first staker joins — the gap between `last_update_block = 0` and the block of the first `stake` call is lost.
2. All stakers fully exit a pool (`unstake` removes the `PoolStakers` entry once `amount` and `rewards` reach zero: [3](#0-2) ), leaving `total_tokens_staked == 0` while the pool still holds staker entries elsewhere or new stakers eventually re-enter — the intervening blocks' reward-rate emission is lost.

`cleanup_pool` only allows the admin to reclaim the pool's *remaining* reward-asset balance, and only when there are zero `PoolStakers` entries at all: [4](#0-3) . This does not help in scenario where a pool has some active stakers but also experienced a transient zero-stake window earlier in its lifetime (e.g., pool created, funded, and left idle before the first stake) — once stakers exist, `cleanup_pool` is blocked by `NonEmptyPool`, and the tokens corresponding to the skipped window can never be attributed to anyone nor recovered by the admin until the pool is fully drained of stakers again.

### Impact Explanation
Reward tokens transferred into a pool's account via `deposit_reward_tokens` (or direct transfer) that correspond to periods where `total_tokens_staked == 0` are never credited to `reward_per_token_stored`, and thus never become claimable by any staker via `harvest_rewards`. This is a direct loss-of-yield / stuck-funds issue analogous to the C4 Medium finding: reward emission windows with no stakers are silently forfeited rather than being deferred until stakers exist. This matches the "unused rewards... locked forever" characterization from the report, since recovery via `cleanup_pool` is only possible when the pool has no active stakers, which is not guaranteed once a legitimate staker population exists.

### Likelihood Explanation
This requires no privileged action or attacker-controlled path beyond ordinary usage: any pool admin creating a pool and funding it before the first staker joins (a natural operational sequence, e.g., during pool bootstrap) will trigger this loss. It is not contingent on malicious behavior, matching the "no deposits before adding rewards" scenario judged Medium severity in the original report.

### Recommendation
When `total_tokens_staked` is zero, `update_pool_rewards`/`reward_per_token` should not advance `last_update_block` to the current block (or should track and either roll over undistributed rewards, or explicitly document/enforce that reward funding must only occur after non-zero stake exists, and/or extend `cleanup_pool`-style recovery to reclaim reward tokens accrued during zero-stake windows even when stakers currently exist elsewhere in the pool).

### Proof of Concept
1. Admin calls `create_pool` at block 0 with a nonzero `reward_rate_per_block`, then `deposit_reward_tokens` to fund the pool account.
2. No one stakes until block `N` (`total_tokens_staked == 0` for the entire window `[0, N)`).
3. At block `N`, a user calls `stake`. This triggers `update_pool_and_staker_rewards` → `reward_per_token()`, which takes the `total_tokens_staked.is_zero()` branch (see `substrate/frame/asset-rewards/src/lib.rs:790-792`) and returns `reward_per_token_stored` unchanged (still `0`).
4. `update_pool_rewards` then sets `last_update_block = N` (see `substrate/frame/asset-rewards/src/lib.rs:780`), permanently discarding the `[0, N)` window's implied `reward_rate_per_block * N` emission — no staker will ever be credited for it, yet the reward pot may have already been funded for that duration.
5. From block `N` onward, accrual resumes normally, but the funds corresponding to blocks `[0, N)` remain in the pool's account, unclaimable via `harvest_rewards`, and unrecoverable via `cleanup_pool` once any staker exists.

### Citations

**File:** substrate/frame/asset-rewards/src/lib.rs (L543-554)
```rust
			// Update Pools.
			pool_info.total_tokens_staked.ensure_sub_assign(amount)?;
			Pools::<T>::insert(pool_id, pool_info);

			// Update PoolStakers.
			staker_info.amount.ensure_sub_assign(amount)?;

			if staker_info.amount.is_zero() && staker_info.rewards.is_zero() {
				PoolStakers::<T>::remove(&pool_id, &staker);
			} else {
				PoolStakers::<T>::insert(&pool_id, &staker, staker_info);
			}
```

**File:** substrate/frame/asset-rewards/src/lib.rs (L696-729)
```rust
		#[pallet::call_index(8)]
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

**File:** substrate/frame/asset-rewards/src/lib.rs (L746-784)
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

**File:** substrate/frame/asset-rewards/src/lib.rs (L787-810)
```rust
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
