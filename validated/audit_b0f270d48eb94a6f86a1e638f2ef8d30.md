### Title
Verifier signature replay across crowdloan re-creation for the same `ParaId` due to missing fund-index binding - (File: polkadot/runtime/common/src/crowdloan/mod.rs)

### Summary
The verifier-signature payload checked in `Pallet::do_contribute` is `(index, &who, old_balance, value)`, where `index` is the `ParaId` and `old_balance` is read from the *current* fund's child-trie contribution storage. Because the payload does not include the fund's unique `fund_index`, and because `old_balance` resets to `0` whenever a fund is fully refunded/dissolved and a new fund is created for the same `ParaId`, a previously-used, still-decodable verifier signature can be replayed verbatim against the new fund.

### Finding Description
In `contribute`/`contribute_all` the signature check is: [1](#0-0) 

- `old_balance` comes from `Self::contribution_get(fund.fund_index, &who)`, which is namespaced by the *current* `fund.fund_index` child trie key [2](#0-1) .
- The signed `payload` tuple is `(index, &who, old_balance, value)` — it uses the `ParaId` (`index`), not `fund.fund_index`, and never binds to the fund's lifecycle/incarnation at all.
- `create` only guards against an *already active* fund for the same `ParaId` (`!Funds::<T>::contains_key(index)`), and does not prevent a `ParaId` from being reused by future crowdloans once a prior one is `dissolve`d [3](#0-2) .
- `dissolve` requires `fund.raised.is_zero()`, i.e., all contributions must already have been refunded via `refund`, which calls `contribution_kill`, resetting the contributor's stored balance to the default `(0, [])` [4](#0-3) [5](#0-4) .
- A brand-new fund created afterward for the same `ParaId` gets a fresh `fund_index` from `NextFundIndex`, so `contribution_get(new_fund_index, who)` again returns `(0, [])` — identical `old_balance` to the very first contribution of the previous fund incarnation.

Exploit flow: verifier signs payload `(P, A, 0, V)` authorizing account `A`'s first contribution of `V` to fund created for `ParaId P` (fund_index N). `A` submits `contribute(P, V, Some(sig))`, which succeeds and is recorded. Later that fund is fully refunded and `dissolve`d, and a new crowdloan for the same `ParaId P` is created (fund_index N+1) — a normal, permitted user flow since nothing prevents `ParaId` reuse. If `A` (or anyone holding the old signature) now calls `contribute(P, V, Some(sig))` again, `old_balance` for the new fund is again `0`, so the encoded payload `(P, A, 0, V)` is byte-identical to the original, and `signature.verify(...)` at line 787-789 passes without any new verifier authorization. None of the existing checks (cap, min contribution, lease-period, auction status) are designed to detect or prevent this — they only check *contribution accounting*, not signature freshness/uniqueness. There is no nonce, fund-index, or block-number component in the signed payload to prevent this replay.

### Impact Explanation
This is a KYC/authorization bypass: a fund's `verifier` mechanism is explicitly documented as gatekeeping contributions ("If exists, contributions must be signed by verifier") [6](#0-5) , but a stale, previously-used signature can be reused to authorize a contribution to an entirely different fund incarnation without the verifier's fresh consent. This allows an unauthorized/no-longer-desired contributor to bypass the intended one-time authorization gate on a new crowdloan round for the same parachain, undermining the verifier's control (e.g. re-admitting a contributor whose KYC status has since changed, or replaying leaked/expired authorization tokens). It does not directly create an accounting mismatch (funds transferred still match `value`, and `fund.raised`/child trie updates are internally consistent), but it does violate the stated invariant that "a verifier signature authorizes exactly one contribution event."

### Likelihood Explanation
Feasible and fully attacker-reachable through normal, unprivileged extrinsics (`create`, `contribute`, `refund`, `dissolve`, `create` again) — no special privilege or governance action is required beyond what any parachain manager/contributor already legitimately performs. It requires: (1) a fund with a `verifier` to have completed a contribution and later be fully refunded and dissolved, (2) a new fund created later reusing the same `ParaId` with the same (or overlapping) verifier key, and (3) the contributor retaining the old signature bytes (trivial, since signatures are public in past block data/events extrinsics). This is a realistic scenario for parachains that run repeated crowdloan campaigns across successive lease auctions.

### Recommendation
Bind the signed payload to the specific fund incarnation, not just the `ParaId`. Include `fund.fund_index` (and/or a monotonically increasing nonce/expiry) in the signed payload, e.g. `(index, fund.fund_index, &who, old_balance, value)`, so that a signature issued for one fund's contribution can never verify against a different fund_index even if the ParaId and old_balance happen to coincide.

### Proof of Concept
Rust unit test plan (extending `polkadot/runtime/common/src/crowdloan/mod.rs` tests using the existing `crypto` ed25519 helpers):
1. Create fund #1 for `ParaId` `P` with `verifier = pubkey`.
2. Sign payload `(P, A, 0, V)` with the verifier key -> `sig`.
3. Call `Crowdloan::contribute(A, P, V, Some(sig))` — assert `Ok(())`, contribution recorded.
4. Advance blocks past `end`, call `refund(P)` (fully refunds `A`), then `dissolve(P)` — assert `Ok(())`, `Funds::<Test>::get(P)` is `None`.
5. Call `create` again for the same `ParaId` `P` with the same `verifier`, producing fund #2 (`fund_index` incremented).
6. Call `Crowdloan::contribute(A, P, V, Some(sig))` reusing the *same* `sig` from step 2 (no new signing).
7. **Current (buggy) behavior**: assert this succeeds (`Ok(())`), demonstrating replay.
8. **Expected fix behavior**: assert `Err(Error::<Test>::InvalidSignature)` once `fund_index` is added to the signed payload.

### Citations

**File:** polkadot/runtime/common/src/crowdloan/mod.rs (L145-146)
```rust
	/// An optional verifier. If exists, contributions must be signed by verifier.
	pub verifier: Option<MultiSigner>,
```

**File:** polkadot/runtime/common/src/crowdloan/mod.rs (L405-406)
```rust
			// There should not be an existing fund.
			ensure!(!Funds::<T>::contains_key(index), Error::<T>::FundNotEnded);
```

**File:** polkadot/runtime/common/src/crowdloan/mod.rs (L525-536)
```rust
			for (who, (balance, _)) in contributions {
				if refund_count >= T::RemoveKeysLimit::get() {
					// Not everyone was able to be refunded this time around.
					all_refunded = false;
					break;
				}
				CurrencyOf::<T>::transfer(&fund_account, &who, balance, AllowDeath)?;
				CurrencyOf::<T>::reactivate(balance);
				Self::contribution_kill(fund.fund_index, &who);
				fund.raised = fund.raised.saturating_sub(balance);
				refund_count += 1;
			}
```

**File:** polkadot/runtime/common/src/crowdloan/mod.rs (L555-580)
```rust
		pub fn dissolve(origin: OriginFor<T>, #[pallet::compact] index: ParaId) -> DispatchResult {
			let who = ensure_signed(origin)?;

			let fund = Funds::<T>::get(index).ok_or(Error::<T>::InvalidParaId)?;
			let pot = Self::fund_account_id(fund.fund_index);
			let now = frame_system::Pallet::<T>::block_number();

			// Only allow dissolution when the raised funds goes to zero,
			// and the caller is the fund creator or we are past the end date.
			let permitted = who == fund.depositor || now >= fund.end;
			let can_dissolve = permitted && fund.raised.is_zero();
			ensure!(can_dissolve, Error::<T>::NotReadyToDissolve);

			// Assuming state is not corrupted, the child trie should already be cleaned up
			// and all funds in the crowdloan account have been returned. If not, governance
			// can take care of that.
			debug_assert!(Self::contribution_iterator(fund.fund_index).count().is_zero());

			// Crowdloan over, burn all funds.
			let _imba = CurrencyOf::<T>::make_free_balance_be(&pot, Zero::zero());
			let _ = frame_system::Pallet::<T>::dec_providers(&pot).defensive();

			CurrencyOf::<T>::unreserve(&fund.depositor, fund.deposit);
			Funds::<T>::remove(index);
			Self::deposit_event(Event::<T>::Dissolved { para_id: index });
			Ok(())
```

**File:** polkadot/runtime/common/src/crowdloan/mod.rs (L697-701)
```rust
	pub fn contribution_get(index: FundIndex, who: &T::AccountId) -> (BalanceOf<T>, Vec<u8>) {
		who.using_encoded(|b| {
			child::get_or_default::<(BalanceOf<T>, Vec<u8>)>(&Self::id_from_index(index), b)
		})
	}
```

**File:** polkadot/runtime/common/src/crowdloan/mod.rs (L782-791)
```rust
		let (old_balance, memo) = Self::contribution_get(fund.fund_index, &who);

		if let Some(ref verifier) = fund.verifier {
			let signature = signature.ok_or(Error::<T>::InvalidSignature)?;
			let payload = (index, &who, old_balance, value);
			let valid = payload.using_encoded(|encoded| {
				signature.verify(encoded, &verifier.clone().into_account())
			});
			ensure!(valid, Error::<T>::InvalidSignature);
		}
```
