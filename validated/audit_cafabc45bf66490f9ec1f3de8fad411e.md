## Analog Found

### Title
In-flight cross-chain transfers become permanently unrefundable when `update_token` removes a destination chain before the message times out - (File: `modules/pallets/hyper-fungible-token/src/lib.rs`)

### Summary
The `pallet-hyper-fungible-token` pallet's `update_token` extrinsic lets `CreateOrigin` add or remove EVM chains from a registered token's configuration at any time, with no delay and no check for outstanding in-flight transfers. If a user's `send()` is already burning/escrowing funds toward a chain that governance subsequently removes via `remove_chains`, and that message later times out (destination congestion, liveness fault, etc.), the pallet's `on_timeout` handler cannot locate the asset for that `(dest, to)` pair anymore — the exact same reverse-lookup entry was just deleted — and the refund fails. This mirrors the JUSD pattern: a legitimate, instantaneous configuration change (delisting a reserve / removing a chain) leaves users who were in good standing with no on-chain grace period or fallback to recover funds already committed under the old configuration.

### Finding Description
`update_token` processes `remove_chains` by deleting both `TokenContracts` and the reverse-lookup `ContractToAsset` for the removed chain, unconditionally and immediately: [1](#0-0) 

There is no check for pending outbound `send()` requests still targeting that chain, and no delay/grace window before the mapping disappears.

`on_timeout` — the only path that refunds a burned/escrowed `send()` after its destination fails to process it in time — depends on that same `ContractToAsset` map to resolve which local asset to refund: [2](#0-1) 

If `ContractToAsset::<T>::get(dest, &to)` no longer resolves (because `update_token` removed that chain in the interim), `on_timeout` returns `HftError::UnknownContractOnTimeout` instead of refunding.

Per the generic ISMP timeout handler, a failing module callback does not delete the request commitment — it is restored so the timeout can be retried later: [3](#0-2) 

This makes the failure retryable in principle, but retrying calls the exact same `on_timeout` logic against the exact same (now-missing) storage entry, so it fails identically every time unless governance deliberately re-inserts the old, deprecated `(dest, to)` mapping purely to unblock the stuck refund — something governance has no protocol-level obligation or reason to do once it has decided to remove that chain. The user's burned/escrowed tokens are left stuck in escrow (native) or already destroyed (non-native burn) with no on-chain path to recovery.

### Impact Explanation
A user who called `send()` in good faith, before any governance action, can have their funds permanently frozen purely because governance performed a normal, legitimate chain-removal operation while their transfer was still in flight and it later timed out. This is a permanent freezing of user funds triggered by an ordinary configuration update rather than any user error, with no on-chain grace period, migration path, or recovery mechanism — directly analogous to JUSD's borrowers losing all recourse the instant a reserve is delisted.

### Likelihood Explanation
This requires no attacker: it triggers under normal, expected pallet operation. `update_token` is a routine governance/admin call used for migrations or chain deprecation (as shown in the pallet's own benchmarking and tests), and any period of destination-chain congestion or delay long enough to cross the timeout combined with an in-between `remove_chains` call is sufficient to strand the affected sender's funds. Given genuine operational reasons to redeploy or migrate a token's chain configuration, the race between in-flight sends and a chain removal is realistic, not a contrived edge case.

### Recommendation
Before permitting `remove_chains` for an asset/chain pair, either (a) refuse removal while there are known outstanding, undelivered `send()` requests to that `(asset, chain)` pair, (b) retain the old `ContractToAsset`/`TokenContracts` entries for a grace period sufficient to drain in-flight timeouts before deleting them, or (c) decouple `on_timeout`'s refund logic from the live `ContractToAsset` map by snapshotting the asset/decimals at `send()` time (e.g., in the request body or a dedicated pending-request store) so a later configuration change cannot block a legitimately pending refund.

### Proof of Concept
1. User calls `HyperFungibleToken::send` with `destination = Evm(42)`, burning (non-native) or escrowing (native) `amount` of `asset_id`. This dispatches a `PostRequest` with `to = TokenContracts::<T>::get(Evm(42), asset_id)`.
2. Before the destination processes the message (e.g. due to congestion or a liveness fault as anticipated by the ISMP timeout design), governance calls `update_token` with `remove_chains = vec![Evm(42)]` for `asset_id` — a routine, non-malicious maintenance action. This deletes `TokenContracts::<T>::(Evm(42), asset_id)` and `ContractToAsset::<T>::(Evm(42), old_contract)` per [1](#0-0) .
3. The destination never processes the message in time; the request times out. A relayer submits the timeout to `pallet-ismp`, which invokes `HyperFungibleToken::on_timeout` per [4](#0-3) .
4. `on_timeout` calls `ContractToAsset::<T>::get(dest, &to).ok_or(HftError::UnknownContractOnTimeout)?` per [5](#0-4) ; this now returns `None`, the callback errors, and no refund is issued.
5. The commitment is restored for retry per [3](#0-2) , but every retry hits the same missing storage entry, so the user's burned/escrowed funds remain permanently unrecoverable unless governance re-adds the deprecated `(Evm(42), old_contract)` mapping solely to service this one stuck refund.

### Citations

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

**File:** modules/ismp/core/src/handlers/timeout.rs (L90-121)
```rust
			let router = host.ismp_router();
			requests
				.into_iter()
				.map(|post| {
					let cb = router.module_for_id(post.from.clone())?;
					let request = Request::Post(post.clone());
					// Re-check the commitment right before dispatch. The up-front
					// pass above runs before any callback executes; a prior
					// on_timeout in this same batch could have caused the
					// commitment for this request to be removed (directly or by
					// re-entering the handler), and we must not invoke
					// on_timeout for a request that is no longer pending.
					let commitment = hash_request::<H>(&request);
					if host.request_commitment(commitment).is_err() {
						Err(Error::UnknownRequest { meta: (&post).into() })?
					}
					// Delete commitment to prevent rentrancy attack
					let meta = host.delete_request_commitment(&request)?;
					let mut signer = None;
					// If it was a routed request delete the receipt
					if host.host_state_machine() != post.source {
						signer = host.delete_request_receipt(&request).ok();
					}
					let res = cb.on_timeout(request.clone()).map(|weight| {
						total_module_weight.saturating_accrue(weight);
						let commitment = hash_request::<H>(&request);
						Event::PostRequestTimeoutHandled(TimeoutHandled {
							commitment,
							source: post.source,
							dest: post.dest,
						})
					});
```

**File:** modules/ismp/core/src/handlers/timeout.rs (L122-134)
```rust
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
