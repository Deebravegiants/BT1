Audit Report

## Title
`assigned_slots::TemporarySlots`/`TemporarySlotCount` desync via `paras_registrar::deregister` on a not-yet-leased temporary slot - (File: polkadot/runtime/common/src/assigned_slots/mod.rs)

## Summary
`assign_temp_parachain_slot` inserts a `TemporarySlots` entry and increments `TemporarySlotCount` unconditionally, but only calls `configure_slot_lease` (which drives the para toward `ParaLifecycle::Parachain`) when `SlotLeasePeriodStart::Current` is chosen and the active-slot cap for the period has not been reached. In the alternative case (`SlotLeasePeriodStart::Next`, or capacity already saturated), the para's `ParaLifecycle` remains `Parathread`, which allows the para's manager to call `paras_registrar::deregister` — a call gated only by lifecycle state — removing the para while `assigned_slots` still tracks it as slot-assigned, permanently desynchronizing `TemporarySlots`/`TemporarySlotCount`.

## Finding Description
`assign_temp_parachain_slot` at `polkadot/runtime/common/src/assigned_slots/mod.rs:363-394` only invokes `Self::configure_slot_lease` — the function that actually leases the slot and changes the para's lifecycle — inside the conditional block gated on `lease_period_start == SlotLeasePeriodStart::Current && ActiveTemporarySlotCount::<T>::get() < T::MaxTemporarySlotPerLeasePeriod::get()`. The `TemporarySlots::<T>::insert(id, temp_slot)` and `TemporarySlotCount::<T>::mutate(|count| count.saturating_inc())` calls at lines 393-394 execute unconditionally, regardless of whether a lease was actually created.

This means that when `SlotLeasePeriodStart::Next` is passed, or when `ActiveTemporarySlotCount` already equals `MaxTemporarySlotPerLeasePeriod`, the para remains `ParaLifecycle::Parathread` while `assigned_slots` bookkeeping already reflects an assigned temporary slot.

`paras_registrar::do_deregister` (`polkadot/runtime/common/src/paras_registrar/mod.rs:660-676`) gates solely on `paras::Pallet::<T>::lifecycle(id)`, allowing deregistration when the lifecycle is `Parathread` or `None`, with no awareness of `assigned_slots` state. The `deregister` extrinsic (lines 307-310) is reachable by the para's manager via `ensure_root_para_or_owner` (lines confirmed at `paras_registrar/mod.rs`), which only checks `para_info.manager == who` and `!is_locked()` for a signed caller — no root/governance privilege is required.

Since `do_deregister` removes `Paras::<T>` and clears `PendingSwap`, but never touches `assigned_slots::TemporarySlots`, `TemporarySlotCount`, or `ActiveTemporarySlotCount`, and there is no cross-pallet hook wired from `paras_registrar` into `assigned_slots` (the only place these are decremented is `unassign_parachain_slot`, at lines 404-449, which is gated behind `T::AssignSlotOrigin`, not the para manager), a stale `TemporarySlots` entry for a deregistered/nonexistent `ParaId` persists indefinitely, and `TemporarySlotCount` is never decremented for it.

The permanent-slot variant of the analogous attack is correctly not exploitable, since `assign_perm_parachain_slot` (lines 291-297) calls `configure_slot_lease` unconditionally, immediately flipping the para's lifecycle away from `Parathread` and causing `do_deregister` to fail with `NotParathread`.

## Impact Explanation
This is a low-severity accounting/griefing issue confined to the `assigned_slots` pallet's own internal bookkeeping. Once triggered, one unit of `TemporarySlotCount` is permanently stranded against the governance-configured `MaxTemporarySlots` cap for a `ParaId` that no longer exists, slightly reducing the pool of temporary slots available to legitimate future parathreads over repeated occurrences. The periodic `allocate_temporary_slot_leases` routine will continue to consider the orphaned entry and attempt `configure_slot_lease` against a deregistered `ParaId`, wasting weight; per the code's own error handling this fails gracefully into a logged warning rather than causing an unhandled panic or fund loss. There is no loss of user funds, no theft, and no consensus-safety issue — this is a permanent (until governance intervention/cleanup) resource-accounting desync in a subsystem primarily governed by root/governance-controlled slot assignment.

## Likelihood Explanation
The precondition (a temporary slot assigned with `SlotLeasePeriodStart::Next`, or assignment occurring when the per-period active-slot cap is saturated) is a normal, expected operational state reachable via ordinary use of `AssignSlotOrigin` (typically root/governance) calling `assign_temp_parachain_slot`. Once that state exists, any para manager — an unprivileged, signed account — can trigger the desync deterministically with a single `paras_registrar::deregister` call, requiring no special permissions beyond being the para's manager and the para not being locked. This is repeatable for every para assigned a pending temporary slot in this manner.

## Recommendation
`paras_registrar::do_deregister` should reject deregistration of a para that still has an `assigned_slots::TemporarySlots` (or `PermanentSlots`) entry, or `assigned_slots` should expose a cleanup hook invoked by `do_deregister` to remove/decrement the corresponding `TemporarySlots`/`TemporarySlotCount`/`ActiveTemporarySlotCount` entries, mirroring the cleanup logic already present in `unassign_parachain_slot`.

## Proof of Concept
1. Register a para as an on-demand parathread via the registrar (`TestRegistrar::register` in tests, or `paras_registrar::register` on a live chain).
2. Have `AssignSlotOrigin` call `assigned_slots::assign_temp_parachain_slot(origin, id, SlotLeasePeriodStart::Next)`. Confirm `TemporarySlots::<T>::get(id).is_some()` and `TemporarySlotCount::<T>::get()` incremented, while `paras::Pallet::<T>::lifecycle(id) == Some(ParaLifecycle::Parathread)` (lease not yet active).
3. As the para's manager (signed, unprivileged), call `paras_registrar::deregister(origin, id)`. Observe it succeeds (`Ok(())`), since lifecycle is still `Parathread`.
4. Confirm `paras::Pallet::<T>::lifecycle(id)` is now `None` (para fully deregistered).
5. Confirm the desync: `TemporarySlots::<T>::get(id)` still returns `Some(..)` and `TemporarySlotCount::<T>::get()` remains unchanged from step 2 — proving `assigned_slots` accounting is permanently out of sync with the actual registered-para set. [1](#0-0) [2](#0-1) [3](#0-2) [4](#0-3) [5](#0-4)

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
