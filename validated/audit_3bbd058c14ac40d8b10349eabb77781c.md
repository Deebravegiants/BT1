Confirmed: `ensure_sub` on unsigned block-number types errors with `ArithmeticError::Underflow` when the subtrahend exceeds the minuend, and `?` propagates this out of `reward_per_token`, which is called by `update_pool_and_staker_rewards` — used in every `stake`, `unstake`, and `harvest_rewards` call.

### Title
Reward pool permanently bricked (DoS on stake/unstake/harvest) after `expiry_block` due to uncapped `last_update_block` - (File: `substrate/frame/asset-rewards/src/lib.rs`)

### Summary
`pallet-asset-rewards` computes each pool's rewardable period using an expiry-capped "last block reward applicable" value, but persists the *uncapped* current block number as `last_update_block`. Once a pool has expired and any interaction (`stake`, `unstake`, `harvest_rewards`) triggers one post-expiry update, every subsequent interaction with that pool permanently reverts with an arithmetic underflow, freezing all staked tokens and unclaimed rewards.

### Finding Description
`reward_per_token` computes the number of rewardable blocks elapsed by capping "now" at the pool's `expiry_block` via `last_block_reward_applicable`, then subtracting `pool_info.last_update_block`:

<cite repo="Alyssadaypin/polkadot-sdk--007" path="substrate/frame/asset-rewards/src/lib.rs" start="794="801" end="801" /> [1](#0-0) 

```rust
let rewardable_blocks_elapsed: u32 =
    match Self::last_block_reward_applicable(pool_info.expiry_block)
        .ensure_sub(pool_info.last_update_block)?
        .try_into()
``` [2](#0-1) 

```rust
fn last_block_reward_applicable(pool_expiry_block: BlockNumberFor<T>) -> BlockNumberFor<T> {
    let now = T::BlockNumberProvider::current_block_number();
    if now < pool_expiry_block { now } else { pool_expiry_block }
}
```

However, `update_pool_rewards` (called right after `reward_per_token` inside `update_pool_and_staker_rewards`) always stores the *real, uncapped* current block number, not the expiry-capped value: [3](#0-2) 

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

This is analogous to the LoopFi `_massUpdatePools`/`_updatePool` discrepancy: `_updatePool` caps `timestamp` at `endRewardTime`, but `_massUpdatePools` unconditionally stamps `lastAllPoolUpdate = block.timestamp`, creating a persistent mismatch between the capped per-item timestamp and the uncapped global timestamp. Here, the same class of bug appears: `last_update_block` (the "cursor") is left uncapped even though the rewardable-blocks calculation is capped at `expiry_block`.

Sequence:
1. Pool `expiry_block = E`. Some staker calls `stake`/`unstake`/`harvest_rewards` at block `N1 > E` (first interaction after expiry). `last_block_reward_applicable` returns `E`. `E.ensure_sub(last_update_block)` succeeds (since `last_update_block < E` from before expiry), rewards computed correctly for the interval up to `E`. `update_pool_rewards` then sets `last_update_block = N1` (i.e., `N1 > E`).
2. Any later interaction at block `N2 > N1 > E` calls `reward_per_token` again. `last_block_reward_applicable` still returns `E` (since `now >= E`). Now `E.ensure_sub(last_update_block)` = `E.ensure_sub(N1)`, and since `N1 > E`, this underflows an unsigned `BlockNumberFor<T>`, causing `ensure_sub` to return `Err(ArithmeticError::Underflow)`, propagated by `?`.
3. Every future call to `update_pool_and_staker_rewards` for this pool — invoked at the start of `stake`, `unstake`, and `harvest_rewards` — will fail identically forever, since `last_update_block` is never corrected back down. [4](#0-3) [5](#0-4) [6](#0-5) 

### Impact Explanation
Once triggered, `stake`, `unstake`, and `harvest_rewards` for the affected pool permanently revert with `ArithmeticError::Underflow` (surfaced through `DispatchError`), because `update_pool_and_staker_rewards` is unconditionally called first in each of these extrinsics. This permanently locks all stakers' frozen tokens (via `AssetsFreezer`) and any unclaimed reward tokens sitting in the pool's reward account, with no recovery path in the pallet itself (there is no admin call to reset `last_update_block`). This is a denial-of-service on user funds triggerable by any unprivileged account simply interacting with an already-expired pool.

### Likelihood Explanation
High likelihood: any pool that is allowed to fully expire (a completely normal, expected lifecycle event — pools are explicitly designed to have a finite `expiry_block`) will hit this bug as soon as a second post-expiry interaction occurs. No attacker privilege is required; a legitimate staker calling `unstake`/`harvest_rewards`/`stake` after expiry is sufficient to trigger the first uncapped write, and the very next such call by anyone bricks the pool.

### Recommendation
In `update_pool_rewards`, cap the stored `last_update_block` at `pool_info.expiry_block` the same way `reward_per_token`/`last_block_reward_applicable` do, e.g. store `Self::last_block_reward_applicable(pool_info.expiry_block)` instead of the raw `T::BlockNumberProvider::current_block_number()`. This keeps `last_update_block` and the capped "now" used in `reward_per_token` consistent, preventing the underflow and preserving correct reward accounting after expiry.

### Proof of Concept
1. `create_pool` with `expiry_block = 100`, `reward_rate_per_block = R`.
2. `stake` some tokens before block 100 (pool `last_update_block` set to some block `< 100`).
3. Advance to block `150` (`now = 150 > expiry_block = 100`). Call `harvest_rewards` (or `unstake`/`stake`): `reward_per_token` computes `100 - last_update_block` (valid), then `update_pool_rewards` sets `last_update_block = 150`.
4. Advance to block `200`. Call `harvest_rewards`/`unstake`/`stake` again: `reward_per_token` computes `last_block_reward_applicable(100) = 100`, then `100.ensure_sub(150)` underflows and the call fails with `ArithmeticError::Underflow`. This happens for every future call, permanently locking staked funds and unclaimed rewards for that pool.

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

**File:** substrate/frame/asset-rewards/src/lib.rs (L569-585)
```rust
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
