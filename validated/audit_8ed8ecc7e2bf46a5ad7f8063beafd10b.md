### Title
Governance updates to per-chain ERC20 `Precisions` can strand or lose escrowed funds for in-flight cross-chain transfers - (File: modules/pallets/hyper-fungible-token/src/lib.rs, modules/pallets/hyper-fungible-token/src/module.rs)

### Summary
`pallet-hyper-fungible-token` records a per-`(AssetId, StateMachine)` decimal precision (`Precisions`) used to scale amounts between the local chain and the EVM counterpart. `send()` converts the user's locked/burned local amount into the ERC20-denominated amount using the `Precisions` value **read at dispatch time**, and that scaled amount is baked into the outgoing ISMP `Message`. However, `on_timeout()` and `on_accept()` re-derive the local amount from the message by reading `Precisions` **again, at delivery/timeout time** [1](#0-0) . If a privileged `CreateOrigin`/governance call updates a chain's decimals via `register_token`/`update_token` between when a user calls `send()` and when the corresponding timeout or inbound message is processed, the amount conversion uses a different (new) decimals value than the one used to compute the original escrowed/burned amount, producing a mismatched refund/mint on the local chain and permanently stranding part of a user's funds — the same "divisibility/precision drift after a parameter change" bug class described in the external report for `LOT_SIZE_UNITS`.

### Finding Description
`send()` looks up `erc_decimals` from `Precisions::<T>::get(params.asset_id, params.destination)` at call time, locks/burns `params.amount` of the local asset, and scales it into an ERC20 `U256` amount using `convert_to_erc20(amount, erc_decimals, decimals)` [2](#0-1) . That `erc20_amount` — computed from the *decimals in effect at send time* — is the only value carried in the dispatched `Message`; the pallet does not persist which `erc_decimals` were used for this specific transfer.

Both the timeout handler and the accept handler re-derive the local amount from the same message by calling `convert_to_balance`, but they fetch `erc_decimals` fresh from storage at that later point in time:

```
let erc_decimals = Precisions::<T>::get(local_asset_id.clone(), dest)
    .ok_or(HftError::DecimalsNotConfigured(dest))?;
let amount = convert_to_balance::<...>(
    U256::from_big_endian(&message.amount.to_be_bytes::<32>()),
    erc_decimals,
    decimals,
)
``` [3](#0-2) 

`update_token` (call index 2) lets `CreateOrigin` add chain configs, including a new `config.decimals`, for an already-registered asset at any time, with no check against or migration of amounts already escrowed under the old decimals value [4](#0-3) . `convert_to_balance` divides by `10^(erc_decimals - local_decimals)` [5](#0-4) , so a change in `erc_decimals` between dispatch and delivery/timeout scales the recovered local amount by a different power of ten than was used to escrow it originally — exactly the "parameter changed mid-flight, existing committed amount computed under the old parameter is no longer consistent" failure described in the report, here manifesting as fund loss/mismatch on refund (timeout) or on mint (accept) for any user (an unprivileged token bridger) whose `send()` transaction straddles a governance precision update.

### Impact Explanation
Any in-flight `send()` whose timeout or delivery is processed after a legitimate `update_token`/`register_token` precision change will refund/mint an amount computed against the *wrong* decimals — either under-refunding the sender on timeout (funds permanently stuck, since escrow was already debited at send time) or over/under-crediting the beneficiary on delivery. This is a fund-loss/fund-freezing bug reachable by any ordinary user who dispatches a `send()` extrinsic — no malicious actor is required, only a routine parameter update racing against normal cross-chain latency (the same "not malicious admin, just careless parameter update" framing as the source report). Given it can permanently lock/misdirect user principal on a token bridge mint/burn path, this is Medium-severity.

### Likelihood Explanation
Likelihood is Medium: it requires a `Precisions` update for a chain that already has in-flight transfers pending (a real operational scenario, e.g. decimals correction or supporting a new representation), combined with normal ISMP delivery/timeout latency. Given that ISMP messages can take a nontrivial window to finalize or time out, and precision/decimals updates are a documented, expected maintenance operation (`update_token`), the race window is realistic rather than contrived.

### Recommendation
Persist the `erc_decimals` used at `send()` time keyed by the request commitment (or embed it in the dispatched message/timeout-refund path) so `on_timeout` and `on_accept` always convert using the same decimals that were used to compute the original escrowed amount, rather than re-reading current `Precisions` storage. Alternatively, disallow decimals changes for a chain while requests dispatched under the old decimals are still outstanding, or provide a migration path that reconciles already-escrowed balances before allowing the update.

### Proof of Concept
1. Register asset `X` with `Precisions[X][EVM-1] = 18`.
2. User calls `send({asset_id: X, destination: EVM-1, amount: 100})`; pallet locks 100 units and computes `erc20_amount = convert_to_erc20(100, 18, local_decimals)` baked into the ISMP `Message`, then dispatches it.
3. Before the request is finalized/timed out, governance calls `update_token` to change `Precisions[X][EVM-1]` to `6`.
4. The request times out; `on_timeout` reads the *current* `Precisions[X][EVM-1] = 6` and calls `convert_to_balance(message.amount, 6, local_decimals)`, which divides by a different power of ten than the `18` used at send time, yielding a refund amount inconsistent with the 100 units originally escrowed — the sender receives either far less or far more than was locked, with the discrepancy either lost from escrow (permanently unaccounted for) or drawn from other users' escrowed balances.

### Citations

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

**File:** modules/pallets/hyper-fungible-token/src/lib.rs (L251-302)
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

**File:** modules/pallets/hyper-fungible-token/src/impls.rs (L43-52)
```rust
pub fn convert_to_balance<B: core::str::FromStr>(
	value: U256,
	erc_decimals: u8,
	local_decimals: u8,
) -> Result<B, B::Err> {
	let dec_str = (value /
		U256::from(10u128.pow(erc_decimals.saturating_sub(local_decimals) as u32)))
	.to_string();
	dec_str.parse::<B>()
}
```
