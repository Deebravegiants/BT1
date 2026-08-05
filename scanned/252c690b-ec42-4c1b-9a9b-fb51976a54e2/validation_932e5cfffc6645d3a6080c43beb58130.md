### Title
Stale `TemporarySlots` entry allows lease seizure by an unrelated para manager after deregister/register of the same `ParaId` - (File: `polkadot/runtime/common/src/assigned_slots/mod.rs`)

### Summary
`assign_temp_parachain_slot` with `SlotLeasePeriodStart::Next` writes a `TemporarySlots` entry immediately but defers the actual lease creation to `allocate_temporary_slot_leases`, which runs later in `on_initialize`/`manage_lease_period_start`. Because `paras_registrar` has no dependency on, or knowledge of, the `assigned_slots` pallet, `deregister`/`register` do not touch `TemporarySlots`/`PermanentSlots`, so the pending slot assignment survives a deregister+re-register cycle and materializes against whoever currently controls the reused `ParaId`.

### Finding Description
`assign_temp_parachain_slot` inserts into `TemporarySlots::<T>` unconditionally at the end of the call for the `Next` branch, without creating a lease at that time: [1](#0-0) 

The actual lease is only created later by `allocate_temporary_slot_leases`, which is driven purely by iterating `TemporarySlots::<T>` and calling `configure_slot_lease` with the manager stored at *assignment time*, not the manager currently on record in `paras_registrar`: [2](#0-1) 

`configure_slot_lease` simply forwards to `T::Leaser::lease_out`, which operates on the `ParaId` directly (triggering the parachain upgrade for that id) and is agnostic of `paras_registrar`'s current manager for that id: [3](#0-2) 

Crucially, `unassign_parachain_slot` — the only extrinsic that removes `TemporarySlots`/`PermanentSlots` entries — is gated by `AssignSlotOrigin` and is never invoked from `paras_registrar`: [4](#0-3) 

`paras_registrar`'s imports show no coupling to `assigned_slots` at all: it only pulls in `configuration`, `paras`, and its own traits, meaning `deregister`/`register` cannot and do not invalidate `TemporarySlots`: [5](#0-4) 

Exploit flow:
1. `AssignSlotOrigin` calls `assign_temp_parachain_slot(id, Next)` for a para whose manager is the attacker. `TemporarySlots::<T>` now holds `{manager: attacker, period_begin: next_period, last_lease: None, ...}`, with no lease materialized yet (attacker's para is still a plain parathread).
2. Attacker (still the current manager, satisfying any manager-only check in `deregister`) calls `paras_registrar::deregister(id)`. Since no lease exists yet (`Next` branch, deferred), the para's `ParaLifecycle` is still `Parathread`, so any lifecycle guard in `deregister` is satisfied and deregistration succeeds. `TemporarySlots::<T>[id]` is untouched.
3. The `ParaId` becomes free. A different, unrelated account calls `paras_registrar::register(id, ...)`, becoming the new manager of that `ParaId`.
4. At the start of the next lease period, `on_initialize` → `manage_lease_period_start` → `allocate_temporary_slot_leases` iterates `TemporarySlots::<T>` and finds the still-present entry for `id`, whose `period_begin` has now arrived. It calls `configure_slot_lease(id, attacker, ...)`, which calls `Leaser::lease_out(id, &attacker, ...)`. This upgrades the **`ParaId`** to a lease-holding parachain — a state change that benefits whoever controls that `ParaId` in `paras_registrar`, i.e. the new, unrelated manager, not the original attacker and certainly not anyone vetted by `AssignSlotOrigin`.

Because `has_temporary_slot`/`has_permanent_slot` only check `TemporarySlots`/`PermanentSlots` key existence for the `ParaId` (not manager identity), and because `configure_slot_lease` never re-validates `T::Registrar::manager_of(id)` against the manager captured at assignment time, the desync goes undetected and the deferred lease is granted against a `ParaId` that has since changed ownership.

### Impact Explanation
An unrelated, unprivileged para manager who registers a previously-deregistered `ParaId` can passively inherit a governance/`AssignSlotOrigin`-approved temporary parachain slot upgrade that was never intended for them, gaining lease-holding-parachain status (coretime/block-production rights) without ever going through `AssignSlotOrigin`. This is a concrete instance of "lease seizure by an unrelated manager" as scoped.

### Likelihood Explanation
Requires only: (a) `AssignSlotOrigin` to have assigned a `Next`-period temp slot to a para (a normal, expected governance action on chains using this pallet, e.g. test/parachain-slot relay chains), and (b) the current manager of that para (an unprivileged, ordinary account) to deregister and have someone re-register the same `ParaId` before the next lease-period boundary. Both `deregister` and `register` are standard signed extrinsics with no interaction with `assigned_slots` state, so the race is fully reproducible by the para's own manager without any special privilege, and is deterministic given the deferred (`Next`) branch always leaves a materialization window of at least one lease period.

### Recommendation
- In `paras_registrar::deregister` (or via a hook/trait), invalidate any pending `assigned_slots::TemporarySlots`/`PermanentSlots` entry for the deregistered `ParaId` (e.g. expose a `Config::OnParaDeregistered` hook that `assigned_slots` implements to purge its storage).
- Alternatively, in `allocate_temporary_slot_leases`/`configure_slot_lease`, re-validate that `T::Registrar::manager_of(id)` still equals `temp_slot.manager` (and that the para is still a parathread/not deregistered) immediately before calling `Leaser::lease_out`, and drop/skip the entry (with an event) if it has desynced.

### Proof of Concept
Rust integration test (in `assigned_slots` mock runtime, extending existing tests in `polkadot/runtime/common/src/assigned_slots/mod.rs`):
1. Register para `id=1` with manager `A` via `TestRegistrar::register`.
2. Call `AssignedSlots::assign_temp_parachain_slot(RuntimeOrigin::root(), id, SlotLeasePeriodStart::Next)`. Assert `TemporarySlots::<Test>::get(id).unwrap().manager == A` and `Slots::already_leased(id, ..) == false`.
3. Call `TestRegistrar::deregister(RuntimeOrigin::signed(A), id)`. Assert it succeeds and `TemporarySlots::<Test>::contains_key(id) == true` (stale entry remains).
4. Register the same `id` again via `TestRegistrar::register(RuntimeOrigin::signed(B), id, ...)` where `B != A`.
5. Advance blocks to the next lease period boundary (`System::run_to_block` past `period_begin`), triggering `manage_lease_period_start` → `allocate_temporary_slot_leases`.
6. Assert `Slots::already_leased(id, next_period, ..) == true` and that the para (now controlled by `B`) is a lease-holding parachain (`TestRegistrar::is_parachain(id) == true`), demonstrating that manager `B`, who never went through `AssignSlotOrigin`, received the parachain upgrade tied to the stale `TemporarySlots` entry originally created for `A`.

### Citations

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

**File:** polkadot/runtime/common/src/assigned_slots/mod.rs (L401-429)
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
```

**File:** polkadot/runtime/common/src/assigned_slots/mod.rs (L537-561)
```rust
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

**File:** polkadot/runtime/common/src/assigned_slots/mod.rs (L575-584)
```rust
	/// Create a parachain slot lease based on given params.
	/// The function merely calls out to `Leaser::lease_out`.
	fn configure_slot_lease(
		para: ParaId,
		manager: T::AccountId,
		lease_period: LeasePeriodOf<T>,
		lease_duration: LeasePeriodOf<T>,
	) -> Result<(), LeaseError> {
		T::Leaser::lease_out(para, &manager, BalanceOf::<T>::zero(), lease_period, lease_duration)
	}
```

**File:** polkadot/runtime/common/src/paras_registrar/mod.rs (L30-48)
```rust
use frame_system::{self, ensure_root, ensure_signed};
use polkadot_primitives::{
	HeadData, Id as ParaId, ValidationCode, LOWEST_PUBLIC_ID, MIN_CODE_SIZE,
};
use polkadot_runtime_parachains::{
	configuration, ensure_parachain,
	paras::{self, ParaGenesisArgs, UpgradeStrategy},
	Origin, ParaLifecycle,
};

use crate::traits::{OnSwap, Registrar};
use codec::{Decode, DecodeWithMemTracking, Encode, MaxEncodedLen};
pub use pallet::*;
use polkadot_runtime_parachains::paras::{OnNewHead, ParaKind};
use scale_info::TypeInfo;
use sp_runtime::{
	traits::{CheckedSub, Saturating},
	Debug,
};
```
