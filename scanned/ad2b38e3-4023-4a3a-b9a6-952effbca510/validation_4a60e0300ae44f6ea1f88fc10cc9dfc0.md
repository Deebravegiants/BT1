Found a valid analog.

### Title
Missing Slippage Protection in `swap_and_burn` Tip/Fee Swap Causes User Fund Loss - (File: bridges/snowbridge/pallets/system-frontend/src/lib.rs)

### Summary
The `pallet-snowbridge-system-frontend`'s `swap_and_burn` function invokes `T::Swap::swap_exact_tokens_for_tokens` with `amount_out_min` hardcoded to `None`, meaning the AMM swap performed by `pallet_asset_conversion::Swap` (or whatever `T::Swap` is configured to) has zero slippage protection, directly analogous to the reported `sy.redeem(..., minTokenOut: 0, ...)` pattern in the Pendle report.

### Finding Description
`register_token` and `add_tip` extrinsics allow any user to swap an arbitrary "tip"/fee asset for Ether before burning it for teleportation to Ethereum. The swap goes through `Pallet::swap_fee_asset_and_burn` → `Pallet::swap_and_burn`: [1](#0-0) 

Specifically, the call site:
```rust
let ether_gained = T::Swap::swap_exact_tokens_for_tokens(
    who.clone(),
    swap_path,
    tip_amount,
    None, // No minimum amount required
    who,
    true,
)?;
```

This is functionally identical to the Pendle bug pattern: an exact-in swap is executed with no caller-supplied minimum output, exposing the user to unbounded slippage/MEV extraction on whatever AMM backs `T::Swap` (in production this would be `pallet_asset_conversion::Pallet` as seen in [2](#0-1) , or a custom `Swap` implementation as in the mock [3](#0-2) ). Note the underlying `AssetConversion` pallet *does* correctly support and enforce `amount_out_min` (see `do_swap_exact_tokens_for_tokens` at [4](#0-3) ), but the `system-frontend` pallet deliberately discards this protection by passing `None`.

There is no computed `amount_out_min` from a quote, no user-supplied slippage parameter in `register_token`/`add_tip` call signatures, and no configuration knob to bound the swap. The comment `// No minimum amount required` documents this as an intentional design choice rather than an oversight guarded elsewhere.

### Impact Explanation
A user submitting `register_token` or `add_tip` with a non-Ether `fee_asset`/`tip` has their asset swapped for Ether at whatever price the pool offers at execution time, with no floor. In a low-liquidity pool, or under MEV sandwich conditions (a block author/relayer can reorder transactions to manipulate the pool reserves immediately before this swap executes and restore them after), the user can receive an arbitrarily small amount of Ether relative to the value of the asset they provided, then have that (small) Ether amount burned for the teleport. The loss is realized entirely by the extrinsic's signed caller, matching the "no recourse" impact described in the source report.

### Likelihood Explanation
Both `register_token` (for non-`Here` origins) and `add_tip` are open, unprivileged extrinsics callable by any signed account, so the attack surface is directly reachable without any privileged role. Exploitation requires either a thin/manipulable liquidity pool for the chosen `fee_asset`↔Ether pair or transaction-ordering control (sandwiching), both realistic on a parachain using `pallet_asset_conversion` pools that anyone can seed with minimal liquidity.

### Recommendation
Add a `min_ether_out` (or equivalent slippage bound) parameter to `register_token`/`add_tip`, thread it through `swap_fee_asset_and_burn`/`swap_and_burn`, and pass it as `Some(min_ether_out)` to `T::Swap::swap_exact_tokens_for_tokens` instead of hardcoding `None`. Alternatively, derive a safe minimum from `QuotePrice::quote_price_exact_tokens_for_tokens` at call time with a configurable tolerance, mirroring the pattern already used correctly elsewhere in the codebase (e.g. `SwapAssetAdapter::correct_and_deposit_fee` in [5](#0-4) , which quotes and supplies `Some(refund_asset_amount)` rather than `None`).

### Proof of Concept
1. Deploy/pool `pallet_asset_conversion` with a thinly-liquid pool for `(TipAsset, Ether)`.
2. Attacker/relayer observes a pending `add_tip(message_id, tip_asset)` call in the transaction queue.
3. Attacker front-runs with a large swap that moves the pool price against the tip asset, then the victim's `add_tip` executes `T::Swap::swap_exact_tokens_for_tokens(..., None, ...)` at the manipulated price, receiving far less Ether than fair value.
4. Attacker back-runs to restore the pool price and pocket the extracted value.
5. Victim's tip is burned for teleport at the degraded Ether amount, permanently losing value with no on-chain recourse since `amount_out_min` was `None`. [6](#0-5)

### Citations

**File:** bridges/snowbridge/pallets/system-frontend/src/lib.rs (L290-317)
```rust
		fn swap_and_burn(
			origin: Location,
			tip_asset_location: Location,
			ether_location: Location,
			tip_amount: u128,
		) -> Result<u128, DispatchError> {
			// Swap tip asset to ether
			let swap_path = vec![tip_asset_location.clone(), ether_location.clone()];
			let who = T::AccountIdConverter::convert_location(&origin)
				.ok_or(Error::<T>::LocationConversionFailed)?;

			let ether_gained = T::Swap::swap_exact_tokens_for_tokens(
				who.clone(),
				swap_path,
				tip_amount,
				None, // No minimum amount required
				who,
				true,
			)?;

			// Burn the ether
			let ether_asset = Asset::from((ether_location.clone(), ether_gained));

			burn_for_teleport::<T::AssetTransactor>(&origin, &ether_asset)
				.map_err(|_| Error::<T>::BurnError)?;

			Ok(ether_gained)
		}
```

**File:** substrate/frame/asset-conversion/src/swap.rs (L147-172)
```rust
impl<T: Config> Swap<T::AccountId> for Pallet<T> {
	type Balance = T::Balance;
	type AssetKind = T::AssetKind;

	fn max_path_len() -> u32 {
		T::MaxSwapPathLength::get()
	}

	#[transactional]
	fn swap_exact_tokens_for_tokens(
		sender: T::AccountId,
		path: Vec<Self::AssetKind>,
		amount_in: Self::Balance,
		amount_out_min: Option<Self::Balance>,
		send_to: T::AccountId,
		keep_alive: bool,
	) -> Result<Self::Balance, DispatchError> {
		Self::do_swap_exact_tokens_for_tokens(
			sender,
			path,
			amount_in,
			amount_out_min,
			send_to,
			keep_alive,
		)
	}
```

**File:** bridges/snowbridge/test-utils/src/mock_swap_executor.rs (L22-36)
```rust
	fn swap_exact_tokens_for_tokens(
		_sender: AccountId,
		_path: Vec<Self::AssetKind>,
		amount_in: Self::Balance,
		_amount_out_min: Option<Self::Balance>,
		_send_to: AccountId,
		_keep_alive: bool,
	) -> Result<Self::Balance, DispatchError> {
		// Special case for testing SwapError:
		// If amount_in is exactly 12345, return an error
		if amount_in == TRIGGER_SWAP_ERROR_AMOUNT {
			return Err(DispatchError::Other("Swap failed for test"));
		}
		Ok(1_000_000_000u128)
	}
```

**File:** substrate/frame/asset-conversion/src/lib.rs (L980-1002)
```rust
		pub(crate) fn do_swap_exact_tokens_for_tokens(
			sender: T::AccountId,
			path: Vec<T::AssetKind>,
			amount_in: T::Balance,
			amount_out_min: Option<T::Balance>,
			send_to: T::AccountId,
			keep_alive: bool,
		) -> Result<T::Balance, DispatchError> {
			ensure!(amount_in > Zero::zero(), Error::<T>::ZeroAmount);
			if let Some(amount_out_min) = amount_out_min {
				ensure!(amount_out_min > Zero::zero(), Error::<T>::ZeroAmount);
			}

			Self::validate_swap_path(&path)?;
			let path = Self::balance_path_from_amount_in(amount_in, path)?;

			let amount_out = path.last().map(|(_, a)| *a).ok_or(Error::<T>::InvalidPath)?;
			if let Some(amount_out_min) = amount_out_min {
				ensure!(
					amount_out >= amount_out_min,
					Error::<T>::ProvidedMinimumNotSufficientForSwap
				);
			}
```

**File:** substrate/frame/transaction-payment/asset-conversion-tx-payment/src/payment.rs (L262-287)
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
```
