### Title
Incorrect decimal scaling in `pallet-hyper-fungible-token`'s cross-chain amount conversion causes unbacked minting / fund loss - (File: `modules/pallets/hyper-fungible-token/src/impls.rs`)

### Summary
The `pallet-hyper-fungible-token` pallet converts amounts between the local chain's asset decimals and the remote EVM chain's ERC20 decimals using `convert_to_erc20` / `convert_to_balance` in `impls.rs`. Both helpers use `erc_decimals.saturating_sub(local_decimals)` to decide the scaling exponent, which silently becomes `0` — i.e. "no scaling" — whenever the local asset has *more* decimals than the registered EVM token. This is analogous to the reported USSD bug (wrong hardcoded/derived amount used at a value-transfer boundary): the wrong amount is computed and propagated at a cross-chain token-bridge mint/burn boundary, in a path reachable from a single signed `send` extrinsic or a single relayed incoming ISMP message.

### Finding Description
`convert_to_erc20` and `convert_to_balance` are defined as: [1](#0-0) 

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

pub fn convert_to_erc20(value: u128, erc_decimals: u8, local_decimals: u8) -> U256 {
    U256::from(value) * U256::from(10u128.pow(erc_decimals.saturating_sub(local_decimals) as u32))
}
```

Both functions only handle the case `erc_decimals >= local_decimals` correctly. When `erc_decimals < local_decimals` (the local/substrate asset has more decimal precision than the registered EVM contract, e.g. local `18` vs EVM `6`), `erc_decimals.saturating_sub(local_decimals)` saturates to `0`, so the code multiplies/divides by `10^0 = 1` — i.e. it performs **no scaling at all**, instead of the required inverse scaling (multiply on the `convert_to_balance` incoming path, divide on the `convert_to_erc20` outgoing path).

This helper is used directly in the outgoing `send` extrinsic: [2](#0-1) 

and in the incoming `on_accept` handler: [3](#0-2) 

The EVM-side `HyperFungibleToken.onAccept` mints exactly `message.amount` with no independent re-scaling or sanity check: [4](#0-3) 

So whatever (wrong) amount the pallet encodes into the ISMP `Message.amount` is minted verbatim on the destination EVM chain.

### Impact Explanation
- Outgoing direction (`send`, local chain → EVM): when the registered EVM decimals (`erc_decimals`) are less than the local asset's decimals, `convert_to_erc20` fails to divide the value down. The dispatched `Message.amount` is left un-scaled (10^(local−erc) times too large), so the destination `HyperFungibleToken`/`WrappedHyperFungibleToken` contract mints/releases far more tokens than were escrowed/burned on the substrate side — an **unbacked mint** directly draining the destination asset's backing, reachable from a single signed `send` extrinsic.
- Incoming direction (`on_accept`, EVM → local chain): the same condition causes `convert_to_balance` to skip multiplying the value up, so the pallet mints/releases far fewer tokens than the user is owed for the ERC20 amount that was actually burned/locked on the EVM side — a **permanent loss of funds** for the recipient, reachable from a single relayed ISMP POST request.

Both outcomes are classified Medium/High-impact token-bridge mint/burn defects matching the report's bug class (wrong amount minted due to an incorrect hardcoded/derived scaling factor at initialization/config time), just manifesting here as a decimal-configuration-dependent conversion bug rather than a literal constant.

### Likelihood Explanation
This is triggered purely by normal usage — any asset registered via `register_token` where the local chain's asset decimals exceed the EVM-side token's decimals (a configuration that is entirely plausible and not validated against by the pallet) will hit this path on every `send` and every inbound transfer for that asset, with no privileged action required beyond a normal `send` extrinsic call or ordinary incoming bridge message.

### Recommendation
Fix the scaling logic in `convert_to_erc20`/`convert_to_balance` to branch explicitly on which side has more decimals, e.g.:
```rust
if erc_decimals >= local_decimals {
    value * 10^(erc_decimals - local_decimals)   // scale up
} else {
    value / 10^(local_decimals - erc_decimals)   // scale down
}
```
applying the inverse operation symmetrically in `convert_to_balance`. Add unit tests covering `erc_decimals < local_decimals` for both `send` and `on_accept`/`on_timeout` paths.

### Proof of Concept
1. Register a non-native asset via `register_token` with local `Assets` decimals `18` and `Precisions::<T>::insert(asset_id, dest_chain, 6)` (EVM side declared as 6 decimals, e.g. mirroring a USDC-like token).
2. Call `send(origin, SendParams { asset_id, destination: dest_chain, amount: 1_000_000000000000000000 /* 1000 * 1e18 */, .. })`.
3. In `send`, `erc_decimals = 6`, `decimals = 18`; `convert_to_erc20(1000e18, 6, 18)` computes `1000e18 * 10^(6u8.saturating_sub(18)) = 1000e18 * 10^0 = 1000e18` instead of the correct `1000e6`.
4. The dispatched `Message.amount` is `1000e18`, which the destination `HyperFungibleToken.onAccept` mints verbatim (`sdk/packages/core/contracts/apps/HyperFungibleToken.sol:301`) — minting `10^12` times the intended amount, unbacked by the `1000e18`-local-unit (but decimal-normalized-lower-value) escrow/burn that occurred locally.

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

**File:** sdk/packages/core/contracts/apps/HyperFungibleToken.sol (L301-313)
```text
        _mint(beneficiary, message.amount);

        if (message.data.length > 0) {
            ICallDispatcher(_dispatcher).dispatch(message.data);
        }

        emit Received({
            from: message.from,
            to: beneficiary,
            source: string(request.source),
            amount: message.amount
        });
    }
```
