### Title
PSM permanently DoS's mint/redeem for an external asset if its live decimals metadata changes after registration - (File: `substrate/frame/psm/src/lib.rs`)

### Summary
`pallet-psm` snapshots an external asset's `decimals` at the moment it is approved via `add_external_asset`, then requires exact equality between that snapshot and the asset's *live* decimals metadata on every subsequent mint/redeem call. Because decimals metadata is controlled by a completely different authority (the underlying `pallet-assets` asset's `Owner`/root via `set_metadata`), a metadata change made outside the PSM's own admin flow permanently blocks the PSM instance's mint/redeem functionality for that external asset — the exact "unsynchronized state update causes DoS" pattern described in the Karak `slashingHandler` report.

### Finding Description
When an external asset is approved for a PSM instance, `add_external_asset` snapshots the external asset's decimals into `ExternalAssetInfo::decimals`: [1](#0-0) 

Similarly, the internal asset's decimals are snapshotted in `PsmInfo::internal_decimals` at PSM-creation time (per the doc comment in `ensure_decimals_match`).

Every mint/redeem-style conversion calls `ensure_decimals_match`, which enforces that the *live* decimals reported by `T::Fungibles::decimals(...)` (backed by `pallet-assets`) still equal the snapshot taken at registration: [2](#0-1) 

`decimals` is part of an asset's metadata in `pallet-assets`, which can be updated after the fact via `set_metadata`/`force_set_metadata`, callable by that asset's own `Owner`/`Issuer` role (or `Root` via the force variant) — an authority entirely independent of the PSM instance's own `full_admin`/`emergency_admin` (`ensure_psm_admin`): [3](#0-2) 

If that asset-team authority changes the asset's decimals for any reason after the PSM has already approved it (`add_external_asset`) — the same "state gets updated after some number of vault/PSM instances have been deployed" scenario from the Karak report — the snapshot stored in `ExternalAssetInfo`/`PsmInfo` is now stale, and `ensure_decimals_match` will start returning `Error::DecimalsMismatch` for every mint and redeem call touching that asset pair, indefinitely.

This mirrors the Karak root cause precisely:
- A registry/whitelist decision is made once and cached inside a per-instance struct (`ExternalAssetInfo.decimals` / `PsmInfo.internal_decimals` ↔ Karak's `NativeVault.slashStore`).
- The authoritative, live value is controlled by a separate, unsynchronized entity (`pallet-assets` metadata ↔ Karak's `Core.assetSlashingHandlers`).
- The pallet enforces strict equality between the stale snapshot and the live value, reverting/DoS'ing all subsequent operations rather than gracefully reconciling or refreshing the cache.

### Impact Explanation
Once triggered, all `mint`/`redeem` operations for the affected `(internal_asset, external_asset)` pair on that PSM instance permanently revert with `DecimalsMismatch`. There is no PSM extrinsic to refresh/re-sync the snapshot; per the pallet's own documentation, the only path to unblock the pair is to `remove_external_asset` (requiring debt to first reach zero — undoable while redemptions are blocked... though redemptions are also blocked, so debt cannot be drained either) and re-`add_external_asset`, exactly the same painful/limited remediation options identified in the Karak finding ("update implementation" / "restore prior value", both with drawbacks). This is a full denial of service of core PSM economic functionality (minting/redeeming) for the affected asset, and in the worst case (decimals changed while `PsmDebt` is nonzero) it can leave the pair in a state where neither minting, redeeming, nor removal is possible, since `remove_external_asset` requires the debt to be zero first.

### Likelihood Explanation
Likelihood is moderate: it requires the external asset's metadata authority (Owner/Issuer of that specific `pallet-assets` asset, or Root) to call `set_metadata`/`force_set_metadata` and change `decimals` after the PSM already onboarded the asset. This is a realistic operational event — asset teams do sometimes correct/update metadata, and the PSM's own admin has no control over or visibility requirement into this action, nor is there any cross-pallet hook to prevent or react to it. Unlike the disqualifying "trusted-role compromise" case, no compromise of the PSM's own admin is required — an entirely different, otherwise benign administrative action from an unrelated authority triggers the DoS, which is precisely the unprivileged-relative-to-PSM trust boundary crossed in the original Karak finding.

### Recommendation
- Do not hard-revert on a live/snapshot decimals mismatch. Options mirroring the Karak mitigations:
  - Recompute conversions using live decimals instead of pinning to a stale snapshot, or
  - Provide a permissionless/PSM-admin extrinsic to refresh the stored decimals snapshot when a mismatch is detected, unblocking users, or
  - Track debt/reserve amounts in a decimals-agnostic unit so a later metadata change cannot invalidate outstanding conversions.
- At minimum, ensure `remove_external_asset` (or an emergency-only variant) can be executed even when `ensure_decimals_match` would otherwise fail, so operators are never stuck with an asset pair that can neither be traded nor removed.

### Proof of Concept
1. Asset team creates external asset `USDC` (id `X`) with `decimals = 6` in `pallet-assets`.
2. PSM admin calls `add_external_asset(internal_asset, X)`. `ExternalAssetInfo { decimals: 6, .. }` is stored (`substrate/frame/psm/src/lib.rs:325-330`).
3. Users mint/redeem normally; `ensure_decimals_match` passes because live decimals (6) == snapshot (6).
4. `X`'s asset `Owner`/`Issuer` (or `Root`) calls `pallet_assets::set_metadata`/`force_set_metadata` to change `decimals` to `8` (e.g. correcting a metadata mistake, or a malicious/compromised asset team on an unrelated asset).
5. Any subsequent `mint`/`redeem` call on `(internal_asset, X)` now fails `ensure_decimals_match` (`substrate/frame/psm/src/lib.rs:1642-1649`) with `Error::DecimalsMismatch`, permanently, for all users, until the PSM asset is removed and re-added (blocked if outstanding `PsmDebt` remains nonzero, since redemptions to drain that debt are themselves blocked).

### Citations

**File:** substrate/frame/psm/src/lib.rs (L325-330)
```rust
	pub struct ExternalAssetInfo {
		/// Per-external circuit breaker status.
		pub status: CircuitBreakerLevel,
		/// Snapshot of the external asset's decimals at registration time.
		pub decimals: u8,
	}
```

**File:** substrate/frame/psm/src/lib.rs (L1633-1651)
```rust
		/// Verify the live decimals for an external still match the snapshot taken at
		/// registration on this PSM, and that the internal asset's live decimals still
		/// match the snapshot stored in [`PsmInfo`].
		pub(crate) fn ensure_decimals_match(
			info: &PsmInfo<T>,
			internal_asset: &T::AssetId,
			external_asset: &T::AssetId,
			external: &ExternalAssetInfo,
		) -> Result<(u8, u8), DispatchError> {
			ensure!(
				T::Fungibles::decimals(external_asset.clone()) == external.decimals,
				Error::<T>::DecimalsMismatch
			);
			ensure!(
				T::Fungibles::decimals(internal_asset.clone()) == info.internal_decimals,
				Error::<T>::DecimalsMismatch
			);
			Ok((external.decimals, info.internal_decimals))
		}
```

**File:** substrate/frame/psm/src/lib.rs (L1659-1675)
```rust
		pub(crate) fn ensure_psm_admin(
			origin: OriginFor<T>,
			internal_asset: &T::AssetId,
			required: impl Fn(PsmManagerLevel) -> bool,
		) -> DispatchResult {
			let admin = PsmAdmin::<T>::get(internal_asset).ok_or(Error::<T>::PsmNotFound)?;
			let caller = <T as Config>::RuntimeOrigin::from(origin).into_caller();
			let level = if caller == admin.full_admin {
				PsmManagerLevel::Full
			} else if caller == admin.emergency_admin {
				PsmManagerLevel::Emergency
			} else {
				return Err(DispatchError::BadOrigin);
			};
			ensure!(required(level), Error::<T>::InsufficientPrivilege);
			Ok(())
		}
```
