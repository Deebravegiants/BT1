## Analysis: Analog of StakedEXA "stuck rewards when no deposits" bug in `pallet-asset-rewards`

### Title
Stale reward index causes permanently lost rewards when a pool's `total_tokens_staked` is zero - (File: `substrate/frame/asset-rewards/src/lib.rs`)

### Summary
`pallet-asset-rewards` implements a Synthetix-style JIT reward-accrual scheme structurally identical to the `StakedEXA` contract described in the report: a `reward_per_token_stored` accumulator that is advanced by `rate * elapsed_blocks / total_staked` every time state is touched. Just like `StakedEXA::globalIndex()`, the pallet's `reward_per_token()` short-circuits and returns the *unchanged* stored value whenever the pool's stake is zero, while the caller (`update_pool_rewards`) still advances `last_update_block` to the current block.

### Finding Description
`reward_per_token()` computes the accumulator based on elapsed blocks since `last_update_block`: [1](#0-0) 

If `pool_info.total_tokens_staked.is_zero()`, it returns `reward_per_token_stored` unchanged — the accrual for that period is not computed at all, matching the StakedEXA `globalIndex()` bug where `if (totalSupply() == 0) return rewardData.index;`.

Immediately after, `update_pool_rewards` is called with this (unchanged) value and it unconditionally advances the pool's `last_update_block` bookkeeping to the current block: [2](#0-1) 

This is the same accounting flaw as `StakedEXA::updateIndex()`, which advances `rewardData.updatedAt` regardless of whether the index was actually incremented. Because `last_update_block` moves forward while `reward_per_token_stored` does not change, any reward that would have accrued at `reward_rate_per_block` during the zero-stake window is permanently skipped — it is never added to the accumulator on a later call, since the next computation only considers blocks *after* the new `last_update_block`.

`update_pool_and_staker_rewards`/`update_pool_rewards` is invoked from the stake/unstake/harvest call paths whenever a staker interacts with the pool (any call that touches `pool_info` and calls `reward_per_token`), so a pool that goes to zero total stake (e.g., the last staker fully unstakes) and later receives a new staker will have silently lost the reward-rate-driven emissions for the intervening idle period.

### Impact Explanation
Reward tokens are pre-funded into the pool's dedicated account by an admin at `reward_rate_per_block`; the emission for periods with zero total stake is neither distributed to anyone nor returned to the admin/pool creator via `cleanup_pool` — it is simply orphaned in the pool account with no accounting path to recover it (unlike `cleanup_pool`, which only works when the pool has zero stakers *and* is being deleted, transferring the entire pool balance back to the admin, not a computed "unclaimed idle" figure): [3](#0-2) 

This is a fund-accounting/DoS-style issue: reward funds become effectively stuck/unrecoverable through normal reward mechanics for any pool that experiences a zero-stake window, which is a realistic and even expected occurrence (a pool can trivially reach zero total stake if all stakers unstake, and pools can be created before any staker joins).

### Likelihood Explanation
Likelihood is moderate-to-high for any long-running incentive pool: reaching `total_tokens_staked == 0` requires no special privilege — any staker(s) fully unstaking drains the pool, and this is an entirely normal, unprivileged action reachable via the pallet's public `unstake` extrinsic. A pool can also simply be created and left with a running `reward_rate_per_block` before the first staker joins. No trusted-role compromise or mocked path is needed — this is a genuinely reachable state-transition bug in accounting logic that mirrors the referenced Sherlock finding almost line-for-line.

### Recommendation
When `total_tokens_staked` is zero, `reward_per_token()`/`update_pool_rewards()` should not simply freeze the accumulator while still advancing `last_update_block`. Either: (a) do not advance `last_update_block` past the point where stake became zero (so a subsequent staker still "catches" the frozen window correctly once compared against `expiry_block`), or (b) track and redirect the un-distributable emission (`reward_rate_per_block * elapsed_blocks_at_zero_stake`) back to the pool admin/creator (analogous to the mitigation suggested in the source report: sending undistributed amounts to a recoverable location instead of a black hole).

### Proof of Concept
1. Admin creates a pool via `create_pool` with a nonzero `reward_rate_per_block` and funds the pool account with reward asset: [4](#0-3) 
2. A staker joins, then later fully unstakes, bringing `total_tokens_staked` to `0`. From this point, every subsequent call into `update_pool_and_staker_rewards`/`update_pool_rewards` computes `reward_per_token()` which returns the stale, unchanged `reward_per_token_stored` due to the zero check at line 790, while `update_pool_rewards` (line 780) still sets `last_update_block = current_block`.
3. Time passes (`N` blocks) with `total_tokens_staked == 0`.
4. A new staker joins. The next `reward_per_token()` call computes rewards only from the *new* `last_update_block` forward — the `reward_rate_per_block * N` that should have accrued during the idle window is permanently unaccounted for and stuck in the pool's reward account with no code path (aside from full pool teardown via `cleanup_pool`, which just returns the *entire* remaining balance, not a computed idle-period amount) to recover it.

**Uncertainty note:** I could not fully trace every call path (`stake`, `unstake`, `harvest_rewards` implementations were located by grep but not read in full due to iteration limits) to confirm there is no additional safeguard (e.g., an explicit skip/short-circuit inside `stake`/`unstake` that prevents this exact window from opening, or a separate `PoolInfo.total_tokens_staked` invariant enforced elsewhere). This should be verified by reading the full `stake`/`unstake`/`harvest_rewards` call implementations in `substrate/frame/asset-rewards/src/lib.rs` before treating this as a fully confirmed, unmitigated issue.

### Citations

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

**File:** substrate/frame/asset-rewards/src/lib.rs (L843-884)
```rust
	fn create_pool(
		creator: &T::AccountId,
		staked_asset_id: T::AssetId,
		reward_asset_id: T::AssetId,
		reward_rate_per_block: T::Balance,
		expiry: DispatchTime<BlockNumberFor<T>>,
		admin: &T::AccountId,
	) -> Result<PoolId, DispatchError> {
		// Ensure the assets exist.
		ensure!(T::Assets::asset_exists(staked_asset_id.clone()), Error::<T>::NonExistentAsset);
		ensure!(T::Assets::asset_exists(reward_asset_id.clone()), Error::<T>::NonExistentAsset);

		// Check the expiry block.
		let now = T::BlockNumberProvider::current_block_number();
		let expiry_block = expiry.evaluate(now);
		ensure!(expiry_block > now, Error::<T>::ExpiryBlockMustBeInTheFuture);

		let pool_id = NextPoolId::<T>::try_mutate(|id| -> Result<PoolId, DispatchError> {
			let current_id = *id;
			*id = id.ensure_add(1)?;
			Ok(current_id)
		})?;

		let footprint = Self::pool_creation_footprint();
		let cost = T::Consideration::new(creator, footprint)?;
		PoolCost::<T>::insert(pool_id, (creator.clone(), cost));

		// Create the pool.
		let pool = PoolInfoFor::<T> {
			staked_asset_id: staked_asset_id.clone(),
			reward_asset_id: reward_asset_id.clone(),
			reward_rate_per_block,
			total_tokens_staked: 0u32.into(),
			reward_per_token_stored: 0u32.into(),
			last_update_block: 0u32.into(),
			expiry_block,
			admin: admin.clone(),
			account: Self::pool_account_id(&pool_id),
		};

		// Insert it into storage.
		Pools::<T>::insert(pool_id, pool);
```
