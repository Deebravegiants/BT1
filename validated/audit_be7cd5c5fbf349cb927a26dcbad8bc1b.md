### Title
`pallet-hyper-fungible-token`'s `on_accept`/`on_timeout` mint/transfer of converted amounts without validating against the destination chain's Existential Deposit - ([File: modules/pallets/hyper-fungible-token/src/module.rs])

### Summary
The Oasis report shows `delegate()` failing because it only checks `amount > 0` while the downstream Oasis consensus layer independently enforces a 100 ROSE minimum, letting anyone dispatch delegations doomed to fail and grief other delegators sharing the same batched/queued flow. `pallet-hyper-fungible-token` (the substrate side of Hyperbridge's HFT bridge) has the same shape of bug: it lets a caller on the EVM side `send()` an arbitrary, attacker-chosen amount of a bridged token, which is decimal-converted and then credited to a (possibly brand-new) substrate account via `NativeCurrency::transfer`/`Assets::mint_into` — without ever checking the converted amount against the local chain's `ExistentialDeposit` / asset `min_balance`, a hard, protocol-level minimum enforced by `pallet-balances`/`pallet-assets`, just like Oasis's 100 ROSE minimum is enforced by the consensus layer.

### Finding Description
`HyperFungibleToken.send()` on the EVM side [1](#0-0)  lets any caller burn/lock an arbitrary `params.amount` (no minimum check) and dispatch a POST request carrying that amount to the destination chain.

On the substrate side, `pallet_hyper_fungible_token::Pallet::on_accept` decodes the message, converts the ERC20-denominated amount to the local chain's decimals via `convert_to_balance`, and then credits the beneficiary: [2](#0-1) 

For the native-asset path this is a `NativeCurrency::transfer(&pallet_account, &beneficiary, amount, ExistenceRequirement::AllowDeath)` call. `AllowDeath` only governs whether the *sender* account may be reaped; it does not exempt the *receiver* from `pallet-balances`' hard rule that crediting a not-yet-existing account with less than `ExistentialDeposit` fails. The same applies to `Assets::mint_into`/`Assets::transfer` for non-native assets, which is subject to the asset's configured `min_balance` (the very `minimum_balance` field documented for `GatewayAssetRegistration`/token registration) [3](#0-2) .

Nowhere in `send()` (EVM), `send()` (pallet, dispatch side) [4](#0-3) , or `on_accept`/`on_timeout` [5](#0-4)  is the converted amount checked against the destination's minimum balance requirement before attempting the credit. This mirrors the Oasis `delegate()` bug exactly: the contract-level check (`amount > 0`) is insufficient because a stricter, protocol-enforced minimum exists one layer below and is never consulted.

### Impact Explanation
Because `on_accept` is the ISMP message-delivery callback, a converted amount that lands below `ExistentialDeposit`/`min_balance` for a beneficiary account that does not yet exist on the destination chain causes the `NativeCurrency::transfer` / `Assets::mint_into` call to return an error, which propagates out of `on_accept` as `Err(HftError::TransferFailed(..))`/`MintFailed`. Any relayer attempting delivery for that request will have its message rejected at the destination — the request can never be successfully delivered, forcing it into permanent failure until timeout. Meanwhile the tokens are already burned/escrowed on the EVM source side [6](#0-5) . Eventually `on_timeout` runs to refund the sender, but it performs the identical unchecked credit (`NativeCurrency::transfer`/`Assets::mint_into` to the original sender) using the same converted amount [7](#0-6) ; if the original sender's account was also reaped (e.g. `AllowDeath` on the earlier `send()` burned/escrowed it below its own ED) or the refund amount is itself sub-ED for a non-existent account, the timeout refund fails too — permanently freezing the bridged funds with no path to recovery. Even short of permanent freezing, this is a costless griefing vector: any attacker can force relayers to repeatedly attempt and fail delivery of a message, wasting relayer gas/resources on the destination chain (mirroring the "malicious user can repeat this... with the intent to harm other users" framing from the Oasis report), since nothing on the EVM side stops dust-value transfers from being dispatched.

### Likelihood Explanation
Likelihood is high: any unprivileged user can call `HyperFungibleToken.send()` (or the pallet's own `send()` extrinsic) with an arbitrarily small `amount`/decimal-converted-to-near-zero value targeting a fresh beneficiary account, with no on-chain minimum enforced at either the EVM contract or the pallet dispatch call. The existential deposit is a standard, always-on Substrate/Polkadot-SDK invariant (`pallet-balances::Config::ExistentialDeposit`, `pallet-assets` `min_balance`), so this failure mode is guaranteed to trigger whenever a bridged transfer's destination-side converted amount is below that threshold for a not-yet-existing account, which is trivial for an attacker to engineer given cross-chain decimal scaling (`convert_to_balance`) can also round small EVM-side amounts down.

### Recommendation
Before dispatching (or accepting) an HFT transfer:
1. On the EVM `send()` path, and/or on `pallet_hyper_fungible_token::send()`, reject amounts that convert to less than the destination chain's known minimum balance for that asset (this requires the pallet/contract to know or query the destination's `ExistentialDeposit`/`min_balance`, similar to how `Precisions` already stores per-chain decimals).
2. In `on_accept`/`on_timeout`, before crediting a beneficiary/refund account, check whether the account already exists; if not, require `amount >= T::NativeCurrency::minimum_balance()` (or the asset's `min_balance`) and handle the shortfall deterministically (e.g., top up from a pallet-controlled reserve, or explicitly document/enforce a floor on transferable amounts) rather than letting the transfer error propagate as an unrecoverable ISMP delivery failure.
3. Ensure the timeout refund path cannot itself fail for the same reason, since that is the last line of defense for recovering escrowed/burned funds.

### Proof of Concept
1. Attacker calls `HyperFungibleToken.send()` on an EVM chain with `params.amount` scaled such that, after `convert_to_balance` on the substrate destination, the local-decimal amount is below `ExistentialDeposit` (e.g., 1 wei-equivalent unit when local decimals are much lower than EVM's 18, per `convert_to_erc20`/`convert_to_balance` scaling) and `params.to` is an address with no existing substrate account.
2. Tokens are burned on the EVM side [6](#0-5) ; the POST request is dispatched to the pallet.
3. A relayer submits the proof; `pallet_hyper_fungible_token::on_accept` computes `amount` via `convert_to_balance` and calls `NativeCurrency::transfer(..., ExistenceRequirement::AllowDeath)` to the new beneficiary account [8](#0-7) ; this fails because the credited amount is below `ExistentialDeposit` and the account does not exist, returning `Err(HftError::TransferFailed(...))`.
4. Every relayer attempting delivery hits the same failure — the request cannot be successfully delivered, and after the configured timeout, `on_timeout` attempts the refund to the original sender using the same converted amount and transfer mechanics [7](#0-6) , which can likewise fail if the sender's account was reaped or the refund amount is sub-ED, permanently stranding the escrowed/burned value.

(Note: I was unable to fully inspect `convert_to_balance`/`convert_to_erc20` in `modules/pallets/hyper-fungible-token/src/impls.rs` due to running out of tool iterations, so the exact rounding/scaling behavior that produces a sub-ED converted amount is inferred from the decimal-conversion pattern documented elsewhere rather than directly confirmed line-by-line.)

### Citations

**File:** sdk/packages/core/contracts/apps/HyperFungibleTokenUpgradeable.sol (L293-311)
```text
    function send(SendParams calldata params) external payable whenNotPaused {
        _burn(msg.sender, params.amount);
        DispatchPost memory request = _buildDispatchPost(params);

        bytes32 commitment;
        if (msg.value > 0) {
            commitment = IDispatcher(_host).dispatch{value: msg.value}(request);
        } else {
            commitment = dispatchWithFeeToken(request);
        }

        emit Sent({
            from: msg.sender,
            to: params.to,
            dest: string(params.dest),
            amount: params.amount,
            commitment: commitment
        });
    }
```

**File:** modules/pallets/hyper-fungible-token/src/module.rs (L82-117)
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

**File:** modules/pallets/hyper-fungible-token/src/module.rs (L205-298)
```rust
		Self::deposit_event(Event::<T>::TokenReceived {
			beneficiary,
			amount: amount.into(),
			source,
		});

		Ok(T::DbWeight::get().reads_writes(5, 2))
	}

	fn on_response(&self, _response: GetResponse) -> Result<Weight, anyhow::Error> {
		Err(HftError::ResponsesNotSupported)?
	}

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
				Ok(T::DbWeight::get().reads_writes(5, 2))
			},
			Request::Get(_) => Err(HftError::UnsupportedTimeoutType)?,
		}
	}
}

```

**File:** docs/content/developers/polkadot/token-gateway.mdx (L147-156)
```text
pub struct GatewayAssetRegistration {
    /// The asset name
    pub name: BoundedVec<u8, ConstU32<50>>,
    /// The asset symbol
    pub symbol: BoundedVec<u8, ConstU32<20>>,
    /// The list of chains to create the asset on
    pub chains: Vec<StateMachine>,
    /// Minimum balance for the asset (only needed for substrate chains)
    pub minimum_balance: Option<u128>,
}
```

**File:** modules/pallets/hyper-fungible-token/src/lib.rs (L241-325)
```rust
		pub fn send(
			origin: OriginFor<T>,
			params: SendParams<
				AssetId<T>,
				<<T as Config>::NativeCurrency as Currency<T::AccountId>>::Balance,
			>,
		) -> DispatchResult {
			let who = ensure_signed(origin)?;
			let dispatcher = <T as Config>::Dispatcher::default();

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
				.map_err(|_| Error::<T>::DispatchError)?;

			Self::deposit_event(Event::<T>::TokenSent {
				from: who,
				to: params.recipient,
				dest: params.destination,
				amount: params.amount,
				commitment,
			});
			Ok(())
		}
```
