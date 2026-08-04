### Title
Post-expiry state corruption permanently locks staked funds in `pallet-asset-rewards` - (File: `substrate/frame/asset-rewards/src/lib.rs`)

### Summary
`pallet-asset-rewards` implements a Synthetix-style JIT reward accrual scheme (explicitly modeled on `StakingRewards.sol`, the same family of contract as the `BaseGauge`/RAAC report). While the pallet does correctly cap reward *accrual* at `expiry_block` (unlike the reported bug, which caused over-distribution), it has an adjacent state-transition defect at the same boundary: after the pool has expired, `update_pool_rewards` still stamps `last_update_block` with the *current* block number rather than the capped value, poisoning the pool state so that all subsequent calls permanently fail with an arithmetic error.

### Finding Description
`reward_per_token` caps the "rewardable" window at `expiry_block` via `last_block_reward_applicable`: [1](#0-0) 

but the companion function that persists this state, `update_pool_rewards`, unconditionally sets `last_update_block` to `T::BlockNumberProvider::current_block_number()` — the *actual* current block, not the value used in the reward computation (`last_block_reward_applicable(expiry_block)`): [2](#0-1) 

Sequence:
1. Pool expiry is reached (`now > expiry_block`) and never extended by the admin.
2. Any staker calls `unstake` or `harvest_rewards` (both explicitly permitted post-expiry via `ensure!(now > pool_info.expiry_block || caller == staker, BadOrigin)`), which internally calls `update_pool_and_staker_rewards` → `reward_per_token` → `update_pool_rewards`. `reward_per_token` correctly computes rewards up to `expiry_block`, but `update_pool_rewards` then writes `last_update_block = now` (which is now **greater than** `expiry_block`).
3. Any subsequent call to `stake`, `unstake`, or `harvest_rewards` on the same pool recomputes `reward_per_token`: `last_block_reward_applicable(expiry_block)` returns `expiry_block` (since `now >= expiry_block`), and `expiry_block.ensure_sub(last_update_block)` underflows because `last_update_block > expiry_block`. The `ensure_sub` returns an `Err`, which is propagated via `?`, causing the extrinsic to fail with a `DispatchError`.

Relevant call sites: [3](#0-2)  (`unstake`) and [4](#0-3)  (`harvest_rewards`).

Once this state is corrupted, the only recovery is the pool admin calling `set_pool_expiry_block` with a new expiry strictly greater than the poisoned `last_update_block` — an admin-only, only-extend operation: [5](#0-4) . If the admin does not (or cannot, e.g. campaign genuinely over) extend the expiry, every remaining staker's frozen tokens become permanently un-unstakeable through the pallet's normal call path, since `unstake` cannot proceed past the reward computation step.

### Impact Explanation
This is not the over-distribution pattern of the original report (the pallet's expiry-capping logic actually prevents that specific bug), but it is the same *vulnerability class* the report calls out: incorrect/missing reset of period-boundary reward state (`last_update_block`/analogous to `rewardRate`/`periodFinish`) when the reward period ends. Here the consequence is worse from a fund-safety standpoint: staked assets held under `FreezeReason::Staked` become stuck (DoS on withdrawal) for any staker who does not manage to be first to interact after expiry, and remain stuck indefinitely unless the admin proactively extends the pool's expiry. This is an unprivileged, permissionless-reachable accounting/state-transition bug with direct fund-lock impact, not merely theoretical.

### Likelihood Explanation
High likelihood in any pool whose admin does not indefinitely keep extending the expiry (i.e. any pool that is allowed to genuinely conclude, which is the pallet's normal expected end-of-life flow — `cleanup_pool` even exists for this purpose). Any two ordinary stakers interacting with the pool after expiry (e.g., both trying to unstake to reclaim frozen funds) will trigger this: the first succeeds and poisons `last_update_block`, the second (and all further) calls to `stake`/`unstake`/`harvest_rewards` on that pool fail deterministically. No special privileges, timing, or interaction with mocked/gated paths are required — only normal `stake`/`unstake` calls and the passage of the pool's own configured expiry.

### Recommendation
In `update_pool_rewards`, set `last_update_block` to the capped value used for reward computation (`Self::last_block_reward_applicable(pool_info.expiry_block)`) instead of the unconditional current block number:

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
This keeps `last_update_block` consistent with the value actually used to bound reward accrual, eliminating the underflow and the resulting permanent lock on `unstake`/`harvest_rewards` after pool expiry.

### Proof of Concept
Conceptual sequence (Rust pseudo-test extending the pallet's existing `tests.rs` harness, since I cannot execute code in this environment):
```rust
// Pool: expiry_block = 25, reward_rate_per_block = 100
create_default_pool(); // uses DEFAULT_EXPIRE_AFTER
System::set_block_number(1);
StakingRewards::stake(RuntimeOrigin::signed(staker1), pool_id, 100)?;

// Advance well past expiry, no admin extension.
System::set_block_number(200);
// First post-expiry interaction succeeds and poisons last_update_block = 200 (> expiry 25).
assert_ok!(StakingRewards::unstake(RuntimeOrigin::signed(staker1), pool_id, 50, None));

// Second staker, or the same staker again, now attempting any further
// stake/unstake/harvest on this pool fails:
System::set_block_number(210);
assert_noop!(
    StakingRewards::unstake(RuntimeOrigin::signed(staker1), pool_id, 50, None),
    ArithmeticError::Underflow // via ensure_sub in reward_per_token
);
```
This mirrors the structure of the existing `set_pool_reward_rate_per_block`/`set_pool_expiry_block` tests in [6](#0-5)  which already exercise the expiry-boundary path but only through the read-only `assert_hypothetically_earned` helper and admin-driven `set_pool_expiry_block` extensions — they never exercise two consecutive *real* state-mutating calls after expiry without an intervening admin extension, which is why this defect is not caught by current tests.

### Citations

**File:** substrate/frame/asset-rewards/src/lib.rs (L513-533)
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
```

**File:** substrate/frame/asset-rewards/src/lib.rs (L568-586)
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

**File:** substrate/frame/asset-rewards/src/lib.rs (L940-963)
```rust
	fn set_pool_expiry_block(
		admin: &T::AccountId,
		pool_id: PoolId,
		new_expiry: DispatchTime<BlockNumberFor<T>>,
	) -> DispatchResult {
		let now = T::BlockNumberProvider::current_block_number();
		let new_expiry_block = new_expiry.evaluate(now);
		ensure!(new_expiry_block > now, Error::<T>::ExpiryBlockMustBeInTheFuture);

		let pool_info = Pools::<T>::get(pool_id).ok_or(Error::<T>::NonExistentPool)?;
		ensure!(pool_info.admin == *admin, BadOrigin);
		ensure!(new_expiry_block > pool_info.expiry_block, Error::<T>::ExpiryCut);

		// Always start by updating the pool rewards.
		let reward_per_token = Self::reward_per_token(&pool_info)?;
		let mut pool_info = Self::update_pool_rewards(&pool_info, reward_per_token)?;

		pool_info.expiry_block = new_expiry_block;
		Pools::<T>::insert(pool_id, pool_info);

		Self::deposit_event(Event::PoolExpiryBlockModified { pool_id, new_expiry_block });

		Ok(())
	}
```

**File:** substrate/frame/asset-rewards/src/tests.rs (L1325-1397)
```rust
		System::set_block_number(9);
		assert_ok!(StakingRewards::stake(RuntimeOrigin::signed(staker2), pool_id, 100));
		// At this point
		// - Staker 1 has earned 200 (100*2) tokens.
		// - Staker 2 has earned 0 tokens.
		// - Staker 1 is earning 50 tokens per block.
		// - Staker 2 is earning 50 tokens per block.

		// Check that Staker 1 has earned 200 tokens and Staker 2 has earned 0 tokens.
		assert_hypothetically_earned(staker1, 200, pool_id, reward_asset_id.clone());
		assert_hypothetically_earned(staker2, 0, pool_id, reward_asset_id.clone());

		// Block 12: Staker 1 stakes an additional 100 tokens.
		System::set_block_number(12);
		assert_ok!(StakingRewards::stake(RuntimeOrigin::signed(staker1), pool_id, 100));
		// At this point
		// - Staker 1 has earned 350 (200 + (50 * 3)) tokens.
		// - Staker 2 has earned 150 (50 * 3) tokens.
		// - Staker 1 is earning 66.66 tokens per block.
		// - Staker 2 is earning 33.33 tokens per block.

		// Check that Staker 1 has earned 350 tokens and Staker 2 has earned 150 tokens.
		assert_hypothetically_earned(staker1, 350, pool_id, reward_asset_id.clone());
		assert_hypothetically_earned(staker2, 150, pool_id, reward_asset_id.clone());

		// Block 22: Staker 1 unstakes 100 tokens.
		System::set_block_number(22);
		assert_ok!(StakingRewards::unstake(RuntimeOrigin::signed(staker1), pool_id, 100, None));
		// - Staker 1 has earned 1016 (350 + 66.66 * 10) tokens.
		// - Staker 2 has earned 483 (150 + 33.33 * 10) tokens.
		// - Staker 1 is earning 50 tokens per block.
		// - Staker 2 is earning 50 tokens per block.
		assert_hypothetically_earned(staker1, 1016, pool_id, reward_asset_id.clone());
		assert_hypothetically_earned(staker2, 483, pool_id, reward_asset_id.clone());

		// Block 23: Staker 1 unstakes 100 tokens.
		System::set_block_number(23);
		assert_ok!(StakingRewards::unstake(RuntimeOrigin::signed(staker1), pool_id, 100, None));
		// - Staker 1 has earned 1065 (1015 + 50) tokens.
		// - Staker 2 has earned 533 (483 + 50) tokens.
		// - Staker 1 is earning 0 tokens per block.
		// - Staker 2 is earning 100 tokens per block.
		assert_hypothetically_earned(staker1, 1066, pool_id, reward_asset_id.clone());
		assert_hypothetically_earned(staker2, 533, pool_id, reward_asset_id.clone());

		// Block 50: Stakers should only have earned 2 blocks worth of tokens (expiry is 25).
		System::set_block_number(50);
		// - Staker 1 has earned 1065 tokens.
		// - Staker 2 has earned 733 (533 + 2 * 100) tokens.
		// - Staker 1 is earning 0 tokens per block.
		// - Staker 2 is earning 0 tokens per block.
		assert_hypothetically_earned(staker1, 1066, pool_id, reward_asset_id.clone());
		assert_hypothetically_earned(staker2, 733, pool_id, reward_asset_id.clone());

		// Block 51: Extend the pool expiry block to 60.
		System::set_block_number(51);
		// - Staker 1 is earning 0 tokens per block.
		// - Staker 2 is earning 100 tokens per block.
		assert_ok!(StakingRewards::set_pool_expiry_block(
			RuntimeOrigin::signed(admin),
			pool_id,
			DispatchTime::At(60u64),
		));
		assert_hypothetically_earned(staker1, 1066, pool_id, reward_asset_id.clone());
		assert_hypothetically_earned(staker2, 733, pool_id, reward_asset_id.clone());

		// Block 53: Check rewards are resumed.
		// - Staker 1 has earned 1065 tokens.
		// - Staker 2 has earned 933 (733 + 2 * 100) tokens.
		// - Staker 2 is earning 100 tokens per block.
		System::set_block_number(53);
		assert_hypothetically_earned(staker1, 1066, pool_id, reward_asset_id.clone());
		assert_hypothetically_earned(staker2, 933, pool_id, reward_asset_id.clone());
```
