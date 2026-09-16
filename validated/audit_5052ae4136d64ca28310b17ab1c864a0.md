## Title
`convert_to_erc20`/`convert_to_balance` in `hyper-fungible-token` fail to scale amounts when local decimals exceed EVM decimals, enabling unbacked minting across the bridge - (File: `modules/pallets/hyper-fungible-token/src/impls.rs`)

### Summary
The `hyper-fungible-token` pallet converts amounts between its local asset precision and the ERC20 precision configured for a destination/source EVM chain using `convert_to_erc20` and `convert_to_balance`. Both functions compute the scaling exponent with `erc_decimals.saturating_sub(local_decimals)`, which silently becomes `0` whenever `local_decimals > erc_decimals`. This mirrors the Zaros `withdrawMarginUsd` bug class: a decimal conversion that is only implemented for one direction (scale up), while the reverse direction (scale down) is dropped, corrupting the transferred amount by orders of magnitude.

### Finding Description
`convert_to_erc20` is used in the `send` extrinsic to encode the outgoing cross-chain `Message.amount`: [1](#0-0) 

`saturating_sub` means that when `local_decimals` (the decimals of the local `pallet-assets`/native asset) is greater than `erc_decimals` (the configured EVM-side decimals stored in `Precisions`), the exponent evaluates to `0`, and `value` is forwarded to the destination chain completely unscaled instead of being divided down by `10^(local_decimals - erc_decimals)`.

This is invoked directly from the unprivileged, signed `send` extrinsic: [2](#0-1) 

`erc_decimals` and `decimals` are read from `Precisions`/asset metadata with no relationship enforced between them, and `params.amount` is a raw, caller-controlled `Balance`. If an asset is registered with `local_decimals` (e.g., 18) greater than the destination’s configured `erc_decimals` (e.g., 6 — a realistic configuration for a bridged synthetic USDC-like asset), a user who burns/locks `amount` raw units locally causes `erc20_amount = amount` (unscaled) to be embedded in the outgoing `Message`. The destination `HyperFungibleToken`/`WrappedHyperFungibleToken` contract interprets that same numeric value in its own (lower) decimal precision, so it mints/releases `10^(local_decimals - erc_decimals)` times more tokens than were actually escrowed/burned on the source chain.

The reverse function has the mirrored defect on inbound delivery: [3](#0-2) 

used in `on_accept`/`on_timeout`: [4](#0-3) 

Here, if `local_decimals > erc_decimals`, `convert_to_balance` also fails to scale up (multiplying instead of leaving as-is is the correct action for erc_decimals < local_decimals, but saturating_sub zeroes the exponent so no scaling occurs at all), under-crediting the beneficiary and effectively freezing value.

### Impact Explanation
The `send` path allows an unprivileged caller to trigger unbacked minting/release of tokens on the destination EVM chain relative to what was actually locked or burned on the substrate side, whenever an asset is registered with `local_decimals > erc_decimals` for that destination. This is a direct "unbacked mint" / theft-of-funds class impact: the destination contract's balance/escrow no longer matches the amount actually removed on the source chain, draining the destination custody/escrow or minting unlimited wrapped tokens. This satisfies the Critical/High bar (unbacked mint, forged value in a cross-chain message).

### Likelihood Explanation
Exploitation requires only a single signed `send` extrinsic call with an `asset_id` whose `Precisions` entry for the target chain has `erc_decimals < local_decimals` — a configuration not prevented by any check in `register_token`/`update_token`/`send`. Since decimal mismatches between substrate assets (which can be created with arbitrary decimals) and EVM tokens (frequently 6 or 8 decimals, e.g. USDC-style assets) are an expected, documented configuration for this pallet, the vulnerable configuration is plausible in normal operation, not a contrived edge case.

### Recommendation
Fix the scaling logic in both directions to handle `local_decimals > erc_decimals` and `local_decimals < erc_decimals` symmetrically, e.g.:
```rust
pub fn convert_to_erc20(value: u128, erc_decimals: u8, local_decimals: u8) -> U256 {
    if erc_decimals >= local_decimals {
        U256::from(value) * U256::from(10u128.pow((erc_decimals - local_decimals) as u32))
    } else {
        U256::from(value) / U256::from(10u128.pow((local_decimals - erc_decimals) as u32))
    }
}
```
and apply the analogous fix to `convert_to_balance`. Add regression tests covering `local_decimals > erc_decimals` for both `send` and `on_accept`/`on_timeout`.

### Proof of Concept
1. Register an asset via `register_token` with `local_decimals = 18` for the local `pallet-assets` asset and `precisions[dest_chain] = 6` (a plausible config for a synthetic USDC-like asset bridged to a 6-decimal ERC20 on an EVM chain).
2. Attacker calls `send(SendParams { asset_id, destination: dest_chain, amount: 1_000_000_000_000_000_000 /* 1.0 token, 18-decimal raw */, recipient: attacker_evm_address, ... })`.
3. Inside `send`, `erc_decimals = 6`, `decimals = 18`; `convert_to_erc20(1e18, 6, 18)` computes `10u128.pow(6u8.saturating_sub(18u8) as u32) = 10u128.pow(0) = 1`, so `erc20_amount = 1e18` is embedded in the dispatched `Message`, instead of the correct `1e18 / 10^12 = 1e6`.
4. On the destination `HyperFungibleToken` EVM contract (6-decimal ERC20 accounting), the message amount `1e18` is credited to `attacker_evm_address`, i.e. `1,000,000,000,000` tokens (1 trillion) are minted/released for a locked/burned deposit of only `1` token on the source chain — a `10^12`x unbacked amplification. [5](#0-4)

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

**File:** modules/pallets/hyper-fungible-token/src/lib.rs (L251-302)
```rust
			let token_contract =
				TokenContracts::<T>::get(params.destination, params.asset_id.clone())
					.ok_or(Error::<T>::TokenContractNotFound)?;
			let erc_decimals = Precisions::<T>::get(params.asset_id.clone(), params.destination)
				.ok_or(Error::<T>::DecimalsNotFound)?;

			// Lock or burn the local asset
			let decimals = if params.asset_id == T::NativeAssetId::get() {
				// escrow the native asset
				<T as Config>::NativeCurrency::transfer(
					&who,
					&Self::pallet_account(),
					params.amount,
					ExistenceRequirement::AllowDeath,
				)?;
				T::Decimals::get()
			} else {
				let is_native = NativeAssets::<T>::get(params.asset_id.clone());
				if is_native {
					<T as Config>::Assets::transfer(
						params.asset_id.clone(),
						&who,
						&Self::pallet_account(),
						params.amount.into(),
						Preservation::Expendable,
					)?;
				} else {
					<T as Config>::Assets::burn_from(
						params.asset_id.clone(),
						&who,
						params.amount.into(),
						Preservation::Expendable,
						Precision::Exact,
						Fortitude::Polite,
					)?;
				}
				<T::Assets as fungibles::metadata::Inspect<T::AccountId>>::decimals(
					params.asset_id.clone(),
				)
			};

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
