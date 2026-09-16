### Title
Missing validation for duplicate/reused remote token contract addresses in `register_token` (and `update_token`) - ([File: modules/pallets/hyper-fungible-token/src/lib.rs])

### Summary
`pallet-hyper-fungible-token`'s `register_token` extrinsic accepts a `token_contract` address per destination chain and blindly writes it into both `TokenContracts` (asset → contract) and `ContractToAsset` (contract → asset) storage maps, without checking whether that `(chain, token_contract)` pair is already bound to a *different* local asset. This is the same root-cause class as the reported `OriginalTokenBridge.registerToken` issue — the registration path fails to enforce that the address used to identify a counterpart token is unique/consistent with the local asset it is meant to represent.

### Finding Description
`register_token` iterates the submitted `chains` map and, for every chain, inserts: [1](#0-0) 

There is no lookup against the existing `ContractToAsset` map to verify the `token_contract` is not already registered for a different `AssetId` on that chain, and no check that the same `local_id` is not already registered (which would silently overwrite `NativeAssets`/`Precisions`/`TokenContracts` without cleaning up the previous `ContractToAsset` entry). Contrast this with `update_token`, which explicitly removes the stale reverse mapping before inserting a new one: [2](#0-1) 

`register_token` has no equivalent cleanup/uniqueness step at all, so if the same EVM `token_contract` address is registered (accidentally, e.g. via a copy-pasted config or template) for two different local `AssetId`s on the same chain, `ContractToAsset::insert` simply overwrites the previous mapping.

### Impact Explanation
`on_accept` resolves the local asset for an inbound message purely via `ContractToAsset` keyed by `(source_chain, from_contract)`, per the module's documented behaviour: [3](#0-2) 

If the reverse mapping for a given contract address has been overwritten to point at a different asset than the one whose outbound `TokenContracts` entry still targets that same contract, inbound deliveries from the legitimate counterpart contract will be minted/released as the *wrong* asset (wrong decimals/denomination, wrong custody accounting), while the original asset's `TokenContracts` entry keeps dispatching outbound transfers to that same now-misattributed contract. This can misdirect or permanently misaccount user funds moving through `send`/`on_accept`, which is the "unexpected behavior in cross-chain operations" called out in the original report, applied to a live mint/burn/escrow accounting path.

### Likelihood Explanation
`register_token` is gated by `T::CreateOrigin`, so exploitation requires a privileged registration action — but as in the original finding, this is a plain configuration-validation gap rather than a malicious-actor scenario: a legitimate operator re-registering, updating tooling, or reusing a template config for a new asset could trivially collide two assets on the same `(chain, token_contract)` key, since nothing in `register_token` prevents it.

### Recommendation
In `register_token`, before inserting into `ContractToAsset`, check that `ContractToAsset::<T>::get(chain, &token_contract)` is either empty or already equal to `registration.local_id`; reject the call (or require an explicit override path) otherwise. Additionally, guard against implicit re-registration of an already-known `local_id` by checking `NativeAssets::<T>::contains_key` and either erroring out or reusing the same stale-mapping cleanup logic already present in `update_token`.

### Proof of Concept
1. Governance/`CreateOrigin` calls `register_token` for `asset_id = A` with `chains = { Evm(1) => ChainConfig { token_contract: 0xAAA…, decimals: 18 } }`. This sets `TokenContracts(Evm(1), A) = 0xAAA` and `ContractToAsset(Evm(1), 0xAAA) = A`.
2. Later, `register_token` is called again for a different `asset_id = B` reusing the same contract address `0xAAA` on `Evm(1)` (e.g. copy-pasted config). This overwrites `ContractToAsset(Evm(1), 0xAAA) = B`, while `TokenContracts(Evm(1), A)` still equals `0xAAA`.
3. A user calls `send` for asset `A` to `Evm(1)`; the pallet dispatches a `Send` message to contract `0xAAA` as before (looks correct from the sender's point of view).
4. When the peer contract `0xAAA` later delivers a POST back to this pallet, `on_accept` resolves the source contract via `ContractToAsset(Evm(1), 0xAAA)`, which now returns `B` instead of `A`, so the pallet mints/releases asset `B` (with `B`'s decimals/custody model) instead of crediting/refunding asset `A` — resulting in funds misattributed to the wrong asset.

### Citations

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

**File:** modules/pallets/hyper-fungible-token/src/lib.rs (L407-419)
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
```

**File:** modules/pallets/hyper-fungible-token/README.md (L83-86)
```markdown
- `on_accept` — receives `Send` messages from the paired EVM contract. Maps
  the source contract back to a local asset via `ContractToAsset`, scales the
  amount using `Precisions`, then mints (non-native) or releases from escrow
  (native) to the beneficiary. Emits `TokenReceived`.
```
