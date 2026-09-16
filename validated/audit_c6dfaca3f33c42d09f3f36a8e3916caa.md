### Title
Missing/One-Directional Decimal Adjustment in HyperFungibleToken Bridge Conversion - (File: modules/pallets/hyper-fungible-token/src/impls.rs)

### Summary
The `hyper-fungible-token` pallet's cross-chain amount conversion helpers, `convert_to_balance` and `convert_to_erc20`, use `saturating_sub` to compute the decimal-scaling exponent between the local asset's decimals and the destination/source ERC20 decimals. When the local asset has **more** decimals than the configured remote/ERC20 decimals, the subtraction saturates to zero and the required inverse scaling (multiplication or division in the other direction) is silently skipped, exactly the same class of "missing asset decimal adjustment" defect described in the external report for `VaultKerosene.sol`, but here it sits directly in the token bridge's mint/burn amount computation rather than in a read-only TVL view.

### Finding Description
`convert_to_erc20`, used by the `send` extrinsic to compute the amount encoded into the outgoing `Message` for the destination chain's HyperFungibleToken/WrappedHyperFungibleToken contract, only scales **up**: [1](#0-0) 

and the companion `convert_to_balance`, used on the receiving side to translate an incoming ERC20 `U256` amount into a local pallet balance, only scales **down**: [2](#0-1) 

Both use `erc_decimals.saturating_sub(local_decimals)` as the scaling exponent. This is only correct for one direction of the decimals relationship:
- `convert_to_erc20` correctly multiplies when `erc_decimals > local_decimals`, but when `erc_decimals < local_decimals` (destination chain configured with fewer decimals than the local asset, e.g. local asset 18 decimals bridging to a chain whose `ChainConfig.decimals` is 6), the exponent saturates to `0` and **no down-scaling is applied at all** — the full, un-scaled local-precision `value` is packed into the `Message.amount` field that is dispatched cross-chain: [3](#0-2) 

- `convert_to_balance` correctly divides when `erc_decimals > local_decimals`, but when `erc_decimals < local_decimals` (an incoming amount denominated in fewer decimals than the local asset expects), the exponent again saturates to `0` and the raw, un-scaled `value` is used as the local balance to credit — instead of being multiplied up by `10^(local_decimals - erc_decimals)`.

This is precisely the report's bug class: the decimal difference between two representations of the same value ("assets"/tokens with different decimals) is asymmetrically applied to only one side of the inequality, so any configuration where `local_decimals > erc_decimals` silently drops the required scaling factor.

### Impact Explanation
- On the `send` path, an un-scaled `erc20_amount` means the destination `HyperFungibleToken`/`WrappedHyperFungibleToken` contract receives a `Message.amount` that is `10^(local_decimals - erc_decimals)` times larger than the value actually escrowed/burned on the source chain. If the destination contract mints or releases funds based on this raw amount (per the registered `ChainConfig.decimals`), this is an unbacked-mint / fund-drain vector reachable by any unprivileged user calling `send` — a single dispatched cross-chain token-bridge transfer inflates the amount minted on the destination side by orders of magnitude.
- On the receive path, the analogous under-scaling in `convert_to_balance` causes the opposite effect: incoming value is credited at a fraction of its true worth, permanently losing/freezing value for the recipient relative to what was escrowed/burned on the sending chain.
- Both cases sit in the token bridge mint/burn logic explicitly called out as in-scope, and are triggered by a normal user transaction (the `send` extrinsic, or delivery of an inbound token message), not by any privileged or admin action.

### Likelihood Explanation
Triggering requires only that a registered token/chain pair have `local_decimals` (the pallet's local asset decimals) greater than the configured `erc_decimals`/`ChainConfig.decimals` for that destination or source chain — a configuration that is entirely plausible (e.g., a locally 18-decimal native asset bridging to/from a chain registered with 6-decimal precision, as illustrated in the docs' `ChainConfig.decimals` field). No attacker privilege is needed beyond calling `send` or having a message routed to the pallet; likelihood is High for any deployment mixing differing decimal configurations across chains.

### Recommendation
Compute the scaling factor bidirectionally instead of relying on `saturating_sub` collapsing to zero:
```rust
pub fn convert_to_erc20(value: u128, erc_decimals: u8, local_decimals: u8) -> U256 {
    if erc_decimals >= local_decimals {
        U256::from(value) * U256::from(10u128.pow((erc_decimals - local_decimals) as u32))
    } else {
        U256::from(value) / U256::from(10u128.pow((local_decimals - erc_decimals) as u32))
    }
}
```
and symmetrically for `convert_to_balance`, dividing when `erc_decimals > local_decimals` and multiplying when `local_decimals > erc_decimals`.

### Proof of Concept
1. Register a token via `register_token` where the local asset (`AssetId`) has 18 decimals, and configure `ChainConfig.decimals = 6` for a destination EVM chain.
2. Call `send` with `params.amount = 1_000_000_000_000_000_000` (1 whole token, 18-decimal local balance). Inside `send`, `erc_decimals = 6`, `decimals = 18`.
3. `convert_to_erc20(1e18, 6, 18)`: `erc_decimals.saturating_sub(local_decimals) = 6u8.saturating_sub(18u8) = 0`, so the function returns `U256::from(1e18) * 10^0 = 1e18` instead of the correct `1e18 / 10^12 = 1e6`.
4. The dispatched `Message.amount` sent to the destination chain's HyperFungibleToken contract is `1e18`, one million times larger than the correct `1e6` value the 6-decimal destination expects for one token — leading to a 10^12x over-issuance/mint or an out-of-range amount being processed on the destination. [4](#0-3) [5](#0-4) 

**Note on confidence**: I was unable to load `modules/pallets/hyper-fungible-token/src/module.rs` (the file that consumes `convert_to_balance` on the inbound/`onAccept` path) due to tool errors during this session, so the exact receive-side crediting logic and whether any additional bounds-checking exists there is not fully confirmed — the root-cause defect in the shared conversion helpers (`impls.rs`) and its use in the `send` extrinsic (`lib.rs`) is directly verified, but end-to-end confirmation of the destination-chain minting behavior would require reviewing the EVM-side `HyperFungibleToken`/`WrappedHyperFungibleToken` contracts as well, which were not available in the indexed context.

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

**File:** modules/pallets/hyper-fungible-token/src/lib.rs (L254-310)
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
```
