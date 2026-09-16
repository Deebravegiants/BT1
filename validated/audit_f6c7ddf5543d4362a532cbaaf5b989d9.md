## Title
Missing bidirectional decimal scaling in `convert_to_erc20`/`convert_to_balance` causes unbacked minting or fund loss in `pallet-hyper-fungible-token` cross-chain transfers - (File: `modules/pallets/hyper-fungible-token/src/impls.rs`)

### Summary
The `pallet-hyper-fungible-token` pallet is explicitly designed to bridge tokens across chains where the same asset can have different decimal precisions (its own README documents that `Precisions` "records the EVM-side decimals so amounts get scaled at the boundary" [1](#0-0) ). However, the two conversion helpers that perform this scaling, `convert_to_erc20` and `convert_to_balance`, only scale correctly in one direction; in the opposite direction they silently apply no scaling at all due to `saturating_sub` clamping to zero, exactly the decimal-normalization gap described in the H-11 report but manifesting here as an actual unbacked mint / fund-loss primitive reachable from a single permissionless `send` extrinsic.

### Finding Description
The helper functions are defined as: [2](#0-1) 

`convert_to_erc20(value, erc_decimals, local_decimals)` multiplies `value` by `10^(erc_decimals.saturating_sub(local_decimals))`. This only produces a correct up-scale when `erc_decimals > local_decimals`. When `local_decimals > erc_decimals` (the destination chain's token representation uses **fewer** decimals than the local asset), `erc_decimals.saturating_sub(local_decimals)` clamps to `0`, so the multiplier becomes `10^0 = 1` — the function passes the raw, high-precision `value` through completely unscaled instead of dividing by `10^(local_decimals - erc_decimals)`.

Symmetrically, `convert_to_balance(value, erc_decimals, local_decimals)` divides by `10^(erc_decimals.saturating_sub(local_decimals))`, which only correctly scales down when `erc_decimals > local_decimals`. When `erc_decimals < local_decimals` (an inbound message carries an amount in a lower-precision remote denomination than the local asset), the divisor clamps to `1`, so the raw low-precision inbound amount is credited directly as if it were already in the local asset's higher-precision units — instead of being multiplied up by `10^(local_decimals - erc_decimals)`.

Both helpers are used on the permissionless, signed extrinsic path:
- `send()` calls `convert_to_erc20(amount, erc_decimals, decimals)` to build the outbound `Message.amount` dispatched via ISMP `DispatchPost`: [3](#0-2) 
- `on_accept()` (inbound receive) and `on_timeout()` (refund) call `convert_to_balance(message.amount, erc_decimals, decimals)` to compute the amount minted/unlocked to the beneficiary: [4](#0-3) [5](#0-4) 

Since decimal precision differences across chains for the *same* logical asset are the pallet's core documented use case (the README explicitly calls out cross-chain decimal scaling as the purpose of `Precisions`), any asset registered with `local_decimals > erc_decimals` for a given destination — a completely legitimate, expected configuration — triggers the unscaled branch on every `send()` to that destination.

### Impact Explanation
On `send()`, when `local_decimals > erc_decimals` for the destination, `convert_to_erc20` emits an ISMP `Message.amount` that is `10^(local_decimals - erc_decimals)` times larger than the correct destination-denominated amount, because the required division is skipped and replaced by a no-op multiply-by-one. This over-inflated amount is what gets minted/unlocked to the beneficiary by the counterpart on the destination chain, i.e. **an unbacked mint**: the recipient receives up to `10^(local_decimals - erc_decimals)`x the value that was actually escrowed/burned on the source chain. Any user with knowledge of an asset's precision configuration can drain the counterpart's minting capability or unlock reserves far beyond what they locked, directly matching the "unbacked mint" / "concrete theft" criteria.

Conversely, on `on_accept`/`on_timeout`, when `erc_decimals < local_decimals` for the relevant chain, `convert_to_balance` under-credits the beneficiary by the same factor, causing legitimate inbound transfers or refunds to be minted/unlocked at a fraction of their true value — a permanent, silent loss of user funds (the escrowed/burned amount on the source side is never fully recovered).

### Likelihood Explanation
This is triggerable by any signed account calling the permissionless `send` extrinsic once an asset is registered with differing decimal precision across chains (a normal, documented configuration, not a misconfiguration) — no privileged role, governance action, or malicious operator is required. It requires only a single dispatched cross-chain message.

### Recommendation
Replace the one-directional `saturating_sub`-based scaling in both `convert_to_erc20` and `convert_to_balance` with a full bidirectional branch (as correctly done elsewhere in this same codebase, e.g. `VWAPOracle._normalizeAmount`): if `erc_decimals >= local_decimals`, multiply by `10^(erc_decimals - local_decimals)`; otherwise divide by `10^(local_decimals - erc_decimals)`. Apply the corresponding inverse logic in `convert_to_balance`.

### Proof of Concept
1. Governance registers asset `X` via `register_token`/`create_erc6160_asset` where the local `pallet-assets` representation has 18 decimals, and `Precisions` for destination chain `D` is set to `6` (a valid, realistic configuration since remote ERC20 tokens can use 6 decimals).
2. A user calls `send(SendParams { asset_id: X, destination: D, amount: 1_000_000 * 10^18, .. })`, burning/escrowing `1_000_000 * 10^18` local units.
3. In `send()`: `erc_decimals = 6`, `decimals = 18`; `convert_to_erc20` computes `6u8.saturating_sub(18) = 0` → multiplier `10^0 = 1` → `erc20_amount = 1_000_000 * 10^18` (unscaled), instead of the correct `1_000_000 * 10^6`. [6](#0-5) 
4. This inflated `Message.amount` is dispatched via ISMP to chain `D`'s paired contract/pallet, which mints/unlocks `1_000_000 * 10^18` units under a 6-decimal denomination — `10^12`x the intended value — to the attacker-chosen recipient, while only `1_000_000` face-value tokens were locked on the source chain.

### Citations

**File:** modules/pallets/hyper-fungible-token/README.md (L31-32)
```markdown
`Precisions` storage records the EVM-side decimals so amounts get scaled at
the boundary.
```

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

**File:** modules/pallets/hyper-fungible-token/src/lib.rs (L292-310)
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
