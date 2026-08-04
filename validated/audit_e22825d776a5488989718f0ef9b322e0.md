I have enough evidence to confirm the analog. `pallet-asset-rewards` explicitly implements the Synthetix `StakingRewards.sol` algorithm, and its `reward_per_token` function has the identical zero-total-stake gap.

### Title
Reward Tokens Permanently Lost When Pool Has Zero Staked Tokens - (File: `substrate/frame/asset-rewards/src/lib.rs`)

### Summary
`pallet-asset-rewards` explicitly ports the Synthetix `StakingRewards.sol` reward algorithm (as documented in the pallet's own module docs), including the exact flaw described in the external report: while `pool_info.total_tokens_staked == 0`, `reward_per_token()` returns the stale `reward_per_token_stored` and does not advance `last_update_block`, so no accounting is created for elapsed blocks in that window. Because `reward_rate_per_block` continues to run against `pool_info.expiry_block` (a wall-clock/block deadline, not a "stake-seconds" clock), any block range during which the pool has zero stakers permanently and irrecoverably consumes part of the pool's reward budget without crediting anyone.

### Finding Description
`reward_per_token` in `substrate/frame/asset-rewards/src/lib.rs`: [1](#0-0) 

```
pub(super) fn reward_per_token(
    pool_info: &PoolInfoFor<T>,
) -> Result<T::Balance, DispatchError> {
    if pool_info.total_tokens_staked.is_zero() {
        return Ok(pool_info.reward_per_token_stored);
    }
    ...
}
```
When `total_tokens_staked.is_zero()`, this returns the previously stored value only, without accounting for `rewardable_blocks_elapsed` since `last_update_block`. `update_pool_rewards` then sets `new_pool_info.last_update_block = current_block_number()` unconditionally whenever it's invoked (e.g., on `stake`, `unstake`, `harvest_rewards`) [2](#0-1) , effectively "fast-forwarding" `last_update_block` through the zero-stake window without ever computing a reward-per-token increment for it.

`last_block_reward_applicable` caps the calculation only at `pool_info.expiry_block`, which is a fixed block number set at pool creation and only ever extendable — it is **not** paused or extended by periods of zero participation: [3](#0-2) 

So the reward budget implied by `reward_rate_per_block * (blocks between creation and expiry)` is fixed regardless of participation. Any block range in which `total_tokens_staked == 0` (e.g., all stakers `unstake` fully, or nobody stakes soon after `create_pool`) causes that slice of the reward budget to be silently dropped: it's neither credited to `reward_per_token_stored` nor reserved for future distribution.

The only fund-recovery path is `cleanup_pool`, which requires the pool to have **zero stakers** (`PoolStakers::iter_key_prefix(pool_id).next()` must be `None`) and transfers the reducible pool balance back to the admin [4](#0-3) . This does return unused tokens once the pool is torn down, but it does not correct or compensate for the specific "dead time" that already elapsed while `reward_rate_per_block` was silently ticking — the pool admin would need to detect the zero-stake condition and manually intervene (e.g., cleanup_pool + recreate pool with adjusted rate, or reduce reward rate) before/during that window, which is not automatic and not always possible (e.g., token deposited via `deposit_reward_tokens` by third parties, permissionless staking/unstaking by users at will).

### Impact Explanation
Funds set aside as `reward_asset_id` tokens for a pool (deposited via `deposit_reward_tokens` or transferred directly to the pool account) can become permanently stranded/unaccounted-for reward budget whenever the pool experiences a period with `total_tokens_staked == 0`, exactly mirroring the Synthetix bug in the referenced report. This is a direct loss to the pool creator/admin who funded the pool, and reduces trust in the pool's advertised reward rate since actual aggregate payouts can fall short of `reward_rate_per_block * duration`.

### Likelihood Explanation
This is easily reachable by any unprivileged user with no special permissions: any staker (or the last remaining staker) can call the permissionless `unstake` extrinsic to fully withdraw, driving `total_tokens_staked` to zero at any time, including immediately after `create_pool` before anyone stakes. There is no protocol mechanism preventing or compensating for this, so periods of zero participation are a normal, expected occurrence for any newly created or thinly-participated pool, especially given permissionless staking/unstaking timing.

### Recommendation
Track reward-per-token accrual so that block ranges with `total_tokens_staked == 0` do not silently consume `reward_rate_per_block` budget — e.g., by tracking a separate "last non-zero-stake update block" and skipping (not just capping) reward accrual for zero-stake spans, or by dynamically extending `expiry_block` by the length of zero-stake spans, or by allowing the admin to reclaim exactly the unaccrued portion (not just the pool's full remaining balance after all stakers exit) corresponding to zero-participation windows.

### Proof of Concept
1. Admin calls `create_pool` with `reward_rate_per_block = R`, `expiry_block = E` (many blocks in the future), and deposits reward tokens.
2. No one calls `stake` for `N` blocks (`total_tokens_staked` remains `0`).
3. Alice calls `stake(pool_id, amount)`. This invokes `update_pool_and_staker_rewards` → `reward_per_token()`; since `total_tokens_staked` was `0` for those `N` blocks, `reward_per_token_stored` is unchanged, and `last_update_block` jumps straight to the current block [5](#0-4) .
4. Later, once fully elapsed to `expiry_block`, total rewards actually claimable by all stakers sum to less than `R * (E - creation_block)` by exactly `R * N` — that `R * N` worth of reward-asset tokens remain stuck in the pool account with no storage record attributing them to anyone, and are only recoverable if/when the pool is fully drained of stakers and `cleanup_pool` is called by the admin.

### Citations

**File:** substrate/frame/asset-rewards/src/lib.rs (L697-729)
```rust
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

**File:** substrate/frame/asset-rewards/src/lib.rs (L775-810)
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
