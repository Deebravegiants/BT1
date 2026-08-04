### Title
Para manager can bypass `unassign_parachain_slot` cleanup via `Registrar::deregister`, leaving a zombie entry in `TemporarySlots` that permanently consumes `MaxTemporarySlotPerLeasePeriod` rotation capacity - ([File: polkadot/runtime/common/src/assigned_slots/mod.rs])

### Summary
`assigned_slots::TemporarySlots`/`TemporarySlotCount`/`ActiveTemporarySlotCount` bookkeeping is only updated by `unassign_parachain_slot`, which is gated by `AssignSlotOrigin`. A para's own signed, unlocked manager can instead call `paras_registrar::Pallet::deregister` (or trigger a `swap`) whenever the para's `ParaLifecycle` is `Parathread`, which is a state a temp-slot para naturally revisits between lease rotations. This desynchronizes `TemporarySlots` from the real registrar/lease state and leaves a stale entry that `allocate_temporary_slot_leases` keeps rotating in, wasting one of the limited `MaxTemporarySlotPerLeasePeriod` allocation turns every cycle.

### Finding Description
`do_deregister` only checks the para's lifecycle, not whether it is tracked by `assigned_slots`: [1](#0-0) 
and the origin check `ensure_root_para_or_owner`/`ensure_signed` allows the para's own unlocked manager to call it directly with a signed origin: [2](#0-1) 

