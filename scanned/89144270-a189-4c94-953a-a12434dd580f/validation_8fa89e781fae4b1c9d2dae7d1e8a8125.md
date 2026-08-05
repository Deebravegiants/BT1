Based on my investigation, I found a directly analogous vulnerability pattern in `pallet-psm` (Peg Stability Module), which handles decimal conversion between an "internal" stablecoin and "external" third-party stablecoins — a conceptually similar cross-decimals accounting problem to `ERC4626Oracle`'s decimals bug.

### Title
Decimals drift check (`ensure_decimals_match`) is enforced in `mint` but skipped in `redeem`, allowing stale/mismatched decimal conversion - (File: `substrate/frame/psm/src/lib.rs`)

### Summary
`pallet-psm` snapshots each external asset's decimals in `ExternalAssets` storage at registration time and uses that snapshot (`external.decimals` / `info.internal_decimals`) to scale amounts between internal and external units via `external_to_internal` / `internal_to_external` [1](#0-0) . The `mint` extrinsic calls a validation helper, `Self::ensure_decimals_match(&info, &internal_asset, &external_asset, &external)?`, before doing any conversion, which is documented to return `Error::DecimalsMismatch` if "live decimals diverged from the registration snapshot" [2](#0-1) . The `redeem` extrinsic, however, reads `ext_decimals`/`internal_decimals` directly from the stored snapshot (`external.decimals` and `info.internal_decimals`) without calling the equivalent `ensure_decimals_match` check [3](#0-2) .

