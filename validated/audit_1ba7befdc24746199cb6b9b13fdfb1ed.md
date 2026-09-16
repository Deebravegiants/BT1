## Analog Found

### Title
Hyper-fungible-token bridge silently drops decimal scaling when local decimals exceed EVM decimals, forging inflated/deflated cross-chain transfer amounts - (File: `modules/pallets/hyper-fungible-token/src/impls.rs`)

### Summary
`convert_to_erc20` and `convert_to_balance` are the only place the `hyper-fungible-token` pallet normalizes amounts between a local asset's decimals and the EVM-side ERC20 decimals recorded in `Precisions`. Both functions use `u8::saturating_sub` to compute the scaling exponent, which silently becomes a no-op (scale factor `10^0 = 1`) whenever `local_decimals > erc_decimals`, instead of applying the required division/multiplication in the opposite direction. This is the same root cause as the referenced Mantra finding: an amount is carried across a decimal-precision boundary without being properly normalized, corrupting the resulting value used for minting/crediting.

### Finding Description
`convert_to_erc20`, used by the `send` extrinsic to encode the ERC20-side `Message.amount` from a locally-debited amount, only scales *up* by `10^(erc_decimals - local_decimals)`: [1](#0-0) 

When `local_decimals > erc_decimals`, `erc_decimals.saturating_sub(local_decimals)` clamps to `0`, so the function multiplies by `10^0 = 1` instead of dividing by `10^(local_decimals - erc_decimals)`. The raw, un-scaled local amount is sent verbatim as the ERC20 `Message.amount` field, dispatched via `DispatchPost`: [2](#0-1) 

Symmetrically, `convert_to_balance`, used in `on_accept`/`on_timeout` to translate an inbound ERC20 amount back into local balance, only scales *down* by `10^(erc_decimals - local_decimals)`: [3](#0-2) 

Again, when `local_decimals > erc_decimals`, the saturating subtraction clamps to `0` and no up-scaling multiplication happens, used directly to mint/transfer the beneficiary's amount: [4](#0-3) [5](#0-4) 

The pallet's own test suite only exercises the case where `erc_decimals (18) > local_decimals (10)` — the direction the code happens to handle correctly — and never exercises the opposite, broken direction: [6](#0-5) 

### Impact Explanation
Whenever a registered asset's local decimals exceed the EVM-side `Precisions` decimals for a destination chain (a routine configuration — e.g. a locally 18-decimal asset bridged to a chain where its ERC20 counterpart uses 6 decimals), any unprivileged user calling `send` has their debited/escrowed amount encoded into the outbound message at the wrong scale: the amount is not divided down, so the encoded `Message.amount` is `10^(local_decimals - erc_decimals)` times larger than intended. On the destination `HyperFungibleToken`/`WrappedHyperFungibleToken` EVM contract this results in an unbacked, wildly inflated mint relative to what was actually locked/burned on the source chain — a direct fund-forgery/unbacked-mint condition. The reverse direction (`on_accept`/`on_timeout`) under-scales inbound amounts, permanently under-crediting or freezing the correct value owed to legitimate beneficiaries. Both directions are reachable purely through the pallet's normal, unprivileged `send` extrinsic and message-delivery callbacks — no malicious admin or governance action is required, only a token configuration with `local_decimals > erc_decimals`.

### Likelihood Explanation
This is not an edge case: decimal mismatches between Substrate assets (commonly 10, 12, or 18 decimals) and their EVM ERC20 counterparts (very commonly 6 or 18 decimals) are the norm, not the exception, for any bridged token. Any token registered via `register_token`/`update_token` with `local_decimals > erc_decimals` for a given destination chain triggers this on every `send` call from any user, with no special preconditions.

### Recommendation
Fix both `convert_to_erc20` and `convert_to_balance` to handle both scaling directions explicitly, e.g. by computing the exponent as `erc_decimals as i16 - local_decimals as i16` and multiplying when positive / dividing when negative (or dividing/multiplying in the opposite functions), rather than relying on `saturating_sub` which silently collapses the negative case to zero. Add tests covering `local_decimals > erc_decimals` for both `send` and `on_accept`/`on_timeout` paths.

### Proof of Concept
Given a registered non-native asset with `local_decimals = 18` and `Precisions::<T>::get(asset_id, dest) = 6` (a plausible, common registration):

1. User calls `send` with `amount = 1 * 10^18` (i.e., "1 token" in local 18-decimal units). Correct ERC20 amount should be `1 * 10^6`.
2. `convert_to_erc20(1_000000000000000000, erc_decimals=6, local_decimals=18)` computes `erc_decimals.saturating_sub(local_decimals) = 0`, so it returns `value * 10^0 = 1_000000000000000000` — 10^12 times larger than the correct `1_000000` value.
3. This inflated amount is placed into `Message.amount` and dispatched to the destination EVM contract via `DispatchPost`, which will mint/release funds based on this value, producing an unbacked mint of `10^12x` the amount actually escrowed/burned on the source chain. [1](#0-0) [7](#0-6)

### Citations

**File:** modules/pallets/hyper-fungible-token/src/impls.rs (L39-52)
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
```

**File:** modules/pallets/hyper-fungible-token/src/impls.rs (L54-59)
```rust
/// Converts a local u128 balance to an ERC20 U256 amount
///
/// Multiplies by 10^(erc_decimals - local_decimals) to scale up to ERC20 precision
pub fn convert_to_erc20(value: u128, erc_decimals: u8, local_decimals: u8) -> U256 {
	U256::from(value) * U256::from(10u128.pow(erc_decimals.saturating_sub(local_decimals) as u32))
}
```

**File:** modules/pallets/hyper-fungible-token/src/lib.rs (L292-315)
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

			let dispatch_post = DispatchPost {
				dest: params.destination,
				from: PALLET_ID.to_bytes(),
				to: token_contract,
				timeout: params.timeout,
				body: Message::abi_encode(&token_message),
			};

			let metadata = FeeMetadata { payer: who.clone(), fee: params.relayer_fee.into() };
			let commitment = dispatcher
				.dispatch_request(DispatchRequest::Post(dispatch_post), metadata)
				.map_err(|_| Error::<T>::DispatchError)?;
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

**File:** modules/pallets/hyper-fungible-token/src/module.rs (L93-116)
```rust
		// Mint or transfer to beneficiary
		if local_asset_id == T::NativeAssetId::get() {
			<T as Config>::NativeCurrency::transfer(
				&Pallet::<T>::pallet_account(),
				&beneficiary,
				amount,
				ExistenceRequirement::AllowDeath,
			)
			.map_err(|e| HftError::TransferFailed(e.into()))?;
		} else {
			let is_native = NativeAssets::<T>::get(local_asset_id.clone());
			if is_native {
				<T as Config>::Assets::transfer(
					local_asset_id,
					&Pallet::<T>::pallet_account(),
					&beneficiary,
					amount.into(),
					Preservation::Expendable,
				)
				.map_err(|e| HftError::TransferFailed(e.into()))?;
			} else {
				<T as Config>::Assets::mint_into(local_asset_id, &beneficiary, amount.into())
					.map_err(|e| HftError::MintFailed(e.into()))?;
			}
```

**File:** modules/pallets/testsuite/src/tests/pallet_hyper_fungible_token.rs (L79-89)
```rust
				let msg = Message {
					from: alloy_primitives::Bytes::from(vec![0x11u8; 20]),
					to: alloy_primitives::Bytes::from(ALICE.as_slice().to_vec()),
					amount: {
						let bytes = convert_to_erc20(SEND_AMOUNT, 18, 10).to_big_endian();
						alloy_primitives::U256::from_be_bytes(bytes)
					},
					data: alloy_primitives::Bytes::default(),
				};
				Message::abi_encode(&msg)
			},
```
