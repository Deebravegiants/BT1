I found a valid, unpatched analog. This codebase already contains a documented fix (`prdoc/pr_12397.prdoc`) for exactly this vulnerability class in `set_commission_max`, but the same root cause remains present in a **different**, unpatched code path: lowering `GlobalMaxCommission` via `Call::set_configs`.

### Title
Lowering `GlobalMaxCommission` via `set_configs` retroactively re-rates already-accrued pool commission without a reward-pool snapshot, causing loss of commission owed to the payee - (File: `substrate/frame/nomination-pools/src/lib.rs`)

### Summary
`pallet-nomination-pools` already fixed one instance of this exact bug class: `set_commission_max` now snapshots the `RewardPool` via `update_records` *before* force-lowering `commission.current` [1](#0-0) , exactly as documented in `prdoc/pr_12397.prdoc` [2](#0-1) . However, `GlobalMaxCommission` — a second, global lever that also clamps the effective commission rate via `Commission::current()` — can still be lowered through `Call::set_configs` with **no snapshot of any pool's reward state at all** [3](#0-2) . Because `current()` is evaluated lazily at the next `update_records` call using whatever `GlobalMaxCommission` value happens to be in storage at that time [4](#0-3) , all commission that accrued since the pool's *last* snapshot — even commission that accrued while the pool's local rate was legitimately below the old global cap — gets retroactively re-rated down to the new lower global cap, and the difference is silently redirected to pool members instead of the commission payee.

### Finding Description
`RewardPool::update_records` computes `current_reward_counter` using whatever commission rate is passed in, and that rate is `bonded_pool.commission.current()` [5](#0-4) . `current()` is defined as:
```rust
fn current(&self) -> Perbill {
    self.current
        .as_ref()
        .map_or(Perbill::zero(), |(c, _)| *c)
        .min(GlobalMaxCommission::<T>::get().unwrap_or(Bounded::max_value()))
}
``` [4](#0-3) 

This means the rate used to split `current_payout_balance` between pool members and the commission payee in `current_reward_counter` [6](#0-5)  is not fixed at the time rewards accrued — it depends on the value of `GlobalMaxCommission` in storage the moment `update_records` is next invoked. `set_configs` mutates `GlobalMaxCommission` directly via `ConfigOp` with no iteration over `BondedPools`/`RewardPools` and no call to `update_records` for any pool [7](#0-6) .

Consequently, if a pool's local `commission.current` is, say, 90% (a rate that was valid because `GlobalMaxCommission` was 90% at the time it was set — see `set_commission`'s own global-max check at [8](#0-7) ), and rewards accrue for a period, then governance lowers `GlobalMaxCommission` to 50% via `set_configs`, the next `join`/`bond_extra`/`unbond`/`set_commission`/`claim_commission` call for that pool will call `update_records` and compute the commission owed for the *entire unclaimed accrual window* using the new 50% rate, not the 90% that was actually in effect while the balance accrued. The differential (40% of the accrued payout balance) is credited to `new_pending_rewards` (i.e., pool members) instead of `new_pending_commission` (the payee) [9](#0-8) .

This is structurally identical to the fixed `set_commission_max` bug: a lowering of an effective-commission-bounding parameter that is applied lazily at the next snapshot instead of being pre-snapshotted, causing already-accrued value to be re-rated and misallocated. The pallet's own test `global_max_caps_max_commission_payout` demonstrates the mechanics of `GlobalMaxCommission` retroactively capping payouts at claim time [10](#0-9) , but that test only deposits rewards *after* lowering the global max — it does not exercise (and therefore does not prove safety for) the case where rewards accrue *before* the global max is lowered, which is the loss-causing scenario.

### Impact Explanation
The commission payee (which can be a third party distinct from the pool root/depositor, per `set_commission`'s `(Perbill, AccountId)` payee tuple) permanently loses commission that had already legitimately accrued under a previously-valid, previously-checked commission rate, with the shortfall redistributed to pool members. This is a direct loss of funds for an account with no way to prevent or foresee it, mirroring the "boost period" report: the `RewardsDistributor`-style checkpoint variable (`GlobalMaxCommission`, analogous to boost period config) is mutated without first finalizing outstanding accruals against the old rate.

### Likelihood Explanation
Likelihood is low, matching the original report's rating: `set_configs` is gated by `T::AdminOrigin`, typically governance/root, so this requires a deliberate (not malicious, just ordinary) governance action to lower `GlobalMaxCommission` while pools have unclaimed/unsnapshotted rewards outstanding — a realistic, foreseeable operational scenario rather than an attacker-controlled path, exactly as in the referenced report and in the already-patched `set_commission_max` sibling issue.

### Recommendation
Apply the same fix pattern already used for `set_commission_max`: before committing a lowered `GlobalMaxCommission` in `set_configs`, either (a) iterate `RewardPools`/`BondedPools` and call `update_records` for every pool whose `commission.current()` exceeds the new global max to snapshot commission at the old effective rate, or (b) disallow lowering `GlobalMaxCommission` in a single unbounded call and instead require it be staged/throttled with a mechanism that forces per-pool snapshotting (e.g. lazily snapshot-on-read the moment a pool's current commission would exceed the new global max, storing the pre-cut rate rather than recomputing it from live storage).

### Proof of Concept
1. Pool 1 sets `commission.current = 90%` via `set_commission` (valid since `GlobalMaxCommission == 90%`) [11](#0-10) .
2. `deposit_rewards(100)` — 100 units accrue to the reward pool with no snapshot in between.
3. Governance calls `set_configs` with `global_max_commission: ConfigOp::Set(Perbill::from_percent(50))` [12](#0-11)  — no `update_records` is invoked for pool 1.
4. Any subsequent trigger of `update_records` (e.g. `claim_commission` or a member `join`) computes commission for the whole 100-unit accrual using `current() == min(90%, 50%) == 50%`, i.e., 50 owed to the payee, instead of the 90 that had actually accrued while the 90% rate was in force — an unrecoverable 40-unit loss to the payee, credited instead to members, mirroring the exact mechanics validated for the already-patched `set_commission_max` case in `set_commission_max_snapshots_rewards_before_lowering_current` [13](#0-12) .

### Citations

**File:** substrate/frame/nomination-pools/src/lib.rs (L843-850)
```rust
	/// Gets the pool's current commission, or returns Perbill::zero if none is set.
	/// Bounded to global max if current is greater than `GlobalMaxCommission`.
	fn current(&self) -> Perbill {
		self.current
			.as_ref()
			.map_or(Perbill::zero(), |(c, _)| *c)
			.min(GlobalMaxCommission::<T>::get().unwrap_or(Bounded::max_value()))
	}
```

**File:** substrate/frame/nomination-pools/src/lib.rs (L862-865)
```rust
				ensure!(
					commission <= &GlobalMaxCommission::<T>::get().unwrap_or(Bounded::max_value()),
					Error::<T>::CommissionExceedsGlobalMaximum
				);
```

**File:** substrate/frame/nomination-pools/src/lib.rs (L1408-1417)
```rust
	fn update_records(
		&mut self,
		id: PoolId,
		bonded_points: BalanceOf<T>,
		commission: Perbill,
	) -> Result<(), Error<T>> {
		let balance = Self::current_balance(id);

		let (current_reward_counter, new_pending_commission) =
			self.current_reward_counter(id, bonded_points, commission)?;
```

**File:** substrate/frame/nomination-pools/src/lib.rs (L1462-1471)
```rust
		let current_payout_balance = balance
			.saturating_add(self.total_rewards_claimed)
			.saturating_add(self.total_commission_claimed)
			.saturating_sub(self.last_recorded_total_payouts);

		// Split the `current_payout_balance` into claimable rewards and claimable commission
		// according to the current commission rate.
		let new_pending_commission = commission * current_payout_balance;
		let new_pending_rewards = current_payout_balance.saturating_sub(new_pending_commission);

```

**File:** substrate/frame/nomination-pools/src/lib.rs (L2740-2778)
```rust
		pub fn set_configs(
			origin: OriginFor<T>,
			min_join_bond: ConfigOp<BalanceOf<T>>,
			min_create_bond: ConfigOp<BalanceOf<T>>,
			max_pools: ConfigOp<u32>,
			max_members: ConfigOp<u32>,
			max_members_per_pool: ConfigOp<u32>,
			global_max_commission: ConfigOp<Perbill>,
		) -> DispatchResult {
			T::AdminOrigin::ensure_origin(origin)?;

			macro_rules! config_op_exp {
				($storage:ty, $op:ident) => {
					match $op {
						ConfigOp::Noop => (),
						ConfigOp::Set(v) => <$storage>::put(v),
						ConfigOp::Remove => <$storage>::kill(),
					}
				};
			}

			config_op_exp!(MinJoinBond::<T>, min_join_bond);
			config_op_exp!(MinCreateBond::<T>, min_create_bond);
			config_op_exp!(MaxPools::<T>, max_pools);
			config_op_exp!(MaxPoolMembers::<T>, max_members);
			config_op_exp!(MaxPoolMembersPerPool::<T>, max_members_per_pool);
			config_op_exp!(GlobalMaxCommission::<T>, global_max_commission);

			Self::deposit_event(Event::<T>::GlobalParamsUpdated {
				min_join_bond: MinJoinBond::<T>::get(),
				min_create_bond: MinCreateBond::<T>::get(),
				max_pools: MaxPools::<T>::get(),
				max_members: MaxPoolMembers::<T>::get(),
				max_members_per_pool: MaxPoolMembersPerPool::<T>::get(),
				global_max_commission: GlobalMaxCommission::<T>::get(),
			});

			Ok(())
		}
```

**File:** substrate/frame/nomination-pools/src/lib.rs (L2965-2995)
```rust
		pub fn set_commission(
			origin: OriginFor<T>,
			pool_id: PoolId,
			new_commission: Option<(Perbill, T::AccountId)>,
		) -> DispatchResult {
			let who = ensure_signed(origin)?;
			let mut bonded_pool = BondedPool::<T>::get(pool_id).ok_or(Error::<T>::PoolNotFound)?;
			// ensure pool is not in an un-migrated state.
			ensure!(!Self::api_pool_needs_delegate_migration(pool_id), Error::<T>::NotMigrated);

			ensure!(bonded_pool.can_manage_commission(&who), Error::<T>::DoesNotHavePermission);

			let mut reward_pool = RewardPools::<T>::get(pool_id)
				.defensive_ok_or::<Error<T>>(DefensiveError::RewardPoolNotFound.into())?;
			// IMPORTANT: make sure that everything up to this point is using the current commission
			// before it updates. Note that `try_update_current` could still fail at this point.
			reward_pool.update_records(
				pool_id,
				bonded_pool.points,
				bonded_pool.commission.current(),
			)?;
			RewardPools::insert(pool_id, reward_pool);

			bonded_pool.commission.try_update_current(&new_commission)?;
			bonded_pool.put();
			Self::deposit_event(Event::<T>::PoolCommissionUpdated {
				pool_id,
				current: new_commission,
			});
			Ok(())
		}
```

**File:** substrate/frame/nomination-pools/src/lib.rs (L3016-3029)
```rust
			let mut reward_pool = RewardPools::<T>::get(pool_id)
				.defensive_ok_or::<Error<T>>(DefensiveError::RewardPoolNotFound.into())?;
			// IMPORTANT: snapshot rewards accrued at the current commission before `try_update_max`
			// can force-lower it. Otherwise rewards accrued since the last snapshot would be
			// re-rated at the new (lower) rate and the differential credited to members instead
			// of the commission payee. Mirrors the ordering in `set_commission`.
			reward_pool.update_records(
				pool_id,
				bonded_pool.points,
				bonded_pool.commission.current(),
			)?;
			RewardPools::insert(pool_id, reward_pool);

			bonded_pool.commission.try_update_max(pool_id, max_commission)?;
```

**File:** prdoc/pr_12397.prdoc (L1-12)
```text
title: 'nomination-pools: snapshot rewards before `set_commission_max` lowers current commission'
doc:
- audience: Runtime Dev
  description: |-
    `set_commission_max` force-lowers `commission.current` (via `try_update_max`) when the new max
    is below the active rate, but did not first call `update_records`. Rewards accrued at the higher
    rate since the last snapshot were therefore re-rated at the new lower rate on the next
    `update_records`, crediting the differential `(old_current - new_max) * accrued` to members
    instead of the commission payee.

    The fix snapshots the reward pool at the current commission before the cut, mirroring the
    ordering already used in `set_commission`.
```

**File:** substrate/frame/nomination-pools/src/tests.rs (L6990-7031)
```rust
	#[test]
	fn set_commission_max_snapshots_rewards_before_lowering_current() {
		// `set_commission_max` force-lowers `current` when the new max is below it. Rewards that
		// accrued at the higher rate since the last snapshot must stay owed to the payee at that
		// higher rate, not be re-rated at the new lower rate and leaked to members.
		ExtBuilder::default().build_and_execute(|| {
			let pool_id = 1;
			let payee = 900;
			let _ = Currency::set_balance(&payee, 5);

			// GIVEN: commission is 50% (this snapshots the still-empty reward pool)...
			assert_ok!(Pools::set_commission(
				RuntimeOrigin::signed(900),
				pool_id,
				Some((Perbill::from_percent(50), payee))
			));
			// ...and 100 of rewards accrue with no intervening snapshot (no claim/bond happens).
			deposit_rewards(100);
			assert_eq!(RewardPool::<Runtime>::current_balance(pool_id), 100);
			assert_eq!(RewardPools::<Runtime>::get(pool_id).unwrap().total_commission_pending, 0);

			// WHEN: root force-lowers max commission to 20%, cutting `current` from 50% to 20%.
			assert_ok!(Pools::set_commission_max(
				RuntimeOrigin::signed(900),
				pool_id,
				Perbill::from_percent(20)
			));

			// THEN: the 100 that accrued at 50% was snapshotted before the cut, so 50 is owed to
			// the payee. Without the pre-cut snapshot this would be 20% * 100 = 20.
			assert_eq!(RewardPools::<Runtime>::get(pool_id).unwrap().total_commission_pending, 50);

			// AND: claiming commission pays the payee the pre-cut 50, not the post-cut 20.
			let _ = pool_events_since_last_call();
			assert_ok!(Pools::claim_commission(RuntimeOrigin::signed(payee), pool_id));
			assert_eq!(
				pool_events_since_last_call(),
				vec![Event::PoolCommissionClaimed { pool_id, commission: 50 }]
			);
			assert_eq!(Currency::free_balance(&payee), 5 + 50);
			assert_eq!(RewardPools::<Runtime>::get(pool_id).unwrap().total_commission_claimed, 50);
		})
```

**File:** substrate/frame/nomination-pools/src/tests.rs (L7428-7458)
```rust
			// Set pool commission to 90% and then set global max commission to 80%.
			assert_ok!(Pools::set_commission(
				RuntimeOrigin::signed(900),
				bonded_pool.id,
				Some((Perbill::from_percent(90), 2)),
			));
			GlobalMaxCommission::<Runtime>::set(Some(Perbill::from_percent(80)));

			// The pool earns 10 points
			deposit_rewards(10);

			// execute the payout
			assert_ok!(Pools::do_reward_payout(
				&10,
				&mut member,
				&mut BondedPool::<Runtime>::get(1).unwrap(),
				&mut reward_pool
			));

			// Confirm the commission was only 8 points out of 10 points, and the payout was 2 out
			// of 10 points, reflecting the 80% global max commission.
			assert_eq!(
				pool_events_since_last_call(),
				vec![
					Event::PoolCommissionUpdated {
						pool_id: 1,
						current: Some((Perbill::from_percent(90), 2))
					},
					Event::PaidOut { member: 10, pool_id: 1, payout: 2 },
				]
			);
```
