### Title
`SwapFirstAssetTrader::refund_weight` swaps XCM fee-refund credit with no slippage protection (`amount_out_min: None`), enabling MEV value extraction - (File: `cumulus/primitives/utility/src/lib.rs`)

### Summary
`SwapFirstAssetTrader`, a `WeightTrader` implementation used by Cumulus-based parachains to let XCM senders pay delivery/execution fees in a non-native asset, swaps any unused weight fee back into the sender's original asset when refunding. This refund swap is executed via the generic `SwapCredit::swap_exact_tokens_for_tokens` interface but is called with `amount_out_min` hard-coded to `None`, i.e. no minimum-output/slippage bound — the same pattern flagged in the referenced Backd finding where `minOut` was set to `0`.

### Finding Description
`SwapFirstAssetTrader::refund_weight` extracts the unused portion of the collected `Target` asset fee and swaps it back into the asset the sender originally paid with: [1](#0-0) 

The call site passes `None` for `amount_out_min`:
```rust
let refund = match SwapCredit::swap_exact_tokens_for_tokens(
    vec![Target::get(), refund_swap_asset],
    refund,
    None,
) { ... }
```

The `SwapCredit` trait explicitly supports an `Option<Balance>` minimum-output guard designed for exactly this purpose: [2](#0-1) 

and the underlying `pallet-asset-conversion` implementation enforces this bound with `Error::ProvidedMinimumNotSufficientForSwap` whenever it is supplied: [3](#0-2) 

Tests confirm the pallet's swap logic is deliberately slippage-safe when a caller supplies a bound, and deliberately unguarded when `None` is passed (used only for "swap whatever you get" semantics): [4](#0-3) 

By contrast, `refund_weight` opts out of this protection entirely. Because the swap executes against the live AMM pool reserves (e.g., `pallet-asset-conversion`) at the moment the refund happens, the value the sender receives back depends on the pool price at that instant, which is influenced by whatever other swaps have executed earlier in the same block.

### Impact Explanation
Whenever an XCM sender overpays weight/fees in a non-`Target` asset (common, since senders typically supply more weight/fees than ultimately consumed), the excess is swapped back at an unprotected, potentially manipulated price. A block producer or MEV actor able to order transactions can execute a swap that skews the pool price immediately before the refund swap executes, and reverse it afterward (classic sandwich), capturing the difference between the fair-value refund and the manipulated one. This is a direct value-extraction vector against ordinary parachain users sending XCM messages paid in non-native assets — same root cause and same impact class as the referenced Backd finding (loss of funds via unguarded swap during MEV/sandwich).

### Likelihood Explanation
The vulnerable path is reachable by any unprivileged user: any XCM message executed through a `SwapFirstAssetTrader`-configured parachain that pays fees in a non-`Target` asset and does not consume 100% of the paid-for weight triggers `refund_weight`, which unconditionally uses `amount_out_min = None`. No privileged origin or special configuration is required beyond a parachain wiring this `WeightTrader` (a supported, in-tree component). Given the prevalence of MEV/searcher activity on chains with live AMM pools, exploitation is realistic whenever liquidity is thin relative to the refund size.

### Recommendation
Compute an acceptable minimum refund (e.g., via `QuotePrice::quote_price_exact_tokens_for_tokens` immediately before the swap, with an allowed tolerance) and pass it as `Some(min_amount)` to `SwapCredit::swap_exact_tokens_for_tokens` in `refund_weight`, mirroring the protection already enforced by `pallet-asset-conversion`'s public extrinsics. If a suitable minimum cannot be computed or the quoted price would result in an unacceptable loss, fail gracefully (return the un-swapped refund in the `Target` asset or skip the refund) rather than executing an unguarded swap.

### Proof of Concept
Conceptual scenario (no code execution performed, derived from code paths cited above):
1. A parachain configures `SwapFirstAssetTrader<Target, pallet_asset_conversion::Pallet<Runtime>, ...>` as its `WeightTrader`.
2. User A sends an XCM message, paying fees in asset `X` (not `Target`). `buy_weight` swaps enough `X` into `Target` to cover the declared weight.
3. Actual weight consumed is less than declared; `refund_weight` is invoked to swap the unused `Target` back into `X` for User A, calling `swap_exact_tokens_for_tokens(vec![Target, X], refund, None)` — [5](#0-4) .
4. A searcher/collator, seeing the pending refund, front-runs with a large swap `X -> Target` in the same pool to depress the `Target -> X` rate, lets the refund execute at the worse rate, then back-runs with the reverse swap to restore the price, pocketing the spread that should have gone to User A.

### Citations

**File:** cumulus/primitives/utility/src/lib.rs (L539-544)
```rust
		let refund = self.total_fee.extract(refund_amount);
		let refund = match SwapCredit::swap_exact_tokens_for_tokens(
			vec![Target::get(), refund_swap_asset],
			refund,
			None,
		) {
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

**File:** substrate/frame/asset-conversion/src/tests.rs (L2625-2645)
```rust
		// provided `credit_in` is not sufficient to swap for desired `amount_out_min`
		let amount_out_min = 20;
		let amount_in = AssetConversion::get_amount_in(
			LpFee::get(),
			&(amount_out_min - 1),
			&liquidity2,
			&liquidity1,
		)
		.unwrap();
		let credit_in = NativeAndAssets::issue(token_1.clone(), amount_in);
		let expected_credit_in = NativeAndAssets::issue(token_1.clone(), amount_in);
		let error = <AssetConversion as SwapCredit<_>>::swap_exact_tokens_for_tokens(
			vec![token_1.clone(), token_2.clone()],
			credit_in,
			Some(amount_out_min),
		)
		.unwrap_err();
		assert_eq!(
			error,
			(expected_credit_in, Error::<Test>::ProvidedMinimumNotSufficientForSwap.into())
		);
```
