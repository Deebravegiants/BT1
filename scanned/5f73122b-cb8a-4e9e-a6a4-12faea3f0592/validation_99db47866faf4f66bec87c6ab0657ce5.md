### Title
Stale `Slots::Leases` records survive `deregister`/`register` cycle, enabling a new manager to bypass auctions via `trigger_onboard` - ([File: polkadot/runtime/common/src/paras_registrar/mod.rs], [File: polkadot/runtime/common/src/slots/mod.rs])

### Summary
`paras_registrar::Pallet::do_deregister` only checks the `paras` pallet's `ParaLifecycle` for a `ParaId` and never touches or checks `slots::Leases`, and `do_register` never re-initializes it either. Because lease-driven lifecycle transitions (`make_parachain`/`make_parathread`) are only *scheduled* (applied at the next session boundary via `paras::ActionsQueue`) while `Slots::Leases` is mutated synchronously, a window exists where a para can be legitimately `deregister`ed while still `Parathread` in `paras::Pallet::lifecycle`, yet still carries a live `Some(...)` entry in `Slots::Leases`. A different account can then `register` the same `ParaId` and call the permissionless `Slots::trigger_onboard`, which only inspects `Leases::<T>::get(para)` and calls `T::Registrar::make_parachain`, bypassing the intended auction/crowdloan process for the new manager.

