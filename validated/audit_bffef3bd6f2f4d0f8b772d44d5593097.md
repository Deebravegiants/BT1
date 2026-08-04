### Title
Unprivileged auction win against a para with a pending `AssignedSlots` temporary slot causes `allocate_temporary_slot_leases` to abort its entire batch via early-return `?`, denying other paras their scheduled temp-slot turn - (File: `polkadot/runtime/common/src/assigned_slots/mod.rs`)

### Summary
`AssignedSlots::assign_temp_parachain_slot` only checks `T::Leaser::already_leased` for the current lease period plus the next `2 * TemporarySlotLeasePeriodLength` periods, and that check is never re-verified later. An unprivileged account (e.g. the para's own manager, or anyone) can subsequently win a `slots` pallet lease via `Auctions::bid`/`Crowdloan` for a future lease period range that overlaps the period `AssignedSlots::allocate_temporary_slot_leases` will later try to configure for that para. When that period arrives, `Self::configure_slot_lease` fails with `LeaseError::AlreadyLeased`, and because the `for` loop in `allocate_temporary_slot_leases` propagates the error with `?` on `TemporarySlots::try_mutate(...)?`, the *entire* function returns early, skipping every other still-unprocessed pending para in that batch and never reaching the `ActiveTemporarySlotCount::<T>::set(...)` update.

### Finding Description
`Pallet::assign_temp_parachain_slot` guards only a bounded near-term window: [1](#0-0) 
This does not protect lease periods further in the future — periods where the temp slot will recur after a prior turn (`last_lease + 2*period_count`), or the very first `period_begin` if it is set via `SlotLeasePeriodStart::Next` and the para's manager delays acting on it. `Auctions::handle_bid` only rejects bids that overlap an *existing* `slots::Leases` entry: [2](#0-1) 
Since `AssignedSlots` only calls `T::Leaser::lease_out` lazily — either immediately in `assign_temp_parachain_slot` or later in `allocate_temporary_slot_leases` at the relevant lease-period boundary — there is no `slots::Leases` entry yet for a future recurring temp-slot period, so nothing stops a signed account from bidding on (and, via `Crowdloan`, winning) that exact future period range for the same para. `Auctions::bid` requires only `ensure_signed`, no special privilege: [3](#0-2) 

When the conflicting period arrives, `allocate_temporary_slot_leases` iterates pending slots and tries to configure a lease for each: [4](#0-3) 
`configure_slot_lease` simply forwards to `T::Leaser::lease_out`, which returns `LeaseError::AlreadyLeased` for a period already occupied by the attacker's won lease: [5](#0-4) 
The `?` after `try_mutate(...)` at line 560 propagates the `Err` out of `allocate_temporary_slot_leases` immediately, short-circuiting the `for` loop over `slots_to_be_upgraded` before it reaches any subsequent (unrelated) para in the batch, and before the `ActiveTemporarySlotCount::<T>::set(active_temp_slots + newly_created_lease)` line is ever executed: [6](#0-5) 
Because `try_mutate` does not commit a mutation on `Err`, the affected para's own `TemporarySlots` entry is left untouched (its `last_lease`/`lease_count` are not advanced) — it is not literally corrupted, but it remains eligible as "pending" indefinitely and will be retried (and can conflict again if the attacker keeps re-winning overlapping auctions). Meanwhile, every other para that was queued later in `slots_to_be_upgraded` for that same lease-period boundary is silently skipped for that period because the caller (`on_initialize` → `manage_lease_period_start`) only logs the error, per the question's own description, and does not retry the remaining entries within the same period.

### Impact Explanation
A single unprivileged account can, by legitimately winning a `slots` auction/crowdloan for a period overlapping a para's scheduled `AssignedSlots` temp-slot turn, cause the whole `allocate_temporary_slot_leases` batch update for that lease-period boundary to abort early. This denies the temp-slot turn not only to the conflicting para but to every other pending para later in the sorted `slots_to_be_upgraded` iterator for that period, and leaves `ActiveTemporarySlotCount` un-refreshed for that period. The affected para's own entry is not advanced and remains "pending," so the conflict can recur if the attacker keeps winning overlapping future auctions, extending the denial of service across lease-period boundaries. This is a genuine batch-isolation/error-handling bug (missing per-item error isolation, i.e. the `?` should not propagate out of the loop), not literal permanent storage corruption, since `try_mutate` leaves state unchanged on failure.

### Likelihood Explanation
Feasible: `Auctions::bid` requires only a signed origin and available/reservable funds; no permission on the para's manager status is required to bid for a `ParaId` as long as it is registered, and crowdloan flows let third parties fund such bids. The attacker needs only to know the para's `period_begin`/`TemporarySlotLeasePeriodLength` (public storage) and to win (or overbid) an auction slot for the matching future period range before that boundary is reached — a cost (deposit reservation) but not requiring privilege. Repeatable each time the para becomes "pending" again.

### Recommendation
- In `allocate_temporary_slot_leases`, do not propagate a single para's `configure_slot_lease` failure with `?` out of the whole function; instead, catch the error per-iteration (e.g. via `let _ = TemporarySlots::<T>::try_mutate(...)` and log a warning), so failures for one para do not prevent processing of the rest of `slots_to_be_upgraded`, and ensure `ActiveTemporarySlotCount` is still updated based on the leases actually created.
- Consider re-checking `T::Leaser::already_leased` for the full future window (not just current+2 periods) before accepting `Auctions::bid`/`Crowdloan` contributions that target a para with an active `AssignedSlots::TemporarySlots` entry, or reject auction bids for paras holding an `AssignedSlots` entry entirely.

### Proof of Concept
Integration test plan (in `polkadot/runtime/common/src/assigned_slots/mod.rs` tests or `integration_tests.rs`, mirroring the existing `assign_temp_slot_succeeds_for_single_parathread` and `handle_bid_checks_existing_lease_periods` tests):
1. Register two parathreads, `para_a` (the target) and `para_b` (an innocent bystander).
2. Call `AssignedSlots::assign_temp_parachain_slot(Root, para_a, SlotLeasePeriodStart::Next)` and `assign_temp_parachain_slot(Root, para_b, SlotLeasePeriodStart::Next)` so both get `TemporarySlots` entries with `last_lease: None`.
3. Before the next lease-period boundary, start an `Auctions::new_auction` and have a signed non-privileged account `Auctions::bid` (or fund via `Crowdloan::create`/`contribute`) exactly for `para_a`'s scheduled `period_begin`..`period_begin+period_count-1` range, and let the auction conclude so `slots::Leases` for `para_a` is populated for that range.
4. Advance to the lease-period boundary triggering `on_initialize` → `manage_lease_period_start` → `allocate_temporary_slot_leases`.
5. Assert: `TemporarySlots::<Test>::get(para_a).last_lease` is still `None` (unchanged, conflict), and — critically — `TemporarySlots::<Test>::get(para_b).last_lease` is also still `None` even though `para_b` had no conflict, demonstrating the batch abort. Also assert `ActiveTemporarySlotCount::<Test>::get()` was not updated for this period (stays at its pre-boundary value), diverging from the real number of active leases.

### Citations

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

**File:** polkadot/runtime/common/src/assigned_slots/mod.rs (L519-566)
```rust
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
```

**File:** polkadot/runtime/common/src/assigned_slots/mod.rs (L577-584)
```rust
	fn configure_slot_lease(
		para: ParaId,
		manager: T::AccountId,
		lease_period: LeasePeriodOf<T>,
		lease_duration: LeasePeriodOf<T>,
	) -> Result<(), LeaseError> {
		T::Leaser::lease_out(para, &manager, BalanceOf::<T>::zero(), lease_period, lease_duration)
	}
```

**File:** polkadot/runtime/common/src/auctions/mod.rs (L282-293)
```rust
		pub fn bid(
			origin: OriginFor<T>,
			#[pallet::compact] para: ParaId,
			#[pallet::compact] auction_index: AuctionIndex,
			#[pallet::compact] first_slot: LeasePeriodOf<T>,
			#[pallet::compact] last_slot: LeasePeriodOf<T>,
			#[pallet::compact] amount: BalanceOf<T>,
		) -> DispatchResult {
			let who = ensure_signed(origin)?;
			Self::handle_bid(who, para, auction_index, first_slot, last_slot, amount)?;
			Ok(())
		}
```

**File:** polkadot/runtime/common/src/auctions/mod.rs (L447-451)
```rust
		// We also make sure that the bid is not for any existing leases the para already has.
		ensure!(
			!T::Leaser::already_leased(para, first_slot, last_slot),
			Error::<T>::AlreadyLeasedOut
		);
```
