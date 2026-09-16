### Title
Decimals-mismatch scaling bug in `pallet-hyper-fungible-token`'s ERC20 conversion helpers causes unbacked over-minting when the local asset has more decimals than the remote ERC20 token - (File: `modules/pallets/hyper-fungible-token/src/impls.rs`)

### Summary
The `hyper-fungible-token` pallet's decimal-scaling helpers, `convert_to_balance` and `convert_to_erc20`, both compute their scaling exponent with `erc_decimals.saturating_sub(local_decimals)`. This one-directional `saturating_sub` is correct only when `erc_decimals >= local_decimals`. When the local asset is configured with *more* decimals than its remote ERC20 counterpart, the exponent saturates to `0`, and the raw balance is passed through the boundary completely unscaled instead of being divided down. On the outgoing `send()` path this causes the ISMP message to carry an amount that is `10^(local_decimals - erc_decimals)` times larger than intended, in an unsigned message the destination `HyperFungibleToken`/`WrappedHyperFungibleToken` contract will mint or release verbatim.

### Finding Description
`convert_to_erc20` and `convert_to_balance` are the sole scaling functions used at the token-bridge boundary: [1](#0-0) 

Both use the *same* exponent, `erc_decimals.saturating_sub(local_decimals)`, but apply it in opposite arithmetic directions (divide for `convert_to_balance`, multiply for `convert_to_erc20`). This is only self-consistent for `erc_decimals >= local_decimals`. When `local_decimals > erc_decimals` (e.g. a native/local asset registered with 12 or 18 decimals bridged to a remote ERC20 deployed with 6 decimals — the docs explicitly say "Decimals between this chain and each remote chain may differ"): [2](#0-1) 

- `erc_decimals.saturating_sub(local_decimals)` saturates to `0`.
- `convert_to_erc20` multiplies by `10^0 = 1`: the raw local balance (already in the finer, larger-magnitude local unit) is sent unchanged as the ERC20 `amount` field of the outgoing `Message`, instead of being divided down by `10^(local_decimals - erc_decimals)`.

This `erc20_amount` is embedded directly into the cross-chain `Message` dispatched via ISMP `send()`: [3](#0-2) 

`send()` is a plain signed extrinsic — reachable by any unprivileged user — so an attacker registered/using an asset pair where `local_decimals > erc_decimals` can burn or escrow a tiny local amount and have the message declare an amount inflated by `10^(local_decimals - erc_decimals)`, which the counterpart EVM contract will mint/release to the attacker's chosen recipient once the message is relayed and accepted.

The reverse direction (`convert_to_balance`, used in `on_accept` for minting/crediting locally) suffers the symmetric flaw and instead *under-credits* incoming transfers in this same decimals configuration, which is a correctness bug but not directly an attacker-profitable path.

This is the same class of arithmetic-direction rounding/scaling defect described in the source report (`Registry::_convertValueInUsdToValueInNumeraire` rounding the wrong way), but manifesting far more severely here: rather than a bounded rounding-down/up discrepancy, the missing scale factor produces an unbounded multiplicative amplification of value crossing the bridge boundary.

### Impact Explanation
This is an unbacked-mint / theft vulnerability at the token-bridge boundary. For any registered asset pair where the local chain's decimals exceed the remote EVM ERC20's decimals, every outgoing `send()` mints/releases `10^(local_decimals - erc_decimals)` times the intended amount on the destination chain, while only the tiny, unscaled amount is escrowed/burned on the source chain. This lets an attacker drain the counterpart contract's token reserves (native custody) or mint arbitrary supply (non-native/wrapped custody) far in excess of what was locked, a direct and unbounded theft of funds / unbacked mint.

### Likelihood Explanation
Triggering requires only that governance (`CreateOrigin`) has registered at least one asset pair whose local decimals are greater than the paired chain's ERC20 decimals — a realistic and likely configuration (e.g., an 18-decimal Substrate-native asset bridged to a 6-decimal ERC20 like USDC-style tokens, or any chain pairing where the local asset simply uses more decimal places than its remote representation). Once such a pair exists, exploitation requires nothing more than calling the public `send()` extrinsic with a valid registered `asset_id`; no privileged role or governance action is needed by the attacker.

### Recommendation
Fix both helpers to branch on the sign of the decimals difference, exactly as done correctly elsewhere in the codebase (e.g. `VWAPOracle._normalizeAmount`, which branches on `_decimals < 18` vs `>= 18`):

```rust
pub fn convert_to_balance<B: core::str::FromStr>(value: U256, erc_decimals: u8, local_decimals: u8) -> Result<B, B::Err> {
    let scaled = if erc_decimals >= local_decimals {
        value / U256::from(10u128.pow((erc_decimals - local_decimals) as u32))
    } else {
        value * U256::from(10u128.pow((local_decimals - erc_decimals) as u32))
    };
    scaled.to_string().parse::<B>()
}

pub fn convert_to_erc20(value: u128, erc_decimals: u8, local_decimals: u8) -> U256 {
    if erc_decimals >= local_decimals {
        U256::from(value) * U256::from(10u128.pow((erc_decimals - local_decimals) as u32))
    } else {
        U256::from(value) / U256::from(10u128.pow((local_decimals - erc_decimals) as u32))
    }
}
```
Add regression tests covering `local_decimals > erc_decimals` for both directions, mirroring the existing coverage for the opposite case in `modules/pallets/testsuite/src/tests/pallet_hyper_fungible_token.rs`.

### Proof of Concept
1. Governance registers a non-native asset with `local_decimals = 18` and `Precisions[(asset_id, dest_chain)] = 6` (a legitimate mismatched pairing per the pallet's design).
2. Attacker calls `send(params)` with `amount = 1_000_000` raw local units (`0.000001` of the local asset at 18 decimals) targeting `dest_chain`.
3. `erc_decimals.saturating_sub(local_decimals) = 6.saturating_sub(18) = 0`, so `convert_to_erc20` computes `erc20_amount = amount * 10^0 = 1_000_000`.
4. The dispatched `Message.amount = 1_000_000` is interpreted on the EVM side as `1_000_000` raw units of a 6-decimal ERC20 token, i.e. `1.0` whole token — a `10^12`× amplification versus the `10^-18` of a token that was actually escrowed/burned.
5. Once relayed and accepted, the counterpart contract mints/releases `1.0` token to the attacker's chosen recipient for a cost of `0.000001` locally escrowed tokens, repeatable to drain/inflate supply.

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

**File:** modules/pallets/hyper-fungible-token/README.md (L30-32)
```markdown
Decimals between this chain and each remote chain may differ; per-pair
`Precisions` storage records the EVM-side decimals so amounts get scaled at
the boundary.
```

**File:** modules/pallets/hyper-fungible-token/src/lib.rs (L292-315)
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
