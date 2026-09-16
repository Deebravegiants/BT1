### Title
Cross-chain ERC20→local-balance decimal conversion in `pallet-hyper-fungible-token` can round a real transfer down to zero, permanently losing value burned/escrowed on the source chain - (File: `modules/pallets/hyper-fungible-token/src/impls.rs`)

### Summary
`pallet-hyper-fungible-token`'s `convert_to_balance` performs integer division to scale an incoming ERC20 `U256` amount down to the pallet's local balance precision. When the ERC20-side amount is smaller than the scaling factor `10^(erc_decimals - local_decimals)`, the division truncates to zero, exactly the "BancorFormula returns zero" rounding-to-zero class from the source report — the sender already had funds burned/escrowed on the EVM side (`HyperFungibleToken.send()`), but the destination pallet credits nothing.

### Finding Description
`convert_to_balance` in `modules/pallets/hyper-fungible-token/src/impls.rs` computes: [1](#0-0) 

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

This function is used by the pallet's incoming-message handler (`module.rs`, per grep results) when an ISMP POST from a `HyperFungibleToken`/`WrappedHyperFungibleToken` EVM contract arrives, to convert the ERC20-precision `amount` field of the ABI-encoded `Message` into the pallet's local balance type before minting (non-native asset) or releasing from escrow (native asset) to the beneficiary, per the pallet README's documented `on_accept` behaviour: [2](#0-1) 

Registration enforces `config.decimals >= local_decimals` (`ErcDecimalsBelowLocal`), so `erc_decimals - local_decimals` is always non-negative and the scaling factor `10^(erc_decimals - local_decimals)` can be large (e.g. `BRIDGE` is 18-decimal on EVM chains and 12-decimal on nexus, giving a 10^6 scale factor per the docs): [3](#0-2) [4](#0-3) 

If a sender on the EVM side burns/escrows any positive `amount` less than that scaling factor (e.g. any amount `< 1_000_000` wei for a 10^6 scale), `convert_to_balance` truncates the quotient to zero. There is no check anywhere in the visible pallet code (`lib.rs` call handlers, `impls.rs`, `error.rs`) that rejects a zero converted amount before crediting the beneficiary — the only related error variant, `InvalidAmountConversion`, guards the `FromStr` parse failure path, not a zero-value result.

### Impact Explanation
The EVM-side `HyperFungibleToken.send()`/`BridgeToken` path has already burned the sender's tokens (or, for `BridgeToken`, escrowed native BRIDGE on nexus) and dispatched an ISMP POST before the destination processes the message. If the destination-side conversion rounds the credited amount to zero, the sender's tokens are burned with no corresponding mint/release on the destination — a permanent loss of funds for that user, with no compensating credit anywhere in the system (this is not a timeout scenario, so the timeout re-mint path on the source side does not apply once the message is accepted). This directly matches the "Accept only concrete theft or permanent freezing of funds" validation bar: value is destroyed rather than delivered.

### Likelihood Explanation
Reachable from a single, unprivileged, ordinary user action: any user calling `pallet-hyper-fungible-token::send()` (or the EVM-side `HyperFungibleToken.send`) with a small enough `amount` relative to the registered decimal gap between the source and destination chain triggers this. No attacker cooperation, governance action, or malicious relayer is required — a normal small-value transfer (e.g., dust, or a user unaware of the decimal scaling) reaching the destination chain suffices. Given `BRIDGE`'s documented 10^6 scale factor between 18- and 12-decimal representations, any transfer under one-millionth of a token unit reproduces this deterministically.

### Recommendation
In the incoming-message handler that calls `convert_to_balance` (in `module.rs`), reject the message (return an error, e.g. a new `Error::AmountRoundsToZero`) whenever the converted local balance is zero but the original ERC20 `amount` was non-zero, rather than silently minting/releasing zero. Symmetrically, consider adding a minimum-transferable-amount check on the EVM-side `send()` (or pallet-side outbound `send`) so that a value guaranteed to round to zero on the receiving side is rejected at the point of burn/escrow, before the sender's funds are locked.

### Proof of Concept
Given a registered pair with `erc_decimals = 18` (EVM side) and `local_decimals = 12` (substrate side), as configured for `BRIDGE`/`pall_hft` per the docs and `BridgeTokenTest.t.sol`:

1. A user calls `HyperFungibleToken.send(...)` (or `BridgeToken.send`) on the EVM chain with `amount = 999_999` (raw ERC20 units, 18 decimals) — a strictly positive, sub-dust amount below the `10^6` scale factor. This burns/escrows the tokens and dispatches an ISMP POST containing `Message.amount = 999_999`.
2. On delivery, `pallet-hyper-fungible-token`'s `on_accept` path calls `convert_to_balance(U256::from(999_999), 18, 12)`, computing `999_999 / 10^6 = 0`.
3. The pallet proceeds to mint/release `0` tokens to the beneficiary (no error path exists for a zero-but-nonzero-input conversion in the reviewed code).
4. Result: the sender's `999_999` raw ERC20 units are burned/escrowed on the source chain, and the beneficiary receives nothing on the destination chain — a silent, permanent loss of value.

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

**File:** modules/pallets/hyper-fungible-token/README.md (L81-89)
```markdown
## ISMP module behaviour

- `on_accept` — receives `Send` messages from the paired EVM contract. Maps
  the source contract back to a local asset via `ContractToAsset`, scales the
  amount using `Precisions`, then mints (non-native) or releases from escrow
  (native) to the beneficiary. Emits `TokenReceived`.
- `on_timeout` — refunds the original sender's balance from escrow or by
  re-minting. Emits `TokenRefunded`.
- `on_response` — unused; this pallet uses post-only messaging.
```

**File:** evm/src/apps/BridgeToken.sol (L33-37)
```text
 *
 * `decimals()` is the inherited ERC20 default of 18 while BRIDGE is 12 decimals on nexus, so the
 * pallet scales by 10^6 in both directions. The chain config registered on nexus via `register_token`
 * must therefore declare 18 decimals for this contract.
 */
```

**File:** evm/tests/foundry/BridgeTokenTest.t.sol (L62-68)
```text
    function testMetadataIsFixedInTheBytecode() public view {
        assertEq(bridge.name(), "Hyperbridge");
        assertEq(bridge.symbol(), "BRIDGE");
        // 18 here while BRIDGE is 12 decimals on nexus, so the pallet scales by 10^6 in
        // both directions and `register_token` must declare 18 for this contract.
        assertEq(bridge.decimals(), 18);
    }
```
