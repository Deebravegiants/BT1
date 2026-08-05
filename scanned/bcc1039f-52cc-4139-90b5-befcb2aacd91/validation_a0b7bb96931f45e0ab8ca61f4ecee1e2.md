## Analysis Summary

I found a direct analog to the reported rETH sandwich vulnerability in `pallet-asset-conversion`'s consumer code within the XCM fee-handling logic. Below is the finding. [1](#0-0) 

### Title
Unprotected spot-price AMM swap in `SwapFirstAssetTrader::refund_weight` enables sandwich extraction on XCM fee refunds - (File: `cumulus/primitives/utility/src/lib.rs`)

### Summary
`SwapFirstAssetTrader`, the `WeightTrader` implementation used by Asset Hub (Rococo/Westend) and Penpal to let users pay XCM execution fees in non-native assets, swaps unused fee credit back to the original payment asset in `refund_weight` by calling `SwapCredit::swap_exact_tokens_for_tokens(..., None)` — passing `None` for `amount_out_min`. This is functionally identical to the reported rETH issue: an AMM swap is executed at the pool's current spot price with **no slippage/minimum-output protection**, making it sandwichable.

### Finding Description
`buy_weight` withdraws the user's asset and swaps a bounded amount for exactly the `fee` needed via `swap_tokens_for_exact_tokens` (which does have an implicit bound because it targets an exact output). However, `refund_weight` swaps the *unused portion of the fee* back into the asset the user originally paid with, using the unbounded variant: [2](#0-1) 

```rust
let refund = self.total_fee.extract(refund_amount);
let refund = match SwapCredit::swap_exact_tokens_for_tokens(
    vec![Target::get(), refund_swap_asset],
    refund,
    None,   // <-- no amount_out_min supplied
) { ... }
```

