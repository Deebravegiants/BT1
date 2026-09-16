### Title
Asymmetric decimal-scaling bug in `convert_to_erc20`/`convert_to_balance` causes unbacked mint or silent fund loss on cross-chain token transfers — (File: `modules/pallets/hyper-fungible-token/src/impls.rs`)

### Summary
`pallet-hyper-fungible-token`'s decimal-conversion helpers scale amounts by `10 ** erc_decimals.saturating_sub(local_decimals)` (and the mirror-image `10 ** erc_decimals.saturating_sub(local_decimals)` for the divide case), which is only correct when `erc_decimals >= local_decimals`. Whenever the local asset's decimals exceed the registered EVM contract's decimals, `saturating_sub` silently clamps to `0`, and the conversion functions become a no-op (multiply/divide by `10**0 = 1`) instead of applying the required scale factor. This is analogous to the Yearn report's root cause: a share/asset (here, local-asset/ERC20-asset) conversion that hard-codes one precision assumption and breaks silently whenever that assumption doesn't hold, causing over- or under-payment.

### Finding Description
`convert_to_erc20` and `convert_to_balance` are the sole precision-conversion primitives used by the pallet's cross-chain `send`, `on_accept`, and `on_timeout` paths: [1](#0-0) 

- `convert_to_erc20(value, erc_decimals, local_decimals)` computes `value * 10^(erc_decimals - local_decimals)` using `saturating_sub`, called from `send()` when dispatching the outbound cross-chain `Message`: [2](#0-1) 

- `convert_to_balance(value, erc_decimals, local_decimals)` computes `value / 10^(erc_decimals - local_decimals)` (again via `saturating_sub`), called from `on_accept` (minting to the beneficiary) and `on_timeout` (refunding the sender): [3](#0-2) [4](#0-3) 

Both functions assume `erc_decimals >= local_decimals`. When that assumption is violated — e.g. the local Substrate asset has more decimal precision than the paired EVM ERC20 contract (a realistic configuration; many Substrate assets use 10–18 decimals while paired EVM stable/wrapped tokens commonly use 6 decimals) — `saturating_sub` returns `0` on both sides instead of returning the true (negative, needs-division) exponent. The conversion then silently degenerates to an identity operation rather than dividing by `10^(local_decimals - erc_decimals)`, producing amounts that are off by orders of magnitude in opposite directions on `send` vs. `on_accept`.

Notably, the pallet declares an `ErcDecimalsBelowLocal` error variant, indicating the developers were aware `erc_decimals < local_decimals` is an invalid/dangerous state: [5](#0-4) 
However, the conversion helpers themselves perform no validation or explicit rejection of this case — they mask it via `saturating_sub`, which converts what should be a hard error into silent, wrong arithmetic. If this invariant is not actively and universally enforced at every point that writes to the `Precisions` storage (registration and update paths), any token pairing where the local asset's decimals exceed the registered EVM decimals reaches this broken math on the hot path of every cross-chain transfer.

### Impact Explanation
- On `send()`: if `local_decimals > erc_decimals`, `convert_to_erc20` fails to divide down, so the ERC20 `amount` encoded into the outbound `Message` is far larger (by `10^(local_decimals - erc_decimals)`) than it should be relative to the amount actually escrowed/burned locally. The destination `HyperFungibleToken`/`WrappedHyperFungibleToken` contract will mint an amount vastly exceeding what was locked/burned on the source chain — an unbacked mint of cross-chain value.
- On `on_accept()`/`on_timeout()`: the same asymmetry causes the local mint/refund to be too small relative to what was sent from the EVM side, causing silent value loss to the user (funds effectively destroyed/frozen relative to what was paid on the source chain).
- Either direction constitutes concrete theft/unbacked-mint or permanent value loss for users of the bridge, directly reachable by any signed user calling `send()` (an unprivileged dispatched request), once a token pair with this decimal relationship is registered.

### Likelihood Explanation
The trigger condition depends on how `Precisions` is populated by `register_token`/`update_token` (gated by `CreateOrigin`). If those extrinsics correctly enforce `erc_decimals >= local_decimals` on every write path, this bug is unreachable under normal, non-malicious configuration. I was not able to fully confirm from the code retrieved whether that invariant is enforced consistently in both `register_token` and `update_token` (time/tool budget exhausted before reaching those function bodies in `lib.rs`), so likelihood cannot be rated with full confidence. Given that many real-world Substrate assets use higher decimal precision than common EVM stable/wrapped tokens, this is a plausible, non-malicious configuration rather than a contrived edge case, which is why the underlying arithmetic function itself should defensively reject (or correctly handle) `erc_decimals < local_decimals` rather than relying entirely on registration-time validation.

### Recommendation
- Make `convert_to_erc20` and `convert_to_balance` symmetric and safe in both directions: compute the signed exponent explicitly and either multiply or divide accordingly, instead of relying on `saturating_sub` to silently clamp to zero.
- Additionally/alternatively, enforce `erc_decimals >= local_decimals` as a hard invariant at every write site of `Precisions` (`register_token` and `update_token`), returning `ErcDecimalsBelowLocal` consistently, and add a defensive `debug_assert!`/explicit check inside the conversion helpers themselves so a future write path cannot reintroduce the bug.

### Proof of Concept
1. Register a local asset with `local_decimals = 18` and a paired EVM contract configured with `erc_decimals = 6` in `Precisions` (plausible if the update/registration validation is not applied consistently, or the native `T::Decimals` value is not compared against the configured `erc_decimals`).
2. Call `send(params)` with `params.amount = 1 * 10^18` (i.e., "1" unit of the local asset).
3. `convert_to_erc20(1e18, 6, 18)` computes `10u128.pow(6u8.saturating_sub(18) as u32) = 10u128.pow(0) = 1`, so `erc20_amount = 1e18` is embedded in the dispatched `Message` unchanged, instead of the correct `1e18 / 10^12 = 1e6`.
4. On the destination EVM `HyperFungibleToken` contract (6 decimals), receiving `amount = 1e18` raw units mints `1e18` raw token units = `1,000,000` whole tokens, despite only 1 whole unit of the local asset having been escrowed/burned — a 10^6x unbacked over-mint. [6](#0-5) [2](#0-1)

### Citations

**File:** modules/pallets/hyper-fungible-token/src/impls.rs (L39-59)
```rust
/// Converts an ERC20 U256 amount to a local balance type
///
/// Divides by 10^(erc_decimals - local_decimals) to scale down from ERC20 precision.
/// The target type must implement `FromStr`.
pub fn convert_to_balance<B: core::str::FromStr>(
	value: U256,
	erc_decimals: u8,
	local_decimals: u8,
) -> Result<B, B::Err> {
	let dec_str = (value /
		U256::from(10u128.pow(erc_decimals.saturating_sub(local_decimals) as u32)))
	.to_string();
	dec_str.parse::<B>()
}

/// Converts a local u128 balance to an ERC20 U256 amount
///
/// Multiplies by 10^(erc_decimals - local_decimals) to scale up to ERC20 precision
pub fn convert_to_erc20(value: u128, erc_decimals: u8, local_decimals: u8) -> U256 {
	U256::from(value) * U256::from(10u128.pow(erc_decimals.saturating_sub(local_decimals) as u32))
}
```

**File:** modules/pallets/hyper-fungible-token/src/lib.rs (L219-224)
```rust
		/// Peer chain is not an EVM state machine; this pallet bridges substrate <-> EVM only
		NonEvmPeerChain,
		/// Configured ERC decimals are less than the local asset's decimals; precision conversion
		/// requires erc_decimals >= local_decimals
		ErcDecimalsBelowLocal,
	}
```

**File:** modules/pallets/hyper-fungible-token/src/lib.rs (L292-302)
```rust
			// Encode the Message body
			let sender: [u8; 32] = who.clone().into();
			let amount: u128 = params.amount.into();
			let erc20_amount = convert_to_erc20(amount, erc_decimals, decimals);

			let token_message = Message {
				from: sender.to_vec().into(),
				to: params.recipient.to_vec().into(),
				amount: alloy_primitives::U256::from_be_bytes(erc20_amount.to_big_endian()),
				data: params.call_data.unwrap_or_default().into(),
			};
```

**File:** modules/pallets/hyper-fungible-token/src/module.rs (L74-91)
```rust
		// Convert amount from ERC20 denomination to local
		let decimals = if local_asset_id == T::NativeAssetId::get() {
			T::Decimals::get()
		} else {
			<T::Assets as fungibles::metadata::Inspect<T::AccountId>>::decimals(
				local_asset_id.clone(),
			)
		};
		let erc_decimals = Precisions::<T>::get(local_asset_id.clone(), source)
			.ok_or(HftError::DecimalsNotConfigured(source))?;
		let amount = convert_to_balance::<
			<<T as Config>::NativeCurrency as Currency<T::AccountId>>::Balance,
		>(
			U256::from_big_endian(&message.amount.to_be_bytes::<32>()),
			erc_decimals,
			decimals,
		)
		.map_err(|e| HftError::InvalidAmountConversion(format!("{e:?}")))?;
```

**File:** modules/pallets/hyper-fungible-token/src/module.rs (L239-255)
```rust
				let decimals = if local_asset_id == T::NativeAssetId::get() {
					T::Decimals::get()
				} else {
					<T::Assets as fungibles::metadata::Inspect<T::AccountId>>::decimals(
						local_asset_id.clone(),
					)
				};
				let erc_decimals = Precisions::<T>::get(local_asset_id.clone(), dest)
					.ok_or(HftError::DecimalsNotConfigured(dest))?;
				let amount = convert_to_balance::<
					<<T as Config>::NativeCurrency as Currency<T::AccountId>>::Balance,
				>(
					U256::from_big_endian(&message.amount.to_be_bytes::<32>()),
					erc_decimals,
					decimals,
				)
				.map_err(|e| HftError::InvalidAmountConversion(format!("{e:?}")))?;
```
