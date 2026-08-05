Audit Report

## Title
Permissionless, zero-cost griefing of `pallet-asset-rewards` reward accrual via integer-truncation of `reward_per_token` on repeated no-op `stake`/`unstake` calls - (File: `substrate/frame/asset-rewards/src/lib.rs`)

## Summary
`pallet-asset-rewards` implements a Synthetix-style reward-per-token accumulator whose per-block increment is computed as `reward_rate_per_block * blocks_elapsed * PRECISION_SCALING_FACTOR / total_tokens_staked` [1](#0-0) . Because `PRECISION_SCALING_FACTOR` is only `4096` [2](#0-1) , and `update_pool_rewards` always advances `last_update_block` to the current block regardless of whether the computed increment was truncated to zero [3](#0-2) , any block whose reward increment truncates to zero is permanently and irrecoverably lost for the entire pool.

## Finding Description
`stake` is permissionless and has no minimum-amount check, so `stake(pool_id, 0)` is a valid call by any signed account, even one with no prior stake, since `PoolStakers::get(...).unwrap_or_default()` supplies a default staker record [4](#0-3) . Each call runs `update_pool_and_staker_rewards`, which computes `reward_per_token` via integer division and then unconditionally persists `last_update_block = now` together with the (possibly unchanged) `reward_per_token_stored` [5](#0-4) . If `reward_rate_per_block * blocks_elapsed * 4096 < total_tokens_staked`, the division in `reward_per_token` truncates the increment to `0` while the elapsed-blocks window still advances past that interval [6](#0-5) . There is no code path that detects this truncation, accumulates a remainder, or refrains from advancing `last_update_block` when no reward accrued — the existing logic simply overwrites state on every `stake`/`unstake` invocation. `unstake(pool_id, 0)` on an existing stake reproduces the identical effect [7](#0-6) .

## Impact Explanation
Because `reward_per_token_stored` is the pool-wide accumulator from which every staker's earned rewards are derived, a truncated update affects all stakers in the pool simultaneously, not just the caller. Since `last_update_block` is unconditionally advanced past the truncated interval, the lost reward window can never be recovered through any subsequent extrinsic — it is a permanent reward-accrual freeze achievable at the cost of ordinary transaction fees only, with no privileged role required.

## Likelihood Explanation
The precondition `total_tokens_staked > reward_rate_per_block * 4096` is easily satisfied in realistic pools, particularly with commonly deployed 18-decimal assets or modest `reward_rate_per_block` configurations (e.g. the pallet is wired into `asset-hub-rococo` via `pallet_asset_rewards::Config` with `EnsureSigned` as `CreatePoolOrigin` [8](#0-7) , so any signed account can even create a pool). An attacker can automate `stake(pool_id, 0)` every block, requiring no special permission, no prior stake, and no victim mistake.

## Recommendation
- Increase `PRECISION_SCALING_FACTOR` substantially to reduce truncation frequency for realistic `reward_rate_per_block`/`total_tokens_staked` ratios.
- In `reward_per_token`, detect when the computed increment truncates to zero while `total_tokens_staked > 0` and elapsed blocks are nonzero; either carry the un-truncated remainder forward instead of dropping it, or avoid persisting `last_update_block` past intervals where no accrual occurred.
- Consider requiring `amount > 0` in `stake`, while recognizing this alone does not fully close the issue since `unstake(pool_id, 0)` on an existing position reproduces the same truncation.

## Proof of Concept
1. A pool is created (permissionlessly, since `CreatePoolOrigin = EnsureSigned` on Asset Hub Rococo) with `reward_rate_per_block = R`, and stakers deposit tokens such that `total_tokens_staked = S` with `S > R * 4096`.
2. Any signed account (attacker) calls `stake(pool_id, 0)` on this pool every block.
3. Each call computes `rewardable_blocks_elapsed = 1`; since `R * 1 * 4096 < S`, `ensure_div` truncates the increment to `0` in `reward_per_token` [1](#0-0) .
4. `Pools::<T>::insert(pool_id, pool_info)` persists `last_update_block = now` with `reward_per_token_stored` unchanged [9](#0-8) .
5. Repeating every block prevents `reward_per_token_stored` from ever advancing for that window, permanently erasing the corresponding reward period for every staker in the pool.

### Citations

**File:** substrate/frame/asset-rewards/src/lib.rs (L117-118)
```rust
/// Multiplier to maintain precision when calculating rewards.
pub(crate) const PRECISION_SCALING_FACTOR: u16 = 4096;
```

**File:** substrate/frame/asset-rewards/src/lib.rs (L472-502)
```rust
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

**File:** cumulus/parachains/runtimes/assets/asset-hub-rococo/src/lib.rs (L1070-1089)
```rust
impl pallet_asset_rewards::Config for Runtime {
	type RuntimeEvent = RuntimeEvent;
	type PalletId = AssetRewardsPalletId;
	type Balance = Balance;
	type Assets = NativeAndAllAssets;
	type AssetsFreezer = NativeAndAllAssetsFreezer;
	type AssetId = xcm::v5::Location;
	type CreatePoolOrigin = EnsureSigned<AccountId>;
	type RuntimeFreezeReason = RuntimeFreezeReason;
	type Consideration = HoldConsideration<
		AccountId,
		Balances,
		RewardsPoolCreationHoldReason,
		ConstantStoragePrice<StakePoolCreationDeposit, Balance>,
	>;
	type WeightInfo = weights::pallet_asset_rewards::WeightInfo<Runtime>;
	type BlockNumberProvider = frame_system::Pallet<Runtime>;
	#[cfg(feature = "runtime-benchmarks")]
	type BenchmarkHelper = PalletAssetRewardsBenchmarkHelper;
}
```
