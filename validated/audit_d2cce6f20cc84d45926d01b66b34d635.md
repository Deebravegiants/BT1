### Title
Unprotected AMM swap with no slippage/minimum-output check in `add_tip` / `register_token` enables sandwich-style price manipulation - (File: `bridges/snowbridge/pallets/system-frontend/src/lib.rs`)

### Summary
The `snowbridge-pallet-system-frontend` pallet's `add_tip` and `register_token` extrinsics swap a caller-supplied fee/tip asset for Ether through `pallet-asset-conversion` and then burn/report the resulting Ether amount to the Ethereum bridge for relayer reward accounting. The swap is executed with `amount_out_min` hard-coded to `None`, disabling all slippage protection, exactly the missing-slippage-control pattern described in the external `BuyAndBurn.swap()` report.

### Finding Description
`swap_and_burn` performs the token conversion: [1](#0-0) 

Note the explicit comment `// No minimum amount required` at line 305, meaning `T::Swap::swap_exact_tokens_for_tokens` (backed by `pallet-asset-conversion`) is invoked without any `amount_out_min`, so the swap will always succeed at whatever spot price the pool currently offers, however unfavorable/favorable.

This function is reachable from two publicly/signed-callable extrinsics:
- `add_tip`, callable by any signed account, which swaps a caller-supplied `asset` for Ether and reports the resulting amount as a relayer reward tip on Ethereum: [2](#0-1) 
- `register_token`, allowed for any origin that owns the nested asset location, which similarly swaps `fee_asset` for Ether before dispatching the registration call with the `ether_gained` amount embedded: [3](#0-2) 

`pallet-asset-conversion`'s underlying swap correctly supports an `amount_out_min` guard (`Error::ProvidedMinimumNotSufficientForSwap`), but this pallet deliberately opts out of it: [4](#0-3) 

Because `T::Swap` resolves to the public `AssetConversion` liquidity pool for the `(tip_asset, ether)` pair (a permissionless, price-manipulable AMM), and the caller fully controls the timing of their own `add_tip`/`register_token` call, an attacker can move the pool's spot price immediately before the call (e.g., by selling Ether into the pool to cheapen it relative to the tip asset), execute `add_tip` to receive an inflated `ether_gained` for a fixed `tip_amount`, then reverse the price-moving trade afterward to recapture most of the capital. This is structurally the same class of issue as the reported `BuyAndBurn.swap()` finding: a value-moving operation that swaps through a public AMM pool with no minimum-output/slippage bound, executable atomically alongside attacker-controlled trades against that same pool.

### Impact Explanation
The `ether_gained` value is not just an internal accounting figure — it is forwarded to the Ethereum-side `EthereumSystem::add_tip`/`register_token` calls as the amount used to compute relayer rewards and registration fees. An attacker who manipulates the AMM price in the same transaction can extract value from the `AssetConversion` pool's liquidity providers while inflating the reported Ether tip/fee amount relative to what they actually paid in fair-market terms, distorting the bridge's fee/reward accounting at LP expense.

### Likelihood Explanation
Both `add_tip` (any signed account) and `register_token` (any qualifying origin) are unprivileged, directly reachable entry points with no admin gating on the swap step, and the `pallet-asset-conversion` AMM pools are themselves permissionlessly tradable. An attacker only needs the ability to trade in the relevant `(tip_asset, ether)` pool and to bundle trades atomically (e.g., via a single extrinsic batch or same-block ordering), which is realistic for any user.

### Recommendation
Add an explicit minimum-output (`amount_out_min`) parameter to `add_tip`/`register_token`, or compute one internally via `QuotePrice`/`quote_price_exact_tokens_for_tokens` with an acceptable tolerance, instead of passing `None` to `swap_exact_tokens_for_tokens` in `swap_and_burn`.

### Proof of Concept
1. Attacker identifies the `AssetConversion` pool for `(tip_asset, EthereumLocation)` used by `swap_and_burn`.
2. In one atomic sequence (batched extrinsics or adjacent transactions within the same block), the attacker:
   a. Swaps Ether into the pool via `AssetConversion::swap_exact_tokens_for_tokens`, cheapening Ether relative to `tip_asset`.
   b. Calls `SystemFrontend::add_tip(message_id, asset)` with their `tip_asset`; because `swap_and_burn` passes `amount_out_min: None` (line 305), the swap executes at the manipulated price and returns an inflated `ether_gained`, which is burned and reported to Ethereum as the tip value.
   c. Reverses the initial trade to restore the pool price and recover most of the capital used in step (a).
3. The attacker obtains a larger reported/burned Ether tip for the same `tip_amount` than fair-market pricing would allow, extracting value from the pool's liquidity providers.

### Citations

**File:** bridges/snowbridge/pallets/system-frontend/src/lib.rs (L225-252)
```rust
		pub fn register_token(
			origin: OriginFor<T>,
			asset_id: Box<VersionedLocation>,
			metadata: AssetMetadata,
			fee_asset: Asset,
		) -> DispatchResult {
			ensure!(!Self::export_operating_mode().is_halted(), Error::<T>::Halted);

			let asset_location: Location =
				(*asset_id).try_into().map_err(|_| Error::<T>::UnsupportedLocationVersion)?;
			let origin_location = T::RegisterTokenOrigin::ensure_origin(origin, &asset_location)?;

			let ether_gained = if origin_location.is_here() {
				// Root origin/location does not pay any fees/tip.
				0
			} else {
				Self::swap_fee_asset_and_burn(origin_location.clone(), fee_asset)?
			};

			let call = Self::build_register_token_call(
				origin_location.clone(),
				asset_location,
				metadata,
				ether_gained,
			)?;

			Self::send_transact_call(origin_location, call)
		}
```

**File:** bridges/snowbridge/pallets/system-frontend/src/lib.rs (L254-273)
```rust
		/// Add an additional relayer tip for a committed message identified by `message_id`.
		/// The tip asset will be swapped for ether.
		#[pallet::call_index(2)]
		#[pallet::weight(
			T::WeightInfo::add_tip()
				.saturating_add(T::BackendWeightInfo::transact_add_tip())
		)]
		pub fn add_tip(origin: OriginFor<T>, message_id: MessageId, asset: Asset) -> DispatchResult
		where
			<T as frame_system::Config>::AccountId: Into<Location>,
		{
			let who = ensure_signed(origin)?;

			let ether_gained = Self::swap_fee_asset_and_burn(who.clone().into(), asset)?;

			// Send the tip details to BH to be allocated to the reward in the Inbound/Outbound
			// pallet
			let call = Self::build_add_tip_call(who.clone(), message_id.clone(), ether_gained);
			Self::send_transact_call(who.into(), call)
		}
```

**File:** bridges/snowbridge/pallets/system-frontend/src/lib.rs (L290-317)
```rust
		fn swap_and_burn(
			origin: Location,
			tip_asset_location: Location,
			ether_location: Location,
			tip_amount: u128,
		) -> Result<u128, DispatchError> {
			// Swap tip asset to ether
			let swap_path = vec![tip_asset_location.clone(), ether_location.clone()];
			let who = T::AccountIdConverter::convert_location(&origin)
				.ok_or(Error::<T>::LocationConversionFailed)?;

			let ether_gained = T::Swap::swap_exact_tokens_for_tokens(
				who.clone(),
				swap_path,
				tip_amount,
				None, // No minimum amount required
				who,
				true,
			)?;

			// Burn the ether
			let ether_asset = Asset::from((ether_location.clone(), ether_gained));

			burn_for_teleport::<T::AssetTransactor>(&origin, &ether_asset)
				.map_err(|_| Error::<T>::BurnError)?;

			Ok(ether_gained)
		}
```

**File:** substrate/frame/asset-conversion/src/lib.rs (L988-1002)
```rust
			ensure!(amount_in > Zero::zero(), Error::<T>::ZeroAmount);
			if let Some(amount_out_min) = amount_out_min {
				ensure!(amount_out_min > Zero::zero(), Error::<T>::ZeroAmount);
			}

			Self::validate_swap_path(&path)?;
			let path = Self::balance_path_from_amount_in(amount_in, path)?;

			let amount_out = path.last().map(|(_, a)| *a).ok_or(Error::<T>::InvalidPath)?;
			if let Some(amount_out_min) = amount_out_min {
				ensure!(
					amount_out >= amount_out_min,
					Error::<T>::ProvidedMinimumNotSufficientForSwap
				);
			}
```
