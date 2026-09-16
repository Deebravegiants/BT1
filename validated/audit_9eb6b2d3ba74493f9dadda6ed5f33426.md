## Title
`convert_to_balance`/`convert_to_erc20` assume EVM decimals ≥ local decimals, enabling unbacked mint on destination chain - (`modules/pallets/hyper-fungible-token/src/impls.rs`)

### Summary
The `pallet-hyper-fungible-token` cross-chain amount scaling helpers hard-code the assumption that the registered EVM token's decimals are always greater than or equal to the local substrate asset's decimals. When a token pair is registered the other way around (local asset decimals > EVM `erc_decimals`), the scaling exponent silently saturates to zero instead of applying the required down-scaling division, causing the outgoing cross-chain `Message.amount` to be encoded far larger than the amount actually escrowed/burned.

### Finding Description
`convert_to_balance` and `convert_to_erc20` both compute the scaling exponent as `erc_decimals.saturating_sub(local_decimals)`: [1](#0-0) 

This only correctly derives the scaling factor for the case `erc_decimals >= local_decimals`. When `local_decimals > erc_decimals` (e.g. a local asset registered with 18 decimals paired to a remote ERC20 token with 6 decimals, which is a common real-world pairing — many ERC20s such as USDC/USDT use 6 decimals while substrate assets are frequently configured with 12 or 18), `saturating_sub` returns `0`, so the exponent becomes `10^0 = 1` — i.e. **no scaling is applied at all**.

This is invoked directly in the `send` extrinsic, which any signed account can call: [2](#0-1) 

Here `decimals` is the local asset's decimals and `erc_decimals` is the registered EVM decimals for the destination (`Precisions` storage, set via `register_token`/`update_token`). `convert_to_erc20(amount, erc_decimals, decimals)` is supposed to scale the raw local `amount` up or down to the destination ERC20's precision before encoding it into the dispatched `Message.amount` and sending the ISMP `PostRequest`. When `decimals > erc_decimals`, the function should **divide** `amount` by `10^(decimals - erc_decimals)`, but instead returns `amount` unchanged, i.e. up to `10^(decimals-erc_decimals)` times larger than correct.

The same flawed helper is reused symmetrically in `on_accept`/`on_timeout` via `convert_to_balance`: [3](#0-2) 

### Impact Explanation
For a token pair where the local substrate asset has more decimals than the destination EVM contract's registered decimals, calling `send()` burns/escrows the correct (small) local amount but encodes a wildly inflated `erc20_amount` into the cross-chain `Message`. Once this message is relayed and delivered to the counterpart `HyperFungibleToken`/`WrappedHyperFungibleToken`/`BridgeToken` contract on the EVM chain, that contract mints tokens to the recipient according to the inflated, unbacked amount (see the corresponding EVM-side mint logic in `evm/src/apps/BridgeToken.sol` / `HyperFungibleToken.sol`). This is a direct unbacked mint / theft vector: a user can burn a negligible amount of the local asset and receive an arbitrarily inflated amount of the wrapped/bridged token on the destination chain, draining backing value from the bridge.

Conversely, the same flaw causes value loss (effectively burning/freezing most of the transferred value) when receiving in the opposite direction (`on_accept` from an EVM chain into a local asset with higher decimals than the registered `erc_decimals`), since `convert_to_balance` fails to multiply up.

### Likelihood Explanation
The vulnerable condition is triggered purely by a legitimate token registration where `local_decimals > erc_decimals` — a plausible, non-malicious configuration (e.g., pairing an 18-decimal local asset with a 6-decimal remote ERC20 such as USDC/USDT). No malicious admin or governance action is required beyond normal `register_token` usage; any signed user can then trigger the bug simply by calling `send()`. The `BridgeToken.sol` contract's own doc comment confirms only the opposite relationship (`erc_decimals(18) >= local_decimals(12)`) was considered and tested; the reverse relationship, which the code does not guard against, is silently mis-handled.

### Recommendation
Fix `convert_to_balance` and `convert_to_erc20` to handle both scaling directions explicitly, e.g.:
```rust
if erc_decimals >= local_decimals {
    value * 10^(erc_decimals - local_decimals)   // or divide, per direction
} else {
    value / 10^(local_decimals - erc_decimals)
}
```
Add explicit unit tests in `pallet_hyper_fungible_token.rs` covering `local_decimals > erc_decimals` for both `send` and `on_accept`/`on_timeout` paths, and consider rejecting `register_token`/`update_token` configurations that have not been validated for both decimal orderings, or asserting decimals invariants at genesis/registration.

### Proof of Concept
1. Admin registers a non-native asset `X` with local `decimals = 18` and `Precisions::<T>::insert(X, dest_chain, 6)` (EVM side declares 6 decimals, e.g. mirroring USDC).
2. A user calls `send(SendParams { asset_id: X, amount: 1_000_000_000_000_000_000 (1.0 token, 18 decimals), destination: dest_chain, ... })`.
3. Inside `send`, `decimals = 18`, `erc_decimals = 6`. `convert_to_erc20(1e18, 6, 18)` computes `10u128.pow(6u8.saturating_sub(18u8) as u32) = 10^0 = 1`, so `erc20_amount = 1e18` — unchanged, instead of the correct `1e18 / 10^12 = 1e6`.
4. The dispatched `Message.amount` therefore encodes `1e18` raw units against a 6-decimal destination token — equivalent to `1,000,000,000,000` tokens instead of `1`.
5. Once relayed and accepted on the EVM destination `HyperFungibleToken`/`BridgeToken` contract, the recipient is minted `1e18` raw units (1 trillion tokens at 6 decimals) despite only 1 token's worth of the local asset having been burned/escrowed — an unbacked mint of value.

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

**File:** modules/pallets/hyper-fungible-token/src/lib.rs (L254-295)
```rust
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
