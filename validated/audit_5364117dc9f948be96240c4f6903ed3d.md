### Title
Decimal-mismatch in `convert_to_erc20` causes unbacked minting on the destination chain when local asset decimals exceed the destination's configured ERC20 decimals - (File: `modules/pallets/hyper-fungible-token/src/impls.rs`)

### Summary
`pallet-hyper-fungible-token`'s `convert_to_erc20` helper, used by the `send` extrinsic to translate a locked/burned local amount into the ERC20-denominated amount encoded in the outbound cross-chain `Message`, only scales *up* correctly. When the local asset's decimals exceed the destination chain's configured `Precisions` decimals, the required down-scaling never happens, so the message carries an amount inflated by `10^(local_decimals - erc_decimals)`. The destination `HyperFungibleToken.sol` contract mints that raw value verbatim via `_mint(beneficiary, message.amount)`, with no independent scaling check, producing tokens far in excess of what was actually escrowed/burned on the source chain.

### Finding Description
`convert_to_erc20` and `convert_to_balance` compute the scaling exponent with `saturating_sub`: [1](#0-0) 

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

Both functions assume `erc_decimals >= local_decimals`. `saturating_sub` returns `0` whenever `local_decimals > erc_decimals`, which means `10^0 = 1` is used instead of the correct divisor `10^(local_decimals - erc_decimals)`. In `send`, this is called as: [2](#0-1) 

```rust
let sender: [u8; 32] = who.clone().into();
let amount: u128 = params.amount.into();
let erc20_amount = convert_to_erc20(amount, erc_decimals, decimals);
```

Here `decimals` is the local asset's decimal precision and `erc_decimals` is the destination chain's per-`(asset, chain)` configured decimals from `Precisions`, which is set independently by governance at `register_token`/`update_token` time and can legitimately be lower than the local asset's decimals (e.g., a local 18-decimal native asset bridged to a 6-decimal ERC20 representation). In that case, `convert_to_erc20` fails to divide by `10^(local_decimals - erc_decimals)` and instead forwards the full, un-scaled-down raw amount.

The destination `HyperFungibleToken.sol` contract trusts this value completely and mints it as-is: [3](#0-2) 

```solidity
_mint(beneficiary, message.amount);
```

There is no reverse validation on the EVM side that the amount is plausible relative to the escrowed/burned amount, since the trust model is that the substrate side performs the correct decimal conversion before dispatch.

### Impact Explanation
Any unprivileged user calling the `send` extrinsic on a token whose local decimals exceed the destination's registered ERC20 decimals will cause the destination contract to mint `10^(local_decimals - erc_decimals)` times more tokens than were actually escrowed or burned on the source chain. This is a critical, permanent, unbacked-mint vulnerability: the attacker can burn/lock a small amount locally and receive an enormously inflated balance on the destination chain, which can then be freely transferred, sold, or bridged elsewhere, draining the bridge's backing and directly stealing value from the protocol/liquidity.

### Likelihood Explanation
Reachable directly by any account holding even a trivial balance of a registered non-18-decimal asset — a single call to the `send` extrinsic. The precondition (a registered `(AssetId, StateMachine)` pair in `Precisions` with `erc_decimals < local_decimals`) is not an edge case; it is an entirely normal governance configuration whenever bridging assets whose native precision (e.g., 18-decimal tokens, or Substrate assets configured with higher-than-6 decimals) is paired with lower-decimal ERC20 representations. No attacker privilege beyond a funded account and a legitimately-registered asset pairing is required.

### Recommendation
Fix both helper functions to correctly scale in either direction instead of assuming `erc_decimals >= local_decimals`:

```rust
pub fn convert_to_erc20(value: u128, erc_decimals: u8, local_decimals: u8) -> U256 {
	if erc_decimals >= local_decimals {
		U256::from(value) * U256::from(10u128.pow((erc_decimals - local_decimals) as u32))
	} else {
		U256::from(value) / U256::from(10u128.pow((local_decimals - erc_decimals) as u32))
	}
}

pub fn convert_to_balance<B: core::str::FromStr>(
	value: U256,
	erc_decimals: u8,
	local_decimals: u8,
) -> Result<B, B::Err> {
	let scaled = if erc_decimals >= local_decimals {
		value / U256::from(10u128.pow((erc_decimals - local_decimals) as u32))
	} else {
		value * U256::from(10u128.pow((local_decimals - erc_decimals) as u32))
	};
	scaled.to_string().parse::<B>()
}
```
Add regression tests covering `local_decimals > erc_decimals` for both `send` and `on_accept` paths.

### Proof of Concept
1. Governance registers a local asset with 18 decimals for bridging to `StateMachine::Evm(X)`, and sets `Precisions::<T>::insert(asset_id, StateMachine::Evm(X), 6)` (a 6-decimal ERC20 representation on the destination — a normal configuration for e.g. stablecoin-like assets).
2. Attacker calls `send` with `amount = 1 * 10^18` (1 whole token in local raw units).
3. Inside `send`, `decimals = 18`, `erc_decimals = 6`. `convert_to_erc20(1e18, 6, 18)` computes `10u128.pow(6u8.saturating_sub(18u8) as u32) = 10u128.pow(0) = 1`, so `erc20_amount = 1e18` (unchanged), instead of the correct `1e18 / 10^12 = 1e6`.
4. The dispatched `Message.amount` field carries `1e18`.
5. On the destination `HyperFungibleToken.sol`, `onAccept` decodes the message and calls `_mint(beneficiary, 1e18)` verbatim — see [3](#0-2)  — minting `1e18` raw units of a 6-decimal token, i.e. `1,000,000,000,000` (1 trillion) whole tokens, instead of the intended `1e6` raw units (1 whole token).
6. The attacker locked/burned only 1 token's worth locally but received a trillion-times-inflated balance on the destination chain, which can be freely transferred out, permanently unbacking the bridge.

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

**File:** modules/pallets/hyper-fungible-token/src/lib.rs (L292-296)
```rust
			// Encode the Message body
			let sender: [u8; 32] = who.clone().into();
			let amount: u128 = params.amount.into();
			let erc20_amount = convert_to_erc20(amount, erc_decimals, decimals);

```

**File:** sdk/packages/core/contracts/apps/HyperFungibleToken.sol (L301-301)
```text
        _mint(beneficiary, message.amount);
```
