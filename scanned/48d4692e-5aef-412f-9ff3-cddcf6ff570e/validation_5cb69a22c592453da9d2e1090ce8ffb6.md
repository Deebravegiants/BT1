### Title
Self-sandwich MEV extraction against the AMM pool via `SwapAssetAdapter`'s pre/post-dispatch fee swaps in `ChargeAssetTxPayment` - ([File: substrate/frame/transaction-payment/asset-conversion-tx-payment/src/payment.rs])

### Summary
`SwapAssetAdapter::withdraw_fee` executes a real AMM swap (asset → native `A`) before the wrapped call is dispatched, and `SwapAssetAdapter::correct_and_deposit_fee` executes a second, opposite-direction AMM swap (`A` → asset, the fee refund) strictly after the call has been dispatched. Because the dispatched call (e.g. the second leg of a `Utility::batch_all`) executes *between* these two extension-controlled swaps, and is fully attacker-controlled, the attacker can insert a pool-manipulating trade in that gap so the refund leg executes at an artificially favorable, self-created price, extracting value from the AMM pool/LPs in a classic sandwich pattern where the "victim" trade is the extension's own mandatory refund swap.

### Finding Description
`ChargeAssetTxPayment`'s `TransactionExtension` lifecycle calls `withdraw_fee` in `prepare` (pre-dispatch) and `correct_and_deposit_fee` in `post_dispatch_details` (post-dispatch), with the actual call dispatch happening strictly in between [1](#0-0) [2](#0-1) .

