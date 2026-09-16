Based on my research, I found a direct analog of the Ajna "division-before-multiplication rounds to zero" bug class in the `hyper-fungible-token` pallet's cross-chain amount conversion. Even though the pallet's registration path validates `erc_decimals >= local_decimals` (see the `ErcDecimalsBelowLocal` error), that guard *guarantees* the normal, supported configuration is exactly the one where the truncating division is dangerous: any legitimate token pair where the EVM side has more decimal precision than the local Substrate asset. Below that path is exercised on every inbound message and on every timeout refund, so an ordinary token bridger — not a privileged actor — can trigger permanent loss of dust amounts, and the same math being reused for refunds means the loss is not even recoverable via timeout.

### Title
Truncating decimal conversion in `hyper-fungible-token` lets small transfers round to zero, burning source funds with no credit or refund - (File: modules/pallets/hyper-fungible-token/src/impls.rs)

### Summary
`convert_to_balance` scales an incoming ERC20 amount down to the local asset's decimals with a single integer division by `10^(erc_decimals - local_decimals)`. Any inbound amount smaller than that scale factor truncates to `0`, and the same function is used both to credit the beneficiary on receipt and to refund the original sender on timeout, so a dust-sized transfer results in tokens being burned/escrowed on the EVM side with the corresponding Substrate-side credit — and even the timeout refund — computed as zero.

### Finding Description
The pallet enforces `erc_decimals >= local_decimals` at registration (`Error::ErcDecimalsBelowLocal`), which means the supported, intended configuration always has a non-trivial scale factor `10^(erc_decimals - local_decimals)`. [1](#0-0) 

The scaling itself is a single truncating division with no minimum-amount check: [2](#0-1) 

This function is called on `on_accept` to compute the amount to mint/transfer to the beneficiary from the raw ERC20 `message.amount`: [3](#0-2) 

and reused on `on_timeout` to compute the refund back to the original sender, using the same conversion and the same erc/local decimals for the destination chain: [4](#0-3) 

The originating EVM `send()` extrinsic burns/escrows the sender's local asset and dispatches the message before any of this Substrate-side scaling happens, so by the time the truncation occurs, the source-side debit is already final: [5](#0-4) 

Because both the successful-delivery path and the timeout-refund path use the exact same truncating division on the exact same decimals pair, there is no path in the protocol that can ever restore the dust amount to the user once it falls below the scale factor.

### Impact Explanation
Any inbound `Send` message whose ERC20 amount is smaller than `10^(erc_decimals - local_decimals)` results in `amount == 0` being minted/transferred to the beneficiary, while the equivalent value was already burned or escrowed on the source EVM chain. If the message times out instead, the refund computation uses the identical conversion and also yields zero, so the funds are not returned to the sender either. The result is a permanent, non-recoverable loss of user funds for any token pair configured with a large decimals gap (e.g., a local asset with 0 or low decimals paired against an 18-decimal EVM token, where the scale factor is `10^18` and effectively any transfer below one whole token rounds to zero). This is a direct freezing/loss-of-funds condition matching the required impact bar.

### Likelihood Explanation
This requires no privileged action and no malicious governance: it is triggered purely by an ordinary user calling `send()` on the paired EVM `HyperFungibleToken`/`WrappedHyperFungibleToken` contract with an amount smaller than the configured scale, or by network conditions causing a legitimate small-value message to time out. Because the decimals-gap configuration (`erc_decimals >= local_decimals`) is the pallet's *intended and validated* operating mode, this is not an edge case outside the supported parameter space — it is the normal path for any asset pair with differing decimal precision, making the likelihood of dust-amount loss realistic for any deployment that registers such a pair.

### Recommendation
Reject (rather than silently truncate) any inbound amount that is not an exact multiple of the scale factor, or round up/require a minimum transferable amount enforced on the EVM sender side (mirroring the `_roundToScale`-style fix suggested in the original report: validate divisibility before dividing, and revert if the amount would truncate to zero, both in `convert_to_balance`'s callers in `on_accept` and `on_timeout`).

### Proof of Concept
1. Register an asset with `local_decimals = 0` (or any low value) and `erc_decimals = 18` for a given EVM `StateMachine`, which is a valid registration since `erc_decimals >= local_decimals`.
2. A user calls `send()` on the peer `HyperFungibleToken` EVM contract with `amount = 1` (1 wei, far below `10^18`). The contract burns/locks this amount and dispatches a `Send` ISMP Post request. [6](#0-5) 
3. A relayer delivers the request; `on_accept` computes `convert_to_balance(1, 18, 0)` = `1 / 10^18` = `0`, so the beneficiary is credited `0` tokens. [7](#0-6) 
4. If instead the request times out, `on_timeout` performs the identical conversion and also computes a `0` refund, so the sender's originally burned/escrowed 1 wei is permanently unrecoverable on either path. [8](#0-7)

### Citations

**File:** modules/pallets/hyper-fungible-token/src/lib.rs (L219-224)
```rust
		/// Peer chain is not an EVM state machine; this pallet bridges substrate <-> EVM only
		NonEvmPeerChain,
		/// Configured ERC decimals are less than the local asset's decimals; precision conversion
		/// requires erc_decimals >= local_decimals
		ErcDecimalsBelowLocal,
	}
```

**File:** modules/pallets/hyper-fungible-token/src/lib.rs (L257-290)
```rust
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

**File:** modules/pallets/hyper-fungible-token/src/impls.rs (L39-52)
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

**File:** modules/pallets/hyper-fungible-token/src/module.rs (L239-265)
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
```
