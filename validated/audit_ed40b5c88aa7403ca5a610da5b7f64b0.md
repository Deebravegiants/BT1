## Analysis

The reported bug class is a **missing/incorrect precision-scaling calculation between two token decimal bases**, causing accuracy loss in a cross-asset amount computation. The Hyperbridge codebase has a directly analogous defect in `pallet-hyper-fungible-token`'s decimal-conversion helpers, but the impact is more severe than the original report (which only caused tx reverts): here it produces a catastrophically wrong minted/credited amount, since these helpers use `saturating_sub` for a decimals difference that can go negative in either direction. [1](#0-0) 

### Title
Decimal-scaling helpers `convert_to_balance`/`convert_to_erc20` silently skip scaling when `erc_decimals < local_decimals`, causing unbacked over-mint or fund loss on HyperFungibleToken bridging - (File: `modules/pallets/hyper-fungible-token/src/impls.rs`)

### Summary
`convert_to_balance` and `convert_to_erc20` scale an amount between an EVM ERC-20's decimals and the local pallet asset's decimals using `10u128.pow(erc_decimals.saturating_sub(local_decimals))`. This expression is only correct when `erc_decimals >= local_decimals`. When `erc_decimals < local_decimals` (a valid, permitted `register_token` configuration), `saturating_sub` clamps to `0`, so the function multiplies/divides by `10^0 = 1` — i.e., performs **no scaling at all** — silently mispricing the amount by a factor of `10^(local_decimals - erc_decimals)`.

### Finding Description
`convert_to_erc20` is called from the `send` extrinsic to compute the amount encoded into the outgoing ISMP `Message` sent to the EVM `HyperFungibleToken`/`WrappedHyperFungibleToken` contract: [2](#0-1) 

```
let erc20_amount = convert_to_erc20(amount, erc_decimals, decimals);
```

where `decimals` is the local asset's decimals and `erc_decimals` is the registered EVM-side decimals (`Precisions` storage) for that `(asset, destination)` pair.

```rust
pub fn convert_to_erc20(value: u128, erc_decimals: u8, local_decimals: u8) -> U256 {
    U256::from(value) * U256::from(10u128.pow(erc_decimals.saturating_sub(local_decimals) as u32))
}
```

This is only correct when `erc_decimals >= local_decimals` (scale up). If a registered asset has `local_decimals > erc_decimals` (e.g., a token native to the substrate chain with 18 decimals, bridged to an EVM chain where the ERC-20 representation has 6 decimals — a configuration explicitly supported per the pallet's own documentation: "Decimals between this chain and each remote chain may differ; per-pair `Precisions` storage records the EVM-side decimals so amounts get scaled at the boundary"), `erc_decimals.saturating_sub(local_decimals)` clamps to `0`. The function then returns `value` completely unscaled — the raw 18-decimal amount is encoded directly as the ERC-20 `amount` field, which the destination `HyperFungibleToken.onAccept` will mint verbatim against its 6-decimal token. The result is a mint of `10^12`× the correct token quantity.



The reverse conversion, `convert_to_balance` (used on `on_accept` to credit incoming ERC-20 amounts into the local asset), has the symmetric failure: when `erc_decimals < local_decimals`, `erc_decimals.saturating_sub(local_decimals)` is again `0`, so the raw ERC-20 amount is credited directly as the local (finer-grained) balance, under-crediting the recipient by `10^(local_decimals - erc_decimals)`.

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

This is the same root-cause bug class as the reported `D3Oracle.getMaxReceive`: a cross-unit conversion formula that omits/mishandles decimal-difference scaling and silently produces an order-of-magnitude-wrong result instead of reverting.

### Impact Explanation
- **Outbound (`send`, native/escrow custody model):** when `local_decimals > erc_decimals` for a registered pair, any signed user calling `send` triggers minting on the EVM side of an amount inflated by `10^(local_decimals - erc_decimals)`. Since the pallet only escrows/burns the (correct, unscaled) local amount, the destination `HyperFungibleToken` mints far more tokens than are backed by escrow — an **unbacked mint** that can drain the bridge's economic backing and be redeemed by burning back through the pallet for real escrowed value, or dumped on the EVM chain.
- **Inbound (`on_accept`):** the reverse mismatch under-credits recipients bridging back, causing **permanent loss of user funds** (tokens burned/escrowed on the EVM side are credited at `10^-(local_decimals-erc_decimals)` of their value locally).
- This is triggered by an ordinary, unprivileged `send` extrinsic call — the pallet's only entry point for outbound transfers — with no admin/governance involvement beyond a legitimately-configured token pair whose decimals differ in this direction.

### Likelihood Explanation
Likelihood depends on whether any `register_token`/`update_token` configuration has `local_decimals > erc_decimals` for some destination chain. The pallet's design explicitly anticipates and documents differing decimals across chains ("Decimals between this chain and each remote chain may differ"), and the only worked example found in the codebase (`BridgeToken`: local=12, erc=18) happens to be scaled in the safe direction — but nothing in `register_token`/`update_token` validates or rejects the opposite (equally plausible) configuration, e.g. bridging an 18-decimal native asset to a 6-decimal ERC-20 representation. Given the codebase already handles multi-decimal tokens elsewhere (6-decimal stables next to 18-decimal ones is a recurring pattern across the repo), this configuration is realistic for any future or existing token registration.

### Recommendation
Replace `saturating_sub`-based scaling with a signed comparison that scales in the correct direction regardless of which side has more decimals:
```rust
pub fn convert_to_erc20(value: u128, erc_decimals: u8, local_decimals: u8) -> U256 {
    if erc_decimals >= local_decimals {
        U256::from(value) * U256::from(10u128.pow((erc_decimals - local_decimals) as u32))
    } else {
        U256::from(value) / U256::from(10u128.pow((local_decimals - erc_decimals) as u32))
    }
}
```
and symmetrically for `convert_to_balance`. Additionally, consider adding an invariant test/assertion in `register_token`/`update_token` that exercises both decimal directions, since the only currently-deployed example (`BridgeToken`) never triggers the buggy branch.

### Proof of Concept
1. Governance registers an asset via `register_token` with `native = true`, local asset decimals = 18, and `Precisions[(asset_id, EVM_CHAIN)] = 6` (a valid, unvalidated configuration).
2. A user calls `send(SendParams { asset_id, amount: 1_000000000000000000 /* 1 token, 18 dec */, destination: EVM_CHAIN, ... })`.
3. In the pallet, `decimals = 18` (native), `erc_decimals = 6`. `convert_to_erc20(1e18, 6, 18)` computes `erc_decimals.saturating_sub(local_decimals) = 0`, so `erc20_amount = 1e18 * 10^0 = 1e18`.
4. The dispatched ISMP `Message.amount = 1e18` is delivered to the EVM `HyperFungibleToken`/`WrappedHyperFungibleToken` contract, which mints/unlocks `1e18` raw units of its 6-decimal token — i.e., `1,000,000,000,000` (one trillion) tokens instead of the intended `1` token, for an escrow of only 1 token's worth on the source chain.

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
