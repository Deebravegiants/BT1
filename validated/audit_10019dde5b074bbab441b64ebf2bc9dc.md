Audit Report

## Title
Verifier signature replay across crowdloan re-creation for the same `ParaId` due to missing fund-index binding - (File: polkadot/runtime/common/src/crowdloan/mod.rs)

## Summary
The verifier-signature payload checked in `Pallet::do_contribute` is `(index, &who, old_balance, value)`, where `index` is the `ParaId` and `old_balance` is read from the current fund's child-trie contribution storage via `contribution_get(fund.fund_index, &who)`. Because the payload never includes `fund.fund_index` and `old_balance` resets to `0` when a fund is fully refunded and dissolved, a previously used verifier signature can be replayed against a newly created fund for the same `ParaId` if `old_balance` and `value` coincide.

## Finding Description
`do_contribute` reads `old_balance` from the current fund incarnation's storage and checks the signature against `(index, &who, old_balance, value)`: [1](#0-0) 

`contribution_get` is namespaced by `fund.fund_index` via the child-trie key, but that `fund_index` itself is not part of the signed payload: [2](#0-1) 

`create` only guards against an *already active* fund for the same `ParaId`; it does not prevent `ParaId` reuse for a brand-new fund once the previous one is dissolved: [3](#0-2) 

`refund` fully zeroes contributor balances via `contribution_kill` before a fund can be `dissolve`d (which requires `fund.raised.is_zero()`): [4](#0-3) [5](#0-4) 

Given these mechanics: a fresh fund created afterward for the same `ParaId` gets a new `fund_index`, and `contribution_get(new_fund_index, who)` again returns `(0, [])` — identical to the very first contribution in the prior fund incarnation. Thus a signature originally authorizing `(ParaId, who, 0, value)` remains valid for the new fund's first contribution of the same `value` from the same account, with no new authorization from the verifier. None of the other checks in `do_contribute` (cap, min contribution, lease-period, auction/VRF status) are designed to detect stale/duplicate signatures — they only govern accounting and timing, not signature freshness. This matches the code exactly as reviewed in the repository.

## Impact Explanation
This breaks the verifier's intended one-time authorization guarantee documented in the code ("If exists, contributions must be signed by verifier"): a stale, previously-used signature can be replayed to authorize a contribution to a different fund incarnation of the same parachain without fresh verifier consent. This is a real authorization/gatekeeping bypass — it allows re-admission of a contributor whose authorization should no longer be valid (e.g., revoked KYC, expired allowlist token) without directly causing fund-accounting loss, since the transferred value still matches `value` and the child-trie/`fund.raised` state stays internally consistent.

## Likelihood Explanation
The full exploit path (`create` → `contribute` → `refund` → `dissolve` → `create` again → `contribute` with the reused signature) uses only ordinary, unprivileged extrinsics available to any parachain manager and contributor — no governance action or privileged origin is required beyond what legitimate crowdloan operators already perform. It requires specific preconditions to line up exactly (same `ParaId` reused, same verifier key retained, same contributor, and identical `value` as the original first contribution, since the signed payload includes `value`), which somewhat narrows applicability but does not eliminate the underlying flaw. Signatures are public in on-chain extrinsic data, so retaining/replaying the old bytes is trivial once these conditions are met.

## Recommendation
Bind the signed payload to the specific fund incarnation, not just the `ParaId`. Include `fund.fund_index` in the signed payload (e.g., `(index, fund.fund_index, &who, old_balance, value)`), or add a monotonically increasing nonce/expiry, so that a signature issued for one fund's contribution round can never verify against a different fund incarnation even if `ParaId`, `old_balance`, and `value` happen to coincide.

## Proof of Concept
1. Create fund #1 for `ParaId` `P` with `verifier = pubkey` via `Crowdloan::create`.
2. Sign payload `(P, A, 0, V)` with the verifier key → `sig`.
3. Call `Crowdloan::contribute(A, P, V, Some(sig))` — succeeds, contribution recorded (`old_balance` becomes `V`).
4. Advance blocks past `fund.end`, call `Crowdloan::refund(P)` to fully refund `A` (resets stored balance to `(0, [])` via `contribution_kill`), then call `Crowdloan::dissolve(P)` — fund #1 removed.
5. Call `Crowdloan::create` again for the same `ParaId` `P` with the same `verifier`, creating fund #2 with a new `fund_index`.
6. Call `Crowdloan::contribute(A, P, V, Some(sig))` reusing the same `sig` from step 2 without any new signing.
7. Current behavior: this succeeds (`Ok(())`), demonstrating the signature replay, since `contribution_get(fund_index_2, A)` again returns `(0, [])`, making the encoded payload byte-identical to the original.
8. Expected fixed behavior: once `fund_index` (or a nonce) is added to the signed payload, this call should fail with `Error::<T>::InvalidSignature`.

### Citations

**File:** polkadot/runtime/common/src/crowdloan/mod.rs (L405-413)
```rust
			// There should not be an existing fund.
			ensure!(!Funds::<T>::contains_key(index), Error::<T>::FundNotEnded);

			let manager = T::Registrar::manager_of(index).ok_or(Error::<T>::InvalidParaId)?;
			ensure!(depositor == manager, Error::<T>::InvalidOrigin);
			ensure!(T::Registrar::is_registered(index), Error::<T>::InvalidParaId);

			let fund_index = NextFundIndex::<T>::get();
			let new_fund_index = fund_index.checked_add(1).ok_or(Error::<T>::Overflow)?;
```

**File:** polkadot/runtime/common/src/crowdloan/mod.rs (L520-536)
```rust
			let mut refund_count = 0u32;
			// Try killing the crowdloan child trie
			let contributions = Self::contribution_iterator(fund.fund_index);
			// Assume everyone will be refunded.
			let mut all_refunded = true;
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

**File:** polkadot/runtime/common/src/crowdloan/mod.rs (L555-581)
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
		}
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
