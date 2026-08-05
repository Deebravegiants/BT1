## Analog Found: Missing Slippage Protection in `SwapFirstAssetTrader::refund_weight`

### Title
Missing slippage protection (`amount_out_min: None`) in `SwapFirstAssetTrader::refund_weight` swap-back of unused XCM execution fees — ([File: cumulus/primitives/utility/src/lib.rs])

### Summary
`SwapFirstAssetTrader` is a `WeightTrader` implementation used by several production runtimes (Asset Hub Rococo, Asset Hub Westend, Penpal) to let XCM senders pay execution fees in a non-native asset by swapping it through `pallet-asset-conversion` into the runtime's target fee asset. While the fee-collection path (`buy_weight`) and the analogous refund path in `pallet-asset-conversion-tx-payment` both correctly enforce a minimum-output/quoted bound on their swaps, the unused-weight refund path (`refund_weight`) performs its reverse swap with no slippage bound at all, mirroring the exact defect described in ASTRO-22 (a swap executed with a hardcoded/absent minimum-output parameter).

### Finding Description
`SwapFirstAssetTrader::buy_weight` swaps the sender's asset into the `Target` fee asset using `swap_tokens_for_exact_tokens`, which by construction bounds the output to an exact `fee` amount — this path is safe from slippage manipulation of the received amount. [1](#0-0) 

However, `refund_weight`, which swaps any unused portion of the collected `Target` fee back into the asset the sender originally supplied (so it can be returned to them), calls `SwapCredit::swap_exact_tokens_for_tokens` with `None` as `amount_out_min`: [2](#0-1) 

Passing `None` disables the `amount_out_min` check entirely inside `pallet_asset_conversion`'s swap logic — the same check that exists specifically to prevent this class of issue: [3](#0-2) 

By contrast, the equivalent refund logic in `pallet-asset-conversion-tx-payment::correct_and_deposit_fee` deliberately quotes the expected refund and passes it as `Some(refund_asset_amount)` to enforce a floor: [4](#0-3) 

This shows the codebase's own established pattern for safe refunds — a pattern `SwapFirstAssetTrader::refund_weight` does not follow.

`SwapFirstAssetTrader` is wired into real runtime XCM configurations, not just test code: [5](#0-4) 
(see also `asset-hub-westend/src/xcm_config.rs`, `penpal/src/xcm_config.rs`, `substrate/frame/staking-async/runtimes/parachain/src/xcm_config.rs`).

### Impact Explanation
Any unprivileged XCM sender who pays execution fees via `SwapFirstAssetTrader` in a non-`Target` asset and overestimates the required weight (e.g. sets `BuyExecution` weight limit higher than actually consumed) triggers `refund_weight`. The unspent portion is swapped back to the sender's asset with no floor, so a third party who observes the pending message (e.g. a block producer or mempool watcher) can manipulate the pool's spot price (sandwich attack) immediately before this swap executes, causing the sender to receive a reduced refund while the attacker/LP captures the difference. This directly matches the reported vulnerability class: value extraction from an un-bounded swap embedded in a cross-chain fee-settlement flow.

### Likelihood Explanation
Reachable by any unprivileged party constructing an XCM message that (a) uses a non-`Target` asset for `BuyExecution`/fee payment through `SwapFirstAssetTrader`, and (b) leaves any unused weight (common, since weight limits are typically set conservatively above actual consumption). No privileged role or trusted origin is required to trigger the vulnerable code path; only pool price manipulation around the block containing the refund is needed, which is a standard MEV/sandwich technique against AMM pools of the kind `pallet-asset-conversion` implements.

### Recommendation
Change `refund_weight` to compute an expected refund amount via `QuotePrice::quote_price_exact_tokens_for_tokens` (as already done in `pallet-asset-conversion-tx-payment::correct_and_deposit_fee`) and pass `Some(minimum_amount)` (e.g. quoted amount minus an acceptable tolerance) instead of `None` to `SwapCredit::swap_exact_tokens_for_tokens`. If no acceptable minimum can be established, the refund swap should be skipped and the leftover `Target` asset credited via `OnUnbalanced` instead of exposing the sender to unbounded price impact.

### Proof of Concept
1. Configure a runtime with `SwapFirstAssetTrader` as (part of) its `WeightTrader`, with an asset-conversion pool between `Target` (e.g. native token) and asset `X` with modest liquidity.
2. Sender submits an XCM message using asset `X` to pay fees via `BuyExecution` with a weight limit well above actual usage, causing `buy_weight` to swap `X`→`Target` for the quoted fee.
3. Before/around the block executing this message, an attacker trades against the `X`/`Target` pool to skew its price unfavorably for a `Target`→`X` swap.
4. At the end of execution, `refund_weight` swaps the unused `Target` credit back to `X` via `swap_exact_tokens_for_tokens(..., None)` — since there is no floor, the sender receives an arbitrarily reduced amount of `X`, with the difference captured by the attacker/pool, matching the `bridgeFunds`-style "zero minimum output" defect in the external report.

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

**File:** cumulus/primitives/utility/src/lib.rs (L539-558)
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

**File:** cumulus/parachains/runtimes/assets/asset-hub-rococo/src/xcm_config.rs (L1-1)
```rust
// Copyright (C) Parity Technologies (UK) Ltd.
```
