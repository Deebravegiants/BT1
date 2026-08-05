Audit Report

## Title
`ensure_updated` griefs fee via `Pays::No` while silently orphaning victims' `PreimageFor` storage on `Consideration::new` failure - (File: substrate/frame/preimage/src/lib.rs)

## Summary
`Pallet::do_ensure_updated` calls `StatusFor::<T>::take(h)` to remove the legacy migration entry before attempting `T::Consideration::new`, and on failure of that call returns `true` without ever writing a `RequestStatusFor` entry, so the associated `PreimageFor` bytes become permanently orphaned while the migration is still counted as a success in `ensure_updated`'s ratio. This lets an unprivileged caller submit a batch of arbitrary legacy hashes (not owned by them) to reach the 90% threshold and obtain `Pays::No`, while any qualifying entry whose depositor's `Consideration::new` call fails after `unreserve` becomes unrecoverable dead storage.

## Finding Description
`ensure_updated` is callable by any signed account with an arbitrary `Vec<T::Hash>` and no ownership check on the hashes: [1](#0-0) 

`do_ensure_updated` unconditionally `take`s the legacy `StatusFor` entry, then attempts `T::Currency::unreserve` followed by `T::Consideration::new`; if the latter fails, the function returns `true` without ever calling `RequestStatusFor::<T>::insert`: [2](#0-1) 

This confirms the reported code behavior exactly: the legacy entry is destructively removed before the new consideration is confirmed, and the `else { return true; }` branches at both the `Unrequested` and `Requested` match arms leave no replacement record, while still contributing to the "updated" count used to compute the `Pays::No` ratio.

However, the exploitability of this defect hinges entirely on `T::Consideration::new` actually failing right after a successful `unreserve` for the same depositor and amount. The code comment and `defensive_proof("Unexpected inability to take deposit after unreserved")` explicitly frame this as an "unexpected" invariant violation — i.e., the pallet authors assumed that funds just freed via `unreserve` should always be sufficient to satisfy the new hold/consideration. I was unable to fully verify, within the available tooling, the concrete `Consideration` implementation(s) (e.g. `HoldConsideration`) wired into production runtimes to determine whether there is a realistic, externally-triggerable balance/freeze state (vesting locks, other holds, ED interactions) under which `unreserve` succeeds but the subsequent `Consideration::new` reliably fails. This is a load-bearing precondition for the claim, and the report itself acknowledges it as speculative ("this assumption can break in practice... given the right victim account state").

## Impact Explanation
If the precondition materializes, the concrete impact is: (a) the calling account obtains a fee waiver (`Pays::No`) it did not "earn" through actually completing migrations, and (b) the victim's preimage bytes in `PreimageFor` become unbacked by any `RequestStatusFor` entry, making them permanently unreachable via `do_unnote_preimage`/`do_unrequest_preimage` (both require a `RequestStatusFor` lookup to succeed). This is a real storage-integrity defect in the code as written. However, the primary "griefing" impact (fee waiver) is a minor economic effect — it saves the attacker a transaction fee, it does not extract value from any other party. The storage-orphaning impact is more significant (unbacked, unremovable storage) but is entirely contingent on the unverified precondition that `Consideration::new` can fail after a successful `unreserve` for the same account/amount under realistic conditions, which the reporter themselves characterizes as an edge case dependent on specific, not-fully-demonstrated balance/freeze states.

## Likelihood Explanation
Reaching the 90% `Pays::No` threshold using only "existing legacy hash" entries is trivially true regardless of the failure branch, since any hash present in `StatusFor` (success or failure) counts as `true`. This part of the claim is well-supported by the code. But the actually damaging outcome (orphaned storage) requires locating or engineering a victim account whose `Consideration::new` call fails immediately after a successful `unreserve` of the same amount — a scenario the report describes as depending on external balance-timing/lock interactions that are "realistic but not guaranteed." No concrete, reproducible demonstration (fork test, PoC against a real `Consideration`/`HoldConsideration` implementation, or existing test in `substrate/frame/preimage/src/tests.rs`) is provided showing this failure path is actually reachable with realistic account states; the PoC section only describes a hypothetical mock-based test that assumes a `MockConsideration` configured to fail under attacker-chosen conditions, rather than demonstrating the failure occurs under the real `Consideration` implementations used in production runtimes.

## Recommendation
Restructure `do_ensure_updated` to only remove/replace the legacy `StatusFor` entry after confirming `T::Consideration::new` succeeds (e.g., peek the entry first, attempt consideration creation, and only then take/replace it), or on failure, re-insert the original `StatusFor` entry or a fallback `RequestStatusFor` entry so no preimage becomes orphaned. Additionally, `do_ensure_updated` should return `false` when migration did not actually complete, so the `ensure_updated` ratio only counts genuine successes.

## Proof of Concept
Not independently reproducible with available tooling: the report's PoC section describes hypothetical mock-based test steps (configuring a mock `Consideration` to fail based on attacker-chosen balance thresholds) rather than demonstrating the failure path against a real `Consideration`/hold implementation with realistic account states. No existing test in `substrate/frame/preimage/src/tests.rs` was located that exercises this failure branch, and the practical trigger condition (successful `unreserve` immediately followed by failing `Consideration::new` for the same account/amount) was not verified against production `Consideration` implementations within this investigation.

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
