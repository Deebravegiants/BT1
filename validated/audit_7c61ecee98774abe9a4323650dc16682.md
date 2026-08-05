This confirms the exact mechanism claimed: `update_pool_rewards` (called inside `update_pool_and_staker_rewards`) advances `last_update_block` to `now` and sets `reward_per_token_stored` on the *local* `pool_info` copy, but `harvest_rewards` never calls `Pools::<T>::insert(pool_id, pool_info)` to persist this returned value, unlike `stake` [1](#0-0)  and `unstake` [2](#0-1) , which both call `Pools::<T>::insert` right after computing the updated pool state.

`harvest_rewards` reads the stale `pool_info` from storage, calls `update_pool_and_staker_rewards`, uses the resulting `pool_info.reward_asset_id`/`pool_info.account` only for the transfer, and returns `Ok(())` without ever writing the advanced `last_update_block`/`reward_per_token_stored` back to `Pools`. [3](#0-2) 

`update_pool_and_staker_rewards` and its helper `update_pool_rewards` confirm the accumulator math: they explicitly advance `last_update_block` to the current block and set `reward_per_token_stored` to the newly computed `reward_per_token`, and the whole design relies on the caller to persist this side-effect-free result. [4](#0-3)  Since `reward_per_token` is computed as `reward_per_token_stored + reward_rate_per_block * (elapsed_blocks_since_last_update_block) * PRECISION / total_staked` [5](#0-4) , failing to advance `last_update_block` after `harvest_rewards` means the next caller's `elapsed_blocks_since_last_update_block` calculation will re-include the window already paid out, double counting that reward window into the global accumulator that determines every staker's payout.

The weights metadata corroborates this: `harvest_rewards`'s `AssetRewards::Pools (r:1 w:0)` shows zero writes to `Pools`, contrasted with `stake`/`unstake` showing `(r:1 w:1)`. [6](#0-5)  This is not a benchmark artifact but a real, direct code-level confirmation of the missing storage write, matching the code inspection above exactly.

The root cause, exploit path, and impact reasoning in the claim all check out against the actual source: the design pattern (`compute -> mutate copy -> Pools::insert`) is followed in `stake`/`unstake` but broken in `harvest_rewards`, and this is triggerable by any unprivileged staker via a normal signed extrinsic with no special preconditions beyond having a stake and pending rewards.

Audit Report

## Title
`harvest_rewards` never persists updated pool reward accumulator, causing reward double-accrual and pool insolvency - (File: substrate/frame/asset-rewards/src/lib.rs)

## Summary
`harvest_rewards` calls `Self::update_pool_and_staker_rewards`, which advances the pool's `last_update_block` and `reward_per_token_stored` on a local copy, but unlike `stake` and `unstake` it never calls `Pools::<T>::insert(pool_id, pool_info)` to persist that update. As a result, every subsequent interaction with the pool recomputes reward accrual starting from the stale `last_update_block`, double-counting the reward window already paid out during the prior harvest and inflating total claimable rewards beyond what the pool's `reward_rate_per_block` and deposited balance support.

## Finding Description
`update_pool_and_staker_rewards`/`update_pool_rewards` are explicitly side-effect-free helpers that compute a new `PoolInfoFor<T>` with `last_update_block` set to the current block and `reward_per_token_stored` set to the freshly derived `reward_per_token`; the pallet's design explicitly delegates persistence of this result to the caller. Both `stake` and `unstake` follow this contract correctly by calling `Pools::<T>::insert(pool_id, pool_info)` after mutating the returned pool info. `harvest_rewards` calls the same helper, uses the returned `pool_info` only to read `reward_asset_id`/`account` for the reward transfer, and updates `PoolStakers` for the staker, but never inserts the updated `pool_info` back into `Pools`. Consequently the on-chain `Pools` entry retains its pre-harvest `last_update_block` and `reward_per_token_stored`. The next call to `stake`, `unstake`, or `harvest_rewards` on that pool recomputes `reward_per_token` using `reward_per_token()`, whose elapsed-blocks term is `now - pool_info.last_update_block` — a window that includes blocks already accounted for and paid out in the earlier harvest. None of the pallet's guards (`BadOrigin` origin check, `NonExistentStaker`/`NonExistentPool` existence checks, or the `Assets::transfer` balance check) validate that the pool-wide accumulator is consistent with cumulative payouts, so this discrepancy is silently absorbed into the shared `reward_per_token_stored` value used by all stakers.

## Impact Explanation
Because the global reward-per-token accumulator is advanced incorrectly (never, from `harvest_rewards`'s perspective, then double-counted by the next caller), the pool can be made to emit more reward tokens in aggregate than `reward_rate_per_block × elapsed_blocks` and the pool's actual reward asset balance support. This can starve later stakers' legitimate `harvest_rewards`/`unstake` calls (transfer failure due to insufficient pool balance) or allow earlier/repeated callers to extract disproportionate, unbacked rewards — a pool insolvency condition.

## Likelihood Explanation
Triggerable by any unprivileged signed account that has staked into a pool and has pending rewards, via the ordinary `harvest_rewards` extrinsic — no special preconditions, governance, or victim mistakes required. The missing write is unconditional, so it reproduces deterministically on every successful `harvest_rewards` call and compounds with subsequent pool interactions.

## Recommendation
In `harvest_rewards`, persist the updated pool state exactly as `stake`/`unstake` do, e.g. add `Pools::<T>::insert(pool_id, pool_info);` immediately after computing `(pool_info, mut staker_info) = Self::update_pool_and_staker_rewards(...)`, ensuring `last_update_block` and `reward_per_token_stored` are advanced to `now` on every harvest.

## Proof of Concept
1. Create a pool with two stakers, `staker1` and `staker2`, each staking equal amounts at block `B0`.
2. Advance to block `B1`; call `harvest_rewards` for `staker1`. Read `Pools::<MockRuntime>::get(pool_id)` and observe `last_update_block` is still `B0` (unchanged), even though the call succeeded and paid out rewards.
3. Advance to block `B2`; call `harvest_rewards` for `staker2`. Because `reward_per_token()` still computes elapsed blocks from `B0` (not `B1`), `staker2`'s payout double-counts the `[B0, B1]` window already paid to `staker1`.
4. Assert `sum(all harvested amounts) > reward_rate_per_block * (B2 - B0)`, demonstrating unbacked over-distribution, and/or show a later `harvest_rewards`/`unstake` failing due to depleted pool asset balance.

### Citations

**File:** substrate/frame/asset-rewards/src/lib.rs (L479-492)
```rust
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
```

**File:** substrate/frame/asset-rewards/src/lib.rs (L529-545)
```rust
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
```

**File:** substrate/frame/asset-rewards/src/lib.rs (L577-615)
```rust
			// Always start by updating the pool and staker rewards.
			let pool_info = Pools::<T>::get(pool_id).ok_or(Error::<T>::NonExistentPool)?;
			let now = T::BlockNumberProvider::current_block_number();
			ensure!(now > pool_info.expiry_block || caller == staker, BadOrigin);

			let staker_info =
				PoolStakers::<T>::get(pool_id, &staker).ok_or(Error::<T>::NonExistentStaker)?;
			let (pool_info, mut staker_info) =
				Self::update_pool_and_staker_rewards(&pool_info, &staker_info)?;

			// Transfer unclaimed rewards from the pool to the staker.
			T::Assets::transfer(
				pool_info.reward_asset_id,
				&pool_info.account,
				&staker,
				staker_info.rewards,
				// Could kill the account, but only if the pool was already almost empty.
				Preservation::Expendable,
			)?;

			// Emit event.
			Self::deposit_event(Event::RewardsHarvested {
				caller,
				staker: staker.clone(),
				pool_id,
				amount: staker_info.rewards,
			});

			// Reset staker rewards.
			staker_info.rewards = 0u32.into();

			if staker_info.amount.is_zero() {
				PoolStakers::<T>::remove(&pool_id, &staker);
			} else {
				PoolStakers::<T>::insert(&pool_id, &staker, staker_info);
			}

			Ok(())
		}
```

**File:** substrate/frame/asset-rewards/src/lib.rs (L750-784)
```rust
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

**File:** substrate/frame/asset-rewards/src/weights.rs (L129-164)
```rust
	/// Storage: `AssetRewards::Pools` (r:1 w:1)
	/// Proof: `AssetRewards::Pools` (`max_values`: None, `max_size`: Some(150), added: 2625, mode: `MaxEncodedLen`)
	/// Storage: `AssetRewards::PoolStakers` (r:1 w:1)
	/// Proof: `AssetRewards::PoolStakers` (`max_values`: None, `max_size`: Some(116), added: 2591, mode: `MaxEncodedLen`)
	/// Storage: `AssetsFreezer::Freezes` (r:1 w:1)
	/// Proof: `AssetsFreezer::Freezes` (`max_values`: None, `max_size`: Some(105), added: 2580, mode: `MaxEncodedLen`)
	/// Storage: `Assets::Account` (r:1 w:0)
	/// Proof: `Assets::Account` (`max_values`: None, `max_size`: Some(134), added: 2609, mode: `MaxEncodedLen`)
	/// Storage: `AssetsFreezer::FrozenBalances` (r:1 w:1)
	/// Proof: `AssetsFreezer::FrozenBalances` (`max_values`: None, `max_size`: Some(84), added: 2559, mode: `MaxEncodedLen`)
	fn unstake() -> Weight {
		// Proof Size summary in bytes:
		//  Measured:  `638`
		//  Estimated: `3615`
		// Minimum execution time: 46_068_000 picoseconds.
		Weight::from_parts(46_950_000, 3615)
			.saturating_add(T::DbWeight::get().reads(5_u64))
			.saturating_add(T::DbWeight::get().writes(4_u64))
	}
	/// Storage: `AssetRewards::Pools` (r:1 w:0)
	/// Proof: `AssetRewards::Pools` (`max_values`: None, `max_size`: Some(150), added: 2625, mode: `MaxEncodedLen`)
	/// Storage: `AssetRewards::PoolStakers` (r:1 w:1)
	/// Proof: `AssetRewards::PoolStakers` (`max_values`: None, `max_size`: Some(116), added: 2591, mode: `MaxEncodedLen`)
	/// Storage: `Assets::Asset` (r:1 w:1)
	/// Proof: `Assets::Asset` (`max_values`: None, `max_size`: Some(210), added: 2685, mode: `MaxEncodedLen`)
	/// Storage: `Assets::Account` (r:2 w:2)
	/// Proof: `Assets::Account` (`max_values`: None, `max_size`: Some(134), added: 2609, mode: `MaxEncodedLen`)
	fn harvest_rewards() -> Weight {
		// Proof Size summary in bytes:
		//  Measured:  `766`
		//  Estimated: `6208`
		// Minimum execution time: 60_648_000 picoseconds.
		Weight::from_parts(62_025_000, 6208)
			.saturating_add(T::DbWeight::get().reads(5_u64))
			.saturating_add(T::DbWeight::get().writes(4_u64))
	}
```
