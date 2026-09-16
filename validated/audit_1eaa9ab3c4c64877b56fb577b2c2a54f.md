### Title
Incorrect decimals scaling in `convert_to_erc20`/`convert_to_balance` allows inflated cross-chain token amounts - (File: `modules/pallets/hyper-fungible-token/src/impls.rs`)

### Summary
The `hyper-fungible-token` pallet's decimal-conversion helpers use `saturating_sub` when computing the scaling exponent between the source and destination token decimals. When the *local* (source-side) decimals exceed the *ERC20* (destination-side) decimals, the exponent saturates to zero instead of applying the correct inverse scaling, causing the value dispatched cross-chain to be many orders of magnitude larger than intended.

### Finding Description
`convert_to_erc20` and `convert_to_balance` are meant to rescale token amounts between a local Substrate asset's decimals and a remote ERC20 token's decimals: [1](#0-0) 

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

Both functions compute `erc_decimals.saturating_sub(local_decimals)`. This is only correct when `erc_decimals >= local_decimals`. When `local_decimals > erc_decimals` (e.g. a native/local asset with 18 decimals bridging to a destination ERC20 token with 6 decimals, such as USDC), `saturating_sub` clamps the exponent to `0`, so **no scaling is applied at all**, instead of the correct division/multiplication by `10^(local_decimals - erc_decimals)`.

This is called directly from the unprivileged, user-callable `send` extrinsic: [2](#0-1) 

```rust
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

Here `decimals` is the local Substrate asset's decimals and `erc_decimals` is the destination ERC20's configured decimals (`Precisions::<T>::get`). If `decimals > erc_decimals`, the encoded `amount` embedded in the cross-chain `Message` is off by a factor of `10^(decimals - erc_decimals)` — i.e. it is *not scaled down* as required, so the numeric value locked/burned at high precision on the source chain is dispatched unchanged and interpreted at the destination's lower-decimal precision, inflating the effective token amount the destination contract will mint/release.

### Impact Explanation
An attacker (any account holding a small amount of the bridged asset) can call `send` with a modest `params.amount` of a local asset whose decimals exceed the configured destination ERC20 decimals. Because the scaling factor silently becomes `1` instead of `10^(decimals-erc_decimals)`, the resulting `Message.amount` delivered to the destination `HyperFungibleToken`/`WrappedHyperFungibleToken` EVM contract represents a vastly larger token amount than what was actually escrowed/burned on the source chain. This is a decimals-driven unbacked-mint / fund-inflation bug at the token bridge mint path — the destination side trusts the encoded amount and mints/transfers accordingly, letting an attacker extract far more value than deposited. This directly matches "unbacked mint" in scope.

### Likelihood Explanation
Likelihood is high wherever a deployment pairs a local asset of higher decimal precision (e.g. 18-decimal native currency) with a destination ERC20 configured at lower decimals (e.g. 6-decimal USDC-like token) via `Precisions::<T>::set` — a very common decimals combination in cross-chain bridges. The bug triggers unconditionally on every `send()` call under that configuration, requiring no special privileges or race conditions, just a standard token-send transaction.

### Recommendation
Fix the scaling logic in `convert_to_erc20` and `convert_to_balance` to handle both directions correctly, e.g.:
```rust
pub fn convert_to_erc20(value: u128, erc_decimals: u8, local_decimals: u8) -> U256 {
    if erc_decimals >= local_decimals {
        U256::from(value) * U256::from(10u128.pow((erc_decimals - local_decimals) as u32))
    } else {
        U256::from(value) / U256::from(10u128.pow((local_decimals - erc_decimals) as u32))
    }
}
```
and symmetrically for `convert_to_balance` (dividing/multiplying in the opposite direction). Add regression tests covering `local_decimals > erc_decimals` (e.g. 18 → 6) in addition to the currently-tested `erc_decimals > local_decimals` case.

### Proof of Concept
1. Configure a local asset with 18 decimals and set `Precisions::<T>` for a destination ERC20 token to 6 decimals (a realistic USDC-style pairing).
2. Call `send` with `params.amount = 1_000_000_000_000_000_000` (1 whole token, 18-decimal units) to that destination.
3. `decimals = 18`, `erc_decimals = 6` → `erc_decimals.saturating_sub(local_decimals) = 0` → `convert_to_erc20` returns the raw value `1_000_000_000_000_000_000` unchanged.
4. The dispatched `Message.amount` is `1e18`, which the destination ERC20 contract (6 decimals) will treat as `1,000,000,000,000` tokens instead of the intended `1,000,000` (i.e., `1e6` for "1 token" at 6 decimals) — a `10^12`-times inflation, letting the sender mint/receive far more value on the destination chain than was locked on the source.

Note: I was unable to fully verify how the destination EVM `HyperFungibleToken.sol`/`HyperFungibleTokenUpgradeable.sol` `onAccept` handles the raw `message.amount` (whether it applies any additional decimal normalization) since the file contents were not retrievable through the available search tools within this session; the substrate-side `on_accept` path (module.rs) confirmed does perform its own (also flawed) `convert_to_balance` scaling, which supports that the destination trusts the encoded amount as denominated at the configured precision rather than re-deriving it independently.

### Citations

**File:** modules/pallets/hyper-fungible-token/src/impls.rs (L43-59)
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

/// Converts a local u128 balance to an ERC20 U256 amount
///
/// Multiplies by 10^(erc_decimals - local_decimals) to scale up to ERC20 precision
pub fn convert_to_erc20(value: u128, erc_decimals: u8, local_decimals: u8) -> U256 {
	U256::from(value) * U256::from(10u128.pow(erc_decimals.saturating_sub(local_decimals) as u32))
}
```

**File:** modules/pallets/hyper-fungible-token/src/lib.rs (L290-302)
```rust
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
