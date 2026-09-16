### Title
Truncation in `convert_to_balance` permanently loses ERC20 dust when receiving cross-chain transfers - (File: modules/pallets/hyper-fungible-token/src/impls.rs)

### Summary
The `hyper-fungible-token` pallet's `on_accept` and `on_timeout` handlers convert an incoming ERC20 `U256` amount (up to 18 decimals) to the local Substrate asset's balance type via `convert_to_balance`, which performs integer division to scale down precision. Any remainder below the local asset's precision is silently discarded, with no accounting, refund, or credit mechanism for the truncated dust.

### Finding Description
`convert_to_balance` divides the incoming ERC20 amount by `10^(erc_decimals - local_decimals)`: [1](#0-0) 

This is invoked directly on message data decoded from an untrusted, relayer-delivered `PostRequest` in `on_accept` (the path reachable by anyone relaying a cross-chain message once the source contract/asset mapping exists): [2](#0-1) 

and again in `on_timeout` for refunds: [3](#0-2) 

When `erc_decimals > local_decimals` (e.g., an 18-decimal EVM token bridged to a 6- or 10-decimal Substrate asset), any ERC20 amount that is not an exact multiple of `10^(erc_decimals - local_decimals)` loses its fractional remainder. That remainder is not minted to the beneficiary, not returned to any pallet account, and not tracked in any storage item — it simply vanishes. The `send()` extrinsic path (Substrate → EVM) uses `convert_to_erc20`, which only scales *up* (multiplication) and is lossless, since `register_token`/`update_token` enforce `erc_decimals >= local_decimals`: [4](#0-3) 

But the reverse direction (EVM → Substrate) has no such protection: an amount arriving from the EVM-side `HyperFungibleToken` contract that was burned/locked in full is only partially credited on the Substrate side whenever its low-order digits are non-zero relative to the local decimal precision.

### Impact Explanation
Every EVM→Substrate transfer whose ERC20 amount doesn't align exactly to the local asset's decimal granularity permanently loses the truncated remainder. Because the full ERC20 amount was already escrowed/burned on the EVM side (per the `send()`/mint-burn message-passing model), the truncated fraction becomes unbacked and unrecoverable value — a direct, permanent loss of user funds on every affected transfer, not a one-off edge case. This is a systemic precision-loss issue triggered on the ordinary "receive" code path for any asset pair with differing decimals, matching the reported bug class (loss when converting high precision to low precision) exactly.

### Likelihood Explanation
High. Any token pair registered with `erc_decimals != local_decimals` (a normal, expected configuration per the pallet's own design, e.g., 18-decimal EVM token vs. 6- or 10-decimal Substrate asset) will trigger this on essentially every transfer, since ERC20 amounts sent from EVM wallets are rarely round multiples of `10^(erc_decimals - local_decimals)`. No privileged action is required — a single ordinary cross-chain transfer relayed through the standard message-delivery flow reproduces the loss.

### Recommendation
Do not silently discard the truncated remainder. Options:
- Reject/refuse messages whose amount is not evenly divisible by `10^(erc_decimals - local_decimals)`, returning an error instead of truncating.
- Or, retain the truncated remainder in the pallet's custodial account (or a dedicated dust-tracking storage item) so it can eventually be swept/credited rather than being permanently lost.
- Alternatively, only allow the receiving low-precision asset to always be the higher-precision side operationally, or round to the nearest unit and account for the systemic difference through a dust pool checked against the amount escrowed/burned on the EVM leg.

### Proof of Concept
1. Register a local asset with `local_decimals = 6` and `erc_decimals = 18` for a given EVM chain via `register_token` (passes `ErcDecimalsBelowLocal` check since `18 >= 6`): [5](#0-4) 
2. On the EVM chain, a user sends `1_500000000000000001` wei (18 decimals) of the token via the `HyperFungibleToken` contract, which is fully locked/burned there.
3. Hyperbridge delivers the corresponding `PostRequest` to the Substrate `on_accept` handler.
4. `convert_to_balance` computes `1_500000000000000001 / 10^12 = 1_500000` (6-decimal units), discarding the trailing `000000000001` fraction.
5. The beneficiary is minted/credited only `1_500000` local units; the fractional `0.000000000001` ERC20-equivalent token value that was escrowed/burned on the EVM side is permanently lost with no corresponding credit anywhere in the system.

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

**File:** modules/pallets/hyper-fungible-token/src/module.rs (L82-91)
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
```

**File:** modules/pallets/hyper-fungible-token/src/module.rs (L246-255)
```rust
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
