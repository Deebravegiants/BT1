### Title
Cross-chain token amount conversion rounds down when scaling from ERC20 precision to local Substrate decimals, permanently freezing dust value on every transfer - (File: modules/pallets/hyper-fungible-token/src/impls.rs)

### Summary
The `hyper-fungible-token` pallet's `convert_to_balance` helper performs integer (floor) division when converting an incoming ERC20-denominated amount (up to 18 decimals) down to the local Substrate asset's decimals. This function is invoked in both `on_accept` (crediting the beneficiary of an incoming transfer) and `on_timeout` (refunding the original sender). Because the division always truncates, the low-order digits of every incoming amount that isn't an exact multiple of the scale factor are silently dropped and never credited to anyone, yet the equivalent full-precision value was already escrowed/burned on the source (EVM) side.

### Finding Description
`convert_to_balance` divides the raw `U256` ERC20 amount by `10^(erc_decimals - local_decimals)` and stringifies/parses the quotient, discarding any remainder: [1](#0-0) 

This is used to compute the credited/refunded amount in the ISMP module's `on_accept` handler: [2](#0-1) 

and again in `on_timeout` for refunds: [3](#0-2) 

`register_token`/`update_token` only enforce `erc_decimals >= local_decimals`: [4](#0-3) 

so `erc_decimals - local_decimals` is commonly non-zero (e.g., an 18-decimal EVM token mapped to a 6- or 10-decimal Substrate asset). The resulting `amount` (the floored quotient) is what actually gets transferred out of `pallet_account` (for native/custodied assets) or minted (for wrapped assets): [5](#0-4) 

The truncated remainder (up to `10^(erc_decimals - local_decimals) - 1` raw ERC20 units) is never accounted for anywhere — it is neither credited to the beneficiary nor tracked in any pallet storage. For custodied (native) assets, this remainder becomes permanently stranded in `pallet_account` with no code path to withdraw it, since every future transfer out is likewise computed from the same floor conversion. For minted (non-native) assets, the value is effectively destroyed relative to what was escrowed/burned on the sending EVM chain.

Any relayer delivering an ordinary cross-chain POST message (or its timeout) triggers this truncation — no privileged role is required, and the message body (the `amount` field) is fully attacker/user-controlled from the EVM side, so an amount can always be crafted to be a non-multiple of the scale factor.

### Impact Explanation
Every incoming transfer or timeout-refund whose ERC20 amount is not an exact multiple of `10^(erc_decimals - local_decimals)` loses the fractional remainder permanently. For custodied assets this is dust that becomes unrecoverable in the pallet's account (permanent freezing of funds); for minted assets it is value that is silently destroyed relative to the amount escrowed on the source chain. This is systemic — it affects the default/common case of bridging an 18-decimal EVM token to a lower-decimal Substrate asset, and losses accumulate with transaction volume, matching the referenced report's finding that "these rounding errors can add up and become significant."

### Likelihood Explanation
High likelihood: this triggers on essentially every cross-chain transfer between chains with differing decimals (the common case, since `erc_decimals >= local_decimals` is enforced and typically strictly greater for e.g. 18→6/10 decimal pairs). No special conditions or privileged actors are needed — any user's ordinary `send()` amount that isn't already decimal-aligned, or any relayer delivering a timed-out message, exercises the truncating path.

### Recommendation
Do not silently discard the truncated remainder. Either (a) round up when computing the amount the pallet actually owes out (mint/transfer) so the recipient/sender never receives less value than was locked/burned, while capping at the truly escrowed amount, or (b) explicitly track and refund/redistribute the truncated dust (e.g., accumulate it and allow periodic sweeping), or (c) reject/require `send()` amounts on the EVM side to be exact multiples of the decimal scale factor so no fractional remainder can ever be created in the first place (mirroring the `PriceNotRepresentable` pattern used elsewhere in this codebase for decimal scaling, e.g. `evm/src/utils/VWAPOracle.sol`'s handling of decimal precision).

### Proof of Concept
1. Register a token with `erc_decimals = 18` and `local_decimals = 6` (a common real-world pairing, e.g., an 18-decimal EVM token bridged to a 6-decimal Substrate asset) via `register_token`.
2. From the EVM `HyperFungibleToken` contract, dispatch a POST request whose `Message.amount` is, e.g., `1_000000_123456789012` (i.e., `1000000.123456789012` in 18-decimal units) to the Substrate chain.
3. In `on_accept`, `convert_to_balance` computes `amount / 10^(18-6) = amount / 10^12`, floor-dividing to `1000000` local units, discarding `123456789012` raw ERC20 units (`0.000000123456789012` of the token) with no accounting.
4. Repeat at scale/volume: each such transfer permanently strands its fractional remainder in `Pallet::pallet_account()` (custodied assets) or destroys it entirely (minted assets), with no mechanism in the pallet to recover or credit it.

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

**File:** modules/pallets/hyper-fungible-token/src/module.rs (L82-91)
```rust
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

**File:** modules/pallets/hyper-fungible-token/src/module.rs (L93-117)
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
		}
```

**File:** modules/pallets/hyper-fungible-token/src/module.rs (L246-255)
```rust
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

**File:** modules/pallets/hyper-fungible-token/src/lib.rs (L352-355)
```rust
				ensure!(
					config.decimals >= local_decimals,
					Error::<T>::ErcDecimalsBelowLocal
				);
```
