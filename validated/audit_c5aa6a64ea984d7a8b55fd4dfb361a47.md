### Title
`update_token`'s `remove_chains` can permanently strand in-flight `HyperFungibleToken` transfers by breaking the `on_timeout` refund path - (File: `modules/pallets/hyper-fungible-token/src/module.rs`)

### Summary
The `pallet-hyper-fungible-token` `update_token` extrinsic lets `CreateOrigin` remove a chain's contract mapping (`TokenContracts`, `ContractToAsset`, `Precisions`) for an asset at any time, with no check for in-flight cross-chain sends still pending against that chain. When such a send later times out, `on_timeout` re-derives the asset and decimals by looking up the now-deleted `ContractToAsset`/`Precisions` entries; the lookup fails and the refund reverts, permanently stranding (or, for non-native assets, permanently burning) the sender's escrowed funds — the same class of bug as the JUSDBank report, where a delist action performed after a user action makes recovery of that user's already-locked/escrowed funds impossible.

### Finding Description
`send()` escrows (native asset) or burns (non-native asset) the sender's tokens and dispatches a `DispatchPost` to the destination chain's contract, keyed by the current `TokenContracts`/`ContractToAsset`/`Precisions` entries for `(asset_id, destination)`: [1](#0-0) 

`update_token` (governance-only, but reachable/triggerable as a normal governance/config-change flow with no user-funds safety check) can remove a chain's mapping for an asset at any time: [2](#0-1) 

If a `send()` was dispatched to that chain before removal and later times out (e.g. the relayer misses the timeout window, or the request simply is never delivered), `on_timeout` re-derives the local asset by looking up `ContractToAsset::<T>::get(dest, &to)` and the decimals via `Precisions::<T>::get(local_asset_id, dest)`: [3](#0-2) 

Once `update_token` has removed that chain for the asset, both of these lookups return `None`, and `on_timeout` errors out (`HftError::UnknownContractOnTimeout` / `HftError::DecimalsNotConfigured`) before the refund transfer/mint executes: [4](#0-3) 

For a **non-native** asset the tokens were already `burn_from`'d at `send()` time, so a failed `on_timeout` means those tokens are gone forever with no compensating mint. For a **native** asset the tokens remain escrowed in the pallet account but the only path back to the user (`on_timeout`'s transfer) is permanently blocked until an operator manually restores the exact stale `(chain, contract-address)` mapping — something the runtime provides no mechanism or incentive to do, and which is not the "delist" action's evident purpose.

This mirrors the JUSDBank analog precisely: an unrelated administrative action (`delistReserve` / `update_token` remove_chains) that is legitimate and necessary for protocol maintenance nonetheless retroactively invalidates the accounting/lookup data an already-in-flight user operation depends on to recover its own funds, with no safeguard requiring in-flight operations to drain or settle first.

### Impact Explanation
Any user with a `send()` in flight to a chain that governance decides to `remove_chains` for that asset (e.g., to migrate to a new contract address, deprecate a route, or respond to an incident) can have their transfer's timeout refund path permanently break:
- Non-native assets: funds are burned at send-time and never re-minted — direct, unrecoverable loss of user funds.
- Native assets: funds remain escrowed in the pallet account indefinitely, inaccessible to the user — a freezing-of-funds outcome.

This satisfies the "concrete theft or permanent freezing of funds" bar even though a single call is not attacker-controlled for profit; it is a legitimate config-change (routine chain/contract migration) that a normal user cannot foresee or prevent, and it strands their money with no on-chain recovery path.

### Likelihood Explanation
`update_token` with `remove_chains` is a documented, expected part of the pallet's operational lifecycle (e.g. contract migrations, deprecating a chain) — not a hypothetical misuse. Any window where a `send()` is outstanding (network latency, relayer delay, or deliberate timeout for stuck requests) coincides with a routine `update_token` call to trigger this. No attacker action is required; it can happen purely through normal governance operations combined with normal user activity, making it moderately likely to occur in production over time.

### Recommendation
Before removing a chain (or asset mapping) via `update_token`, either:
1. Retain the old `(chain, contract)` → asset / decimals mapping in a secondary "retired" store that `on_timeout` (and `on_accept`, if needed) can still consult, so in-flight requests continue to resolve correctly after removal; or
2. Enforce a delay/quarantine period (long enough to exceed any outstanding request's timeout) between removing a chain and purging its `ContractToAsset`/`Precisions` entries; or
3. Encode the asset id and decimals directly in the outgoing `Message`/`DispatchPost` body rather than deriving them from mutable pallet storage at `on_timeout` time, so refunds don't depend on configuration that can change after dispatch.

### Proof of Concept
1. Governance registers asset `A` with `chains = {Evm(X): contract_X}` via `register_token`.
2. Alice calls `send(asset_id=A, destination=Evm(X), amount=100)`; her non-native `A` tokens are `burn_from`'d and a `DispatchPost` is dispatched to `contract_X` on chain `X`.
3. Before the request is delivered or has timed out, governance calls `update_token(asset_id=A, remove_chains=[Evm(X)])` (e.g., migrating `A` to a new contract on chain `X`). This removes `TokenContracts[X,A]`, `ContractToAsset[X, contract_X]`, and `Precisions[A, X]`.
4. The original request eventually times out; `pallet-ismp` invokes `on_timeout`. `ContractToAsset::<T>::get(dest=X, &to=contract_X)` now returns `None`, so `on_timeout` returns `Err(HftError::UnknownContractOnTimeout)` before any refund/mint occurs.
5. Alice's 100 `A` tokens, burned in step 2, are never restored — permanent loss. (For a native asset, the tokens instead sit escrowed in the pallet account with no way for Alice to reclaim them.)

### Citations

**File:** modules/pallets/hyper-fungible-token/src/lib.rs (L251-290)
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
```

**File:** modules/pallets/hyper-fungible-token/src/lib.rs (L423-430)
```rust
			for chain in update.remove_chains {
				if let Some(old_contract) = TokenContracts::<T>::get(chain, update.asset_id.clone())
				{
					ContractToAsset::<T>::remove(chain, old_contract);
				}
				TokenContracts::<T>::remove(chain, update.asset_id.clone());
				Precisions::<T>::remove(update.asset_id.clone(), chain);
			}
```

**File:** modules/pallets/hyper-fungible-token/src/module.rs (L218-256)
```rust
	fn on_timeout(&self, request: Request) -> Result<Weight, anyhow::Error> {
		match request {
			Request::Post(PostRequest { body, to, dest, .. }) => {
				let message = Message::abi_decode(&body).map_err(HftError::DecodeError)?;

				// Refund the original sender
				let from_bytes = message.from.as_ref();
				let mut sender_bytes = [0u8; 32];
				if from_bytes.len() == 32 {
					sender_bytes.copy_from_slice(from_bytes);
				} else if from_bytes.len() == 20 {
					sender_bytes[12..].copy_from_slice(from_bytes);
				} else {
					Err(HftError::InvalidSenderLength(from_bytes.len()))?
				}
				let beneficiary: T::AccountId = sender_bytes.into();

				// Look up the asset from the destination contract address
				let local_asset_id = ContractToAsset::<T>::get(dest, &to)
					.ok_or(HftError::UnknownContractOnTimeout)?;

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

```
