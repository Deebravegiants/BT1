This is a genuine confirmed finding: `pallet-asset-rewards` uses a precision scaling factor of only **4096 (~2^12, ~4.1e3)**, far smaller than the `1e18`/`1e27` values discussed in the report, making the analog precision-loss bug directly applicable and arguably worse here.

### Title
`reward_per_token` rounds to zero due to insufficient `PRECISION_SCALING_FACTOR` in `pallet-asset-rewards` - (File: `substrate/frame/asset-rewards/src/lib.rs`)

### Summary
`pallet-asset-rewards` computes a per-block accumulator (`reward_per_token_stored`) analogous to `secRewardsPerShare` in the referenced report. The scaling constant used to preserve precision, `PRECISION_SCALING_FACTOR`, is set to `4096` [1](#0-0)  — far too small relative to realistic `total_tokens_staked` values (which, like `cNOTE` in the report, can easily exceed `1e18` in base units). This mirrors the exact rounding-to-zero root cause from the external report, just with an even smaller scaling factor.

### Finding Description
`reward_per_token` computes:
```
reward_per_token_stored + (reward_rate_per_block * blocks_elapsed * PRECISION_SCALING_FACTOR) / total_tokens_staked
``` [2](#0-1) 

If `reward_rate_per_block * blocks_elapsed * 4096 < total_tokens_staked`, the division truncates to `0`, exactly the "M-01" bug pattern from the report. Since staked asset amounts are `fungibles` balances with typical 18-decimals precision (or any asset with a reasonably large integer supply), it is trivial for `total_tokens_staked` to exceed `4096 * reward_rate_per_block` for extended periods, especially for low reward-rate pools or pools with large total stake. `derive_rewards` then divides the resulting delta again by `PRECISION_SCALING_FACTOR` [3](#0-2) , so any rounding-to-zero in `reward_per_token` permanently loses that block's reward slice — there is no compensation or carry-over mechanism.

### Impact Explanation
Stakers permanently lose yield whenever `reward_per_token` rounds down to zero per-block-delta, exactly the "loss of yield" impact accepted as Medium severity in the referenced report. Because `update_pool_and_staker_rewards` is called before every staker interaction (stake/unstake/claim) [4](#0-3) , frequent interactions with a large-supply pool and modest reward rate will silently zero out rewards for extended intervals, and the lost fraction is never recovered since `reward_per_token_stored` only accumulates the (rounded-down) delta.

### Likelihood Explanation
This requires no privileged role and is reachable by any user who stakes into a pool via the standard `stake`/`unstake`/`claim_rewards` flow — the pool creator only needs to set a `reward_rate_per_block` that is small relative to `total_tokens_staked * (1/4096)`, which is a very plausible configuration (e.g. any pool with staked-asset amounts denominated with 12–18 decimals and modest reward emission). This is a realistic, permissionless-triggerable scenario, not a contrived edge case.

### Recommendation
Increase `PRECISION_SCALING_FACTOR` substantially (e.g., to `1e18` or a `U256`-based intermediate calculation as already done elsewhere in the codebase, such as `balance_to_point`/`point_to_balance` in `pallet-nomination-pools` which use `U256` for the multiply-then-divide step [5](#0-4) ). Alternatively, adopt a `FixedU128`/`RewardCounter`-style fixed-point accumulator like `pallet-nomination-pools` uses for its reward pool, which was explicitly designed with accuracy analysis to avoid this exact rounding-to-zero class of bug [6](#0-5) .

### Proof of Concept
1. Create an asset-rewards pool with `staked_asset` having 12-decimal precision, `total_tokens_staked = 10_000 * 10^12` (10,000 tokens), and `reward_rate_per_block = 1000` (a small reward emission, e.g. 1000 raw units/block, well below 1 full token/block).
2. Stake tokens, wait `blocks_elapsed = 1` block, then call `reward_per_token`:
   `1000 * 1 * 4096 / (10_000 * 10^12) = 4_096_000 / 10^16 = 0` (integer division truncates to 0).
3. Repeat over many blocks with same conditions: as long as `reward_rate_per_block * blocks_elapsed * 4096 < total_tokens_staked`, `reward_per_token_stored` never increases, and `derive_rewards` computes `0` for stakers via `staker_info.amount.ensure_mul(reward_per_token.ensure_sub(...)).ensure_div(PRECISION_SCALING_FACTOR)` [3](#0-2) , so stakers accumulate zero rewards despite pool emissions occurring, directly reproducing the "M-01" precision-loss vulnerability class.

### Citations

**File:** substrate/frame/asset-rewards/src/lib.rs (L117-118)
```rust
/// Multiplier to maintain precision when calculating rewards.
pub(crate) const PRECISION_SCALING_FACTOR: u16 = 4096;
```

**File:** substrate/frame/asset-rewards/src/lib.rs (L746-765)
```rust
		/// Computes update pool and staker reward state.
		///
		/// Should be called prior to any operation involving a staker.
		///
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

**File:** substrate/frame/asset-rewards/src/lib.rs (L815-824)
```rust
		fn derive_rewards(
			staker_info: &PoolStakerInfo<T::Balance>,
			reward_per_token: &T::Balance,
		) -> Result<T::Balance, DispatchError> {
			Ok(staker_info
				.amount
				.ensure_mul(reward_per_token.ensure_sub(staker_info.reward_per_token_paid)?)?
				.ensure_div(PRECISION_SCALING_FACTOR.into())?
				.ensure_add(staker_info.rewards)?)
		}
```

**File:** substrate/frame/nomination-pools/src/lib.rs (L1672-1686)
```rust
		type RuntimeFreezeReason: From<FreezeReason>;

		/// The type that is used for reward counter.
		///
		/// The arithmetic of the reward counter might saturate based on the size of the
		/// `Currency::Balance`. If this happens, operations fails. Nonetheless, this type should be
		/// chosen such that this failure almost never happens, as if it happens, the pool basically
		/// needs to be dismantled (or all pools migrated to a larger `RewardCounter` type, which is
		/// a PITA to do).
		///
		/// See the inline code docs of `Member::pending_rewards` and `RewardPool::update_recorded`
		/// for example analysis. A [`sp_runtime::FixedU128`] should be fine for chains with balance
		/// types similar to that of Polkadot and Kusama, in the absence of severe slashing (or
		/// prevented via a reasonable `MaxPointsToBalance`), for many many years to come.
		type RewardCounter: FixedPointNumber + MaxEncodedLen + TypeInfo + Default + codec::FullCodec;
```

**File:** substrate/frame/nomination-pools/src/lib.rs (L3473-3499)
```rust
	/// Calculate the equivalent point of `new_funds` in a pool with `current_balance` and
	/// `current_points`.
	fn balance_to_point(
		current_balance: BalanceOf<T>,
		current_points: BalanceOf<T>,
		new_funds: BalanceOf<T>,
	) -> BalanceOf<T> {
		let u256 = T::BalanceToU256::convert;
		let balance = T::U256ToBalance::convert;
		match (current_balance.is_zero(), current_points.is_zero()) {
			(_, true) => new_funds.saturating_mul(POINTS_TO_BALANCE_INIT_RATIO.into()),
			(true, false) => {
				// The pool was totally slashed.
				// This is the equivalent of `(current_points / 1) * new_funds`.
				new_funds.saturating_mul(current_points)
			},
			(false, false) => {
				// Equivalent to (current_points / current_balance) * new_funds
				balance(
					u256(current_points)
						.saturating_mul(u256(new_funds))
						// We check for zero above
						.div(u256(current_balance)),
				)
			},
		}
	}
```
