### Title
`fractionalize` can be called twice on the same NFT, orphaning the previously minted fractional asset while leaving the underlying NFT lock unchanged - (File: substrate/frame/nft-fractionalization/src/lib.rs)

### Summary
`fractionalize` only checks that the caller is the current owner of the NFT and that `asset_id` is unused; it never checks whether `(nft_collection_id, nft_id)` is already present in `NftToAsset`. Since locking an NFT via `do_lock_nft` only disables transfers and does not change the item's owner, the same owner can call `fractionalize` again on an already-fractionalized NFT with a fresh `asset_id`, which overwrites the `NftToAsset` entry and strands the first fractional asset as permanently unbacked.

### Finding Description
In `fractionalize` [1](#0-0) , the only ownership/state guard is:
```
let nft_owner = T::Nfts::owner(&nft_collection_id, &nft_id).ok_or(Error::<T>::NftNotFound)?;
ensure!(nft_owner == who, Error::<T>::NoPermission);
```
There is no check of `NftToAsset::<T>::contains_key((nft_collection_id, nft_id))` before proceeding. `do_lock_nft` merely calls `T::Nfts::disable_transfer`, which flips a per-item transfer-lock flag on `pallet-nfts` but does not transfer the item away from `who` [2](#0-1) . As a result, after the first `fractionalize` call, `T::Nfts::owner(...)` still returns the original `who`, so the `ensure!(nft_owner == who, ...)` check trivially passes again on a second call for the same `(nft_collection_id, nft_id)` pair, as long as a fresh, unused `asset_id2` is supplied (asset creation itself is guarded only by asset-id uniqueness in `T::Assets::create`, not by NFT-based uniqueness).

The second call:
1. Places a second `Deposit` hold on the same account via `T::Currency::hold` (deposit1 for asset1, deposit2 for asset2).
2. Calls `do_lock_nft` again (idempotent no-op on an already-disabled item).
3. Creates a brand-new asset `asset2` and mints `fractions2` into `beneficiary2`.
4. Unconditionally overwrites the `NftToAsset` storage entry via `NftToAsset::<T>::insert((nft_collection_id, nft_id), Details { asset: asset_id2, ... })` [3](#0-2) .

After this overwrite, the `unify` extrinsic [4](#0-3)  for the given `(nft_collection_id, nft_id)` will only ever match `asset_id2` (`ensure!(details.asset == asset_id, Error::<T>::IncorrectAssetId)`). Holders of `asset1` — the first fractional token, which was fully "backed" and freely tradable at the time of mint — can never redeem it for the NFT any more, since the stored `Details` record referencing `asset1` has been replaced. The first fractional-asset holders are left holding a token that markets and other integrators still treat as backed by the locked NFT (it still exists, is still transferable, still has metadata pointing to the NFT), but the actual redemption path (`unify`) is now permanently bound to `asset2`. This is a stale reference left by the ownership-preserving re-fractionalization: `asset1`'s minted supply is now unbacked, and the deposit paid for `asset1` remains held indefinitely (never released, since only the `asset_creator`/`deposit` fields of the *current* `Details` record, tied to `asset2`, are used in `unify`).

### Impact Explanation
This produces an unbacked fractional-asset situation: `asset1` tokens minted to `beneficiary1` in the first call continue to circulate as if entitled to a share of the locked NFT, but the only path that can release the NFT (`unify`) is now permanently tied to `asset2`. Any third party who acquired `asset1` tokens on secondary markets (assuming they are backed 1:1 by the NFT, which is the entire premise of this pallet) loses that backing with no recourse — this matches the "unauthorized NFT or fractional-asset transfer / unbacked mint" impact category, since it lets the NFT owner mint a second, disjoint fractional-asset claim over the same locked collateral without ever losing ownership/control of the underlying NFT.

### Likelihood Explanation
The attacker only needs to be the current owner of an NFT that has already been fractionalized through this pallet (which is entirely under their control, since they chose to fractionalize it in the first place), and simply needs to submit a second signed `fractionalize` extrinsic with a fresh `asset_id` and a `beneficiary` of their choosing (or someone else's, to increase confusion) before ever calling `unify`. No special timing window, race condition, or privileged access is required — it's a straightforward repeated call using a signed extrinsic path with attacker-controlled `asset_id`/`fractions`/`beneficiary` parameters, which is a normal user-triggered exploit path.

### Recommendation
In `fractionalize`, add a guard immediately after (or instead of) the owner check to reject re-fractionalization of an NFT that is already tracked in `NftToAsset`, e.g.:
```rust
ensure!(!NftToAsset::<T>::contains_key((nft_collection_id, nft_id)), Error::<T>::AlreadyFractionalized);
```
This prevents creating a second, disjoint `Details` record (and second asset) for an NFT whose lock/deposit/`Details` mapping is already active, closing the stale-reference window entirely.

### Proof of Concept
Rust integration test (in `substrate/frame/nft-fractionalization/src/tests.rs` style, using the pallet's `mock.rs` environment):
```rust
#[test]
fn double_fractionalize_orphans_first_asset() {
    new_test_ext().execute_with(|| {
        // setup: mint NFT #0 in collection #0 to account 1
        mint_nft(0, 0, 1);

        // first fractionalize: asset_id = 1, beneficiary = 1, fractions = 100
        assert_ok!(NftFractionalization::fractionalize(
            RuntimeOrigin::signed(1), 0, 0, 1, 1, 100
        ));
        // asset 1 now exists and is minted to account 1
        assert_eq!(Assets::balance(1, 1), 100);
        assert!(NftToAsset::<Test>::get((0, 0)).unwrap().asset == 1);

        // NFT owner is unchanged (still account 1) because locking only disables transfer
        assert_eq!(Nfts::owner(0, 0), Some(1));

        // second fractionalize on same NFT: asset_id = 2, beneficiary = 1, fractions = 50
        assert_ok!(NftFractionalization::fractionalize(
            RuntimeOrigin::signed(1), 0, 0, 2, 1, 50
        ));

        // NftToAsset now points to asset 2, asset 1 is orphaned
        let details = NftToAsset::<Test>::get((0, 0)).unwrap();
        assert_eq!(details.asset, 2);

        // unify with asset_id = 1 (the first, previously "backed" asset) now fails
        assert_noop!(
            NftFractionalization::unify(RuntimeOrigin::signed(1), 0, 0, 1, 1),
            Error::<Test>::IncorrectAssetId
        );

        // but asset 1 tokens are still freely held/transferable, unbacked
        assert_eq!(Assets::balance(1, 1), 100);
    });
}
```
Expected assertions: the test should demonstrate that after a second `fractionalize` call on the same `(nft_collection_id, nft_id)`, `unify` for the original `asset_id` fails with `IncorrectAssetId` while the original asset's tokens remain in circulation, proving the first fractional asset became permanently unredeemable/unbacked. Applying the recommended `contains_key` guard would make the second `fractionalize` call fail with a new `AlreadyFractionalized` error instead, closing the gap.

### Citations

**File:** substrate/frame/nft-fractionalization/src/lib.rs (L220-252)
```rust
		pub fn fractionalize(
			origin: OriginFor<T>,
			nft_collection_id: T::NftCollectionId,
			nft_id: T::NftId,
			asset_id: AssetIdOf<T>,
			beneficiary: AccountIdLookupOf<T>,
			fractions: AssetBalanceOf<T>,
		) -> DispatchResult {
			let who = ensure_signed(origin)?;
			let beneficiary = T::Lookup::lookup(beneficiary)?;

			let nft_owner =
				T::Nfts::owner(&nft_collection_id, &nft_id).ok_or(Error::<T>::NftNotFound)?;
			ensure!(nft_owner == who, Error::<T>::NoPermission);

			let pallet_account = Self::get_pallet_account();
			let deposit = T::Deposit::get();
			T::Currency::hold(&HoldReason::Fractionalized.into(), &nft_owner, deposit)?;
			Self::do_lock_nft(nft_collection_id, nft_id)?;
			Self::do_create_asset(asset_id.clone(), pallet_account.clone())?;
			Self::do_mint_asset(asset_id.clone(), &beneficiary, fractions)?;
			Self::do_set_metadata(
				asset_id.clone(),
				&who,
				&pallet_account,
				&nft_collection_id,
				&nft_id,
			)?;

			NftToAsset::<T>::insert(
				(nft_collection_id, nft_id),
				Details { asset: asset_id.clone(), fractions, asset_creator: nft_owner, deposit },
			);
```

**File:** substrate/frame/nft-fractionalization/src/lib.rs (L283-317)
```rust
		pub fn unify(
			origin: OriginFor<T>,
			nft_collection_id: T::NftCollectionId,
			nft_id: T::NftId,
			asset_id: AssetIdOf<T>,
			beneficiary: AccountIdLookupOf<T>,
		) -> DispatchResult {
			let who = ensure_signed(origin)?;
			let beneficiary = T::Lookup::lookup(beneficiary)?;

			NftToAsset::<T>::try_mutate_exists((nft_collection_id, nft_id), |maybe_details| {
				let details = maybe_details.take().ok_or(Error::<T>::NftNotFractionalized)?;
				ensure!(details.asset == asset_id, Error::<T>::IncorrectAssetId);

				let deposit = details.deposit;
				let asset_creator = details.asset_creator;
				Self::do_burn_asset(asset_id.clone(), &who, details.fractions)?;
				Self::do_unlock_nft(nft_collection_id, nft_id, &beneficiary)?;
				T::Currency::release(
					&HoldReason::Fractionalized.into(),
					&asset_creator,
					deposit,
					BestEffort,
				)?;

				Self::deposit_event(Event::NftUnified {
					nft_collection: nft_collection_id,
					nft: nft_id,
					asset: asset_id,
					beneficiary,
				});

				Ok(())
			})
		}
```

**File:** substrate/frame/nft-fractionalization/src/lib.rs (L336-339)
```rust
		/// Prevent further transferring of NFT.
		fn do_lock_nft(nft_collection_id: T::NftCollectionId, nft_id: T::NftId) -> DispatchResult {
			T::Nfts::disable_transfer(&nft_collection_id, &nft_id)
		}
```
