### Title
Double-fractionalize of an already-locked NFT via missing `NftToAsset` existence check - ([File: substrate/frame/nft-fractionalization/src/lib.rs])

### Summary
`Pallet::fractionalize` never checks whether `(nft_collection_id, nft_id)` is already present in `NftToAsset::<T>` before locking the NFT and inserting a new `Details` entry. Because `do_lock_nft` (which calls `T::Nfts::disable_transfer`) does not return an error when the item is already transfer-disabled, and the underlying NFT owner does not change on lock (only its transferability flag is toggled), the original owner can call `fractionalize` a second time with a new `asset_id`, silently overwriting the first `Details` entry in `NftToAsset` and orphaning the first asset's holders.

### Finding Description
`fractionalize` at [1](#0-0)  performs:
1. `nft_owner == who` check — this reads the *current* owner via `T::Nfts::owner`, which is unaffected by locking, since `do_lock_nft` only disables transfers rather than transferring custody to the pallet: [2](#0-1) .
2. `T::Currency::hold(...)` — reserves a fresh `Deposit`, unconditionally, every call.
3. `Self::do_lock_nft(...)` — calls `T::Nfts::disable_transfer`, which sets the item's transferable flag; it is not an "insert-or-fail" primitive keyed off `NftToAsset`, so calling it again on an already-locked item does not itself fail on that account.
4. `Self::do_create_asset(asset_id, ...)` and `Self::do_mint_asset(...)` — succeed for any new `asset_id` value B that doesn't already exist, independent of whether the NFT was previously fractionalized under asset A.
5. `NftToAsset::<T>::insert((nft_collection_id, nft_id), Details { asset: asset_id, ... })` at [3](#0-2)  — this is an unconditional `insert`, not `try_mutate`/`ensure!(!contains_key(..))`, so it silently overwrites any pre-existing entry for the same NFT key.

There is no guard such as `ensure!(NftToAsset::<T>::get((nft_collection_id, nft_id)).is_none(), Error::<T>::AlreadyFractionalized)` anywhere in the function or in `do_lock_nft`. The pallet's own `Error<T>` enum at [4](#0-3)  has no "already locked/fractionalized" variant at all, confirming this state was never checked for.

Exploit flow: owner mints NFT, calls `fractionalize(nft, asset_id=A, ...)` — succeeds, `Details{asset: A, ...}` stored, deposit D1 held. Owner (still the owner, since `disable_transfer` doesn't move custody) calls `fractionalize(nft, asset_id=B, ...)` again — `nft_owner == who` still holds, deposit D2 is held (second hold under the same `HoldReason::Fractionalized`), `disable_transfer` is a no-op success, asset B is created/minted, and `NftToAsset::insert` overwrites the map entry, discarding the `Details` for asset A. Asset A tokens are now unbacked: `unify` for asset A will fail with `IncorrectAssetId` (comparing against the now-stored asset B) at [5](#0-4) , since the entry `maybe_details.take()` will already have been consumed once B is unified, or will simply never match A. Only a successful `unify` on asset B can retrieve the NFT, and it will release only one `Deposit` amount via `T::Currency::release` at [6](#0-5) , leaving the first hold (D1) permanently stuck (BestEffort release of a single `deposit` value cannot recover the doubled hold), and asset A permanently unbacked/unclaimable.

### Impact Explanation
Holders of the first fractional asset (A) permanently lose their claim on the underlying NFT — their tokens become unbacked/worthless since the pallet no longer tracks that asset as owning any NFT and `unify(asset_id=A)` will always fail with `IncorrectAssetId`. Additionally, the owner's reserved `Deposit` from the first `fractionalize` call is left stranded (never released), since only one release occurs on `unify`, matching the scoped "unbacked asset / stranded value" / "double-hold of Deposit" impact.

### Likelihood Explanation
Fully reachable by an ordinary signed account that is the NFT owner, using only the public `fractionalize` extrinsic twice (no need for `batch_all` timing tricks — even two separate blocks work, since nothing in storage or `Nfts::disable_transfer` blocks re-locking an already-locked item on behalf of the same owner). No privileged origin, XCM, or race condition is required — this is a straightforward missing-existence-check bug, deterministic and 100% reproducible.

### Recommendation
In `fractionalize`, before holding the deposit/locking the NFT, add `ensure!(NftToAsset::<T>::get((nft_collection_id, nft_id)).is_none(), Error::<T>::AlreadyFractionalized)` (adding a new `AlreadyFractionalized` error variant), and use `try_mutate` (fail if occupied) instead of unconditional `insert` for defense in depth.

### Proof of Concept
Rust integration test extending `fractionalize_should_work` in `substrate/frame/nft-fractionalization/src/tests.rs`:
1. Mint NFT `(collection, item)`, call `fractionalize(collection, item, asset_id=A, beneficiary, fractions)` — assert `Ok`.
2. Call `fractionalize(collection, item, asset_id=B, beneficiary, fractions)` again on the same NFT — currently succeeds; assert it should instead return `Err(Error::<Test>::AlreadyFractionalized)` (or equivalent).
3. Assert `NftToAsset::<Test>::get((collection, item))` still equals the original `Details{asset: A, ...}` (not overwritten to B).
4. Assert `Balances::reserved_balance(&owner)` equals exactly one `Deposit`, not two.
5. As a regression check without the fix in place, demonstrate that `unify(collection, item, asset_id=A, ...)` returns `Error::IncorrectAssetId` after the second fractionalize, proving asset A is orphaned.

### Citations

**File:** substrate/frame/nft-fractionalization/src/lib.rs (L179-189)
```rust
	#[pallet::error]
	pub enum Error<T> {
		/// Asset ID does not correspond to locked NFT.
		IncorrectAssetId,
		/// The signing account has no permission to do the operation.
		NoPermission,
		/// NFT doesn't exist.
		NftNotFound,
		/// NFT has not yet been fractionalised.
		NftNotFractionalized,
	}
```

**File:** substrate/frame/nft-fractionalization/src/lib.rs (L220-263)
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

			Self::deposit_event(Event::NftFractionalized {
				nft_collection: nft_collection_id,
				nft: nft_id,
				fractions,
				asset: asset_id,
				beneficiary,
			});

			Ok(())
		}
```

**File:** substrate/frame/nft-fractionalization/src/lib.rs (L293-296)
```rust
			NftToAsset::<T>::try_mutate_exists((nft_collection_id, nft_id), |maybe_details| {
				let details = maybe_details.take().ok_or(Error::<T>::NftNotFractionalized)?;
				ensure!(details.asset == asset_id, Error::<T>::IncorrectAssetId);

```

**File:** substrate/frame/nft-fractionalization/src/lib.rs (L301-306)
```rust
				T::Currency::release(
					&HoldReason::Fractionalized.into(),
					&asset_creator,
					deposit,
					BestEffort,
				)?;
```

**File:** substrate/frame/nft-fractionalization/src/lib.rs (L336-339)
```rust
		/// Prevent further transferring of NFT.
		fn do_lock_nft(nft_collection_id: T::NftCollectionId, nft_id: T::NftId) -> DispatchResult {
			T::Nfts::disable_transfer(&nft_collection_id, &nft_id)
		}
```
