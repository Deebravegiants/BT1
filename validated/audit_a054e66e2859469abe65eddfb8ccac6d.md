## Verdict: Partially valid, but the exploit mechanism described in the question is inaccurate. The real bug is narrower.

### Title
`ensure_updated` extrinsic can commit a partial `StatusFor`→`RequestStatusFor` migration on `Consideration::new` failure, permanently orphaning the preimage deposit accounting - (File: substrate/frame/preimage/src/lib.rs)

### Summary
`Pallet::do_ensure_updated` takes the legacy `StatusFor` entry, unreserves the old deposit, and then attempts to open a new `Consideration` ticket; if that fails, it returns early **without** writing anything to `RequestStatusFor`, leaving the hash with no status record at all. Whether this is a real, exploitable, *permanent* bug depends entirely on which call path triggers it, because most callers propagate the error and get rolled back by FRAME's per-extrinsic storage transaction — except the `ensure_updated` extrinsic itself, which unconditionally returns `Ok(..)` and therefore commits the partial state.

### Finding Description
`do_ensure_updated` ( [1](#0-0) ) does:

1. `StatusFor::<T>::take(h)` — unconditionally removes the legacy entry.
2. For `Unrequested { deposit: (who, amount), len }`: `T::Currency::unreserve(&who, amount)`, then `T::Consideration::new(&who, footprint)`.
3. If `Consideration::new` fails, `.defensive_proof(...)` logs a defensive warning and the function `return true` **without** calling `RequestStatusFor::<T>::insert`.

At this point the hash has no entry in either `StatusFor` (removed) or `RequestStatusFor` (never inserted), while `amount` has already been returned to `who`'s free balance, and the raw bytes remain sitting in `PreimageFor` ( [2](#0-1) ) with no status record pointing at them.

Almost every internal caller of `do_ensure_updated` (`note_bytes`, `do_request_preimage`, `do_unnote_preimage`, `do_unrequest_preimage`, `len`, `fetch`) subsequently reads `RequestStatusFor::<T>::get(hash)` and, finding `None`, either takes a fresh-deposit branch (which itself calls `Consideration::new` again and, since the underlying balance condition is unchanged, will fail again and propagate a `DispatchError` all the way up through `?`) or returns `Err`/`None` in a way that surfaces as a dispatch failure. Because `#[pallet::call]` wraps every dispatchable in a transactional storage layer, an `Err` return from the top-level extrinsic rolls back *all* storage changes made during that call — including the `unreserve` and the `StatusFor::take` — so state is restored and there is no permanent loss through `note_preimage`, `unnote_preimage`, or the `QueryPreimage`/`PreimageProvider` trait paths when invoked from within another pallet's dispatchable.

The one path that does **not** propagate the failure is the `ensure_updated` extrinsic itself: [3](#0-2) 
It calls `do_ensure_updated` for each hash purely to count successes for the fee-discount ratio and always returns `Ok(pays.into())` regardless of per-hash outcome. If `Consideration::new` fails for one of the hashes, that failure is silently swallowed, the extrinsic succeeds, and the storage transaction is **committed** — permanently orphaning that entry: `StatusFor` gone, `RequestStatusFor` never populated, deposit already refunded, and the `PreimageFor` bytes now unreachable (any subsequent `fetch`/`len` on that hash returns `None`/`Unavailable` since there's no status record to read the length from).

Any signed account can call `ensure_updated` on **any** hash, not just their own, since the only origin check is `ensure_signed(origin)?` ( [4](#0-3) ).

### Impact Explanation
This is a real (though narrower than claimed) accounting break: a legacy preimage deposit can be unreserved without producing a new tracked deposit/ticket, and the underlying bytes become permanently orphaned in `PreimageFor` — inaccessible via `fetch`/`len`, un-removable (no code path reaches `PreimageFor::remove` for a hash with no status record), and a silent storage leak. It also causes a denial-of-service on any consumer (e.g. `pallet_referenda`) that depended on that preimage being fetchable, since it now appears never-noted.

However, the claimed follow-on exploit — "call `note_preimage` again to obtain a *second* deposit-free entry, double-registering the same content without paying twice" — does **not** hold: after the loss, `RequestStatusFor::get(hash)` returns `None`, so a subsequent `note_preimage` call falls into the `(None, Some(depositor))` branch of `note_bytes` ( [5](#0-4) ), which requires a **fresh, paid** `Consideration::new`. There is no free/duplicate registration; the attacker must pay again to re-register the same content.

### Likelihood Explanation
Requires: (a) a legacy `StatusFor` entry still present (plausible on any chain that hasn't fully swept its old preimages), and (b) `Consideration::new` failing right after the equivalent amount was just unreserved for the same account. The "attacker drains balance in the same tx" mechanism from the question is not feasible — `unreserve` and `Consideration::new` execute back-to-back with no possibility for another extrinsic to interleave. A far more realistic trigger is a runtime upgrade that changed the per-byte/base deposit pricing (so the new required deposit exceeds the refunded amount) combined with the depositor's free balance having decreased since the deposit was first taken for unrelated reasons — both plausible on a long-lived chain. The only path where this becomes *permanent* (not rolled back) is via the public `ensure_updated` extrinsic, callable by any signed account on any hash.

### Recommendation
Make `do_ensure_updated`'s failure path atomic with the removal: either restore/re-insert the old `StatusFor` entry (and re-reserve) if `Consideration::new` fails, or explicitly write a degraded-but-tracked `RequestStatusFor` entry that still reflects an outstanding deposit obligation (e.g., an `Unrequested` variant with a zero/failed ticket flagged for cleanup) rather than leaving no record at all. At minimum, `ensure_updated` should be changed to not silently swallow this failure mode — e.g., roll back per-hash migration failures individually, or track and emit them so operators can detect orphaned `PreimageFor` entries.

### Proof of Concept
Rust unit test in `substrate/frame/preimage/src/tests.rs` (mock runtime):
1. Insert a legacy `StatusFor::<Test>::insert(hash, OldRequestStatus::Unrequested { deposit: (who, amount), len })` and matching `PreimageFor` bytes, with `who`'s reserved balance = `amount`.
2. Configure `Consideration::new` (via the mock's Consideration impl) to fail specifically for `who`'s next call (simulate a raised deposit price so that after `unreserve` the free balance is insufficient for the new footprint deposit).
3. Call `Preimage::ensure_updated(RuntimeOrigin::signed(some_other_account), vec![hash])`.
4. Assert:
   - The call returns `Ok(..)`.
   - `who`'s reserved balance dropped by `amount` (unreserved) and was NOT re-reserved.
   - `RequestStatusFor::<Test>::get(hash)` is `None`.
   - `StatusFor::<Test>::get(hash)` is `None`.
   - `PreimageFor::<Test>::get((hash, len))` still contains the bytes (orphaned).
   - A subsequent `Preimage::note_preimage(RuntimeOrigin::signed(who), bytes)` succeeds only after `who` pays a **new** deposit (assert `Consideration::new` is invoked again and reserved balance increases), disproving the "second free entry" claim while confirming the orphaned-storage/broken-status-tracking defect.

### Citations

**File:** substrate/frame/preimage/src/lib.rs (L188-190)
```rust
	#[pallet::storage]
	pub type PreimageFor<T: Config> =
		StorageMap<_, Identity, (T::Hash, u32), BoundedVec<u8, ConstU32<MAX_SIZE>>>;
```

**File:** substrate/frame/preimage/src/lib.rs (L249-262)
```rust
		pub fn ensure_updated(
			origin: OriginFor<T>,
			hashes: Vec<T::Hash>,
		) -> DispatchResultWithPostInfo {
			ensure_signed(origin)?;
			ensure!(hashes.len() > 0, Error::<T>::TooFew);
			ensure!(hashes.len() <= MAX_HASH_UPGRADE_BULK_COUNT as usize, Error::<T>::TooMany);

			let updated = hashes.iter().map(Self::do_ensure_updated).filter(|b| *b).count() as u32;
			let ratio = Perbill::from_rational(updated, hashes.len() as u32);

			let pays: Pays = (ratio < Perbill::from_percent(90)).into();
			Ok(pays.into())
		}
```

**File:** substrate/frame/preimage/src/lib.rs (L267-312)
```rust
	fn do_ensure_updated(h: &T::Hash) -> bool {
		#[allow(deprecated)]
		let r = match StatusFor::<T>::take(h) {
			Some(r) => r,
			None => return false,
		};
		let n = match r {
			OldRequestStatus::Unrequested { deposit: (who, amount), len } => {
				// unreserve deposit
				T::Currency::unreserve(&who, amount);
				// take consideration
				let Ok(ticket) =
					T::Consideration::new(&who, Footprint::from_parts(1, len as usize))
						.defensive_proof("Unexpected inability to take deposit after unreserved")
				else {
					return true;
				};
				RequestStatus::Unrequested { ticket: (who, ticket), len }
			},
			OldRequestStatus::Requested { deposit: maybe_deposit, count, len: maybe_len } => {
				let maybe_ticket = if let Some((who, deposit)) = maybe_deposit {
					// unreserve deposit
					T::Currency::unreserve(&who, deposit);
					// take consideration
					if let Some(len) = maybe_len {
						let Ok(ticket) =
							T::Consideration::new(&who, Footprint::from_parts(1, len as usize))
								.defensive_proof(
									"Unexpected inability to take deposit after unreserved",
								)
						else {
							return true;
						};
						Some((who, ticket))
					} else {
						None
					}
				} else {
					None
				};
				RequestStatus::Requested { maybe_ticket, count, maybe_len }
			},
		};
		RequestStatusFor::<T>::insert(h, n);
		true
	}
```

**File:** substrate/frame/preimage/src/lib.rs (L358-362)
```rust
			(None, Some(depositor)) => {
				let ticket =
					T::Consideration::new(depositor, Footprint::from_parts(1, len as usize))?;
				RequestStatus::Unrequested { ticket: (depositor.clone(), ticket), len }
			},
```
