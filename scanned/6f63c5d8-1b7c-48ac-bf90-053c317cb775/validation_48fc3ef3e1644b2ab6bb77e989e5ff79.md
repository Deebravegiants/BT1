### Title
Unprotected sUSDe-style swap-and-burn allows MEV sandwich attack on `add_tip`/`register_token` tip conversion - (File: `bridges/snowbridge/pallets/system-frontend/src/lib.rs`)

### Summary
The `pallet-snowbridge-system-frontend`'s `swap_and_burn` function converts a user-supplied tip/fee asset into Ether via `AssetConversion::swap_exact_tokens_for_tokens` with **no minimum output amount** (`None` is passed explicitly for `amount_out_min`), then unconditionally burns whatever Ether is returned for teleport to Ethereum. This is the same root cause pattern as the reported Ethena `_sellStakedUSDe` bug: a swap leg executed with zero slippage protection, whose output is trusted and consumed downstream without any sanity check.

### Finding Description
`swap_and_burn` is called from `swap_fee_asset_and_burn`, which itself is invoked from the public extrinsics `register_token` and `add_tip`: [1](#0-0) [2](#0-1) 

Both extrinsics are callable by any signed origin (`add_tip`) or by any origin owning the asset location (`register_token`), and both accept an arbitrary user-chosen `fee_asset`/`asset` whose `Location` becomes the swap path's first hop: [3](#0-2) 

The actual swap is performed here, with the slippage parameter hard-coded to `None`: [4](#0-3) 

This directly mirrors the sponsor bug: the underlying `AssetConversion::swap_exact_tokens_for_tokens` / `do_swap_exact_tokens_for_tokens` fully supports an `amount_out_min` check (`ProvidedMinimumNotSufficientForSwap`) when `Some` is supplied [5](#0-4) , but `swap_and_burn` deliberately opts out of it by passing `None`, comment: `// No minimum amount required`. Unlike the Ethena report's second-leg conditional check, here there is *no* leg at all that enforces slippage — the swap output (`ether_gained`) is taken as-is and passed straight to `burn_for_teleport`, with no post-swap validation against an expected/quoted price.

Because on-chain AMM pools (via `pallet-asset-conversion`) are public, permissionless, and price-manipulable within a single block via other extrinsics in the transaction pool, an attacker can:
1. Observe a pending `add_tip`/`register_token` call in the mempool with a sizeable `fee_asset`/tip amount.
2. Front-run it by swapping into the pool to move the price of `tip_asset_location -> ether_location` unfavorably.
3. Let the victim's swap execute at the manipulated price, receiving far less `ether_gained` than the fair-market rate.
4. Back-run by swapping back to restore price and capture the difference.

### Impact Explanation
The user's supplied tip/fee asset can be effectively drained by sandwich attackers, resulting in significantly less (or negligible) Ether being burned/registered/tipped than intended. Since `ether_gained` also feeds into `build_register_token_call`'s `amount` parameter and the relayer reward tip amount in `add_tip`, victims lose value directly (fee asset consumed) while receiving degraded downstream behavior (under-tipped relayers, under-funded token registration) — a direct loss-of-funds condition analogous to the referenced report.

### Likelihood Explanation
High for any signed account calling `add_tip` or non-root callers of `register_token` with a `fee_asset` that is not already the `EthereumLocation` asset, provided a pool exists between that asset and Ether via `pallet-asset-conversion`/`T::Swap`. No privileged role is required — these are ordinary user-facing extrinsics with unpermissioned origins (`ensure_signed` / `RegisterTokenOrigin` checking only asset ownership, not trust). MEV sandwiching of on-chain AMM swaps within a single block via transaction ordering is a well-established, realistic attack pattern.

### Recommendation
Add an explicit `min_ether_out` (or equivalent slippage) parameter to `register_token`/`add_tip`/`swap_and_burn`, and pass `Some(min_ether_out)` into `T::Swap::swap_exact_tokens_for_tokens` instead of hard-coded `None`, so the call fails with `ProvidedMinimumNotSufficientForSwap` rather than silently accepting a manipulated price. Alternatively, use `quote_price_exact_tokens_for_tokens` to compute an expected value and enforce a maximum acceptable deviation before burning.

### Proof of Concept
Conceptual reproduction (would require a Devin session with the runtime test harness to execute end-to-end):
1. In a test runtime with `pallet-asset-conversion` configured as `T::Swap` and a pool created between `TIP_ASSET` and `ETHER_ASSET` with modest liquidity.
2. Attacker account front-runs by swapping a large amount of `TIP_ASSET` into the pool to skew the price against `TIP_ASSET -> ETHER_ASSET`.
3. Victim calls `add_tip(origin, message_id, Asset { id: TIP_ASSET, fun: Fungible(tip_amount) })`, which triggers `swap_and_burn` with `amount_out_min = None`; the swap executes at the skewed price and returns a much lower `ether_gained` than at the pre-attack price.
4. Attacker back-runs, restoring the pool price and net-capturing the spread.
5. Assert that `ether_gained` (and hence the value burned/tipped) is far below the fair-value quote obtainable via `quote_price_exact_tokens_for_tokens` prior to the attacker's front-run trade, demonstrating measurable value loss to the victim.

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

**File:** bridges/snowbridge/pallets/system-frontend/src/lib.rs (L261-273)
```rust
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

**File:** bridges/snowbridge/pallets/system-frontend/src/lib.rs (L372-404)
```rust
		fn swap_fee_asset_and_burn(
			origin: Location,
			fee_asset: Asset,
		) -> Result<u128, DispatchError> {
			let ether_location = T::EthereumLocation::get();
			let (fee_asset_location, fee_amount) = match fee_asset {
				Asset { id: AssetId(ref loc), fun: Fungible(amount) } => (loc, amount),
				_ => {
					tracing::debug!(target: LOG_TARGET, ?fee_asset, "error matching fee asset");
					return Err(Error::<T>::UnsupportedAsset.into());
				},
			};
			if fee_amount == 0 {
				return Ok(0);
			}

			let ether_gained = if *fee_asset_location != ether_location {
				Self::swap_and_burn(
					origin.clone(),
					fee_asset_location.clone(),
					ether_location,
					fee_amount,
				)
				.inspect_err(|&e| {
					tracing::debug!(target: LOG_TARGET, ?e, "error swapping asset");
				})?
			} else {
				burn_for_teleport::<T::AssetTransactor>(&origin, &fee_asset)
					.map_err(|_| Error::<T>::BurnError)?;
				fee_amount
			};
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
