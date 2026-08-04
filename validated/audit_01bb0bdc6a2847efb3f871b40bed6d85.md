## Analysis: Reward-rounding DoS analog exists in `pallet-asset-rewards`

The Curve/`LiquidityGauge` issue (attacker forces `dt` to stay small so `rate * last_weight * dt` truncates to zero under integer division, freezing the integral) maps directly onto `substrate/frame/asset-rewards`'s reward-per-token accumulator, which recomputes rewards using a block-delta and fixed-point-free integer arithmetic with a very small scaling constant.

### Title
Reward accrual can be permanently frozen via spam calls that force single-block reward-per-token updates - (File: `substrate/frame/asset-rewards/src/lib.rs`)

### Summary
`pallet-asset-rewards` computes `reward_per_token` using an integer formula that multiplies `reward_rate_per_block` by the number of elapsed blocks and a fixed `PRECISION_SCALING_FACTOR` (4096), then divides by `total_tokens_staked`. Any signed account can force `rewardable_blocks_elapsed` to always equal `1` by calling `stake` (with `amount = 0`) or `harvest_rewards` on every block. If `reward_rate_per_block * 1 * 4096 < total_tokens_staked`, each recomputation floors to zero, so `reward_per_token_stored` never advances and all stakers permanently stop earning rewards, exactly mirroring the `LiquidityGauge._checkpoint` issue where an attacker keeps `dt` small enough that `rate * last_weight * dt / _working_supply` rounds to zero.

