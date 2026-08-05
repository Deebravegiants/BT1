### Title
Unbounded refund-swap quote allows AMM price manipulation to extract excess asset value in `correct_and_deposit_fee` - (File: substrate/frame/transaction-payment/asset-conversion-tx-payment/src/payment.rs)

### Summary
`SwapAssetAdapter::withdraw_fee` and `SwapAssetAdapter::correct_and_deposit_fee` execute two independent, live-price AMM swaps separated in time by the dispatched call's own execution. Because the refund leg's quoted/swapped amount (`refund_asset_amount`) is never bounded by the amount of `asset_id` originally consumed (`fee_asset_amount`), a caller who can shift the pool price between the two swaps (e.g., via actions taken inside their own batched call) can receive back more of `asset_id` than they paid in, while the native-fee accounting to `OU` remains untouched and "correct."

### Finding Description
`withdraw_fee` [1](#0-0)  quotes `asset_fee` via `S::quote_price_tokens_for_exact_tokens` at the pool's state *before* the extrinsic's call is dispatched, and immediately executes `swap_tokens_for_exact_tokens` at that price, producing `(fee_credit, fee_asset_amount)`.

Later, in `correct_and_deposit_fee`, after the call has fully executed, the pallet computes a purely native-denominated `refund_amount = fee_paid.peek() - corrected_fee` [2](#0-1) , then independently re-quotes and swaps that native amount back into `asset_id` using the pool's *current* (post-call) state: [3](#0-2) 

There is no check anywhere that `refund_asset_amount <= fee_asset_amount`, nor any binding of the refund-swap price to the price used at withdrawal. The only guard is `can_deposit` (checks the recipient account can hold the tokens) — it does not constrain the *amount* relative to what was originally taken. Since `withdraw_fee` runs in the transaction extension *before* the call dispatches, and `correct_and_deposit_fee` runs in the extension *after* the call dispatches, any AMM-affecting action performed by the call itself (e.g., a `pallet_asset_conversion` swap or liquidity operation batched inside the very extrinsic being fee-charged) executes strictly between the two pricing points and is fully attacker-controlled. Because pool interaction is permissionless, an attacker can also pre-position the pool with a preceding extrinsic in the same block (their own transaction ordered before this one by nonce) to set the price seen by `withdraw_fee` favorably (minimizing `fee_asset_amount`), then use the dispatched call itself to move the price to a different favorable point for the `correct_and_deposit_fee` quote (maximizing `refund_asset_amount`). The native side of the accounting (`corrected_fee` credited to `OU::on_unbalanceds`) is completely price-independent and always correct, so this manipulation produces no discrepancy visible from `OU`'s perspective — the leakage occurs purely on the `asset_id` side, funded by the AMM pool's reserves (and thus its other liquidity providers).

### Impact Explanation
An attacker can cause the pallet to pay out more `asset_id` in the refund step than was withdrawn from the same user in the fee step, extracting value from the `pallet_asset_conversion` pool (and its LPs) with no corresponding reduction in fee revenue collected by `OU`. This is an asset-accounting violation: the "backing" assumption that the fee-asset flow into/out of a user's account nets to at most the true fee-native-equivalent is broken, letting an unprivileged user siphon pool liquidity via legitimate-looking swap/liquidity actions bundled in their own extrinsic.

### Likelihood Explanation
Requires: (1) a live `pallet_asset_conversion` pool for the `asset_id`/native pair with the attacker able to move its price meaningfully (large trade or thin liquidity), (2) the ability to bundle pool-manipulating calls inside the same dispatched call as the fee-paying extrinsic (e.g., via `pallet_utility::batch`) and/or a preceding same-block extrinsic to set the pre-dispatch price. Both are ordinary, permissionless capabilities of any signed account; no privileged access, forged signatures, or unusual chain conditions are needed. Profitability is bounded by AMM swap fees paid during manipulation, so it is most attractive against thin/low-liquidity pools or with large capital, but it is a repeatable, deterministic strategy, not probabilistic.

### Recommendation
Bound the refund-swap so that it cannot return more `asset_id` than was originally withdrawn for the fee (e.g., `refund_asset_amount = min(quoted_amount, fee_asset_amount.saturating_mul(refund_amount) / fee)`, or more simply cap `refund_asset_amount` at a pro-rata share of `fee_asset_amount`), and/or record the effective price from `withdraw_fee` and require the refund swap to execute at a price no better than that recorded rate (reject/clamp otherwise). At minimum, add `ensure!(refund_asset_amount <= fee_asset_amount, ...)` before performing the refund swap.

### Proof of Concept
Integration test outline (pallet-asset-conversion-tx-payment mock runtime with `pallet_utility` and `pallet_asset_conversion`):
1. Create pool `(NativeAsset, FeeAsset)` with liquidity, note initial reserves `R_native0`, `R_fee0`.
2. Attacker submits `Extrinsic A` (prior nonce, same block) performing a large swap/liquidity removal that skews price so that `quote_price_tokens_for_exact_tokens` for the fee is minimized when the target extrinsic's `withdraw_fee` runs.
3. Attacker submits `Extrinsic B`: a `pallet_utility::batch` call composed of `[pallet_asset_conversion::swap_exact_tokens_for_tokens (reverse the skew)]` plus a no-op/cheap call, paid for using `FeeAsset` via `ChargeAssetTxPayment`.
4. Record `fee_asset_amount` returned from `withdraw_fee` (via event/storage) and `refund_asset_amount` computed inside `correct_and_deposit_fee` (via emitted event or account balance delta).
5. Assert `refund_asset_amount > fee_asset_amount` (violates expected invariant `refund_asset_amount <= fee_asset_amount`), while independently asserting `OU`/treasury received exactly `corrected_fee` in native asset — proving the excess came from the pool, not from any native-fee shortfall.

### Citations

**File:** substrate/frame/transaction-payment/asset-conversion-tx-payment/src/payment.rs (L142-176)
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
	}
```

**File:** substrate/frame/transaction-payment/asset-conversion-tx-payment/src/payment.rs (L221-229)
```rust
		let (fee_paid, fee_asset_amount) = already_withdrawn;
		let refund_amount = fee_paid.peek().saturating_sub(corrected_fee);

		// nothing to refund or the account was removed by to the dispatched function.
		if refund_amount.is_zero() || F::total_balance(asset_id.clone(), who).is_zero() {
			let (tip, fee) = fee_paid.split(tip);
			OU::on_unbalanceds(Some(fee).into_iter().chain(Some(tip)));
			return Ok(fee_asset_amount);
		}
```

**File:** substrate/frame/transaction-payment/asset-conversion-tx-payment/src/payment.rs (L261-286)
```rust
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
```
