## Title
Removing a chain from a HyperFungibleToken's configuration permanently blocks timeout refunds for funds already in transit - (File: `modules/pallets/hyper-fungible-token/src/lib.rs`, `modules/pallets/hyper-fungible-token/src/module.rs`)

### Summary
`pallet-hyper-fungible-token` looks up per-`(asset, StateMachine)` decimal precision (`Precisions`) on both the accept path and the timeout/refund path. The `update_token` extrinsic lets governance remove a chain's configuration (`remove_chains`) from a token that already has outstanding in-flight transfers to that chain. Once the chain's `Precisions` entry is gone, a subsequent `on_timeout` for a request that was dispatched while the chain was still configured can no longer resolve `erc_decimals`, causing the refund path to error out and permanently strand the user's escrowed/burned funds — the same "removing a previously-approved parameter breaks a core downstream function for pre-existing state" pattern as the Revert Finance `collateralFactor` bug, here manifesting as a required-but-now-missing config lookup instead of a division by zero.

### Finding Description
`send()` escrows (native asset) or burns (non-native asset) the user's funds and dispatches a cross-chain `Post` request, keyed to the destination chain's registered token contract and decimals: [1](#0-0) 

If that request times out, `on_timeout` must look up the same `Precisions` entry to convert the ERC20 amount back to local balance before refunding the sender: [2](#0-1) 
and it returns a hard error, `HftError::DecimalsNotConfigured(dest)`, if the entry is missing.

`update_token` is a governance-gated (`T::CreateOrigin`) extrinsic that both adds/updates and — per its `TokenUpdate` type and its own doc comment ("Add or remove chains from an existing token's configuration") — removes chains from a token's configuration: [3](#0-2) [4](#0-3) 
`TokenContracts`, `ContractToAsset` and `Precisions` are all keyed by `(StateMachine, AssetId)`/`(AssetId, StateMachine)`, so a `remove_chains` entry is expected to clear the same `Precisions` map that `on_accept`/`on_timeout` depend on: [5](#0-4) 

Because governance can legitimately deprecate a chain at any time — the same "reasonable and normal" admin action the Revert-Lend judge cited when downgrading severity — any `send()` that is in flight to that chain at the moment of removal (or any request that has not yet been delivered/confirmed and later times out) will hit the now-empty `Precisions` entry in `on_timeout` and revert with `DecimalsNotConfigured`, exactly mirroring how Revert's `_checkLoanIsHealthy`/`_calculateLiquidation` reverted once `collateralFactor` was zeroed for an already-open loan.

### Impact Explanation
A single unprivileged `send()` transaction escrows or burns the user's tokens; the user's ability to recover those funds on timeout depends entirely on the destination chain's config remaining present. A governance action that removes the chain (a routine, sanctioned reconfiguration, not an attack) permanently blocks the on-timeout refund path for any transfer that was already dispatched, which either:
- reverts the timeout dispatchable so pallet-ismp can never clear/refund the request (permanent freezing of the user's escrowed or burned funds), or
- if pallet-ismp treats a module error as a dropped/ignored timeout, silently leaves the burned/escrowed principal unrecoverable.

Either outcome is a permanent freezing of user funds triggered by a normal admin/governance configuration change, matching the accepted Medium severity of the analog finding.

### Likelihood Explanation
This requires no malicious actor: any legitimate `send()` racing an in-progress or subsequently-approved `update_token(remove_chains=[dest])` governance call is enough. Chain deprecations, contract migrations, or decimal corrections via `update_token` are described in the pallet's own documentation as normal operations, so the window where in-flight transfers exist alongside a chain removal is realistic, especially under a relayer outage or a deliberately delayed relay that pushes a request past a planned deprecation.

### Recommendation
Do not treat the absence of a `Precisions`/`TokenContracts` entry as fatal in `on_timeout`. Options:
- Snapshot/cache the decimals used at `send()` time (e.g., store them alongside the outgoing request commitment) so `on_timeout` never needs a live config lookup.
- Retain `Precisions` entries for chains that have been "soft-removed" (mark them inactive for new `send()`s only) rather than deleting them, and only garbage-collect once no in-flight requests reference that `(asset, chain)` pair.
- If deletion is required, provide a governance escape hatch to re-add just enough config (contract address + decimals) to allow outstanding timeouts to resolve, and document that `remove_chains` must never be executed while requests to that chain are outstanding.

### Proof of Concept
1. `register_token` a non-native asset with a chain config for `StateMachine::Evm(X)` (decimals `d`).
2. User calls `send()` to `Evm(X)`; the pallet burns the user's tokens and dispatches a `Post` request via ISMP (`modules/pallets/hyper-fungible-token/src/lib.rs:257-315`).
3. Before the request is delivered/confirmed, governance calls `update_token` with `remove_chains: [Evm(X)]`, which clears `Precisions::<T>::get(asset_id, Evm(X))` (and the contract mappings) for that pair.
4. The request times out; `pallet-ismp` invokes `on_timeout`, which calls `Precisions::<T>::get(local_asset_id, dest).ok_or(HftError::DecimalsNotConfigured(dest))?` (`modules/pallets/hyper-fungible-token/src/module.rs:246-247`) and errors instead of refunding the user.
5. The user's burned tokens are never returned, and no code path exists to convert the ERC20 amount back to local balance for that chain without re-registering it.

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

**File:** modules/pallets/hyper-fungible-token/src/lib.rs (L378-421)
```rust
		/// Updates chain configuration for an existing token
		#[pallet::call_index(2)]
		#[pallet::weight(T::WeightInfo::update_token(
			update.add_chains.len() as u32,
			update.remove_chains.len() as u32,
		))]
		pub fn update_token(
			origin: OriginFor<T>,
			update: TokenUpdate<AssetId<T>>,
		) -> DispatchResult {
			T::CreateOrigin::ensure_origin(origin)?;

			let local_decimals = if update.asset_id == T::NativeAssetId::get() {
				T::Decimals::get()
			} else {
				<T::Assets as fungibles::metadata::Inspect<T::AccountId>>::decimals(
					update.asset_id.clone(),
				)
			};

			for (chain, config) in update.add_chains {
				// This pallet bridges substrate <-> EVM only; reject non-EVM peers.
				if !matches!(chain, StateMachine::Evm(_)) {
					return Err(Error::<T>::NonEvmPeerChain.into());
				}
				ensure!(
					config.decimals >= local_decimals,
					Error::<T>::ErcDecimalsBelowLocal
				);
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
			}
```

**File:** modules/pallets/hyper-fungible-token/src/module.rs (L239-255)
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
```

**File:** modules/pallets/hyper-fungible-token/src/types.rs (L92-103)
```rust
/// Parameters for updating an existing token's chain configuration
#[derive(
	Debug, Clone, Encode, Decode, DecodeWithMemTracking, scale_info::TypeInfo, PartialEq, Eq,
)]
pub struct TokenUpdate<AssetId> {
	/// Local asset ID
	pub asset_id: AssetId,
	/// Chains to add or update
	pub add_chains: BTreeMap<StateMachine, ChainConfig>,
	/// Chains to remove
	pub remove_chains: Vec<StateMachine>,
}
```

**File:** modules/pallets/hyper-fungible-token/README.md (L38-43)
```markdown
| Item | Type | Description |
|------|------|-------------|
| `TokenContracts` | `DoubleMap<StateMachine, AssetId → Vec<u8>>` | EVM contract address of a token on the given chain. Used as the `to` field on outgoing `DispatchPost`. |
| `ContractToAsset` | `DoubleMap<StateMachine, Vec<u8> → AssetId>` | Reverse lookup; on `on_accept` the source contract is mapped back to the local asset. |
| `NativeAssets` | `Map<AssetId → bool>` | Custody model flag (native vs non-native). |
| `Precisions` | `DoubleMap<AssetId, StateMachine → u8>` | EVM decimals for an `(asset, chain)` pair. |
```
