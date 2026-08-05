Audit Report

## Title
`SwapFirstAssetTrader::refund_weight` swaps XCM fee-refund credit with no slippage protection (`amount_out_min: None`), enabling MEV value extraction - (File: `cumulus/primitives/utility/src/lib.rs`)

## Summary
`SwapFirstAssetTrader::refund_weight` swaps the unused portion of a collected `Target` asset fee back into the sender's original payment asset via `SwapCredit::swap_exact_tokens_for_tokens`, but hard-codes `amount_out_min` to `None`, meaning the refund executes against live AMM pool reserves with no minimum-output guard. This exposes ordinary XCM senders paying fees in a non-`Target` asset to value extraction if pool price is manipulated around the time the refund swap executes.

## Finding Description
The refund path is confirmed as described: `refund_weight` extracts the unspent portion of `self.total_fee` and swaps it back to the original asset with `None` passed as the slippage bound: [1](#0-0) 

This contrasts with `buy_weight`, which uses `swap_tokens_for_exact_tokens` (exact-output swap bounded by the target fee amount, so slippage there manifests as needing more input, not less output for the user): [2](#0-1) 

The `SwapCredit` trait explicitly supports a slippage bound via `Option<Balance>` for `amount_out_min`, and `pallet-asset-conversion`'s implementation enforces it with `Error::ProvidedMinimumNotSufficientForSwap` when supplied, but is a no-op guard when `None`: [3](#0-2) 

`refund_weight` never supplies this bound, so the refund is fully exposed to whatever the pool price is at execution time — no code path in `SwapFirstAssetTrader` computes or checks an expected/minimum refund value before or after the swap.

## Impact Explanation
Any XCM sender who pays weight/delivery fees in a non-`Target` asset and does not consume the full declared weight triggers `refund_weight`. Since this swaps at an unguarded market rate, a party able to influence pool reserves immediately before the refund executes (e.g., via other swaps ordered in the same block) can reduce the value the sender receives back, extracting the difference. This is a direct, unprivileged value-loss vector for XCM users routed through a `SwapFirstAssetTrader`-configured parachain, matching the impact class of unguarded-swap/MEV-sandwich issues.

## Likelihood Explanation
The vulnerable path requires only that a parachain adopt `SwapFirstAssetTrader` as its `WeightTrader` (an in-tree, intended-for-use component) and that a user pay fees in an asset other than `Target` while overpaying weight — both are normal, expected usage patterns, not edge cases or misconfigurations. Exploitation additionally requires an actor capable of manipulating the relevant AMM pool's price around the refund's execution (e.g., a block/collator with control over intra-block ordering, or low-liquidity pools), which is a realistic condition on chains with live AMM pools and typical collator/MEV dynamics.

## Recommendation
Compute an acceptable minimum refund immediately before the swap (e.g., via `QuotePrice::quote_price_exact_tokens_for_tokens` with a configurable tolerance) and pass it as `Some(min_amount)` to `SwapCredit::swap_exact_tokens_for_tokens` in `refund_weight`. If a sufficient minimum cannot be met, prefer failing safe (e.g., retain the refund in `Target` or drop it via existing error-handling `total_fee.subsume` path) instead of executing an unguarded swap.

## Proof of Concept
1. Configure a parachain with `SwapFirstAssetTrader<Target, pallet_asset_conversion::Pallet<Runtime>, ...>` as its `WeightTrader`.
2. User A sends an XCM message paying fees in asset `X` ≠ `Target`; `buy_weight` swaps `X` → `Target` for the declared weight fee.
3. Actual weight consumed is less than declared, so `refund_weight` swaps unused `Target` back to `X` via `swap_exact_tokens_for_tokens(vec![Target, X], refund, None)` — [4](#0-3) .
4. An actor with intra-block ordering influence (e.g., collator or searcher) executes an `X→Target` swap in the same pool before this refund executes to depress the `Target→X` rate, lets the refund settle at the worse rate, then reverses the swap afterward, capturing the spread that should have accrued to User A.
5. A unit test using `pallet-asset-conversion`'s mock runtime can demonstrate this by pre-swapping the pool to shift reserves, then invoking `refund_weight` and comparing the resulting refund amount against the amount obtainable at the unperturbed price — confirming the loss is attributable to the missing `amount_out_min` bound.

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

**File:** cumulus/primitives/utility/src/lib.rs (L539-544)
```rust
		let refund = self.total_fee.extract(refund_amount);
		let refund = match SwapCredit::swap_exact_tokens_for_tokens(
			vec![Target::get(), refund_swap_asset],
			refund,
			None,
		) {
```

**File:** substrate/frame/asset-conversion/src/lib.rs (L1092-1096)
```rust
				let amount_out = path.last().map(|(_, a)| *a).ok_or(Error::<T>::InvalidPath)?;
				ensure!(
					amount_out_min.map_or(true, |a| amount_out >= a),
					Error::<T>::ProvidedMinimumNotSufficientForSwap
				);
```
