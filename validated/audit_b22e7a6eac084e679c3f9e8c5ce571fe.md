Confirmed: the ISMP timeout handler restores the request commitment (allowing retry) whenever `on_timeout` returns `Err`, per the "Danger" callout in `docs/content/protocol/ismp/timeouts.mdx:57-58` and the implementation in `modules/ismp/core/src/handlers/timeout.rs:122-134`. This means `pallet-hyper-fungible-token::update_token` removing a chain's `ContractToAsset`/`Precisions` entries while a `send` is still in flight causes `on_timeout` to fail *indefinitely* — the escrowed/burned funds can never be refunded through the normal retry path, since retrying just re-triggers the same lookup failure.

### Title
Removing a chain from a HyperFungibleToken asset permanently strands escrowed/burned funds pending timeout/delivery - ([File: modules/pallets/hyper-fungible-token/src/lib.rs])

### Summary
`pallet_hyper_fungible_token::update_token` lets `CreateOrigin` remove a chain's contract mapping (`TokenContracts`, `ContractToAsset`, `Precisions`) for an asset at any time, with no check for in-flight `send` requests to that chain. If a `remove_chains` update executes for a chain while a user's earlier `send` (which already escrowed or burned their tokens) is still awaiting delivery or timeout, both `on_accept` and `on_timeout` become permanently unable to resolve the asset for that chain, and the corresponding funds can never be recovered through the retry-safe ISMP timeout mechanism.

### Finding Description
`send` escrows (native) or burns (non-native) the caller's tokens, then dispatches a `DispatchPost` keyed on `(params.destination, params.asset_id)` [1](#0-0) .

`update_token`'s `remove_chains` branch deletes the `TokenContracts`, `ContractToAsset`, and `Precisions` entries for a chain with no guard against requests currently in flight to that chain: [2](#0-1) 

Both callbacks that must later resolve this asset depend entirely on these same maps:
- `on_accept` authenticates via `ContractToAsset::<T>::get(source, &from)` and reads `Precisions::<T>::get(local_asset_id, source)` [3](#0-2) 
- `on_timeout` looks up the asset via `ContractToAsset::<T>::get(dest, &to)` and `Precisions::<T>::get(local_asset_id, dest)` before refunding the original sender [4](#0-3) 

If governance/`CreateOrigin` removes the chain (e.g. deprecating a chain, rotating the contract address, or any routine `update_token` maintenance) while a `send` to that chain is still pending, `on_timeout` will hit `HftError::UnknownContractOnTimeout` for every future retry. The Hyperbridge timeout handler treats a failing `on_timeout` as "not yet settled" and restores the request commitment for retry rather than deleting it [5](#0-4) , and documents this explicitly as a module invariant to prevent partial state changes [6](#0-5) . Since the module never restores `ContractToAsset`/`Precisions` on its own, every retry fails the same way — the request can never be timed out successfully, and the previously escrowed/burned funds are permanently unreachable by this mechanism. The same failure mode applies to `on_accept` if a legitimate inbound message from that chain arrives after the mapping has been removed (e.g. the peer contract dispatched before the governance update landed): `UnknownSourceContract` blocks delivery with no alternate recovery path, and the tokens already burned/escrowed on the remote chain are stranded there instead.

This is the direct analog of the reported `UXDController` issue: an asset/chain being de-whitelisted after a deposit has been made removes the very state the redemption/timeout path needs, freezing user funds that were already committed under the old configuration.

### Impact Explanation
Funds already escrowed (native custody) or burned (non-native) by users via `send` become permanently unrecoverable once the destination chain mapping is removed while their request is unsettled — the ISMP retry-safety guarantee (restore-commitment-on-failure) actually locks the funds in limbo forever since nothing ever restores the deleted mapping. This is a genuine freezing-of-funds bug reachable by any ordinary user who called `send` before an entirely routine governance `update_token` call removed the chain.

### Likelihood Explanation
`update_token` is a normal maintenance operation (rotating a contract address by combining add+remove, or deprecating support for a chain) that `CreateOrigin` may reasonably invoke at any time without any awareness of currently in-flight `send` requests, since the pallet has no bookkeeping of pending cross-chain requests per chain/asset. Any `send` dispatched shortly before such an update is exposed; given non-zero timeouts and normal relay latency, this window is realistically reachable in production operations, not merely a contrived edge case.

### Recommendation
Before deleting a chain's `TokenContracts`/`ContractToAsset`/`Precisions` entries in `update_token`, either (a) track outstanding request commitments per `(asset_id, chain)` and refuse removal while any are pending, or (b) retain the old contract-to-asset and precision mapping in a secondary "retired" store so `on_accept`/`on_timeout` can still resolve requests dispatched under the prior configuration, falling back to it when the primary lookup misses. Alternatively, allow `on_timeout` to fall back to decoding the asset directly from stored request metadata rather than depending solely on live governance-mutable storage.

### Proof of Concept
1. Governance registers asset `X` with chain `Evm(1)` via `register_token`, mapping contract `C` to `X` in `TokenContracts`/`ContractToAsset`/`Precisions`.
2. Alice calls `send` with `destination = Evm(1)`, `asset_id = X`; her tokens are escrowed (or burned) and a `DispatchPost` is dispatched with a non-zero timeout.
3. Before delivery or timeout, `CreateOrigin` calls `update_token` with `remove_chains = [Evm(1)]` for asset `X` — routine maintenance, e.g. rotating to a new contract address without adding it back yet, or dropping the chain. This deletes `TokenContracts`, `ContractToAsset`, and `Precisions` for `(Evm(1), X)`.
4. The request eventually times out; a relayer submits `TimeoutMessage::Post`. `pallet-ismp`'s `handle` calls `on_timeout`, which calls `ContractToAsset::<T>::get(dest, &to)` — now `None` — and returns `Err(HftError::UnknownContractOnTimeout)`.
5. Per `modules/ismp/core/src/handlers/timeout.rs:122-134`, the commitment is restored for retry rather than deleted. Every subsequent retry of the timeout hits the identical `None` lookup and fails identically.
6. Alice's escrowed/burned funds from step 2 are now permanently unrecoverable — neither `on_accept` (mapping is gone) nor `on_timeout` (same) can ever resolve them.

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

**File:** modules/pallets/hyper-fungible-token/src/module.rs (L54-83)
```rust
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
```

**File:** modules/pallets/hyper-fungible-token/src/module.rs (L218-247)
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
```

**File:** modules/ismp/core/src/handlers/timeout.rs (L122-134)
```rust
					if res.is_ok() {
						host.on_request_timeout(&request, meta)?;
					} else {
						// Module callback failed; restore commitment so the request
						// can be retried.
						host.store_request_commitment(&request, meta)?;
						if host.host_state_machine() != post.source && signer.is_some() {
							host.store_request_receipt(
								&request,
								&signer.ok_or_else(|| anyhow::anyhow!("Infallible"))?,
							)?;
						}
					}
```

**File:** docs/content/protocol/ismp/timeouts.mdx (L57-58)
```text
<Callout title={'Danger'} type={"warn"}>
It's important to note that if the `IsmpModule::on_timeout` does not return `Ok`, the commitment of the relevant messages will not be deleted, allowing the timeout to be **replayed**. Consequently, the `IsmpModule` is responsible for maintaining all invariants before modifying it's internal state to prevent partial state changes that could result in critical vulnerabilities in their timeout handler. This model ensures that if a timeout cannot be executed successfully, it can be retried later.
```