### Finding Description
This mirrors the root cause of the ERC4626Oracle bug: a decimals value is cached/assumed rather than being read from (or validated against) the live, authoritative source at the time of the price/conversion calculation. In the ERC4626 case, `IERC4626.decimals()` was wrongly assumed to equal the underlying asset's decimals. In `pallet-psm`, the `internal_decimals`/`ext_decimals` snapshot taken at `register_external_asset`/PSM-creation time is wrongly assumed to remain valid forever, and only `mint` re-validates that assumption via `ensure_decimals_match`; `redeem` does not. If an asset's live metadata decimals ever diverge from the snapshot (e.g., governance changes an asset's metadata via `pallet_assets::set_metadata`, or the asset is a fungible whose decimals can be mutated by its owner), `mint` will correctly reject the operation with `Error::DecimalsMismatch`, but `redeem` will silently proceed using the stale snapshot decimals to compute `external_to_internal`/`internal_to_external` scaling factors.

### Impact Explanation
If the live decimals diverge from the snapshot and redemption is not blocked, `internal_to_external` will scale by the wrong power-of-ten factor, producing an output amount either far too large (over-redemption, draining the PSM reserve or paying out much more external asset than the burned internal asset is worth) or far too small (under-redemption, effectively locking user funds and breaking the 1:1 peg guarantee this pallet exists to maintain). This directly threatens PSM solvency and user funds — the equivalent of the "under/overestimated price" impact in the original oracle report, but expressed as an under/over-scaled swap amount.

### Likelihood Explanation
Exploitability depends entirely on whether the decimals of the internal or external asset can actually change after PSM registration. Since `pallet-psm`'s own authors already added a `DecimalsMismatch` defense specifically for `mint` (per the `prdoc/stable2606/pr_11819.prdoc` changelog: "Runtime drift guard: `mint`/`redeem` return `DecimalsMismatch` if live metadata diverges from the registration snapshot" [4](#0-3) ), the prdoc's own documentation claims this guard applies to *both* `mint` and `redeem`. My reading of the current `redeem` implementation shows no call to `ensure_decimals_match` [3](#0-2) , which is inconsistent with that documented behavior — this is either a genuine gap in `redeem`'s validation or the guard is applied through a code path I could not fully trace (I was unable to locate and inspect the body of `ensure_decimals_match` itself before the tool budget ran out). Whether decimals can actually drift post-registration in practice (e.g., via `pallet_assets::Config` allowing owner-mutable metadata) also needs to be confirmed against the runtime's `pallet_assets` configuration for `AssetHub`, which I did not have iterations left to verify.

### Recommendation
Confirm the exact behavior of `ensure_decimals_match` and, if `redeem` indeed omits this drift check while `mint` performs it, add the same `Self::ensure_decimals_match(...)?` call to `redeem` before computing `external_to_internal`/`internal_to_external`, consistent with the documented "mint/redeem return DecimalsMismatch" guarantee.

### Proof of Concept
Not fully constructable without confirming (a) the body of `ensure_decimals_match`, and (b) whether the runtime configuration allows an approved asset's decimals to change after PSM registration (e.g., via `pallet_assets::set_metadata` called by the asset owner or an admin origin). I was unable to complete this verification within the available tool budget — this should be checked further (e.g., by starting a Devin session) before treating this as a confirmed, reportable finding, since it currently rests on an unverified discrepancy between the `redeem` code path and the PR changelog's claim about drift-guard coverage.

### Citations

**File:** substrate/frame/psm/src/lib.rs (L686-717)
```rust
		///   or higher.
		/// - [`Error::BelowMinimumSwap`]: If the internal-equivalent of `external_amount` is below
		///   the instance's `min_swap_amount`.
		/// - [`Error::FeeTooHigh`]: If the configured minting fee exceeds `max_fee`.
		/// - [`Error::ExceedsMaxPsmDebt`]: If minting would exceed this PSM's debt ceiling
		///   (aggregate or per-asset).
		/// - [`Error::DecimalsMismatch`]: If live decimals diverged from the snapshot taken at
		///   registration.
		/// - [`Error::AmountTooSmallAfterConversion`]: If the conversion to the counter-asset
		///   rounds to zero; swap would transfer nothing.
		///
		/// ## Events
		///
		/// - [`Event::Minted`]: Emitted on successful mint.
		#[pallet::call_index(0)]
		#[pallet::weight(T::WeightInfo::mint(T::MaxExternals::get()))]
		pub fn mint(
			origin: OriginFor<T>,
			internal_asset: T::AssetId,
			external_asset: T::AssetId,
			external_amount: BalanceOf<T>,
			max_fee: Permill,
		) -> DispatchResult {
			let who = ensure_signed(origin)?;
			let info = Psm::<T>::get(&internal_asset).ok_or(Error::<T>::PsmNotFound)?;

			let external = ExternalAssets::<T>::get(&internal_asset, &external_asset)
				.ok_or(Error::<T>::UnsupportedAsset)?;
			ensure!(external.status.allows_minting(), Error::<T>::MintingStopped);

			let (ext_decimals, internal_decimals) =
				Self::ensure_decimals_match(&info, &internal_asset, &external_asset, &external)?;
```

**File:** substrate/frame/psm/src/lib.rs (L811-836)
```rust
		pub fn redeem(
			origin: OriginFor<T>,
			internal_asset: T::AssetId,
			external_asset: T::AssetId,
			internal_amount: BalanceOf<T>,
			max_fee: Permill,
		) -> DispatchResult {
			let who = ensure_signed(origin)?;
			let info = Psm::<T>::get(&internal_asset).ok_or(Error::<T>::PsmNotFound)?;

			let external = ExternalAssets::<T>::get(&internal_asset, &external_asset)
				.ok_or(Error::<T>::UnsupportedAsset)?;
			ensure!(external.status.allows_redemption(), Error::<T>::AllSwapsStopped);

			let ext_decimals = external.decimals;
			let internal_decimals = info.internal_decimals;

			ensure!(internal_amount >= info.min_swap_amount, Error::<T>::BelowMinimumSwap);

			let fee_rate = RedemptionFee::<T>::get(&internal_asset, &external_asset);
			ensure!(fee_rate <= max_fee, Error::<T>::FeeTooHigh);
			let fee = fee_rate.mul_ceil(internal_amount);
			let internal_net = internal_amount.saturating_sub(fee);

			let external_out =
				Self::internal_to_external(internal_net, ext_decimals, internal_decimals)?;
```

**File:** substrate/frame/psm/src/lib.rs (L1575-1624)
```rust
		/// Convert an amount denominated in external-asset units into internal units.
		///
		/// Scales by `10^(ext_decimals - internal_decimals)` — multiplies up when internal has more
		/// decimals, floor-divides when it has fewer. Returns [`Error::ConversionOverflow`] if
		/// the scaling factor or the product does not fit in the balance type.
		pub(crate) fn external_to_internal(
			amount: BalanceOf<T>,
			ext_decimals: u8,
			internal_decimals: u8,
		) -> Result<BalanceOf<T>, Error<T>> {
			use core::cmp::Ordering::*;
			match ext_decimals.cmp(&internal_decimals) {
				Equal => Ok(amount),
				Less => {
					let diff = (internal_decimals - ext_decimals) as u32;
					let factor = Self::pow10(diff)?;
					amount.checked_mul(&factor).ok_or(Error::<T>::ConversionOverflow)
				},
				Greater => {
					let diff = (ext_decimals - internal_decimals) as u32;
					let factor = Self::pow10(diff)?;
					Ok(amount.checked_div(&factor).unwrap_or_else(BalanceOf::<T>::zero))
				},
			}
		}

		/// Convert an amount denominated in internal units into external-asset units.
		///
		/// Inverse of [`Self::external_to_internal`]. Floor-divides when internal has more
		/// decimals, multiplies up when it has fewer.
		pub(crate) fn internal_to_external(
			amount: BalanceOf<T>,
			ext_decimals: u8,
			internal_decimals: u8,
		) -> Result<BalanceOf<T>, Error<T>> {
			use core::cmp::Ordering::*;
			match ext_decimals.cmp(&internal_decimals) {
				Equal => Ok(amount),
				Less => {
					let diff = (internal_decimals - ext_decimals) as u32;
					let factor = Self::pow10(diff)?;
					Ok(amount.checked_div(&factor).unwrap_or_else(BalanceOf::<T>::zero))
				},
				Greater => {
					let diff = (ext_decimals - internal_decimals) as u32;
					let factor = Self::pow10(diff)?;
					amount.checked_mul(&factor).ok_or(Error::<T>::ConversionOverflow)
				},
			}
		}
```

**File:** prdoc/stable2606/pr_11819.prdoc (L18-21)
```text
      checks are meaningful across mixed-decimal assets.
    - Runtime drift guard: `mint`/`redeem` return `DecimalsMismatch` if live
      metadata diverges from the registration snapshot; that asset halts until
      governance intervenes.
```
