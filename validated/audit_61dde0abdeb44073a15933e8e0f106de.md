### Title
Live re-query of asset decimals breaks the registration-time decimals invariant, corrupting cross-chain amount scaling in `pallet-hyper-fungible-token` - (File: `modules/pallets/hyper-fungible-token/src/module.rs`, `modules/pallets/hyper-fungible-token/src/impls.rs`, `modules/pallets/hyper-fungible-token/src/lib.rs`)

### Summary
`register_token` validates the decimals invariant (`erc_decimals >= local_decimals`) exactly once, at registration time, using a **snapshot** of the asset's current metadata decimals. However, `send`, `on_accept`, and `on_timeout` never store or reuse that snapshot — they call `fungibles::metadata::Inspect::decimals(asset_id)` **live**, on every cross-chain transfer, while the ERC20-side decimals (`Precisions`) stay fixed forever. Because `pallet-assets` metadata decimals are mutable independently of the bridge registration (via the asset's own `Issuer`/admin role, not protocol governance), this design assumes the collateral/asset "decimals never change" — the same class of assumption flagged in the reference report — without actually pinning it. This is the direct analog: TAU's `TauMath` assumed a fixed 18-decimals collateral and broke when that assumption didn't hold; here the pallet assumes the once-checked decimals relationship holds forever and re-derives it live instead of storing it.

