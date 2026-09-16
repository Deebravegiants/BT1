### Title
Stale reverse-mapping entries in `ContractToAsset` allow duplicate/orphaned EVM contracts to mint against a live asset — (File: `modules/pallets/hyper-fungible-token/src/lib.rs`)

### Summary
`pallet-hyper-fungible-token`'s `register_token` extrinsic writes the forward mapping `TokenContracts[chain, asset_id] -> contract` and the reverse mapping `ContractToAsset[chain, contract] -> asset_id` for every chain in a registration, but never checks for or removes any pre-existing entry when an asset is re-registered with a new contract address for the same `(chain, asset_id)` pair. Only the separate `update_token` call cleans up the old reverse mapping. If governance ever re-runs `register_token` for an asset whose EVM contract migrated (upgrade, redeploy, deprecation), the old contract address remains permanently valid in `ContractToAsset`, alongside the new one, both resolving to the same local asset. This is structurally the same "old and new market both live" condition that caused the LendHub loss: two different acceptance points, one supposed to be retired, both still recognized by the accounting logic (`on_accept`), and sharing the *same* `Precisions` entry keyed only by `(asset_id, chain)` regardless of which contract sent the message.

### Finding Description
`register_token` at [1](#0-0)  unconditionally inserts into both `TokenContracts` and `ContractToAsset` for each configured chain, without checking whether an entry already exists for that `(chain, asset_id)` and, critically, without removing the previous `ContractToAsset[chain, old_contract]` entry if the contract address changes.

Contrast this with `update_token`, which explicitly removes the stale reverse mapping before writing a new one: [2](#0-1) 

Because `register_token` is the documented entry point for registering a token's per-chain contract, and there is nothing preventing it from being called again for an already-registered `asset_id`/`chain` pair (e.g. after a contract upgrade or redeploy), calling it a second time leaves:
- `TokenContracts[chain, asset_id] = new_contract` (forward map updated correctly)
- `ContractToAsset[chain, old_contract] = asset_id` (stale, never removed)
- `ContractToAsset[chain, new_contract] = asset_id` (new, correct)

`on_accept` authenticates any incoming message purely by looking up `ContractToAsset::<T>::get(source, &from)`: [3](#0-2) 

Both the old and the new contract addresses on that chain now authenticate as valid sources for the same local asset. Worse, the ERC decimals used to convert the incoming amount are looked up only by `(asset_id, source)` in `Precisions`, with no distinction for which contract sent it: [4](#0-3) 

If the old contract had different decimals or a different custody/supply state than the currently-registered one (e.g. it was deprecated because of a bug, or its balance/allowance configuration differs), messages relayed from the old contract are still accepted and minted/unlocked using the *current* registration's `Precisions` and `NativeAssets` flag — exactly the LendHub pattern of two live markets sharing one price/liability accounting path while having diverged state.

### Impact Explanation
An attacker (or an already-compromised/abandoned old token contract) can dispatch a `PostRequest` from the stale, still-recognized contract address. Since `on_accept` accepts it and mints (`Assets::mint_into`) or unlocks (`NativeCurrency::transfer`/`Assets::transfer`) funds from the pallet's custody account using the current asset's precision/native settings, this can result in unbacked minting or draining of the custody account for the currently-live asset — a direct, unauthorized-mint / fund-loss impact reachable by a single relayed message once the registration divergence exists.

### Likelihood Explanation
Re-registration of an already-registered asset with a new contract address is a normal, expected operational event (contract redeploys/upgrades are common in EVM ecosystems), and `register_token` provides no guard against it and no cleanup step, unlike `update_token`. Any legitimate governance action that re-registers an asset via `register_token` (rather than remembering to explicitly `update_token` + remove the old chain first) silently creates this dual-acceptance condition, after which exploitation only requires a single relayed message from the old, still-mapped contract address.

### Recommendation
In `register_token`, before inserting a new `TokenContracts`/`ContractToAsset` pair, check for and remove any existing `TokenContracts[chain, asset_id]` entry's corresponding `ContractToAsset` reverse mapping (mirroring the cleanup already done in `update_token`), or reject re-registration of an already-registered `(chain, asset_id)` and require callers to go through `update_token` exclusively for changes to existing chains.

### Proof of Concept
1. Governance calls `register_token` for `asset_id = X` with `chains = { Evm(1): ChainConfig { token_contract: A, decimals: 18 } }`. This sets `TokenContracts[Evm(1), X] = A` and `ContractToAsset[Evm(1), A] = X`.
2. The contract at `A` is later redeployed/migrated to address `B` (e.g., due to an upgrade). Governance calls `register_token` again for `asset_id = X` with `chains = { Evm(1): ChainConfig { token_contract: B, decimals: 18 } }`. Per [1](#0-0) , this sets `TokenContracts[Evm(1), X] = B` and `ContractToAsset[Evm(1), B] = X`, but `ContractToAsset[Evm(1), A] = X` is never removed.
3. Anyone able to relay (or forge, if `A` is still deployed and callable, or was compromised/abandoned) a `PostRequest` with `source = Evm(1)`, `from = A` is still accepted by `on_accept` ( [3](#0-2) ), resolving to `local_asset_id = X` and minting/unlocking funds to an attacker-controlled beneficiary using the pallet's current `Precisions`/`NativeAssets` configuration for `X`, regardless of `A`'s actual on-chain state.

### Citations

**File:** modules/pallets/hyper-fungible-token/src/lib.rs (L356-367)
```rust
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
```

**File:** modules/pallets/hyper-fungible-token/src/lib.rs (L407-419)
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
```

**File:** modules/pallets/hyper-fungible-token/src/module.rs (L54-56)
```rust
		// Authenticate: look up which local asset this contract address maps to
		let local_asset_id = ContractToAsset::<T>::get(source, &from)
			.ok_or(HftError::UnknownSourceContract(source))?;
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
