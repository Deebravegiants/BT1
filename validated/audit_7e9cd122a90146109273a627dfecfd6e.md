## Title
Incorrect decimal-scaling direction in `pallet-hyper-fungible-token`'s `convert_to_erc20`/`convert_to_balance` causes unbacked mint / fund loss when the remote ERC20 has fewer decimals than the local asset - ([File: modules/pallets/hyper-fungible-token/src/impls.rs])

## Summary
`pallet-hyper-fungible-token`'s cross-chain amount conversion helpers only implement one direction of decimal scaling. They assume the remote EVM token's decimals (`erc_decimals`) are always `>=` the local asset's decimals (`local_decimals`). When a governance-registered pairing has the opposite relationship (local asset decimals higher than the remote ERC20's decimals — a realistic and explicitly supported configuration per this pallet's own `Precisions` storage), `saturating_sub` silently clamps the scaling exponent to zero instead of scaling in the other direction. This produces amounts that are off by `10^(local_decimals - erc_decimals)`, exactly the class of bug described in the Paladin report (wrong power-of-ten scaling from an unhandled decimals mismatch), but here it is reachable from an unprivileged `send` extrinsic and results in an unbacked mint on the EVM side.

## Finding Description
Two helper functions perform the boundary conversion: [1](#0-0) 

```rust
/// Converts an ERC20 U256 amount to a local balance type
/// Divides by 10^(erc_decimals - local_decimals) to scale down from ERC20 precision.
pub fn convert_to_balance<B: core::str::FromStr>(...) -> Result<B, B::Err> {
	let dec_str = (value /
		U256::from(10u128.pow(erc_decimals.saturating_sub(local_decimals) as u32)))
	.to_string();
	...
}

/// Converts a local u128 balance to an ERC20 U256 amount
/// Multiplies by 10^(erc_decimals - local_decimals) to scale up to ERC20 precision
pub fn convert_to_erc20(value: u128, erc_decimals: u8, local_decimals: u8) -> U256 {
	U256::from(value) * U256::from(10u128.pow(erc_decimals.saturating_sub(local_decimals) as u32))
}
```

Both functions compute `erc_decimals.saturating_sub(local_decimals)`. This only produces a correct exponent when `erc_decimals >= local_decimals`. When `erc_decimals < local_decimals`, `saturating_sub` clamps to `0`, so the exponent becomes `10^0 = 1` — i.e. **no scaling is applied at all**, even though the two chains disagree by `10^(local_decimals - erc_decimals)`.

These helpers are used on both the outbound (`send`) and inbound (`on_accept`/`on_timeout`) paths: [2](#0-1) [3](#0-2) 

The pallet's own documentation confirms that per-pair decimal mismatches in either direction are an expected, governance-configured scenario: [4](#0-3) 

`Precisions` stores an arbitrary `u8` decimals value per `(AssetId, StateMachine)` pair with no constraint that it must be `>=` the local asset's decimals (which itself is arbitrary, taken from `pallet-assets` metadata or `T::Decimals`). A very plausible real deployment is a locally-registered asset with 18 decimals (e.g., a DOT-ecosystem token or a wrapped stablecoin created with 18-decimal `pallet-assets` metadata) paired with an EVM-side ERC20 that legitimately uses 6 decimals (the common convention for USDC/USDT-style tokens).

## Impact Explanation
- **Outbound (`send` → `convert_to_erc20`):** if `local_decimals (18) > erc_decimals (6)`, the exponent clamps to `10^0`. A user sending `1 * 10^18` (1 token in local units) burns/escrows 1 token locally but the ERC20 message encodes `amount = 1 * 10^18` raw, which the destination `HyperFungibleToken`/`WrappedHyperFungibleToken` contract mints/releases directly in the remote ERC20's own units. Since the remote token only has 6 decimals, minting `10^18` raw units is `10^12` times the intended amount — an **unbacked mint** of `10^12` tokens on the destination chain, i.e. attacker-controlled economic value creation from a single unprivileged `send` call.
- **Inbound (`on_accept`/`on_timeout` → `convert_to_balance`):** the same asymmetry underscales a legitimate deposit from the EVM side by the same factor, causing **permanent loss of value** for the depositor (their locally-credited balance is undervalued by `10^(local_decimals-erc_decimals)`).

Either direction is a concrete violation of backing/solvency for the bridged asset, matching the "unbacked mint" / "permanent freezing of funds" impact classes. This is directly reachable by any signed account calling `pallet_hyper_fungible_token::send`, with no privileged role required — only a governance-set `Precisions` entry that puts the local asset's decimals above the remote ERC20's decimals, which is a supported and plausible configuration, not an admin-malice scenario.

## Likelihood Explanation
Likelihood is Medium-High: it requires no attacker privilege and triggers automatically any time governance registers a local asset whose decimals exceed the paired chain's ERC20 decimals (a common real-world case, e.g. bridging a locally-18-decimal asset to a 6-decimal USDC-style ERC20 peer). No malicious governance is needed — this is a routine, foreseeable configuration; the bug is a pure arithmetic/direction error in the conversion helpers, not a misuse of privilege.

## Recommendation
Fix both helpers to scale in the correct direction regardless of which side has more decimals, e.g.:

```rust
pub fn convert_to_balance<B: core::str::FromStr>(value: U256, erc_decimals: u8, local_decimals: u8) -> Result<B, B::Err> {
    let dec_str = if erc_decimals >= local_decimals {
        (value / U256::from(10u128.pow((erc_decimals - local_decimals) as u32))).to_string()
    } else {
        (value * U256::from(10u128.pow((local_decimals - erc_decimals) as u32))).to_string()
    };
    dec_str.parse::<B>()
}

pub fn convert_to_erc20(value: u128, erc_decimals: u8, local_decimals: u8) -> U256 {
    if erc_decimals >= local_decimals {
        U256::from(value) * U256::from(10u128.pow((erc_decimals - local_decimals) as u32))
    } else {
        U256::from(value) / U256::from(10u128.pow((local_decimals - erc_decimals) as u32))
    }
}
```

Add explicit test coverage for the `local_decimals > erc_decimals` case (currently the test suite likely only exercises the `erc_decimals >= local_decimals` example from the docs, e.g. BRIDGE's 12→18 case).

## Proof of Concept
1. Governance registers a local asset `X` via `register_token` with `local_decimals = 18` (e.g. `pallet-assets` metadata), and sets `Precisions::<T>::insert(X, DestChain, 6)` for a destination EVM chain whose deployed ERC20 for `X` uses 6 decimals.
2. A user calls `send(params { asset_id: X, amount: 1_000_000_000_000_000_000 /* 1 token, 18-dec */, destination: DestChain, ... })`.
3. Inside `send`, `erc_decimals = 6`, `decimals = 18`; `convert_to_erc20(1e18, 6, 18)` computes `10u128.pow(6u8.saturating_sub(18) as u32) = 10^0 = 1`, returning `erc20_amount = 1e18` unchanged.
4. The dispatched `Message.amount = 1e18` is delivered to the destination `HyperFungibleToken` contract's `onAccept`, which mints `1e18` raw units of a 6-decimal ERC20 — i.e. `1,000,000,000,000` (one trillion) tokens instead of the intended `1` token, an unbacked mint of `10^12`x.

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

**File:** modules/pallets/hyper-fungible-token/src/lib.rs (L292-296)
```rust
			// Encode the Message body
			let sender: [u8; 32] = who.clone().into();
			let amount: u128 = params.amount.into();
			let erc20_amount = convert_to_erc20(amount, erc_decimals, decimals);

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
