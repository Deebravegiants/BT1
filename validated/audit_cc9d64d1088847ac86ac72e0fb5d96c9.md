## Analysis: Analog Vulnerability Found

The reported vulnerability class (an asset priced/valued at 1:1 parity to a reference, with no protection against loss of peg, causing bad debt) has a direct analog in `pallet-psm` (`substrate/frame/psm/src/lib.rs`), which is even more exposed than the original report since it doesn't use any oracle at all — it hard-codes a 1:1 parity assumption between the internal stablecoin and any approved external asset.

### Title
PSM `mint`/`redeem` assume permanent 1:1 parity between internal and external assets with no peg-deviation protection - (File: `substrate/frame/psm/src/lib.rs`)

### Summary
`pallet-psm` implements a Peg Stability Module that swaps an internal stablecoin for approved external assets (e.g. USDC/USDT-style bridged/wrapped stablecoins) strictly 1:1 (adjusted only for decimals), with no price oracle, TWAP, or peg-deviation check anywhere in the mint/redeem path.

### Finding Description
`Pallet::mint` computes `internal_equivalent` purely via `Self::external_to_internal`, a decimal-only conversion, then mints internal asset 1:1 minus fee: [1](#0-0) 

`Pallet::redeem` mirrors this, converting `internal_amount` to `external_out` via `Self::internal_to_external`, again purely decimal-based, and transferring external reserve out 1:1: [2](#0-1) 

There is no oracle lookup, no reference to `pallet-oracle` (which exists elsewhere in this same codebase, see `substrate/frame/honzon/oracle/src/lib.rs`), and no deviation threshold anywhere in this pallet. The only safety mechanism is a manually-triggered `CircuitBreakerLevel` per external asset (`set_asset_status`), which requires an admin to observe the depeg and react: [3](#0-2) 

This is architecturally identical to the reported class of bug: an asset assumed to always be worth its peg target (WBTC≈BTC in the original report, external≈internal here) is priced/valued without any live market-price cross-check, so a depeg is not detected on-chain and the protocol keeps accepting/paying out the asset at stale par value.

### Impact Explanation
If any approved external asset depegs downward (e.g., a bridged/wrapped stablecoin loses its peg due to bridge compromise, reserve mismanagement, or a banking-crisis-style event as happened to USDC in March 2023), any unprivileged signed account can:
1. Call `mint` with the depegged external asset, receiving internal stablecoin at full 1:1 face value regardless of the asset's real market value.
2. Call `redeem` against a *different, still-healthy* external asset approved on the same PSM instance (if the instance has `MaxExternals > 1`), draining good collateral out of the reserve.

This leaves the PSM instance holding worthless/devalued external collateral while its internal-asset liabilities (and healthy-collateral reserves) are drained — directly causing bad debt and undercollateralization of the internal stablecoin, exactly the impact class described in the source report.

### Likelihood Explanation
The `mint`/`redeem` extrinsics are permissionless (`ensure_signed` only) — no special privilege is required to exploit a depeg once it occurs: [4](#0-3) [5](#0-4) 

The only mitigation is a reactive, governance-triggered circuit breaker (`set_asset_status`), meaning there is a window between depeg onset and admin intervention during which the exploit above is fully executable by any user holding the depegging asset. This mirrors the original report's own characterization — accepted by the judge as a valid Medium "given the edge case possibility of [asset] de-pegging" — since the external assets approved into a PSM (via `add_external_asset`, admin-gated) are still market-dependent third-party tokens outside the runtime's control, not something the runtime itself can guarantee to hold its peg.

### Recommendation
Integrate an oracle-based sanity check (e.g., consuming `pallet-oracle`'s `DataProvider`) into `mint`/`redeem` to reject or throttle swaps when the external asset's observed market price deviates from 1:1 beyond a governance-configured threshold, and/or add an automatic (non-discretionary) circuit breaker triggered by oracle-reported deviation rather than relying solely on manual admin action via `set_asset_status`.

### Proof of Concept
1. Governance creates a PSM for internal asset `USSD` and approves two externals via `add_external_asset`: `USDC` and `USDT`.
2. `USDC` depegs to $0.80 due to an external event (bridge/reserve issue) — this is undetectable by the pallet since there is no price check.
3. Attacker calls `Pallet::mint(origin, USSD, USDC, large_amount, max_fee)` — receives `USSD` at full 1:1 value for devalued `USDC` per the logic at [6](#0-5) .
4. Attacker immediately calls `Pallet::redeem(origin, USSD, USDT, internal_amount, max_fee)` to withdraw healthy `USDT` reserve 1:1 per [7](#0-6) , profiting the peg differential and leaving the PSM under-collateralized (holding only devalued `USDC`).

### Citations

**File:** substrate/frame/psm/src/lib.rs (L702-709)
```rust
		pub fn mint(
			origin: OriginFor<T>,
			internal_asset: T::AssetId,
			external_asset: T::AssetId,
			external_amount: BalanceOf<T>,
			max_fee: Permill,
		) -> DispatchResult {
			let who = ensure_signed(origin)?;
```

**File:** substrate/frame/psm/src/lib.rs (L716-751)
```rust
			let (ext_decimals, internal_decimals) =
				Self::ensure_decimals_match(&info, &internal_asset, &external_asset, &external)?;

			let internal_equivalent =
				Self::external_to_internal(external_amount, ext_decimals, internal_decimals)?;
			ensure!(!internal_equivalent.is_zero(), Error::<T>::AmountTooSmallAfterConversion);
			ensure!(internal_equivalent >= info.min_swap_amount, Error::<T>::BelowMinimumSwap);

			let effective_external =
				Self::internal_to_external(internal_equivalent, ext_decimals, internal_decimals)?;

			let fee_rate = MintingFee::<T>::get(&internal_asset, &external_asset);
			ensure!(fee_rate <= max_fee, Error::<T>::FeeTooHigh);
			let fee = fee_rate.mul_ceil(internal_equivalent);
			let internal_to_user = internal_equivalent.saturating_sub(fee);

			let current_total_psm_debt = Self::total_psm_debt(&internal_asset);
			ensure!(
				current_total_psm_debt.saturating_add(internal_equivalent) <= info.max_debt,
				Error::<T>::ExceedsMaxPsmDebt
			);

			let current_debt = PsmDebt::<T>::get(&internal_asset, &external_asset);
			let max_debt = Self::max_asset_debt(&internal_asset, &external_asset, &info);
			let new_debt = current_debt.saturating_add(internal_equivalent);
			ensure!(new_debt <= max_debt, Error::<T>::ExceedsMaxPsmDebt);

			let psm_account = Self::psm_account(&internal_asset);
			T::Fungibles::transfer(
				external_asset.clone(),
				&who,
				&psm_account,
				effective_external,
				Preservation::Expendable,
			)?;
			T::Fungibles::mint_into(internal_asset.clone(), &who, internal_to_user)?;
```

**File:** substrate/frame/psm/src/lib.rs (L811-818)
```rust
		pub fn redeem(
			origin: OriginFor<T>,
			internal_asset: T::AssetId,
			external_asset: T::AssetId,
			internal_amount: BalanceOf<T>,
			max_fee: Permill,
		) -> DispatchResult {
			let who = ensure_signed(origin)?;
```

**File:** substrate/frame/psm/src/lib.rs (L825-887)
```rust
			let ext_decimals = external.decimals;
			let internal_decimals = info.internal_decimals;

			ensure!(internal_amount >= info.min_swap_amount, Error::<T>::BelowMinimumSwap);

			let fee_rate = RedemptionFee::<T>::get(&internal_asset, &external_asset);
			ensure!(fee_rate <= max_fee, Error::<T>::FeeTooHigh);
			let fee = fee_rate.mul_ceil(internal_amount);
			let internal_net = internal_amount.saturating_sub(fee);

			let external_out =
				Self::internal_to_external(internal_net, ext_decimals, internal_decimals)?;
			ensure!(
				internal_net.is_zero() || !external_out.is_zero(),
				Error::<T>::AmountTooSmallAfterConversion
			);
			// `effective_internal_net` is the internal value that round-trips to `external_out`;
			// it is what we actually burn and what the tracked debt decreases by. Any truncation
			// dust stays in the caller's internal balance, symmetric with `mint`, which takes
			// only the round-tripped share of the external amount.
			let effective_internal_net =
				Self::external_to_internal(external_out, ext_decimals, internal_decimals)?;

			let current_debt = PsmDebt::<T>::get(&internal_asset, &external_asset);
			ensure!(current_debt >= effective_internal_net, Error::<T>::InsufficientReserve);

			let reserve = Self::get_reserve(&internal_asset, &external_asset);
			if reserve < external_out {
				defensive!("PSM reserve is less than expected output amount");
				return Err(Error::<T>::Unexpected.into());
			}

			if !fee.is_zero() {
				T::Fungibles::transfer(
					internal_asset.clone(),
					&who,
					&info.fee_destination,
					fee,
					Preservation::Expendable,
				)?;
			}

			if !effective_internal_net.is_zero() {
				T::Fungibles::burn_from(
					internal_asset.clone(),
					&who,
					effective_internal_net,
					Preservation::Expendable,
					Precision::Exact,
					Fortitude::Polite,
				)?;
			}

			let psm_account = Self::psm_account(&internal_asset);
			if !external_out.is_zero() {
				T::Fungibles::transfer(
					external_asset.clone(),
					&psm_account,
					&who,
					external_out,
					Preservation::Expendable,
				)?;
			}
```

**File:** substrate/frame/psm/src/lib.rs (L1188-1232)
```rust
		/// Set the circuit breaker per external asset on a PSM instance.
		///
		/// ## Dispatch Origin
		///
		/// Must match the PSM instance's `full_admin` or `emergency_admin`; either the
		/// `Full` or `Emergency` privilege level may use this call.
		///
		/// ## Parameters
		///
		/// - `internal_asset`: The PSM instance to configure.
		/// - `external_asset`: The external asset whose status is being updated.
		/// - `status`: The new circuit breaker level for that external.
		///
		/// ## Errors
		///
		/// - [`Error::AssetNotApproved`]: If `external_asset` is not approved on `internal_asset`.
		///
		/// ## Events
		///
		/// - [`Event::AssetStatusUpdated`]: Emitted on a successful update.
		#[pallet::call_index(7)]
		#[pallet::weight(T::WeightInfo::set_asset_status())]
		pub fn set_asset_status(
			origin: OriginFor<T>,
			internal_asset: T::AssetId,
			external_asset: T::AssetId,
			status: CircuitBreakerLevel,
		) -> DispatchResult {
			Self::ensure_psm_admin(origin, &internal_asset, |l| l.can_set_circuit_breaker())?;
			ExternalAssets::<T>::try_mutate(
				&internal_asset,
				&external_asset,
				|maybe| -> DispatchResult {
					let info = maybe.as_mut().ok_or(Error::<T>::AssetNotApproved)?;
					info.status = status;
					Ok(())
				},
			)?;
			Self::deposit_event(Event::AssetStatusUpdated {
				internal_asset,
				external_asset,
				status,
			});
			Ok(())
		}
```
