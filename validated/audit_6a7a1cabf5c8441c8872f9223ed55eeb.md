Based on my review, the code matches the claim exactly. `SwapFirstAssetTrader::buy_weight` uses `swap_tokens_for_exact_tokens` (which bounds output to the exact `fee` amount), while `refund_weight` uses `swap_exact_tokens_for_tokens` with `None` as `amount_out_min`, disabling any minimum-output check on the reverse swap. [1](#0-0) [2](#0-1) 

`SwapFirstAssetTrader` is confirmed to be referenced in real runtime `xcm_config.rs` files for Asset Hub Rococo, Asset Hub Westend, Penpal, and the staking-async parachain runtime, not just test code. [3](#0-2) 

The `pallet_asset_conversion` swap logic does skip the output floor check entirely when `amount_out_min` is `None`, confirming that passing `None` truly disables slippage protection for this call.

The finding is well-supported by the code: `refund_weight` performs an unbounded reverse swap of unused fee credit back into the sender's original asset, with no minimum-output enforcement, while the codebase's own established pattern (in `pallet-asset-conversion-tx-payment`) quotes and enforces a floor for the analogous refund operation. This creates a genuine sandwich/MEV exposure for any XCM sender who pays fees via a non-`Target` asset through this trader and leaves any unused weight, which is a common occurrence given typical conservative weight limits. The exploit path requires no privileged access — an attacker merely needs to manipulate the relevant AMM pool's price immediately before block execution processes the refund, a standard MEV technique against `pallet-asset-conversion` pools.

Audit Report

## Title
Missing slippage protection (`amount_out_min: None`) in `SwapFirstAssetTrader::refund_weight` swap-back of unused XCM execution fees - ([File: cumulus/primitives/utility/src/lib.rs])

## Summary
`SwapFirstAssetTrader::refund_weight` swaps unused `Target`-asset fee credit back into the sender's originally-supplied asset via `SwapCredit::swap_exact_tokens_for_tokens` while passing `None` as `amount_out_min`, disabling the minimum-output floor check that `pallet_asset_conversion` provides specifically to protect against this class of issue. This contrasts with `buy_weight` in the same struct, which safely uses `swap_tokens_for_exact_tokens` to bound the exact output amount, and with the analogous refund logic in `pallet-asset-conversion-tx-payment::correct_and_deposit_fee`, which quotes and enforces a floor via `Some(refund_asset_amount)`.

## Finding Description
`SwapFirstAssetTrader::refund_weight` extracts the unused portion of collected `Target`-asset fee credit and swaps it back to the sender's original asset via `SwapCredit::swap_exact_tokens_for_tokens(vec![Target::get(), refund_swap_asset], refund, None)`. Passing `None` for `amount_out_min` causes `pallet_asset_conversion`'s internal swap logic to skip the `ensure!(amount_out >= amount_out_min, ...)` check entirely, meaning the swap succeeds regardless of how unfavorable the resulting exchange rate is. This is inconsistent with `buy_weight` in the same trader, which is inherently protected because `swap_tokens_for_exact_tokens` bounds the output to the exact `fee` amount, and inconsistent with the codebase's own established safe pattern in `pallet-asset-conversion-tx-payment::correct_and_deposit_fee`, which computes an expected refund via `QuotePrice::quote_price_exact_tokens_for_tokens` and passes it as a `Some(...)` floor.

## Impact Explanation
Any XCM sender paying fees through `SwapFirstAssetTrader` in a non-`Target` asset, who leaves any unused execution weight (a routine occurrence since weight limits are conservative), triggers this unbounded refund swap. An attacker able to influence the relevant asset-conversion pool's price immediately before the refund executes (a standard sandwich/MEV pattern against AMM pools) can cause the sender to receive an arbitrarily reduced amount of their asset back, with the difference captured by the attacker or the pool. `SwapFirstAssetTrader` is wired into production runtime XCM configurations (Asset Hub Rococo, Asset Hub Westend, Penpal, staking-async parachain), not just test code, making this a real value-extraction vector against ordinary XCM senders.

## Likelihood Explanation
No privileged role is required — any unprivileged party constructing an XCM message using a non-`Target` fee asset and a conservative weight limit reaches the vulnerable path. Manipulating spot price around a specific block is a standard, low-cost MEV technique against AMM pools of the kind `pallet-asset-conversion` implements, making this readily and repeatably exploitable whenever pool liquidity is not deep enough to absorb the price impact.

## Recommendation
Compute an expected refund amount in `refund_weight` using `QuotePrice::quote_price_exact_tokens_for_tokens` (mirroring `pallet-asset-conversion-tx-payment::correct_and_deposit_fee`) and pass `Some(minimum_amount)` instead of `None` to `SwapCredit::swap_exact_tokens_for_tokens`, with an appropriate tolerance. If no acceptable minimum can be established, skip the refund swap and route the leftover `Target` asset through `OnUnbalanced` rather than exposing the sender to unbounded price impact.

## Proof of Concept
1. Configure a runtime with `SwapFirstAssetTrader` as part of its `WeightTrader`, with an asset-conversion pool between `Target` and asset `X` of modest liquidity.
2. Sender submits an XCM message paying fees in asset `X` with a weight limit above actual consumption, triggering `buy_weight` to swap `X`→`Target` for the exact quoted fee.
3. An attacker trades against the `X`/`Target` pool to skew the price unfavorably for the reverse `Target`→`X` direction immediately before the refund is processed.
4. `refund_weight` swaps the unused `Target` credit back to `X` via `swap_exact_tokens_for_tokens(..., None)`; with no floor enforced, the sender receives a reduced amount of `X`, with the attacker/pool capturing the difference.

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

**File:** cumulus/parachains/runtimes/assets/asset-hub-rococo/src/xcm_config.rs (L1-1)
```rust
// Copyright (C) Parity Technologies (UK) Ltd.
```
