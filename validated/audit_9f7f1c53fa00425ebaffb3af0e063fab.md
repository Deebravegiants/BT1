### Title
Removing a chain from a token's configuration via `update_token` can permanently strand in-flight cross-chain transfers - (File: `modules/pallets/hyper-fungible-token/src/lib.rs`)

### Summary
`pallet-hyper-fungible-token::update_token` lets `CreateOrigin` delete a chain's `TokenContracts`/`ContractToAsset`/`Precisions` entries for an asset with no check for requests already dispatched to or from that chain. This mirrors the referenced `UXDRouter.unregisterDepository` issue: removing a routing/registry entry that still has live obligations breaks delivery for funds that are already committed, rather than reverting the removal until it is safe.

### Finding Description
`update_token` (`modules/pallets/hyper-fungible-token/src/lib.rs:384-433`) processes `remove_chains` unconditionally:

```
for chain in update.remove_chains {
    if let Some(old_contract) = TokenContracts::<T>::get(chain, update.asset_id.clone())
    { ContractToAsset::<T>::remove(chain, old_contract); }
    TokenContracts::<T>::remove(chain, update.asset_id.clone());
    Precisions::<T>::remove(update.asset_id.clone(), chain);
}
```
The same unconditional overwrite happens in the `add_chains` loop, which deletes the old `ContractToAsset` reverse mapping before installing the new one (lines 407-411).

`ContractToAsset` and `Precisions` are exactly the state `on_accept` needs to process an *incoming* EVM→Substrate transfer (per the pallet's own README: "`on_accept` — ... Maps the source contract back to a local asset via `ContractToAsset`, scales the amount using `Precisions`, then mints/releases..."). A counterpart `HyperFungibleToken`/`BridgeToken` EVM contract already burned/escrowed the user's tokens and dispatched a `PostRequest` before governance calls `update_token`. If that request is still unrelayed, or was relayed and rejected once and awaits retry, and governance removes the chain (or repoints the contract address) in the interim, the subsequent `on_accept` lookup on `ContractToAsset`/`Precisions` fails: the message can never be credited on the Substrate side. Unlike a host-level freeze which is meant to halt *new* traffic, this specific removal silently invalidates already-committed, already-burned value with no fallback path — the pallet does not check `TokenContracts::iter` for extant escrow/pending state before dropping the mapping, exactly the "revert if the target [route] has assets" gap flagged in the source report.

### Impact Explanation
Any inbound transfer that was dispatched (and had its source-side tokens burned/escrowed) but not yet delivered when governance updates the token's chain list becomes permanently undeliverable: `on_accept` cannot resolve `ContractToAsset`/`Precisions` for that chain/contract, so the mint/release never happens. If the underlying ISMP request has no timeout (or the timeout window elapses without delivery for unrelated relaying reasons), the source-side burned/escrowed tokens are unrecoverable — a permanent freeze/loss of user funds with no unprivileged remediation path. This satisfies the "permanent freezing of funds" impact bar.

### Likelihood Explanation
This requires an ordinary, non-malicious governance action (`update_token` re-pointing or removing a chain, e.g. to fix a misconfigured contract address or deprecate a peer) racing against a completely unprivileged user's cross-chain `send`. Given HFT/BRIDGE token deployments across multiple EVM chains and periodic contract migrations are a stated maintenance operation (see `update_token`/`register_token` docs), any transfer in flight during such an update is silently orphaned — a realistic and even likely occurrence, not an attacker-crafted edge case.

### Recommendation
Before removing or repointing a chain's `TokenContracts`/`ContractToAsset`/`Precisions` entry in `update_token`, either:
- require a grace/quarantine period during which the old mapping is still honored for `on_accept`, or
- keep the old `(chain, old_contract) -> asset_id` reverse mapping alive (instead of deleting it) so pending deliveries using the previous contract address still resolve, only removing it once no requests reference it, or
- gate governance updates behind an explicit safety check (e.g., an event-log/relayer attestation that no undelivered request targets the chain being removed) similar to the suggested fix of reverting the removal when the target still has outstanding obligations.

### Proof of Concept
1. Governance calls `register_token`/`update_token` registering asset `A` on `StateMachine::Evm(X)` with contract `C1`.
2. A user on chain `X` calls the counterpart `HyperFungibleToken`/`BridgeToken.send` function, burning/escrowing their tokens and dispatching a `PostRequest` (`from = C1`) destined for `pall_hft` on this chain.
3. Before the request is relayed and delivered (`on_accept` invoked), governance calls `update_token` with `remove_chains = [Evm(X)]` for asset `A` (e.g., migrating to a new contract `C2` via `add_chains`, which also deletes the `(Evm(X), C1)` reverse mapping per lines 407-411).
4. The relayer eventually submits the pending message; `Pallet::on_accept` looks up `ContractToAsset::<T>::get(Evm(X), C1)` — now `None` — and the delivery fails/reverts.
5. The user's original tokens remain burned/escrowed on chain `X` with no path to mint/release on this chain, since the message can never be reconstructed against the new mapping and the request may have no timeout to trigger a source-side refund. [1](#0-0) [2](#0-1)

### Citations

**File:** modules/pallets/hyper-fungible-token/src/lib.rs (L378-433)
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

			for chain in update.remove_chains {
				if let Some(old_contract) = TokenContracts::<T>::get(chain, update.asset_id.clone())
				{
					ContractToAsset::<T>::remove(chain, old_contract);
				}
				TokenContracts::<T>::remove(chain, update.asset_id.clone());
				Precisions::<T>::remove(update.asset_id.clone(), chain);
			}

			Ok(())
		}
```

**File:** modules/pallets/hyper-fungible-token/README.md (L81-89)
```markdown
## ISMP module behaviour

- `on_accept` — receives `Send` messages from the paired EVM contract. Maps
  the source contract back to a local asset via `ContractToAsset`, scales the
  amount using `Precisions`, then mints (non-native) or releases from escrow
  (native) to the beneficiary. Emits `TokenReceived`.
- `on_timeout` — refunds the original sender's balance from escrow or by
  re-minting. Emits `TokenRefunded`.
- `on_response` — unused; this pallet uses post-only messaging.
```
