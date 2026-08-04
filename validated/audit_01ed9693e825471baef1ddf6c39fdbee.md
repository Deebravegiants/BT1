## Analysis

The reported bug pattern — an `ExactInput` swap invoked with `amountOutMinimum` hardcoded to a value that provides no slippage protection — has a direct analog in this codebase's XCM fee-refund logic.

### Title
Unbounded Slippage in `SwapFirstAssetTrader::refund_weight` XCM Fee Refund Swap - (File: `cumulus/primitives/utility/src/lib.rs`)

### Summary
`SwapFirstAssetTrader` is a `WeightTrader` used to pay XCM execution fees by swapping a user-provided asset into a `Target` fee asset via `pallet_asset_conversion`'s `SwapCredit` trait. When unused weight is refunded (`refund_weight`), the trader swaps the refund amount back from `Target` into the original payment asset by calling `SwapCredit::swap_exact_tokens_for_tokens` with `amount_out_min` hardcoded to `None`, i.e., no minimum-output/slippage protection at all.

### Finding Description
In `buy_weight`, the user's asset is exchanged into `Target` using `swap_tokens_for_exact_tokens`, which is bounded (an exact-output swap with an implicit maximum input equal to `credit_in`) [1](#0-0) .

However, in `refund_weight`, the reverse swap (converting the unspent portion of `total_fee` back into the asset the user originally paid with) is performed with no minimum output at all: [2](#0-1) 

The `SwapCredit::swap_exact_tokens_for_tokens` signature explicitly supports an `Option<Balance>` minimum-output guard for exactly this purpose [3](#0-2) , and the pallet's own extrinsic-level API requires callers to always supply a non-zero `amount_out_min` and enforces it via `ProvidedMinimumNotSufficientForSwap` [4](#0-3) . `refund_weight` bypasses this protection entirely by passing `None`.

By contrast, `SingleAssetExchangeAdapter::exchange_asset` (the other main consumer of `SwapCredit` in XCM tooling) correctly supplies `Some(want_amount)` as the minimum when doing a "maximal" exact-in swap [5](#0-4) , confirming that `refund_weight`'s omission is inconsistent with the rest of the codebase's own safe usage pattern.

### Impact Explanation
Because the AMM pool price can move between the time the refund amount is computed and the time the swap executes (e.g., other swaps against the same pool being included in the same or an adjacent block by the collator/block producer), the refund swap can be sandwiched: an attacker/collator can move the pool price unfavorably immediately before the refund executes and revert it afterward, capturing the difference. The affected value is the unused-weight fee credit being refunded to the XCM message sender — the user receives less of their original asset back than the fair-price refund, with no upper bound on the loss (in the extreme, `swap_exact_tokens_for_tokens` with `None` will accept any nonzero output).

### Likelihood Explanation
Exploitation requires an adversarial party capable of influencing swap ordering around the parachain block/message that triggers the refund (e.g. a MEV-aware collator or a searcher able to co-locate transactions within the same block), which is a realistic threat model for permissionless AMM pools on parachains — no privileged/root access is required, only normal transaction submission plus favorable ordering. This is lower-severity than the analogous DeFi report because refunds are typically limited to the "unused" portion of a weight-limit overestimate rather than a user's full trade amount, but the root cause (an `ExactInput`-style swap call with no `amount_out_min`) is identical in kind.

### Recommendation
Compute a safe, non-`None` `amount_out_min` for the refund swap in `refund_weight` — e.g., by using `QuotePrice::quote_price_exact_tokens_for_tokens` to derive an expected amount and applying a tolerance, mirroring how `SingleAssetExchangeAdapter` and the pallet's own extrinsics require a caller-supplied minimum.

### Proof of Concept
No PoC harness was built; the finding is derived from direct code reading of `refund_weight`'s call site, contrasted with the safe pattern used elsewhere in the same crate and in `pallet_asset_conversion` itself, as cited above.

---
Note: this is a code-level, medium-confidence analog rather than a confirmed exploit — actual severity depends on typical refund sizes and how much slippage a given asset-conversion pool for that asset pair would allow, which would need runtime-specific parameters (pool depth, `Target` asset choice) to quantify precisely.

### Citations

**File:** cumulus/primitives/utility/src/lib.rs (L471-475)
```rust
		let (credit_out, credit_change) = match SwapCredit::swap_tokens_for_exact_tokens(
			vec![swap_asset, Target::get()],
			credit_in,
			fee,
		) {
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

**File:** substrate/frame/asset-conversion/src/swap.rs (L93-97)
```rust
	fn swap_exact_tokens_for_tokens(
		path: Vec<Self::AssetKind>,
		credit_in: Self::Credit,
		amount_out_min: Option<Self::Balance>,
	) -> Result<Self::Credit, (Self::Credit, DispatchError)>;
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

**File:** polkadot/xcm/xcm-builder/src/asset_exchange/single_asset_adapter/adapter.rs (L110-114)
```rust
			let credit_out = match <AssetConversion as SwapCredit<_>>::swap_exact_tokens_for_tokens(
				vec![swap_asset, want_asset_id],
				credit_in,
				Some(want_amount),
			) {
```
