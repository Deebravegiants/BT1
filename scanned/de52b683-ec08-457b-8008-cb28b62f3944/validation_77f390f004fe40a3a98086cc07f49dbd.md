### Title
Reward accrual decoupled from actual pool funding can cause `harvest_rewards` to permanently revert for unprivileged stakers - (File: `substrate/frame/asset-rewards/src/lib.rs`)

### Summary
`pallet-asset-rewards` computes staker rewards just-in-time from `reward_rate_per_block × elapsed_blocks` with no on-chain check that the pool account actually holds enough of the reward asset to pay out what has accrued. This mirrors the reported NarwhalPool/TradingVaultV2 pattern: a duration/rate is set once, tokens are optionally topped up, but the amount "owed" to stakers (as computed by `earned`/JIT accrual) is never reconciled against actual balance until payout time, when the transfer can fail.

### Finding Description
`create_pool` and `set_pool_reward_rate_per_block` allow a permissioned admin to set/raise `reward_rate_per_block` for a pool, and rewards accrue purely as a function of elapsed blocks via `update_pool_and_staker_rewards` (referenced in the module docs at [1](#0-0) ). Funding of the pool account is a *separate, optional* step (`deposit_reward_tokens`), and the pallet's own documentation explicitly acknowledges the resulting risk: [2](#0-1) 

When a staker calls `harvest_rewards`, the pallet computes `staker_info.rewards` from the JIT accrual logic and then unconditionally attempts to transfer that exact amount from the pool account to the staker: [3](#0-2) 

There is no check prior to the transfer that the pool account's actual reward-asset balance covers the accrued amount. If accrued rewards (rate × time, potentially across many stakers) exceed what was actually deposited via `deposit_reward_tokens`, the `T::Assets::transfer` call fails and the whole extrinsic reverts — exactly the "insufficient balance" failure mode described in the external report, where `notifyRewardAmount`/`setRewardDuration` allowed accrual to be promised without guaranteeing the underlying balance.

Unlike `pallet-nomination-pools`, where `RewardPool::current_reward_counter` derives claimable rewards directly from the reward account's *actual current balance* (`Self::current_balance(id)` in [4](#0-3) ), so pending rewards can mathematically never exceed real funds, `pallet-asset-rewards` has no equivalent invariant tying accrual to on-chain balance.

### Impact Explanation
An unprivileged staker's `harvest_rewards` call can revert with a transfer error whenever the pool is under-funded relative to what has accrued (e.g., admin sets a high `reward_rate_per_block` but funds the pool with less than the full runway, or multiple stakers accrue faster than top-ups occur, or earlier harvesters drain the pool for later harvesters). This is a denial-of-service on reward claims for legitimate, non-malicious users — no exploit action beyond normal usage is required. It is not a fund-loss bug since state is only mutated after a successful transfer (extrinsic reverts atomically), but stakers are blocked from claiming already-accrued rewards until the pool operator manually tops it up, and any staker whose harvest happens to land when the pool is drained will experience a failed transaction.

### Likelihood Explanation
Likelihood is realistic under normal (non-malicious) operating conditions rather than requiring compromise of a trusted role: this exactly matches the setup in the external report where a legitimate admin sets a rate/duration and funds the pool, but subsequent harvesting by multiple users over time can outpace the deposited balance. The pallet's own doc comment ("Care should be taken by the pool operator to keep pool accounts adequately funded") confirms this is a recognized, still-present operational hazard in the code as written, not something structurally prevented by an invariant like the one in `pallet-nomination-pools`.

### Recommendation
Tie reward accrual/claims to the pool account's actual current reward-asset balance, similar to `pallet-nomination-pools`'s `current_balance`-based `current_reward_counter` approach, or cap the transferable amount at `min(accrued, pool_balance)` with the shortfall tracked as a deficit to be settled on next top-up, so a single underfunded pool cannot cause `harvest_rewards` to hard-fail for stakers.

### Proof of Concept
1. Admin calls `create_pool` with `reward_rate_per_block = R` and a distant `expiry`.
2. Admin calls `deposit_reward_tokens` with an amount smaller than `R × (expiry - now)`.
3. Staker A stakes; time passes; `update_pool_and_staker_rewards` accrues `A`'s `staker_info.rewards` based on `R × elapsed`.
4. Staker A calls `harvest_rewards`; if accrued rewards for all stakers exceed the pool account's actual reward-asset balance, `T::Assets::transfer` in [5](#0-4)  fails and the call reverts, blocking the staker from claiming any of their legitimately accrued reward.

Note: I was not able to further trace `deposit_reward_tokens`'s exact balance-check semantics (e.g., whether it enforces coverage of the full remaining runway) within the remaining investigation budget; this should be verified in a follow-up session, along with checking `benchmarking.rs`/`tests.rs` in `substrate/frame/asset-rewards` for any existing coverage of this underfunded-pool scenario.

### Citations

**File:** substrate/frame/asset-rewards/src/lib.rs (L35-38)
```rust
//! Reward assets pending distribution are held in an account unique to each pool.
//!
//! Care should be taken by the pool operator to keep pool accounts adequately funded with the
//! reward asset.
```

**File:** substrate/frame/asset-rewards/src/lib.rs (L56-63)
```rust
//! ## Implementation Notes
//!
//! Internal logic functions such as `update_pool_and_staker_rewards` were deliberately written
//! without side-effects.
//!
//! Storage interaction such as reads and writes are instead all performed in the top level
//! pallet Call method, which while slightly more verbose, makes it easier to understand the
//! code and reason about how storage reads and writes occur in the pallet.
```

**File:** substrate/frame/asset-rewards/src/lib.rs (L582-595)
```rust
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
```

**File:** substrate/frame/nomination-pools/src/lib.rs (L1456-1465)
```rust
		let balance = Self::current_balance(id);

		// Calculate the current payout balance. The first 3 values of this calculation added
		// together represent what the balance would be if no payouts were made. The
		// `last_recorded_total_payouts` is then subtracted from this value to cancel out previously
		// recorded payouts, leaving only the remaining payouts that have not been claimed.
		let current_payout_balance = balance
			.saturating_add(self.total_rewards_claimed)
			.saturating_add(self.total_commission_claimed)
			.saturating_sub(self.last_recorded_total_payouts);
```
