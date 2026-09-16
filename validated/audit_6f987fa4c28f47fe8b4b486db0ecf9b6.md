## Title
Asymmetric decimal conversion in `hyper-fungible-token` pallet inflates outgoing/incoming cross-chain amounts by 10^n when local decimals exceed remote decimals - ([File: modules/pallets/hyper-fungible-token/src/impls.rs])

### Summary
The C4 finding describes Astaria's Seaport listing price being wrong because a value denominated in 18 decimals was passed unconverted to an asset that actually has fewer decimals, inflating the effective price by 10^12. The `hyper-fungible-token` pallet's `convert_to_balance`/`convert_to_erc20` helper functions have the analogous defect: they only scale correctly in one direction (when the ERC20 side has *more* decimals than the local side), and silently skip scaling when the local side has more decimals than the ERC20 side, because `saturating_sub` clamps the exponent to zero instead of dividing/multiplying in the other direction.

### Finding Description
`convert_to_erc20` (used in `Pallet::send`) is defined as: [1](#0-0) 

```rust
pub fn convert_to_erc20(value: u128, erc_decimals: u8, local_decimals: u8) -> U256 {
    U256::from(value) * U256::from(10u128.pow(erc_decimals.saturating_sub(local_decimals) as u32))
}
```

and the reverse `convert_to_balance` (used in `on_accept`/`on_timeout`): [2](#0-1) 

Both functions compute the scaling exponent as `erc_decimals.saturating_sub(local_decimals)` (or the inverse), which is correct only when `erc_decimals >= local_decimals`. When `local_decimals > erc_decimals` — e.g. the local asset uses 18 decimals (a common Substrate default, or `T::Decimals::get()` for the native asset) while the paired EVM token is a 6-decimal stablecoin such as USDC — `saturating_sub` returns `0`, so `convert_to_erc20` multiplies by `10^0 = 1` instead of dividing by `10^12`. The outgoing ERC20 amount is therefore emitted still expressed in 18-decimal local units, exactly mirroring the Astaria bug where an 18-decimal `liquidationInitialAsk` was passed unconverted to a 6-decimal asset.

This is invoked from the `send` extrinsic, which any signed account can call: [3](#0-2) 

The resulting `Message.amount` is ABI-encoded and dispatched as an ISMP `PostRequest` to the paired `HyperFungibleToken`/`WrappedHyperFungibleToken` contract on the destination EVM chain: [4](#0-3) 

On the EVM side that amount is minted/released directly against the token's real decimals (e.g. USDC's 6), so a user who sent, say, 1 local unit (in 18-decimal terms) would have the raw `10^12`-times-too-large integer minted as if it were already 6-decimal denominated, effectively minting up to `10^12`x more tokens than backed by the escrowed/burned amount on the Substrate side.

The reverse path (`on_accept`/`on_timeout` calling `convert_to_balance`) has the symmetric flaw: if `erc_decimals < local_decimals`, `saturating_sub` again clamps to zero and the local mint/release amount is computed as if the ERC20 amount were already in local-chain (18-decimal) units, so an incoming 6-decimal amount is credited without being scaled up by 10^12, freezing (undervaluing by 10^12) the recipient's funds instead of inflating them. [5](#0-4) [6](#0-5) 

### Impact Explanation
Depending on which decimals pairing is configured via `Precisions` (`modules/pallets/hyper-fungible-token/src/lib.rs:145-155`), this defect either:
- Mints/unlocks up to `10^n` times more ERC20 tokens on the destination EVM chain than were escrowed/burned on the substrate side (`send` → `convert_to_erc20`), an unbacked-mint / theft-of-funds scenario, or
- Credits up to `10^n` times fewer local tokens than the ERC20 amount actually represents (`on_accept`/`on_timeout` → `convert_to_balance`), permanently freezing the difference in the pallet's escrow / burning it with no recovery path.

Both are concrete "unbacked mint" or "permanent freezing of funds" outcomes reachable from a single `send` extrinsic or a single relayed cross-chain message, matching the required impact classes.

### Likelihood Explanation
This triggers deterministically whenever an asset pair is registered with `local_decimals > erc_decimals` (a realistic configuration, since many Substrate assets/native currencies default to 18 decimals while common EVM stablecoins like USDC/USDT use 6). No malicious actor action beyond a normal `send()` call or a normal cross-chain transfer is required — any unprivileged user triggers the bug just by using the bridge for such an asset pair. Likelihood is high wherever such a decimals pairing exists in the deployed configuration.

### Recommendation
Fix `convert_to_erc20` and `convert_to_balance` in `modules/pallets/hyper-fungible-token/src/impls.rs` to handle both directions explicitly instead of relying on `saturating_sub`:
```rust
pub fn convert_to_erc20(value: u128, erc_decimals: u8, local_decimals: u8) -> U256 {
    if erc_decimals >= local_decimals {
        U256::from(value) * U256::from(10u128.pow((erc_decimals - local_decimals) as u32))
    } else {
        U256::from(value) / U256::from(10u128.pow((local_decimals - erc_decimals) as u32))
    }
}
```
and symmetrically for `convert_to_balance`. Add test coverage for `local_decimals > erc_decimals` pairings (the current test suite only appears to exercise the opposite direction).

### Proof of Concept
1. Register a token pair where the local asset has `decimals = 18` (e.g. the chain's `T::NativeAssetId`) and the EVM counterpart is USDC with `Precisions = 6` for the destination chain.
2. A user calls `send` with `amount = 1_000_000_000_000_000_000` (1 token, 18-decimal local units).
3. `erc_decimals.saturating_sub(local_decimals)` = `6u8.saturating_sub(18u8)` = `0`, so `convert_to_erc20` returns `1_000_000_000_000_000_000` unchanged instead of `1_000_000` (1 USDC, 6 decimals).
4. The `Message.amount` field dispatched to the destination `HyperFungibleToken` contract therefore requests minting/releasing `1_000_000_000_000_000_000` raw USDC units (`10^12` USDC) against only 1 locally-escrowed unit — an unbacked mint of `10^12`x the intended amount.

### Citations

**File:** modules/pallets/hyper-fungible-token/src/impls.rs (L43-52)
```rust
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

**File:** modules/pallets/hyper-fungible-token/src/lib.rs (L292-296)
```rust
			// Encode the Message body
			let sender: [u8; 32] = who.clone().into();
			let amount: u128 = params.amount.into();
			let erc20_amount = convert_to_erc20(amount, erc_decimals, decimals);

```

**File:** modules/pallets/hyper-fungible-token/src/lib.rs (L297-315)
```rust
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