### Finding Description
`reward_per_token` is computed as: [1](#0-0) 

`rewardable_blocks_elapsed` is `now - pool_info.last_update_block`, and `last_update_block` is reset to `now` on *every* call to `update_pool_rewards`, which happens on every `stake`, `unstake`, and `harvest_rewards` call: [2](#0-1) 

`PRECISION_SCALING_FACTOR` is only `4096`: [3](#0-2) 

`stake` accepts any `amount`, including `0`, is callable by any signed account, and always triggers `update_pool_and_staker_rewards` before touching balances: [4](#0-3) 

`harvest_rewards` similarly forces an update and can be called by anyone once the pool has expired, or by the staker themselves at any time: [5](#0-4) 

Because `ensure_div` here performs floor (truncating) integer division, if an attacker (or any staker who simply calls `stake(pool_id, 0)` — a legal no-op — every single block) forces `rewardable_blocks_elapsed` to always be `1`, then whenever `reward_rate_per_block * 1 * 4096 < total_tokens_staked`, the added term truncates to `0` and `reward_per_token_stored` never increases. Without the spam, a legitimate gap of `N` blocks between interactions would compute `reward_rate_per_block * N * 4096`, which eventually exceeds `total_tokens_staked` and yields a non-zero increment — i.e., rewards would accrue correctly over time. The spam prevents this accumulation by always resetting the elapsed-block window back to `1`, permanently zeroing accrual, similar to the Curve report's `LiquidityGauge._checkpoint` where the attacker manipulates `dt` to always be small.

### Impact Explanation
Any staking-reward pool configured with `reward_rate_per_block * PRECISION_SCALING_FACTOR < total_tokens_staked` (an easily reachable configuration — pools with modest reward rates or larger total stake) can have its reward accrual permanently frozen by an unprivileged account submitting a trivial `stake(pool_id, 0)` or `harvest_rewards` transaction every block. This denies all stakers their expected rewards indefinitely, a direct availability/accounting-correctness violation of the pallet's core purpose.

### Likelihood Explanation
This does not require any privileged role, bridge, or mocked/gated path — `stake` and `harvest_rewards` are plain signed extrinsics reachable by any account, and the attack only costs ordinary per-block transaction fees (no special miner/validator privilege is required, unlike the original Ethereum report which needed a miner to avoid gas costs). The likelihood of the vulnerable configuration (`reward_rate_per_block * 4096 < total_tokens_staked`) occurring in realistic pools is high given the pallet's small, fixed scaling factor compared to `pallet-nomination-pools`'s `FixedU128`-based (10^18 precision) reward counter, which mitigates the same class of rounding issue by design and is validated by its own precision tests (e.g. `smallest_claimable_reward`, `if_small_member_waits_long_enough_they_will_earn_rewards`): [6](#0-5) 

### Recommendation
Short term: increase `PRECISION_SCALING_FACTOR` substantially (e.g., to a `FixedU128`-comparable magnitude, `10^18`-scale) or switch `reward_per_token` accounting to a fixed-point type as used in `pallet-nomination-pools`'s `current_reward_counter`, so that single-block increments do not systematically truncate to zero for realistic `reward_rate_per_block` / `total_tokens_staked` ratios.
Long term: add integration/property tests (e.g., via `#[test]` fuzzing or model-based tests) that specifically simulate an attacker calling `stake(pool_id, 0)`/`harvest_rewards` every block over long durations and assert that `reward_per_token_stored` still converges to the expected value, catching any reintroduction of rounding-to-zero DoS behavior.

### Proof of Concept
1. Create a pool via `create_pool` with `reward_rate_per_block = R` and have `total_tokens_staked` reach a value `S` such that `R * 4096 < S` (e.g., `R = 1`, `S = 5000`).
2. Attacker (any signed account, does not even need to hold the staked asset beyond the ED for the freeze) calls `stake(pool_id, 0)` in every subsequent block.
3. Because `stake` invokes `update_pool_and_staker_rewards` → `reward_per_token`, and `last_update_block` is reset to `now` on each call, `rewardable_blocks_elapsed` is always `1`.
4. `reward_per_token_stored + R * 1 * 4096 / S` computes to `reward_per_token_stored + 0` every block, so `reward_per_token_stored` never increases.
5. Legitimate stakers who call `harvest_rewards` will always receive `0`, confirmed by `derive_rewards`: [7](#0-6)

### Citations

**File:** substrate/frame/asset-rewards/src/lib.rs (L117-118)
```rust
/// Multiplier to maintain precision when calculating rewards.
pub(crate) const PRECISION_SCALING_FACTOR: u16 = 4096;
```

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

**File:** substrate/frame/asset-rewards/src/lib.rs (L568-585)
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

**File:** substrate/frame/asset-rewards/src/lib.rs (L812-824)
```rust
		/// Derives the amount of rewards earned by a staker.
		///
		/// This is a helper function for `update_pool_rewards` and should not be called directly.
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

**File:** substrate/frame/nomination-pools/src/tests.rs (L5957-6024)
```rust
	#[test]
	fn if_small_member_waits_long_enough_they_will_earn_rewards() {
		// create a pool that has a quarter of the current polkadot issuance
		ExtBuilder::default()
			.ed(DOT)
			.min_bond(POLKADOT_TOTAL_ISSUANCE_GENESIS / 4)
			.build_and_execute(|| {
				assert_eq!(
					pool_events_since_last_call(),
					vec![
						Event::Created { depositor: 10, pool_id: 1 },
						Event::Bonded {
							member: 10,
							pool_id: 1,
							bonded: 2500000000000000000,
							joined: true,
						},
						Event::MetadataUpdated { pool_id: 1, caller: 900 },
					]
				);

				// and have a tiny fish join the pool as well..
				Currency::set_balance(&20, 20 * DOT);
				assert_ok!(Pools::join(RuntimeOrigin::signed(20), 10 * DOT, 1));

				// earn some small rewards
				deposit_rewards(DOT / 1000);

				// no point in claiming for 20 (nonetheless, it should be harmless)
				assert!(pending_rewards(20).unwrap().is_zero());
				assert_ok!(Pools::claim_payout(RuntimeOrigin::signed(10)));
				assert_eq!(
					pool_events_since_last_call(),
					vec![
						Event::Bonded {
							member: 20,
							pool_id: 1,
							bonded: 100000000000,
							joined: true
						},
						Event::PaidOut { member: 10, pool_id: 1, payout: 9999997 }
					]
				);

				// earn some small more, still nothing can be claimed for 20, but 10 claims their
				// share.
				deposit_rewards(DOT / 1000);
				assert!(pending_rewards(20).unwrap().is_zero());
				assert_ok!(Pools::claim_payout(RuntimeOrigin::signed(10)));
				assert_eq!(
					pool_events_since_last_call(),
					vec![Event::PaidOut { member: 10, pool_id: 1, payout: 10000000 }]
				);

				// earn some more rewards, this time 20 can also claim.
				deposit_rewards(DOT / 1000);
				assert_eq!(pending_rewards(20).unwrap(), 1);
				assert_ok!(Pools::claim_payout(RuntimeOrigin::signed(10)));
				assert_ok!(Pools::claim_payout(RuntimeOrigin::signed(20)));
				assert_eq!(
					pool_events_since_last_call(),
					vec![
						Event::PaidOut { member: 10, pool_id: 1, payout: 10000000 },
						Event::PaidOut { member: 20, pool_id: 1, payout: 1 }
					]
				);
			});
	}
```
