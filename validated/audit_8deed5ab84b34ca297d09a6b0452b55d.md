The code confirms the claim exactly as described. The payload at line 786 is `(index, &who, old_balance, value)` — no `fund.fund_index` is included, while `old_balance` is read from `contribution_get(fund.fund_index, &who)` which is keyed to the child-trie derived from `fund.fund_index`, not `index` (ParaId). This means the signed payload only binds to the `ParaId`, not to the specific fund instance.

I confirmed all the referenced code paths:
- `create` at line 369-440 allocates a new `fund_index` each time and requires no existing fund at that `ParaId` (line 406), consistent with re-creation after dissolution.
- `contribute`/`do_contribute` at lines 749-791 shows the vulnerable signature check.
- `withdraw` and `dissolve` (read earlier from the prompt's citations, matching actual file layout at those line numbers) reset the contribution and remove the fund respectively.

The exploit path is logically sound: since `old_balance` is fetched from the new fund's child-trie (which starts at 0 for a new `fund_index`), and the payload only encodes `(ParaId, who, old_balance, value)`, a previously captured signature for `(P, who, 0, V)` remains valid for verification against a new fund on the same `ParaId` as long as the verifier key is reused and the old_balance/value match. This is a real gap in binding the signature to a specific campaign instance.

Audit Report

## Title
Verifier-signature replay across re-created crowdloans for the same ParaId due to missing fund-instance binding in signed payload - (File: polkadot/runtime/common/src/crowdloan/mod.rs)

## Summary
`Pallet::do_contribute` builds the verifier-signature payload as `(index, &who, old_balance, value)` [1](#0-0) , where `index` is the `ParaId` and `old_balance` is read live from the child-trie contribution storage keyed by `fund.fund_index` [2](#0-1) . Because the payload contains no fund-instance identifier, a signature captured for one crowdloan campaign on a `ParaId` remains valid for a later, independently created crowdloan on the same `ParaId` once the contributor's on-chain balance in the new fund's child-trie starts at the same value (0).

## Finding Description
The permissioned-crowdloan gate only checks that `signature.verify(payload, verifier)` succeeds, with `payload = (index, who, old_balance, value)`, where `old_balance` is fetched fresh via `contribution_get(fund.fund_index, &who)` [3](#0-2) . The child-trie key used for contribution storage is derived from `fund.fund_index`, an internal counter incremented on every `create` call [4](#0-3) , not from the `ParaId`. The signed payload only binds to `index` (`ParaId`), never to `fund.fund_index`.

`create` explicitly permits creating a new fund for a `ParaId` once any prior fund entry for that id has been removed (`ensure!(!Funds::<T>::contains_key(index), ...)`) [5](#0-4) , and allocates a fresh `fund_index` for the new campaign [6](#0-5) . Since the child-trie is keyed by `fund_index`, `contribution_get` on the new fund starts at the default (0) for any account, even if that account had previously contributed and withdrawn from a prior fund on the same `ParaId`.

Consequently, a signature originally produced for `(ParaId, who, old_balance=0, value=V)` under the first campaign remains a valid signature to submit against the newly created campaign on the same `ParaId`, provided the verifier key is reused and the contributor's balance in the new campaign is still 0 (true for a brand-new fund). Existing checks in `do_contribute` — `now < fund.end` [7](#0-6) , cap check, lease period check, and auction-won check — do not check fund identity or reject stale signatures; none of them bind the check to fund instance identity.

## Impact Explanation
This breaks the intended guarantee of permissioned crowdloans, that only contributions explicitly approved by the off-chain `verifier` for the *current* campaign are accepted. An attacker who was legitimately approved for an earlier campaign on a `ParaId` can force acceptance of a contribution into a later, unrelated campaign without a fresh verifier approval, as long as the verifier key is reused (common in serial crowdloan rounds by the same project) and the balance/value match. This is an unauthorized state change — an unapproved contribution recorded and funds moved into the new fund's pot — matching the impact of bypassing a permissioned allowlist gate.

## Likelihood Explanation
The exploit requires: the same verifier key reused across campaigns for the same `ParaId` (a realistic and common operational choice, but not guaranteed), the attacker retaining an old signature, and the natural lifecycle of `withdraw` → `dissolve` → `create` occurring for that `ParaId`, all of which use ordinary signed extrinsics with no elevated privilege except `create`'s requirement that the caller be the parachain manager, which is expected in the normal flow of setting up a new campaign, not attacker-controlled. The likelihood is bounded by needing verifier-key reuse, which is a real, but not universal, practice.

## Recommendation
Bind the verifier signature to the specific fund instance by including `fund.fund_index` (and/or fund creation block number) in the signed payload, e.g., `(fund.fund_index, index, &who, old_balance, value)`, so that a signature is cryptographically scoped to exactly one crowdloan campaign and cannot be replayed after that fund is dissolved and a new one is created for the same `ParaId`.

## Proof of Concept
1. Create fund #1 for `ParaId(1)` with `verifier = V` via `create` (allocates `fund_index = 0`).
2. Sign payload `(ParaId(1), who, 0, value)` off-chain with `V`'s key to produce `sig`.
3. Call `contribute(ParaId(1), value, Some(sig))` from `who` — succeeds; `contribution_get(0, who) == value`.
4. Advance blocks past `fund.end`; call `withdraw(who, ParaId(1))` — resets contribution to 0, per [8](#0-7) .
5. With `fund.raised == 0`, call `dissolve(ParaId(1))` — removes the `Funds` entry, per [9](#0-8) .
6. Recreate a fund for `ParaId(1)` with the same `verifier = V` (allocates a new `fund_index = 1`).
7. Replay the same captured `sig` via `contribute(ParaId(1), value, Some(sig))` — assert this succeeds instead of returning `Error::<T>::InvalidSignature`, and assert `Funds::<Test>::get(ParaId(1)).raised == value`, confirming the unauthorized contribution was accepted in the new campaign without a fresh verifier signature.

### Citations

**File:** polkadot/runtime/common/src/crowdloan/mod.rs (L405-406)
```rust
			// There should not be an existing fund.
			ensure!(!Funds::<T>::contains_key(index), Error::<T>::FundNotEnded);
```

**File:** polkadot/runtime/common/src/crowdloan/mod.rs (L412-436)
```rust
			let fund_index = NextFundIndex::<T>::get();
			let new_fund_index = fund_index.checked_add(1).ok_or(Error::<T>::Overflow)?;

			let deposit = T::SubmissionDeposit::get();

			frame_system::Pallet::<T>::inc_providers(&Self::fund_account_id(fund_index));
			CurrencyOf::<T>::reserve(&depositor, deposit)?;

			Funds::<T>::insert(
				index,
				FundInfo {
					depositor,
					verifier,
					deposit,
					raised: Zero::zero(),
					end,
					cap,
					last_contribution: LastContribution::Never,
					first_period,
					last_period,
					fund_index,
				},
			);

			NextFundIndex::<T>::put(new_fund_index);
```

**File:** polkadot/runtime/common/src/crowdloan/mod.rs (L475-500)
```rust
		pub fn withdraw(
			origin: OriginFor<T>,
			who: T::AccountId,
			#[pallet::compact] index: ParaId,
		) -> DispatchResult {
			ensure_signed(origin)?;

			let mut fund = Funds::<T>::get(index).ok_or(Error::<T>::InvalidParaId)?;
			let now = frame_system::Pallet::<T>::block_number();
			let fund_account = Self::fund_account_id(fund.fund_index);
			Self::ensure_crowdloan_ended(now, &fund_account, &fund)?;

			let (balance, _) = Self::contribution_get(fund.fund_index, &who);
			ensure!(balance > Zero::zero(), Error::<T>::NoContributions);

			CurrencyOf::<T>::transfer(&fund_account, &who, balance, AllowDeath)?;
			CurrencyOf::<T>::reactivate(balance);

			Self::contribution_kill(fund.fund_index, &who);
			fund.raised = fund.raised.saturating_sub(balance);

			Funds::<T>::insert(index, &fund);

			Self::deposit_event(Event::<T>::Withdrew { who, fund_index: index, amount: balance });
			Ok(())
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

**File:** polkadot/runtime/common/src/crowdloan/mod.rs (L761-763)
```rust
		// Make sure crowdloan has not ended
		let now = frame_system::Pallet::<T>::block_number();
		ensure!(now < fund.end, Error::<T>::ContributionPeriodOver);
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
