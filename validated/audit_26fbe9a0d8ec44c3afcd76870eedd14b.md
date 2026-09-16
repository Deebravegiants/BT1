### Title
`convert_to_balance`/`convert_to_erc20` silently no-op the decimal scale when the EVM token has fewer decimals than the local asset, enabling unbacked minting or value loss on cross-chain transfers - (File: modules/pallets/hyper-fungible-token/src/impls.rs)

### Summary
`pallet-hyper-fungible-token`'s decimal-conversion helpers assume the EVM-side (`erc_decimals`) precision is always greater than or equal to the local substrate asset's precision (`local_decimals`). This is the same root-cause bug class as the referenced report: a share/price/amount conversion function silently assumes one asset's decimals dominate the other's, and breaks when a differently-configured token is registered.

### Finding Description
`convert_to_balance` and `convert_to_erc20` compute their scaling exponent with `erc_decimals.saturating_sub(local_decimals)`: [1](#0-0) 

- `convert_to_balance` (used in `on_accept`, converting an incoming EVM-encoded amount into the local balance) divides by `10^(erc_decimals.saturating_sub(local_decimals))`.
- `convert_to_erc20` (used in `send`, converting a local balance into the EVM-encoded amount) multiplies by the same saturating-subtracted exponent.

Both are only correct when `erc_decimals >= local_decimals` — the comments even say so explicitly ("Divides by 10^(erc_decimals - local_decimals) to scale down from ERC20 precision", "Multiplies... to scale up to ERC20 precision"). When a token is registered where the EVM contract's decimals are *fewer* than the local asset's decimals, `erc_decimals.saturating_sub(local_decimals)` clamps to `0`, so the exponent becomes `10^0 = 1` — i.e., **no scaling happens at all** in either direction: [2](#0-1) 

`Precisions` is a plain per-`(asset, chain)` `u8` set via `register_token`/`update_token` with no validation that `erc_decimals >= local_decimals` for every configured chain: [3](#0-2) 

So this is not merely a theoretical edge case — any governance-approved token whose local asset has more decimals than its EVM counterpart (e.g. a local 18-decimal asset paired with a 6-decimal ERC20, the mirror image of the BRIDGE/nexus 18-vs-12 case that IS handled correctly because `erc_decimals(18) > local_decimals(12)` there) hits this silently-broken branch.

### Impact Explanation
- **Outbound (`send`, `convert_to_erc20`):** a user calling the unprivileged `send` extrinsic burns/escrows an amount denominated in local (higher) decimals, but the raw, unscaled integer is placed in the outgoing ISMP message and interpreted by the EVM contract as an amount in its own (lower) decimals. This makes the destination contract mint far more tokens than were actually escrowed on the source chain — e.g. escrowing 1 unit of an 18-decimal local asset (`1e18` raw units) results in minting `1e18` raw units of a 6-decimal ERC20, i.e. `1,000,000` whole tokens instead of `1`. This is an unbacked mint (10^12x here) reachable from a single unprivileged extrinsic.
- **Inbound (`onAccept`/`on_accept`, `convert_to_balance`):** the reverse direction under-credits recipients by the same factor, a permanent value loss for legitimate bridgers.

Both outcomes match the "Accept only concrete theft or permanent freezing of funds, unbacked mint... or unsound state commitment" bar, via the pallet's mint/transfer path (`fungibles::Mutate::mint_into` / `NativeCurrency::transfer`).

### Likelihood Explanation
Requires governance (`CreateOrigin`) to register a token whose local decimals exceed the EVM decimals recorded in `Precisions` — a configuration mistake rather than a coding bug in a caller, but nothing in the pallet prevents or warns about this configuration, and once registered, exploitation only needs a single ordinary `send` transaction from any user, matching the "reachable from a single submitted extrinsic" requirement. Likelihood is Medium: it depends on a specific but plausible token-decimals configuration that the pallet does nothing to guard against, unlike a purely malicious-admin scenario (governance intent here is legitimate registration, not malice).

### Recommendation
Fix `convert_to_balance` and `convert_to_erc20` to handle both directions explicitly instead of relying on `saturating_sub`, e.g.:
```rust
if erc_decimals >= local_decimals {
    value / 10^(erc_decimals - local_decimals)
} else {
    value * 10^(local_decimals - erc_decimals)
}
```
(and symmetrically for `convert_to_erc20`). Additionally, consider validating in `register_token`/`update_token` that the configured decimals produce lossless conversions, or at minimum add a runtime test exercising `erc_decimals < local_decimals` (the current test suite only exercises `erc_decimals(18) > local_decimals(10)`, per `modules/pallets/testsuite/src/tests/pallet_hyper_fungible_token.rs`).

### Proof of Concept
1. Governance calls `register_token` for a new non-native asset whose local `Assets` metadata reports 18 decimals, with `ChainConfig.decimals = 6` for an EVM destination (a legitimate-looking but under-specified configuration since nothing checks this relationship) — this populates `Precisions::<T>::get(asset, evm_chain) = 6`.
2. A user calls `send(asset_id, destination=evm_chain, amount = 1_000_000_000_000_000_000 /* 1.0 token, 18 decimals */)`. The local asset is burned/escrowed for `1e18` raw units.
3. `convert_to_erc20(1e18, erc_decimals=6, local_decimals=18)` computes `erc_decimals.saturating_sub(local_decimals) = 0`, so it returns `1e18 * 10^0 = 1e18` unchanged, per [4](#0-3) .
4. The ISMP message encodes `amount = 1e18` for a contract whose ERC20 `decimals()` is 6 — the destination `HyperFungibleToken`/`WrappedHyperFungibleToken` contract mints `1e18` raw units, which is `1,000,000` whole tokens (10^12 more than the `1.0` token actually escrowed), an unbacked mint that can drain the bridge's economic backing across every future redemption.

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

**File:** modules/pallets/hyper-fungible-token/README.md (L30-43)
```markdown
Decimals between this chain and each remote chain may differ; per-pair
`Precisions` storage records the EVM-side decimals so amounts get scaled at
the boundary.

---

## Storage

| Item | Type | Description |
|------|------|-------------|
| `TokenContracts` | `DoubleMap<StateMachine, AssetId → Vec<u8>>` | EVM contract address of a token on the given chain. Used as the `to` field on outgoing `DispatchPost`. |
| `ContractToAsset` | `DoubleMap<StateMachine, Vec<u8> → AssetId>` | Reverse lookup; on `on_accept` the source contract is mapped back to the local asset. |
| `NativeAssets` | `Map<AssetId → bool>` | Custody model flag (native vs non-native). |
| `Precisions` | `DoubleMap<AssetId, StateMachine → u8>` | EVM decimals for an `(asset, chain)` pair. |
```
