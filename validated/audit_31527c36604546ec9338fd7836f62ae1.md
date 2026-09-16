### Title
Truncated cross-chain amount conversion in `hyper-fungible-token` silently mints zero tokens for dust-sized transfers, permanently losing user funds - (File: `modules/pallets/hyper-fungible-token/src/impls.rs`)

### Summary
`convert_to_balance` in the `hyper-fungible-token` pallet performs integer division to rescale an ERC20-denominated `U256` amount down to the local asset's decimal precision. When the local asset has fewer decimals than the remote ERC20 token (e.g. an 18-decimal EVM asset bridged to a 6-decimal Substrate asset), any amount smaller than the scaling factor (`10^(erc_decimals - local_decimals)`) truncates to zero, exactly the same class of precision loss described in the referenced report (`USSD.sol` collateral-factor truncation for tokens with `< 1e6` inputs on 18-decimal assets).

### Finding Description
`convert_to_balance` divides the incoming `U256` value by `10^(erc_decimals.saturating_sub(local_decimals))` with no rounding or minimum-amount check: [1](#0-0) 

This function is invoked directly in the `on_accept` handler of the ISMP module, which processes an inbound `PostRequest` delivered by any relayer proving a message from a registered remote contract. The resulting `amount` is used unconditionally to mint/transfer funds to the beneficiary: [2](#0-1) 

The same conversion and lack of a floor/zero-check is repeated on the `on_timeout` refund path: [3](#0-2) 

Neither `convert_to_balance` nor its callers reject a result of `0`. If the remote `message.amount` (already deducted/escrowed/burned on the source chain by the corresponding `send` extrinsic there, in the *source* chain's own decimals) is smaller than the divisor implied by the decimals gap, the beneficiary is credited/minted `0` tokens while the source-side value was already consumed. Since `Currency::transfer` and `Assets::mint_into` both succeed trivially with amount `0`, the message is accepted, the commitment is recorded as delivered, and there is no retry or recovery path — the value is permanently lost.

### Impact Explanation
This causes a genuine, permanent loss of user funds whenever an asset pair straddles a large decimals gap (e.g., 18-decimal EVM token → 6-decimal Substrate asset representation, a very common configuration per `docs/content/developers/polkadot/token-gateway.mdx`'s guidance that "ERC6160 assets on EVM chains should always use `18`" while Substrate assets are frequently 6-12 decimals). Any transfer below the scaling threshold silently evaporates: the sender's tokens are debited on the source chain, but the beneficiary receives nothing, and the message is marked successfully delivered so no timeout/refund logic ever fires. This is a direct instance of "permanent freezing/loss of funds" from unbacked accounting truncation, matching the report's bug class.

### Likelihood Explanation
Any unprivileged user calling `send` on the pallet's `send` extrinsic, or the corresponding EVM `HyperFungibleToken`/`WrappedHyperFungibleToken` contract, can trigger this simply by sending a small amount when the registered precision gap is large — no attacker privilege or malicious relayer collusion is required, only normal operation of the token-bridge as configured via `Precisions::<T>`. Given that precision registration explicitly supports arbitrary per-chain decimal configurations, this is readily reachable in production usage, not a contrived edge case.

### Recommendation
- Reject conversions that truncate to zero: after computing `amount`, if the source `value` was non-zero but the scaled result is `0`, return an error (e.g., extend `InvalidAmountConversion`) instead of silently minting nothing.
- Alternatively, round up (ceiling) when scaling down so dust is preserved rather than lost, or enforce a minimum transferable amount at the `send` call site (source chain) proportional to the destination's precision so sub-threshold sends are rejected before funds are locked/burned.
- Apply the same fix consistently to both the `on_accept` minting path and the `on_timeout` refund path.

### Proof of Concept
1. Register an asset with `Precisions::<T>` mapping to `erc_decimals = 18` for a remote EVM chain, while the local Substrate asset uses `local_decimals = 6` (a supported, documented configuration).
2. A user sends `500_000` (5×10^5) wei worth of the asset from the EVM side, i.e., `message.amount = 500_000` in the `Message.amount` field of the ISMP `PostRequest` body.
3. On `on_accept`, `convert_to_balance(U256::from(500_000), 18, 6)` computes `500_000 / 10^12 = 0`.
4. `amount = 0` is minted/transferred to the beneficiary; the call succeeds, `TokenReceived` event fires with `amount: 0`, and the message is marked as delivered.
5. The equivalent value was already locked/burned on the source chain's `send` extrinsic; the beneficiary never receives it — permanent loss. [1](#0-0) [4](#0-3)

### Citations

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

**File:** modules/pallets/hyper-fungible-token/src/module.rs (L74-117)
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
		}
```

**File:** modules/pallets/hyper-fungible-token/src/module.rs (L239-292)
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

				// Refund: release escrowed tokens back to the original sender
				if local_asset_id == T::NativeAssetId::get() {
					<T as Config>::NativeCurrency::transfer(
						&Pallet::<T>::pallet_account(),
						&beneficiary,
						amount.into(),
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
						<T as Config>::Assets::mint_into(
							local_asset_id,
							&beneficiary,
							amount.into(),
						)
						.map_err(|e| HftError::MintFailed(e.into()))?;
					}
				}

				Pallet::<T>::deposit_event(Event::<T>::TokenRefunded {
					beneficiary,
					amount: amount.into(),
					dest,
				});
				Ok(T::DbWeight::get().reads_writes(5, 2))
```
