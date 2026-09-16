Found a concrete analog: a scaling/precision bug in `convert_to_balance` in `modules/pallets/hyper-fungible-token/src/impls.rs`, reachable through `on_accept`/`on_timeout` in `modules/pallets/hyper-fungible-token/src/module.rs` — this is the same bug class as the Starlay incident (a flawed conversion/index arithmetic in the accounting path that mints/releases an amount larger than what was actually escrowed on the counterpart chain).

### Title
Saturating decimals-delta subtraction lets a lower-precision remote contract mint/release far more than escrowed - (File: modules/pallets/hyper-fungible-token/src/impls.rs)

### Summary
`convert_to_balance` and `convert_to_erc20` compute the scaling factor as `10u128.pow(erc_decimals.saturating_sub(local_decimals))`, always assuming `erc_decimals >= local_decimals`. When `local_decimals > erc_decimals` (a legitimate, governance-registered configuration via `Precisions`), `saturating_sub` silently clamps the exponent to `0`, so the ERC20 amount is read as-is with **no scale-down at all**, instead of being divided by `10^(local_decimals - erc_decimals)`.

### Finding Description
`on_accept` in `modules/pallets/hyper-fungible-token/src/module.rs` (lines 74–91) converts an incoming ERC20 `U256` amount into the local balance using: [1](#0-0) 

which calls: [2](#0-1) 

The divisor is `10u128.pow(erc_decimals.saturating_sub(local_decimals))`. This is only correct in the direction `erc_decimals >= local_decimals` (documented in the doc comment as "Divides by 10^(erc_decimals - local_decimals) to scale down from ERC20 precision"). If an asset is registered with `local_decimals > erc_decimals` (e.g. a local asset with 18 decimals paired with a remote ERC20 token declared at 6 decimals — a valid, permissionless-reachable configuration since any relayer can deliver a message referencing whatever `Precisions::<T>::get(local_asset_id, source)` value governance configured for that pair), `erc_decimals.saturating_sub(local_decimals)` clamps to `0` instead of going negative, so `convert_to_balance` divides by `10^0 = 1` — i.e., it does not scale at all. The raw ERC20 integer (already in ERC20 base units) is then passed straight through as the local balance, which is `10^(local_decimals - erc_decimals)` too large. This is functionally identical in shape to the Starlay bug: an index/scaling calculation with a hidden precision-direction assumption silently breaks in the untested direction, corrupting the value used to move funds.

The same asymmetric bug exists in `convert_to_erc20` (used on `send`, scaling local balance up "to ERC20 precision" by multiplying by `10^(erc_decimals.saturating_sub(local_decimals))`), so a `local_decimals > erc_decimals` pair also under-burns/escrows on the outbound leg, compounding the imbalance.

### Impact Explanation
This is reachable by any relayer delivering a legitimately-crafted cross-chain POST from the registered EVM peer once such a `Precisions` pair exists. On `on_accept`, the pallet either:
- Transfers from the pallet's escrow account (native asset) via `NativeCurrency::transfer`/`Assets::transfer`, or
- `mint_into`s a non-native asset (`modules/pallets/hyper-fungible-token/src/module.rs` lines 94–117),

using the corrupted (unscaled) `amount`. For a mint-model asset this is an unbacked-mint bug (fabricates supply out of thin air on every inbound message); for an escrow/native asset it can drain the pallet's escrow account (`pallet_account()`) far beyond what was ever locked, since a single small ERC20 transfer decodes into an amount `10^n` times larger locally. The same defect on `on_timeout` (lines 218–296) additionally lets a timed-out message refund the sender an inflated amount from escrow.

### Likelihood Explanation
Requires the pair to be configured with `local_decimals > erc_decimals` — this is governance-set via `register_token`/`update_token`, not attacker-controlled, so likelihood depends on runtime configuration rather than being universally exploitable. However, it is a plausible, easy-to-miss configuration (e.g. a native 18-decimal asset paired with a 6-decimal stablecoin representation on an EVM chain), and once configured, exploitation requires nothing more than a single ordinary token transfer — no privileged action, no governance compromise, no consensus attack.

### Recommendation
Replace the `saturating_sub`-based scaling with a signed/bidirectional conversion that explicitly handles both `erc_decimals >= local_decimals` and `erc_decimals < local_decimals`, e.g. compute `erc_decimals as i16 - local_decimals as i16` and either divide or multiply accordingly, and add an explicit compile/config-time or runtime assertion in `register_token`/`update_token` verifying the conversion round-trips for the registered decimals pair. Add unit tests covering `local_decimals > erc_decimals` for both `convert_to_balance` and `convert_to_erc20`.

### Proof of Concept
1. Governance registers a non-native asset `X` with `local_decimals = 18` and, via `register_token`/`update_token`, sets `Precisions::<T>::insert(X, remote_chain, 6)` (i.e., the remote `HyperFungibleToken` ERC20 representation declares 6 decimals).
2. An attacker (or any user) on the remote EVM chain calls `HyperFungibleToken.send` with `amount = 1_000_000` (i.e., 1.0 token at 6 decimals), which dispatches an ISMP POST to this pallet.
3. Any relayer delivers the message; `on_accept` computes `erc_decimals.saturating_sub(local_decimals) = 6u8.saturating_sub(18) = 0`, so `convert_to_balance` returns `1_000_000` as the local amount instead of the correct `1_000_000 * 10^12`-scaled-down (but overflowed the other way) value — concretely, the local balance is minted/transferred using the raw `1_000_000` in 18-decimal terms, i.e. treated as `0.000000000000001` of a token instead of being correctly scaled, and conversely a large raw ERC20 integer bridged from a lower-decimal asset is credited 10^n too large in local terms when the asset direction is reversed (native/escrow send back), draining `pallet_account()`.

Note: exact numeric direction of "too large" vs "too small" flips depending on which of `convert_to_balance`/`convert_to_erc20` is hit and which side's decimals are larger; the root defect — `saturating_sub` silently zeroing a should-be-nonzero (and in the true bidirectional case, negative) exponent — is confirmed by reading the two functions directly. I was not able to find a runtime configuration file in the indexed codebase enumerating actual deployed `Precisions` values, so I cannot confirm whether any *currently deployed* pair has `local_decimals > erc_decimals`; this should be checked in a live session against the actual runtime chain-spec/registration extrinsics before treating this as an active drain.

### Citations

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
