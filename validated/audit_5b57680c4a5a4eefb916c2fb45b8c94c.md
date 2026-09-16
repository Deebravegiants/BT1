### Title
`update_token()` chain reconfiguration permanently strands in-flight escrowed/burned funds - (File: `modules/pallets/hyper-fungible-token/src/lib.rs`)

### Summary
`pallet-hyper-fungible-token`'s `update_token()` extrinsic immediately deletes the `ContractToAsset` reverse-lookup entry for a chain's old token contract address whenever that chain's configuration is updated (`add_chains` branch) or removed (`remove_chains` branch). Any `send()` transfer that is still in flight to that chain at the moment of the update becomes unrefundable if it later times out, because `on_timeout` depends on that exact mapping to resolve the escrowed/burned asset. This mirrors the reported analog class: a normal (non-malicious) administrative call permanently locks user funds that were already committed to the protocol, with no clean recovery path.

### Finding Description
`send()` locks (native asset) or burns (non-native asset) a user's tokens and dispatches a cross-chain `Post` request whose `to` field is the currently configured EVM contract address for `(destination, asset_id)`: [1](#0-0) [2](#0-1) 

If that request later times out, `on_timeout` refunds the sender, but only after resolving the local asset via `ContractToAsset::<T>::get(dest, &to)`, keyed by the exact `to` contract address that was embedded in the original request: [3](#0-2) 

`update_token()` is called by `CreateOrigin` to change a chain's token-contract address (e.g. a routine contract migration) or to remove a chain entirely. Both paths unconditionally delete the *old* `ContractToAsset` entry before installing the new one (or nothing, for `remove_chains`), with no check for outstanding in-flight requests still referencing the old contract address: [4](#0-3) [5](#0-4) 

Once that mapping is gone, any pending `send()` to the now-stale `to` address that subsequently times out will hit `HftError::UnknownContractOnTimeout` in `on_timeout`, and the previously escrowed/burned funds are never refunded to the sender. This is a routine, foreseeable maintenance action (correcting a contract address, updating decimals, or deprecating a chain) — not an abuse of privilege — that nonetheless destroys the invariant the timeout-refund path depends on, exactly analogous to the reported `UXDController.setRedeemable()` pattern where an ordinary function call locks users' already-committed funds.

### Impact Explanation
Users who dispatched `send()` transfers shortly before a legitimate `update_token()` reconfiguration (contract address rotation, precision fix, or chain removal) permanently lose access to their escrowed or burned funds once the in-flight request times out: `on_timeout` cannot resolve the asset and errors out, and while `pallet-ismp`'s timeout handler preserves the commitment for retry, retrying is futile unless `CreateOrigin` manually and precisely restores the exact stale `(chain, old_contract)` mapping — which is not part of any expected operational flow and, for `remove_chains`, may not even be knowable/desired once a chain is deprecated. This is a genuine freezing-of-funds bug reachable purely by a normal user's `send()` call combined with a routine, non-malicious protocol maintenance action.

### Likelihood Explanation
Likelihood is moderate: it requires (1) a user's `send()` transfer being in flight, and (2) `CreateOrigin` performing a routine `update_token()` reconfiguration (contract migration, decimal correction, or chain deprecation) before that transfer is delivered or times out. Contract migrations and chain deprecations are realistic, expected operational events for a long-lived cross-chain token bridge, making this a credible, recurring risk rather than a contrived edge case.

### Recommendation
Before removing/overwriting a `(chain, asset_id)` → contract mapping in `update_token()`, either (a) retain the old `ContractToAsset` entry until all in-flight requests referencing it have resolved (delivered or timed out), e.g. via a grace-period/versioned mapping, or (b) have `on_timeout` fall back to a per-request embedded asset identifier (encoded in the dispatched `Message`/request body) rather than relying solely on a mutable global `ContractToAsset` reverse lookup that can be invalidated after dispatch.

### Proof of Concept
1. User calls `send()` for `asset_id` to `destination = Evm(X)`; funds are escrowed/burned and a `Post` request is dispatched with `to = TokenContracts::<T>::get(Evm(X), asset_id)` (contract `A`).
2. Before the request is delivered or times out, `CreateOrigin` calls `update_token()` with `add_chains` containing a new `token_contract = B` for `(Evm(X), asset_id)` (e.g. legitimate contract migration) — this deletes `ContractToAsset::<T>::remove(Evm(X), A)` at `lib.rs:408-411`, or alternatively calls it with `remove_chains = [Evm(X)]`, which also removes the mapping at `lib.rs:423-427`.
3. The original request later times out; `pallet-ismp` invokes `on_timeout`, which calls `ContractToAsset::<T>::get(Evm(X), A)` — now `None` — returning `HftError::UnknownContractOnTimeout` at `module.rs:236-237`.
4. Per `pallet-ismp`'s timeout handler, the commitment is restored for retry, but retries fail identically unless `CreateOrigin` re-inserts the exact stale `(Evm(X), A)` mapping, which is outside normal operational expectations — the user's escrowed/burned funds remain stuck.

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

**File:** modules/pallets/hyper-fungible-token/src/lib.rs (L407-420)
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

**File:** modules/pallets/hyper-fungible-token/src/module.rs (L235-237)
```rust
				// Look up the asset from the destination contract address
				let local_asset_id = ContractToAsset::<T>::get(dest, &to)
					.ok_or(HftError::UnknownContractOnTimeout)?;
```
