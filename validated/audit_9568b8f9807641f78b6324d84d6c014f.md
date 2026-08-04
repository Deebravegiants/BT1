### Title
`harvest_rewards` never persists updated pool reward accumulator, causing reward double-accrual and pool insolvency - (File: substrate/frame/asset-rewards/src/lib.rs)

### Summary
`harvest_rewards` calls `Self::update_pool_and_staker_rewards(&pool_info, &staker_info)` to compute up-to-date per-token reward accrual, but — unlike `stake` and `unstake` — it never writes the returned, updated `pool_info` back into the `Pools` storage map. This leaves the pool's accumulator/last-update bookkeeping stale after every successful harvest, even though the extrinsic returns `Ok(())` and emits `RewardsHarvested`.

### Finding Description
In `stake` (`substrate/frame/asset-rewards/src/lib.rs:472-502`) and `unstake` (`:513-560`), the pattern is:
```
let (mut pool_info, mut staker_info) = Self::update_pool_and_staker_rewards(&pool_info, &staker_info)?;
...
Pools::<T>::insert(pool_id, pool_info);
``` [1](#0-0) 

In `harvest_rewards` (`:568-615`), the same helper is called:
```
let (pool_info, mut staker_info) = Self::update_pool_and_staker_rewards(&pool_info, &staker_info)?;
T::Assets::transfer(pool_info.reward_asset_id, &pool_info.account, &staker, staker_info.rewards, Preservation::Expendable)?;
...
Ok(())
```
but the resulting `pool_info` (which `update_pool_and_staker_rewards` uses to advance the pool's reward-per-token accumulator / last-update block to `now`) is discarded — there is no `Pools::<T>::insert(pool_id, pool_info)` anywhere in the function body. [2](#0-1) 

This is corroborated by the pallet's own generated benchmark weight metadata, which documents storage access counts per call: `stake`'s and `unstake`'s handler both show `AssetRewards::Pools (r:1 w:1)`, while `harvest_rewards` shows `AssetRewards::Pools (r:1 w:0)` — i.e., zero writes to `Pools` — confirming the pool-level state is genuinely never persisted during harvest. [3](#0-2) [4](#0-3) 

Because the pool-wide accumulator is not advanced past the block at which harvest occurred, the next public actor who touches the same pool (another staker calling `stake`, `unstake`, or `harvest_rewards`, or even the same staker again) will re-run `update_pool_and_staker_rewards` starting from the stale `last_update`/accumulator snapshot still in storage. The elapsed-block reward accrual for the window that was already paid out during the earlier successful harvest gets computed and credited a second time into the pool-wide accumulator, which is then used to compute every staker's owed rewards. This inflates the total rewards claimable by all stakers beyond what `reward_rate_per_block × elapsed_blocks` should allow for the pool, without any corresponding backing having been deposited via `deposit_reward_tokens`. `harvest_rewards` returns `Ok(())` and the terminal state (from the caller's perspective) looks fully settled, but the object (`Pools` entry) is left semantically incomplete — the accrual has been paid out to one staker but not "checked off" in the shared ledger that the next public caller relies on.

None of the pallet's existing checks catch this: `ensure!(now > pool_info.expiry_block || caller == staker, BadOrigin)` only gates origin, `NonExistentStaker`/`NonExistentPool` only validate existence, and the transfer with `Preservation::Expendable` only checks the *current* pool asset balance is sufficient for *this* payout — it does not validate that the payout is actually backed by unclaimed pool-wide reward-rate accrual.

### Impact Explanation
Repeated exploitation drains the reward pool's asset balance faster than the pool's configured `reward_rate_per_block` intends, letting stakers collectively harvest more reward tokens than were ever earned/deposited. This is pool insolvency: later legitimate stakers' `harvest_rewards`/`unstake` calls can fail (transfer of `staker_info.rewards` fails due to insufficient pool balance) or receive less than their fair share, while earlier callers extract disproportionate/unbacked rewards — matching the "unbacked mint or pool insolvency" scoped impact.

### Likelihood Explanation
Any unprivileged signed staker who has staked into a pool can trigger this simply by calling `harvest_rewards` as part of normal use — no special preconditions beyond having non-zero pending rewards. The missing write is unconditional (not input-dependent edge case), so it reproduces on every single successful `harvest_rewards` call, and the corruption compounds with every subsequent pool interaction by any staker, making this fully deterministic and repeatable, not merely a hypothetical edge case.

### Recommendation
In `harvest_rewards`, persist the updated pool state exactly as `stake`/`unstake` do:
```rust
let (mut pool_info, mut staker_info) = Self::update_pool_and_staker_rewards(&pool_info, &staker_info)?;
...
Pools::<T>::insert(pool_id, pool_info);
```
placed before or alongside the `PoolStakers` update, so the pool's reward accumulator/last-update block is advanced to `now` on every harvest, matching the invariant maintained by `stake` and `unstake`.

### Proof of Concept
Rust integration test (extend `substrate/frame/asset-rewards/src/tests.rs`, `mod harvest_rewards`):
1. Create a pool with two stakers, `staker1` and `staker2`, each staking equal amounts at block `B0`.
2. Advance to block `B1`. Call `harvest_rewards` for `staker1` — assert `Ok`, and record `pool_info` before/after via test-only storage read of `Pools::<MockRuntime>::get(pool_id)` — assert the stored pool's last-update/accumulator field is unchanged (still `B0`), demonstrating the missing persistence.
3. Advance to block `B2`. Call `harvest_rewards` for `staker2`. Assert the amount harvested for `staker2` equals `reward_rate_per_block * (B2 - B0)` proportional share instead of the expected `reward_rate_per_block * (B2 - B1)` share — i.e. `staker2`'s payout double-counts the `[B0, B1]` window already paid to `staker1`.
4. Assert `sum(all harvested amounts) > reward_rate_per_block * (B2 - B0)`, proving unbacked over-distribution relative to the pool's configured emission, and/or assert a later `harvest_rewards`/`unstake` call fails with an `Assets` transfer error due to depleted pool balance, confirming insolvency.

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

**File:** substrate/frame/asset-rewards/src/lib.rs (L576-615)
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

**File:** cumulus/parachains/runtimes/assets/asset-hub-rococo/src/weights/pallet_asset_rewards.rs (L115-134)
```rust
	/// Storage: `AssetRewards::Pools` (r:1 w:0)
	/// Proof: `AssetRewards::Pools` (`max_values`: None, `max_size`: Some(1344), added: 3819, mode: `MaxEncodedLen`)
	/// Storage: `AssetRewards::PoolStakers` (r:1 w:1)
	/// Proof: `AssetRewards::PoolStakers` (`max_values`: None, `max_size`: Some(116), added: 2591, mode: `MaxEncodedLen`)
	/// Storage: `Assets::Asset` (r:1 w:1)
	/// Proof: `Assets::Asset` (`max_values`: None, `max_size`: Some(210), added: 2685, mode: `MaxEncodedLen`)
	/// Storage: `Assets::Account` (r:2 w:2)
	/// Proof: `Assets::Account` (`max_values`: None, `max_size`: Some(134), added: 2609, mode: `MaxEncodedLen`)
	/// Storage: `AssetsFreezer::FrozenBalances` (r:1 w:0)
	/// Proof: `AssetsFreezer::FrozenBalances` (`max_values`: None, `max_size`: Some(84), added: 2559, mode: `MaxEncodedLen`)
	fn harvest_rewards() -> Weight {
		// Proof Size summary in bytes:
		//  Measured:  `1072`
		//  Estimated: `6208`
		// Minimum execution time: 81_304_000 picoseconds.
		Weight::from_parts(83_068_000, 0)
			.saturating_add(Weight::from_parts(0, 6208))
			.saturating_add(T::DbWeight::get().reads(6))
			.saturating_add(T::DbWeight::get().writes(4))
	}
```
