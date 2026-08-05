## Analysis Result

Based on the code reviewed, this describes a real, confirmed inconsistency in the `OnSwap` wiring, but its practical exploit value against the specific invariant claimed needs qualification.

### Title
`AssignedSlots::TemporarySlots`/`PermanentSlots` desynchronize from `slots::Leases` after unprivileged `paras_registrar::swap` - ([File: polkadot/runtime/common/src/assigned_slots/mod.rs])

### Summary
The `paras_registrar::swap` extrinsic is gated by `Self::ensure_root_para_or_owner(origin, id)?`, which permits the para's manager/owner (an unprivileged signed account) to call it, not just root. [1](#0-0) . In both Rococo and Westend runtimes, `paras_registrar::Config::OnSwap` is configured as `(Crowdloan, Slots, SwapLeases)` — the `assigned_slots` pallet is **not** included in the `OnSwap` tuple. [2](#0-1) [3](#0-2) 

### Finding Description
`slots::Pallet::on_swap` swaps the `Leases` storage map entries keyed by `ParaId`: [4](#0-3) . Meanwhile `assigned_slots::TemporarySlots`/`PermanentSlots` are storage maps keyed by the same `ParaId`: [5](#0-4) . Since `assigned_slots::Pallet` implements no `OnSwap` hook and is not wired into `T::OnSwap` in either Rococo or Westend, calling `Registrar::swap(id, other)` (both directions, confirmatory) via the unprivileged `ensure_root_para_or_owner` path moves the underlying `slots::Leases` entry to the other `ParaId` (and swaps lifecycle for chain/thread swaps) while leaving `assigned_slots::TemporarySlots`/`PermanentSlots` still keyed to the original `id`. This produces the described desync: `AssignedSlots::has_temporary_slot(id)` continues to report `true` for a para whose lease has actually moved to `other`, while `slots::Leases(other)` now holds the real lease. This satisfies the reachable-path requirement (`swap` is unprivileged for a para owner) and the storage-key mismatch described in the audit prompt.

However, note important caveats that limit real exploitability of the "corruption" framing:
- `assigned_slots::TemporarySlots`/`PermanentSlots` are purely **bookkeeping structures internal to the `assigned_slots` pallet** used only for `allocate_temporary_slot_leases` scheduling and `unassign_parachain_slot` accounting; they do not themselves grant parachain status. Actual parachain status derives from `paras::ParaLifecycle` and `slots::Leases`, both of which `paras_registrar::swap` does correctly update/swap via `do_thread_and_chain_swap` and `T::OnSwap::on_swap`. So a swap does not let an unswapped para "continue parachain status" it wasn't otherwise entitled to under `paras`/`slots` — lifecycle and lease ownership stay internally consistent between `paras` and `slots`.
- The desync is confined to `assigned_slots`' own record-keeping (`TemporarySlots`, `PermanentSlots`, `ActiveTemporarySlotCount`). This can cause `allocate_temporary_slot_leases` to later attempt to re-lease/renew a lease for the wrong `ParaId` (the original `id`, which is no longer the parachain holding that lease), potentially failing (`OngoingLeaseExists`/logged warning) or creating an incorrect lease renewal for a para that never had a legitimate temp slot assignment. `ActiveTemporarySlotCount` can also become permanently miscounted since `unassign_parachain_slot`'s decrement logic keys off `TemporarySlots::contains_key(id)` and `is_parachain(id)`, which may no longer correspond to reality post-swap.

### Impact Explanation
Concrete scoped impact: `assigned_slots` accounting (`TemporarySlots`, `PermanentSlots`, `ActiveTemporarySlotCount`) becomes decoupled from actual `slots::Leases` ownership after an unprivileged, reachable `swap`. This can corrupt the fairness/turn-rotation logic of `allocate_temporary_slot_leases` (a para not entitled to a slot could get re-leased due to stale `TemporarySlots` entry pointing at the wrong `ParaId`) and can leave `ActiveTemporarySlotCount`/`TemporarySlotCount` permanently miscounted, denying legitimate temporary-slot rotation to other paras or trapping the privileged `unassign_parachain_slot`/`assign_temp_parachain_slot` flows into `SlotAlreadyAssigned`/`MaxTemporarySlotsExceeded` inconsistent states. This is a state-accounting bug, not a direct fund-theft or unauthorized-parachain-status bug, since `paras::ParaLifecycle` and `slots::Leases` remain internally consistent with each other.

### Likelihood Explanation
Fully feasible and repeatable by any unprivileged para manager: preconditions are only that (1) the manager's para currently has an assigned temp/perm slot (root-assigned, but this is a normal, expected relay-chain-test-network operation, not attacker-controlled setup) and (2) a second on-demand parachain with an unlocked manager exists to swap with. The `swap` call sequence (both directions to confirm) is a standard documented usage of `paras_registrar::swap` and requires no special origin beyond being the para owner (`ensure_root_para_or_owner`). This is a genuine oversight in `OnSwap` composition rather than requiring any privileged/root action from the attacker.

### Recommendation
Add an `OnSwap` implementation for `assigned_slots::Pallet` that mirrors/swaps `TemporarySlots`, `PermanentSlots` (and adjusts `ActiveTemporarySlotCount` bookkeeping as needed) between `one`/`other`, analogous to `slots::Pallet::on_swap` and `crowdloan::Pallet::on_swap`, and include `AssignedSlots` in the `type OnSwap = (...)` tuple for Rococo/Westend runtimes. Alternatively, since the pallet doc states it "should not be used on a production relay chain, only on a test relay chain," at minimum add a `try-runtime`/`debug_assert` invariant check ensuring `TemporarySlots`/`PermanentSlots` keys stay consistent with `slots::Leases` non-emptiness after any `OnSwap::on_swap` invocation for that `ParaId`.

### Proof of Concept
Integration test (in `assigned_slots` test harness combined with `paras_registrar`):
1. Register `para_1` and `para_2` (para_2 as on-demand/parathread).
2. As root, call `AssignedSlots::assign_temp_parachain_slot(root, para_1, Current)`; run to next lease period so `para_1` is upgraded to `ParaLifecycle::Parachain` and `slots::Leases(para_1)` populated; assert `AssignedSlots::has_temporary_slot(para_1) == true`.
3. As `para_1`'s manager (signed, unprivileged), call `Registrar::swap(para_origin(para_1), para_1, para_2)`.
4. As `para_2`'s manager (signed, unprivileged), call `Registrar::swap(para_origin(para_2), para_2, para_1)` to confirm the swap.
5. Run to next session/lease period.
6. Assert: `slots::Leases::get(para_2)` now contains the lease data previously under `para_1` (swap succeeded at the `slots` layer) — confirming `paras::lifecycle(para_2) == Parachain`.
7. Assert (bug confirmation): `AssignedSlots::TemporarySlots::get(para_1)` still returns `Some(...)` (stale) while the actual lease-holding para is now `para_2`, and `AssignedSlots::has_temporary_slot(para_2) == false` despite `para_2` now holding the temp-slot-originated lease — demonstrating the key desync between `assigned_slots` bookkeeping and `slots::Leases`/`paras::lifecycle`.

### Citations

**File:** polkadot/runtime/common/src/paras_registrar/mod.rs (L324-327)
```rust
		#[pallet::call_index(3)]
		#[pallet::weight(<T as Config>::WeightInfo::swap())]
		pub fn swap(origin: OriginFor<T>, id: ParaId, other: ParaId) -> DispatchResult {
			Self::ensure_root_para_or_owner(origin, id)?;
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

**File:** polkadot/runtime/westend/src/lib.rs (L1275-1283)
```rust
impl paras_registrar::Config for Runtime {
	type RuntimeOrigin = RuntimeOrigin;
	type RuntimeEvent = RuntimeEvent;
	type Currency = Balances;
	type OnSwap = (Crowdloan, Slots, SwapLeases);
	type ParaDeposit = ParaDeposit;
	type DataDepositPerByte = RegistrarDataDepositPerByte;
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

**File:** polkadot/runtime/common/src/assigned_slots/mod.rs (L150-171)
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

	/// Number of assigned temporary slots.
	#[pallet::storage]
	pub type TemporarySlotCount<T: Config> = StorageValue<_, u32, ValueQuery>;
```