The underlying `pallet_asset_conversion::Pallet::do_swap_exact_credit_tokens_for_tokens` only checks the minimum when one is supplied: [3](#0-2) 

With `amount_out_min = None`, the check is skipped entirely and the swap accepts whatever `get_amount_out` produces from the *current* pool reserves — the same constant-product spot-price formula used in the AMM (`get_amount_out`): [4](#0-3) 

`SwapFirstAssetTrader` is wired into production runtime configs, not just tests: [5](#0-4) [6](#0-5) [7](#0-6) [8](#0-7) 

This means: whenever an XCM message pays fees with a non-native, pool-tradeable asset and the executor's `WeightLimit` purchase exceeds actual weight consumed (the normal case — a fee refund happens for essentially every XCM message processed this way), a spot-price swap with zero slippage protection is executed against a public, permissionless AMM pool (`pallet-asset-conversion`), which anyone can add liquidity to or trade against.

### Impact Explanation
An attacker who can predict/observe that an incoming XCM message will trigger this refund path can manipulate the relevant asset/native pool's reserves immediately beforehand (skew the price against the refund direction), let the unprotected swap execute at the manipulated price (extracting value from the refund recipient / the pool), then reverse their trade to lock in profit — precisely the sandwich pattern described in the source report. Because there is no `amount_out_min`, the swap cannot fail no matter how unfavorable the price is, unlike `buy_weight`'s exact-output variant, which is naturally bounded.

### Likelihood Explanation
The profit is capped by the size of the fee refund (typically a small fraction of the purchased weight-fee), which limits attractiveness against deep, well-arbitraged pools such as the native DOT/USDT/USDC pools on Asset Hub. However:
- Any permissionless user can create a shallow pool for a new asset and use that asset to pay XCM fees, directly controlling pool depth and thus the price impact/sandwich profitability.
- The swap executes deterministically against on-chain reserves with a well-known formula, so the manipulated price and resulting refund shortfall/attacker profit are fully computable in advance — same as the cited PoC.
- The overall attack requires the attacker to place trades in blocks surrounding the block that processes the inbound XCM message (this is a normal, unprivileged sandwich pattern already applicable to any AMM swap on this chain, not something requiring elevated privilege).

This is a real but bounded-value griefing/MEV vector rather than a large fund-drain; severity should track the size of feasible refunds and pool depths a user can create, similar to the original "High" rating being tied to attacker-controllable pool skew.

### Recommendation
Pass a real `amount_out_min` in `refund_weight` (e.g., derive it from `QuotePrice`/`quote_price_exact_tokens_for_tokens` at the time of `buy_weight`, adjusted by a bounded slippage tolerance) instead of `None`, mirroring the protection already present in `swap_tokens_for_exact_tokens` used in `buy_weight`. Alternatively, avoid a live-pool swap for small refunds (e.g., only refund in `Target` asset, or skip refund below a threshold) to remove the sandwichable code path altogether.

### Proof of Concept
1. Attacker permissionlessly creates a `pallet-asset-conversion` pool for `(Target, X)` with minimal liquidity (bounded only by `MintMinLiquidity`).
2. Attacker (or a colluding party) sends an XCM message that pays execution fees in `X`, triggering `SwapFirstAssetTrader::buy_weight` then `refund_weight` for the unused weight.
3. In the block(s) surrounding this message's processing, the attacker swaps against the `(Target, X)` pool to shift the spot price unfavorably for the upcoming `refund_weight` call — since `swap_exact_tokens_for_tokens(..., None)` has no minimum-output check (confirmed at [3](#0-2) ), the refund executes regardless of how unfavorable the price is.
4. Attacker reverses their trade after the refund settles, capturing the price-impact spread as profit, exactly as in the rETH PoC math (buy low pre-manipulation, force victim swap through skewed price, sell back).

### Citations

**File:** cumulus/primitives/utility/src/lib.rs (L512-558)
```rust
	fn refund_weight(&mut self, weight: Weight, _context: &XcmContext) -> Option<AssetsInHolding> {
		log::trace!(
			target: "xcm::weight",
			"SwapFirstAssetTrader::refund_weight weight: {:?}, self.total_fee: {:?}",
			weight,
			self.total_fee,
		);
		if weight.is_zero() || self.total_fee.peek().is_zero() {
			// noting to refund.
			return None;
		}
		let refund_asset = if let Some(asset) = &self.last_fee_asset {
			// create an initial zero refund in the asset used in the last `buy_weight`.
			(asset.clone(), Fungible(0)).into()
		} else {
			return None;
		};
		let refund_amount = WeightToFee::weight_to_fee(&weight);
		if refund_amount >= self.total_fee.peek() {
			// not enough was paid to refund the `weight`.
			return None;
		}

		let refund_swap_asset = FungiblesAssetMatcher::matches_fungibles(&refund_asset)
			.map(|(a, _)| a.into())
			.ok()?;

		let refund = self.total_fee.extract(refund_amount);
		let refund = match SwapCredit::swap_exact_tokens_for_tokens(
			vec![Target::get(), refund_swap_asset],
			refund,
			None,
		) {
			Ok(refund_in_target) => refund_in_target,
			Err((refund, _)) => {
				// return an attempted refund back to the `total_fee`.
				let _ = self.total_fee.subsume(refund).map_err(|refund| {
					// error may occur if `total_fee.asset` differs from `refund.asset`, which does
					// not apply in this context.
					defensive!(
						"`total_fee.asset` must be equal to `refund.asset`",
						(self.total_fee.asset(), refund.asset())
					);
				});
				return None;
			},
		};
```

**File:** substrate/frame/asset-conversion/src/lib.rs (L1086-1096)
```rust
				ensure!(!amount_in.is_zero(), Error::<T>::ZeroAmount);
				ensure!(amount_out_min.map_or(true, |a| !a.is_zero()), Error::<T>::ZeroAmount);

				Self::validate_swap_path(&path)?;
				let path = Self::balance_path_from_amount_in(amount_in, path)?;

				let amount_out = path.last().map(|(_, a)| *a).ok_or(Error::<T>::InvalidPath)?;
				ensure!(
					amount_out_min.map_or(true, |a| amount_out >= a),
					Error::<T>::ProvidedMinimumNotSufficientForSwap
				);
```

**File:** substrate/frame/asset-conversion/src/lib.rs (L1388-1419)
```rust
		pub fn get_amount_out(
			fee: Permill,
			amount_in: &T::Balance,
			reserve_in: &T::Balance,
			reserve_out: &T::Balance,
		) -> Result<T::Balance, Error<T>> {
			let amount_in = T::HigherPrecisionBalance::from(*amount_in);
			let reserve_in = T::HigherPrecisionBalance::from(*reserve_in);
			let reserve_out = T::HigherPrecisionBalance::from(*reserve_out);

			if reserve_in.is_zero() || reserve_out.is_zero() {
				return Err(Error::<T>::ZeroLiquidity);
			}

			let fee_complement = fee.left_from_one().deconstruct();
			let amount_in_with_fee = amount_in
				.checked_mul(&T::HigherPrecisionBalance::from(fee_complement))
				.ok_or(Error::<T>::Overflow)?;

			let numerator =
				amount_in_with_fee.checked_mul(&reserve_out).ok_or(Error::<T>::Overflow)?;

			let denominator = reserve_in
				.checked_mul(&T::HigherPrecisionBalance::from(Permill::ACCURACY))
				.ok_or(Error::<T>::Overflow)?
				.checked_add(&amount_in_with_fee)
				.ok_or(Error::<T>::Overflow)?;

			let result = numerator.checked_div(&denominator).ok_or(Error::<T>::Overflow)?;

			result.try_into().map_err(|_| Error::<T>::Overflow)
		}
```

**File:** cumulus/parachains/runtimes/assets/asset-hub-rococo/src/xcm_config.rs (L370-394)
```rust
	type Trader = (
		UsingComponents<
			WeightToFee,
			TokenLocation,
			AccountId,
			Balances,
			ResolveTo<StakingPot, Balances>,
		>,
		cumulus_primitives_utility::SwapFirstAssetTrader<
			TokenLocation,
			crate::AssetConversion,
			WeightToFee,
			crate::NativeAndNonPoolAssets,
			(
				TrustBackedAssetsAsLocation<
					TrustBackedAssetsPalletLocation,
					Balance,
					xcm::v5::Location,
				>,
				ForeignAssetsConvertedConcreteId,
			),
			ResolveAssetTo<StakingPot, crate::NativeAndNonPoolAssets>,
			AccountId,
		>,
	);
```

**File:** cumulus/parachains/runtimes/assets/asset-hub-westend/src/xcm_config.rs (L446-470)
```rust
	type Trader = (
		UsingComponents<
			WeightToFee,
			WestendLocation,
			AccountId,
			Balances,
			ResolveTo<StakingPot, Balances>,
		>,
		cumulus_primitives_utility::SwapFirstAssetTrader<
			WestendLocation,
			crate::AssetConversion,
			WeightToFee,
			crate::NativeAndNonPoolAssets,
			(
				TrustBackedAssetsAsLocation<
					TrustBackedAssetsPalletLocation,
					Balance,
					xcm::v5::Location,
				>,
				ForeignAssetsConvertedConcreteId,
			),
			ResolveAssetTo<StakingPot, crate::NativeAndNonPoolAssets>,
			AccountId,
		>,
	);
```

**File:** cumulus/parachains/runtimes/testing/penpal/src/xcm_config.rs (L399-413)
```rust
	type Trader = (
		// Allow native asset to pay the execution fee
		UsingComponents<WeightToFee, PenpalNativeCurrency, AccountId, Balances, ToAuthor<Runtime>>,
		// This trader allows to pay with any assets exchangeable to native asset with
		// [`AssetConversion`].
		cumulus_primitives_utility::SwapFirstAssetTrader<
			PenpalNativeCurrency,
			crate::AssetConversion,
			WeightToFee,
			crate::NativeAndAssets,
			(LocalAssetsConvertedConcreteId, ForeignAssetsConvertedConcreteId),
			ResolveAssetTo<StakingPot, crate::NativeAndAssets>,
			AccountId,
		>,
	);
```

**File:** substrate/frame/staking-async/runtimes/parachain/src/xcm_config.rs (L404-427)
```rust
	type Trader = (
		UsingComponents<
			WeightToFee,
			WestendLocation,
			AccountId,
			Balances,
			ResolveTo<StakingPot, Balances>,
		>,
		cumulus_primitives_utility::SwapFirstAssetTrader<
			WestendLocation,
			crate::AssetConversion,
			WeightToFee,
			crate::NativeAndNonPoolAssets,
			(
				TrustBackedAssetsAsLocation<
					TrustBackedAssetsPalletLocation,
					Balance,
					xcm::v5::Location,
				>,
				ForeignAssetsConvertedConcreteId,
			),
			ResolveAssetTo<StakingPot, crate::NativeAndNonPoolAssets>,
			AccountId,
		>,
```
