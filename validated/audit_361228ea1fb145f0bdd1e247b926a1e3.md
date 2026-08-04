[1](#0-0) [2](#0-1) [3](#0-2) [4](#0-3)

### Citations

**File:** polkadot/runtime/common/src/assigned_slots/mod.rs (L259-260)
```rust
		pub fn assign_perm_parachain_slot(origin: OriginFor<T>, id: ParaId) -> DispatchResult {
			T::AssignSlotOrigin::ensure_origin(origin)?;
```

**File:** polkadot/runtime/common/src/assigned_slots/mod.rs (L271-283)
```rust
			let current_lease_period: BlockNumberFor<T> = Self::current_lease_period_index();
			ensure!(
				!T::Leaser::already_leased(
					id,
					current_lease_period,
					// Check current lease & next one
					current_lease_period.saturating_add(
						BlockNumberFor::<T>::from(2u32)
							.saturating_mul(T::PermanentSlotLeasePeriodLength::get().into())
					)
				),
				Error::<T>::OngoingLeaseExists
			);
```

**File:** polkadot/runtime/common/src/assigned_slots/mod.rs (L317-322)
```rust
		pub fn assign_temp_parachain_slot(
			origin: OriginFor<T>,
			id: ParaId,
			lease_period_start: SlotLeasePeriodStart,
		) -> DispatchResult {
			T::AssignSlotOrigin::ensure_origin(origin)?;
```

**File:** polkadot/runtime/common/src/assigned_slots/mod.rs (L333-345)
```rust
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
```
