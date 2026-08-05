### Title
`ensure_updated` griefs fee via `Pays::No` while silently orphaning victims' `PreimageFor` storage on `Consideration::new` failure - (File: substrate/frame/preimage/src/lib.rs)

### Summary
`Pallet::do_ensure_updated` consumes (`take`s) a legacy `StatusFor` entry and, if `T::Consideration::new` fails for the associated depositor, returns `true` (counted as "successfully migrated") without writing any replacement `RequestStatusFor` entry, leaving the corresponding `PreimageFor` data permanently untracked/unremovable. Because any legacy `StatusFor` entry - success or failure - counts as `true` in `ensure_updated`'s ratio, an unprivileged caller can pass a batch of arbitrary, non-owned legacy hashes to obtain `Pays::No` while causing this orphaning for any entries whose depositor's `Consideration::new` call fails.

### Finding Description
`ensure_updated` is permissionlessly callable by any signed account and accepts an arbitrary `Vec<T::Hash>` with no ownership check: [1](#0-0) 

For each hash, `do_ensure_updated` does:
```
let r = match StatusFor::<T>::take(h) { Some(r) => r, None => return false };
...
T::Currency::unreserve(&who, amount);
let Ok(ticket) = T::Consideration::new(&who, ...).defensive_proof(...) else { return true; };
RequestStatusFor::<T>::insert(h, n); // only reached on success
``` [2](#0-1) 

The critical defect: `StatusFor::<T>::take(h)` unconditionally removes the legacy entry before the new `Consideration::new` call is attempted. If that call fails (`else { return true; }` at lines 282 and 298), the function still returns `true` - counting toward `updated` in the ratio computed by the caller - but `RequestStatusFor::<T>::insert` is never reached, so no new record backs the preimage. The `PreimageFor` map (keyed by `(hash, len)`) is untouched by this function entirely, so the raw preimage bytes remain in storage with no `RequestStatusFor` entry pointing to them. Any subsequent lookup (`RequestStatusFor::<T>::get(hash)`) returns `None`, so functions like `do_unnote_preimage`/`do_unrequest_preimage` will fail with `NotNoted`/`NotRequested`, meaning the orphaned `PreimageFor` bytes become permanently unreachable/un-removable dead storage, and the depositor's original stake accounting for that storage is gone (the old deposit was unreserved, but no consideration/hold was created to replace it).

Because a hash's `do_ensure_updated` result is `true` whenever it exists in the legacy `StatusFor` map, *regardless of whether the migration to `RequestStatusFor` actually succeeded*, an attacker only needs to submit a batch consisting of legacy pending hashes to obtain a high `ratio` (`updated / hashes.len()`) sufficient to cross `Perbill::from_percent(90)` and receive `Pays::No`: [3](#0-2) 
No signature, origin, or ownership check prevents this: `ensure_signed(origin)?` only checks the caller is a real account, and the hash list is fully attacker-chosen with no relation to the caller's own deposits.

The only mitigating factor is that `Consideration::new` failure after a successful `unreserve` should be "unexpected" per the code comment/`defensive_proof`, implying the pallet authors assumed unreserve-then-hold is normally infallible. However, this assumption can break in practice (e.g., the depositor's freed balance is still below required minimums due to freezes/locks such as vesting, or existential-deposit interactions differ between `Currency::reserve` and the newer `Consideration`/hold-based mechanism), making the "unexpected" path attacker-observable and exploitable given the right victim account state - exactly the precondition scenario described (borderline-funded depositor).

### Impact Explanation
- An unprivileged attacker obtains a completely fee-free (`Pays::No`) transaction by supplying a batch of legacy `StatusFor` hashes they do not own.
- Any legacy entry among those hashes whose depositor's `Consideration::new` call fails is silently converted from a properly-tracked (`StatusFor`/`RequestStatusFor`) preimage into an untracked, permanently orphaned `PreimageFor` entry - the raw bytes remain on-chain consuming storage but can never be cleared through the pallet's public API since all removal paths require a `RequestStatusFor` entry to exist.
- This is a storage/accounting-integrity defect (unbacked storage) combined with fee griefing, matching the scoped impact.

### Likelihood Explanation
- Requires only a signed account - no special privileges, proxy, or multisig needed.
- Requires the attacker to identify at least one legacy `StatusFor::Unrequested`/`Requested` entry whose depositor's current free/unfrozen balance would be insufficient for the new `Consideration::new` hold immediately after `unreserve` (a state that is publicly observable on-chain by inspecting balances/locks vs. legacy deposit and new footprint cost).
- Fully repeatable: any batch composed of legacy hashes will satisfy the ratio threshold since none of the code paths for existing legacy entries return `false` (only truly-absent hashes do), so the "90%" fee-free bar is trivial to clear.
- The likelihood of finding a qualifying victim depends on external balance-timing (vesting/lock interactions), which is realistic but not guaranteed to exist for any given account at any given time.

### Recommendation
- Do not call `StatusFor::<T>::take(h)` before confirming that `T::Consideration::new` will succeed; instead, peek the entry, attempt the consideration creation first, and only remove/replace the legacy entry after success. Alternatively, on failure, re-insert the original `StatusFor` entry (or a safe fallback `RequestStatusFor` entry with `ticket=None`) instead of leaving nothing.
- `do_ensure_updated` must return `false` (or propagate an explicit error) when the migration did not actually complete, so `ensure_updated`'s ratio only counts genuinely successful migrations.
- Consider requiring the unreserved deposit amount to be re-reserved (rollback) if the new consideration cannot be created, keeping the preimage backed under the old accounting scheme rather than orphaning it.

### Proof of Concept
Rust integration test in `substrate/frame/preimage/src/tests.rs`:
1. Insert a legacy `StatusFor::Unrequested { deposit: (victim, amount), len }` entry for `hash_a` (via storage setup mirroring pre-migration state), and ensure `victim`'s current free balance (after simulated `unreserve`) is insufficient to satisfy `MockConsideration::new` (configure the mock `Consideration` to fail when caller balance < some threshold).
2. Insert a normal, funded legacy entry for `hash_b` with a depositor who can afford the new consideration.
3. Call `Preimage::ensure_updated(signed(attacker), vec![hash_a, hash_b])` from an account with no relation to either hash.
4. Assert:
   - The dispatch result is `Pays::No`.
   - `RequestStatusFor::<Test>::get(hash_a).is_none()` (orphaned).
   - `PreimageFor::<Test>::get((hash_a, len)).is_some()` (bytes still present but now unreachable).
   - Any subsequent call to `Preimage::unnote_preimage(hash_a)` returns `Error::<Test>::NotNoted`, proving the entry can never be cleaned up.
   - `RequestStatusFor::<Test>::get(hash_b).is_some()` (control case migrated correctly).

### Citations

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
