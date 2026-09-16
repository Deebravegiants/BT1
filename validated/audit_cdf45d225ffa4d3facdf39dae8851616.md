### Title
Truncated Decimal Down-Conversion in `convert_to_balance` Permanently Burns Dust on Every Incoming Cross-Chain Token Message - (File: `modules/pallets/hyper-fungible-token/src/impls.rs`)

### Summary
The `hyper-fungible-token` pallet's `on_accept` (mint/credit) and `on_timeout` (refund) handlers convert an incoming ERC20-denominated `U256` amount to the local Substrate balance via `convert_to_balance`, which performs integer division with no remainder handling. Any amount whose ERC20-decimal value is not an exact multiple of `10^(erc_decimals - local_decimals)` has its fractional remainder silently discarded — the value is neither credited to the beneficiary nor tracked anywhere, so it is permanently lost.

### Finding Description
`convert_to_balance` truncates on scale-down: [1](#0-0) 

It is invoked in the ISMP module's `on_accept` handler, which mints/transfers tokens to a beneficiary based on an incoming cross-chain `PostRequest` from any registered EVM `HyperFungibleToken`/`WrappedHyperFungibleToken` contract, and again in `on_timeout` for refunds: [2](#0-1) [3](#0-2) 

`erc_decimals` is required to be `>= local_decimals` at registration time: [4](#0-3) 

so the scale-down branch (`erc_decimals > local_decimals`) is always the one exercised on the receiving/mint path, and the divisor `10^(erc_decimals - local_decimals)` is always ≥ 1. Any `message.amount` whose low-order digits (below that divisor) are non-zero is truncated with no remainder capture, no event, and no way to reclaim the dust — it is simply not minted to anyone.

By contrast, the sending path uses `convert_to_erc20`, which only multiplies (scales up, never loses precision): [5](#0-4) 

The asymmetry is structural: outbound conversions (local → EVM) are exact, but every inbound conversion (EVM → local, in both the happy-path mint and the timeout refund) truncates. A single ISMP `PostRequest`/timeout delivered by any relayer is sufficient to trigger the loss — no privileged actor is required, matching the unprivileged-message-dispatcher reachability requirement.

### Impact Explanation
Each cross-chain message that arrives with a non-multiple-of-`10^(erc_decimals-local_decimals)` amount permanently destroys the truncated remainder. This is a genuine, reachable value-freezing (in the "unbacked burn"/permanent loss sense) bug: dust originally escrowed or minted on the EVM side (see the `1:1` `convert_to_erc20` scale-up on send) is not fully returned/credited on delivery to the destination chain. Over the life of the bridge across many messages, this can accumulate into a material and unrecoverable loss of user funds, since neither the beneficiary, the pallet account, nor any storage item retains the truncated remainder. The `on_timeout` refund path has the same defect, meaning even the "safety net" refund of a failed/timed-out transfer does not fully restore the original escrowed amount when `erc_decimals != local_decimals` and the ERC20 amount isn't an exact multiple.

### Likelihood Explanation
High likelihood of at least minor loss on every message where token decimals differ between the EVM side and the Substrate side (a common configuration, since `ErcDecimalsBelowLocal` only guarantees `erc_decimals >= local_decimals`, not equality) and the transferred amount is not a round multiple of the scale factor. Because inbound messages are dispatched via ordinary ISMP `PostRequest` delivery/relaying — not privileged, and reachable by any user initiating a cross-chain send whose amount happens to include non-zero low-order digits — the precondition is trivial to hit in normal operation, not just via an adversarial input.

### Recommendation
- Track and accumulate truncated remainders (e.g., per asset/chain) in pallet storage, and either credit them back to the beneficiary in a follow-up mint, or expose a claimable/redeemable dust balance.
- Alternatively, reject/require inbound amounts to be exact multiples of `10^(erc_decimals - local_decimals)` when validating the message, forcing the EVM-side sender (or gateway) to only ever transmit amounts free of low-order dust, and refund the sender for any un-transmittable remainder before dispatch.
- At minimum, emit an event recording the truncated remainder so it is auditable, and treat this the same in both `on_accept` and `on_timeout`.

### Proof of Concept
1. Register a token where the EVM contract's ERC20 decimals are 18 and the local Substrate asset decimals are 6 (`register_token` permits this since `18 >= 6`) — divisor = `10^12`. [6](#0-5) 
2. A user (or contract) on the EVM chain dispatches a `PostRequest` to the pallet with `message.amount = 1_000_000_000_500` (i.e., `10^12 + 500`), representing `1.0000000000005` in ERC20 units.
3. `on_accept` calls `convert_to_balance(1_000_000_000_500, 18, 6)`, which computes `1_000_000_000_500 / 10^12 = 1` (integer division), discarding the `500` remainder. [7](#0-6) 
4. The beneficiary is minted/credited exactly `1` local unit; the `500`-unit remainder (in ERC20-decimal terms) is permanently gone — not minted, not stored, not refundable.
5. The identical defect applies on `on_timeout`, so even a failed transfer's refund does not restore the full original amount whenever the ERC20 amount isn't an exact multiple of the scale factor.

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

**File:** modules/pallets/hyper-fungible-token/src/lib.rs (L292-295)
```rust
			// Encode the Message body
			let sender: [u8; 32] = who.clone().into();
			let amount: u128 = params.amount.into();
			let erc20_amount = convert_to_erc20(amount, erc_decimals, decimals);
```

**File:** modules/pallets/hyper-fungible-token/src/lib.rs (L330-368)
```rust
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
