### Title
Removing a chain from `pallet-hyper-fungible-token` while a transfer is in-flight permanently locks user funds because `on_timeout` depends on the same `ContractToAsset` mapping that `update_token` deletes - ([File: modules/pallets/hyper-fungible-token/src/lib.rs])

### Summary
`pallet-hyper-fungible-token` mirrors the reported `PortalV2`/`WhitelistV2` pattern: a user-initiated cross-chain transfer burns/escrows tokens on the source chain based on the configuration valid *at send time*, but the pallet re-checks a mutable, admin-controlled mapping (`ContractToAsset`) at a later point in the transfer's lifecycle (`on_timeout`) rather than relying on data embedded in the original request. If that mapping is changed between `send` and delivery/timeout, the refund path reverts and the user's principal — already burned or escrowed — becomes permanently unrecoverable, which is a strictly worse outcome than the original report's fee-only loss.

### Finding Description
`send()` looks up the destination token contract address from `TokenContracts` and dispatches an ISMP `PostRequest` after burning (non-native asset) or escrowing (native asset) the user's funds: [1](#0-0) 

If the corresponding cross-chain request never gets accepted on the destination and times out, `on_timeout` is expected to refund the original sender. To do so it must re-derive the local asset ID from the **current** `ContractToAsset` storage, keyed by `(dest, to)` where `to` is the destination contract address that was embedded in the original request: [2](#0-1) 

`ContractToAsset` is not immutable per-request state — it is a live configuration map that `update_token` can freely rewrite or delete via `remove_chains`, dropping both the `TokenContracts` and `ContractToAsset` entries for that chain: [3](#0-2) 

Sequence:
1. User calls `send()` targeting chain X; the pallet burns the user's non-native asset and dispatches a `PostRequest` with `to = <old contract address on X>`. `ContractToAsset::<T>::get(X, old_contract)` currently resolves to the asset.
2. Before the request is delivered/accepted, `CreateOrigin` calls `update_token` with `remove_chains: [X]` (a normal maintenance/config operation, e.g. migrating to a new contract address on X, deprecating a chain, or rotating an asset mapping) — this deletes `TokenContracts::(X, asset)` and `ContractToAsset::(X, old_contract)`.
3. The request eventually times out (either because delivery genuinely failed, or because the destination-side registration was likewise updated/removed so `on_accept` there rejects it).
4. `on_timeout` executes `ContractToAsset::<T>::get(dest, &to)`, which now returns `None` because the entry was removed in step 2, causing `Err(HftError::UnknownContractOnTimeout)`.
5. The timeout handler reverts, so the refund transfer never executes. The user's tokens were already burned in step 1 and can never be minted on the destination (its own registration was also changed) nor refunded on the source (its lookup is now broken) — the funds are permanently lost.

This is the same root cause class as the reported bug: a state check performed asynchronously at a later stage of a cross-chain lifecycle depends on mutable configuration that can legitimately change between the time funds are debited and the time recovery/refund is attempted, with no mechanism to correlate the refund with the *original* mapping used at send time.

### Impact Explanation
Unlike the original report (relayer-fee-only loss), this analog risks the **entire principal** of an in-flight transfer becoming permanently unrecoverable: burned on the source chain, never minted on the destination, and now un-refundable via `on_timeout` because the lookup key it depends on has been deleted. This is a concrete, permanent freezing-of-funds condition reachable through the pallet's normal token-lifecycle-management call (`update_token`), which is a legitimate, expected administrative operation (chain deprecation, contract migration/rotation, asset re-mapping) rather than a malicious-admin exploit — exactly analogous to the honest `WhitelistV2` owner action in the original report.

### Likelihood Explanation
Any token/chain configuration update (`update_token` with `remove_chains`, or effectively re-registering with a new contract address) that overlaps with in-flight `send()` requests targeting that chain triggers this. Given that ISMP request timeouts can take a non-trivial window (finalization + relayer delay + configured timeout), and that asset/contract migrations are a normal operational activity for a bridge pallet, the race window is realistic and not contrived.

### Recommendation
Do not re-derive the asset mapping from live, mutable storage during `on_timeout` (or `on_accept`). Instead, embed the local `AssetId` (or an immutable snapshot of the mapping used at dispatch time) directly in the outgoing `Message`/request body so that timeout processing is self-contained and independent of subsequent `update_token` calls. Alternatively, retain historical `ContractToAsset` entries (e.g., a versioned/append-only map, or defer removal until all in-flight requests referencing the old contract have resolved) so that `on_timeout` for previously-dispatched requests can still resolve the correct asset and refund the sender.

### Proof of Concept
1. Register asset `A` (non-native) for destination chain `X` with contract address `C1` via `register_token`.
2. User calls `send()` for asset `A` to chain `X`; pallet burns the user's tokens and dispatches `PostRequest{ dest: X, to: C1, ... }`.
3. Admin (`CreateOrigin`) calls `update_token` with `remove_chains: [X]` for asset `A` (a legitimate migration/deprecation action), removing `TokenContracts::(X, A)` and `ContractToAsset::(X, C1)`.
4. The dispatched request times out (e.g., destination-side contract update or normal timeout).
5. ISMP core invokes `Pallet::<T>::on_timeout` with the original `PostRequest{ to: C1, dest: X, ... }`; `ContractToAsset::<T>::get(X, C1)` returns `None`, producing `HftError::UnknownContractOnTimeout` and reverting the refund.
6. The user's burned tokens from step 2 are never restored — permanent loss of principal.

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
