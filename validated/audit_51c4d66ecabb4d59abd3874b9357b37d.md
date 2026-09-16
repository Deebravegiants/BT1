### Title
`register_token` leaves stale `ContractToAsset` reverse-mapping entries, letting a decommissioned EVM contract keep minting/unlocking tokens - ([File: modules/pallets/hyper-fungible-token/src/lib.rs])

### Summary
Same bug class as the `GatewayRegistry` finding: a privileged "re-registration" path overwrites a forward mapping but forgets to clear the corresponding reverse mapping, leaving a stale entry that a later, unprivileged message delivery can exploit to unlock value that should no longer be reachable through that key.

### Finding Description
`pallet_hyper_fungible_token::register_token` writes `TokenContracts[(chain, asset_id)] = new_contract` and `ContractToAsset[(chain, new_contract)] = asset_id`, but it never removes the previous `ContractToAsset[(chain, old_contract)]` entry when the same `(asset_id, chain)` pair is registered again with a different `token_contract`: [1](#0-0) 

Compare this with `update_token`, which explicitly removes the stale reverse entry before inserting the new one: [2](#0-1) 

`on_accept` — the entry point reachable by any relayer delivering an ISMP message from the EVM side — authenticates purely by looking up `ContractToAsset::<T>::get(source, &from)`, with no additional freshness/liveness check on the contract address: [3](#0-2) 

So if governance calls `register_token` a second time for the same `asset_id`/chain to rotate the EVM contract address (e.g., after finding a bug in the old EVM `HyperFungibleTokenImpl`/`WrappedHyperFungibleToken` contract, or moving to a new deployment), the old contract address remains a valid `from` for `on_accept` forever. Any message purporting to originate from that old, no-longer-canonical contract address is still accepted and will mint/unlock tokens for the registered asset — exactly the "stale mapping never cleared on effective re-registration" root cause described in the `GatewayRegistry` report, just manifesting on the reverse contract→asset lookup instead of a stake-tracking array.

### Impact Explanation
An attacker who controls (or who can still trigger message construction from) the decommissioned EVM contract address — for instance if that contract was deprecated precisely because it was compromised, or because its logic allows arbitrary `Send` messages to be crafted by anyone (self-service dispatch is the whole point of the paired EVM contract) — can continue to originate `on_accept` calls that are authenticated as the current asset. This results in unbacked minting of the wrapped asset (`Assets::mint_into`) or draining of the native-asset custody account (`NativeCurrency::transfer` from `pallet_account()`), i.e., concrete theft/unbacked mint of funds, satisfying the "Accept" bar (unbacked mint / unauthorized app action).

### Likelihood Explanation
This requires a specific but plausible governance sequence: calling `register_token` twice for the same `(asset_id, chain)` with different `token_contract` values instead of always routing rotations through `update_token`. Both extrinsics exist in the same pallet and have overlapping purposes, and nothing in `register_token`'s logic or documentation prevents or warns against using it for a rotation. Given `update_token` demonstrably implements the correct cleanup for the same scenario, the omission in `register_token` looks like an oversight rather than an intentional exclusion, and governance operators rotating a contract are unlikely to know that only one of the two near-identical extrinsics performs the cleanup.

### Recommendation
In `register_token`, before inserting a new `ContractToAsset` entry for a `(chain, asset_id)` pair, look up and remove any existing `TokenContracts::get(chain, asset_id)` → `ContractToAsset` reverse entry, mirroring the cleanup already implemented in `update_token`:
```rust
if let Some(old_contract) = TokenContracts::<T>::get(chain, registration.local_id.clone()) {
    ContractToAsset::<T>::remove(chain, old_contract);
}
```

### Proof of Concept
1. Governance calls `register_token` for `asset_id = X` with `chains = { Evm(1) => ChainConfig { token_contract: A, decimals: 18 } }`. Now `TokenContracts[(Evm(1), X)] = A` and `ContractToAsset[(Evm(1), A)] = X`.
2. Contract `A` is later found to be flawed / needs replacement. Governance calls `register_token` again for the same `asset_id = X` with `chains = { Evm(1) => ChainConfig { token_contract: B, decimals: 18 } }`. Now `TokenContracts[(Evm(1), X)] = B` and `ContractToAsset[(Evm(1), B)] = X`, but `ContractToAsset[(Evm(1), A)] = X` is untouched and still present.
3. Any relayer submits an ISMP `PostRequest` with `source = Evm(1)`, `from = A` (still a legitimate, previously-deployed contract address) to `on_accept`. The lookup `ContractToAsset::<T>::get(source, &from)` succeeds and returns `X`, so the pallet mints/unlocks tokens for asset `X` to the attacker-controlled beneficiary, even though contract `A` is no longer the sanctioned bridge contract for `X`. [4](#0-3) [5](#0-4)

### Citations

**File:** modules/pallets/hyper-fungible-token/src/lib.rs (L344-368)
```rust
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

**File:** modules/pallets/hyper-fungible-token/src/lib.rs (L407-420)
```rust
				// Remove old reverse mapping if it exists
				if let Some(old_contract) = TokenContracts::<T>::get(chain, update.asset_id.clone())
				{
					ContractToAsset::<T>::remove(chain, old_contract);
				}

				let token_contract = config.token_contract.0.to_vec();
				TokenContracts::<T>::insert(
					chain,
					update.asset_id.clone(),
					token_contract.clone(),
				);
				ContractToAsset::<T>::insert(chain, token_contract, update.asset_id.clone());
				Precisions::<T>::insert(update.asset_id.clone(), chain, config.decimals);
```

**File:** modules/pallets/hyper-fungible-token/src/module.rs (L50-117)
```rust
	fn on_accept(
		&self,
		PostRequest { body, from, source, .. }: PostRequest,
	) -> Result<Weight, anyhow::Error> {
		// Authenticate: look up which local asset this contract address maps to
		let local_asset_id = ContractToAsset::<T>::get(source, &from)
			.ok_or(HftError::UnknownSourceContract(source))?;

		// Decode the Message
		let message = Message::abi_decode(&body).map_err(HftError::DecodeError)?;

		// Convert recipient bytes to substrate AccountId
		// If 32 bytes: use directly. If 20 bytes: left-pad with zeros.
		let mut beneficiary_bytes = [0u8; 32];
		let to_bytes = message.to.as_ref();
		if to_bytes.len() == 32 {
			beneficiary_bytes.copy_from_slice(to_bytes);
		} else if to_bytes.len() == 20 {
			beneficiary_bytes[12..].copy_from_slice(to_bytes);
		} else {
			Err(HftError::InvalidRecipientLength(to_bytes.len()))?;
		}
		let beneficiary: T::AccountId = beneficiary_bytes.into();

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