In `withdraw_fee`, when the fee asset is not the target asset `A`, the adapter quotes and then immediately executes a real swap: `asset_id` in, exact `fee` amount of `A` out, moving the pool such that `A` becomes scarcer relative to `asset_id` [3](#0-2) .

In `correct_and_deposit_fee`, the refund leg quotes `S::quote_price_exact_tokens_for_tokens(A::get(), asset_id, refund_amount, true)` and then immediately swaps that exact `refund_amount` of `A` for `asset_id`, crediting the caller [4](#0-3) . Both the quote and the swap in each function are executed back-to-back so each individual swap is internally consistent — but the **quote used for the refund leg is taken from whatever pool state exists at post-dispatch time**, with no comparison to the rate used at withdrawal time.

Because `Utility::batch_all` (or any multi-call construct) lets the attacker place an arbitrary call between the extension's `prepare` and `post_dispatch_details` phases, the attacker can:
1. Submit `ChargeAssetTxPayment::from(tip, Some(asset_id))` wrapping `Utility::batch_all([manipulate_call, target_call])`.
2. `withdraw_fee` executes: `asset_id` → `A` swap at the *original* pool price, pushing `A`'s price up slightly (unavoidable protocol cost).
3. The batch's `manipulate_call` (e.g., a direct `AssetConversion::swap_tokens_for_exact_tokens` call funded by the attacker's own capital) executes, buying more `A` with `asset_id`, pushing `A`'s price up further. This trade's AMM weight cost is essentially fixed regardless of trade size, so the attacker can scale the manipulation trade size up using only capital, without materially increasing the extrinsic's consumed weight.
4. `correct_and_deposit_fee` executes post-dispatch: it quotes and swaps `A` (the `refund_amount`, sized by the gap between the pre-dispatch weight estimate and the real post-dispatch weight) for `asset_id` **at the now-inflated `A` price**, crediting the attacker with more `asset_id` than a non-manipulated refund would have yielded.
5. The attacker may unwind the manipulation position (sell the acquired `A` back) at will; because the "victim" leg (the extension's forced refund swap of `refund_amount`) is independent of the attacker's manipulation trade size, the classic AMM sandwich-profitability result applies: an attacker choosing an optimal manipulation size can realize positive net profit at the LPs'/pool's expense, extracted through the tx-payment refund mechanism.

No check in `correct_and_deposit_fee` bounds the refund conversion rate relative to the rate used in `withdraw_fee`, nor limits how much the pool may have moved due to the extrinsic's own dispatched call. The existing checks (`can_deposit`, `total_balance` zero-check, `change.peek().is_zero()`) guard against balance/precision failures, not price manipulation, so they do not mitigate this.

### Impact Explanation
An unprivileged, signed account paying fees in a non-native asset via `ChargeAssetTxPayment` can extract value from the `pallet-asset-conversion` liquidity pool (ultimately paid by LPs) by batching a pool-manipulating call with any target call whose actual post-dispatch weight is meaningfully lower than its declared `DispatchInfo` weight, so that a non-trivial `refund_amount` is swapped back at an attacker-inflated price. This is a repeatable, atomic, single-block value extraction from AMM liquidity via the fee-payment machinery, not requiring any privileged access, front-running by third parties, or non-atomic timing assumptions.

### Likelihood Explanation
Preconditions are entirely within a normal user's control: pay fees with `ChargeAssetTxPayment::from(tip, Some(asset_id))`, wrap `[manipulate_call, target_call]` in `Utility::batch_all`, and choose a `target_call` whose worst-case declared weight materially exceeds its realized (post-dispatch) weight to obtain a non-trivial `refund_amount`. The manipulation call cost scales with capital, not with the (fixed) AMM-swap weight, so larger manipulations barely shrink the exploitable refund. This is reproducible on any chain configuring `SwapAssetAdapter` for `pallet-asset-conversion-tx-payment` with sufficient pool depth relative to typical fee-refund sizes.

### Recommendation
Do not let the refund leg re-price against pool state that has moved due to the extrinsic's own dispatched call. Options: (a) cache/carry a price bound established during `withdraw_fee` (e.g., min-acceptable-refund derived from the pre-dispatch rate) and reject/clamp refunds that exceed that bound; (b) perform the refund swap using a TWAP/oracle-resistant price source rather than the instantaneous spot AMM state; (c) disallow the refund-swap direction from benefiting from price moves that occurred strictly within the same extrinsic's dispatch window, e.g., by snapshotting reserves before dispatch and using the minimum of the pre- and post-dispatch implied rates for the refund.

### Proof of Concept
Extend `substrate/frame/transaction-payment/asset-conversion-tx-payment/src/tests.rs` (near `native_asset_refund_reports_corrected_fee_in_event`) with a test that:
1. Sets up an asset/native pool via `setup_lp`.
2. Constructs `ChargeAssetTxPayment::from(tip, Some(asset_id))`, calls `validate_and_prepare` to perform `withdraw_fee` (asserting the resulting pool reserves).
3. Between `prepare` and `post_dispatch_details`, directly invokes `AssetConversion::swap_tokens_for_exact_tokens` (simulating the batched `manipulate_call`) to shift the pool price in the direction favorable to the refund leg.
4. Calls `post_dispatch_details` (triggering `correct_and_deposit_fee`) and asserts:
   - the `expected_token_refund` computed against the **manipulated** post-call reserves is strictly greater than the refund that would have been computed against the **pre-manipulation** reserves;
   - the caller's net asset balance change plus the value of tokens acquired in the manipulation trade (valued at the pool's pre-manipulation price) is positive, demonstrating net extractable profit versus the no-manipulation baseline.

### Citations

**File:** substrate/frame/transaction-payment/asset-conversion-tx-payment/src/lib.rs (L327-343)
```rust
	fn prepare(
		self,
		val: Self::Val,
		_origin: &<T::RuntimeCall as Dispatchable>::RuntimeOrigin,
		call: &T::RuntimeCall,
		info: &DispatchInfoOf<T::RuntimeCall>,
		_len: usize,
	) -> Result<Self::Pre, TransactionValidityError> {
		match val {
			Val::Charge { tip, who, fee } => {
				// Mutating call of `withdraw_fee` to actually charge for the transaction.
				let (_fee, initial_payment) = self.withdraw_fee(&who, call, info, fee)?;
				Ok(Pre::Charge { tip, who, initial_payment, weight: self.weight(call) })
			},
			Val::NoCharge => Ok(Pre::NoCharge { refund: self.weight(call) }),
		}
	}
```

**File:** substrate/frame/transaction-payment/asset-conversion-tx-payment/src/lib.rs (L389-420)
```rust
			InitialPayment::Asset((asset_id, already_withdrawn)) => {
				// Take into account the weight used by this extension before calculating the
				// refund.
				let actual_ext_weight = <T as Config>::WeightInfo::charge_asset_tx_payment_asset();
				let unspent_weight = extension_weight.saturating_sub(actual_ext_weight);
				let mut actual_post_info = *post_info;
				actual_post_info.refund(unspent_weight);
				let actual_fee = pallet_transaction_payment::Pallet::<T>::compute_actual_fee(
					len as u32,
					info,
					&actual_post_info,
					tip,
				);
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

				Ok(unspent_weight)
			},
```

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

**File:** substrate/frame/transaction-payment/asset-conversion-tx-payment/src/payment.rs (L259-317)
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
			// The error should not occur since swap was quoted before.
			Err((refund, _)) => {
				defensive!(
					"Refund swap should pass for the quoted amount",
					(refund.asset(), refund.peek(), refund_asset_amount, who)
				);
				// cancel `refund` and include it back into `adjusted_paid`.
				adjusted_paid.merge(refund).map_or_else(
					|(adjusted_paid, refund)| {
						defensive!(
							"`adjusted_paid` and `refund` are credits of the same asset.",
							(adjusted_paid.asset(), refund.asset(), who)
						);
						// drop `refund` and return `adjusted_paid` without it.
						(fee_asset_amount, adjusted_paid)
					},
					|fee_paid| (fee_asset_amount, fee_paid),
				)
			},
		};
```
