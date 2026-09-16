### Title
Incorrect Decimal Scaling in `pallet-hyper-fungible-token`'s `convert_to_erc20`/`convert_to_balance` Causes Unbacked Minting or Permanent Fund Loss - (File: modules/pallets/hyper-fungible-token/src/impls.rs)

### Summary
The `pallet-hyper-fungible-token` scaling helpers that convert amounts between the local substrate asset's decimal precision and the remote EVM token's decimal precision use `saturating_sub` to compute the scaling exponent instead of a bidirectional (signed) difference. This mirrors the RToken analog exactly: a scaling routine that is supposed to convert an amount proportionally between two precisions instead silently degenerates to "no scaling" whenever the subtraction underflows, corrupting amounts by orders of magnitude in one of the two possible configurations.

### Finding Description
`convert_to_balance` and `convert_to_erc20` are the only functions responsible for translating amounts between an ERC20 token's decimals and the local asset's decimals whenever tokens move across the bridge: [1](#0-0) 

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

Both functions only correctly scale for the case `erc_decimals >= local_decimals` (the only case exercised by the test suite and the `BridgeToken` deployment, where nexus's 12-decimal `BRIDGE` maps to an 18-decimal EVM representation). When a token is registered (via the permissionless-reachable `send` extrinsic against any asset whose `Precisions`/local decimals were configured with `local_decimals > erc_decimals`), `erc_decimals.saturating_sub(local_decimals)` clamps to `0`, so the exponent becomes `10^0 = 1` — i.e. **no scaling is applied at all** in the direction that actually needs it.

- In `send()` (`modules/pallets/hyper-fungible-token/src/lib.rs:294-295`), the local amount is burned/escrowed at full local precision, then `convert_to_erc20` is supposed to divide it down to the EVM chain's coarser precision but instead forwards the raw, unscaled local-precision value in the `Message.amount` field of the ISMP `Send` request: [2](#0-1) 

- On the EVM side, `HyperFungibleToken.onAccept` mints exactly `message.amount` of the token at its own (coarser) decimals with no further adjustment, so it mints a supply that is `10^(local_decimals - erc_decimals)` times larger than what was actually escrowed/burned on the substrate side — an unbacked mint of the bridged asset.
- Symmetrically, `convert_to_balance` (used in `on_accept`/`on_timeout`, `modules/pallets/hyper-fungible-token/src/module.rs:74-91,246-255`) under-scales incoming amounts by the same missing factor when `erc_decimals < local_decimals`, permanently destroying most of the value of legitimate inbound transfers/refunds.

This is the same bug class as the reported RToken issue: a scaling function meant to preserve proportional value across a precision boundary that instead behaves as an identity function under specific (unhandled) input conditions, because the implementation used unsigned/saturating subtraction instead of correctly handling both signs of the decimal delta.

### Impact Explanation
When a token is registered with `local_decimals > erc_decimals` for a given destination chain, every `send()` call (an unprivileged, signed extrinsic anyone holding the asset can invoke) burns/escrows the correct local amount but instructs the destination `HyperFungibleToken`/`WrappedHyperFungibleToken` contract to mint or release `10^(local_decimals - erc_decimals)` times too many tokens to the attacker-chosen recipient — an unbacked mint that can drain the token's cross-chain backing/economics, or (in the reverse direction) permanently strand nearly all value of every inbound transfer and every timeout refund. This is a High severity issue: it can be triggered by anyone with existing token balance and no privileged role.

### Likelihood Explanation
The bug only manifests for token registrations where the local pallet asset's decimals exceed the remote EVM contract's decimals — a configuration `register_token`/`update_token` allows and does not forbid. `pallet-hyper-fungible-token` is a generic, reusable pallet intended to onboard arbitrary tokens (not just the hardcoded 12-vs-18-decimal `BRIDGE`/nexus pairing that happens to avoid the bug), so any future or existing asset registered with that decimal relationship will hit this deterministically on every transfer, exactly like the certain/systemic likelihood described in the source report.

### Recommendation
Rewrite `convert_to_balance` and `convert_to_erc20` to handle both directions of the decimal delta explicitly, e.g.:
```rust
if erc_decimals >= local_decimals {
    value / 10^(erc_decimals - local_decimals)   // convert_to_balance
} else {
    value * 10^(local_decimals - erc_decimals)
}
```
and the mirrored (multiply/divide swapped) logic for `convert_to_erc20`, using `checked_sub`/`abs_diff` plus an explicit branch instead of `saturating_sub`, so no scaling silently collapses to a no-op. Add test coverage for the `local_decimals > erc_decimals` case symmetric to the existing tests that only cover `erc_decimals > local_decimals`.

### Proof of Concept
1. Register a token via `register_token` with `local_id` decimals = 18 (e.g., a standard `pallet-assets` asset) and a `ChainConfig.decimals = 6` for some EVM destination (a legitimate configuration the pallet accepts).
2. Call `send(SendParams { asset_id, destination, recipient: attacker, amount: 1_000_000_000_000_000_000 /* 1.0 token, 18 decimals */, .. })`. This burns/escrows exactly `1e18` raw units from the sender locally — correct debit.
3. Inside `send`, `convert_to_erc20(1e18, erc_decimals=6, local_decimals=18)` computes `erc_decimals.saturating_sub(local_decimals) = 0`, so it returns `1e18` unchanged (should be `1e18 * 10^(6-18) = 1e6`).
4. The dispatched ISMP `Message.amount` therefore encodes `1e18` instead of `1e6`.
5. On the destination EVM chain, `HyperFungibleToken.onAccept` mints `1e18` raw units to `attacker` at the token's 6-decimal precision — i.e. `1,000,000,000,000` (one trillion) tokens instead of the intended `1.0` token, a `10^12`x unbacked over-mint from burning a single token locally. [3](#0-2) [2](#0-1)

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

**File:** modules/pallets/hyper-fungible-token/src/lib.rs (L292-303)
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
