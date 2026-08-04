### Title
`assigned_slots::TemporarySlots`/`TemporarySlotCount` desync via `paras_registrar::deregister` on a not-yet-leased temporary slot - (File: polkadot/runtime/common/src/assigned_slots/mod.rs)

### Summary
`paras_registrar::do_deregister` only checks the para's `ParaLifecycle` (must be `Parathread` or `None`) and has no awareness of `assigned_slots` pallet state, so a para manager can deregister a para that still has a pending (not-yet-active) `TemporarySlots` entry. For a permanent slot, `assign_perm_parachain_slot` immediately triggers a lease that turns the para into a lease-holding `Parachain`, which blocks `deregister` via the lifecycle check — so that specific sub-case in the prompt is not exploitable. However, for a temporary slot assigned with `SlotLeasePeriodStart::Next` (or when the current period's active-slot cap is already reached), the para's `ParaLifecycle` remains `Parathread` while `assigned_slots::TemporarySlots`/`TemporarySlotCount` already account for it, and `do_deregister` succeeds in that state, permanently desynchronizing `assigned_slots` bookkeeping.

### Finding Description
`assign_temp_parachain_slot` (`polkadot/runtime/common/src/assigned_slots/mod.rs:317-399`) inserts a `TemporarySlots` entry and increments `TemporarySlotCount` unconditionally, but only calls `configure_slot_lease` (which actually leases out the slot and drives the para toward `ParaLifecycle::Parachain`) when `lease_period_start == SlotLeasePeriodStart::Current` and `ActiveTemporarySlotCount < MaxTemporarySlotPerLeasePeriod`: [1](#0-0) 

If `SlotLeasePeriodStart::Next` is chosen, or the active-slot cap for the current period is already reached, no lease is created yet — the para's on-chain `ParaLifecycle` stays `Parathread`, even though `TemporarySlots`/`TemporarySlotCount` in `assigned_slots` already reflect an assigned slot: [2](#0-1) 

Meanwhile, `paras_registrar::do_deregister` only gates on `ParaLifecycle`: [3](#0-2) 

Since the lifecycle is still `Parathread` in this window, the para's manager can call the signed, owner-reachable `deregister` extrinsic (gated only by `ensure_root_para_or_owner`): [4](#0-3) [5](#0-4) 

`do_deregister` removes the `Paras` entry, unreserves the deposit, schedules cleanup, and clears `PendingSwap`, but it never touches `assigned_slots::TemporarySlots`/`TemporarySlotCount`/`ActiveTemporarySlotCount`. There is no `OnSwap`/deregistration hook wired from `paras_registrar` into `assigned_slots` (`assigned_slots` only mutates its own storage inside `unassign_parachain_slot`, at `polkadot/runtime/common/src/assigned_slots/mod.rs:404-449`). Consequently, after deregistration the stale `TemporarySlots` entry for the now-nonexistent `ParaId` still exists, and `TemporarySlotCount` remains incremented.

This stale entry is also periodically iterated by `allocate_temporary_slot_leases` (`polkadot/runtime/common/src/assigned_slots/mod.rs:491-567`), which will attempt `Self::configure_slot_lease` for the orphaned `ParaId` — a call into a deregistered para that either fails silently (treated as a logged warning) or, in the worst case, could allocate scheduler resources for an ID that no longer exists once its `period_begin` condition is reached.

Note: the permanent-slot half of the described attack is not reachable this way — `assign_perm_parachain_slot` immediately calls `configure_slot_lease` for the current period unconditionally (`polkadot/runtime/common/src/assigned_slots/mod.rs:291-297`), and the codebase's own test (`unassign_perm_slot_succeeds`, `polkadot/runtime/common/src/assigned_slots/mod.rs:1335-1364`) confirms `is_parachain(id)` becomes `true` right after assignment, which flips `ParaLifecycle` away from `Parathread` and causes `do_deregister` to return `Error::<T>::NotParathread`, blocking the manager's `deregister` call while a permanent slot is held.

### Impact Explanation
For paras with a pending (`SlotLeasePeriodStart::Next` or capacity-blocked) temporary slot, a manager-triggered deregistration permanently strands one unit of `assigned_slots::TemporarySlotCount` against a `MaxTemporarySlots` cap set by governance, since nothing ever decrements it for the deregistered `ParaId`. This is a griefing vector against the temporary-slot allocation pool (fewer temporary slots become available to legitimate future parathreads) and leaves an orphaned `TemporarySlots` map entry that the periodic `allocate_temporary_slot_leases` routine will keep considering, wasting weight and potentially misbehaving against a non-existent `ParaId`.

### Likelihood Explanation
Requires the pallet's `AssignSlotOrigin` (root/governance in practice) to have assigned a temporary slot with `SlotLeasePeriodStart::Next`, or for the current period's temporary-slot capacity to already be saturated at assignment time — both are normal, expected operational states of `assigned_slots`, not edge cases. Once that precondition holds, any para manager can trigger the desync with a single ordinary `paras_registrar::deregister` call; no special privileges beyond being the para's manager are needed.

### Recommendation
`paras_registrar::do_deregister` should not allow deregistration of a para that still has any `assigned_slots::PermanentSlots`/`TemporarySlots` entry, or `assigned_slots` should expose a cleanup hook that `do_deregister` invokes to remove/decrement the corresponding entry and counters (mirroring what `unassign_parachain_slot` already does) whenever a para with an assigned slot is deregistered.

### Proof of Concept
Integration test in `polkadot/runtime/common/src/assigned_slots/mod.rs` test module:
1. Register a para as an on-demand parathread via `TestRegistrar::register`.
2. Call `AssignedSlots::assign_temp_parachain_slot(RuntimeOrigin::root(), id, SlotLeasePeriodStart::Next)` — assert `TemporarySlots::<Test>::get(id).is_some()` and `TemporarySlotCount::<Test>::get() == 1`, and assert `TestRegistrar::<Test>::is_parachain(id) == false` (lease not yet active).
3. As the para's signed manager, call `paras_registrar::Pallet::deregister(RuntimeOrigin::signed(manager), id)` and assert it returns `Ok(())`.
4. Assert `paras::Pallet::<Test>::lifecycle(id).is_none()` (para fully deregistered).
5. Assert the bug: `TemporarySlots::<Test>::get(id).is_some()` (stale entry) and `TemporarySlotCount::<Test>::get() == 1` (not decremented), proving `assigned_slots` accounting is desynchronized from the actual set of registered paras.

### Citations

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

**File:** polkadot/runtime/common/src/paras_registrar/mod.rs (L301-310)
```rust
		/// Deregister a Para Id, freeing all data and returning any deposit.
		///
		/// The caller must be Root, the `para` owner, or the `para` itself. The para must be an
		/// on-demand parachain.
		#[pallet::call_index(2)]
		#[pallet::weight(<T as Config>::WeightInfo::deregister())]
		pub fn deregister(origin: OriginFor<T>, id: ParaId) -> DispatchResult {
			Self::ensure_root_para_or_owner(origin, id)?;
			Self::do_deregister(id)
		}
```

**File:** polkadot/runtime/common/src/paras_registrar/mod.rs (L572-586)
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

		Self::ensure_root_or_para(origin, id)
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
