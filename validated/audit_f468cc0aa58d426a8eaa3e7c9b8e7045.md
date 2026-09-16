## Title
Removing a chain from `pallet-hyper-fungible-token` while a cross-chain transfer is in-flight permanently blocks the timeout refund path, locking (or destroying, for burned assets) user funds — (File: `modules/pallets/hyper-fungible-token/src/lib.rs`)

### Summary
`pallet-hyper-fungible-token::update_token` lets `CreateOrigin` remove a chain's token configuration (`TokenContracts`, `ContractToAsset`, `Precisions`) for an asset at any time, with no check for outstanding in-flight requests to that chain. If a user already called `send()` to that chain (locking or burning their tokens) before the removal, and the request later times out, `on_timeout` cannot resolve the required lookups and fails permanently — the escrow can never be refunded through the pallet's only reversion path.

### Finding Description
`send()` locks (native asset) or burns (non-native asset) the caller's tokens and dispatches a `DispatchPost` to the destination chain/contract recorded in `TokenContracts`/`ContractToAsset`/`Precisions`: [1](#0-0) 

The only way to reverse this state change is `IsmpModule::on_timeout`, which re-derives the local asset from `ContractToAsset::<T>::get(dest, &to)` and the decimals from `Precisions`: [2](#0-1) 

`update_token` (callable by `CreateOrigin`, a governance/admin-style origin, but intended for routine migrations such as rotating a contract address or decommissioning a chain) deletes exactly these entries for `remove_chains`, with no guard for pending requests: [3](#0-2) 

If this call executes for a `(chain, asset)` pair that still has an outstanding `send()` in flight (dispatched, not yet delivered/acked), a later timeout for that same request calls `on_timeout`, which fails with `HftError::UnknownContractOnTimeout` because `ContractToAsset` no longer has the `(dest, to)` entry.

Per the ISMP timeout handler design, when `IsmpModule::on_timeout` returns an error, the request commitment is *not* deleted, allowing the timeout to be retried later: [4](#0-3) [5](#0-4) 

This "retry later" model only helps if the failure is transient. Here it is not: the exact `(dest, old_contract)` mapping was permanently removed by `update_token`, so every retry of the timeout will hit the same `UnknownContractOnTimeout` error forever, unless an operator manually re-inserts the deleted historical contract mapping — which defeats the purpose of the removal (e.g. decommissioning a compromised or superseded contract) and is not exposed as any documented recovery procedure.

For non-native assets this is worse than a temporary lock: `send()` already executed `burn_from` on the user's tokens, so once the timeout path is permanently blocked the supply reduction is never reversed — the user's tokens are destroyed with no compensating credit.

This mirrors the referenced UXD `unregisterDepository` bug precisely: a privileged "unregister"/"remove" action deletes the bookkeeping needed to later settle funds that were already committed against the entity being removed, and the protocol provides no other path to reach those funds.

### Impact Explanation
Any in-flight `send()` to a chain that is later removed via `update_token(remove_chains)` becomes permanently unrefundable through the pallet's own logic. For native assets, funds are frozen in the pallet's custody account with no way to reach the depositor. For non-native assets, funds are irrecoverably burned. This is a direct, unbacked loss of user funds triggered by a normal governance/admin lifecycle operation (chain/contract migration or deprecation) combined with ordinary user activity, not a malicious actor abusing the origin.

### Likelihood Explanation
`CreateOrigin` calls to `update_token` for maintenance (rotating a compromised contract address, adjusting decimals, discontinuing support for a chain) are a documented, expected part of pallet operation. Any user transaction dispatched shortly before such an update, that subsequently times out (network congestion, relayer unavailability, destination chain issues) will hit this condition. No attacker coordination is required — it is a straightforward TOCTOU race between routine configuration changes and normal cross-chain traffic.

### Recommendation
Before removing a chain's `TokenContracts`/`ContractToAsset`/`Precisions` entries in `update_token`, either:
1. Track outstanding request commitments per `(dest, asset)` pair and refuse removal while any are pending, or
2. Retain the old `ContractToAsset`/`Precisions` mapping in a secondary "retired" store that `on_timeout` (and `on_accept`, if relevant) can still consult, so in-flight requests can always be settled even after the active configuration is updated/removed.

### Proof of Concept
1. Governance registers asset `A` for `StateMachine::Evm(X)` with contract `C1` via `register_token`.
2. A user calls `send()` for asset `A` to `StateMachine::Evm(X)`; their tokens are escrowed (native) or burned (non-native), and a `DispatchPost` referencing `to = C1` is created with some `timeout`.
3. Before the request is delivered or times out, governance calls `update_token` with `remove_chains: [StateMachine::Evm(X)]` for asset `A` (e.g. rotating to a new contract `C2` via `add_chains`, or fully deprecating chain `X`). This removes `ContractToAsset[(X, C1)]` and `Precisions[(A, X)]`.
4. The destination never processes the request within `timeout`; a relayer submits a `TimeoutMessage::Post` for it.
5. `pallet-ismp`'s timeout handler invokes `HyperFungibleToken::on_timeout`, which calls `ContractToAsset::<T>::get(X, C1)` — now `None` — and returns `HftError::UnknownContractOnTimeout`.
6. Per `modules/ismp/core/src/handlers/timeout.rs`, the failed callback causes the commitment to be restored/kept rather than deleted, so the timeout is retryable — but every future retry fails identically, since the deleted mapping is never restored. The user's escrowed/burned funds are never returned.

### Citations

**File:** modules/pallets/hyper-fungible-token/src/lib.rs (L257-290)
```rust
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

**File:** modules/ismp/core/src/handlers/timeout.rs (L113-134)
```rust
					let res = cb.on_timeout(request.clone()).map(|weight| {
						total_module_weight.saturating_accrue(weight);
						let commitment = hash_request::<H>(&request);
						Event::PostRequestTimeoutHandled(TimeoutHandled {
							commitment,
							source: post.source,
							dest: post.dest,
						})
					});
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

**File:** docs/content/protocol/ismp/timeouts.mdx (L55-58)
```text
- Finally dispatch the timeouts to the relevant `IsmpModule::on_timeout` and delete the commitments for the outgoing messages.

<Callout title={'Danger'} type={"warn"}>
It's important to note that if the `IsmpModule::on_timeout` does not return `Ok`, the commitment of the relevant messages will not be deleted, allowing the timeout to be **replayed**. Consequently, the `IsmpModule` is responsible for maintaining all invariants before modifying it's internal state to prevent partial state changes that could result in critical vulnerabilities in their timeout handler. This model ensures that if a timeout cannot be executed successfully, it can be retried later.
```
