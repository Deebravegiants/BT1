Confirmed: `paras_registrar` has zero references to `assigned_slots`, meaning there is no cross-pallet hook or check preventing deregistration of a para with a pending slot assignment. This validates the core architectural gap described in the claim.

Audit Report

## Title
`assigned_slots::TemporarySlots`/`TemporarySlotCount` desync via `paras_registrar::deregister` on a not-yet-leased temporary slot - (File: polkadot/runtime/common/src/assigned_slots/mod.rs)

## Summary
`assign_temp_parachain_slot` inserts a `TemporarySlots` entry and increments `TemporarySlotCount` unconditionally, but only actually leases the para (which would flip `ParaLifecycle` to `Parachain`) when `SlotLeasePeriodStart::Current` is chosen and `ActiveTemporarySlotCount` is below the per-period cap. [1](#0-0)  When `SlotLeasePeriodStart::Next` is used (or the cap is already reached), the para's `ParaLifecycle` remains `Parathread`, so `paras_registrar::do_deregister`'s lifecycle-only gate does not block deregistration. [2](#0-1)  Since `paras_registrar` has no reference to or hook into `assigned_slots` state, the manager's ordinary `deregister` call succeeds while `assigned_slots::TemporarySlots`/`TemporarySlotCount` still account for the now-nonexistent para, permanently desynchronizing the bookkeeping.

## Finding Description
`assign_temp_parachain_slot` conditionally calls `Self::configure_slot_lease` only inside the `if lease_period_start == SlotLeasePeriodStart::Current && ActiveTemporarySlotCount::<T>::get() < T::MaxTemporarySlotPerLeasePeriod::get()` branch; the `TemporarySlots::<T>::insert(id, temp_slot)` and `TemporarySlotCount::<T>::mutate(|count| count.saturating_inc())` calls happen unconditionally afterward, regardless of whether a lease was actually created. [3](#0-2)  This means a para can have a `TemporarySlots` entry recorded while its `ParaLifecycle` is still `Parathread`.

`paras_registrar::do_deregister` gates purely on `paras::Pallet::<T>::lifecycle(id)` being `Parathread` or `None`, with no awareness of `assigned_slots` storage: [4](#0-3)  and this is reachable via the signed extrinsic `deregister`, gated only by `ensure_root_para_or_owner` (root, para itself, or the para's manager provided the para isn't locked): [5](#0-4) . A confirmed grep across `paras_registrar/mod.rs` shows zero references to `assigned_slots`, confirming there is no cross-pallet cleanup hook.

By contrast, `assigned_slots::unassign_parachain_slot` is the only path that correctly decrements `TemporarySlots`/`TemporarySlotCount`/`ActiveTemporarySlotCount`, but it is a separate, `AssignSlotOrigin`-gated call that is never invoked by `do_deregister`. [6](#0-5)  Consequently, a para manager can deregister a para with a pending (not-yet-leased) temporary slot, leaving a stale `TemporarySlots` entry and an un-decremented `TemporarySlotCount` for a `ParaId` that no longer exists.

The permanent-slot sub-case described in the original report is correctly identified as non-exploitable: `assign_perm_parachain_slot` unconditionally calls `configure_slot_lease` for the current period, immediately making `is_parachain(id)` true and flipping lifecycle away from `Parathread`, which blocks `do_deregister` via `Error::<T>::NotParathread`. [7](#0-6) 

## Impact Explanation
This is a state-accounting/griefing bug rather than a funds-loss or consensus-safety bug. Each exploitation permanently strands one unit of `TemporarySlotCount` against the governance-set `MaxTemporarySlots` cap, since nothing ever decrements it for the deregistered `ParaId`, and leaves an orphaned `TemporarySlots` entry that `allocate_temporary_slot_leases` will continue to iterate and attempt to lease against a nonexistent para (treated as a warning on failure, but wasting weight indefinitely). Over repeated occurrences this reduces the effective supply of temporary slots available to legitimate parathreads, a low-severity griefing/DoS-of-resource-allocation issue confined to the `assigned_slots` pallet's internal bookkeeping.

## Likelihood Explanation
The precondition — a temporary slot assigned with `SlotLeasePeriodStart::Next`, or assignment while the current period's active-slot cap is saturated — is a normal, expected operational path for `assigned_slots`, not a contrived edge case. Once a temporary slot in this pending state exists, any ordinary para manager (no elevated privilege beyond being the para's own manager, and the para must not be locked) can trigger the desync with a single standard `deregister` call, and can repeat this on newly-registered paras to accumulate stranded slot counts over time.

## Recommendation
`paras_registrar::do_deregister` should check for and clear any `assigned_slots::PermanentSlots`/`TemporarySlots` entry for the para (mirroring the decrement logic already implemented in `unassign_parachain_slot`), or `assigned_slots` should expose a public cleanup function that `paras_registrar` invokes during deregistration so that `TemporarySlotCount`/`TemporarySlots`/`ActiveTemporarySlotCount` stay synchronized with the actual set of registered/leased paras.

## Proof of Concept
In `polkadot/runtime/common/src/assigned_slots/mod.rs` test module:
1. Register a para as an on-demand parathread via `TestRegistrar::register`.
2. Call `AssignedSlots::assign_temp_parachain_slot(RuntimeOrigin::root(), id, SlotLeasePeriodStart::Next)`; assert `TemporarySlots::<Test>::get(id).is_some()`, `TemporarySlotCount::<Test>::get() == 1`, and `TestRegistrar::<Test>::is_parachain(id) == false`.
3. As the para's signed manager, call `paras_registrar::Pallet::<Test>::deregister(RuntimeOrigin::signed(manager), id)` and assert `Ok(())`.
4. Assert `paras::Pallet::<Test>::lifecycle(id).is_none()`.
5. Assert the desync: `TemporarySlots::<Test>::get(id).is_some()` still true and `TemporarySlotCount::<Test>::get() == 1`, unchanged despite the para no longer existing.

### Citations

**File:** polkadot/runtime/common/src/assigned_slots/mod.rs (L290-297)
```rust
			// Permanent slot assignment fails if a lease cannot be created
			Self::configure_slot_lease(
				id,
				manager,
				current_lease_period,
				T::PermanentSlotLeasePeriodLength::get().into(),
			)
			.map_err(|_| Error::<T>::CannotUpgrade)?;
```

**File:** polkadot/runtime/common/src/assigned_slots/mod.rs (L363-399)
```rust
			if lease_period_start == SlotLeasePeriodStart::Current &&
				ActiveTemporarySlotCount::<T>::get() < T::MaxTemporarySlotPerLeasePeriod::get()
			{
				// Try to allocate slot directly
				match Self::configure_slot_lease(
					id,
					manager,
					temp_slot.period_begin,
					temp_slot.period_count,
				) {
					Ok(_) => {
						ActiveTemporarySlotCount::<T>::mutate(|count| count.saturating_inc());
						temp_slot.last_lease = Some(temp_slot.period_begin);
						temp_slot.lease_count += 1;
					},
					Err(err) => {
						// Treat failed lease creation as warning .. slot will be allocated a lease
						// in a subsequent lease period by the `allocate_temporary_slot_leases`
						// function.
						log::warn!(
							target: LOG_TARGET,
							"Failed to allocate a temp slot for para {:?} at period {:?}: {:?}",
							id,
							current_lease_period,
							err
						);
					},
				}
			}

			TemporarySlots::<T>::insert(id, temp_slot);
			TemporarySlotCount::<T>::mutate(|count| count.saturating_inc());

			Self::deposit_event(Event::<T>::TemporarySlotAssigned(id));

			Ok(())
		}
```

**File:** polkadot/runtime/common/src/assigned_slots/mod.rs (L404-429)
```rust
		pub fn unassign_parachain_slot(origin: OriginFor<T>, id: ParaId) -> DispatchResult {
			T::AssignSlotOrigin::ensure_origin(origin.clone())?;

			ensure!(
				Self::has_permanent_slot(id) || Self::has_temporary_slot(id),
				Error::<T>::SlotNotAssigned
			);

			// Check & cache para status before we clear the lease
			let is_parachain = Self::is_parachain(id);

			// Remove perm or temp slot
			Self::clear_slot_leases(origin.clone(), id)?;

			if PermanentSlots::<T>::contains_key(id) {
				PermanentSlots::<T>::remove(id);
				PermanentSlotCount::<T>::mutate(|count| *count = count.saturating_sub(One::one()));
			} else if TemporarySlots::<T>::contains_key(id) {
				TemporarySlots::<T>::remove(id);
				TemporarySlotCount::<T>::mutate(|count| *count = count.saturating_sub(One::one()));
				if is_parachain {
					ActiveTemporarySlotCount::<T>::mutate(|active_count| {
						*active_count = active_count.saturating_sub(One::one())
					});
				}
			}
```

**File:** polkadot/runtime/common/src/paras_registrar/mod.rs (L572-584)
```rust
	fn ensure_root_para_or_owner(
		origin: <T as frame_system::Config>::RuntimeOrigin,
		id: ParaId,
	) -> DispatchResult {
		if let Ok(who) = ensure_signed(origin.clone()) {
			let para_info = Paras::<T>::get(id).ok_or(Error::<T>::NotRegistered)?;

			if para_info.manager == who {
				ensure!(!para_info.is_locked(), Error::<T>::ParaLocked);
				return Ok(());
			}
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
