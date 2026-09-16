Found the analog: `on_timeout` in the `pallet-hyper-fungible-token` ISMP module depends on `ContractToAsset` / `Precisions` storage entries that `update_token` can delete for a chain that still has in-flight (undelivered) requests, causing the timeout refund path to permanently fail and freeze the escrowed/burned amount.

### Title
Removing a chain/asset config via `update_token` while a cross-chain transfer is in-flight permanently freezes the sender's escrowed or burned funds on timeout - (File: `modules/pallets/hyper-fungible-token/src/lib.rs`, `modules/pallets/hyper-fungible-token/src/module.rs`)

### Summary
`send()` in the `hyper-fungible-token` pallet locks (native asset) or burns (non-native asset) a user's tokens and dispatches a cross-chain `Post` request to a `token_contract` on the destination chain, keyed by `(dest, asset_id)` in `TokenContracts`/`ContractToAsset`/`Precisions` storage [1](#0-0) . If the privileged `CreateOrigin` later calls `update_token` to remove that chain from the asset's configuration (e.g. rotating to a new contract, decommissioning a chain, or correcting a misconfiguration), it deletes the `ContractToAsset` and `Precisions` entries for that `(chain, asset_id)` pair unconditionally, with no check for requests still in flight [2](#0-1) . If the original request never gets delivered and instead times out, `on_timeout` looks up the local asset via `ContractToAsset::<T>::get(dest, &to)` and the decimals via `Precisions::<T>::get(local_asset_id, dest)`; both are now missing, so the call returns `HftError::UnknownContractOnTimeout` / `HftError::DecimalsNotConfigured` and reverts before the refund transfer executes [3](#0-2) .

### Finding Description
This is directly analogous to the reported UXDController bug class: an admin action (removing an asset/chain from a whitelist-like registry) that is legitimate in isolation, but strands funds that were already escrowed/burned under the old configuration because the withdrawal/refund path is gated on the same registry entry the admin just removed.

In `send()`, the sender's funds are moved out of their control immediately (locked into the pallet's custody account for native assets, or burned outright for non-native assets), before the cross-chain message is ever delivered [4](#0-3) . The only path back to the user if delivery never completes is `on_timeout`, called by `pallet-ismp` once the request's timeout has elapsed. That refund path re-derives the asset and decimals purely from `ContractToAsset` and `Precisions`, keyed by `(dest, to)`/`(asset_id, dest)` [5](#0-4) . `update_token`'s `remove_chains` loop deletes exactly these entries with no check of whether any requests to that chain for that asset are still outstanding [2](#0-1) .

Consequently, for any `send()` call whose request has not yet been delivered or timed out at the moment `update_token` removes that chain, the eventual timeout callback will fail to look up the asset/decimals and error out, leaving the burned tokens permanently destroyed (non-native case) or the locked native/asset tokens permanently stuck in the pallet's custody account (native case), since the same storage lookup gates the refund with no fallback recovery mechanism.

### Impact Explanation
This is a permanent freezing-of-funds bug reachable by an ordinary user's own `send` transaction combined with a routine, expected admin operation (`update_token` to rotate/decommission a chain's contract address). For non-native assets, user funds are irrecoverably burned with no possibility of reissue since the mint side (`on_timeout`'s mint branch) can never run once the lookup fails. For native assets, funds sit locked in the pallet account permanently, since there is no other extrinsic that can release funds keyed by an already-deleted `(dest, asset_id)` pair. This matches the required bar of concrete permanent freezing/loss of user funds.

### Likelihood Explanation
Likelihood is realistic: `update_token` with `remove_chains` is an expected, documented pallet operation (README describes it as "Add or remove chains from an existing token's configuration") [6](#0-5) , and cross-chain message timeouts are a normal occurrence in ISMP (finality delays, relayer failures, congestion). Any window between a `send()` call and its request's delivery/timeout during which the operator removes that chain from the asset config triggers the bug — this requires no malicious actor, just ordinary operational timing.

### Recommendation
Before removing a chain from `TokenContracts`/`ContractToAsset`/`Precisions` in `update_token`, either (a) require confirmation that no `Post` requests are still pending for that `(dest, asset_id)` pair, or (b) preserve the removed `ContractToAsset`/`Precisions` entries in a secondary "retired" mapping that `on_timeout` can still consult, so in-flight refunds can always complete even after the live configuration changes. Alternatively, encode the asset ID and decimals directly into the outgoing request body/context at `send()` time so that `on_timeout` does not need to re-derive them from possibly-mutated live storage.

### Proof of Concept
1. Operator registers asset `X` for chain `Evm(1)` via `register_token`, setting `TokenContracts[(Evm(1), X)]`, `ContractToAsset[(Evm(1), contract)]`, `Precisions[(X, Evm(1))]` [7](#0-6) .
2. User calls `send(params)` with `asset_id = X`, `destination = Evm(1)`; tokens are burned (or locked) and a `DispatchPost` is created with a timeout `T` [8](#0-7) .
3. Before the request is delivered, operator calls `update_token` with `remove_chains = [Evm(1)]` for asset `X` (e.g. to rotate to a new contract address) — this deletes `ContractToAsset[(Evm(1), contract)]` and `Precisions[(X, Evm(1))]` [2](#0-1) .
4. The request times out; `pallet-ismp` invokes `on_timeout`, which calls `ContractToAsset::<T>::get(dest, &to)` — now `None` — causing `HftError::UnknownContractOnTimeout` and the refund transfer never executes [9](#0-8) .
5. The user's burned/locked tokens are permanently unrecoverable.

### Citations

**File:** modules/pallets/hyper-fungible-token/src/lib.rs (L251-314)
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
```

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

**File:** modules/pallets/hyper-fungible-token/README.md (L53-53)
```markdown
| `update_token(update)` | `CreateOrigin` | Add or remove chains from an existing token's configuration. |
```
