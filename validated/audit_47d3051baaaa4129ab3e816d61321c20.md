### Title
Stale/mutable per-chain decimals cause incorrect refund and mint amounts in `pallet-hyper-fungible-token` - (File: `modules/pallets/hyper-fungible-token/src/lib.rs`, `modules/pallets/hyper-fungible-token/src/module.rs`)

### Summary
`pallet-hyper-fungible-token` stores per-`(AssetId, StateMachine)` ERC20 decimal precision in the mutable `Precisions` map. `send()` encodes the cross-chain ERC20 amount using the *current* value of `Precisions` at dispatch time, but the amount itself is not stored with the decimals used to encode it. When the counterpart chain later delivers (`on_accept`) or the request times out (`on_timeout`), the pallet re-reads `Precisions` *at that later time* to decode the same raw ERC20 amount back into local balance units. If `Precisions` was updated (via `update_token`) in between, the decode step misinterprets the ERC20 amount using the wrong decimal base — exactly the same bug class as the reported `FantiumClaimingV1` issue, where amounts stored for "the current token's decimals" become wrong once decimals change later.

### Finding Description
- `send()` reads `erc_decimals = Precisions::<T>::get(asset_id, destination)` and encodes the outgoing ERC20 amount with `convert_to_erc20(amount, erc_decimals, local_decimals)`: [1](#0-0) 
- `update_token` lets `CreateOrigin` freely overwrite `Precisions` for an already-configured chain (`add_chains` re-inserts into `Precisions::<T>::insert(...)`), with no restriction tied to in-flight requests: [2](#0-1) 
- `on_accept` decodes the inbound message's raw ERC20 `amount` by looking up `Precisions::<T>::get(local_asset_id, source)` *at delivery time*, not the value that was in effect when the counterpart contract encoded it: [3](#0-2) 
- `on_timeout` does the same for the refund path, re-reading `Precisions::<T>::get(local_asset_id, dest)` at timeout-processing time to decode the amount originally encoded by `send()`: [4](#0-3) 

Because the raw `message.amount` (an ERC20 `U256`) is committed into the dispatched/committed request body once and never re-scaled, any decimals change between dispatch and eventual `on_accept`/`on_timeout` processing causes `convert_to_balance` to apply the wrong scaling factor to a value that was fixed under the old scaling — mirroring the reported bug where `DistributionEvent.totalTournamentEarnings`/`totalOtherEarnings` are computed under one decimals assumption but consumed later under a different one.

### Impact Explanation
- If decimals are decreased after `send()` but before `on_timeout`/`on_accept` (e.g. `18 → 6`), `convert_to_balance` divides by a much larger `10^(erc_decimals-local_decimals)` than intended, rounding the refunded/minted local balance down to near-zero — a user's escrowed/burned tokens become **permanently unrecoverable** (freezing of funds).
- If decimals are increased (e.g. `6 → 18`), the division factor shrinks, causing the pallet to refund/mint **far more** local balance than was ever escrowed/burned — an **unbacked mint** that can drain the escrow account (`pallet_account()`) backing the native/non-native asset, since e.g. `BridgeToken.sol` on the EVM side explicitly documents that its supply is "always backed by the pallet's escrow account".
- Both outcomes are direct fund-safety violations reachable through the pallet's normal, unprivileged `send()` extrinsic combined with a subsequent `update_token` reconfiguration and the standard timeout/accept delivery flow — no malicious admin action is required, only an ordinary decimals correction/migration performed while requests are in flight.

### Likelihood Explanation
`update_token` is a routine, expected operation (e.g. correcting a misconfigured `config.decimals`, or migrating a token to a new EVM contract with different decimals) rather than an attack requiring compromised governance. Any in-flight `send()` request that has not yet been accepted or timed out at the moment `update_token` changes `Precisions` for that `(asset, chain)` pair will be settled with the wrong scaling factor. Given that cross-chain settlement latency (timeout windows, relayer delays) is measured in blocks-to-hours, and decimals updates are a plausible maintenance action, the race window is realistic, not contrived.

### Recommendation
Snapshot the decimals used to encode an outgoing amount alongside the in-flight commitment (e.g., embed `erc_decimals`/`local_decimals` in the request body, or store them keyed by the request commitment) so that `on_accept` and `on_timeout` decode using the same precision that was used at `send()` time, rather than re-reading the potentially-mutated `Precisions` map. Alternatively, disallow `update_token` from mutating decimals for a chain while there are outstanding undelivered/untimed-out requests referencing that `(asset, chain)` pair.

### Proof of Concept
1. Register asset `X` (local decimals = 6) for chain `A` with `Precisions[X][A] = 6` via `register_token`.
2. User calls `send({ asset_id: X, destination: A, amount: 100_000000 })` (100 tokens). `send()` reads `erc_decimals = 6`, computes `erc20_amount = convert_to_erc20(100_000000, 6, 6) = 100_000000`, and dispatches a `Message{ amount: 100_000000 }` to chain `A`. [5](#0-4) 
3. Before delivery/timeout resolves, governance calls `update_token` to re-register chain `A` for asset `X` with `config.decimals = 18` (e.g., a legitimate decimals fix), overwriting `Precisions[X][A] = 18`.
4. The original request times out. `on_timeout` re-reads `Precisions::get(X, A) = 18` and calls `convert_to_balance(100_000000, erc_decimals=18, local_decimals=6)`, dividing by `10^(18-6) = 10^12`, yielding `0`. The user's escrowed 100 tokens are refunded as `0` — permanently lost. [6](#0-5) 
5. Conversely, swapping the before/after decimals values (`18 → 6`) in the same scenario causes `convert_to_balance` to multiply instead of correctly scale, refunding/minting drastically more than was ever escrowed, draining `pallet_account()`.

### Citations

**File:** modules/pallets/hyper-fungible-token/src/lib.rs (L254-316)
```rust
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
				.map_err(|_| Error::<T>::DispatchError)?;

```

**File:** modules/pallets/hyper-fungible-token/src/lib.rs (L398-421)
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
```

**File:** modules/pallets/hyper-fungible-token/src/module.rs (L74-91)
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
```

**File:** modules/pallets/hyper-fungible-token/src/module.rs (L239-291)
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

				Pallet::<T>::deposit_event(Event::<T>::TokenRefunded {
					beneficiary,
					amount: amount.into(),
					dest,
				});
```
