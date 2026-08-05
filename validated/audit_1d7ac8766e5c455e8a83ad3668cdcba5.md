Audit Report

## Title
Verifier signature replay across crowdloan fund lifecycles due to missing `fund_index` in signed payload - (File: `polkadot/runtime/common/src/crowdloan/mod.rs`)

## Summary
`Pallet::do_contribute` verifies KYC/verifier signatures against the payload `(index, &who, old_balance, value)` [1](#0-0) , where `index` is the `ParaId` and `old_balance` is read from the current fund's child-trie keyed by `fund.fund_index` [2](#0-1) . Because `fund_index` is never part of the signed payload, and `old_balance` resets to `0` whenever a fund is dissolved and a fresh fund is created for the same `ParaId`, a signature obtained for a contributor's first contribution to one fund can be replayed unmodified as the first contribution to a subsequent fund for the same parachain.

## Finding Description
`create` assigns a fresh, monotonically-increasing `fund_index` from `NextFundIndex` and stores it in the `FundInfo` for that `ParaId` [3](#0-2) . `dissolve` removes the `Funds` entry for a `ParaId` once `raised` is zero, permitted either by the fund's depositor or by anyone once `now >= fund.end` [4](#0-3) , which permits a brand-new `create` call to be issued later for the identical `ParaId`.

In `do_contribute`, the contributor's `old_balance` is fetched from the child-trie associated with `fund.fund_index` [5](#0-4) , and the verifier signature is checked over `(index, &who, old_balance, value)` — notably omitting `fund.fund_index` from the payload [6](#0-5) . Since a newly created fund for the same `ParaId` gets a fresh child-trie via `id_from_index(new_fund_index)`, any contributor's `old_balance` there starts at `0`, exactly matching the value signed for that contributor's original first contribution to the prior (now-dissolved) fund. Because `index` (the `ParaId`) is unchanged across the dissolve/recreate cycle, the entire signed payload — and thus the `MultiSignature` — is identical, so the previously broadcast extrinsic can be resubmitted verbatim and will pass verification.

None of the other checks in `do_contribute` (minimum contribution, cap, contribution period, lease period, auction/VRF status) reference `fund_index` or otherwise distinguish which fund lifecycle a given signature was issued for [7](#0-6) , so none of them prevent this replay.

## Impact Explanation
This breaks the intended guarantee that a verifier signature authorizes exactly one contribution event tied to a specific fund instance. A contributor whose participation was previously KYC/whitelist-gated can bypass a fresh verifier authorization requirement on a newly created fund for the same parachain simply by resubmitting an old, already-public extrinsic — undermining jurisdictional/accredited-investor gating that crowdloan organizers rely on the verifier mechanism to enforce.

## Likelihood Explanation
The preconditions are realistic and require no privileged access: a verifier-gated fund is created, a contributor's first contribution (`old_balance == 0`) is broadcast on-chain (extrinsics and signatures are public), the fund is later dissolved once `raised` returns to zero (a routine outcome after `refund`, achievable by anyone once `now >= fund.end`), and a new fund is created for the same `ParaId`. The "attacker" only replays their own previously-authorized, previously-signed transaction — no cryptographic forgery is required, and `who` is bound to the payload so this is not third-party exploitable, but it does let the original contributor bypass fresh authorization for the new fund.

## Recommendation
Bind the verifier signature to the specific fund instance by including `fund.fund_index` (or another value unique to the fund's lifetime) in the signed payload, e.g., `(fund.fund_index, index, &who, old_balance, value)`, so a signature cannot be replayed across dissolve/recreate cycles for the same `ParaId`.

## Proof of Concept
1. `create` fund `F1` for `ParaId(1)` with `verifier = Some(pubkey)`.
2. Verifier signs payload `(ParaId(1), who=1, old_balance=0, value=100)` → `sig`.
3. `contribute(who=1, index=1, value=100, Some(sig))` succeeds; `Contributed` event emitted, extrinsic and `sig` now public.
4. `refund` fund `F1` (contribution removed, `raised` back to `0`), then `dissolve(index=1)` (removes `Funds` entry).
5. `create` a new fund `F2` for the same `ParaId(1)` (new `fund_index`, fresh child-trie).
6. Replay `contribute(who=1, index=1, value=100, Some(sig))` using the identical `sig` from step 2, with no new signing.
7. Observe the call succeeds because `old_balance` for `who` in `F2`'s child-trie is `0`, matching the originally signed payload — confirming the signature is replayable across the fund lifecycle boundary.

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

**File:** polkadot/runtime/common/src/crowdloan/mod.rs (L695-699)
```rust
	}

	pub fn contribution_get(index: FundIndex, who: &T::AccountId) -> (BalanceOf<T>, Vec<u8>) {
		who.using_encoded(|b| {
			child::get_or_default::<(BalanceOf<T>, Vec<u8>)>(&Self::id_from_index(index), b)
```

**File:** polkadot/runtime/common/src/crowdloan/mod.rs (L756-780)
```rust
		ensure!(value >= T::MinContribution::get(), Error::<T>::ContributionTooSmall);
		let mut fund = Funds::<T>::get(index).ok_or(Error::<T>::InvalidParaId)?;
		fund.raised = fund.raised.checked_add(&value).ok_or(Error::<T>::Overflow)?;
		ensure!(fund.raised <= fund.cap, Error::<T>::CapExceeded);

		// Make sure crowdloan has not ended
		let now = frame_system::Pallet::<T>::block_number();
		ensure!(now < fund.end, Error::<T>::ContributionPeriodOver);

		// Make sure crowdloan is in a valid lease period
		let now = frame_system::Pallet::<T>::block_number();
		let (current_lease_period, _) =
			T::Auctioneer::lease_period_index(now).ok_or(Error::<T>::NoLeasePeriod)?;
		ensure!(current_lease_period <= fund.first_period, Error::<T>::ContributionPeriodOver);

		// Make sure crowdloan has not already won.
		let fund_account = Self::fund_account_id(fund.fund_index);
		ensure!(
			!T::Auctioneer::has_won_an_auction(index, &fund_account),
			Error::<T>::BidOrLeaseActive
		);

		// We disallow any crowdloan contributions during the VRF Period, so that people do not
		// sneak their contributions into the auction when it would not impact the outcome.
		ensure!(!T::Auctioneer::auction_status(now).is_vrf(), Error::<T>::VrfDelayInProgress);
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
