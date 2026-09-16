### Title
Silent decimal-precision truncation and mutable-metadata desync in HFT cross-chain amount conversion - (File: modules/pallets/hyper-fungible-token/src/impls.rs)

### Summary
The `pallet-hyper-fungible-token` cross-chain amount conversion functions `convert_to_erc20`/`convert_to_balance` implement the exact "overcomplicated unit conversion" bug class called out in the report: precision scaling is done with `10^(erc_decimals.saturating_sub(local_decimals))` and depends on an invariant (`erc_decimals >= local_decimals`) that is validated only once at `register_token`/`update_token` time, but the `local_decimals` value used at the actual `send()`/`on_accept()` conversion time is re-queried live from `fungibles::metadata::Inspect::decimals()` rather than being pinned at registration. [1](#0-0) 

### Finding Description
`convert_to_erc20` and `convert_to_balance` scale amounts between the local asset's decimals and the EVM-side (`erc_decimals`) representation: [2](#0-1) 

The safety of `saturating_sub(erc_decimals, local_decimals)` depends entirely on `erc_decimals >= local_decimals` holding at the time of every `send()` and `on_accept()`/`on_timeout()` call. That invariant is checked only at `register_token`/`update_token`, using a `local_decimals` snapshot taken from `fungibles::metadata::Inspect::decimals()` at registration time: [3](#0-2) 

But `send()` and the `on_accept`/`on_timeout` handlers in `module.rs` re-fetch `decimals` live from the same `fungibles::metadata::Inspect` call rather than reusing the value validated at registration: [4](#0-3) [5](#0-4) 

If the underlying local asset's metadata decimals can be changed after registration (e.g. the asset was created/administered outside of HFT's `CreateOrigin` — many `pallet-assets` deployments allow the asset's own owner/admin to call `set_metadata`), the registration-time invariant `erc_decimals >= local_decimals` can be silently violated at runtime. When that happens, `saturating_sub` clamps to `0`, `10^0 = 1`, and the conversion functions **stop scaling entirely** while still being treated as correctly scaled — every subsequent `send()` will burn/escrow the correct local amount but emit an ERC20-side amount that is off by the entire missing power-of-ten factor, and every subsequent `on_accept()`/`on_timeout()` will mint/release the wrong (scaled) amount for a given incoming ERC20 value. There is no re-validation of the invariant on the hot path, and no error is raised — the conversion silently produces an incorrect (much smaller or much larger) amount instead of failing loudly like `BandwidthManager.purchase()` does with its `PriceNotRepresentable()` guard for an analogous scaling mismatch.

Separately, even under the intended (validated) precondition, `convert_to_balance` performs floor/truncating integer division with no minimum/dust handling: an incoming ERC20 amount that is not an exact multiple of the scale factor has its remainder silently discarded on every `on_accept`/`on_timeout` call, with no error, no event, and no accounting of the lost dust — unlike `BandwidthManager.purchase()`'s explicit `% scale != 0 → revert` pattern for the same class of division.

### Impact Explanation
- If the decimals invariant is violated (asset decimals changed post-registration, or a future runtime wires an `Assets` type whose decimals are not immutable/CreateOrigin-controlled), the `saturating_sub` clamp converts an unbounded/large scaling error into a silent no-op scale, causing gross over- or under-minting/releasing of tokens on the receiving chain relative to what was escrowed/burned on the sending chain. This is a direct fund-safety issue for any unprivileged user who calls the permissionless `send()` extrinsic or whose incoming message is processed by `on_accept`.
- Even without any decimals drift, the unguarded truncation in `convert_to_balance` silently destroys value on every incoming message whose raw amount isn't a clean multiple of the scale factor, with no path to reclaim the truncated remainder — a systemic (if individually small) value leak reachable by any relayer delivering a legitimate message.

### Likelihood Explanation
The truncation issue triggers on essentially every incoming message with a non-round amount, so it is a near-certain, though small-magnitude, occurrence. The decimals-invariant violation requires the local asset's `decimals()` metadata to change after HFT registration, which depends on runtime configuration of `Config::Assets`; whether this is achievable by a non-privileged actor is runtime-specific and could not be fully confirmed from the code alone — this is worth flagging explicitly as unverified in this analysis.

### Recommendation
- Pin the `local_decimals` used for scaling in `send()`/`on_accept()`/`on_timeout()` to the value validated at `register_token`/`update_token` time (store it in `Precisions` or a new storage item) instead of re-querying live `fungibles::metadata::Inspect::decimals()`, so the registration-time invariant cannot silently drift.
- Replace the `saturating_sub` clamp with an explicit `checked_sub`/`ensure!` that hard-fails the extrinsic/message if `erc_decimals < local_decimals` is ever observed at runtime, rather than degrading to a no-op scale factor.
- Add an explicit divisibility guard in `convert_to_balance` (mirroring `BandwidthManager.purchase()`'s `% scale != 0 → revert PriceNotRepresentable()`) so that non-representable incoming amounts are rejected rather than silently truncated, or explicitly document/emit the truncated remainder if some dust loss is intentionally accepted.

### Proof of Concept
1. Governance registers asset `X` on this chain with `local_decimals = 6` and EVM chain config `decimals (erc_decimals) = 18` — passes the `ensure!(config.decimals >= local_decimals)` check in `register_token`.
2. (Precondition, not fully verified against this runtime's `Assets` config) The owner/admin of asset `X` in `pallet-assets` later changes its metadata to `decimals = 20` via `set_metadata`/`force_set_metadata`, which is outside `CreateOrigin`'s (HFT governance) control.
3. A user calls `send()` for asset `X`. `decimals` is re-fetched as `20`; `erc_decimals` (still `18` from `Precisions`) is used with `convert_to_erc20(amount, 18, 20)` → `saturating_sub(18,20) = 0` → `scale = 1` → `erc20_amount = amount` (unscaled).
4. The EVM-side `HyperFungibleToken` contract, which treats the incoming amount as 18-decimal, mints `amount` raw units instead of `amount * 10^2`, so the recipient receives 100x fewer tokens than the sender escrowed/burned — permanent value loss for that user, reachable purely through the permissionless `send()` call once the (unverified) precondition holds.

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
