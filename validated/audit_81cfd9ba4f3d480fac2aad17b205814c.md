## Analysis

The reported bug class is precision/decimal-scaling assumptions breaking down when a bridged asset's decimal count differs from the "typical" case. The closest reachable analog in this codebase is in `modules/pallets/hyper-fungible-token`, whose `send`/`on_accept`/`on_timeout` paths convert amounts between a local substrate asset's decimals and the paired EVM contract's decimals using `convert_to_erc20`/`convert_to_balance`. Both helpers assume `erc_decimals >= local_decimals` and only scale in one direction via `saturating_sub`, silently doing **no scaling at all** when that assumption is false. [1](#0-0) 

### Title
Broken bidirectional decimal conversion in `pallet-hyper-fungible-token` causes unbacked minting/fund loss when EVM decimals < local decimals - (File: modules/pallets/hyper-fungible-token/src/impls.rs)

### Summary
`convert_to_balance` and `convert_to_erc20` in `modules/pallets/hyper-fungible-token/src/impls.rs` both compute the scaling exponent as `erc_decimals.saturating_sub(local_decimals)`, i.e. they only ever scale *up* on the EVM side and *down* on the local side. This implicitly assumes the EVM-side decimals are always greater than or equal to the local (substrate) asset's decimals — the same class of unchecked precision assumption flagged in the external report (fixed conversion factor that ignores real per-token decimal relationships).

### Finding Description
- `convert_to_erc20(value, erc_decimals, local_decimals)` is used in `send()` to scale a local balance up to the ERC20 amount dispatched to the paired EVM contract: it multiplies by `10^(erc_decimals.saturating_sub(local_decimals))`. [2](#0-1) [3](#0-2) 
- `convert_to_balance(value, erc_decimals, local_decimals)` is used in `on_accept()`/`on_timeout()` to scale an incoming ERC20 amount down to the local balance: it divides by `10^(erc_decimals.saturating_sub(local_decimals))`. [4](#0-3) [5](#0-4) 

`Precisions` is a per-`(AssetId, StateMachine)` admin-configured value with no documented or enforced constraint that it be `>= local_decimals` — the README only says "Decimals between this chain and each remote chain may differ; per-pair `Precisions` storage records the EVM-side decimals so amounts get scaled at the boundary," implying arbitrary decimal relationships are expected, exactly like the DOT (10 vs 18 decimals) example documented for the sibling token-gateway pallet. [6](#0-5) 

When a local asset is registered with **more** decimals than its paired EVM contract (`local_decimals > erc_decimals`, e.g. a local asset minted with 18 decimals paired against a 6-decimal EVM token, mirroring the AURA-vs-18-decimal-token scenario in the original report):
- `send()`: `saturating_sub` returns 0, so `convert_to_erc20` performs **no down-scaling**. A user escrowing/burning `X` local (18-decimal) units causes an ERC20 `Message.amount` numerically equal to `X`, which the EVM contract mints as if it were 18-decimal — over-minting by `10^(local_decimals - erc_decimals)` relative to what was actually escrowed/burned.
- `on_accept()`/`on_timeout()`: symmetric failure — an incoming EVM amount in `erc_decimals` precision is credited directly as the local balance without multiplying up by `10^(local_decimals - erc_decimals)`, drastically under-crediting the beneficiary (effectively burning most of the transferred value).

### Impact Explanation
This is not mere rounding dust — it's a full silent failure of the scaling logic in one direction, which can either (a) mint unbacked tokens on the EVM side for a fraction of the true cost (theft/insolvency of the bridge's backing), or (b) permanently strand/lose most of a user's value on receipt. Either outcome is a concrete Medium/High-severity fund-safety issue in the token bridge's mint/burn accounting.

### Likelihood Explanation
Triggering requires only a legitimate token registration where the EVM-side decimals are lower than the local asset's decimals (`register_token`/`Precisions` update) — a configuration the pallet's own documentation implies is supported ("decimals... may differ"), not an attacker compromising governance. Once such an asset exists, every ordinary `send`/`on_accept`/`on_timeout` transaction on that asset silently mis-scales.

### Recommendation
Replace the one-directional `saturating_sub` scaling in `convert_to_balance`/`convert_to_erc20` with logic that scales in the correct direction regardless of which side has more decimals (multiply when the target has more decimals, divide when it has fewer), and add an explicit invariant check/test covering `local_decimals > erc_decimals`.

### Proof of Concept
1. Register a local asset (e.g. via `pallet-assets`) with `decimals = 18`.
2. Call `register_token` with `Precisions` for a destination EVM chain set to `erc_decimals = 6` (a legitimately different-decimals token, per the pallet's documented support for differing decimals).
3. Call `send()` with `amount = 1_000_000_000_000_000_000` (1 whole token, 18 decimals): `convert_to_erc20` computes `10^(6.saturating_sub(18)) = 10^0 = 1`, so `erc20_amount = 1_000_000_000_000_000_000` is dispatched — the EVM contract mints `1e18` raw units, i.e. `1e12` whole tokens at 6-decimal precision instead of 1, a 10^12x over-mint.
4. Conversely, delivering `amount = 1_000_000` (1 whole EVM token at 6 decimals) back via `on_accept` yields `convert_to_balance` dividing by `10^0 = 1`, crediting the beneficiary only `1_000_000` raw local units (`0.000000000001` of a token at 18-decimal precision) instead of `1_000_000_000_000_000_000`. [7](#0-6) [8](#0-7)

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

**File:** modules/pallets/hyper-fungible-token/src/lib.rs (L251-310)
```rust
			let token_contract =
				TokenContracts::<T>::get(params.destination, params.asset_id.clone())
					.ok_or(Error::<T>::TokenContractNotFound)?;
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

**File:** modules/pallets/hyper-fungible-token/src/module.rs (L205-211)
```rust
		Self::deposit_event(Event::<T>::TokenReceived {
			beneficiary,
			amount: amount.into(),
			source,
		});

		Ok(T::DbWeight::get().reads_writes(5, 2))
```

**File:** modules/pallets/hyper-fungible-token/README.md (L27-33)
```markdown
The chain's own native currency (`T::NativeAssetId`) is always treated as
native, with `T::NativeCurrency` providing custody.

Decimals between this chain and each remote chain may differ; per-pair
`Precisions` storage records the EVM-side decimals so amounts get scaled at
the boundary.

```