### Finding Description
`do_deregister` gates purely on `paras::Pallet::lifecycle(id)`: [1](#0-0) 
It never reads or clears `slots::Leases`. Likewise, `do_register` only checks `paras::Pallet::lifecycle(id).is_none()` before re-inserting `Paras::<T>` and scheduling initialization: [2](#0-1) 

Meanwhile, `Slots::trigger_onboard` is a fully permissionless, signed-only call that trusts `Leases::<T>::get(para)` in isolation: [3](#0-2) 
If `leases.first()` is `Some(Some(_))` it unconditionally invokes `T::Registrar::make_parachain(para)`.

`make_parachain` in the registrar only re-checks the *current* `ParaLifecycle`: [4](#0-3) 
It requires `lifecycle(id) == Some(ParaLifecycle::Parathread)` — which is exactly the state of any freshly re-registered para. It does not verify that the `Leases` entry actually belongs to the current manager/incarnation of the `ParaId`.

Critically, lease-driven upgrades/downgrades scheduled from `slots::Pallet::manage_lease_period_start` / `Leaser::lease_out` (`schedule_parachain_downgrade`/`schedule_parathread_upgrade`, and registration's `schedule_para_initialize`/`schedule_para_cleanup`) are queued into `paras::ActionsQueue` and only take effect at the *next session boundary*, not immediately — this is directly demonstrated by the registrar's own tests, which require `run_to_session(...)` after `register`/`make_parachain` calls before the lifecycle actually flips: [5](#0-4) 
Meanwhile `Leases::<T>` is mutated synchronously in the same call (`lease_out`, `manage_lease_period_start`): [6](#0-5) 
This one-session lag is the desync window: a para whose lease has just become "current" (`Leases` first entry `Some`) can still show `ParaLifecycle::Parathread` in `paras::Pallet` until the following session is processed. In that window, `do_deregister`'s check (`lifecycle == Parathread`) passes, so manager A can deregister X while `Slots::Leases[X]` still contains a live entry — which `do_deregister` never purges. Manager B can then `register` the same `ParaId` X; once X's fresh registration is itself onboarded to `Parathread` (again via the normal session-delayed path), `Leases::<T>::get(X)` still returns A's stale entry, and anyone can call `trigger_onboard(X)` to elevate B's new para directly to full parachain status.

Existing protections are insufficient because:
- `do_deregister`/`do_register` have no awareness of `slots::Leases` at all (no cross-pallet invariant enforcement).
- `trigger_onboard` and `make_parachain` validate only the current `ParaLifecycle`, which is agnostic to which "incarnation" (manager) of the `ParaId` produced the lease.
- No mechanism ties a `Leases` entry to a specific registration epoch/manager of the `ParaId`.

### Impact Explanation
A new, unauthorized manager can obtain full lease-holding parachain status for a `ParaId` without participating in or winning any auction/crowdloan, seizing a parachain slot resource that rightfully required payment/bidding. This also can leave the original leaser's deposit accounting inconsistent (reserved funds tied to a `ParaId` no longer controlled or owned by them), and can trigger `debug_assert!` panics in `manage_lease_period_start` in debug builds if a stale future-period lease later resolves against a para that isn't in the expected state.

### Likelihood Explanation
The exploit requires no privileged origin: `deregister`/`register` are manager/owner-signed calls, and `trigger_onboard` is `ensure_signed`-only, callable by anyone. The precondition is a real, structurally-decoupled timing window between `slots::Leases` mutation (synchronous) and `paras::ActionsQueue`-driven lifecycle transitions (session-delayed), which is inherent to the current design and not an exotic edge case — it is exercised by every lease onboarding/offboarding cycle. Reliable exploitation requires precise timing around session boundaries and lease-period boundaries (an attacker/manager controls when they call `deregister`, so they can pick the right block), making it feasible though it requires some care in sequencing blocks/sessions relative to `LeasePeriod`/`LeaseOffset` and session length.

### Recommendation
- Have `paras_registrar::do_deregister` purge `slots::Leases` (and refund/unreserve associated deposits) for the `ParaId` being deregistered, e.g., by exposing a callback/trait method the registrar invokes on deregistration (similar to `T::OnSwap`), or by making `Leases` cleanup part of a unified "on para removed" hook shared by both pallets.
- Alternatively/additionally, make `do_register` refuse registration (or force-clear stale lease state) whenever `slots::Leases::<T>::get(id)` is non-empty, ensuring a fresh registration cannot inherit any previous incarnation's lease.
- Harden `trigger_onboard`/`make_parachain` to validate that the lease entry's leaser/manager matches the para's current manager, or track a "registration epoch" for each `ParaId` and only honor leases minted under the same epoch.

### Proof of Concept
Rust integration test in `polkadot/runtime/common/src/slots/mod.rs` (or a runtime integration test with the real `paras_registrar` + `paras` + `slots` pallets, not the `TestRegistrar` mock, since the mock's `deregister`/`make_parachain` don't model the session-delay lifecycle):
1. Register `ParaId` X under manager A; run to session so X becomes `Parathread`.
2. Have A win/force a lease for X for the *current* lease period (`Leases::<T>::insert`/`force_lease` with `period_begin == current_lease_period`), which synchronously updates `Leases` and schedules (but does not immediately apply) `make_parachain`.
3. Before the next session boundary is processed (so `paras::Pallet::lifecycle(X)` is still `Parathread`), call `Registrar::deregister(A, X)` and assert it succeeds.
4. Assert `Slots::Leases::<Test>::get(X)` is still non-empty (bug confirmation).
5. Register X again under manager B (`Registrar::register(B, X, ...)`), run to session so X becomes `Parathread` again.
6. Call `Slots::trigger_onboard(RuntimeOrigin::signed(anyone), X)` and assert it currently **succeeds**, incorrectly promoting B's para to lease-holding parachain status — then assert this should instead fail with an error (e.g., a new `StaleLease`/`NotOwner` error) once the fix (purging `Leases` on deregister or epoch-checking on trigger) is applied.

### Citations

**File:** polkadot/runtime/common/src/paras_registrar/mod.rs (L522-532)
```rust
	fn make_parachain(id: ParaId) -> DispatchResult {
		// Para backend should think this is an on-demand parachain...
		ensure!(
			paras::Pallet::<T>::lifecycle(id) == Some(ParaLifecycle::Parathread),
			Error::<T>::NotParathread
		);
		polkadot_runtime_parachains::schedule_parathread_upgrade::<T>(id)
			.map_err(|_| Error::<T>::CannotUpgrade)?;

		Ok(())
	}
```

**File:** polkadot/runtime/common/src/paras_registrar/mod.rs (L623-657)
```rust
	fn do_register(
		who: T::AccountId,
		deposit_override: Option<BalanceOf<T>>,
		id: ParaId,
		genesis_head: HeadData,
		validation_code: ValidationCode,
		ensure_reserved: bool,
	) -> DispatchResult {
		let deposited = if let Some(para_data) = Paras::<T>::get(id) {
			ensure!(para_data.manager == who, Error::<T>::NotOwner);
			ensure!(!para_data.is_locked(), Error::<T>::ParaLocked);
			para_data.deposit
		} else {
			ensure!(!ensure_reserved, Error::<T>::NotReserved);
			Default::default()
		};
		ensure!(paras::Pallet::<T>::lifecycle(id).is_none(), Error::<T>::AlreadyRegistered);
		let (genesis, deposit) =
			Self::validate_onboarding_data(genesis_head, validation_code, ParaKind::Parathread)?;
		let deposit = deposit_override.unwrap_or(deposit);

		if let Some(additional) = deposit.checked_sub(&deposited) {
			<T as Config>::Currency::reserve(&who, additional)?;
		} else if let Some(rebate) = deposited.checked_sub(&deposit) {
			<T as Config>::Currency::unreserve(&who, rebate);
		};
		let info = ParaInfo { manager: who.clone(), deposit, locked: None };

		Paras::<T>::insert(id, info);
		// We check above that para has no lifecycle, so this should not fail.
		let res = polkadot_runtime_parachains::schedule_para_initialize::<T>(id, genesis);
		debug_assert!(res.is_ok());
		Self::deposit_event(Event::<T>::Registered { para_id: id, manager: who });
		Ok(())
	}
```

**File:** polkadot/runtime/common/src/paras_registrar/mod.rs (L660-676)
```rust
	fn do_deregister(id: ParaId) -> DispatchResult {
		match paras::Pallet::<T>::lifecycle(id) {
			// Para must be a parathread (on-demand parachain), or not exist at all.
			Some(ParaLifecycle::Parathread) | None => {},
			_ => return Err(Error::<T>::NotParathread.into()),
		}
		polkadot_runtime_parachains::schedule_para_cleanup::<T>(id)
			.map_err(|_| Error::<T>::CannotDeregister)?;

		if let Some(info) = Paras::<T>::take(&id) {
			<T as Config>::Currency::unreserve(&info.manager, info.deposit);
		}

		PendingSwap::<T>::remove(id);
		Self::deposit_event(Event::<T>::Deregistered { para_id: id });
		Ok(())
	}
```

**File:** polkadot/runtime/common/src/slots/mod.rs (L210-223)
```rust
		#[pallet::call_index(2)]
		#[pallet::weight(T::WeightInfo::trigger_onboard())]
		pub fn trigger_onboard(origin: OriginFor<T>, para: ParaId) -> DispatchResult {
			ensure_signed(origin)?;
			let leases = Leases::<T>::get(para);
			match leases.first() {
				// If the first element in leases is present, then it has a lease!
				// We can try to onboard it.
				Some(Some(_lease_info)) => T::Registrar::make_parachain(para)?,
				// Otherwise, it does not have a lease.
				Some(None) | None => return Err(Error::<T>::ParaNotOnboarding.into()),
			};
			Ok(())
		}
```

**File:** polkadot/runtime/common/src/slots/mod.rs (L238-284)
```rust
		let mut parachains = Vec::new();
		for (para, mut lease_periods) in Leases::<T>::iter() {
			if lease_periods.is_empty() {
				continue;
			}
			// ^^ should never be empty since we would have deleted the entry otherwise.

			if lease_periods.len() == 1 {
				// Just one entry, which corresponds to the now-ended lease period.
				//
				// `para` is now just an on-demand parachain.
				//
				// Unreserve whatever is left.
				if let Some((who, value)) = &lease_periods[0] {
					T::Currency::unreserve(&who, *value);
				}

				// Remove the now-empty lease list.
				Leases::<T>::remove(para);
			} else {
				// The parachain entry has leased future periods.

				// We need to pop the first deposit entry, which corresponds to the now-
				// ended lease period.
				let maybe_ended_lease = lease_periods.remove(0);

				Leases::<T>::insert(para, &lease_periods);

				// If we *were* active in the last period and so have ended a lease...
				if let Some(ended_lease) = maybe_ended_lease {
					// Then we need to get the new amount that should continue to be held on
					// deposit for the parachain.
					let now_held = Self::deposit_held(para, &ended_lease.0);

					// If this is less than what we were holding for this leaser's now-ended lease,
					// then unreserve it.
					if let Some(rebate) = ended_lease.1.checked_sub(&now_held) {
						T::Currency::unreserve(&ended_lease.0, rebate);
					}
				}

				// If we have an active lease in the new period, then add to the current parachains
				if lease_periods[0].is_some() {
					parachains.push(para);
				}
			}
		}
```

**File:** polkadot/runtime/common/src/paras_registrar/tests.rs (L43-60)
```rust
		assert_ok!(mock::Registrar::register(
			RuntimeOrigin::signed(1),
			para_id,
			test_genesis_head(32),
			validation_code.clone(),
		));
		conclude_pvf_checking::<Test>(&validation_code, VALIDATORS, START_SESSION_INDEX);

		run_to_session(START_SESSION_INDEX + 2);
		// It is now a parathread (on-demand parachain).
		assert!(Parachains::is_parathread(para_id));
		assert!(!Parachains::is_parachain(para_id));
		// Some other external process will elevate on-demand to lease holding parachain
		assert_ok!(mock::Registrar::make_parachain(para_id));
		run_to_session(START_SESSION_INDEX + 4);
		// It is now a lease holding parachain.
		assert!(!Parachains::is_parathread(para_id));
		assert!(Parachains::is_parachain(para_id));
```