### Finding Description
`register_token` computes `local_decimals` from the live asset metadata and checks it against the configured `erc_decimals` for each destination chain: [1](#0-0) 

This check is never repeated afterward. `convert_to_balance`/`convert_to_erc20` compute the scaling exponent as `erc_decimals.saturating_sub(local_decimals)` (or the reverse), which silently returns `0` — i.e., **no scaling at all** — whenever `local_decimals >= erc_decimals`, instead of erroring: [2](#0-1) 

Both `send()` and the ISMP `on_accept`/`on_timeout` handlers re-fetch `local_decimals` live from `fungibles::metadata::Inspect` at call time rather than from a stored snapshot taken at registration: [3](#0-2) [4](#0-3) [5](#0-4) 

If the underlying `pallet-assets` asset's decimals metadata is changed after registration (e.g. via `pallet_assets::set_metadata`, which is callable by the asset's own admin/issuer role — a permission an ordinary asset creator holds, not protocol governance/`CreateOrigin`), the invariant `erc_decimals >= local_decimals` enforced only once at `register_token` no longer holds for later transfers. `pallet-assets` decimals metadata changes do **not** rescale existing raw balances; they only change how the same raw integer is interpreted/exponentiated by callers like this pallet. Consequently:

- On `send()` (outbound, local → EVM): `convert_to_erc20` multiplies by `10^(erc_decimals.saturating_sub(local_decimals))`. If `local_decimals` is lowered after registration, the multiplier increases (or, if it crosses `erc_decimals`, `saturating_sub` incorrectly clamps to `0`, dropping scaling entirely instead of the correct up-scale). A user burning/escrowing a raw balance under a *lowered* decimals interpretation causes the pallet to mint a disproportionately large ERC20 amount on the destination EVM `HyperFungibleToken`/`WrappedHyperFungibleToken` contract relative to what was actually escrowed/burned.
- On `on_accept`/`on_timeout` (inbound, EVM → local): the same asymmetry can under- or over-credit the local balance relative to the actual ERC20 amount burned/escrowed on the EVM side.

This is reachable by a single unprivileged action — the asset's metadata admin calling `set_metadata` — with no need to compromise protocol governance, `CreateOrigin`, or the relayer; the bridging pallet itself never re-validates the relationship it originally checked.

### Impact Explanation
A decimals mismatch introduced after registration lets a user mint more `HyperFungibleToken`/`WrappedHyperFungibleToken` supply on a destination EVM chain than the value actually escrowed/burned on the substrate side (or vice versa, permanently mis-crediting/losing value on refund/timeout). Because the EVM side supply is meant to be fully backed by the substrate-side escrow/burn accounting, an amplified `convert_to_erc20` output is effectively unbacked minting of the bridged token — a direct fund-theft/insolvency vector for the bridge, matching the "high" severity classification of the original 18-decimals report (comparisons/scalings computed under a decimals assumption that individual assets are not guaranteed to satisfy).

### Likelihood Explanation
Likelihood is moderate: it requires (a) a token whose local asset's decimals metadata remains mutable by a party other than bridge governance after `register_token`, and (b) that party changing decimals post-registration. `pallet-assets` decimals are commonly left admin-mutable for legitimate reasons (correcting a mistake, rebranding), so this is a realistic operational scenario rather than a purely theoretical one, and it requires no privileged access to the bridge pallet itself — only to the (potentially separate) asset's own metadata-admin role.

### Recommendation
Snapshot `local_decimals` in the same per-`(asset, chain)` `Precisions`-like storage at `register_token` time (or store `local_decimals` alongside `erc_decimals`) instead of re-querying live asset metadata in `send`, `on_accept`, and `on_timeout`. Re-validate (or refuse to process) any transfer where the live decimals no longer match the snapshot, and replace the `saturating_sub` clamps in `convert_to_balance`/`convert_to_erc20` with checked arithmetic that hard-errors instead of silently defaulting to a 1:1 conversion when the invariant is violated.

### Proof of Concept
1. Governance calls `register_token` for asset `X` (created via permissionless `pallet_assets::create`, decimals currently `6`) with `ChainConfig { decimals: 6 }` for EVM chain `C` — passes the `config.decimals >= local_decimals` check (6 >= 6). [1](#0-0) 
2. The asset's admin (its creator, an ordinary account, not bridge governance) calls `pallet_assets::set_metadata` on asset `X`, lowering `decimals` to `0`. Existing raw balances are unchanged.
3. A user calls `send()` with `params.amount` = their raw balance of `X`. `local_decimals` is now re-fetched live as `0`, so `convert_to_erc20` computes `value * 10^(6 - 0) = value * 1_000_000`. [6](#0-5) [7](#0-6) 
4. The dispatched `Message.amount` is 1,000,000× the correct ERC20 amount that should correspond to the escrowed/burned value; the destination `HyperFungibleToken` contract mints that inflated amount to the recipient, unbacked by the actual value moved on the source chain.

I was not able to fully trace `update_token`'s validation logic (only referenced in docs/README, not read directly) or confirm whether `pallet-assets`'s exact deployment configuration in this codebase restricts `set_metadata` origin further than the standard `Issuer`/`Owner` role — this would affect exact likelihood but not the core root-cause finding above.

### Citations

**File:** modules/pallets/hyper-fungible-token/src/lib.rs (L286-295)
```rust
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

**File:** modules/pallets/hyper-fungible-token/src/lib.rs (L336-355)
```rust
			let local_decimals = if registration.local_id == T::NativeAssetId::get() {
				T::Decimals::get()
			} else {
				<T::Assets as fungibles::metadata::Inspect<T::AccountId>>::decimals(
					registration.local_id.clone(),
				)
			};

			NativeAssets::<T>::insert(registration.local_id.clone(), registration.native);

			let chains: Vec<StateMachine> = registration.chains.keys().cloned().collect();
			for (chain, config) in registration.chains {
				// This pallet bridges substrate <-> EVM only; reject non-EVM peers.
				if !matches!(chain, StateMachine::Evm(_)) {
					return Err(Error::<T>::NonEvmPeerChain.into());
				}
				ensure!(
					config.decimals >= local_decimals,
					Error::<T>::ErcDecimalsBelowLocal
				);
```

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

**File:** modules/pallets/hyper-fungible-token/src/module.rs (L74-90)
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
```

**File:** modules/pallets/hyper-fungible-token/src/module.rs (L239-255)
```rust
				let decimals = if local_asset_id == T::NativeAssetId::get() {
					T::Decimals::get()
				} else {
					<T::Assets as fungibles::metadata::Inspect<T::AccountId>>::decimals(
						local_asset_id.clone(),
					)
				};
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
