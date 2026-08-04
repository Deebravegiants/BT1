## Finding

The reported Omnipool bug (`batchSwap()` with infinite limits and no slippage bound) has a direct structural analog in `SwapFirstAssetTrader::refund_weight()` in Cumulus' XCM weight-trading utilities. [1](#0-0) 

### Title
Missing slippage protection in `SwapFirstAssetTrader::refund_weight()` XCM fee-refund swap — (File: `cumulus/primitives/utility/src/lib.rs`)

### Summary
`SwapFirstAssetTrader` is a `WeightTrader` used to let XCM messages pay execution fees in a non-native fungible asset by swapping it through `pallet-asset-conversion` (via the generic `SwapCredit` trait) into the runtime's target fee asset, and vice versa for unspent-weight refunds. The refund path performs a swap with `amount_out_min = None`, i.e. an unbounded-slippage swap, structurally identical to the reported Balancer `swapForGem()`/infinite-limits `batchSwap()` pattern.

### Finding Description
In `buy_weight()`, when an XCM message pays fees in an asset other than `Target`, the trader swaps exactly the needed amount using `SwapCredit::swap_tokens_for_exact_tokens`, which is correctly bounded (the credit itself acts as the max-input bound). [2](#0-1) 

However, in `refund_weight()`, the unspent portion of the already-swapped `Target` asset (`self.total_fee`) is swapped *back* into the original fee asset using `SwapCredit::swap_exact_tokens_for_tokens(..., refund, None)` — passing `None` for `amount_out_min`: [3](#0-2) 

This means the AMM swap (`pallet_asset_conversion`'s `do_swap_exact_credit_tokens_for_tokens`) will accept whatever output the pool returns, no matter how unfavorable, exactly mirroring the "blind swap with infinite limits" root cause described in the external report. [4](#0-3) 

`SwapFirstAssetTrader` is wired in as the configured `WeightTrader`/part of `Trader` on production Asset Hub runtimes:

so this code path executes for every incoming XCM message that pays execution fees in a swappable, non-target asset and leaves unused weight (which is the common case, since `buy_weight` is called with a purchase amount before actual execution weight is known).

### Impact Explanation
An attacker who can influence the `pallet-asset-conversion` pool price for the `Target ↔ refund_swap_asset` pair immediately before an XCM message's `refund_weight()` executes (e.g. by trading heavily against the pool, then reverting after) can force the refund swap to execute at a near-zero exchange rate. This lets the attacker extract essentially the entire refunded execution-fee value from arbitrary XCM messages executed on the chain, at the expense of the user who over-paid for weight and the runtime's fee accounting. This is a genuine instance of the same vulnerability class (unbounded-slippage AMM swap enabling sandwich extraction), though the value at risk per message is bounded by the size of the unspent-weight refund (`total_fee - amount actually consumed`) rather than an entire reward payout, so the blast radius is smaller than in the original DeFi report.

### Likelihood Explanation
Exploitation requires: (1) a runtime that configures `SwapFirstAssetTrader` with a real AMM (Asset Hub does), (2) a liquid-enough-to-be-thin pool for the fee-swap pair so it can be economically manipulated within one block/refund window, and (3) the attacker being able to place manipulating swaps immediately before the refund executes and reverse them immediately after. Because XCM messages are not visible in a public parachain mempool the way ordinary extrinsics are, the practical window for sandwiching is narrower and typically requires either colluding with/being the block author or exploiting the fact that pool-changing extrinsics submitted in the same block as the refunding XCM message execute in a predictable order relative to it. This makes the attack feasible but with meaningfully lower likelihood/ease than a standard mempool-visible DEX sandwich.

### Recommendation
Do not pass `None` for `amount_out_min` in `refund_weight()`. Compute an acceptable minimum using `QuotePrice::quote_price_exact_tokens_for_tokens` (already used elsewhere in the codebase, e.g. `substrate/frame/transaction-payment/asset-conversion-tx-payment/src/payment.rs`) immediately before the swap, and apply a small tolerance, or fall back to returning the refund in the `Target` asset (no swap) if the quoted price cannot be met, similar to how `SwapAssetAdapter::correct_and_deposit_fee`'s Path C behaves when a route/quote is unavailable. [5](#0-4) 

### Proof of Concept
1. Configure/deploy on a runtime using `SwapFirstAssetTrader` (e.g. Asset Hub) with an asset-conversion pool for `Target ↔ AssetX` that has modest liquidity.
2. Attacker, in the block immediately preceding the block that will process a pending XCM message paying fees in `AssetX` (visible via HRMP/UMP channel state on the relay chain, or via mempool if colluding with the block author), swaps a large amount of `Target` into `AssetX` in the pool, skewing the price heavily.
3. The XCM message executes: `buy_weight()` swaps `AssetX` into `Target` for the exact fee, and after execution `refund_weight()` calls `swap_exact_tokens_for_tokens(vec![Target, AssetX], refund, None)` at the now-skewed price, returning far less `AssetX` than fair value.
4. Attacker swaps back `AssetX → Target` in the same or next block, realizing the difference as profit, funded by the value that should have been refunded to the fee payer.

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

**File:** substrate/frame/asset-conversion/src/lib.rs (L1075-1097)
```rust
		pub(crate) fn do_swap_exact_credit_tokens_for_tokens(
			path: Vec<T::AssetKind>,
			credit_in: CreditOf<T>,
			amount_out_min: Option<T::Balance>,
		) -> Result<CreditOf<T>, (CreditOf<T>, DispatchError)> {
			let amount_in = credit_in.peek();
			let inspect_path = |credit_asset| {
				ensure!(
					path.first().map_or(false, |a| *a == credit_asset),
					Error::<T>::InvalidPath
				);
				ensure!(!amount_in.is_zero(), Error::<T>::ZeroAmount);
				ensure!(amount_out_min.map_or(true, |a| !a.is_zero()), Error::<T>::ZeroAmount);

				Self::validate_swap_path(&path)?;
				let path = Self::balance_path_from_amount_in(amount_in, path)?;

				let amount_out = path.last().map(|(_, a)| *a).ok_or(Error::<T>::InvalidPath)?;
				ensure!(
					amount_out_min.map_or(true, |a| amount_out >= a),
					Error::<T>::ProvidedMinimumNotSufficientForSwap
				);
				Ok((path, amount_out))
```

**File:** substrate/frame/transaction-payment/asset-conversion-tx-payment/src/payment.rs (L259-297)
```rust
		// refund is non zero and `who`'s fee `asset_id` is not the target asset.

		// check if the refund amount can be swapped back into `who`'s fee `asset_id`.
		let refund_asset_amount =
			S::quote_price_exact_tokens_for_tokens(A::get(), asset_id.clone(), refund_amount, true)
				// No refund given if it cannot be swapped back.
				.unwrap_or(Zero::zero());

		// `fee_paid` cannot be swapped back into `who`'s fee `asset_id` or the refund amount cannot
		// be deposited into `who`'s fee `asset_id`, exit without refund.
		if refund_asset_amount.is_zero() ||
			!matches!(
				F::can_deposit(asset_id.clone(), who, refund_asset_amount, Provenance::Extant),
				DepositConsequence::Success
			) {
			let (tip, fee) = fee_paid.split(tip);
			OU::on_unbalanceds(Some(fee).into_iter().chain(Some(tip)));
			return Ok(fee_asset_amount);
		}

		// swap the refund amount back into `who`'s fee `asset_id`.

		let (refund, adjusted_paid) = fee_paid.split(refund_amount);

		let (fee_asset_amount, adjusted_paid) = match S::swap_exact_tokens_for_tokens(
			vec![A::get(), asset_id],
			refund,
			Some(refund_asset_amount),
		) {
			Ok(refund_asset) => match F::resolve(who, refund_asset) {
				Ok(_) => (fee_asset_amount.saturating_sub(refund_asset_amount), adjusted_paid),
				Err(refund_asset) => {
					defensive!(
						"Refund resolve should pass since `can_deposit` was checked",
						(refund_asset.asset(), refund_asset.peek(), who)
					);
					(fee_asset_amount, adjusted_paid)
				},
			},
```
