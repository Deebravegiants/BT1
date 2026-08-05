Yes — the same *manipulable single-source spot price* vulnerability class exists in this codebase, in `pallet-asset-conversion` (a Uniswap V2-style on-chain AMM) and its consumer `pallet-asset-conversion-tx-payment`, which uses the pool's *instantaneous reserve ratio* as the price source for paying transaction fees in non-native assets.

### Title
On-chain transaction-fee pricing relies on manipulable AMM spot price with no TWAP protection - (File: `substrate/frame/transaction-payment/asset-conversion-tx-payment/src/payment.rs`)

### Summary
`pallet_asset_conversion` computes swap prices directly from the current reserve balances of a liquidity pool (`Pallet::get_reserves`, `Pallet::quote_price_tokens_for_exact_tokens`), exactly the "single DEX / no TWAP" pattern flagged in the external report. `SwapAssetAdapter::withdraw_fee` in `pallet-asset-conversion-tx-payment` uses this spot quote to decide how much of a user-chosen asset to withdraw to cover a transaction fee. [1](#0-0) [2](#0-1) 

### Finding Description
`quote_price_tokens_for_exact_tokens` and `quote_price_exact_tokens_for_tokens` read `T::Assets` balances of the pool account (`get_reserves`) at call time and apply the constant-product formula — an on-chain analog to Uniswap V2 spot pricing: [3](#0-2) 

The pallet's own `QuotePrice` trait doc explicitly acknowledges the staleness/manipulation risk: *"The quoted price is only guaranteed if no other swaps are made after the price is quoted and before the target swap."* [4](#0-3) 

`SwapAssetAdapter::withdraw_fee`, used by the `ChargeAssetTxPayment` signed extension, quotes and immediately swaps the user's chosen `asset_id` for the fee-asset `A`, using whatever the pool reserves are at that moment in the block: [5](#0-4) 

Since reserves are ordinary on-chain storage mutated by any `swap_exact_tokens_for_tokens`/`swap_tokens_for_exact_tokens` extrinsic, an attacker (or a block-producing collator) can:
1. Submit a swap that skews the pool's reserve ratio in their favor.
2. Submit (or have ordered next in the same block) the fee-paying extrinsic, whose `withdraw_fee` will quote the fee-asset amount off the skewed reserves.
3. Submit a reverse swap to restore the pool, keeping the discount as profit (minus round-trip LP fees).

This mirrors the "manipulate the single-source spot price to pay lower fees" scenario described for `RadiantOFT._getBridgeFee()` in the external report — the mechanism (constant-product spot price, no time-weighting) and the attacker goal (reduce a fee calculated from that price) are structurally identical.

### Impact Explanation
A successful manipulation lets a user underpay transaction fees when paying in a non-native asset, at the expense of the pool's liquidity providers (value extraction via a self-sandwich) and at the expense of the fee mechanism's anti-spam/anti-DoS guarantee (fees are supposed to reflect real economic cost). Impact scales with how "thin" (low-liquidity) the relevant asset-conversion pool is — thin pools are cheap to move.

### Likelihood Explanation
Likelihood is bounded by two factors that reduce it well below the original DeFi report's severity:
- There is no flashloan primitive in this codebase to size an attack for free; the attacker must actually own/lock capital for the round-trip swaps within the same block.
- The manipulation requires favorable extrinsic ordering within a single block (attacker-controlled ordering, e.g., as a block author/collator, or lucky mempool ordering), since `withdraw_fee`'s quote-and-swap happen atomically back-to-back and cannot be manipulated *within* the same call.
- Runtimes are free to choose which pools/assets are accepted for `ChargeAssetTxPayment`, and can restrict this to deep, governance-vetted pools, which is the deployed mitigation in the actual asset-hub runtimes.

This is a realistic but low-severity/likelihood griefing vector against thin pools rather than a critical, broadly-exploitable issue, and it is a known, documented limitation of the `QuotePrice` design rather than an unknown root cause.

### Recommendation
- Where `pallet-asset-conversion` prices are used for security/economically-sensitive decisions (fee payment, collateral valuation, etc.), prefer a time-weighted or multi-block-delayed price rather than the instantaneous spot reserve ratio, or restrict `ChargeAssetTxPayment`-eligible pools to deep, permissioned/governance-approved pools.
- Consider adding a slippage/deviation check comparing the quoted spot price against a recent historical average before using it for fee withdrawal.

### Proof of Concept
Conceptual (no working exploit code required by scope, but the mechanics):
1. Attacker funds a thin `AssetConversion` pool for `(NativeAsset, TargetAsset)`.
2. In block N, attacker submits `swap_exact_tokens_for_tokens` swapping a large amount of `TargetAsset` into the pool, sharply increasing `TargetAsset`'s price relative to `NativeAsset` reserves.
3. Attacker (or victim) submits a `ChargeAssetTxPayment`-covered extrinsic specifying `asset_id = TargetAsset`; `withdraw_fee` calls `quote_price_tokens_for_exact_tokens(TargetAsset, Native, fee, true)` against the skewed reserves, yielding a smaller-than-fair `asset_fee`.
4. Attacker submits a reverse swap to restore the pool and recapture most of the deployed capital, keeping the fee discount as profit (net of LP fees). [6](#0-5) [7](#0-6)

### Citations

**File:** substrate/frame/asset-conversion/src/lib.rs (L1499-1514)
```rust
		pub fn get_reserves(
			asset1: T::AssetKind,
			asset2: T::AssetKind,
		) -> Result<(T::Balance, T::Balance), Error<T>> {
			let pool_account = T::PoolLocator::pool_address(&asset1, &asset2)
				.map_err(|_| Error::<T>::InvalidAssetPair)?;

			let balance1 = Self::get_balance(&pool_account, asset1);
			let balance2 = Self::get_balance(&pool_account, asset2);

			if balance1.is_zero() || balance2.is_zero() {
				Err(Error::<T>::PoolEmpty)?;
			}

			Ok((balance1, balance2))
		}
```

**File:** substrate/frame/asset-conversion/src/lib.rs (L1516-1562)
```rust
		/// Gets a quote for swapping an exact amount of `asset1` for `asset2`.
		///
		/// If `include_fee` is true, the quote will include the liquidity provider fee.
		/// If the pool does not exist or has no liquidity, `None` is returned.
		/// Note that the price may have changed by the time the transaction is executed.
		/// (Use `amount_out_min` to control slippage.)
		/// Returns `Some(quoted_amount)` on success.
		pub fn quote_price_exact_tokens_for_tokens(
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

			let amount_out = if include_fee {
				let fee = Self::pool_fee_for(&asset1, &asset2).ok()?;
				Self::get_amount_out(fee, &amount, &balance1, &balance2).ok()?
			} else {
				Self::quote(&amount, &balance1, &balance2).ok()?
			};

			// Small inputs can round output to zero due to integer division.
			if amount_out.is_zero() {
				return None;
			}

			// Swap withdrawals from pools use `keep_alive=true` (Preserve). Use the same
			// preservation level to determine the actual withdrawable amount.
			let max_output = T::Assets::reducible_balance(asset2, &pool_account, Preserve, Polite);
			if amount_out > max_output {
				return None;
			}

			Some(amount_out)
		}
```

**File:** substrate/frame/transaction-payment/asset-conversion-tx-payment/src/payment.rs (L119-176)
```rust
	fn withdraw_fee(
		who: &T::AccountId,
		_call: &T::RuntimeCall,
		_dispatch_info: &DispatchInfoOf<<T>::RuntimeCall>,
		asset_id: Self::AssetId,
		fee: Self::Balance,
		_tip: Self::Balance,
	) -> Result<Self::LiquidityInfo, TransactionValidityError> {
		if asset_id == A::get() {
			// The `asset_id` is the target asset, we do not need to swap.
			let fee_credit = F::withdraw(
				asset_id.clone(),
				who,
				fee,
				Precision::Exact,
				Preservation::Preserve,
				Fortitude::Polite,
			)
			.map_err(|_| InvalidTransaction::Payment)?;

			return Ok((fee_credit, fee));
		}

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

**File:** substrate/frame/asset-conversion/src/swap.rs (L116-120)
```rust
/// Trait providing methods to quote swap prices between asset classes.
///
/// The quoted price is only guaranteed if no other swaps are made after the price is quoted and
/// before the target swap (e.g., the swap is made immediately within the same transaction).
pub trait QuotePrice {
```
