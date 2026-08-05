### Title
`paras_registrar::swap` desyncs `assigned_slots::{TemporarySlots,PermanentSlots}` from `slots::Leases` because `AssignedSlots` is not wired into `T::OnSwap` - ([File: polkadot/runtime/common/src/assigned_slots/mod.rs])

### Summary
`paras_registrar::swap` is callable by an unprivileged para owner via `Self::ensure_root_para_or_owner(origin, id)` [1](#0-0) , and it triggers `T::OnSwap::on_swap` to migrate per-`ParaId` state between the two swapped IDs [2](#0-1) . In the Rococo runtime, `OnSwap = (Crowdloan, Slots, SwapLeases)` [3](#0-2) , which swaps `slots::Leases` [4](#0-3)  but does **not** include `assigned_slots::Pallet`, so `TemporarySlots`/`PermanentSlots` (keyed by `ParaId`) are left untouched, causing them to desync from the actual lease holder after a swap.

### Finding Description
`assigned_slots::TemporarySlots` and `PermanentSlots` are `StorageMap<_, Twox64Concat, ParaId, ...>` entries [5](#0-4) . These maps track which `ParaId` owns an assigned slot and drive periodic re-leasing via `allocate_temporary_slot_leases`, which reads `TemporarySlots::<T>::iter()` and calls `configure_slot_lease`/`Leaser::lease_out` (ultimately `T::Registrar::make_parachain`) purely based on the `ParaId` key stored there [6](#0-5) .

Separately, `slots::Pallet` implements `OnSwap::on_swap` by swapping `Leases::<T>` between the two `ParaId`s [4](#0-3) . `paras_registrar::swap` is reachable by the para owner (not just Root) through `ensure_root_para_or_owner`, and for a Parachain/Parathread pair it calls `do_thread_and_chain_swap`, which schedules the lifecycle changes and then calls `T::OnSwap::on_swap(to_upgrade, to_downgrade)` [7](#0-6) [2](#0-1) .

Because `assigned_slots::Pallet` does not implement `OnSwap` and is not present in the runtime's `OnSwap` tuple (`(Crowdloan, Slots, SwapLeases)` for Rococo, confirmed at the config site) [3](#0-2) , a swap correctly moves the actual lease (`slots::Leases`) and lifecycle status (Parachain vs Parathread) between the two `ParaId`s, but leaves `assigned_slots::TemporarySlots`/`PermanentSlots` keyed on the *original* `ParaId`. After the swap:
- `AssignedSlots::has_temporary_slot(original_id)` still returns `true`, even though `original_id` is now a Parathread and no longer holds the lease.
- The para that now actually holds the lease and Parachain status (`other`) has no `TemporarySlots`/`PermanentSlots` entry.
- At the next lease-period boundary, `allocate_temporary_slot_leases` will still process `TemporarySlots::<T>::get(original_id)` and call `Leaser::lease_out`/`make_parachain(original_id)` again, re-granting parachain status to `original_id` — silently reversing the swap outcome for on-chain lifecycle purposes and corrupting the notion of which para is "using" the temp slot, while `ActiveTemporarySlotCount` bookkeeping (only updated in `unassign_parachain_slot` and `allocate_temporary_slot_leases`) becomes inconsistent with the real number of paras that are actually parachains.

No check in `paras_registrar::swap` or `Slots::on_swap` consults `assigned_slots` storage at all, so nothing prevents or reconciles this desync.

### Impact Explanation
This produces a genuine state-transition/accounting desync between `assigned_slots` and `paras_registrar`/`slots`, exactly matching the scoped impact: `TemporarySlots`/`PermanentSlots` no longer track the actual lease holder, `ActiveTemporarySlotCount` can diverge from reality, and re-allocation logic can silently re-grant/revoke parachain status independent of the swap the owner performed, which can trap or misallocate a scarce temporary/permanent slot resource. This is limited to runtimes that both enable `assigned_slots` and `paras_registrar::swap` with an owner-controllable origin (i.e., Rococo-style test relay chains, per the pallet's own doc comment stating it is intended only for test relay chains) [8](#0-7) .

### Likelihood Explanation
Feasible and repeatable given: (1) an assigned temp/perm slot para exists (root sets this up once, as acknowledged in the question), (2) the para manager is unlocked (owner can call registrar extrinsics), and (3) a second on-demand para exists to swap with. The manager only needs two unprivileged `Registrar::swap` calls (one to propose, one to confirm from the other side, or from itself if it also controls/colludes with the other para's owner) — both directions are demonstrated to work as owner-only calls in the existing test suite [9](#0-8) . No governance or root call is required after the initial (out-of-scope) slot assignment.

### Recommendation
Add `assigned_slots::Pallet<T>` as an `OnSwap` implementer (analogous to `slots::Pallet` and `crowdloan::Pallet`), swapping `TemporarySlots` and `PermanentSlots` entries (and any per-id state needed to keep `ActiveTemporarySlotCount`/`TemporarySlotCount` consistent) between the two `ParaId`s whenever `on_swap` fires, and include it in each runtime's `OnSwap` tuple (e.g., `(Crowdloan, Slots, AssignedSlots, SwapLeases)`).

### Proof of Concept
Rust integration test (extend `polkadot/runtime/common/src/assigned_slots/mod.rs` test harness, wiring in `paras_registrar::Pallet` with `OnSwap = (Slots,)` as currently configured, i.e. without `AssignedSlots`):
1. Root: `AssignedSlots::assign_temp_parachain_slot(root, id, SlotLeasePeriodStart::Current)` — `id` becomes a Parachain with `TemporarySlots::<Test>::get(id) = Some(..)`, `slots::Leases::<Test>::get(id)` populated, `ActiveTemporarySlotCount == 1`.
2. Register a second on-demand para `other` (Parathread).
3. Manager (owner) calls `Registrar::swap(para_origin(id), id, other)` then `Registrar::swap(para_origin(other), other, id)` (both owner-signed, no root).
4. Advance to next session/lease period.
5. Assert:
   - `paras::Pallet::lifecycle(other) == Some(ParaLifecycle::Parachain)`, `lifecycle(id) == Some(ParaLifecycle::Parathread)` (swap took effect at the lifecycle/lease level).
   - `slots::Leases::<Test>::get(other)` is non-empty (lease moved) and `slots::Leases::<Test>::get(id)` is empty/default.
   - `AssignedSlots::has_temporary_slot(id) == true` and `AssignedSlots::has_temporary_slot(other) == false` — proving the desync: the slot-tracking storage still points at `id` even though `id` no longer holds the lease or Parachain status.
   - After the next lease-period tick, observe `allocate_temporary_slot_leases` re-promoting `id` to Parachain via `TemporarySlots::<Test>::get(id)`, contradicting the swap and corrupting `ActiveTemporarySlotCount`/`TemporarySlotCount` relative to actual parachain count.

### Citations

**File:** polkadot/runtime/common/src/paras_registrar/mod.rs (L326-327)
```rust
		pub fn swap(origin: OriginFor<T>, id: ParaId, other: ParaId) -> DispatchResult {
			Self::ensure_root_para_or_owner(origin, id)?;
```

**File:** polkadot/runtime/common/src/paras_registrar/mod.rs (L343-363)
```rust
				// identify which is a lease holding parachain and which is a parathread (on-demand
				// parachain)
				if id_lifecycle == ParaLifecycle::Parachain &&
					other_lifecycle == ParaLifecycle::Parathread
				{
					Self::do_thread_and_chain_swap(id, other);
				} else if id_lifecycle == ParaLifecycle::Parathread &&
					other_lifecycle == ParaLifecycle::Parachain
				{
					Self::do_thread_and_chain_swap(other, id);
				} else if id_lifecycle == ParaLifecycle::Parachain &&
					other_lifecycle == ParaLifecycle::Parachain
				{
					// If both chains are currently parachains, there is nothing funny we
					// need to do for their lifecycle management, just swap the underlying
					// data.
					T::OnSwap::on_swap(id, other);
				} else {
					return Err(Error::<T>::CannotSwap.into());
				}
				Self::deposit_event(Event::<T>::Swapped { para_id: id, other_id: other });
```

**File:** polkadot/runtime/common/src/paras_registrar/mod.rs (L704-710)
```rust
	fn do_thread_and_chain_swap(to_downgrade: ParaId, to_upgrade: ParaId) {
		let res1 = polkadot_runtime_parachains::schedule_parachain_downgrade::<T>(to_downgrade);
		debug_assert!(res1.is_ok());
		let res2 = polkadot_runtime_parachains::schedule_parathread_upgrade::<T>(to_upgrade);
		debug_assert!(res2.is_ok());
		T::OnSwap::on_swap(to_upgrade, to_downgrade);
	}
```

**File:** polkadot/runtime/rococo/src/lib.rs (L1239-1247)
```rust
impl paras_registrar::Config for Runtime {
	type RuntimeOrigin = RuntimeOrigin;
	type RuntimeEvent = RuntimeEvent;
	type Currency = Balances;
	type OnSwap = (Crowdloan, Slots, SwapLeases);
	type ParaDeposit = ParaDeposit;
	type DataDepositPerByte = DataDepositPerByte;
	type WeightInfo = weights::polkadot_runtime_common_paras_registrar::WeightInfo<Runtime>;
}
```

**File:** polkadot/runtime/common/src/slots/mod.rs (L332-336)
```rust
impl<T: Config> crate::traits::OnSwap for Pallet<T> {
	fn on_swap(one: ParaId, other: ParaId) {
		Leases::<T>::mutate(one, |x| Leases::<T>::mutate(other, |y| core::mem::swap(x, y)))
	}
}
```

**File:** polkadot/runtime/common/src/assigned_slots/mod.rs (L17-24)
```rust
//! This pallet allows to assign permanent (long-lived) or temporary
//! (short-lived) parachain slots to paras, leveraging the existing
//! parachain slot lease mechanism. Temporary slots are given turns
//! in a fair (though best-effort) manner.
//! The dispatchables must be called from the configured origin
//! (typically `Sudo` or a governance origin).
//! This pallet should not be used on a production relay chain,
//! only on a test relay chain (e.g. Rococo).
```

**File:** polkadot/runtime/common/src/assigned_slots/mod.rs (L150-167)
```rust
	/// Assigned permanent slots, with their start lease period, and duration.
	#[pallet::storage]
	pub type PermanentSlots<T: Config> =
		StorageMap<_, Twox64Concat, ParaId, (LeasePeriodOf<T>, LeasePeriodOf<T>), OptionQuery>;

	/// Number of assigned (and active) permanent slots.
	#[pallet::storage]
	pub type PermanentSlotCount<T: Config> = StorageValue<_, u32, ValueQuery>;

	/// Assigned temporary slots.
	#[pallet::storage]
	pub type TemporarySlots<T: Config> = StorageMap<
		_,
		Twox64Concat,
		ParaId,
		ParachainTemporarySlot<T::AccountId, LeasePeriodOf<T>>,
		OptionQuery,
	>;
```

**File:** polkadot/runtime/common/src/assigned_slots/mod.rs (L491-561)
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
```

**File:** polkadot/runtime/common/src/paras_registrar/tests.rs (L366-372)
```rust
		// Swap between parathread and parachain
		assert_ok!(mock::Registrar::swap(para_origin(para_1), para_1, para_2,));
		assert_ok!(mock::Registrar::swap(para_origin(para_2), para_2, para_1,));
		System::assert_last_event(RuntimeEvent::Registrar(paras_registrar::Event::Swapped {
			para_id: para_2,
			other_id: para_1,
		}));
```
