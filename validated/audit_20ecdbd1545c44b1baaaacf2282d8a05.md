Audit Report

## Title
Unbounded refund-swap quote allows AMM price manipulation to extract excess asset value in `correct_and_deposit_fee` - (File: substrate/frame/transaction-payment/asset-conversion-tx-payment/src/payment.rs)

## Summary
`SwapAssetAdapter::withdraw_fee` and `SwapAssetAdapter::correct_and_deposit_fee` perform two independent AMM swaps at two different points in time — before and after the dispatched call executes — and the refund leg's quoted amount (`refund_asset_amount`) is never checked against the amount originally withdrawn (`fee_asset_amount`). This allows a user who can shift the `pallet_asset_conversion` pool price between the two swaps (e.g., via a swap bundled in the very call being fee-charged) to receive back more `asset_id` than was taken, extracting value from the pool's liquidity providers while the native-side accounting to `OU` remains unaffected.

## Finding Description
In `withdraw_fee`, `asset_fee` (`fee_asset_amount`) is quoted via `S::quote_price_tokens_for_exact_tokens` and withdrawn/swapped at the pool state prior to the extrinsic's call being dispatched. [1](#0-0) 

In `correct_and_deposit_fee`, which runs in `post_dispatch` after the call has executed, `refund_amount` is computed purely in native terms and then independently re-quoted into `asset_id` via `S::quote_price_exact_tokens_for_tokens` at the pool's *current* (post-call) state, with no comparison to `fee_asset_amount`: [2](#0-1) [3](#0-2) 

The only guard, `can_deposit`, verifies the recipient account can hold the resulting tokens — it does not bound the amount relative to what was withdrawn. The actual balance-changing swap executes with `refund_asset_amount` as the exact-out target with no upper clamp tied to `fee_asset_amount`: [4](#0-3) 

Existing tests confirm the refund is quoted at whatever the *current* pool price is at post-dispatch time, independent of the withdrawal price, and can approach the full original fee amount even without any deliberate manipulation (refund of 199 against an original 201 fee-asset withdrawal, i.e., the pool's spread is the only friction): [5](#0-4) 

Because `pallet_asset_conversion` pools and swaps are permissionless, and the dispatched call executes strictly between the withdraw quote and the refund quote, a user can bundle an AMM-price-shifting action into the very extrinsic being fee-charged (e.g., via `pallet_utility::batch`) to push the post-call quote in their favor, causing `refund_asset_amount` to exceed `fee_asset_amount`. Since typical fee-refund scenarios (large weight overestimation or `Pays::No` calls) already refund a value close to the full originally-withdrawn amount even without manipulation, only a modest price shift is needed to flip the sign and produce net extraction from the pool rather than a legitimate partial refund.

## Impact Explanation
This breaks the implicit accounting invariant that the fee-asset flow into/out of a user's account for a single fee-payment cycle should never exceed the fee-native-equivalent value actually consumed. An unprivileged user can use ordinary swap/liquidity actions bundled in their own extrinsic to cause the pallet to pay out more `asset_id` in the refund than was collected in the withdrawal, funded by the AMM pool's reserves (and thus by other liquidity providers), while `OU` (e.g., treasury) accounting stays nominally correct since it's entirely native-denominated. This is a genuine value-extraction vector against a live `pallet_asset_conversion` pool/LPs, not merely a cosmetic accounting issue.

## Likelihood Explanation
The exploit needs only ordinary, permissionless capabilities: a live pool for the chosen `asset_id`/native pair, the ability to bundle a price-moving swap inside the same dispatched call (e.g., `pallet_utility::batch`) or via a preceding same-block extrinsic, and payment of the fee in a non-native asset via `ChargeAssetTxPayment`. No privileged access or unusual chain conditions are required. Profitability is bounded by the AMM swap fees paid while manipulating price and by the size of `refund_amount` (capped by the estimated fee), so it is most attractive against thin-liquidity pools or scenarios with large weight refunds/`Pays::No` calls, but it is a deterministic, repeatable strategy rather than a probabilistic one.

## Recommendation
Bound the refund swap so it cannot return more `asset_id` than was originally withdrawn for the fee, e.g., cap `refund_asset_amount` at a pro-rata share of `fee_asset_amount` (`refund_asset_amount = min(quoted_amount, fee_asset_amount * refund_amount / fee)`), or record the effective exchange rate from `withdraw_fee` and reject/clamp the refund swap if the post-call price is more favorable than that recorded rate. At minimum add `ensure!(refund_asset_amount <= fee_asset_amount, ...)` before performing the refund swap in `correct_and_deposit_fee`.

## Proof of Concept
1. Create a `pallet_asset_conversion` pool for `(Native, FeeAsset)` with modest liquidity.
2. Attacker submits an extrinsic paid via `ChargeAssetTxPayment` in `FeeAsset`, wrapping the actual call in `pallet_utility::batch` together with a `pallet_asset_conversion` swap/liquidity action that shifts the pool price favorably between `withdraw_fee` (pre-dispatch) and `correct_and_deposit_fee` (post-dispatch).
3. Use a call shape that naturally yields a large `refund_amount` (e.g., large weight overestimation or a `Pays::No` sub-call), following the pattern already exercised in `transaction_payment_without_fee` in `substrate/frame/transaction-payment/asset-conversion-tx-payment/src/tests.rs` (lines 345-433), but adding the price-shifting action inside the batched call.
4. Assert `refund_asset_amount > fee_asset_amount` by comparing the `Withdrawn`/`Deposited` events, while confirming `OU`'s native-side total (`FeeUnbalancedAmount`/`TipUnbalancedAmount`) remains exactly `corrected_fee`/`tip`, demonstrating the excess `asset_id` came from the pool rather than any native-fee shortfall.

### Citations

**File:** substrate/frame/transaction-payment/asset-conversion-tx-payment/src/payment.rs (L142-157)
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
```

**File:** substrate/frame/transaction-payment/asset-conversion-tx-payment/src/payment.rs (L221-222)
```rust
		let (fee_paid, fee_asset_amount) = already_withdrawn;
		let refund_amount = fee_paid.peek().saturating_sub(corrected_fee);
```

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

**File:** substrate/frame/transaction-payment/asset-conversion-tx-payment/src/payment.rs (L279-297)
```rust
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

**File:** substrate/frame/transaction-payment/asset-conversion-tx-payment/src/tests.rs (L404-422)
```rust
			let refund = AssetConversion::quote_price_exact_tokens_for_tokens(
				NativeOrWithId::Native,
				NativeOrWithId::WithId(asset_id),
				fee_in_native,
				true,
			)
			.unwrap();
			assert_eq!(refund, 199);

			assert_ok!(ChargeAssetTxPayment::<Runtime>::post_dispatch_details(
				pre,
				&info_from_weight(WEIGHT_5),
				&post_info_from_pays(Pays::No),
				len,
				&Ok(()),
			));

			// caller should get refunded
			assert_eq!(Assets::balance(asset_id, caller), balance - fee_in_asset + refund);
```
