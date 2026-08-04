Confirmed: `ChargeAssetTxPayment<T>` in `substrate/frame/transaction-payment/asset-conversion-tx-payment/src/lib.rs` only carries `tip` and `asset_id` — there is no user-supplied slippage/maximum-asset-fee bound field [1](#0-0) .

### Title
Unbounded spot-price fee conversion in `pallet-asset-conversion-tx-payment` enables sandwich-style fee overcharging - (File: `substrate/frame/transaction-payment/asset-conversion-tx-payment/src/payment.rs`)

### Summary
The `SwapAssetAdapter`/`OnChargeAssetTransaction` implementation prices non-native transaction fees using the live, unprotected constant-product spot price of `pallet-asset-conversion` pools (an on-chain AMM analogous to Uniswap V2), with no user-supplied cap on how much of the fee-asset may be spent.

### Finding Description
`withdraw_fee` computes `asset_fee` via `S::quote_price_tokens_for_exact_tokens(asset_id, A::get(), fee, true)`, which reads the pool's current reserves (`get_reserves`) and applies the constant-product formula — the direct analog of Uniswap's `slot0` spot price used in the Predy report [2](#0-1) . Unlike the `swap_exact_tokens_for_tokens`/`swap_tokens_for_exact_tokens` extrinsics, which take explicit `amount_out_min`/`amount_in_max` parameters from the caller [3](#0-2) , `ChargeAssetTxPayment` exposes no such bound: its only fields are `tip` and `asset_id` [1](#0-0) . The refund path (`correct_and_deposit_fee`) similarly re-quotes and swaps using `quote_price_exact_tokens_for_tokens` at whatever price the pool has when the transaction is finally included [4](#0-3) . The pallet's own docs and code comments repeatedly caveat that "the price may have changed by the time the transaction is executed. (Use `amount_out_min`/`amount_in_max` to control slippage.)" [5](#0-4) [6](#0-5)  — but `ChargeAssetTxPayment` never lets a signer set that bound for the *fee-payment* swap it performs on their behalf.

Because the quote and the corresponding swap are executed back-to-back inside a single extrinsic (no intervening call), there is no reentrancy-style manipulation *within* the fee-charging call itself. The exposure instead exists across transaction ordering within a block/mempool: an adversary who can place a large `swap_exact_tokens_for_tokens` call immediately before a victim's fee-paying transaction (via tip/priority manipulation, or if they are the block author) can shift the pool reserves so that the victim's `quote_price_tokens_for_exact_tokens` call returns a far larger `asset_fee` than the "fair" price, then reverse the swap afterward, extracting the difference as MEV. This mirrors the report's core defect class ("unchecked spot price feeding an unprotected calculation, manipulable by an adversary who can move the pool in the same window") but manifests as a sandwich/front-run rather than a Uniswap-V3-style flash loan, since `pallet-asset-conversion` has no native flash-loan primitive.

### Impact Explanation
A victim paying fees in a non-native asset via `ChargeAssetTxPayment` can be forced to surrender substantially more of that asset than the fair-market fee, with the excess captured by the attacker/manipulator. Severity is bounded by: (a) the fee amounts involved are typically small relative to a full trade, (b) it requires capital to move the pool and precise transaction ordering, and (c) it affects only chains/runtimes that configure `pallet-asset-conversion-tx-payment` with `SwapAssetAdapter` and thin pools. This is a real but modest-value, availability-of-capital-gated loss for the victim, not a protocol-insolvency bug.

### Likelihood Explanation
Any unprivileged user can submit ordinary `swap_exact_tokens_for_tokens` calls to shift a pool's reserves; ordering relative to a target's fee-paying transaction can be influenced through tips/priority in the transaction pool, and is trivially guaranteed if the attacker is (or colludes with) the block author/collator. No privileged role or governance action is required. Realistic likelihood is higher on chains with shallow, low-liquidity fee-asset pools and near negligible on deep pools, since price impact for a given capital outlay is proportional to pool depth.

### Recommendation
Add an optional maximum-asset-amount (slippage bound) field to `ChargeAssetTxPayment`, analogous to `amount_in_max`/`amount_out_min` on the underlying swap extrinsics, and reject the extension in `validate`/`prepare` if the quoted `asset_fee` (or refund) exceeds it. Alternatively/additionally, consider using a time-weighted or block-delay-resistant price source for fee-conversion rather than the instantaneous pool ratio, consistent with the mitigation Predy was advised to adopt (TWAP instead of spot price).

### Proof of Concept
Conceptual sequence (not executed, derived from code review):
1. Victim broadcasts a transaction with `ChargeAssetTxPayment::from(tip, Some(asset_id))` intending to pay a small, predictable fee in `asset_id`.
2. Attacker observes the pending transaction and submits `AssetConversion::swap_exact_tokens_for_tokens` with a large amount to skew the `(asset_id, native)` pool reserves, prioritized (via tip or by being the block author) to execute immediately before the victim's transaction.
3. When the victim's transaction executes, `withdraw_fee` calls `quote_price_tokens_for_exact_tokens(asset_id, native, fee, true)` [2](#0-1)  against the manipulated reserves, returning an inflated `asset_fee`, which is withdrawn from the victim with no cap check.
4. Attacker submits a reverse swap to restore the pool and realizes the extracted spread as profit; this is testable in the existing `substrate/frame/transaction-payment/asset-conversion-tx-payment/src/tests.rs` harness (e.g. `setup_lp`) by manipulating pool reserves between quoting and dispatch and observing `fee_in_asset` scale with the manipulated ratio.

**Note on confidence**: This is a plausible analog derived from static code review; I was not able to execute a live PoC in this environment, and the actual exploitability (magnitude of extractable value, and feasibility of guaranteed ordering without being a collator) depends on runtime-specific pool depth and mempool/ordering assumptions that are outside what the indexed code alone can confirm.

### Citations

**File:** substrate/frame/transaction-payment/asset-conversion-tx-payment/src/lib.rs (L176-191)
```rust
#[derive(Encode, Decode, DecodeWithMemTracking, Clone, Eq, PartialEq, TypeInfo)]
#[scale_info(skip_type_params(T))]
pub struct ChargeAssetTxPayment<T: Config> {
	#[codec(compact)]
	tip: BalanceOf<T>,
	asset_id: Option<T::AssetId>,
}

impl<T: Config> ChargeAssetTxPayment<T>
where
	T::RuntimeCall: Dispatchable<Info = DispatchInfo, PostInfo = PostDispatchInfo>,
{
	/// Utility constructor. Used only in client/factory code.
	pub fn from(tip: BalanceOf<T>, asset_id: Option<T::AssetId>) -> Self {
		Self { tip, asset_id }
	}
```

**File:** substrate/frame/transaction-payment/asset-conversion-tx-payment/src/payment.rs (L142-146)
```rust
		// Quote the amount of the `asset_id` needed to pay the fee in the asset `A`.
		let asset_fee =
			S::quote_price_tokens_for_exact_tokens(asset_id.clone(), A::get(), fee, true)
				.filter(|asset_fee| !asset_fee.is_zero())
				.ok_or(InvalidTransaction::Payment)?;
```

**File:** substrate/frame/transaction-payment/asset-conversion-tx-payment/src/payment.rs (L259-287)
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
```

**File:** substrate/frame/asset-conversion/src/lib.rs (L521-545)
```rust
		/// you're happy to receive.
		///
		/// [`AssetConversionApi::quote_price_exact_tokens_for_tokens`] runtime call can be called
		/// for a quote.
		#[pallet::call_index(3)]
		#[pallet::weight(T::WeightInfo::swap_exact_tokens_for_tokens(path.len() as u32))]
		pub fn swap_exact_tokens_for_tokens(
			origin: OriginFor<T>,
			path: Vec<Box<T::AssetKind>>,
			amount_in: T::Balance,
			amount_out_min: T::Balance,
			send_to: T::AccountId,
			keep_alive: bool,
		) -> DispatchResult {
			let sender = ensure_signed(origin)?;
			Self::do_swap_exact_tokens_for_tokens(
				sender,
				path.into_iter().map(|a| *a).collect(),
				amount_in,
				Some(amount_out_min),
				send_to,
				keep_alive,
			)?;
			Ok(())
		}
```

**File:** substrate/frame/asset-conversion/src/lib.rs (L1516-1522)
```rust
		/// Gets a quote for swapping an exact amount of `asset1` for `asset2`.
		///
		/// If `include_fee` is true, the quote will include the liquidity provider fee.
		/// If the pool does not exist or has no liquidity, `None` is returned.
		/// Note that the price may have changed by the time the transaction is executed.
		/// (Use `amount_out_min` to control slippage.)
		/// Returns `Some(quoted_amount)` on success.
```

**File:** substrate/frame/asset-conversion/src/lib.rs (L1615-1630)
```rust
		/// Provides a quote for [`Pallet::swap_tokens_for_exact_tokens`].
		///
		/// Note that the price may have changed by the time the transaction is executed.
		/// (Use `amount_in_max` to control slippage.)
		fn quote_price_tokens_for_exact_tokens(
			asset1: AssetId,
			asset2: AssetId,
			amount: Balance,
			include_fee: bool,
		) -> Option<Balance>;

		/// Provides a quote for [`Pallet::swap_exact_tokens_for_tokens`].
		///
		/// Note that the price may have changed by the time the transaction is executed.
		/// (Use `amount_out_min` to control slippage.)
		fn quote_price_exact_tokens_for_tokens(
```
