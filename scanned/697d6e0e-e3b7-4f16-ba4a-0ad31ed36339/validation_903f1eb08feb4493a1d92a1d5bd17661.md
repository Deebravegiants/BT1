### Title
`allocate_temporary_slot_leases` aborts entire batch on first `configure_slot_lease` failure, letting an unprivileged auction bidder starve lower-priority temporary-slot paras indefinitely - (File: polkadot/runtime/common/src/assigned_slots/mod.rs)

### Summary
`allocate_temporary_slot_leases` iterates the fairness-sorted `pending_temp_slots` list and calls `configure_slot_lease` for each candidate inside a `try_mutate(...)?` whose `?` propagates out of the *whole function*, not just that iteration. An unprivileged account can force `configure_slot_lease` (i.e. `Leaser::lease_out`) to fail for any targeted victim para by placing a cheap winning `Auctions::bid` on that exact para/lease-period range, which aborts allocation for every subsequent (lower-priority) candidate that lease period while the entries already processed before the victim (which can include the attacker's own para) keep their committed lease. Because the victim's `TemporarySlots` entry is never mutated on failure, it stays permanently at the front of the fairness sort, so the attacker can repeat this every lease period to indefinitely freeze rotation past the victim, subverting the documented "fair, best-effort" allocation order.

### Finding Description
`allocate_temporary_slot_leases` builds and sorts `pending_temp_slots` by `(lease_count asc, last_lease asc, para_id asc)` and then does: [1](#0-0) 

For each candidate it calls `TemporarySlots::<T>::try_mutate::<_, _, Error<T>, _>(id, |s| { ... Self::configure_slot_lease(...).map_err(|_| Error::<T>::CannotUpgrade)?; ... })?;`. The trailing `?` after `try_mutate` means that as soon as one iteration's closure returns `Err`, the enclosing `for` loop is exited and `allocate_temporary_slot_leases` itself returns `Err` immediately — the remaining candidates in `slots_to_be_upgraded` are never attempted, and the final `ActiveTemporarySlotCount::<T>::set(...)` line is skipped entirely.

`configure_slot_lease` merely forwards to `T::Leaser::lease_out`: [2](#0-1) 

The concrete `Leaser` implementation (Slots pallet) fails with `LeaseError::AlreadyLeased` if the target `para`/period already has an entry in `Leases::<T>`: [3](#0-2) 

An unprivileged, signed account can create exactly such a conflicting `Leases` entry for *any registered para* — not just paras it manages — via the fully public `Auctions::bid` extrinsic: [4](#0-3) 
`handle_bid` only checks that the para is registered and that the bid doesn't already overlap an existing lease — there is no manager/ownership restriction on whose para a bidder targets: [5](#0-4) 

When the targeted auction round ends, `manage_auction_end` calls `Leaser::lease_out` for the winning bidder/para/period, populating `Leases::<T>` for the victim's `ParaId` at the exact `lease_period_index` that `allocate_temporary_slot_leases` will later try to use for that victim's temp-slot turn. Since the victim's temp slot is not yet leased (it is "pending"), an attacker can win that period range cheaply (often for the existentialdeposit-level amount, since nobody else is bidding on a para that is administratively slotted via `assigned_slots` rather than through the auction market).

Exploit flow:
1. Multiple `TemporarySlots` entries exist (precondition satisfied via `assign_temp_parachain_slot`, called by governance for legitimate temp-slot paras).
2. An open auction exists (started by `InitiateOrigin`/governance, a normal recurring on-chain event unrelated to attacker privilege).
3. Attacker (a plain signed account) calls `Auctions::bid` targeting the victim para's `ParaId` for the lease-period range that matches the victim's upcoming `period_begin`/`period_count`, winning cheaply since no one else is bidding for that para.
4. At auction end, `Leases::<T>` gets an entry for the victim `ParaId` at that period, controlled by the attacker's deposit.
5. On the next `on_initialize` → `manage_lease_period_start` → `allocate_temporary_slot_leases`, the victim's `configure_slot_lease` call hits `LeaseError::AlreadyLeased`, so the `try_mutate` closure returns `Err(Error::CannotUpgrade)`, and the `?` aborts the whole function.
6. Any candidate that sorted before the victim (including the attacker's own temp-slot para, if it has an equal/lower `lease_count`) already had its `try_mutate` committed and its real lease created via `Leaser::lease_out` before the abort — that state is not rolled back.
7. Any candidate sorted after the victim never gets attempted this period at all.
8. Because the victim's `TemporarySlots` entry is untouched (try_mutate failure leaves storage as-is), the victim keeps the exact same low `lease_count`/`last_lease`, so it remains first (or near-first) in the priority sort in every subsequent lease period, letting the attacker repeat the cheap bid every period to keep the victim (and everyone sorted after it) permanently blocked, while paras sorted before the victim — potentially including the attacker's own para — continue to be granted turns normally.

No existing check stops this: `configure_slot_lease` failures are explicitly treated as recoverable/"try next period" in `assign_temp_parachain_slot`'s inline call (see the `Err(err) => { log::warn!(...) }` branch), but the same tolerance is not applied inside `allocate_temporary_slot_leases`'s loop — there the `?` breaks the entire batch instead of just skipping that one slot.

### Impact Explanation
This breaks the documented fairness invariant of `allocate_temporary_slot_leases` ("ranked by total number of leases (lower first), and then when they last had a turn"). A single unprivileged account, at the cost of a small/minimal auction deposit repeated periodically, can indefinitely freeze fair rotation for any targeted temporary-slot para (and every para ranked after it in the sort), while paras ranked ahead of the target (potentially the attacker's own para) continue to receive lease turns normally. This is unauthorized monopolization/denial of the shared temporary parachain slot resource, contrary to the pallet's fairness guarantee.

### Likelihood Explanation
Feasible with only:
- an unprivileged signed account with a small reservable balance,
- an active auction (a normal, recurring on-chain event started by governance — the attacker doesn't need to start it, only bid in it),
- knowledge of the victim's temp slot `period_begin`/`period_count`, which is public on-chain state (`TemporarySlots` storage).

The attack is cheap (single bid per lease period targeting an unclaimed range) and repeatable indefinitely, since the victim's priority-sort state never advances while blocked.

### Recommendation
Change the loop in `allocate_temporary_slot_leases` so a `configure_slot_lease` failure for one candidate does not abort processing of the remaining candidates: catch the error per-iteration (e.g., `if let Err(e) = ... { log::warn!(...); continue; }`) instead of propagating it via `?` out of the enclosing function, consistent with how `assign_temp_parachain_slot` already treats such failures as best-effort/retry-next-period rather than fatal.

### Proof of Concept
Integration test (in `polkadot/runtime/common/src/assigned_slots/mod.rs` tests, or `integration_tests.rs` using the Auctions+Slots+AssignedSlots pallets):
1. Register and `assign_temp_parachain_slot` for 3 paras `A` (attacker-favored, lower lease_count/para_id), `V` (victim), `C` (third pending para sorted after `V`), all with `last_lease = None`/`lease_count = 0`, eligible in the same lease period.
2. Start an auction via root/`InitiateOrigin` covering the lease-period range equal to the temp-slot `period_begin..period_begin+period_count` for para `V`.
3. Have an attacker signed account (not `V`'s manager) call `Auctions::bid` for para `V` on that exact range with a minimal amount, and let the auction conclude so `Leases::<T>` now has an entry for `V` at that range.
4. Run to the next lease-period boundary triggering `manage_lease_period_start` → `allocate_temporary_slot_leases`.
5. Assert: `TemporarySlots::<Test>::get(A)` shows `lease_count == 1` (or as expected if `A` sorted before `V`) and `Slots::already_leased(A, ...) == true` (attacker's para got its turn), while `TemporarySlots::<Test>::get(V)` still has `lease_count == 0`/`last_lease == None`, and `TemporarySlots::<Test>::get(C)` also still has `lease_count == 0` (never attempted, despite being unaffected by any conflict) — proving `C`'s legitimate turn was denied purely because of the abort triggered by `V`'s conflict.
6. Repeat steps 2–4 for the next lease period targeting `V` again; assert `V` remains starved indefinitely (`lease_count` stays `0` across N periods) while `A`/other higher-priority paras continue to rotate normally.

### Citations

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

**File:** polkadot/runtime/common/src/assigned_slots/mod.rs (L576-584)
```rust
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

**File:** polkadot/runtime/common/src/slots/mod.rs (L375-395)
```rust
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
```

**File:** polkadot/runtime/common/src/auctions/mod.rs (L280-293)
```rust
		#[pallet::call_index(1)]
		#[pallet::weight(T::WeightInfo::bid())]
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

**File:** polkadot/runtime/common/src/auctions/mod.rs (L428-451)
```rust
	) -> DispatchResult {
		// Ensure para is registered before placing a bid on it.
		ensure!(T::Registrar::is_registered(para), Error::<T>::ParaNotRegistered);
		// Bidding on latest auction.
		ensure!(auction_index == AuctionCounter::<T>::get(), Error::<T>::NotCurrentAuction);
		// Assume it's actually an auction (this should never fail because of above).
		let (first_lease_period, _) = AuctionInfo::<T>::get().ok_or(Error::<T>::NotAuction)?;

		// Get the auction status and the current sample block. For the starting period, the sample
		// block is zero.
		let auction_status = Self::auction_status(frame_system::Pallet::<T>::block_number());
		// The offset into the ending samples of the auction.
		let offset = match auction_status {
			AuctionStatus::NotStarted => return Err(Error::<T>::AuctionEnded.into()),
			AuctionStatus::StartingPeriod => Zero::zero(),
			AuctionStatus::EndingPeriod(o, _) => o,
			AuctionStatus::VrfDelay(_) => return Err(Error::<T>::AuctionEnded.into()),
		};

		// We also make sure that the bid is not for any existing leases the para already has.
		ensure!(
			!T::Leaser::already_leased(para, first_slot, last_slot),
			Error::<T>::AlreadyLeasedOut
		);
```
