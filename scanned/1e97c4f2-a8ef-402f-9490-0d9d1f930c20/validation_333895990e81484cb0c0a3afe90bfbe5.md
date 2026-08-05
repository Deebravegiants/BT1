### Title
`paras_registrar::deregister` bypasses `assigned_slots::unassign_parachain_slot`, orphaning `TemporarySlots`/`TemporarySlotCount` accounting - (File: polkadot/runtime/common/src/assigned_slots/mod.rs)

### Summary
`assign_temp_parachain_slot` can insert a `TemporarySlots` entry and increment `TemporarySlotCount` without ever creating a `slots::Leases` entry or transitioning the para's `ParaLifecycle` away from `Parathread` — this happens whenever the slot is scheduled for the *next* lease period, or the current period's `MaxTemporarySlotPerLeasePeriod` cap is already reached. Because `paras_registrar::do_deregister` only inspects `paras::Pallet::lifecycle(id)` (must be `Parathread` or `None`) and never consults `assigned_slots` storage, the para manager can call `deregister` directly through `ensure_root_para_or_owner`, completely bypassing `AssignSlotOrigin`/`unassign_parachain_slot` and leaving `TemporarySlots`/`TemporarySlotCount` permanently desynchronized from reality.

### Finding Description
`assign_temp_parachain_slot` ( [1](#0-0) ) only calls `Self::configure_slot_lease` (which calls `T::Leaser::lease_out`, which in turn calls `T::Registrar::make_parachain` → `schedule_parathread_upgrade`, synchronously flipping `ParaLifecycle` to `UpgradingParathread`) when `lease_period_start == SlotLeasePeriodStart::Current` **and** `ActiveTemporarySlotCount::<T>::get() < T::MaxTemporarySlotPerLeasePeriod::get()`. In every other case (start = `Next`, or the per-period cap is already reached), the function still unconditionally does:
```
TemporarySlots::<T>::insert(id, temp_slot);
TemporarySlotCount::<T>::mutate(|count| count.saturating_inc());
```
without ever creating a `slots::Leases` entry, so `paras::Pallet::lifecycle(id)` remains `Some(ParaLifecycle::Parathread)`.

`paras_registrar::do_deregister` ( [2](#0-1) ) only checks:
```
match paras::Pallet::<T>::lifecycle(id) {
    Some(ParaLifecycle::Parathread) | None => {},
    _ => return Err(Error::<T>::NotParathread.into()),
}
```
It has no knowledge of `assigned_slots::TemporarySlots`/`PermanentSlots`. Since the para is still `Parathread` in this scenario, the manager can call `deregister` (via `ensure_root_para_or_owner`, [3](#0-2) ) with a plain signed origin — no `AssignSlotOrigin` (governance/root) check is involved at all.

The correct cleanup path, `unassign_parachain_slot` ( [4](#0-3) ), is the only place that removes the `TemporarySlots`/`PermanentSlots` entries and decrements `TemporarySlotCount`/`PermanentSlotCount`/`ActiveTemporarySlotCount`, but it requires `T::AssignSlotOrigin`. Because `deregister` never calls it, `TemporarySlots::<T>::contains_key(id)` and `TemporarySlotCount` remain stale/incremented after the para no longer exists in `paras_registrar::Paras` or `paras::ParaLifecycles`.

Note: for `assign_perm_parachain_slot` and the "immediate lease" branch of `assign_temp_parachain_slot`, `configure_slot_lease` runs synchronously and immediately flips lifecycle away from plain `Parathread` (to `UpgradingParathread`), so `deregister` is correctly blocked in that specific case — this is a real, but narrower, hole limited to the deferred/queued temporary-slot paths.

### Impact Explanation
This produces a genuine, permanent accounting desync between `assigned_slots::TemporarySlotCount`/`TemporarySlots` and the real state of the system (invariant violation as specified in the question). Concretely:
- `TemporarySlotCount` never returns to a value reflecting live slots, permanently consuming capacity against `MaxTemporarySlots`, effectively griefing/DoS-ing the temporary-slot allocation mechanism (fewer real slots can ever be assigned by governance again since the count check `TemporarySlotCount::<T>::get() < MaxTemporarySlots::<T>::get()` in `assign_temp_parachain_slot` will eventually block new legitimate assignments).
- The orphaned `TemporarySlots` entry (with the original manager's `AccountId`) survives keyed to a `ParaId` that is now fully deregistered and free to be re-reserved (`paras_registrar::reserve`/`register`) by anyone. If the periodic slot-rotation logic (`allocate_temporary_slot_leases`) later processes this orphaned entry and calls `configure_slot_lease`/`lease_out` for that `ParaId` without re-validating that the id is still owned by the original manager or still a genuine assigned slot, a subsequently re-registered, unrelated para could inherit a free lease turn that was never sanctioned by `AssignSlotOrigin`. I was not able to fully inspect the body of `allocate_temporary_slot_leases` in this pass to confirm whether it re-validates para existence/manager before granting the lease turn, so this specific secondary "fraudulent lease inheritance" consequence is plausible but not fully verified — the accounting-desync/DoS impact on `TemporarySlotCount`/`TemporarySlots`, however, is confirmed.

### Likelihood Explanation
Fully reachable by an unprivileged signed account: the attacker only needs to be the manager of a para that (a) has been assigned a temporary slot via `assign_temp_parachain_slot(..., SlotLeasePeriodStart::Next)` (or the current-period cap is saturated), and (b) is unlocked (`para_info.locked` is `None`/`false`, which is the default state before the para's first head is submitted). Both preconditions are easily satisfiable by a manager who deliberately deregisters before ever running a collator/submitting a head (so `on_new_head` never sets `locked = Some(true)`). This is deterministically reproducible, not a race condition.

### Recommendation
`paras_registrar::do_deregister` (and `swap`) should additionally reject the call, or trigger `assigned_slots::unassign_parachain_slot`-equivalent cleanup, when the target `id` still has a `PermanentSlots` or `TemporarySlots` entry in `assigned_slots`. Concretely, add a check (via a trait hook implemented by `assigned_slots`, similar to `OnSwap`) that `!assigned_slots::PermanentSlots::<T>::contains_key(id) && !assigned_slots::TemporarySlots::<T>::contains_key(id)` before allowing `do_deregister`/`swap` to proceed, returning a new `Error::CannotDeregister`-style error otherwise, and force the assigned-slots pallet to clean up (`TemporarySlots::remove`, decrement counters) whenever it detects the para's registration has actually been offboarded.

### Proof of Concept
```rust
#[test]
fn deregister_orphans_temporary_slot_accounting() {
    new_test_ext().execute_with(|| {
        System::run_to_block::<AllPalletsWithSystem>(1);

        assert_ok!(TestRegistrar::<Test>::register(
            1, ParaId::from(1_u32), dummy_head_data(), dummy_validation_code(),
        ));

        // Saturate the per-period cap so lease_out is NOT called immediately,
        // or use SlotLeasePeriodStart::Next -- lifecycle stays Parathread.
        assert_ok!(AssignedSlots::assign_temp_parachain_slot(
            RuntimeOrigin::root(),
            ParaId::from(1_u32),
            SlotLeasePeriodStart::Next,
        ));

        // Lifecycle is still Parathread: no lease was created.
        assert_eq!(TestRegistrar::<Test>::is_parachain(ParaId::from(1_u32)), false);
        assert!(assigned_slots::TemporarySlots::<Test>::contains_key(ParaId::from(1_u32)));
        assert_eq!(assigned_slots::TemporarySlotCount::<Test>::get(), 1);

        // Manager deregisters directly, bypassing AssignSlotOrigin entirely.
        assert_ok!(mock::Registrar::deregister(RuntimeOrigin::signed(1), ParaId::from(1_u32)));

        // BUG: TemporarySlots/TemporarySlotCount remain stale even though the para
        // is fully deregistered from paras_registrar and paras::ParaLifecycles.
        assert!(assigned_slots::TemporarySlots::<Test>::contains_key(ParaId::from(1_u32))); // still true -> orphaned
        assert_eq!(assigned_slots::TemporarySlotCount::<Test>::get(), 1); // never decremented
        assert!(paras::Pallet::<Test>::lifecycle(ParaId::from(1_u32)).is_none());
    });
}
```
Expected (buggy) result: both assertions pass, proving `TemporarySlots`/`TemporarySlotCount` diverge from the real registrar/lifecycle state without any `AssignSlotOrigin`-gated call being involved.

### Citations

**File:** polkadot/runtime/common/src/assigned_slots/mod.rs (L317-399)
```rust
		pub fn assign_temp_parachain_slot(
			origin: OriginFor<T>,
			id: ParaId,
			lease_period_start: SlotLeasePeriodStart,
		) -> DispatchResult {
			T::AssignSlotOrigin::ensure_origin(origin)?;

			let manager = T::Registrar::manager_of(id).ok_or(Error::<T>::ParaDoesntExist)?;

			ensure!(T::Registrar::is_parathread(id), Error::<T>::NotParathread);

			ensure!(
				!Self::has_permanent_slot(id) && !Self::has_temporary_slot(id),
				Error::<T>::SlotAlreadyAssigned
			);

			let current_lease_period: BlockNumberFor<T> = Self::current_lease_period_index();
			ensure!(
				!T::Leaser::already_leased(
					id,
					current_lease_period,
					// Check current lease & next one
					current_lease_period.saturating_add(
						BlockNumberFor::<T>::from(2u32)
							.saturating_mul(T::TemporarySlotLeasePeriodLength::get().into())
					)
				),
				Error::<T>::OngoingLeaseExists
			);

			ensure!(
				TemporarySlotCount::<T>::get() < MaxTemporarySlots::<T>::get(),
				Error::<T>::MaxTemporarySlotsExceeded
			);

			let mut temp_slot = ParachainTemporarySlot {
				manager: manager.clone(),
				period_begin: match lease_period_start {
					SlotLeasePeriodStart::Current => current_lease_period,
					SlotLeasePeriodStart::Next => current_lease_period + One::one(),
				},
				period_count: T::TemporarySlotLeasePeriodLength::get().into(),
				last_lease: None,
				lease_count: 0,
			};

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

**File:** polkadot/runtime/common/src/assigned_slots/mod.rs (L401-449)
```rust
		/// Unassign a permanent or temporary parachain slot
		#[pallet::call_index(2)]
		#[pallet::weight((<T as Config>::WeightInfo::unassign_parachain_slot(), DispatchClass::Operational))]
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

			// Force downgrade to on-demand parachain (if needed) before end of lease period
			if is_parachain {
				if let Err(err) = polkadot_runtime_parachains::schedule_parachain_downgrade::<T>(id)
				{
					// Treat failed downgrade as warning .. slot lease has been cleared,
					// so the parachain will be downgraded anyway by the slots pallet
					// at the end of the lease period .
					log::warn!(
						target: LOG_TARGET,
						"Failed to downgrade parachain {:?} at period {:?}: {:?}",
						id,
						Self::current_lease_period_index(),
						err
					);
				}
			}

			Ok(())
		}
```

**File:** polkadot/runtime/common/src/paras_registrar/mod.rs (L570-586)
```rust
	/// Ensure the origin is one of Root, the `para` owner, or the `para` itself.
	/// If the origin is the `para` owner, the `para` must be unlocked.
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
