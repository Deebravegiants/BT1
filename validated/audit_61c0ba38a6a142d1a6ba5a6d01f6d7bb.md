## Title
Updating a `HyperFungibleToken` chain's contract address orphans in-flight transfers, permanently freezing/destroying escrowed and burned funds - (File: `modules/pallets/hyper-fungible-token/src/lib.rs`, `modules/pallets/hyper-fungible-token/src/module.rs`)

### Summary
`pallet-hyper-fungible-token`'s `update_token` extrinsic lets `CreateOrigin` change (or remove) the EVM contract address configured for a chain. Doing so deletes the `ContractToAsset` reverse-mapping for the old contract address before inserting the new one. Any `send()` transfer that was dispatched to the old address and is still in flight when the update happens can never be resolved by `on_timeout`, because `on_timeout` looks up the asset via that exact reverse mapping using the address embedded in the original request. The lookup fails, the timeout call reverts, and the user's escrowed (or already-burned) funds can never be recovered — the same "switching vault token strands existing balances" bug class as the referenced Sherlock report, but here it destroys funds outright for non-native (burn/mint) assets.

### Finding Description
`send()` escrows native-custody assets or burns non-native assets, then dispatches a `DispatchPost` whose `to` field is the token contract address read from `TokenContracts` at dispatch time: [1](#0-0) 

If the request later times out, `on_timeout` must locate the local asset to refund the original sender. It does so purely via `ContractToAsset::<T>::get(dest, &to)`, where `to` is the contract address recorded in the original (already-dispatched, content-addressed) request: [2](#0-1) 

`update_token`, callable at any time by `CreateOrigin`, updates a chain's `token_contract`. For every added/updated chain it first removes the *old* reverse mapping and then inserts the mapping for the new contract, and for removed chains it deletes the mapping entirely: [3](#0-2) 

Because ISMP requests are content-addressed, an in-flight `send()` dispatched before the update permanently carries the *old* contract address as its `to`/`dest` pair. If `update_token` runs before that request is delivered or times out, `ContractToAsset::get(dest, &old_contract)` returns `None`, and `on_timeout` reverts with `UnknownContractOnTimeout` instead of refunding the sender. The confirmatory test only exercises `update_token`'s storage effects in isolation and never checks in-flight-transfer safety: [4](#0-3) 

### Impact Explanation
- For non-native assets, `send()` already **burned** the user's tokens before dispatch; if the timeout can no longer resolve the asset via the stale reverse mapping, the mint-back in `on_timeout` never executes, so the burned value is unrecoverable — a permanent loss of user funds.
- For native (escrow) assets, the funds sit in `Pallet::pallet_account()` custody with no code path to force a match against the new mapping; they are effectively frozen with no recovery mechanism, since `on_timeout` is the pallet's only refund path.
- This is triggerable by an ordinary user's single unprivileged `send()` extrinsic combined with a routine (non-malicious) `update_token` maintenance/migration call — exactly the "switching vault token" bug class from the reference report, reachable through the token bridge's ordinary mint/burn and timeout-refund accounting.

### Likelihood Explanation
`update_token` is a normal, expected operational call (e.g. redeploying/upgrading the paired EVM `HyperFungibleToken` contract, or reconfiguring decimals), not an attack. Any timing overlap between in-flight `send()` requests and a legitimate `update_token` call for the same `(chain, asset)` pair — which is plausible during any contract migration on a busy bridge — triggers the bug. No malicious actor is required.

### Recommendation
Do not immediately delete the old `ContractToAsset` entry when updating a chain's contract address. Instead, retain historical contract→asset mappings (e.g., keep prior entries alive until all pending requests referencing them have resolved, or resolve `on_timeout`/`on_accept` by `(local asset, chain)` metadata embedded in the request rather than solely by current reverse-address lookup), or block `update_token` from repointing/removing a chain's contract while requests dispatched to the old address are still outstanding.

### Proof of Concept
1. Admin registers asset `X` for `StateMachine::Evm(1)` with `token_contract = A` via `register_token` — `TokenContracts[(Evm(1), X)] = A`, `ContractToAsset[(Evm(1), A)] = X`.
2. User calls `send()` for asset `X` to `Evm(1)`; funds are escrowed/burned and a `DispatchPost{ to: A, dest: Evm(1), ... }` is dispatched (see `send()` at lines 251-310).
3. Before the request is delivered, admin calls `update_token` to migrate the EVM contract to address `B` (e.g. contract redeploy): `ContractToAsset::remove(Evm(1), A)` runs, then `ContractToAsset::insert(Evm(1), B, X)` (lines 398-421).
4. The original request eventually times out. `pallet-ismp` invokes `on_timeout` with `to = A, dest = Evm(1)`. `ContractToAsset::get(Evm(1), A)` now returns `None`, so `on_timeout` errors with `UnknownContractOnTimeout` (module.rs lines 236-237) and the escrowed/burned funds are never refunded to the user.

### Citations

**File:** modules/pallets/hyper-fungible-token/src/lib.rs (L251-310)
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
```

**File:** modules/pallets/hyper-fungible-token/src/lib.rs (L398-430)
```rust
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

**File:** modules/pallets/testsuite/src/tests/pallet_hyper_fungible_token.rs (L233-252)
```rust
		// Update: remove chain
		let update = TokenUpdate {
			asset_id,
			add_chains: BTreeMap::new(),
			remove_chains: vec![StateMachine::Evm(42)],
		};

		HyperFungibleToken::update_token(RuntimeOrigin::signed(ALICE), update).unwrap();

		assert!(pallet_hyper_fungible_token::TokenContracts::<Test>::get(
			StateMachine::Evm(42),
			asset_id
		)
		.is_none());
		assert!(pallet_hyper_fungible_token::ContractToAsset::<Test>::get(
			StateMachine::Evm(42),
			&contract
		)
		.is_none());
	});
```
