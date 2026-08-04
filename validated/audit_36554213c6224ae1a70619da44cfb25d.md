### Title
Failed refund-swap fallback silently overcharges users and misreports full pre-correction fee via `AssetTxFeePaid` - (File: substrate/frame/transaction-payment/asset-conversion-tx-payment/src/payment.rs)

### Summary
In `SwapAssetAdapter::correct_and_deposit_fee`, when the reverse quote `AssetConversion::quote_price_exact_tokens_for_tokens` (via `S::quote_price_exact_tokens_for_tokens`) returns `None`/zero or the resulting `can_deposit` check fails, the function forwards the entire originally-withdrawn native `fee_paid` to `OU::on_unbalanceds` with no refund, and returns the pre-correction `fee_asset_amount` unchanged. This value is then reported verbatim as `actual_fee` in the `AssetTxFeePaid` event, even though the true post-dispatch `corrected_fee` (computed from actual weight) was lower.

### Finding Description
The refund branch for non-native, non-target assets is: [1](#0-0) 

When `refund_asset_amount` is zero (quote fails) or `can_deposit` fails, the code takes the "no refund" fallback: it splits off tip/fee from the **entire** `fee_paid` credit (the full amount withdrawn pre-correction) and forwards it to `OU::on_unbalanceds`, then returns the original `fee_asset_amount` untouched — not any value derived from `corrected_fee`.

In `lib.rs`, this return value (`converted_fee`) is used directly as the `actual_fee` reported in the `AssetTxFeePaid` event: [2](#0-1) 

So both the on-chain accounting (fee/tip forwarded to `OU`) and the emitted event reflect the pre-correction amount, not the deterministic corrected fee that `pallet_transaction_payment::Pallet::<T>::compute_actual_fee` computed from actual dispatch weight. The `AssetRefundFailed` event defined in `lib.rs` (intended to signal exactly this condition) is not deposited anywhere in this code path, so there is no on-chain signal distinguishing "legitimately owed full fee" from "refund silently dropped due to pool illiquidity."

An unprivileged user can trigger the pool-illiquidity precondition against another user's transaction (or their own) by submitting a large swap extrinsic in `pallet-asset-conversion` that drains/skews the `(Native, asset_id)` pool between the victim's `validate`/`prepare` step and `post_dispatch_details` in the same block, causing the reverse quote to fail or the swap to produce a value that fails `can_deposit`. No signature/origin/nonce/weight check prevents this, since swapping a public AMM pool is a normal permissionless operation.

### Impact Explanation
The victim (or the attacker themself, if self-targeting is beneficial in edge cases) is charged the full pre-correction fee in `asset_id` terms with no refund, even when the dispatched call's actual weight was far lower than estimated. The discrepancy between what was actually owed (`corrected_fee_in_native`) and what was collected (`fee_paid` in full) is durable and unrecoverable — there is no retry or later reconciliation. This is a concrete instance of the scoped impact: economic griefing via pool-liquidity manipulation causing systemic overcharging without recourse.

### Likelihood Explanation
The precondition (draining/manipulating the specific `(Native, asset_id)` pool within the same block as the victim's `ChargeAssetTxPayment` extrinsic) is realistic on any chain where a low-liquidity or thin pool exists, and is fully permissionless — an attacker only needs enough capital to move the pool price/liquidity temporarily via a normal swap extrinsic, then can reverse the swap in a following block to recover funds while the victim's transaction is trapped in between. This requires no privileged access, only ordinary swap extrinsics and awareness of pending transactions (front-running), which is a well-established and already-anticipated risk class in AMM designs. It is worth noting the code comments show this "no refund" outcome was anticipated by developers as a fallback safety measure (to avoid failing the whole extrinsic when a refund swap can't be quoted), but the consequence — full fee kept with no signal and no bound relative to `corrected_fee` — was not fully accounted for in the accounting/event layer.

### Recommendation
- When the refund-swap fallback is taken, deposit the existing `AssetRefundFailed { native_amount_kept }` event (or similar) so downstream indexers/users can detect and be compensated for silent overcharges.
- Consider bounding the fallback exposure, e.g., by using a stored/oracle-based reference price with slippage tolerance instead of relying solely on the spot AMM quote for the refund direction, or by re-attempting the refund at a later block via a queued refund mechanism.
- At minimum, ensure the reported `actual_fee` in `AssetTxFeePaid` distinguishes the "no-refund" case from normal full-refund cases so client tooling doesn't treat the pre-correction amount as if it were the correctly-adjusted fee.

### Proof of Concept
Extend `substrate/frame/transaction-payment/asset-conversion-tx-payment/src/tests.rs`'s existing "no refund"/Path C test to:
1. Set up a `(Native, asset_id)` pool with sufficient liquidity, submit a `ChargeAssetTxPayment` extrinsic with a high estimated weight/fee.
2. Before calling `post_dispatch_details`, drain/skew the pool (via `AssetConversion::swap_exact_tokens_for_tokens` or similar) so that `quote_price_exact_tokens_for_tokens(Native, asset_id, refund_amount, true)` returns `None`.
3. Dispatch with a low actual weight (`post_info` reflecting minimal weight), call `post_dispatch_details`.
4. Assert: `converted_fee` (and the emitted `AssetTxFeePaid.actual_fee`) equals the full pre-correction `fee_asset_amount`, not a value bounded by `corrected_fee_in_native`; assert `FeeUnbalancedAmount` (test helper tracking `OU::on_unbalanceds`) equals the full `fee_paid.peek()` rather than `corrected_fee`; compute and assert the attacker-controllable overcharge = `fee_paid.peek() - corrected_fee_in_native` is nonzero and proportional to the weight-estimate gap.

### Citations

**File:** substrate/frame/transaction-payment/asset-conversion-tx-payment/src/payment.rs (L261-277)
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
```

**File:** substrate/frame/transaction-payment/asset-conversion-tx-payment/src/lib.rs (L402-417)
```rust
				let converted_fee = T::OnChargeAssetTransaction::correct_and_deposit_fee(
					&who,
					info,
					&actual_post_info,
					actual_fee,
					tip,
					asset_id.clone(),
					already_withdrawn,
				)?;

				Pallet::<T>::deposit_event(Event::<T>::AssetTxFeePaid {
					who,
					actual_fee: converted_fee,
					tip,
					asset_id,
				});
```
