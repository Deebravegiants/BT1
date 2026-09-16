### Title
Precision truncation to zero in `convert_to_balance` causes permanent loss of bridged funds - (File: `modules/pallets/hyper-fungible-token/src/impls.rs`)

### Summary
`pallet-hyper-fungible-token`'s `convert_to_balance` performs a floor division when converting an incoming ERC20 amount (18/EVM-decimals precision) down to the local Substrate asset's decimals. Because this division truncates (rounds toward zero) rather than rejecting sub-unit amounts, a cross-chain transfer whose value is smaller than one local-denomination unit is accepted, minted/transferred as `0`, and the event/dispatch reports success — while the equivalent value was already burned/escrowed on the EVM side.

### Finding Description
`convert_to_balance` is: [1](#0-0) 

It divides `value` by `10^(erc_decimals - local_decimals)` with plain integer division, discarding the remainder. This is invoked from the `on_accept` handler in the ISMP module, which is reachable by any relayer delivering a proven cross-chain post request from a registered peer contract: [2](#0-1) 

The amount used here, `message.amount`, was ABI-decoded straight from the untrusted cross-chain `Message` body — the only gate is that the request came from a contract registered in `ContractToAsset`, not that the encoded amount is "large enough" to survive the decimals conversion. If `erc_decimals - local_decimals = d` and the sender specifies (or an attacker crafts, on the EVM side, when initiating a transfer with `send()`/`HyperFungibleToken`) any `message.amount < 10^d`, `convert_to_balance` returns `0`. The code proceeds unconditionally to `NativeCurrency::transfer(...,0,...)`, `Assets::transfer(...,0.into(),...)`, or `Assets::mint_into(...,0.into())` — none of which fail for a zero amount — and then emits `TokenReceived { amount: 0, ... }` and returns `Ok(...)`, i.e. the request is recorded as successfully handled.

Register-side validation only ensures `erc_decimals >= local_decimals` (`ErcDecimalsBelowLocal`), it does not bound how large the decimals gap `d` can be, nor does it prevent registering an asset with 0 local decimals against an 18-decimal ERC20 (a `d = 18` gap, i.e. any EVM amount below 10^18 units, which is the entire realistic value range, would floor to 0 locally). [3](#0-2) 

Symmetrically, the on-timeout refund path uses the same `convert_to_balance` conversion when releasing the escrow back to the original sender: [4](#0-3) 
so even a timeout-triggered refund of a small enough amount also floors to zero, meaning neither the destination mint path nor the failure/refund path can recover the value.

Meanwhile, the corresponding EVM side already debited/escrowed the sender's full amount before dispatch (`send()`/burn or escrow on the EVM `HyperFungibleToken`), and once the ISMP request commits, there's no on-chain re-validation of the resulting local amount before it is treated as "delivered".

### Impact Explanation
This is not merely rounding "slippage" like the referenced constant-product-pool bug — it is complete, permanent, silent loss of the transferred value for any message whose amount is below the local asset's smallest representable unit after decimals conversion. The user's tokens are burned/escrowed on the source chain, the destination chain mints/transfers `0`, and the protocol considers the transfer fully and successfully delivered (`TokenReceived` event fires, no error, no refund path triggers because there was no timeout). For assets registered with a large decimals gap (e.g., a local asset with very few decimals versus an 18-decimal ERC20 peer), essentially any dust-level transfer or any attacker-crafted small `message.amount` results in unbacked burn with zero compensation — a direct fund loss for legitimate users and a griefing vector against unsuspecting senders. This matches the "concrete... permanent freezing/loss of funds" criterion, and is a materially stronger outcome than the referenced AMM report (which only reduces value proportionally, never to outright unrecoverable zero for a nonzero deposit).

### Likelihood Explanation
Reachable from a single, ordinary cross-chain transfer dispatched by any user calling `send()` (or triggered by any relayer delivering the corresponding ISMP `PostRequest`) — no privileged role is required. The likelihood of hitting it depends on the registered decimals gap for a given asset: for assets with 0 or very few local decimals registered against an 18-decimal EVM token, it can be trivially and repeatedly triggered by sending small amounts, or exploited by an attacker instructing a victim/自己-controlled account to send sub-threshold amounts.

### Recommendation
- Reject (revert) rather than silently floor to zero: `convert_to_balance` should return an error (e.g., `AssetTransferError`/a new `AmountTooSmall` variant) whenever the computed local amount is `0` but the input `value` was nonzero, so the request is refused up front instead of being marked delivered with a lost value.
- Alternatively/additionally, enforce a minimum transferable amount at `send()` time (both in the pallet and the EVM `HyperFungibleToken`/`WrappedHyperFungibleToken` contracts) equal to `10^(erc_decimals - local_decimals)`, so dust amounts can never be dispatched in the first place.
- Ensure the same minimum check is applied on the `on_timeout` refund path so a refund cannot also degenerate to zero.

### Proof of Concept
1. Register an asset via `register_token` with `local_decimals = 0` (or any small value) and `erc_decimals = 18` for an EVM peer chain — this passes the `ErcDecimalsBelowLocal` check since `18 >= 0`. [5](#0-4) 
2. On the EVM `HyperFungibleToken` deployment, call `send()` with `amount = 1` (1 wei, an 18-decimal-denominated dust amount) to the pallet-registered recipient; the contract burns/escrows this amount and dispatches the ISMP post request containing `message.amount = 1`.
3. The relayer delivers the request; the pallet's `on_accept` computes `convert_to_balance(1, 18, 0) = 1 / 10^18 = 0`. [6](#0-5) 
4. `NativeCurrency::transfer`/`mint_into` is called with `amount = 0`, which succeeds; `TokenReceived { amount: 0 }` is emitted, and the request is marked delivered with no error and no path to refund the original sender — the burned/escrowed value on the EVM side is permanently unrecoverable.

### Citations

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

**File:** modules/pallets/hyper-fungible-token/src/module.rs (L238-284)
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
```

**File:** modules/pallets/hyper-fungible-token/src/lib.rs (L327-368)
```rust
		/// Registers a new token with per-chain contract configuration
		#[pallet::call_index(1)]
		#[pallet::weight(T::WeightInfo::register_token(registration.chains.len() as u32))]
		pub fn register_token(
			origin: OriginFor<T>,
			registration: TokenRegistration<AssetId<T>>,
		) -> DispatchResult {
			T::CreateOrigin::ensure_origin(origin)?;

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
				let token_contract = config.token_contract.0.to_vec();
				TokenContracts::<T>::insert(
					chain,
					registration.local_id.clone(),
					token_contract.clone(),
				);
				ContractToAsset::<T>::insert(
					chain,
					token_contract,
					registration.local_id.clone(),
				);
				Precisions::<T>::insert(registration.local_id.clone(), chain, config.decimals);
			}
```
