### Title
`pallet-asset-rewards::cleanup_pool` allows the pool admin to drain reward tokens deposited by third parties before staking ever begins, and without waiting for pool expiry - ([File: substrate/frame/asset-rewards/src/lib.rs])

### Summary
`pallet-asset-rewards` is the FRAME analog of the reward-pool/staking contract described in the external report. Its `cleanup_pool` extrinsic checks only that the caller is the pool admin and that no stakers currently exist, but never checks that the pool has actually expired (`expiry_block` passed) nor that the reward balance being swept was deposited by the admin itself. Because `deposit_reward_tokens` is a permissionless call that lets *any* account fund a pool's reward pot, the admin can claim those third-party-funded rewards immediately, before a single staker has joined — exactly the "rewards withdrawn before staking starts" failure mode described in the MuteAmplifier report.

### Finding Description
`cleanup_pool` is defined at: [1](#0-0) 

```rust
pub fn cleanup_pool(origin: OriginFor<T>, pool_id: PoolId) -> DispatchResult {
    let who = ensure_signed(origin)?;
    let pool_info = Pools::<T>::get(pool_id).ok_or(Error::<T>::NonExistentPool)?;
    ensure!(pool_info.admin == who, BadOrigin);
    let stakers = PoolStakers::<T>::iter_key_prefix(pool_id).next();
    ensure!(stakers.is_none(), Error::<T>::NonEmptyPool);
    let pool_balance = T::Assets::reducible_balance(...);
    T::Assets::transfer(pool_info.reward_asset_id, &pool_info.account, &pool_info.admin, pool_balance, ...)?;
    ...
    Pools::<T>::remove(pool_id);
    ...
}
```

The only two conditions checked are:
1. Caller is the pool `admin`.
2. `PoolStakers` for this pool is empty.

There is no check on `pool_info.expiry_block` (i.e. whether the pool is still meant to be actively distributing rewards) and no check tying the swept `pool_balance` to only the amount the admin itself contributed. Meanwhile, `deposit_reward_tokens` deliberately allows *any* signed account to fund the pool's reward pot directly: [2](#0-1) 

Sequence:
1. Anyone (permissioned by `CreatePoolOrigin`) creates a pool with an `admin` and a future `expiry_block` via `create_pool` [3](#0-2) .
2. A third party calls `deposit_reward_tokens` to fund the pool's reward pot, expecting rewards to accrue to future stakers over `[now, expiry_block]`.
3. Before any account calls `stake`, the pool `admin` calls `cleanup_pool`. Since `PoolStakers` is empty, the `stakers.is_none()` check passes trivially, `expiry_block` is never checked, and the entire reward pot balance (including the third party's deposit) is transferred to the admin and the pool is deleted.

This is structurally identical to the root cause in the report: a withdrawal/rescue-style function checks only a superficial "no active participants" condition (`totalStakers == 0` analog / `stakers.is_none()`) instead of validating whether reward funds are still committed to the program (staking period still active / `endTime` not yet reached in the Solidity report, `expiry_block` not yet reached here).

### Impact Explanation
- Reward funds contributed by a third party (or even by the pool creator itself, if reward accounting were meant to be decoupled from admin control) can be unilaterally withdrawn by the pool `admin` at any time before a first staker joins, defeating the purpose of the reward-pool mechanism — matching Impact #1 in the source report ("the reward system can be broken as rewards can be withdrawn before starting staking").
- Because the pool is also deleted (`Pools::<T>::remove(pool_id)`), any staker who was about to join loses the ability to earn from those pre-funded rewards; the funds are transferred entirely to the admin rather than being locked/returned to depositors, so there is a real, immediate loss of funds for whoever funded the pool via `deposit_reward_tokens`.

### Likelihood Explanation
The likelihood depends on the runtime's configuration of `T::CreatePoolOrigin` — if any signed account can create a pool (a very plausible community/permissionless configuration for reward programs), then any user can create a pool, advertise it for reward deposits, collect third-party deposits, and immediately call `cleanup_pool` to steal the pooled rewards before any staker interacts with the pool. Even if `CreatePoolOrigin` is restricted, the flaw remains a functional defect: the admin can always reclaim reward funds mid-program (before expiry) as long as the staker set is transiently empty (e.g., right after the last staker fully unstakes and before a new one joins), which can also happen unintentionally and break ongoing reward commitments.

### Recommendation
`cleanup_pool` should additionally require that the pool has actually reached its `expiry_block` (i.e. `now >= pool_info.expiry_block`) before allowing the admin to reclaim the remaining balance — mirroring the report's recommendation to check `totalRewards`/timing when there are no active participants but the program is still supposed to be running. Consider also tracking a separate "admin-contributed" balance if the admin is meant to reclaim only their own deposits rather than any co-mingled third-party deposits.

### Proof of Concept
1. `create_pool(admin=Alice, expiry_block=1000, reward_asset=X, staked_asset=Y)` at block 0.
2. Bob (a third party) calls `deposit_reward_tokens(pool_id, 10_000 X)` at block 1, funding the pool's reward pot.
3. No account has called `stake` yet, so `PoolStakers::iter_key_prefix(pool_id)` is empty.
4. Alice calls `cleanup_pool(pool_id)` at block 2 (block 2 << expiry_block 1000).
5. The check `stakers.is_none()` passes; `pool_balance` (10,000 X, Bob's deposit) is transferred entirely to Alice; `Pools` entry for `pool_id` is removed.
6. Bob's 10,000 X reward tokens are now fully controlled by Alice, with no staking having ever occurred, and the reward program is deleted.

### Citations

**File:** substrate/frame/asset-rewards/src/lib.rs (L448-467)
```rust
		#[pallet::call_index(0)]
		pub fn create_pool(
			origin: OriginFor<T>,
			staked_asset_id: Box<T::AssetId>,
			reward_asset_id: Box<T::AssetId>,
			reward_rate_per_block: T::Balance,
			expiry: DispatchTime<BlockNumberFor<T>>,
			admin: Option<T::AccountId>,
		) -> DispatchResult {
			let creator = T::CreatePoolOrigin::ensure_origin(origin)?;
			<Self as RewardsPool<_>>::create_pool(
				&creator,
				*staked_asset_id,
				*reward_asset_id,
				reward_rate_per_block,
				expiry,
				&admin.unwrap_or_else(|| creator.clone()),
			)?;
			Ok(())
		}
```

**File:** substrate/frame/asset-rewards/src/lib.rs (L667-688)
```rust
		/// Convenience method to deposit reward tokens into a pool.
		///
		/// This method is not strictly necessary (tokens could be transferred directly to the
		/// pool pot address), but is provided for convenience so manual derivation of the
		/// account id is not required.
		#[pallet::call_index(7)]
		pub fn deposit_reward_tokens(
			origin: OriginFor<T>,
			pool_id: PoolId,
			amount: T::Balance,
		) -> DispatchResult {
			let caller = ensure_signed(origin)?;
			let pool_info = Pools::<T>::get(pool_id).ok_or(Error::<T>::NonExistentPool)?;
			T::Assets::transfer(
				pool_info.reward_asset_id,
				&caller,
				&pool_info.account,
				amount,
				Preservation::Preserve,
			)?;
			Ok(())
		}
```

**File:** substrate/frame/asset-rewards/src/lib.rs (L690-729)
```rust
		/// Cleanup a pool.
		///
		/// Origin must be the pool admin.
		///
		/// Cleanup storage, release any associated storage cost and return the remaining reward
		/// tokens to the admin.
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
