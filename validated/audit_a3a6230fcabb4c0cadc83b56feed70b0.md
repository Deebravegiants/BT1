## Title
`update_token()` config changes break in‑flight transfer refunds, permanently freezing user funds - (File: `modules/pallets/hyper-fungible-token/src/lib.rs`, `modules/pallets/hyper-fungible-token/src/module.rs`)

### Summary
`pallet-hyper-fungible-token`'s `update_token` extrinsic can repoint or remove the `TokenContracts`/`ContractToAsset` mapping for an asset/chain pair after a user has already escrowed or burned funds via `send()`. When the corresponding cross-chain request times out, `on_timeout` looks up the asset strictly by the *original* destination contract address, which no longer resolves once the mapping has changed — causing the refund to fail and the user's funds to be permanently stuck, exactly mirroring the reported `setRedeemable()` issue where a legitimate config change orphans previously committed user funds.

### Finding Description
A user calls the unprivileged `send()` extrinsic, which locks (native) or burns (non-native) their tokens and dispatches a cross-chain `DispatchPost` whose `to` field is resolved from `TokenContracts` at that moment: [1](#0-0) 

If, before the request is delivered or times out, `CreateOrigin` calls `update_token()`, the pallet removes the old `ContractToAsset` reverse mapping for that chain (either to repoint it to a new contract, or entirely, when the chain is in `remove_chains`): [2](#0-1) 

When the original request eventually times out, `on_timeout` resolves the asset to refund purely from `ContractToAsset::get(dest, &to)`, using the stale `to` address baked into the already-dispatched request: [3](#0-2) 

Because the old `(dest, to)` entry no longer exists in `ContractToAsset` (it was removed/repointed by `update_token`), this lookup returns `None` and `on_timeout` errors out with `HftError::UnknownContractOnTimeout`: [4](#0-3) 

Since the pallet has no alternative recovery path for a timed-out request whose asset cannot be resolved, the tokens that were locked in the pallet's escrow account (or already burned) can never be returned to the user. This is structurally identical to the reported `setRedeemable()` bug: a subsequent, non-malicious reconfiguration of a token/contract mapping invalidates state that earlier, legitimate user transactions depended on, leaving those users unable to recover funds tied to the earlier configuration.

### Impact Explanation
Any user with an in-flight `send()` request at the time `update_token` is called to rotate or remove a chain's contract mapping for that asset will have their escrowed or burned funds permanently frozen — `on_timeout` reverts indefinitely and there is no other mechanism in the pallet to reclaim the locked/burned balance. This is a direct, permanent freezing of user funds triggered by a routine, expected governance operation (updating a token's contract configuration, e.g. after an EVM contract upgrade or migration), not requiring any malicious behavior — matching the severity and mechanism of the original report.

### Likelihood Explanation
`update_token` is a normal, expected maintenance operation (e.g., migrating to a new `HyperFungibleToken` contract address on an EVM chain, or deprecating support for a chain) documented as part of pallet operation. Any request dispatched by any user shortly before such an update is affected, and cross-chain request timeouts are common (chain congestion, relayer delay, or intentional handling of stuck requests). No attacker action is needed—only the routine sequence of "user sends" followed by "administrator updates/removes chain config" followed by "the request times out."

### Recommendation
Do not rely on late-bound conflict-prone reverse lookups from mutable storage (`ContractToAsset`) to resolve the asset for `on_timeout`/refund logic. Instead, embed the local `AssetId` (and/or decimals) directly in the outbound request body/commitment at `send()` time, so that `on_timeout` can resolve the correct asset independent of any later `update_token`/`register_token` changes. Alternatively, retain historical `ContractToAsset` entries (e.g., versioned/keyed by commitment) until all requests referencing them have resolved or timed out, instead of eagerly removing them in `update_token`.

### Proof of Concept
1. Governance registers asset `X` with `TokenContracts[Evm(1)][X] = ContractA` via `register_token`.
2. User calls `send()` for asset `X` to `Evm(1)`; the pallet burns/escrows the user's tokens and dispatches a `DispatchPost` with `to = ContractA`. [5](#0-4) 
3. Before the request is delivered/times out, governance calls `update_token` to repoint asset `X` on `Evm(1)` to `ContractB` (or removes `Evm(1)` from `X`'s chains). This removes the `ContractToAsset[Evm(1)][ContractA]` entry. [2](#0-1) 
4. The original request times out; `pallet-ismp` invokes `on_timeout`, which calls `ContractToAsset::get(Evm(1), ContractA)` — now `None` — and errors with `UnknownContractOnTimeout`, so the refund never happens. [3](#0-2) 
5. The user's escrowed/burned funds are permanently unrecoverable.

### Citations

**File:** modules/pallets/hyper-fungible-token/src/lib.rs (L251-253)
```rust
			let token_contract =
				TokenContracts::<T>::get(params.destination, params.asset_id.clone())
					.ok_or(Error::<T>::TokenContractNotFound)?;
```

**File:** modules/pallets/hyper-fungible-token/src/lib.rs (L304-310)
```rust
			let dispatch_post = DispatchPost {
				dest: params.destination,
				from: PALLET_ID.to_bytes(),
				to: token_contract,
				timeout: params.timeout,
				body: Message::abi_encode(&token_message),
			};
```

**File:** modules/pallets/hyper-fungible-token/src/lib.rs (L407-430)
```rust
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

**File:** modules/pallets/hyper-fungible-token/src/module.rs (L218-237)
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
```
