### Title
Disabled slippage control in `SwapFirstAssetTrader::refund_weight` swap-back - (File: `cumulus/primitives/utility/src/lib.rs`)

### Summary
`SwapFirstAssetTrader`, the XCM `WeightTrader` used by asset-hub/Penpal runtimes to let users pay execution fees in a non-native asset via `pallet_asset_conversion`, calls `SwapCredit::swap_exact_tokens_for_tokens` with `amount_out_min` hard-coded to `None` when refunding unused weight back into the original fee-paying asset. This mirrors the Pendle `_redeemPT` pattern where `minTokenOut` was hard-coded to `0`, disabling slippage protection on a value-bearing conversion.

### Finding Description
`buy_weight` swaps the client's asset into the `Target` asset using `swap_tokens_for_exact_tokens`, whose amount-in is implicitly bounded by the credit supplied, so it has natural slippage protection (it either gets `fee` exactly or fails) [1](#0-0) .

However, `refund_weight` extracts the unused portion of `total_fee` (already in `Target` asset) and swaps it back into the asset the user originally paid with, using `swap_exact_tokens_for_tokens` with the minimum-out parameter explicitly set to `None`: [2](#0-1) 

The underlying `pallet_asset_conversion::SwapCredit::swap_exact_tokens_for_tokens` trait explicitly supports an optional `amount_out_min` for exactly this purpose [3](#0-2) , and `do_swap_exact_credit_tokens_for_tokens` only enforces the minimum when `Some(_)` is supplied [4](#0-3) . By passing `None`, `refund_weight` accepts any amount of `refund_swap_asset`, however small, as long as the pool has any liquidity — exactly analogous to the Pendle report's `netTokenOut = SY.redeem(..., 0, true)` accepting any output.

The refunded credit is returned as XCM "unused weight" change and folded back into the holding register for the specific XCM message being executed (i.e., ultimately benefits the account whose message triggered `buy_weight`/`refund_weight`) [5](#0-4) . This trader is wired into production runtime configs, e.g. Asset Hub Westand and Penpal `XcmConfig::Trader` [6](#0-5) [7](#0-6) .

### Impact Explanation
If the underlying `AssetConversion` pool's price is unfavorably manipulated at the exact moment `refund_weight` executes (e.g., via a preceding/following swap against the same pool), the swap-back can return a value far below fair market value, and the code has no mechanism to reject or bound this loss. The value difference is captured by whoever manipulated the pool (classic sandwich/JIT-liquidity economics), while the account that receives the refund credit loses value relative to what it should have received. Because AMM-based swaps in `pallet_asset_conversion` are permissionless and reserves can be small/thin on a per-pool basis, the potential loss scales with pool depth and total_fee magnitude; unlike `buy_weight` (which is naturally bounded), `refund_weight`'s output is fully unconstrained.

### Likelihood Explanation
Exploitation requires an attacker to move the specific `(Target, refund_swap_asset)` pool's reserves unfavorably immediately around the processing of the victim's XCM message and later reverse the trade to capture the difference. Whether this is same-block sandwichable depends on transaction ordering relative to inherents (inbound HRMP/DMP processing typically happens as an inherent before extrinsics in the same block, limiting single-block front-running of inbound messages) versus locally-submitted `pallet_xcm::execute` calls by third parties (which are ordinary signed extrinsics and can, in principle, be reordered/sandwiched by a block producer or bundled attacker transactions, e.g. via `pallet_utility::batch_all`). This makes the attack more plausible for locally-initiated XCM executions that use this trader than for inbound cross-chain messages, and it also depends on pool liquidity depth. I could not fully verify block-authoring/inherent-ordering guarantees in this codebase within the scope of this review, so the exact same-block feasibility remains uncertain and should be validated with a concrete PoC before treating this as high severity.

### Recommendation
Do not pass `None` for the minimum-out parameter in `refund_weight`. Compute an acceptable lower bound (e.g., via `QuotePrice::quote_price_exact_tokens_for_tokens` at the time of refund, with a configurable tolerance) and pass `Some(min_amount)` to `SwapCredit::swap_exact_tokens_for_tokens`, falling back to returning the un-swapped `Target` asset (or failing the refund gracefully) if the quote cannot be met, consistent with how `pallet_asset_conversion`'s own extrinsics enforce `amount_out_min`.

### Proof of Concept
Not independently reproduced. A concrete PoC would need to: (1) set up an `AssetConversion` pool for `(Target, refund_swap_asset)` with realistic-but-thin liquidity in a runtime using `SwapFirstAssetTrader` (e.g., Penpal or Asset Hub testing runtime), (2) trigger an XCM execution path that leaves an unused-weight refund via `refund_weight` (e.g., over-estimated weight for a `Transact`/program executed with `pallet_xcm::execute`), and (3) interleave a manipulating swap (via `pallet_utility::batch_all` or adjacent extrinsics within the same block) immediately before/after the refund to demonstrate the refunded amount is materially below the pre-manipulation quoted price. This was not executed against the live codebase in this review; the finding is based on static code analysis of the missing `amount_out_min` bound at [8](#0-7) .

### Citations

**File:** cumulus/primitives/utility/src/lib.rs (L469-489)
```rust
		let fee = WeightToFee::weight_to_fee(&weight);
		// swap the user's asset for the `Target` asset.
		let (credit_out, credit_change) = match SwapCredit::swap_tokens_for_exact_tokens(
			vec![swap_asset, Target::get()],
			credit_in,
			fee,
		) {
			Ok(a) => a,
			Err((credit_in, error)) => {
				log::trace!(
					target: "xcm::weight",
					"SwapFirstAssetTrader::buy_weight swap couldn't be done. Error was: {:?}",
					error,
				);
				// put back the taken credit
				let taken =
					AssetsInHolding::new_from_fungible_credit(id.clone(), Box::new(credit_in));
				payment.subsume_assets(taken);
				return Err((payment, XcmError::FeesNotMet));
			},
		};
```

**File:** cumulus/primitives/utility/src/lib.rs (L539-562)
```rust
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

		let refund = AssetsInHolding::new_from_fungible_credit(refund_asset.id, Box::new(refund));
		Some(refund)
	}
```

**File:** substrate/frame/asset-conversion/src/swap.rs (L85-97)
```rust
	/// Swap exactly `credit_in` of asset `path[0]` for asset `path[last]`.  If `amount_out_min` is
	/// provided and the swap can't achieve at least this amount, an error is returned.
	///
	/// On a successful swap, the function returns the `credit_out` of `path[last]` obtained from
	/// the `credit_in`. On failure, it returns an `Err` containing the original `credit_in` and the
	/// associated error code.
	///
	/// This operation is expected to be atomic.
	fn swap_exact_tokens_for_tokens(
		path: Vec<Self::AssetKind>,
		credit_in: Self::Credit,
		amount_out_min: Option<Self::Balance>,
	) -> Result<Self::Credit, (Self::Credit, DispatchError)>;
```

**File:** substrate/frame/asset-conversion/src/lib.rs (L1092-1096)
```rust
				let amount_out = path.last().map(|(_, a)| *a).ok_or(Error::<T>::InvalidPath)?;
				ensure!(
					amount_out_min.map_or(true, |a| amount_out >= a),
					Error::<T>::ProvidedMinimumNotSufficientForSwap
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
