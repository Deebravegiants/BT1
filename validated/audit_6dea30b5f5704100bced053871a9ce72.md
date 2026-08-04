### Title
Deregistering a parathread does not clear stale `assigned_slots::PermanentSlots`/`TemporarySlots` entries, leaving `PermanentSlotCount`/`TemporarySlotCount` overcounted - ([File: polkadot/runtime/common/src/paras_registrar/mod.rs])

### Summary
`Registrar::do_deregister` only checks `paras::Pallet::lifecycle(id)` and has no dependency on, or knowledge of, the `assigned_slots` pallet's `PermanentSlots`/`TemporarySlots`/`PermanentSlotCount`/`TemporarySlotCount` storage. A parathread manager can call the ordinary, unprivileged `deregister` extrinsic once a previously assigned permanent/temporary slot lease naturally expires and the para's lifecycle reverts to `Parathread`, fully removing the para and refunding the manager's deposit while the stale slot bookkeeping in `assigned_slots` is left behind.

### Finding Description
`assign_perm_parachain_slot` (`polkadot/runtime/common/src/assigned_slots/mod.rs:259-310`) inserts an entry into `PermanentSlots::<T>` and increments `PermanentSlotCount::<T>` when a slot is assigned to a parathread. This is a one-way accounting operation: the only code path that removes a `PermanentSlots`/`TemporarySlots` entry and decrements the corresponding count is the privileged `unassign_parachain_slot` call (`assigned_slots/mod.rs:404-449`), gated by `T::AssignSlotOrigin`.

Once the slot lease's `PermanentSlotLeasePeriodLength` elapses, the underlying `slots` pallet lease naturally expires and the para's lifecycle is downgraded back to `Parathread` (confirmed by the existing unit test `assign_perm_slot_succeeds_for_parathread`, `assigned_slots/mod.rs:946-990`, which shows `is_parathread == true` after the lease period ends). However, this automatic downgrade never touches `PermanentSlots`/`PermanentSlotCount` - those only change via `assign_perm_parachain_slot`/`unassign_parachain_slot`.

At this point the para is again a normal `ParaLifecycle::Parathread`, and its manager is unprivileged (a signed account, `ensure_root_para_or_owner` at `paras_registrar/mod.rs:572-586` accepts the manager as long as the para is unlocked). The manager can call:

```
pub fn deregister(origin: OriginFor<T>, id: ParaId) -> DispatchResult {
    Self::ensure_root_para_or_owner(origin, id)?;
    Self::do_deregister(id)
}
```
(`paras_registrar/mod.rs:307-310`)

which invokes:
```rust
fn do_deregister(id: ParaId) -> DispatchResult {
    match paras::Pallet::<T>::lifecycle(id) {
        Some(ParaLifecycle::Parathread) | None => {},
        _ => return Err(Error::<T>::NotParathread.into()),
    }
    polkadot_runtime_parachains::schedule_para_cleanup::<T>(id)
        .map_err(|_| Error::<T>::CannotDeregister)?;

    if let Some(info) = Paras::<T>::take(&id) {
        <T as Config>::Currency::unreserve(&info.manager, info.deposit);
    }
    ...
}
```
(`paras_registrar/mod.rs:660-676`)

This code only reads `paras::Pallet::lifecycle` and never queries `assigned_slots::PermanentSlots`/`TemporarySlots`. Since the lifecycle is `Parathread` (post-expiry), the check passes, `schedule_para_cleanup` fully offboards the para (eventually purging `ParaLifecycles`, `Heads`, `CurrentCodeHash`, etc. in `paras::Pallet::apply_actions_queue`, `polkadot/runtime/parachains/src/paras/mod.rs:1588-1611`), the `Registrar::Paras` entry is removed, and the manager's `ParaDeposit` is unreserved. The `assigned_slots::PermanentSlots::<T>` map entry for `id` and the `PermanentSlotCount` increment, however, are never cleared - they were never made contingent on the para's continued existence in the registrar.

