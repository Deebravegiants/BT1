### Title
Escrowed relayer fee can be double-spent because request-timeout refund ignores the `claimed` flag - ([File: modules/pallets/ismp/src/host.rs])

### Summary
`pallet-ismp`'s timeout path refunds the escrowed relayer fee to the original payer without ever checking whether that fee has already been credited to a relayer through `pallet-ismp-relayer`'s `accumulate_fees` flow. The `claimed` field on `RequestMetadata` is written by the fee-accumulation pallet but never read by the timeout pallet, so the two independent "release" paths for the same escrowed balance are not mutually exclusive.

### Finding Description
`RequestCommitments<T>` stores a `RequestMetadata { offchain, fee, claimed }` entry per outgoing request, with `claimed` intended to record that a relayer has already been credited for delivering the request: [1](#0-0) 

`pallet-ismp-relayer::accumulate_fees` (unsigned, callable by anyone with a valid delivery proof) verifies a `WithdrawalProof` and, for every claimed commitment, sets `claimed = true` and credits the relayer's balance in the `Fees` ledger — but it does **not** remove the `RequestCommitments` entry or transfer funds out of escrow yet: [2](#0-1) 

Independently, the ISMP timeout handler removes a request commitment and, if the module callback acknowledges the timeout, calls `on_request_timeout` to refund the escrowed fee to the payer: [3](#0-2) 

`delete_request_commitment` only checks that the entry exists — it never inspects `claimed`: [4](#0-3) 

`on_request_timeout` then unconditionally transfers the escrowed `fee.fee` back to `fee.payer` from the shared `RELAYER_FEE_ACCOUNT`, again without checking `leaf_meta.claimed`: [5](#0-4) 

The fee for a given request is escrowed exactly once, at dispatch time, into `RELAYER_FEE_ACCOUNT`: [6](#0-5) 

If the same commitment is both (a) marked `claimed = true` and credited to a relayer via `accumulate_fees`, and (b) later processed through the timeout path (the request still exists in `RequestCommitments` after step (a) since `accumulate_fees` re-inserts it with `claimed = true` rather than deleting it), the single escrowed amount is paid out twice: once to the relayer's `Fees` balance (eventually withdrawn via the `HYPR-FEE` refunding router) and once directly back to the payer. This is structurally analogous to the CVE-2022-3910 pattern: a resource that is "permanently registered" and should only be released through one authoritative path (the `claimed` flag) is instead released through a second path that fails to check/respect that reference-count-like invariant, producing an over-release of the same underlying balance.

I was not able to fully confirm, within the tool budget available, whether the timeout handler's `verify_non_membership` check against `RequestReceipts` on the destination chain (which should normally prevent timing out an already-delivered request) can be bypassed with a stale/older accepted state-machine height that predates the actual delivery. `state_machine_commitment` height selection in `validate_state_machine`/`handle` is not shown to enforce monotonic/latest-height usage for timeout proofs, which would be the mechanism enabling exploitation; this should be verified against the full `modules/ismp/core/src/handlers/timeout.rs` and consensus-client `verify_non_membership` implementations.

### Impact Explanation
If exploitable, this drains the shared `RELAYER_FEE_ACCOUNT` pool (funded by all applications' relayer fees) by paying out the same escrowed fee twice — a form of unbacked fund release / theft from a shared escrow account, directly affecting relayer reward accounting across the whole protocol, not just a single request.

### Likelihood Explanation
Both code paths (`accumulate_fees` and unsigned message timeout handling) are permissionless and reachable by any relayer/message submitter. The missing `claimed` check is a definite code-level gap; whether it is practically triggerable depends on the ability to submit a stale non-membership proof for the timeout, which I could not fully verify in this session.

### Recommendation
Have `delete_request_commitment` / `on_request_timeout` check `leaf_meta.claimed` before refunding the payer, and reject (or treat as a no-op refund) commitments already marked as claimed by `accumulate_fees`. Additionally, verify that timeout proofs must reference the state machine's latest known height (or otherwise ensure the non-membership proof cannot reference a height that predates a legitimate delivery already recorded via `accumulate_fees`).

### Proof of Concept
Conceptual sequence (root cause confirmed; full end-to-end reachability of the double payment depends on the unresolved stale-height question noted above):
1. App dispatches a request via `dispatch_request`, escrowing `fee.fee` into `RELAYER_FEE_ACCOUNT` [6](#0-5) .
2. A relayer delivers the request on the destination and later submits a `WithdrawalProof` to `accumulate_fees`, which sets `RequestCommitments[req].claimed = true` and credits the relayer's `Fees` balance [2](#0-1) .
3. Because the entry is re-inserted (not removed) and `claimed` is never checked by the timeout path, a subsequent (or race-condition/stale-proof) timeout submission for the same commitment passes `delete_request_commitment` and `on_request_timeout`, refunding `fee.fee` a second time to `payer` from `RELAYER_FEE_ACCOUNT` [5](#0-4) .

### Citations

**File:** modules/pallets/ismp/src/dispatcher.rs (L64-74)
```rust
#[derive(codec::Encode, codec::Decode, scale_info::TypeInfo, Clone)]
#[cfg_attr(feature = "std", derive(serde::Deserialize, serde::Serialize))]
#[scale_info(skip_type_params(T))]
pub struct RequestMetadata<T: Config> {
	/// Information about where it's stored in the offchain db
	pub offchain: LeafIndexAndPos,
	/// Other metadata about the request
	pub fee: FeeMetadata<T>,
	/// Has fee been claimed?
	pub claimed: bool,
}
```

**File:** modules/pallets/ismp/src/dispatcher.rs (L92-106)
```rust
	fn dispatch_request(
		&self,
		request: DispatchRequest,
		fee: FeeMetadata<T>,
	) -> Result<H256, anyhow::Error> {
		// collect payment for the request
		if fee.fee != Zero::zero() {
			T::Currency::transfer(
				&fee.payer,
				&RELAYER_FEE_ACCOUNT.into_account_truncating(),
				fee.fee,
				Preservation::Expendable,
			)
			.map_err(|err| IsmpError::Custom(format!("Error withdrawing request fees: {err:?}")))?;
		}
```

**File:** modules/pallets/relayer/src/accumulate.rs (L149-161)
```rust
		for req in withdrawal_proof.commitments {
			if !claimed_commitments.contains(&req) {
				continue;
			}
			match RequestCommitments::<T>::get(req) {
				Some(mut leaf_meta) => {
					leaf_meta.claimed = true;
					RequestCommitments::<T>::insert(req, leaf_meta)
				},
				// Unreachable
				None => {},
			}
		}
```

**File:** modules/ismp/core/src/handlers/timeout.rs (L106-127)
```rust
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
					if res.is_ok() {
						host.on_request_timeout(&request, meta)?;
					} else {
						// Module callback failed; restore commitment so the request
						// can be retried.
						host.store_request_commitment(&request, meta)?;
```

**File:** modules/pallets/ismp/src/host.rs (L236-243)
```rust
	fn delete_request_commitment(&self, req: &Request) -> Result<Vec<u8>, Error> {
		let hash = hash_request::<Self>(req);
		// We can't delete actual leaves in the mmr so this serves as a replacement for that
		let meta = child_trie::RequestCommitments::<T>::get(hash)
			.ok_or_else(|| Error::Custom("Request Commitment not found".to_string()))?;
		child_trie::RequestCommitments::<T>::remove(hash);
		Ok(meta.encode())
	}
```

**File:** modules/pallets/ismp/src/host.rs (L322-335)
```rust
	fn on_request_timeout(&self, _req: &Request, meta: Vec<u8>) -> Result<(), Error> {
		let leaf_meta = RequestMetadata::<T>::decode(&mut &*meta)
			.map_err(|_| Error::Custom("Failed to decode leaf metadata".to_string()))?;
		if leaf_meta.fee.fee > Zero::zero() {
			T::Currency::transfer(
				&RELAYER_FEE_ACCOUNT.into_account_truncating(),
				&leaf_meta.fee.payer,
				leaf_meta.fee.fee,
				Preservation::Expendable,
			)
			.map_err(|err| Error::Custom(format!("Failed to refund relayer fee: {err:?}")))?;
		}
		Ok(())
	}
```
