### Title
Non-atomic legacy `StatusFor` → `RequestStatusFor` migration can permanently orphan `PreimageFor` bytes with lost deposit accounting - (File: substrate/frame/preimage/src/lib.rs)

### Summary
`Pallet::do_ensure_updated` first calls `StatusFor::<T>::take(h)` (irreversibly consuming the legacy deposit record) and `T::Currency::unreserve(&who, amount)` before attempting `T::Consideration::new(&who, ...)`. If the new consideration/hold fails, the function only logs via `.defensive_proof(...)` and returns `true` without ever calling `RequestStatusFor::<T>::insert`, leaving the already-unreserved (now fully spendable) funds with no new hold, and the `PreimageFor` bytes with no corresponding accounting entry at all.

### Finding Description
`do_ensure_updated` at `substrate/frame/preimage/src/lib.rs` performs the migration in this order: [1](#0-0) 

1. `StatusFor::<T>::take(h)` removes the legacy entry unconditionally — there is no going back once this line executes.
2. `T::Currency::unreserve(&who, amount)` immediately returns the old reserved deposit to the account's *free* balance via the legacy `ReservableCurrency` accounting.
3. `T::Consideration::new(&who, Footprint::from_parts(1, len))` (e.g. `HoldConsideration::new` → `F::hold(...)`, seen at [2](#0-1) ) attempts to place a *new* hold for the same nominal amount, but hold-placement is checked against the account's current `frozen` balance (driven by `pallet_vesting`'s `VESTING_ID` lock, staking locks, or other freezes on the same `pallet_balances` instance), not just against the just-restored free balance.
4. If `hold` fails, `.defensive_proof(...)` only logs (in production it does not panic) and the `else { return true; }` branch is taken — `RequestStatusFor::<T>::insert` is never reached.

Because the legacy amount was originally reserved when the account's `frozen` balance may have been lower (e.g., before an additional vesting schedule or staking bond increased the lock), the exact same nominal amount that was safely reserved before can fail to be re-held after unreserve, purely due to headroom shrinkage from a concurrent lock — with no relation to the preimage logic itself.

The result: `StatusFor` entry is gone, `RequestStatusFor` was never populated, and `PreimageFor::<T>` for `(hash, len)` still holds the (potentially up to 4 MB) preimage bytes untouched, since removal of `PreimageFor` only happens through `Self::remove` in `do_unnote_preimage`/`do_unrequest_preimage`, both of which require a `RequestStatusFor` entry to exist. Any subsequent call for the same hash hits `StatusFor::<T>::take(h) => None => return false` at the top of `do_ensure_updated`, so the hash can never be reprocessed, and every read/write path (`do_unnote_preimage`, `do_unrequest_preimage`, `len`, `have`, `fetch`, `is_requested`) treats the hash as `NotNoted`/`NotRequested`/absent, permanently orphaning the stored bytes with no possible cleanup through any dispatchable, including `ManagerOrigin`-gated calls.

### Impact Explanation
An account's deposit is fully released to spendable balance while the on-chain `PreimageFor` bytes it was paying for remain stored forever, unbacked by any consideration/hold and unreachable by any extrinsic (including privileged `unrequest_preimage`/manager calls, since they too route through `RequestStatusFor`). This is state-bloat with zero deposit backing, exactly the scoped "unbacked storage" and "permanent inability to reclaim" impact — it is not fund theft, but a storage-accounting/DoS-style bug against the chain's deposit-for-storage invariant.

### Likelihood Explanation
This requires: (1) a real leftover legacy `OldRequestStatus::Unrequested` entry for a hash the attacker owns — realistic on any chain that upgraded to the `Consideration`-based accounting but has preimages that were never subsequently touched (lazy/opportunistic migration, not a one-shot runtime-upgrade migration); and (2) the attacker's free-vs-frozen headroom on the very same `pallet_balances` instance to have shrunk since the original deposit (e.g., attacker took a new vesting schedule, extended a staking bond, or added an NFT/asset freeze) such that `unreserve` followed by `hold` for the identical nominal amount now fails. Both conditions are plausible and fully attacker-controlled (the attacker chooses when to bond/vest and when to call `note_preimage`/`unnote_preimage`/`ensure_updated`), though it depends on pre-existing unmigrated legacy state, which is not something the attacker can freshly manufacture post-migration on a chain where the lazy migration has already touched all entries.

### Recommendation
Make the migration atomic and order-safe: attempt to acquire the new `Consideration`/hold for the account *before* calling `StatusFor::<T>::take`/`unreserve`, or re-insert into `StatusFor`/roll back `unreserve` if `Consideration::new` fails, so the legacy record is only discarded once the new hold is confirmed successful. At minimum, on failure, do not drop the record silently — re-insert the (now-unbacked) status into `RequestStatusFor` (e.g. as `Unrequested` with no ticket, or re-insert the old `StatusFor` entry) so subsequent calls can retry and `PreimageFor` remains reachable for cleanup.

### Proof of Concept
Rust integration test in `substrate/frame/preimage/src/tests.rs` style:
1. Set up a mock runtime whose `Currency` is `pallet_balances` and whose `Consideration = HoldConsideration<..., Balances, PreimageHoldReason, ...>`.
2. Seed legacy state directly analogous to pre-migration chain state: insert `StatusFor::<Test>::insert(hash, OldRequestStatus::Unrequested{ deposit: (who, amount), len })` and `PreimageFor::<Test>::insert((hash, len), bytes)` (this mirrors real on-chain legacy state, not a "malicious direct storage mutation" by the attacker — it represents genuine unmigrated history).
3. Apply a lock on `who` via `Balances::set_lock(VESTING_ID, &who, big_amount, WithdrawReasons::all())` such that `free_balance(who) - amount < frozen_balance(who)` after `unreserve`.
4. Call `Preimage::note_preimage(RuntimeOrigin::signed(who), some_bytes)` or `Preimage::ensure_updated(RuntimeOrigin::signed(who), vec![hash])`, triggering `do_ensure_updated`.
5. Assert: `RequestStatusFor::<Test>::get(hash).is_none()`, `PreimageFor::<Test>::contains_key((hash, len))` is still `true`, and `Balances::free_balance(who)` reflects the fully-unreserved (spendable) amount with no new hold recorded (`Balances::balance_on_hold(&HoldReason::Preimage.into(), &who) == 0`).

### Citations

**File:** substrate/frame/preimage/src/lib.rs (L267-285)
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
```

**File:** substrate/frame/support/src/traits/tokens/fungible/mod.rs (L285-291)
```rust
	> Consideration<A, Fp> for HoldConsideration<A, F, R, D, Fp>
{
	fn new(who: &A, footprint: Fp) -> Result<Self, DispatchError> {
		let new = D::convert(footprint);
		F::hold(&R::get(), who, new)?;
		Ok(Self(new, PhantomData))
	}
```
