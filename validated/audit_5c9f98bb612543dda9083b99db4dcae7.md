Audit Report

## Title
Fee-in-asset payment relies on manipulable on-chain AMM spot price with no user-supplied slippage bound - ([File: substrate/frame/transaction-payment/asset-conversion-tx-payment/src/payment.rs])

## Summary
`SwapAssetAdapter::withdraw_fee`, `can_withdraw_fee`, and `correct_and_deposit_fee` in `pallet-asset-conversion-tx-payment` derive the amount of a non-native asset a signer must pay for fees purely from `pallet-asset-conversion`'s live constant-product reserves via `quote_price_tokens_for_exact_tokens`/`quote_price_exact_tokens_for_tokens`, and `ChargeAssetTxPayment` provides no caller-supplied maximum/minimum bound on that amount. [1](#0-0) [2](#0-1)  This allows an unprivileged attacker who can influence intra-block ordering to skew the pool ratio immediately before the victim's `prepare()`/`post_dispatch_details()` executes, forcing the victim to overpay in the non-native asset or receive a reduced refund.

## Finding Description
`withdraw_fee` quotes the exact amount of `asset_id` needed to cover a fee via `S::quote_price_tokens_for_exact_tokens(asset_id, A::get(), fee, true)` and immediately withdraws and swaps that amount with no bound check against a caller-supplied maximum. [1](#0-0)  The same unbounded quote is used in `can_withdraw_fee` (dry run during `validate`) [3](#0-2)  and in the refund path of `correct_and_deposit_fee`, which quotes `S::quote_price_exact_tokens_for_tokens` at post-dispatch time. [4](#0-3) 

`quote_price_tokens_for_exact_tokens` computes the price directly and only from the pool's current on-chain reserves (`get_reserves`) via `get_amount_in`, i.e., a pure constant-product spot price with no time-weighting, oracle, or manipulation resistance. [5](#0-4) 

`ChargeAssetTxPayment` only carries `tip` and `asset_id`, with no `max_asset_fee`/`amount_in_max`-style field: [2](#0-1)  and both `validate()` and `prepare()` independently re-derive the fee amount from live pool state and unconditionally act on it, with no slippage guard exposed to the transaction author: [6](#0-5) 

I verified all cited code paths directly and confirm they match the claim's description exactly — the spot price is indeed derived solely from current reserves, and no slippage-bound field exists on `ChargeAssetTxPayment` or is threaded through `OnChargeAssetTransaction`.

## Impact Explanation
This is a legitimate design gap: a user paying fees in a non-native asset can be forced to pay more of that asset than fair market rate if pool reserves are manipulated immediately before their extrinsic executes, and/or receive a smaller refund on the correction path. Ordinary swappers in `pallet-asset-conversion` get `amount_out_min`/`amount_in_max` protection via `swap_exact_tokens_for_tokens`/`swap_tokens_for_exact_tokens`, but `ChargeAssetTxPayment` offers no equivalent protection to the fee payer. The magnitude of extractable value is bounded by pool depth relative to the fee size, making this most exploitable against thin asset/native pools — consistent with the report's own characterization of limited-but-real economic damage rather than protocol insolvency.

## Likelihood Explanation
Pool manipulation via `swap_exact_tokens_for_tokens`/`swap_tokens_for_exact_tokens` is callable by any unprivileged account, satisfying the "no privileged role required" and "unprivileged user path" requirements. However, exploitability is conditioned on the attacker's ability to reliably order their manipulation transaction immediately before the victim's fee-paying extrinsic within the same block and reverse it afterward — a realistic but non-trivial MEV/searcher capability that depends on the specific chain's block-authoring/mempool visibility model (not something demonstrated with a concrete reproducible harness in this report, only asserted as "realistic on parachains with public transaction pools"). This is analogous to well-known sandwich-attack risk in any AMM-based on-chain pricing mechanism without slippage protection, which is a recognized (if not fully eliminated) design tradeoff in these pallets rather than a memory-safety or accounting-invariant-breaking bug — the pool's own invariants remain intact; only the fee-payer's economic outcome is affected.

## Recommendation
Add a caller-supplied slippage bound to `ChargeAssetTxPayment` (e.g., `max_asset_fee: Option<Balance>`), thread it through `OnChargeAssetTransaction::withdraw_fee`/`can_withdraw_fee`/`correct_and_deposit_fee`, and fail validation if the quoted `asset_fee` (or refund) exceeds/falls below the caller's tolerance — mirroring the `amount_in_max`/`amount_out_min` protections already available to ordinary `pallet-asset-conversion` swappers.

## Proof of Concept
1. Create a shallow `NativeOrWithId::WithId(asset)`/`Native` pool via `pallet_asset_conversion::create_pool` + `add_liquidity`.
2. Victim submits a signed extrinsic using `ChargeAssetTxPayment::from(tip, Some(asset_id))`.
3. Attacker submits, and ensures gets ordered before, a large `swap_exact_tokens_for_tokens` skewing the pool ratio to make `asset_id` expensive relative to native currency.
4. Victim's `prepare()` invokes `withdraw_fee`, which calls `S::quote_price_tokens_for_exact_tokens(asset_id, Native, fee, true)` against the skewed reserves, returning an inflated `asset_fee` withdrawn from the victim (substrate/frame/transaction-payment/asset-conversion-tx-payment/src/payment.rs, lines 142-157).
5. Attacker submits a reverse swap after the victim's extrinsic to restore the pool and realize the profit extracted from the victim's overpayment.

A unit test demonstrating this would construct a mock runtime with `pallet-asset-conversion` + `SwapAssetAdapter`, seed a pool, invoke a swap to shift reserves, then call `ChargeAssetTxPayment::validate`/`prepare` and assert the withdrawn `asset_fee` differs materially from the pre-manipulation quote — this exact scenario is not present in the existing test suite (`substrate/frame/transaction-payment/asset-conversion-tx-payment/src/tests.rs`), so the report's PoC steps are plausible but unverified by an existing executable test.

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

**File:** substrate/frame/transaction-payment/asset-conversion-tx-payment/src/payment.rs (L196-205)
```rust
		let asset_fee =
			S::quote_price_tokens_for_exact_tokens(asset_id.clone(), A::get(), fee, true)
				.filter(|asset_fee| !asset_fee.is_zero())
				.ok_or(InvalidTransaction::Payment)?;

		// Ensure we can withdraw enough `asset_id` for the swap.
		match F::can_withdraw(asset_id.clone(), who, asset_fee) {
			WithdrawConsequence::Success => {},
			_ => return Err(TransactionValidityError::from(InvalidTransaction::Payment)),
		};
```

**File:** substrate/frame/transaction-payment/asset-conversion-tx-payment/src/payment.rs (L259-266)
```rust
		// refund is non zero and `who`'s fee `asset_id` is not the target asset.

		// check if the refund amount can be swapped back into `who`'s fee `asset_id`.
		let refund_asset_amount =
			S::quote_price_exact_tokens_for_tokens(A::get(), asset_id.clone(), refund_amount, true)
				// No refund given if it cannot be swapped back.
				.unwrap_or(Zero::zero());

```

**File:** substrate/frame/transaction-payment/asset-conversion-tx-payment/src/lib.rs (L176-182)
```rust
#[derive(Encode, Decode, DecodeWithMemTracking, Clone, Eq, PartialEq, TypeInfo)]
#[scale_info(skip_type_params(T))]
pub struct ChargeAssetTxPayment<T: Config> {
	#[codec(compact)]
	tip: BalanceOf<T>,
	asset_id: Option<T::AssetId>,
}
```

**File:** substrate/frame/transaction-payment/asset-conversion-tx-payment/src/lib.rs (L305-343)
```rust
	fn validate(
		&self,
		origin: <T::RuntimeCall as Dispatchable>::RuntimeOrigin,
		call: &T::RuntimeCall,
		info: &DispatchInfoOf<T::RuntimeCall>,
		len: usize,
		_self_implicit: Self::Implicit,
		_inherited_implication: &impl Encode,
		_source: TransactionSource,
	) -> ValidateResult<Self::Val, T::RuntimeCall> {
		let Some(who) = origin.as_system_origin_signer() else {
			return Ok((ValidTransaction::default(), Val::NoCharge, origin));
		};
		// Non-mutating call of `compute_fee` to calculate the fee used in the transaction priority.
		let fee = pallet_transaction_payment::Pallet::<T>::compute_fee(len as u32, info, self.tip);
		self.can_withdraw_fee(&who, call, info, fee)?;
		let priority = ChargeTransactionPayment::<T>::get_priority(info, len, self.tip, fee);
		let validity = ValidTransaction { priority, ..Default::default() };
		let val = Val::Charge { tip: self.tip, who: who.clone(), fee };
		Ok((validity, val, origin))
	}

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

**File:** substrate/frame/asset-conversion/src/lib.rs (L1571-1603)
```rust
		pub fn quote_price_tokens_for_exact_tokens(
			asset1: T::AssetKind,
			asset2: T::AssetKind,
			amount: T::Balance,
			include_fee: bool,
		) -> Option<T::Balance> {
			// Swaps reject zero amounts, match that behavior.
			if amount.is_zero() {
				return None;
			}
			let pool_account = T::PoolLocator::pool_address(&asset1, &asset2).ok()?;

			let (balance1, balance2) = Self::get_reserves(asset1.clone(), asset2.clone()).ok()?;

			if balance1.is_zero() {
				return None;
			}

			// Swap withdrawals from pools use `keep_alive=true` (Preserve). Use the same
			// preservation level to determine the actual withdrawable amount.
			let max_output =
				T::Assets::reducible_balance(asset2.clone(), &pool_account, Preserve, Polite);
			if amount > max_output {
				return None;
			}

			if include_fee {
				let fee = Self::pool_fee_for(&asset1, &asset2).ok()?;
				Self::get_amount_in(fee, &amount, &balance1, &balance2).ok()
			} else {
				Self::quote(&amount, &balance2, &balance1).ok()
			}
		}
```
