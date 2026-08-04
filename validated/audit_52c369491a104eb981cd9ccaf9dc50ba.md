This confirms the analog vulnerability class already existed and was fixed. The results show this exact accounting mismatch pattern was found and patched in `pallet-nomination-pools`/`pallet-staking` via [1](#0-0) , which introduced `OnStakingUpdate::on_withdraw` specifically to keep `TotalValueLocked` in sync when staking implicitly withdraws unlocking chunks belonging to a bonded pool stash.

### Title
No current vulnerability — analog accounting bug was already identified and fixed - (File: `substrate/frame/nomination-pools/src/lib.rs`, `substrate/frame/staking-async/src/pallet/impls.rs`)

### Summary
The Fei Pool bug describes a `stakedBalance`/`totalStaked` desynchronization: per-user balance decremented on withdrawal, but the pool-wide total left stale, causing over-release of rewards or a lockup via an underflow check. The closest analog in this codebase is `pallet-nomination-pools`'s `TotalValueLocked` storage item, which tracks the pool-wide total value locked in relation to individual `PoolMembers` balances.

### Finding Description
`TotalValueLocked` is documented as tracking the sum of members' balances, and is explicitly noted as potentially getting out of sync: [2](#0-1) . Historically, when `pallet-staking` performed an *implicit* withdrawal of unlocking chunks belonging to a pool's bonded stash (e.g., triggered as a side effect of another account's `unbond` call filling up `MaxUnlockingChunks`), the nomination-pools pallet's `TotalValueLocked` was not adjusted, since only the explicit pool-level extrinsics (`pool_withdraw_unbonded`, `withdraw_unbonded`) updated it. This is exactly the same root-cause shape as the Fei Pool bug: a total/aggregate counter not being decremented on every real withdrawal code path, only some of them.

This was fixed via a new `OnStakingUpdate::on_withdraw` hook so nomination-pools pallet can adjust `TotalValueLocked` on both implicit and explicit withdrawals, as documented in [1](#0-0) , and exercised by the `automatic_unbonding_pools` test which explicitly checks `TotalValueLocked` stays correct across an implicit staking withdrawal: [3](#0-2) . The current `do_withdraw_unbonded` in `staking-async` also fires the `on_withdraw` listener whenever the ledger total decreases: [4](#0-3) .

Separately, the pallet's own docs acknowledge a residual, intentional discrepancy: calling `pool_withdraw_unbonded` can decrease the bonded account's actual staked balance without adjusting the pallet-internal `UnbondingPool` balances, meaning `TotalValueLocked` may end up *lower* than the sum of members' `total_balance()`, which is the safe direction (no over-payment), as documented and tested: [5](#0-4) [6](#0-5) .

There is also a defensive `try-runtime`/`on_runtime_upgrade` reconciliation migration (`TotalValueLockedSync`) that recomputes and corrects `TotalValueLocked` if found out of sync on-chain: [7](#0-6) .

### Impact Explanation
No exploitable impact for an unprivileged attacker in the current code: the specific desync scenario described in the Fei report (aggregate counter not decremented on withdrawal, permitting over-redemption or lockup via underflow) was already identified, fixed via `on_withdraw`, and is regression-tested. The remaining, currently-known discrepancy direction (`TotalValueLocked` lower than member balances) does not enable extra token release and is not an underflow/DoS vector, since it's the mirror-safe direction of the bug class.

### Likelihood Explanation
Not applicable — the once-existing issue is patched and covered by tests; no currently reachable code path reproduces the "increment on deposit, but total left stale on withdrawal, causing over-redemption or underflow-revert lockup" pattern from the report.

### Recommendation
No action required for this specific pattern. If auditing further, verify all future withdrawal-adjacent code paths (e.g., new slashing or migration flows) call `T::EventListeners::on_withdraw` / equivalent hooks so `TotalValueLocked` stays reconciled, and keep the `TotalValueLockedSync` migration available as a safety net.

### Proof of Concept
Not applicable — no reachable/reproducible vulnerability found in the current codebase; historical bug and fix referenced above via `prdoc/1.8.0/pr_3052.prdoc` and associated tests.

### Citations

**File:** prdoc/1.8.0/pr_3052.prdoc (L1-15)
```text
title: "Fixes a scenario where a nomination pool's `TotalValueLocked` is out of sync due to staking's implicit withdraw"

doc:
  - audience: Runtime Dev
    description: |
      The nomination pools pallet `TotalValueLocked` may get out of sync if the staking pallet
      does implicit withdrawal of unlocking chunks belonging to a bonded pool stash. This fix
      is based on a new method on the `OnStakingUpdate` traits, `on_withdraw`, which allows the
      nomination pools pallet to adjust the `TotalValueLocked` every time there is an implicit or
      explicit withdrawal from a bonded pool's stash.

crates: 
  - name: "pallet-nomination-pools"
  - name: "pallet-staking"
  - name: "sp-staking"
```

**File:** substrate/frame/nomination-pools/src/lib.rs (L1745-1750)
```rust
	///
	/// This might be lower but never higher than the sum of `total_balance` of all [`PoolMembers`]
	/// because calling `pool_withdraw_unbonded` might decrease the total stake of the pool's
	/// `bonded_account` without adjusting the pallet-internal `UnbondingPool`'s.
	#[pallet::storage]
	pub type TotalValueLocked<T: Config> = StorageValue<_, BalanceOf<T>, ValueQuery>;
```

**File:** substrate/frame/election-provider-multi-phase/test-staking-e2e/src/lib.rs (L376-397)
```rust
		// now unbonding 3 will work, although the pool's ledger still has the unlocking chunks
		// filled up.
		assert_ok!(Pools::unbond(RuntimeOrigin::signed(3), 3, 10));
		assert_eq!(unlocking_chunks_of(pool_bonded_account), 1);

		assert_eq!(
			staking_events(),
			[
				// auto-withdraw happened as expected to release 2's unbonding funds, but the funds
				// were not transferred to 2 and stay in the pool's transferrable balance instead.
				pallet_staking::Event::Withdrawn { stash: pool_bonded_account, amount: 10 },
				pallet_staking::Event::Unbonded { stash: pool_bonded_account, amount: 10 }
			]
		);

		// balance of the pool remains the same, it hasn't withdraw explicitly from the pool yet.
		assert_eq!(delegated_balance_for(pool_bonded_account), 25);
		// but the locked amount in the pool's account decreases due to the auto-withdraw:
		assert_eq!(staked_before_withdraw_pool - 10, staked_amount_for(pool_bonded_account));

		// TVL correctly updated.
		assert_eq!(TotalValueLocked::<Runtime>::get(), 25 - 10);
```

**File:** substrate/frame/staking-async/src/pallet/impls.rs (L305-314)
```rust
		// `old_total` should never be less than the new total because
		// `consolidate_unlocked` strictly subtracts balance.
		if new_total < old_total {
			// Already checked that this won't overflow by entry condition.
			let value = old_total.defensive_saturating_sub(new_total);
			Self::deposit_event(Event::<T>::Withdrawn { stash, amount: value });

			// notify listeners.
			T::EventListeners::on_withdraw(controller, value);
		}
```

**File:** substrate/frame/nomination-pools/src/tests.rs (L3759-3791)
```rust
	fn pool_withdraw_unbonded_creates_tvl_diff() {
		ExtBuilder::default().add_members(vec![(20, 10)]).build_and_execute(|| {
			// Given 10 unbond'ed directly against the pool account
			assert_ok!(Pools::unbond(RuntimeOrigin::signed(20), 20, 5));

			assert_eq!(StakingMock::active_stake(&default_bonded_account()), Ok(15));
			assert_eq!(StakingMock::total_stake(&default_bonded_account()), Ok(20));
			assert_eq!(pool_balance(1), 20);
			assert_eq!(TotalValueLocked::<T>::get(), 20);

			// When
			CurrentEra::set(StakingMock::current_era() + StakingMock::bonding_duration() + 1);
			assert_ok!(Pools::pool_withdraw_unbonded(RuntimeOrigin::signed(10), 1, 0));
			assert_eq!(TotalValueLocked::<T>::get(), 15);

			let member_balance = PoolMembers::<T>::iter()
				.map(|(_, member)| member.total_balance())
				.reduce(|acc, total_balance| acc + total_balance)
				.unwrap_or_default();

			// Then their unbonding balance is no longer locked
			assert_eq!(StakingMock::active_stake(&default_bonded_account()), Ok(15));
			assert_eq!(StakingMock::total_stake(&default_bonded_account()), Ok(15));
			assert_eq!(pool_balance(1), 20);

			// The difference between TVL and member_balance is exactly the difference between
			// `pool balance` (sum of all balance delegated to pool) and the `staked balance`.
			// This is the withdrawn funds from the pool stake that has not yet been claimed by the
			// respective members.
			let non_locked_balance =
				pool_balance(1) - StakingMock::total_stake(&default_bonded_account()).unwrap();
			assert_eq!(member_balance, TotalValueLocked::<T>::get() + non_locked_balance);
		});
```

**File:** substrate/frame/nomination-pools/src/migration.rs (L61-94)
```rust
	/// Checks and updates `TotalValueLocked` if out of sync.
	pub struct TotalValueLockedSync<T>(core::marker::PhantomData<T>);
	impl<T: Config> OnRuntimeUpgrade for TotalValueLockedSync<T> {
		#[cfg(feature = "try-runtime")]
		fn pre_upgrade() -> Result<Vec<u8>, TryRuntimeError> {
			Ok(Vec::new())
		}

		fn on_runtime_upgrade() -> Weight {
			let migrated = BondedPools::<T>::count();

			// recalculate the `TotalValueLocked` to compare with the current on-chain TVL which may
			// be out of sync.
			let tvl: BalanceOf<T> = helpers::calculate_tvl_by_total_stake::<T>();
			let onchain_tvl = TotalValueLocked::<T>::get();

			let writes = if tvl != onchain_tvl {
				TotalValueLocked::<T>::set(tvl);

				log!(
					info,
					"on-chain TVL was out of sync, update. Old: {:?}, new: {:?}",
					onchain_tvl,
					tvl
				);

				// writes: onchain version + set total value locked.
				2
			} else {
				log!(info, "on-chain TVL was OK: {:?}", tvl);

				// writes: onchain version write.
				1
			};
```
