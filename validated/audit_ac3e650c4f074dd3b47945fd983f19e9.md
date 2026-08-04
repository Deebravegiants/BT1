### Title
`pallet-psm`: `remove_external_asset` and `remove_psm` check accounting debt, not actual reserve balance, allowing external asset removal while collateral remains stuck - (File: `substrate/frame/psm/src/lib.rs`)

### Summary
This is the same vulnerability class as the reported MarinateV2.sol issue: a function removes an approved asset from tracking based on an internal accounting counter reaching zero, without verifying that the contract/pallet's actual token balance for that asset is also zero. In `pallet-psm`, `remove_external_asset` gates on `PsmDebt::<T>::get(...).is_zero()` [1](#0-0)  rather than on the actual balance of the external asset held by the PSM's reserve account.

### Finding Description
Each PSM instance has a deterministically-derived reserve account (`Self::psm_account(&internal_asset)`) that holds external-asset collateral [2](#0-1) . `PsmDebt` is a separate accounting counter tracking internal asset minted against that external asset, not the actual token balance of the reserve account.

`remove_external_asset` only checks `PsmDebt::<T>::get(&internal_asset, &external_asset).is_zero()` before wiping all per-external state (`ExternalAssets`, `MintingFee`, `RedemptionFee`, `AssetCeilingWeight`, `PsmDebt`) and decrementing `external_count`: [3](#0-2) 

Because the reserve account is a normal, derived on-chain account, any user can transfer the external asset directly into it (e.g., via `pallet-assets::transfer`) without going through `mint`/`redeem`, which is the only path that updates `PsmDebt`. This creates a divergence between `PsmDebt` (accounting) and the actual `Account` balance in `pallet-assets` for the reserve account — mirroring exactly how MarinateV2 could hold token/NFT balances that weren't reflected in the state used to gate removal.

Once `remove_external_asset` succeeds, `ExternalAssets` no longer contains the entry, so the asset is no longer "approved" and none of the pallet's dispatchables (`mint`, `redeem`) can act on it for that internal asset — there is no `sweep`/`recover` extrinsic found in `substrate/frame/psm/src/lib.rs`. Any balance sitting in the reserve account for that specific external asset becomes unreachable through the pallet's normal interface.

The same pattern extends to `remove_psm`, which only checks `external_count == 0` and `total_psm_debt(&internal_asset).is_zero()` before removing `Psm`/`PsmAdmin` and decrementing provider references on the reserve account [4](#0-3)  — again with no check of actual token balances held by `psm_account`.

### Impact Explanation
If residual/donated balances exist in the reserve account for an external asset whose `PsmDebt` is zero (a realistic scenario since anyone can transfer tokens to any account, and dust/rounding from fee calculations in `mint`/`redeem` could also leave small untracked residues), those funds become stuck: the pallet's business logic no longer has a doorway (approved external asset entry) to move them, and there's no admin sweep function. This is a loss-of-funds / permanently-locked-collateral issue, similar in class to the MarinateV2 finding, though the *root cause* here is architectural (accounting counter vs actual balance) rather than identical mechanics.

### Likelihood Explanation
Likelihood is moderate-to-low in practice: it requires (a) an admin/`full_admin` to call `remove_external_asset` or `remove_psm` (a privileged action), and (b) either a griefer intentionally sending dust to the reserve account, or a legitimate rounding/dust residual accumulating from fee math in mint/redeem that isn't captured by `PsmDebt`. I was not able to fully verify from the excerpts examined whether `do_mint`/`do_redeem` can themselves ever leave dust in the reserve account without corresponding `PsmDebt` updates (the mint/redeem implementation bodies were not fully reviewed in this pass), so this part of the likelihood assessment carries some uncertainty. The unprivileged part of the attack (sending unsolicited tokens to the reserve account) is trivial and requires no special access, but by itself does not directly steal funds — it only sets up a state where the admin's subsequent removal action can trap the value, meaning full exploitation is not achievable by an unprivileged actor alone.

### Recommendation
Before permitting `remove_external_asset` (and before decrementing providers / removing the PSM entirely in `remove_psm`), add a check that the actual balance of the external asset held by `Self::psm_account(&internal_asset)` (via `T::Fungibles::balance(...)`) is zero, not just that `PsmDebt` is zero. If a non-zero balance exists, either block removal or provide an explicit sweep path (e.g., transfer residual balance to `fee_destination` or back to depositors) before allowing the external asset to be dropped from `ExternalAssets`.

### Proof of Concept
Conceptual sequence (not fully verified against `do_mint`/`do_redeem` internals due to tool-call limits):
1. PSM instance created for `internal_asset` with approved `external_asset` (e.g., USDC), reserve account `R = Psm::psm_account(internal_asset)`.
2. Attacker (or any user) calls `pallet_assets::transfer(origin, external_asset, R, amount)` directly, moving USDC into `R` without calling `Psm::mint`. `PsmDebt::<T>::get(internal_asset, external_asset)` remains `0` (or whatever it was, unaffected by this transfer).
3. Admin (holding `full_admin`) calls `Psm::remove_external_asset(root/full_admin_origin, internal_asset, external_asset)`. The check `ensure!(PsmDebt::<T>::get(&internal_asset,&external_asset).is_zero(), Error::<T>::AssetHasDebt)` passes despite `R` holding `amount` of `external_asset`.
4. `ExternalAssets`, `MintingFee`, `RedemptionFee`, `AssetCeilingWeight`, `PsmDebt` entries are removed [5](#0-4) .
5. The `amount` of `external_asset` remains in `R`, but no pallet call can reference it anymore since `external_asset` is no longer in `ExternalAssets` for that `internal_asset` — the value is stranded absent a manual/root-level workaround outside the pallet's public interface.

### Citations

**File:** substrate/frame/psm/src/lib.rs (L54-59)
```rust
//! * **PSM instance**: A configured Peg Stability Module, keyed by its internal asset id and
//!   described by [`PsmInfo`]. Each instance has its own reserve account derived from
//!   `blake2_256((PalletId::TYPE_ID, PalletId, internal_asset).encode())`.
//! * **Minting**: Deposit external asset → receive internal asset (minus fee).
//! * **Redemption**: Burn internal asset → receive external asset (minus fee).
//! * **Reserve**: External asset balance held by a PSM's reserve account (derived, not stored).
```

**File:** substrate/frame/psm/src/lib.rs (L1030-1053)
```rust
		pub fn remove_psm(origin: OriginFor<T>, internal_asset: T::AssetId) -> DispatchResult {
			Self::ensure_psm_admin(origin, &internal_asset, |l| l.can_remove_psm())?;
			let info = Psm::<T>::get(&internal_asset).ok_or(Error::<T>::PsmNotFound)?;
			ensure!(info.external_count == 0, Error::<T>::PsmHasApprovedExternals);
			ensure!(Self::total_psm_debt(&internal_asset).is_zero(), Error::<T>::PsmHasDebt);

			let PsmAdminInfo { deposit, .. } =
				PsmAdmin::<T>::get(&internal_asset).ok_or(Error::<T>::PsmNotFound)?;
			if let Some((depositor, ticket)) = deposit {
				ticket.drop(&depositor)?;
			}

			Psm::<T>::remove(&internal_asset);
			PsmAdmin::<T>::remove(&internal_asset);

			// Release the provider references acquired in `create_psm`. Reaps each account when
			// empty; a `ConsumerRemaining` error just means it still holds funds and must stay
			// alive, so the result is intentionally discarded.
			frame_system::Pallet::<T>::dec_providers(&Self::psm_account(&internal_asset)).ok();
			frame_system::Pallet::<T>::dec_providers(&info.fee_destination).ok();

			Self::deposit_event(Event::PsmRemoved { internal_asset });
			Ok(())
		}
```

**File:** substrate/frame/psm/src/lib.rs (L1390-1409)
```rust
			Self::ensure_psm_admin(origin, &internal_asset, |l| l.can_manage_assets())?;
			let mut info = Psm::<T>::get(&internal_asset).ok_or(Error::<T>::PsmNotFound)?;
			ensure!(
				ExternalAssets::<T>::contains_key(&internal_asset, &external_asset),
				Error::<T>::AssetNotApproved
			);
			ensure!(
				PsmDebt::<T>::get(&internal_asset, &external_asset).is_zero(),
				Error::<T>::AssetHasDebt
			);
			ExternalAssets::<T>::remove(&internal_asset, &external_asset);
			MintingFee::<T>::remove(&internal_asset, &external_asset);
			RedemptionFee::<T>::remove(&internal_asset, &external_asset);
			AssetCeilingWeight::<T>::remove(&internal_asset, &external_asset);
			PsmDebt::<T>::remove(&internal_asset, &external_asset);
			info.external_count = info.external_count.saturating_sub(1);
			Psm::<T>::insert(&internal_asset, info);

			Self::deposit_event(Event::ExternalAssetRemoved { internal_asset, external_asset });
			Ok(())
```
