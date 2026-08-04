## Analog Vulnerability Found

### Title
Frequent `stake`/`unstake` calls permanently truncate `reward_per_token` growth in `pallet-asset-rewards`, suppressing staker rewards - (`substrate/frame/asset-rewards/src/lib.rs`)

### Summary
`pallet-asset-rewards` computes staking rewards "just-in-time" using an integer formula that divides an elapsed-time-scaled numerator by `total_tokens_staked`, then unconditionally advances the `last_update_block` checkpoint on every call — exactly the pattern described in the external report for `AccountableOpenTerm::_linearInterest`/`accrueInterest`. This lets any staker permanently destroy small increments of reward accrual by calling permissionless extrinsics frequently.

### Finding Description
`reward_per_token` computes the accrued increment as: [1](#0-0) 

```
reward_per_token_stored + reward_rate_per_block * rewardable_blocks_elapsed * PRECISION_SCALING_FACTOR / total_tokens_staked
```

`PRECISION_SCALING_FACTOR` is only `4096` (a `u16`), a very small fixed-point scale compared to the arbitrary-precision fix (`PRECISION` scaled to 1e18/1e36) applied in the referenced audit remediation: [2](#0-1) 

`update_pool_rewards` then unconditionally moves the checkpoint forward regardless of whether the computed increment was non-zero: [3](#0-2) 

Just like `_accruedAt = block.timestamp` in the external report, `new_pool_info.last_update_block = T::BlockNumberProvider::current_block_number()` is set every time this path runs — even when `rewardable_blocks_elapsed * reward_rate_per_block * PRECISION_SCALING_FACTOR` rounds down to `0` because `total_tokens_staked` is large. Any elapsed-time slice whose contribution rounds to zero is discarded forever, instead of being carried into the next computation.

Both permissionless extrinsics `stake` and `unstake` invoke this exact path via `update_pool_and_staker_rewards` on every call: [4](#0-3) [5](#0-4) 

An unprivileged account can become a staker in any pool (pool creation is permissioned, but staking into an existing pool is not), then repeatedly call `stake`/`unstake` (with minimal amounts) every block. Whenever the elapsed-blocks window is small enough that `reward_rate_per_block * elapsed * 4096 < total_tokens_staked`, the increment truncates to zero on every call, yet `last_update_block` still advances — bleeding away reward growth that would otherwise have accumulated non-zero over a longer, uninterrupted window.

### Impact Explanation
This suppresses `reward_per_token_stored` growth for the entire pool, reducing rewards owed to *all* stakers (not just the attacker), analogous to the LP-return degradation described in the source report. Because `PRECISION_SCALING_FACTOR` is small (`4096`) relative to realistic `total_tokens_staked` values, the rounding-to-zero window is wide, making this practically triggerable rather than purely theoretical.

### Likelihood Explanation
No privileged role is required — staking into an already-created pool is permissionless, and `stake`/`unstake` are ordinary extrinsics callable every block at only the cost of transaction fees. The attack does not require any special origin, mocked path, or trusted actor; it directly reaches production reward-accounting logic.

### Recommendation
- Track sub-unit remainders (or use a higher-precision accumulator, e.g. scale `PRECISION_SCALING_FACTOR` up significantly, or track fractional remainder separately) so truncated fractions are preserved across calls instead of being discarded.
- Alternatively, only advance `last_update_block` when the computed increment is non-zero, or accumulate a carried remainder that is added into the next computation's numerator.

### Proof of Concept
Conceptually (mirroring the referenced Solidity PoC), for a pool with `reward_rate_per_block = R` and `total_tokens_staked = S` such that `R * 4096 < S`:
1. Staker A stakes into the pool at block `b0`.
2. Every subsequent block, staker A calls `unstake(0)`/`stake(0)` (or minimal amount), which calls `update_pool_and_staker_rewards` → `reward_per_token` → `update_pool_rewards`.
3. Each call computes `elapsed = 1`, increment `= R * 1 * 4096 / S = 0` (integer division truncation), yet `last_update_block` advances to the current block.
4. After `N` blocks of spam calls, `reward_per_token_stored` is unchanged (`0` accrued), whereas a single uninterrupted `harvest_rewards` call after the same `N` blocks would have computed `R * N * 4096 / S`, which is non-zero once `N` is large enough — demonstrating strictly lower payout under the "spam" pattern versus the "clean" single-accrual pattern, exactly as in the external report's `sfSpam < sfClean` assertion.

### Citations

**File:** substrate/frame/asset-rewards/src/lib.rs (L117-118)
```rust
/// Multiplier to maintain precision when calculating rewards.
pub(crate) const PRECISION_SCALING_FACTOR: u16 = 4096;
```

**File:** substrate/frame/asset-rewards/src/lib.rs (L469-502)
```rust
		/// Stake additional tokens in a pool.
		///
		/// A freeze is placed on the staked tokens.
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

**File:** substrate/frame/asset-rewards/src/lib.rs (L504-560)
```rust
		/// Unstake tokens from a pool.
		///
		/// Removes the freeze on the staked tokens.
		///
		/// Parameters:
		/// - origin: must be the `staker` if the pool is still active. Otherwise, any account.
		/// - pool_id: the pool to unstake from.
		/// - amount: the amount of tokens to unstake.
		/// - staker: the account to unstake from. If `None`, the caller is used.
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

			// Check the staker has enough staked tokens.
			ensure!(staker_info.amount >= amount, Error::<T>::NotEnoughTokens);

			// Unfreeze staker assets.
			T::AssetsFreezer::decrease_frozen(
				pool_info.staked_asset_id.clone(),
				&FreezeReason::Staked.into(),
				&staker,
				amount,
			)?;

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

			// Emit event.
			Self::deposit_event(Event::Unstaked { caller, staker, pool_id, amount });

			Ok(())
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
