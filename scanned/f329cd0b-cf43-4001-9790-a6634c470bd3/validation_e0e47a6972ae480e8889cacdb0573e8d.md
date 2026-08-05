### Title
Shared bonded-pool staking ledger allows a griefing member to DoS `unbond`/`withdraw_unbonded` for other members of the same nomination pool - (File: `substrate/frame/nomination-pools/src/lib.rs`)

### Summary
The RocketPool `rETH` report describes a shared, bounded state variable (the deposit-delay window) that any user's deposit can reset/occupy, blocking a *different* user's withdrawal. `pallet-nomination-pools` has a structurally analogous shared resource: all members of a pool delegate to a single underlying staking ledger keyed by the pool's `bonded_account`, and that ledger's `unlocking` chunk queue is bounded by `T::MaxUnlockingChunks`. Because every member's `Pools::unbond` call writes into this one shared ledger, a member who repeatedly unbonds tiny amounts in successive eras can fill up all unlocking-chunk slots before they mature, causing `Error::NoMoreChunks` for every other member trying to unbond, until the oldest chunk finally matures.

### Finding Description
`Pools::unbond` dissolves the caller's points from the bonded pool and then unbonds the corresponding balance from the pool's single shared stash via `T::StakeAdapter::unbond(Pool::from(bonded_pool.bonded_account()), unbonding_balance)`: [1](#0-0) 

That call flows into the staking pallet's `do_unbond`, which operates on the *ledger of the bonded account* — not on a per-member ledger — and is bounded by `MaxUnlockingChunks`: [2](#0-1) [3](#0-2) 

The same pattern exists in `pallet-staking-async`: [4](#0-3) [5](#0-4) 

Because chunks are merged only when they share the exact same maturation `era`, an attacker who issues one small `unbond` per distinct era (rather than merging into an existing slot) consumes a fresh slot each time. Once `unlocking.len() == MaxUnlockingChunks`, any further `unbond` call — from *any* pool member, since it is the same underlying ledger — triggers an automatic `do_withdraw_unbonded` attempt to free a slot, but this only succeeds if the oldest chunk has already matured: [6](#0-5) 

If the attacker keeps refeeding the queue faster than chunks mature (i.e., submits a new tiny unbond every era, keeping the oldest slot perpetually "just unmatured"), the `ensure!` check fails with `NoMoreChunks` for every other member's `unbond` attempt on that pool. This exact end-to-end scenario ("no more chunks available... haven't been there for more than bonding duration") is demonstrated and asserted in the test suite itself: [7](#0-6) 

### Impact Explanation
This blocks other members of the *same* nomination pool from calling `unbond` (and, by extension, from later calling `withdraw_unbonded`), denying them the ability to exit their stake for as long as the attacker sustains the griefing. Since nomination pools are the primary staking on-ramp for small holders (they cannot bond directly due to `MinNominatorBond`), being locked out of `unbond` is a meaningful denial of a core protocol function for those users, analogous to the reported `unstake()` DoS in the external report.

### Likelihood Explanation
The blast radius and cost make this a low/medium-likelihood issue rather than a high one:
- The griefing is scoped to a single pool (the attacker must be a member of that specific pool), not protocol-wide.
- `MaxUnlockingChunks` in this repo's production-oriented configs (`substrate/bin/node/runtime/src/lib.rs`, `cumulus/parachains/runtimes/assets/asset-hub-westend/src/staking.rs`) is set to a non-trivial value, so an attacker must sustain the attack (one distinct-era `unbond` transaction per slot, repeated indefinitely) over many eras/days to keep every slot permanently unmatured, which is an ongoing operational cost, not a one-shot exploit like the RocketPool case.
- The team appears aware of the interaction between `MaxUnlockingChunks`/`bonding_duration` and shared-ledger unbonding, given the explicit regression test (`automatic_unbonding_pools`) covering exactly this failure mode.
- I was unable to fully confirm the exact numeric values of `MaxUnlockingChunks`/`BondingDuration`/era length configured for each production runtime in this checkout (the grep only located the config keys, not their resolved numeric values), so I cannot precisely quantify the capital/time cost required to sustain the griefing in a live deployment; this uncertainty should be verified before treating this as an actionable, reportable finding.

### Recommendation
- Consider allowing pool-level `unbond`/`withdraw_unbonded` calls to opportunistically consolidate/withdraw *any* matured chunks (not just when the queue is completely full) so legitimate members are not blocked while unmatured chunks from other members occupy slots.
- Consider tracking per-member reservations of unlocking-chunk capacity, or increasing `MaxUnlockingChunks` with era-based rate limiting on how many *new* distinct-era chunks a single account can create within a bonding-duration window, reducing an individual member's ability to monopolize the shared queue.
- Re-verify the concretely configured `MaxUnlockingChunks` / `BondingDuration` / era length for all production runtimes in this repo to quantify real-world attack cost before deciding whether further mitigation is warranted.

### Proof of Concept
Conceptual reproduction, following the pattern already validated by the existing test (`automatic_unbonding_pools`):
1. Pool `P` is configured with `MaxUnlockingChunks = N` (staking pallet) and pool members A (victim) and M (attacker) both join `P`.
2. Attacker M calls `Pools::unbond(M, small_amount)` in era `e0`, creating unlocking chunk 1 in the shared bonded-account ledger (`bonded_pool.bonded_account()`), maturing at `e0 + bonding_duration`. [1](#0-0) 
3. M repeats this once per subsequent era (`e1`, `e2`, ... `e(N-1)`), each time creating a *new* chunk (since the merge-by-era optimization only merges same-era unbonds) until `unlocking.len() == N`. [3](#0-2) 
4. Before the earliest chunk (from `e0`) matures, victim A calls `Pools::unbond(A, amount)`. Because the ledger is full and the oldest chunk is not yet mature, the auto-withdraw does nothing and the subsequent bound check fails: `Error::<T>::NoMoreChunks`, exactly as demonstrated in the existing test. [8](#0-7) 
5. M continues submitting a fresh small `unbond` every era so that the oldest chunk is replaced/refreshed via the queue dynamics before it can be consolidated, keeping A (and any other member) permanently unable to `unbond` from pool `P`.

### Citations

**File:** substrate/frame/nomination-pools/src/lib.rs (L2290-2296)
```rust
			let active_era = T::StakeAdapter::current_era();
			let unbond_era = T::StakeAdapter::bonding_duration().saturating_add(active_era);

			// Unbond in the actual underlying nominator.
			let unbonding_balance = bonded_pool.dissolve(unbonding_points);
			T::StakeAdapter::unbond(Pool::from(bonded_pool.bonded_account()), unbonding_balance)?;

```

**File:** substrate/frame/staking/src/pallet/impls.rs (L1386-1413)
```rust
	pub(crate) fn do_unbond(
		controller: T::AccountId,
		value: BalanceOf<T>,
	) -> Result<Option<Weight>, DispatchError> {
		let unlocking = Self::ledger(Controller(controller.clone())).map(|l| l.unlocking.len())?;

		// if there are no unlocking chunks available, try to withdraw chunks older than
		// `BondingDuration` to proceed with the unbonding.
		let maybe_withdraw_weight = {
			if unlocking == T::MaxUnlockingChunks::get() as usize {
				let real_num_slashing_spans =
					SlashingSpans::<T>::get(&controller).map_or(0, |s| s.iter().count());
				Some(Self::do_withdraw_unbonded(&controller, real_num_slashing_spans as u32)?)
			} else {
				None
			}
		};

		// we need to fetch the ledger again because it may have been mutated in the call
		// to `Self::do_withdraw_unbonded` above.
		let mut ledger = Self::ledger(Controller(controller))?;
		let mut value = value.min(ledger.active);
		let stash = ledger.stash.clone();

		ensure!(
			ledger.unlocking.len() < T::MaxUnlockingChunks::get() as usize,
			Error::<T>::NoMoreChunks,
		);
```

**File:** substrate/frame/staking/src/pallet/impls.rs (L1440-1450)
```rust
			if let Some(chunk) = ledger.unlocking.last_mut().filter(|chunk| chunk.era == era) {
				// To keep the chunk count down, we only keep one chunk per era. Since
				// `unlocking` is a FiFo queue, if a chunk exists for `era` we know that it will
				// be the last one.
				chunk.value = chunk.value.defensive_saturating_add(value)
			} else {
				ledger
					.unlocking
					.try_push(UnlockChunk { value, era })
					.map_err(|_| Error::<T>::NoMoreChunks)?;
			};
```

**File:** substrate/frame/staking-async/src/pallet/mod.rs (L1934-1967)
```rust
		) -> DispatchResultWithPostInfo {
			let controller = ensure_signed(origin)?;
			let unlocking =
				Self::ledger(Controller(controller.clone())).map(|l| l.unlocking.len())?;

			// if there are no unlocking chunks available, try to remove any chunks by withdrawing
			// funds that have fully unbonded.
			let maybe_withdraw_weight = {
				if unlocking == T::MaxUnlockingChunks::get() as usize {
					Some(Self::do_withdraw_unbonded(&controller)?)
				} else {
					None
				}
			};

			// we need to fetch the ledger again because it may have been mutated in the call
			// to `Self::do_withdraw_unbonded` above.
			let mut ledger = Self::ledger(Controller(controller))?;
			let mut value = value.min(ledger.active);
			let stash = ledger.stash.clone();

			// If unbonding all active stake, chill the stash first to avoid `InsufficientBond`
			// errors. This matches the behavior of pallet-staking.
			let chill_weight = if value >= ledger.active {
				Self::chill_stash(&stash);
				T::WeightInfo::chill()
			} else {
				Weight::zero()
			};

			ensure!(
				ledger.unlocking.len() < T::MaxUnlockingChunks::get() as usize,
				Error::<T>::NoMoreChunks,
			);
```

**File:** substrate/frame/staking-async/src/pallet/mod.rs (L2011-2023)
```rust
				let era =
					session_rotation::Rotator::<T>::active_era().saturating_add(unbond_duration);
				if let Some(chunk) = ledger.unlocking.last_mut().filter(|chunk| chunk.era == era) {
					// To keep the chunk count down, we only keep one chunk per era. Since
					// `unlocking` is a FiFo queue, if a chunk exists for `era` we know that it will
					// be the last one.
					chunk.value = chunk.value.defensive_saturating_add(value)
				} else {
					ledger
						.unlocking
						.try_push(UnlockChunk { value, era })
						.map_err(|_| Error::<T>::NoMoreChunks)?;
				};
```

**File:** substrate/frame/election-provider-multi-phase/test-staking-e2e/src/lib.rs (L344-362)
```rust
		// currently unlocking 0 chunks in the bonded pools ledger.
		assert_eq!(unlocking_chunks_of(pool_bonded_account), 0);

		// unbond 2 from pool.
		assert_ok!(Pools::unbond(RuntimeOrigin::signed(2), 2, 10));

		// amount is still locked in the pool, needs to wait for unbonding period.
		assert_eq!(staked_amount_for(pool_bonded_account), 25);

		// max chunks in the ledger are now filled up (`MaxUnlockingChunks == 1`).
		assert_eq!(unlocking_chunks_of(pool_bonded_account), 1);

		// tries to unbond 3 from pool. it will fail since there are no unlocking chunks left
		// available and the current in the queue haven't been there for more than bonding
		// duration.
		assert_err!(
			Pools::unbond(RuntimeOrigin::signed(3), 3, 10),
			pallet_staking::Error::<Runtime>::NoMoreChunks
		);
```
