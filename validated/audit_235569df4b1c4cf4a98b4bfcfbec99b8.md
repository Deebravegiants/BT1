Audit Report

## Title
Crowdloan verifier signature replay across dissolved-and-recreated funds due to signature payload lacking fund instance binding - (File: polkadot/runtime/common/src/crowdloan/mod.rs)

## Summary
`do_contribute` signs/verifies the payload `(index, &who, old_balance, value)` without including `fund.fund_index` or any other per-fund-lifecycle nonce. Since a new crowdloan for the same `ParaId` always starts with a fresh, empty child trie (keyed by the new `fund_index`), `old_balance` resets to `0`, allowing a verifier signature originally issued for a contributor's first contribution to an earlier, dissolved fund incarnation to be replayed against a newly created fund for the same `ParaId` if the verifier key is reused.

## Finding Description
The signed/verified payload in `do_contribute` is constructed and checked as: [1](#0-0) 

`old_balance` is fetched via `contribution_get(fund.fund_index, &who)`, which reads from a child trie whose key is derived from `fund_index`: [2](#0-1) 

`fund_index` is allocated fresh on every `create` call (monotonically incrementing, guarded by `checked_add`), so a new fund for the same `ParaId` gets a brand-new, empty child trie: [3](#0-2) 

The `verifier` field is supplied as a parameter to `create` and is not required to differ from a previous fund's verifier for the same `ParaId`, so a manager can legitimately reuse the same verifier key across fund re-creations. Because the payload signed by the verifier does not include `fund.fund_index` (or any other per-incarnation identifier), a signature issued for `(index, who, 0, value)` under an old, now-dissolved fund remains a valid signature for `(index, who, 0, value)` under a brand-new fund with the same `ParaId`, since the new fund's `old_balance` for that contributor is also `0`. No other check in `do_contribute` (lines 756-791) binds the signature to a specific fund lifecycle — the checks present (`ContributionTooSmall`, `CapExceeded`, `ContributionPeriodOver`, `BidOrLeaseActive`, `VrfDelayInProgress`) address unrelated invariants and do not prevent this replay.

`dissolve` is reachable by the fund depositor (or anyone once `now >= fund.end`) and requires `fund.raised.is_zero()`: [4](#0-3) 

This confirms the dissolve-and-recreate cycle described is achievable through normal, unprivileged/parachain-manager-level extrinsics without requiring root or governance action.

## Impact Explanation
This is a KYC/authorization-bypass issue: a contributor can reuse a stale verifier signature to contribute to a newly created crowdloan for the same `ParaId` without obtaining fresh sign-off from the verifier, undermining the intended per-fund authorization gate. It does not directly cause fund loss or insolvency since the contributor still transfers real balance, but it breaks the security guarantee that the `verifier` signature check is supposed to provide for the new fund's contribution window.

## Likelihood Explanation
The exploit requires: (1) a fund for a given `ParaId` is dissolved and a new fund created for the same `ParaId` (a normal operational flow, e.g., retrying after a failed auction), (2) the new fund reuses the same verifier key (a realistic administrative choice for the same project's KYC provider), and (3) the attacker retained a signature for `old_balance == 0` (trivially satisfied by their first-ever contribution signature to the old fund). All of this is achievable without any privileged action beyond the normal parachain-manager `create`/`dissolve` calls, making the scenario plausible in practice.

## Recommendation
Include `fund.fund_index` (or another per-creation nonce, e.g., a hash of the fund's deposit/creation block) in the payload signed and verified in `do_contribute`, so that a verifier signature is cryptographically scoped to exactly one fund lifecycle and cannot be replayed after a `dissolve`/`create` cycle recreates a fund for the same `ParaId`.

## Proof of Concept
1. Create fund #1 for `ParaId(1)` via `create` with `verifier = V`; note the assigned `fund.fund_index` (e.g., `0`).
2. Have `V` sign payload `(ParaId(1), who, 0, value)` off-chain → `sig`.
3. Call `contribute(ParaId(1), value, Some(sig))` from `who`; the check at `do_contribute` lines 784-790 passes, and `who`'s child-trie balance becomes `value`.
4. Ensure `fund.raised` returns to zero (e.g., refund flow) and call `dissolve(ParaId(1))`, satisfying the conditions in lines 555-581.
5. Call `create` again for `ParaId(1)` reusing `verifier = V`; this allocates a new `fund.fund_index` (e.g., `1`) with a fresh, empty child trie.
6. Replay `contribute(ParaId(1), value, Some(sig))` from `who` with the same old `sig`. Because `contribution_get` for the new `fund_index` returns `old_balance == 0` again, the signature check at lines 786-790 passes and the call succeeds — demonstrating the replay, whereas a fund-scoped signature scheme should instead return `Error::<T>::InvalidSignature`.

### Citations

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
