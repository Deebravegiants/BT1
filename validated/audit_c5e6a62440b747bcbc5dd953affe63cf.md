### Title
Stale decimal-precision invariant in `hyper-fungible-token` allows incorrect mint amounts on message delivery - ([File: modules/pallets/hyper-fungible-token/src/module.rs])

### Summary
The `hyper-fungible-token` pallet bridges ERC20 tokens between EVM chains and Substrate assets. It enforces `erc_decimals >= local_decimals` only at `register_token`/`update_token` time, then re-derives `local_decimals` *live* from the asset's metadata every time a cross-chain message is delivered via `on_accept`/`on_timeout`. If the local asset's decimals value changes after registration (a legitimate metadata update, not necessarily malicious), the previously-enforced invariant silently breaks, and `convert_to_balance`'s `saturating_sub` collapses the scaling exponent to zero — the incoming ERC20 amount is credited to the beneficiary with none of the required decimal scaling, drastically inflating the minted/transferred amount. This mirrors the Term Labs root cause: an internal inconsistency in decimal precision introduced during a routine configuration update leads to grossly mispriced/miscaled asset amounts.

### Finding Description
`register_token` and `update_token` validate the precision relationship once, at write time: [1](#0-0) 

But `on_accept` (triggered by any relayer delivering an incoming ISMP post request — an unprivileged, externally-reachable path) and `on_timeout` recompute `decimals` live from `fungibles::metadata::Inspect` on every message, while `erc_decimals` is the value cached in `Precisions` storage at registration time: [2](#0-1) 

The conversion itself relies on `erc_decimals.saturating_sub(local_decimals)`: [3](#0-2) 

If, after registration, the local asset's `decimals()` value increases (e.g. `pallet-assets::set_metadata` is called again for a legitimate reason such as correcting an earlier misconfiguration, similar to Term Labs' "update to the oracle") such that `local_decimals > erc_decimals`, `saturating_sub` returns `0`. The division `value / 10^0` becomes a no-op, so the raw ERC20 `U256` amount (typically scaled to 18 decimals) is minted/transferred directly as the local balance with zero scale-down. Since local balances are typically far lower-precision (e.g. 6 or 10 decimals), this converts what should be a modest amount into an amount inflated by up to `10^(local_decimals)` — an internal decimal-precision inconsistency exactly analogous to the Term Labs tETH oracle incident, except here it directly and permanently mints/unlocks excess funds rather than triggering liquidations.

### Impact Explanation
Any relayer submitting a legitimately-proven ISMP message (`on_accept`) after the precision invariant has drifted would trigger a massively over-scaled `mint_into`/`transfer` to the beneficiary from the pallet's custody account or via unbacked minting for non-native assets, directly draining custody funds or creating unbacked supply. This satisfies the "unbacked mint" / "concrete theft" impact bar.

### Likelihood Explanation
The precondition (decimals changing after registration) is not attacker-controlled through malicious governance abuse in this analog — it requires only a legitimate metadata correction/update to the underlying asset, which is exactly the "human error during a sensitive system upgrade" failure mode described in the Term Labs report. Once that drift occurs, exploitation only requires a single unprivileged relayer to deliver any valid cross-chain message for that asset — no special privilege needed for the triggering transaction.

### Recommendation
Re-validate `erc_decimals >= local_decimals` (or recompute the scale factor safely, erroring instead of saturating) inside `on_accept`/`on_timeout` at message-processing time, not only at registration/update time, and consider caching `local_decimals` in `Precisions` alongside `erc_decimals` so both values are locked together and cannot drift independently.

### Proof of Concept
1. `register_token` for asset `X` with `local_decimals = 6` and `config.decimals (erc_decimals) = 6` (passes the `>=` check).
2. Asset issuer legitimately updates `pallet-assets` metadata for `X`, raising its `decimals()` to `12` (no re-validation occurs, since `update_token`/`register_token` are not re-invoked).
3. A relayer delivers a valid, correctly-proven ISMP `PostRequest` carrying an ERC20 amount for `X`. `module.rs::on_accept` computes `decimals = 12` (live) and `erc_decimals = 6` (stale, from `Precisions`).
4. `convert_to_balance` computes `erc_decimals.saturating_sub(local_decimals) = 6u8.saturating_sub(12u8) = 0`, so the raw ERC20 `U256` amount (in 6-decimal ERC20 units per registration) is minted as-is with no scale-down, crediting the beneficiary `10^6` times more than intended relative to the 6-decimal configuration originally validated. [3](#0-2) [4](#0-3)

### Citations

**File:** modules/pallets/hyper-fungible-token/src/lib.rs (L352-355)
```rust
				ensure!(
					config.decimals >= local_decimals,
					Error::<T>::ErcDecimalsBelowLocal
				);
```

**File:** modules/pallets/hyper-fungible-token/src/module.rs (L75-116)
```rust
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

		// Mint or transfer to beneficiary
		if local_asset_id == T::NativeAssetId::get() {
			<T as Config>::NativeCurrency::transfer(
				&Pallet::<T>::pallet_account(),
				&beneficiary,
				amount,
				ExistenceRequirement::AllowDeath,
			)
			.map_err(|e| HftError::TransferFailed(e.into()))?;
		} else {
			let is_native = NativeAssets::<T>::get(local_asset_id.clone());
			if is_native {
				<T as Config>::Assets::transfer(
					local_asset_id,
					&Pallet::<T>::pallet_account(),
					&beneficiary,
					amount.into(),
					Preservation::Expendable,
				)
				.map_err(|e| HftError::TransferFailed(e.into()))?;
			} else {
				<T as Config>::Assets::mint_into(local_asset_id, &beneficiary, amount.into())
					.map_err(|e| HftError::MintFailed(e.into()))?;
			}
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
