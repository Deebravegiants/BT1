### Title
Staking after pool expiry can permanently brick a pool via arithmetic underflow in `reward_per_token`, locking rewards and staked funds forever - (File: `substrate/frame/asset-rewards/src/lib.rs`)

### Summary
`pallet-asset-rewards` (the `StakingRewards` pallet) is structurally analogous to `MuteAmplifier.sol`: users `stake` a token into a time-bounded reward pool, and the admin later reclaims leftover rewards via `cleanup_pool`, which is blocked while any staker remains. Just like the Mute finding, the `stake` extrinsic performs no check that the pool has not already expired, letting an unprivileged user stake into an already-expired, empty pool. Unlike Mute (where the impact is "just" an unremovable, reward-less staker blocking rescue), here this also drives the pool's `last_update_block` past `expiry_block` while `total_tokens_staked` becomes non-zero, which makes every subsequent reward computation underflow and revert — permanently bricking `unstake`, `harvest_rewards` and `cleanup_pool` for that pool.

### Finding Description
`stake` has no expiry check at all: [1](#0-0) 

Compare with `unstake`/`harvest_rewards`, which only allow the caller to act on behalf of another staker once the pool has expired, but otherwise are also unrestricted for the staker themselves: [2](#0-1) [3](#0-2) 

`reward_per_token` takes a fast path when `total_tokens_staked` is zero (returning the stored value untouched), otherwise it computes elapsed "rewardable" blocks as `last_block_reward_applicable(expiry_block).ensure_sub(last_update_block)`: [4](#0-3) 

`last_block_reward_applicable` clamps "now" to `expiry_block` once the pool has expired: [5](#0-4) 

But `update_pool_rewards` always stamps `last_update_block` with the real current block, **not** clamped to `expiry_block`: [6](#0-5) 

Sequence of the exploit on a pool that expired with nobody ever having staked (`total_tokens_staked == 0`, `last_update_block == 0` or some pre-expiry block):
1. Attacker calls `stake` after `expiry_block`. Because `total_tokens_staked` is still 0 at the time `reward_per_token` is evaluated, the zero-stake fast path is taken and the call succeeds with no error. `update_pool_rewards` then sets `pool_info.last_update_block = now` (a block number *after* `expiry_block`), and `pool_info.total_tokens_staked` becomes non-zero after the attacker's deposit is added.
2. Any subsequent call that touches this pool (`stake`, `unstake`, `harvest_rewards` — including calls made by the admin trying to unwind the attacker's position, or by anyone using the "permissionless after expiry" path in `unstake`) invokes `reward_per_token` again. Now `total_tokens_staked > 0`, so the calculation branch runs: `last_block_reward_applicable(expiry_block)` returns `expiry_block` (clamped, since now > expiry), and `.ensure_sub(pool_info.last_update_block)` subtracts a *larger* number (`last_update_block`, which is > `expiry_block`) from a *smaller* one (`expiry_block`), underflowing.
3. `ensure_sub` (from the checked-arithmetic trait family used throughout FRAME pallets) returns an `Err` on underflow rather than saturating, so the whole extrinsic call fails with a dispatch error.
4. From this point on, the attacker's stake entry can never be removed via `unstake` (it always fails), so `PoolStakers::iter_key_prefix(pool_id).next()` never returns `None`, and `cleanup_pool`'s guard permanently blocks reclamation of the pool's rewards: [7](#0-6) 

This is a direct analog of the Mute bug's root cause class: a missing/misplaced time-window check on the permissionless `stake` entry point lets an attacker acquire staker status in a pool that has already ended, which then defeats the admin's cleanup/rescue path that assumes "no stakers ⇒ safe to reclaim."

### Impact Explanation
Once triggered, the pool's reward-asset balance (held in `pool_info.account`) and the `PoolCost` storage-deposit consideration become permanently unrecoverable: `cleanup_pool` can never succeed because the stakers list is never empty, and the attacker (or anyone) can also never successfully `unstake` because every call to `reward_per_token` for that pool underflows and reverts. This is a full, permanent denial-of-service against the pool's admin-controlled reward-reclamation mechanism and effectively locks funds forever, matching the "reward locked in the contract indefinitely" impact of the referenced report.

### Likelihood Explanation
The trigger requires only: (a) a pool exists past its `expiry_block`, and (b) `total_tokens_staked == 0` at that time (i.e., either nobody ever staked, or all stakers fully exited before the attack). Any unprivileged, signed account can then call `stake` with a minimal amount — no special origin, balance threshold, or race condition against block-production timing is required beyond simply staking after expiry and before the admin calls `cleanup_pool`. This is a realistic and low-cost griefing vector for any pool that is momentarily empty near/after its expiry.

### Recommendation
- Reject `stake` once `now >= pool_info.expiry_block` (mirroring the spirit of the Mute fix — the "staking is over" check must apply universally, not only to the non-first staker).
- Additionally/alternatively, clamp `last_update_block` to `expiry_block` in `update_pool_rewards` when the pool has already expired, so `reward_per_token`'s subtraction can never underflow regardless of when `stake` is called.
- Consider allowing `cleanup_pool` (or a dedicated admin-only sweep) to force-remove residual stakers with zero accrued rewards after expiry, so a poisoned pool state cannot permanently block fund recovery.

### Proof of Concept
1. Admin calls `create_pool` with `expiry_block = E`; nobody stakes, or all stakers fully unstake, so at block `E` (and after) `Pools::<T>::get(pool_id).total_tokens_staked == 0`.
2. At block `E + k` (k > 0), attacker calls `stake(origin=attacker, pool_id, amount=1)`. This succeeds silently: `reward_per_token` takes the `total_tokens_staked.is_zero()` fast path (see `substrate/frame/asset-rewards/src/lib.rs:790-792`), then `update_pool_rewards` sets `last_update_block = E + k` (see `substrate/frame/asset-rewards/src/lib.rs:780`), and `total_tokens_staked` becomes `1`.
3. Admin (or attacker) subsequently calls `unstake(pool_id, 1, Some(attacker))` (permissionless since `now > expiry_block`, see `substrate/frame/asset-rewards/src/lib.rs:526`). This calls `reward_per_token`, which now takes the calculation branch: `last_block_reward_applicable(E) = E`, then `E.ensure_sub(E + k)` underflows and returns `Err(ArithmeticError::Underflow)`, propagated via `?` up through `update_pool_and_staker_rewards` and out of `unstake` as a failed `DispatchResult`.
4. Every future `stake`/`unstake`/`harvest_rewards`/attempted cleanup path on this `pool_id` fails identically, and `cleanup_pool`'s `ensure!(stakers.is_none(), Error::<T>::NonEmptyPool)` (see `substrate/frame/asset-rewards/src/lib.rs:703-704`) can never pass — the pool's reward-asset balance and its `PoolCost` deposit are permanently stuck.

Note: I was unable to run this pallet's test-suite (`substrate/frame/asset-rewards/src/tests.rs`) to empirically confirm the underflow at runtime; the conclusion above is derived from static analysis of the exact arithmetic and control flow shown in the cited lines, and from the semantics of the `EnsureSub`/`ensure_sub` checked-arithmetic trait used throughout `substrate/primitives/arithmetic/src/traits.rs`, which returns `Err` (not saturating) on underflow.

### Citations

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

**File:** substrate/frame/asset-rewards/src/lib.rs (L524-526)
```rust
			let pool_info = Pools::<T>::get(pool_id).ok_or(Error::<T>::NonExistentPool)?;
			let now = T::BlockNumberProvider::current_block_number();
			ensure!(now > pool_info.expiry_block || caller == staker, BadOrigin);
```

**File:** substrate/frame/asset-rewards/src/lib.rs (L578-580)
```rust
			let pool_info = Pools::<T>::get(pool_id).ok_or(Error::<T>::NonExistentPool)?;
			let now = T::BlockNumberProvider::current_block_number();
			ensure!(now > pool_info.expiry_block || caller == staker, BadOrigin);
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

**File:** substrate/frame/asset-rewards/src/lib.rs (L786-801)
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
