Audit Report

## Title
Fee-refund path in `SwapAssetAdapter::correct_and_deposit_fee` uses a manipulable spot-price AMM quote, letting a user extract LP-pool value via same-transaction price manipulation - (File: `substrate/frame/transaction-payment/asset-conversion-tx-payment/src/payment.rs`)

## Summary
`ChargeAssetTxPayment`'s `SwapAssetAdapter` withdraws a non-native fee asset at prepare-time using a pool quote taken before the wrapped call is dispatched, but refunds unspent weight at `post_dispatch_details` using an independent spot-price quote taken *after* the call has executed and potentially moved the pool reserves. Since the refunded native amount is fixed by weight accounting and unrelated to price, but the asset amount returned for it is priced off whatever reserves exist at that post-dispatch instant, a user who moves the pool price between withdrawal and refund can receive more asset back than economically justified, extracting value from the AMM pool.

## Finding Description
The code confirms the claim precisely. At withdrawal time, `withdraw_fee` quotes and swaps the fee at the pool state prevailing before dispatch: [1](#0-0) 

At `correct_and_deposit_fee`, the refund amount is derived purely from weight accounting, independent of any AMM price: [2](#0-1) 

The refund is then converted back to `asset_id` using a fresh spot quote taken at the current (post-dispatch) pool state, with the swap executed back-to-back at that same quoted price: [3](#0-2) 

The `Some(refund_asset_amount)` parameter passed to `swap_exact_tokens_for_tokens` only guarantees the quote and the swap execute at the identical price (protecting against manipulation *between* those two calls); it provides no protection against manipulation that occurred *before* the quote, i.e., during dispatch of the wrapped call or via interleaved extrinsics within the same block. There is no mechanism tying the refund conversion rate back to the rate used at withdrawal (no caching of the original price ratio, and no ceiling clamping the refund to `fee_asset_amount`), so the refund quote is a genuine unprotected spot-price read of attacker-influenceable state.

## Impact Explanation
An unprivileged signed account paying fees via `ChargeAssetTxPayment` in a non-native asset, where a live `pallet-asset-conversion` pool exists for that asset against the native token, can embed or precede a pool-skewing swap so that by the time `correct_and_deposit_fee` runs, the native→asset exchange rate favors the attacker. Because the refunded native amount is fixed and independent of price, but the returned asset amount scales with the skewed spot price, the attacker's refund swap extracts value from the pool (LPs) beyond what a fair, unmanipulated refund would return. This is a genuine in-scope fee-accounting/oracle-manipulation flaw affecting `pallet-asset-conversion` liquidity providers.

## Likelihood Explanation
The preconditions are fully attacker-controlled and require no privileged access: a live asset/native conversion pool, an account paying fees in that asset, and the ability to submit an ordinary `AssetConversion::swap_exact_tokens_for_tokens` extrinsic (or embed a swap as the dispatched call) before `post_dispatch_details` executes. Profitability depends on pool depth relative to the refundable weight-fee amount and the LP fee cost of the round-trip manipulation, but for pools that are not very deep relative to the manipulation size, a net gain is achievable and the attack is repeatable every block.

## Recommendation
Avoid re-quoting the refund leg against fresh spot-pool state. Preferable mitigations: (1) derive the refund proportionally from the price ratio recorded at withdrawal time (`fee_asset_amount`/`fee`) rather than issuing a new `quote_price_exact_tokens_for_tokens` call, (2) hard-clamp `refund_asset_amount` to be no greater than `fee_asset_amount` (the user can never receive back more asset than they originally paid in), and/or (3) source the refund conversion from a time-weighted/oracle price instead of instantaneous spot reserves.

## Proof of Concept
Add an integration test to `substrate/frame/transaction-payment/asset-conversion-tx-payment/src/tests.rs`:
1. Set up a pool via `setup_lp(asset_id, balance_factor)` with moderate depth.
2. Call `validate_and_prepare` for `ChargeAssetTxPayment`, recording `fee_in_asset` withdrawn and pool reserves at that point.
3. Before calling `post_dispatch_details`, execute an ordinary `AssetConversion::swap_exact_tokens_for_tokens` extrinsic (as the same caller) that swaps a large amount of `asset_id` into the pool for native, skewing reserves.
4. Call `post_dispatch_details` with `post_info` reflecting unused weight so `refund_amount > 0`; record the actual `Assets::balance` change for the caller.
5. Compute the "fair" refund using `quote_price_exact_tokens_for_tokens` at the pre-manipulation (step 2) reserves for the same `refund_amount`.
6. Assert the actual refund exceeds the fair refund, and optionally reverse the manipulation swap to show the caller's net asset balance strictly exceeds what a fair-price fee/refund cycle would have left them with, demonstrating value extracted from the pool.

### Citations

**File:** substrate/frame/transaction-payment/asset-conversion-tx-payment/src/payment.rs (L142-175)
```rust
		// Quote the amount of the `asset_id` needed to pay the fee in the asset `A`.
		let asset_fee =
			S::quote_price_tokens_for_exact_tokens(asset_id.clone(), A::get(), fee, true)
				.filter(|asset_fee| !asset_fee.is_zero())
				.ok_or(InvalidTransaction::Payment)?;

		// Withdraw the `asset_id` credit for the swap.
		let asset_fee_credit = F::withdraw(
			asset_id.clone(),
			who,
			asset_fee,
			Precision::Exact,
			Preservation::Preserve,
			Fortitude::Polite,
		)
		.map_err(|_| InvalidTransaction::Payment)?;

		let (fee_credit, change) = match S::swap_tokens_for_exact_tokens(
			vec![asset_id, A::get()],
			asset_fee_credit,
			fee,
		) {
			Ok((fee_credit, change)) => (fee_credit, change),
			Err((credit_in, _)) => {
				defensive!("Fee swap should pass for the quoted amount");
				let _ = F::resolve(who, credit_in).defensive_proof("Should resolve the credit");
				return Err(InvalidTransaction::Payment.into());
			},
		};

		// Since the exact price for `fee` has been quoted, the change should be zero.
		ensure!(change.peek().is_zero(), InvalidTransaction::Payment);

		Ok((fee_credit, asset_fee))
```

**File:** substrate/frame/transaction-payment/asset-conversion-tx-payment/src/payment.rs (L221-222)
```rust
		let (fee_paid, fee_asset_amount) = already_withdrawn;
		let refund_amount = fee_paid.peek().saturating_sub(corrected_fee);
```

**File:** substrate/frame/transaction-payment/asset-conversion-tx-payment/src/payment.rs (L262-297)
```rust
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