### Impact Explanation
After this sequence, `PermanentSlots::<T>::get(id)` still returns `Some((period, duration))` for a `ParaId` that no longer exists at all (not even as a parathread), and `PermanentSlotCount::<T>` remains incremented for a dead entry. Since `assign_perm_parachain_slot` gates new assignments with `ensure!(PermanentSlotCount::<T>::get() < MaxPermanentSlots::<T>::get(), Error::<T>::MaxPermanentSlotsExceeded)` (`assigned_slots/mod.rs:285-288`), this stale, uncorrectable-by-normal-flow count permanently occupies one slot of the finite `MaxPermanentSlots`/`MaxTemporarySlots` pool until a privileged `AssignSlotOrigin` account notices the inconsistency and calls `unassign_parachain_slot` to manually clear it. This is exactly the scoped impact: dangling/orphaned on-chain accounting state that blocks other legitimate slot assignments, i.e., a resource-seizure/DoS on the permanent (or temporary) slot pool, triggered entirely through an unprivileged, ordinary extrinsic (`deregister`) by the para's own manager.

### Likelihood Explanation
The precondition is a normal admin/governance action (assigning a slot via `assign_perm_parachain_slot`/`assign_temp_parachain_slot`), which is expected operational behavior, not an attack by itself. Once a slot is granted, the attacker only needs to (a) wait for the lease to naturally expire (a normal, guaranteed event within `PermanentSlotLeasePeriodLength`/`TemporarySlotLeasePeriodLength`), and (b) call the permissionless `deregister` extrinsic as the para manager. No special privileges, races, or protocol violations are needed, and this is fully reproducible deterministically every time a slot expires and its manager chooses to deregister instead of the assignor calling `unassign_parachain_slot` first.

### Recommendation
`do_deregister` (or `schedule_para_cleanup`) should check `assigned_slots::PermanentSlots`/`TemporarySlots` (or expose a hook, e.g. via an `OnDeregister`/`OnOffboard` trait implemented for the `AssignedSlots` pallet) and either: (1) refuse to deregister a para that still has an active `PermanentSlots`/`TemporarySlots` entry, forcing `unassign_parachain_slot` first; or (2) automatically remove the `PermanentSlots`/`TemporarySlots` entry and decrement the corresponding count as part of `do_deregister`'s cleanup, keeping the counts in sync with the registrar's source of truth.

### Proof of Concept
Rust integration test (in `polkadot/runtime/common/src/assigned_slots/mod.rs` test module, using `TestRegistrar`/`Slots`/`AssignedSlots` mocks already present):
```rust
#[test]
fn deregister_leaves_stale_permanent_slot_accounting() {
    new_test_ext().execute_with(|| {
        let mut block = 1;
        System::run_to_block::<AllPalletsWithSystem>(block);
        assert_ok!(TestRegistrar::<Test>::register(
            1, ParaId::from(1_u32), dummy_head_data(), dummy_validation_code(),
        ));
        assert_ok!(AssignedSlots::assign_perm_parachain_slot(
            RuntimeOrigin::root(), ParaId::from(1_u32),
        ));
        assert_eq!(assigned_slots::PermanentSlotCount::<Test>::get(), 1);

        // Run past the lease period so it naturally reverts to Parathread.
        while block < 9 {
            block += 1;
            System::run_to_block::<AllPalletsWithSystem>(block);
        }
        assert_eq!(TestRegistrar::<Test>::is_parathread(ParaId::from(1_u32)), true);

        // Manager deregisters the parathread via the ordinary, unprivileged path.
        assert_ok!(mock::Registrar::deregister(
            RuntimeOrigin::signed(1), ParaId::from(1_u32),
        ));

        // BUG: stale slot accounting remains even though para no longer exists.
        assert_eq!(assigned_slots::PermanentSlotCount::<Test>::get(), 1); // should be 0
        assert!(assigned_slots::PermanentSlots::<Test>::get(ParaId::from(1_u32)).is_some()); // should be None

        // A second, unrelated user cannot get a permanent slot even though
        // the pool should logically have room, if MaxPermanentSlots == 1.
        assert_ok!(TestRegistrar::<Test>::register(
            2, ParaId::from(2_u32), dummy_head_data(), dummy_validation_code(),
        ));
        assert_noop!(
            AssignedSlots::assign_perm_parachain_slot(RuntimeOrigin::root(), ParaId::from(2_u32)),
            Error::<Test>::MaxPermanentSlotsExceeded
        );
    });
}
```
Expected assertions confirm: `PermanentSlotCount` remains `1` and `PermanentSlots` entry survives after full deregistration of the para, and a new, unrelated para is incorrectly blocked from obtaining a permanent slot due to the stale counter.