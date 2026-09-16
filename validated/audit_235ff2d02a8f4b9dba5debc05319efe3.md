### Title
Saturating decimal-difference scaling in `convert_to_erc20`/`convert_to_balance` allows unbacked minting or fund freezing on cross-decimal HyperFungibleToken transfers - (File: `modules/pallets/hyper-fungible-token/src/impls.rs`)

### Summary
`pallet-hyper-fungible-token`'s decimal conversion helpers use `saturating_sub` when computing the scaling exponent between local-asset decimals and the remote ERC20's registered decimals. When the remote (or local) side has fewer decimals than the other, the subtraction saturates to `0`, silently skipping the scale factor instead of scaling in the opposite direction. This is the same bug class as the Cooler report ("fixed decimals" assumption breaking arithmetic for tokens with different decimal counts), but here it can distort the actual bridged amount by orders of magnitude rather than merely zeroing an interest rate.

### Finding Description
`convert_to_erc20` (outbound, local balance → ERC20 `U256`) and `convert_to_balance` (inbound, ERC20 `U256` → local balance) both compute a single-direction scale factor: [1](#0-0) 

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

Both functions only handle the case `erc_decimals >= local_decimals` correctly (dividing/multiplying by `10^(erc_decimals - local_decimals)`). When `erc_decimals < local_decimals`, `saturating_sub` clamps to `0`, so the exponent becomes `10^0 = 1` — i.e., **no scaling is applied at all**, instead of the mathematically required inverse operation (multiply on the divide side, divide on the multiply side).

This is invoked directly in the `send` extrinsic: [2](#0-1) 

`erc_decimals` comes from the per-`(asset, chain)` `Precisions` storage (set by `register_token`/`update_token`), and `decimals` is either `T::Decimals::get()` for the native asset or the local `fungibles::Inspect::decimals()` for other assets. Whichever value is smaller determines whether the arithmetic silently drops scaling.

Concretely:
- **Outbound (`convert_to_erc20`)**: if the local asset has more decimals than the destination ERC20 (`erc_decimals < local_decimals`), the raw local integer amount is passed through unscaled into the `Message.amount` field dispatched to the EVM contract. The EVM `HyperFungibleToken`/`WrappedHyperFungibleToken` `onAccept` will mint that raw number of *ERC20* base units (interpreted at `erc_decimals`), which — since `erc_decimals < local_decimals` — represents a value up to `10^(local_decimals - erc_decimals)` times larger than what was actually escrowed/burned on the substrate side. This mints unbacked value on the destination chain.
- **Inbound (`convert_to_balance`)**: symmetric issue on `on_accept`, if `erc_decimals < local_decimals` for an inbound message, the local balance credited is under- or mis-scaled relative to what should be minted, causing incorrect balances on receipt (potential lock/loss of funds or, depending on direction, a mismatched excess mint).

The registration path in `register_token` for the EVM/BridgeToken example enforces `chains[].decimals` be declared appropriately (e.g., BRIDGE token's docs mandate the EVM side register 18 decimals to match nexus's 12, with the pallet always scaling *up* by `10^6` — i.e., the intended design assumes `erc_decimals >= local_decimals`). However, the `register_token`/`update_token` extrinsics (per README, gated by `CreateOrigin`) do not appear to enforce `erc_decimals >= local_decimals` as an invariant in the conversion helpers themselves; the helpers will silently misbehave for any asset pairing where that assumption doesn't hold (e.g., a locally-registered 18-decimal asset paired with a 6-decimal remote ERC20 registration).

### Impact Explanation
If any registered pair violates `erc_decimals >= local_decimals`, an unprivileged user calling `send()` can bridge a small amount and have the destination `HyperFungibleToken` contract mint/release an amount inflated by `10^(local_decimals - erc_decimals)` — real unbacked minting of value on the destination chain, breaking the escrow-backed invariant documented for the token bridge (`docs/content/developers/polkadot/hyper-fungible-token.mdx`, `modules/pallets/hyper-fungible-token/README.md`). This is a concrete theft/unbacked-mint vector reachable from a single signed `send` extrinsic, matching the required severity bar (Medium/High).

### Likelihood Explanation
Likelihood depends on whether `CreateOrigin` (governance/root-gated `register_token`) would ever register a chain config with fewer decimals than the local asset. The pallet does not appear to validate this relationship at registration time in the code reviewed, so a single misconfiguration — or a deliberately crafted `update_token`/`register_token` call by anyone possessing `CreateOrigin` for a low-value/attacker-influenced asset — is enough to trigger. Because `CreateOrigin` is privileged, exploitation requires either an operational misconfiguration or a privileged actor, which lowers likelihood somewhat, but the reachable path itself (the `send` extrinsic call by any signed user against a misconfigured pair) is unprivileged and directly executes the flawed math.

### Recommendation
Fix the scaling helpers to handle both directions explicitly instead of relying on `saturating_sub`:

```rust
pub fn convert_to_balance<B: core::str::FromStr>(
    value: U256, erc_decimals: u8, local_decimals: u8,
) -> Result<B, B::Err> {
    let dec_str = if erc_decimals >= local_decimals {
        value / U256::from(10u128.pow((erc_decimals - local_decimals) as u32))
    } else {
        value * U256::from(10u128.pow((local_decimals - erc_decimals) as u32))
    }.to_string();
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
Additionally, add a registration-time invariant check (or explicit documentation + runtime assertion) in `register_token`/`update_token` if the protocol intends to only ever support `erc_decimals >= local_decimals`, to fail closed rather than silently miscompute.

### Proof of Concept
1. Governance registers a local asset with `local_decimals = 18` and, via `register_token`, configures a destination `ChainConfig { decimals: 6, .. }` for some EVM chain (no code path prevents this).
2. A user calls `send(params)` with `amount = 1_000_000_000_000_000_000` (1 whole token, 18 decimals).
3. `erc_decimals = 6`, `decimals = 18` → `erc_decimals.saturating_sub(local_decimals) = 0` in `convert_to_erc20`, so `erc20_amount = value = 1_000_000_000_000_000_000` unchanged.
4. This raw `U256` is placed into `Message.amount` and dispatched to the EVM `HyperFungibleToken` contract, which mints `1_000_000_000_000_000_000` units of a token declared with 6 decimals — i.e., `1_000_000_000_000` (one trillion) whole tokens, versus the 1 whole token actually escrowed/burned locally. This is a 10^12 inflation factor, demonstrating unbacked minting. [3](#0-2) [4](#0-3)

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

**File:** modules/pallets/hyper-fungible-token/src/lib.rs (L254-296)
```rust
			let erc_decimals = Precisions::<T>::get(params.asset_id.clone(), params.destination)
				.ok_or(Error::<T>::DecimalsNotFound)?;

			// Lock or burn the local asset
			let decimals = if params.asset_id == T::NativeAssetId::get() {
				// escrow the native asset
				<T as Config>::NativeCurrency::transfer(
					&who,
					&Self::pallet_account(),
					params.amount,
					ExistenceRequirement::AllowDeath,
				)?;
				T::Decimals::get()
			} else {
				let is_native = NativeAssets::<T>::get(params.asset_id.clone());
				if is_native {
					<T as Config>::Assets::transfer(
						params.asset_id.clone(),
						&who,
						&Self::pallet_account(),
						params.amount.into(),
						Preservation::Expendable,
					)?;
				} else {
					<T as Config>::Assets::burn_from(
						params.asset_id.clone(),
						&who,
						params.amount.into(),
						Preservation::Expendable,
						Precision::Exact,
						Fortitude::Polite,
					)?;
				}
				<T::Assets as fungibles::metadata::Inspect<T::AccountId>>::decimals(
					params.asset_id.clone(),
				)
			};

			// Encode the Message body
			let sender: [u8; 32] = who.clone().into();
			let amount: u128 = params.amount.into();
			let erc20_amount = convert_to_erc20(amount, erc_decimals, decimals);

```
