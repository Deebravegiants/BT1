The claim is technically accurate based on the code I reviewed. `reward_per_token` computes `reward_rate_per_block * rewardable_blocks_elapsed * PRECISION_SCALING_FACTOR / total_tokens_staked` as a single integer division with no remainder tracking, and this is invoked on every `stake`/`unstake` call, both of which are permissionless-per-caller extrinsics with no minimum-interval restriction.

Audit Report

## Title
Truncated division in `reward_per_token` causes permanent loss of staking rewards - (File: `substrate/frame/asset-rewards/src/lib.rs`)

## Summary
`pallet-asset-rewards`'s reward accrual formula in `reward_per_token` (lib.rs:786-810) performs `reward_rate_per_block.ensure_mul(rewardable_blocks_elapsed).ensure_mul(PRECISION_SCALING_FACTOR).ensure_div(total_tokens_staked)` as a single truncating integer division with no remainder carry-over, using the fixed constant `PRECISION_SCALING_FACTOR = 4096` [1](#0-0)  as the only scaling factor. Because `reward_per_token_stored` only ever accumulates the already-rounded per-interval increment, whenever the numerator is smaller than `total_tokens_staked` for an interval, that interval's reward increment truncates to exactly zero and is permanently lost rather than deferred.

## Finding Description
`reward_per_token` computes the increment as shown, adding it directly into `reward_per_token_stored` with no fractional remainder retained across calls [2](#0-1) . `update_pool_rewards` stores exactly this value, overwriting the prior state, and `last_update_block` is advanced to the current block, so any truncated remainder for that interval is gone forever, not deferred to a future call [3](#0-2) . Both `stake` and `unstake` are signed, permissionless-per-caller extrinsics that call `update_pool_and_staker_rewards` → `reward_per_token` unconditionally on every invocation, with no minimum-interval or rate-limiting guard [4](#0-3) [5](#0-4) . This confirms the reported root cause and code path exactly.

## Impact Explanation
When `reward_rate_per_block * elapsed_blocks * 4096 < total_tokens_staked` for an interval, the reward due for that interval is permanently and irrecoverably lost to all stakers in the pool — it is not deferred to the next update, because `reward_per_token_stored` is a monotonic running value overwritten each call with the rounded-down result. The reward tokens allocated for that interval remain stranded in the pool's reward account, retrievable only by the admin via `cleanup_pool`, which additionally requires the pool to have zero active stakers, making recovery impractical while the pool is in use. This is a genuine, concrete fund-loss/griefing impact on honest stakers caused entirely by pallet logic (no external actor/node behavior required), matching an in-scope funds-loss/accounting-break impact class.

## Likelihood Explanation
The condition is realistic and does not require any privileged position: any signed account can call `stake`/`unstake` with no cooldown, and `total_tokens_staked` being large relative to `reward_rate_per_block * 4096` is plausible for pools where the staked asset has many decimals (e.g., 18) and/or the reward rate is modest relative to the staked-asset precision (e.g., reward asset with fewer decimals). An attacker forcing `rewardable_blocks_elapsed = 1` every block via repeated dust stake/unstake cycles converts what would otherwise be a coarser, non-truncating multi-block computation into many single-block computations that round to zero, at the cost only of transaction fees. This is a well-known class of vulnerability in reward-per-token accounting patterns (analogous to the cited external Locke.sol finding), and the fixed, small `PRECISION_SCALING_FACTOR` constant (12 bits of extra precision) rather than a large fixed-point scale (e.g., 1e18-style) makes the truncation threshold easy to cross for realistic parameter combinations.

## Recommendation
- Increase `PRECISION_SCALING_FACTOR` substantially (e.g., to a value proportional to `T::Balance`'s bit width, similar to 1e18-style fixed-point scaling used elsewhere in the runtime) to shrink rounding error.
- Track and carry over the fractional remainder from each `reward_per_token` computation across updates (e.g., store a remainder alongside `reward_per_token_stored`) so rewards are deferred rather than discarded.
- Consider imposing a minimum interval between reward-affecting operations per staker, or decoupling reward accrual granularity from `stake`/`unstake` call frequency.

## Proof of Concept
1. Admin creates a pool via `create_pool` with `reward_rate_per_block = R` and stakers bring `total_tokens_staked = S` such that `R * 4096 < S`.
2. Attacker repeatedly calls `stake(pool_id, 1)` then `unstake(pool_id, 1, None)` every block, each time forcing `rewardable_blocks_elapsed = 1` in `reward_per_token` [6](#0-5) .
3. Each call computes `R * 1 * 4096 / S = 0` via `ensure_div`, so `reward_per_token_stored` never increases across these griefed blocks despite `R` tokens/block nominally being due to the pool.
4. Over many griefed blocks, cumulative rewards distributable via `harvest_rewards` are measurably less than `R * total_blocks_elapsed`, with the shortfall stranded in the pool's reward account, unrecoverable by stakers, and recoverable by the admin only via `cleanup_pool` after the pool is fully emptied of stakers [7](#0-6) . A unit test asserting `reward_per_token_stored` remains unchanged across N single-block stake/unstake cycles under such `R`/`S` parameters, while `T::BlockNumberProvider` advances by N blocks, would concretely demonstrate the loss.

### Citations

**File:** substrate/frame/asset-rewards/src/lib.rs (L117-118)
```rust
/// Multiplier to maintain precision when calculating rewards.
pub(crate) const PRECISION_SCALING_FACTOR: u16 = 4096;
```

**File:** substrate/frame/asset-rewards/src/lib.rs (L473-502)
```rust
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

**File:** substrate/frame/asset-rewards/src/lib.rs (L513-560)
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

**File:** substrate/frame/asset-rewards/src/lib.rs (L700-729)
```rust
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