Meanwhile, all bookkeeping cleanup for temp slots (`TemporarySlots::remove`, `TemporarySlotCount`/`ActiveTemporarySlotCount` decrement) lives only inside `unassign_parachain_slot`, gated by `T::AssignSlotOrigin::ensure_origin`: [3](#0-2) 

A temp slot assigned by root does not keep the para as `ParaLifecycle::Parachain` permanently: it is only upgraded to `Parachain` while an active lease window exists in `Slots::Leases`, and reverts back to `Parathread` automatically once the lease period ends (handled entirely inside the `slots` pallet's `manage_lease_period_start`, with no callback into `assigned_slots`): [4](#0-3) 
Additionally, if `assign_temp_parachain_slot` is called with `SlotLeasePeriodStart::Next`, or the direct allocation attempt fails because `ActiveTemporarySlotCount >= MaxTemporarySlotPerLeasePeriod`, the para is registered in `TemporarySlots` while its lifecycle is still `Parathread`: [5](#0-4) 

In either window (pre-activation or post-lease-expiry), the manager can call `deregister(id)` successfully, since lifecycle is `Parathread` — this removes the `Paras` entry, refunds the registration deposit, and schedules cleanup, but never touches `TemporarySlots`/`TemporarySlotCount`.

The stale `TemporarySlots` entry is not removed by this path. On subsequent lease-period starts, `allocate_temporary_slot_leases` selects candidates purely from `TemporarySlots` storage (it never checks whether the para is still registered): [6](#0-5) 
`configure_slot_lease`/`Leaser::lease_out` is invoked for the now-deregistered `ParaId`, creating a `Slots::Leases` entry and best-effort (ignored-on-failure) attempting `Registrar::make_parachain`: [7](#0-6) 
The temp slot's `lease_count`/`last_lease` get updated and `ActiveTemporarySlotCount` is incremented for this phantom allocation, consuming a slot in `slots_to_be_upgraded` that should have gone to a real, still-registered para. Because nothing ever removes the zombie `TemporarySlots` entry except the privileged `unassign_parachain_slot`, this repeats every eligible rotation, permanently reducing effective `MaxTemporarySlotPerLeasePeriod` capacity by one for every para deregistered this way — up to `MaxTemporarySlots` such zombies.

### Impact Explanation
An unprivileged para manager can unilaterally desynchronize `assigned_slots` bookkeeping from actual registrar/lease state and create a persistent "ghost" slot that keeps winning rotation turns in `allocate_temporary_slot_leases`, starving legitimate temp-slot paras of `MaxTemporarySlotPerLeasePeriod` allocations. Recovery requires a privileged `AssignSlotOrigin` call to `unassign_parachain_slot` for each affected `ParaId` — the manager forced an unplanned governance intervention and, until that happens, wastes shared, scarce temporary-slot rotation capacity that a test-network (Rococo-style) `MaxTemporarySlotPerLeasePeriod` is meant to fairly distribute.

### Likelihood Explanation
Fully reachable by a signed, unprivileged account: the attacker only needs to be the recognized (unlocked) manager of a para that was granted a temp slot by root/governance — a normal, expected precondition for any project using this pallet. No special timing beyond waiting for the natural `Parathread` window (pre-activation with `SlotLeasePeriodStart::Next`, or after a lease naturally elapses) is required, and `deregister` is a standard, always-available extrinsic for the manager.

### Recommendation
Have `paras_registrar::do_deregister` (and `do_thread_and_chain_swap`) invoke a cleanup hook into `assigned_slots` (e.g. via a new trait method on `Registrar`/`OnSwap`-like hook) that removes any `PermanentSlots`/`TemporarySlots` entry and decrements `TemporarySlotCount`/`ActiveTemporarySlotCount` (and `PermanentSlotCount`) for the deregistered `ParaId` before allowing deregistration; alternatively, block `deregister`/`swap` for any `ParaId` that still has an entry in `assigned_slots::PermanentSlots`/`TemporarySlots`, requiring `unassign_parachain_slot` to be called first. Also harden `allocate_temporary_slot_leases` to skip/purge `TemporarySlots` entries whose `ParaId` is no longer registered (`Registrar::manager_of(id).is_none()`).

### Proof of Concept
Rust unit test in `polkadot/runtime/common/src/assigned_slots/mod.rs` tests module:
1. Register para 1 via `TestRegistrar::register`, then `AssignedSlots::assign_temp_parachain_slot(RuntimeOrigin::root(), 1.into(), SlotLeasePeriodStart::Next)` — assert `TemporarySlotCount == 1`, lifecycle still `Parathread`.
2. As the manager (signed origin 1, matching `TestRegistrar` manager), call `TestRegistrar::<Test>::deregister(1.into())` directly through the equivalent signed registrar extrinsic path (or via `paras_registrar::Pallet::deregister` in an integration test using `paras_registrar` + `assigned_slots` wired together) — assert it succeeds (`Ok(())`).
3. Assert `assigned_slots::TemporarySlots::<Test>::get(1.into())` is still `Some(..)` and `TemporarySlotCount::<Test>::get() == 1` even though the para no longer exists in the registrar (`TestRegistrar::manager_of(1.into()) == None`).
4. Advance blocks to the next lease period boundary and call `AssignedSlots::allocate_temporary_slot_leases` (via `on_initialize`) — assert `ActiveTemporarySlotCount::<Test>::get()` increments for the deregistered id and that a real, still-registered competing temp-slot para (id 2, assigned in the same period) fails to get allocated because the zombie entry occupied the `MaxTemporarySlotPerLeasePeriod` capacity.

### Citations

**File:** polkadot/runtime/common/src/paras_registrar/mod.rs (L569-586)
```rust
impl<T: Config> Pallet<T> {
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

**File:** polkadot/runtime/common/src/assigned_slots/mod.rs (L352-399)
```rust
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

**File:** polkadot/runtime/common/src/assigned_slots/mod.rs (L491-567)
```rust
	fn allocate_temporary_slot_leases(lease_period_index: LeasePeriodOf<T>) -> DispatchResult {
		let mut active_temp_slots = 0u32;
		let mut pending_temp_slots = Vec::new();
		TemporarySlots::<T>::iter().for_each(|(para, slot)| {
				match slot.last_lease {
					Some(last_lease)
						if last_lease <= lease_period_index &&
							lease_period_index <
								(last_lease.saturating_add(slot.period_count)) =>
					{
						// Active slot lease
						active_temp_slots += 1;
					}
					Some(last_lease)
						// Slot w/ past lease, only consider it every other slot lease period (times period_count)
						if last_lease.saturating_add(slot.period_count.saturating_mul(2u32.into())) <= lease_period_index => {
							pending_temp_slots.push((para, slot));
					},
					None if slot.period_begin <= lease_period_index => {
						// Slot hasn't had a lease yet
						pending_temp_slots.insert(0, (para, slot));
					},
					_ => {
						// Slot not being considered for this lease period (will be for a subsequent one)
					},
				}
		});

		let mut newly_created_lease = 0u32;
		if active_temp_slots < T::MaxTemporarySlotPerLeasePeriod::get() &&
			!pending_temp_slots.is_empty()
		{
			// Sort by lease_count, favoring slots that had no or less turns first
			// (then by last_lease index, and then Para ID)
			pending_temp_slots.sort_by(|a, b| {
				a.1.lease_count
					.cmp(&b.1.lease_count)
					.then_with(|| a.1.last_lease.cmp(&b.1.last_lease))
					.then_with(|| a.0.cmp(&b.0))
			});

			let slots_to_be_upgraded = pending_temp_slots.iter().take(
				(T::MaxTemporarySlotPerLeasePeriod::get().saturating_sub(active_temp_slots))
					as usize,
			);

			for (id, temp_slot) in slots_to_be_upgraded {
				TemporarySlots::<T>::try_mutate::<_, _, Error<T>, _>(id, |s| {
					// Configure temp slot lease
					Self::configure_slot_lease(
						*id,
						temp_slot.manager.clone(),
						lease_period_index,
						temp_slot.period_count,
					)
					.map_err(|_| Error::<T>::CannotUpgrade)?;

					// Update temp slot lease info in storage
					*s = Some(ParachainTemporarySlot {
						manager: temp_slot.manager.clone(),
						period_begin: temp_slot.period_begin,
						period_count: temp_slot.period_count,
						last_lease: Some(lease_period_index),
						lease_count: temp_slot.lease_count + 1,
					});

					newly_created_lease += 1;

					Ok(())
				})?;
			}
		}

		ActiveTemporarySlotCount::<T>::set(active_temp_slots + newly_created_lease);

		Ok(())
	}
```

**File:** polkadot/runtime/common/src/slots/mod.rs (L227-301)
```rust
impl<T: Config> Pallet<T> {
	/// A new lease period is beginning. We're at the start of the first block of it.
	///
	/// We need to on-board and off-board parachains as needed. We should also handle reducing/
	/// returning deposits.
	fn manage_lease_period_start(lease_period_index: LeasePeriodOf<T>) -> Weight {
		Self::deposit_event(Event::<T>::NewLeasePeriod { lease_period: lease_period_index });

		let old_parachains = T::Registrar::parachains();

		// Figure out what chains need bringing on.
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
		parachains.sort();

		for para in parachains.iter() {
			if old_parachains.binary_search(para).is_err() {
				// incoming.
				let res = T::Registrar::make_parachain(*para);
				debug_assert!(res.is_ok());
			}
		}

		for para in old_parachains.iter() {
			if parachains.binary_search(para).is_err() {
				// outgoing.
				let res = T::Registrar::make_parathread(*para);
				debug_assert!(res.is_ok());
			}
		}
```

**File:** polkadot/runtime/common/src/slots/mod.rs (L343-413)
```rust
	fn lease_out(
		para: ParaId,
		leaser: &Self::AccountId,
		amount: <Self::Currency as Currency<Self::AccountId>>::Balance,
		period_begin: Self::LeasePeriod,
		period_count: Self::LeasePeriod,
	) -> Result<(), LeaseError> {
		let now = frame_system::Pallet::<T>::block_number();
		let (current_lease_period, _) =
			Self::lease_period_index(now).ok_or(LeaseError::NoLeasePeriod)?;
		// Finally, we update the deposit held so it is `amount` for the new lease period
		// indices that were won in the auction.
		let offset = period_begin
			.checked_sub(&current_lease_period)
			.and_then(|x| x.checked_into::<usize>())
			.ok_or(LeaseError::AlreadyEnded)?;

		// offset is the amount into the `Deposits` items list that our lease begins. `period_count`
		// is the number of items that it lasts for.

		// The lease period index range (begin, end) that newly belongs to this parachain
		// ID. We need to ensure that it features in `Deposits` to prevent it from being
		// reaped too early (any managed parachain whose `Deposits` set runs low will be
		// removed).
		Leases::<T>::try_mutate(para, |d| {
			// Left-pad with `None`s as necessary.
			if d.len() < offset {
				d.resize_with(offset, || None);
			}
			let period_count_usize =
				period_count.checked_into::<usize>().ok_or(LeaseError::AlreadyEnded)?;
			// Then place the deposit values for as long as the chain should exist.
			for i in offset..(offset + period_count_usize) {
				if d.len() > i {
					// Already exists but it's `None`. That means a later slot was already leased.
					// No problem.
					if d[i] == None {
						d[i] = Some((leaser.clone(), amount));
					} else {
						// The chain tried to lease the same period twice. This might be a griefing
						// attempt.
						//
						// We bail, not giving any lease and leave it for governance to sort out.
						return Err(LeaseError::AlreadyLeased);
					}
				} else if d.len() == i {
					// Doesn't exist. This is usual.
					d.push(Some((leaser.clone(), amount)));
				} else {
					// earlier resize means it must be >= i; qed
					// defensive code though since we really don't want to panic here.
				}
			}

			// Figure out whether we already have some funds of `leaser` held in reserve for
			// `para_id`.  If so, then we can deduct those from the amount that we need to reserve.
			let maybe_additional = amount.checked_sub(&Self::deposit_held(para, &leaser));
			if let Some(ref additional) = maybe_additional {
				T::Currency::reserve(&leaser, *additional)
					.map_err(|_| LeaseError::ReserveFailed)?;
			}

			let reserved = maybe_additional.unwrap_or_default();

			// Check if current lease period is same as period begin, and onboard them directly.
			// This will allow us to support onboarding new parachains in the middle of a lease
			// period.
			if current_lease_period == period_begin {
				// Best effort. Not much we can do if this fails.
				let _ = T::Registrar::make_parachain(para);
			}
```
