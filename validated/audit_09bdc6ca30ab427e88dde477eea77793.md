### Title
Asymmetric decimals scaling in `hyper-fungible-token`'s `convert_to_erc20`/`convert_to_balance` causes unbacked over-minting or fund loss when the ERC20 destination has fewer decimals than the local asset - ([File: modules/pallets/hyper-fungible-token/src/impls.rs])

### Summary
The reported bug is a precision-unit mismatch: `SingleSidedLiquidityVault` mixes an 18-decimal reward value with a 36-decimal debt accumulator, letting repeat claims extract more than owed. The Hyperbridge analog is in `modules/pallets/hyper-fungible-token/src/impls.rs`, where the helper functions that convert amounts between local-asset decimals and remote-ERC20 decimals only handle one direction of the decimals relationship (`erc_decimals >= local_decimals`), silently no-op the scaling in the opposite case via `saturating_sub`, and are used directly to size a cross-chain mint/burn — the same class of "assumed precision direction, produces a materially wrong scaled amount" defect.

### Finding Description
`convert_to_erc20` and `convert_to_balance` compute a decimals delta with `erc_decimals.saturating_sub(local_decimals)`: [1](#0-0) 

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

Both functions only apply a scaling factor when `erc_decimals > local_decimals`. When `erc_decimals < local_decimals` (a plausible, governance-configurable combination since `Precisions` is set per `(asset_id, destination)` pair with no invariant enforcing `erc_decimals >= local_decimals`), `saturating_sub` returns `0`, so `10^0 = 1` and the conversion becomes a no-op — the raw value is used unscaled instead of being divided down.

`convert_to_erc20` is called from the unprivileged, user-reachable `send()` extrinsic to encode the amount that will be minted/unlocked on the destination EVM chain: [2](#0-1) 

`convert_to_balance` is called symmetrically in `on_accept` (inbound mint/transfer) and `on_timeout` (refund) in `module.rs`: [3](#0-2) [4](#0-3) 

Concretely: if the local asset has 18 decimals and the registered destination ERC20 has 6 decimals (`erc_decimals=6 < local_decimals=18`), a user calling `send()` with `amount = 1_000_000000000000000` (1 unit, burned/escrowed locally) computes `erc20_amount = value * 10^(6-18 saturating to 0) = value` — i.e. the full 1e18-scaled raw integer is placed unscaled into the outbound `Message.amount` field, instead of being divided by `10^12` to the correct 6-decimal ERC20 representation. The destination contract then mints/releases an amount ~10^12 times larger than what was actually escrowed on the source chain.

### Impact Explanation
This is an unbacked-mint / fund-drain vector reachable by any unprivileged user simply calling `send()` on the `hyper-fungible-token` pallet for any asset pair configured with `erc_decimals < local_decimals`. It lets an attacker escrow a tiny amount locally and receive (mint) an enormously inflated amount on the destination chain — directly matching the "theft of funds via broken precision accounting" impact class of the original report, but manifesting as unbacked minting rather than double-claiming a reward debt. The reverse direction (`erc_decimals > local_decimals` is the only case actually handled) is fine; only the asymmetric case is broken, and in the opposite decimals configuration the bug instead truncates value to functionally zero on `convert_to_balance`'s inverse call path, causing permanent loss of user funds on refund/receipt.

### Likelihood Explanation
Likelihood depends entirely on whether any live asset/destination pair is configured with `erc_decimals < local_decimals`. Given that Polkadot-SDK assets commonly use 10-18 decimals while many canonical EVM stablecoins (USDC/USDT) use 6 decimals, this configuration is realistic and not inherently invalid — nothing in `_processTokenDecimalsUpdates`/`Precisions` setup enforces `erc_decimals >= local_decimals`, so it is a plausible governance/config state rather than a contrived edge case.

### Recommendation
Fix `convert_to_erc20` and `convert_to_balance` to handle both directions symmetrically (multiply when target decimals > source decimals, divide when target decimals < source decimals), mirroring the correct pattern already used elsewhere in the codebase (e.g. `VWAPOracle._normalizeAmount` in `evm/src/utils/VWAPOracle.sol`, lines 240-248, which correctly branches on `_decimals < 18` vs `>= 18`). Add an explicit round-trip invariant test (`convert_to_balance(convert_to_erc20(x)) == x` for `erc_decimals < local_decimals` cases) to `hyper-fungible-token`'s test suite.

### Proof of Concept
1. Governance/admin configures `Precisions[asset_id][EVM-dest] = 6` for a local asset with `local_decimals = 18` (e.g., via `set_precision`/`_processTokenDecimalsUpdates`-equivalent extrinsic).
2. Attacker calls `send()` with `amount = 1e18` (1 whole unit), which is burned/escrowed from the attacker's local balance.
3. `convert_to_erc20(1e18, erc_decimals=6, local_decimals=18)` computes `10u128.pow(6u8.saturating_sub(18) as u32) = 10u128.pow(0) = 1`, so `erc20_amount = 1e18` is encoded in the dispatched `Message.amount` — instead of the correct `1e18 / 10^12 = 1_000_000` (1 unit in 6-decimal terms).
4. On delivery, the destination `HyperFungibleToken`/`WrappedHyperFungibleToken` ERC20 contract mints/releases `1e18` raw units to the recipient — a 10^12x overpayment relative to what was escrowed, funded from the pallet's/contract's other locked liquidity, i.e. unbacked mint / theft of funds.

### Citations

**File:** modules/pallets/hyper-fungible-token/src/impls.rs (L39-58)
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
```

**File:** modules/pallets/hyper-fungible-token/src/lib.rs (L292-315)
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

			let metadata = FeeMetadata { payer: who.clone(), fee: params.relayer_fee.into() };
			let commitment = dispatcher
				.dispatch_request(DispatchRequest::Post(dispatch_post), metadata)
				.map_err(|_| Error::<T>::DispatchError)?;
```

**File:** modules/pallets/hyper-fungible-token/src/module.rs (L82-117)
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

**File:** modules/pallets/hyper-fungible-token/src/module.rs (L239-285)
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
```
