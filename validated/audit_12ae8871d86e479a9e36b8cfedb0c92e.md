## No further tool calls available — presenting findings based on evidence gathered

### Title
Missing keys/values length check in EVM `verify_membership` allows a membership proof to omit some requested commitments without being caught - (File: `modules/ismp/state-machines/evm/src/lib.rs`)

### Summary
`EvmStateMachine::verify_membership` (and the shared free function `verify_membership`) verifies that request commitments are present in the source chain's ISMP storage by decoding the proof, deriving storage keys, and calling `get_values_from_proof`. It then only checks that none of the *returned* values are `None`: [1](#0-0) 

Unlike its sibling functions in the same trait implementation — `verify_non_membership` and `verify_state_proof` — which explicitly assert `values.len() != keys_len` and return `EvmStateMachineError::MismatchedValuesAndKeys` if the proof output does not "account for every key": [2](#0-1) 

`verify_membership` never performs this length check. The `MismatchedValuesAndKeys` error variant is explicitly documented as guarding against "the proof did not account for every key" [3](#0-2) , confirming this is a known class of proof malformation the codebase defends against elsewhere but omitted in this one path.

### Finding Description
The overall aggregate check in `verify_membership` is: "no returned value is `None`." This is analogous to the ACA-Py LDP-VC flaw, where an aggregated verification result (`verified: true/false`) failed to factor in the result of *all* individual sub-proofs — here, the aggregate membership check fails to confirm that *all* requested commitment keys were actually present in `get_values_from_proof`'s output map, only that whichever entries *were* returned are non-empty. If `get_values_from_proof` (in `modules/ismp/state-machines/evm/src/utils.rs`) can, for any malformed/partial storage proof, return fewer entries than `keys.len()` (e.g., a proof covering only a subset of the requested slots) without itself erroring, then `verify_membership` would return `Ok(())` even though not every requested request commitment was actually proven to exist in the source chain's state.

This function is called directly from the request handler when processing an incoming `RequestMessage` batch, reachable by any unprivileged relayer via `pallet_ismp::Call::handle_unsigned`: [4](#0-3) [5](#0-4) 

### Impact Explanation
If exploitable, this would let a malicious relayer submit a batch of `Post` requests together with a state proof that fully proves only a subset of the claimed commitments, while the missing entries silently pass the "no `None`" check because they were never present in the returned map at all. This could result in the handler dispatching (and modules' `on_accept` executing) requests that were never actually committed on the source chain — i.e., forged message delivery / unsound state-membership verification, matching the "forged message delivery" and "unsound state commitment" impact categories in scope.

### Likelihood Explanation
The likelihood is uncertain without confirming the internal behavior of `get_values_from_proof` in `modules/ismp/state-machines/evm/src/utils.rs`, which I was unable to inspect before running out of tool calls. If that helper always returns exactly one entry per input key (erroring otherwise), this gap is only a defense-in-depth/consistency issue and not exploitable. The strong signal that this is a real gap is the explicit, purpose-built `MismatchedValuesAndKeys` error that the two structurally identical sibling verification paths (`verify_non_membership`, `verify_state_proof`) both use, while `verify_membership` — which shares the same "proof interpretation" pattern — omits it entirely.

### Recommendation
Confirm (via a Devin session with full repo access) whether `get_values_from_proof` guarantees a 1:1 mapping from `keys` to returned entries for every possible malformed proof. If not, add the same `values.len() != keys.len()` guard used in `verify_non_membership`/`verify_state_proof` to `verify_membership` in `modules/ismp/state-machines/evm/src/lib.rs`, returning `EvmStateMachineError::MismatchedValuesAndKeys` (or an equivalent) so that partial proofs cannot silently pass membership verification for a subset of commitments.

### Proof of Concept
Could not be constructed/verified without inspecting `get_values_from_proof`'s implementation in `modules/ismp/state-machines/evm/src/utils.rs`, which requires filesystem access beyond what the ask-only index search could retrieve in the remaining iterations. A background Devin session with full repo access should verify this function's guarantees before treating this as a confirmed, exploitable vulnerability.

### Citations

**File:** modules/ismp/state-machines/evm/src/lib.rs (L51-53)
```rust
	/// The number of verified values doesn't match the number of supplied keys.
	#[error("Mismatched values/keys: the proof did not account for every key")]
	MismatchedValuesAndKeys,
```

**File:** modules/ismp/state-machines/evm/src/lib.rs (L119-147)
```rust
pub fn verify_membership<H: Keccak256 + Send + Sync>(
	commitments: Vec<H256>,
	root: StateCommitment,
	proof: &Proof,
	contract_address: H160,
) -> Result<(), Error> {
	let mut evm_state_proof = decode_evm_state_proof(proof)?;
	let storage_proof = evm_state_proof
		.storage_proof
		.remove(&contract_address.0.to_vec())
		.ok_or(EvmStateMachineError::ContractAccountProofMissing)?;
	let keys = req_commitment_key::<H, _>(commitments, |k| H::keccak256(k).0.to_vec());
	let root = H256::from_slice(&root.state_root[..]);
	let contract_root = get_contract_account::<H>(
		evm_state_proof.contract_proof,
		&contract_address.0,
		root.clone(),
	)?
	.storage_root
	.0
	.into();
	let values = get_values_from_proof::<H>(keys, contract_root, storage_proof)?;

	if values.into_iter().any(|val| val.is_none()) {
		return Err(EvmStateMachineError::MissingMembershipValues.into());
	}

	Ok(())
}
```

**File:** modules/ismp/state-machines/evm/src/lib.rs (L282-321)
```rust
	fn verify_membership(
		&self,
		host: &dyn IsmpHost,
		commitments: Vec<H256>,
		root: StateCommitment,
		proof: &Proof,
	) -> Result<(), Error> {
		let contract_address = EvmHosts::<T>::get(&proof.height.id.state_id)
			.ok_or(EvmStateMachineError::IsmpContractNotFound)?;
		verify_membership::<H>(commitments, root, proof, contract_address)
	}

	fn commitment_state_trie_key(&self, commitments: Vec<H256>) -> Vec<Vec<u8>> {
		req_commitment_key::<H, _>(commitments, |k| H::keccak256(k).0.to_vec())
	}

	fn receipts_state_trie_key(&self, commitments: Vec<H256>) -> Vec<Vec<u8>> {
		// State trie keys are used to process timeouts from EVM chains.
		// We return the trie keys for request receipts.
		req_receipt_keys::<H>(commitments)
	}

	fn verify_non_membership(
		&self,
		host: &dyn IsmpHost,
		commitments: Vec<H256>,
		root: StateCommitment,
		proof: &Proof,
	) -> Result<(), Error> {
		let keys = self.receipts_state_trie_key(commitments);
		let keys_len = keys.len();
		let values = self.verify_state_proof(host, keys, root.state_root, proof)?;
		if values.len() != keys_len {
			return Err(EvmStateMachineError::MismatchedValuesAndKeys.into());
		}
		if values.into_iter().any(|(_key, val)| val.is_some()) {
			return Err(EvmStateMachineError::DeliveredRequestsInBatch.into());
		}
		Ok(())
	}
```

**File:** modules/ismp/core/src/handlers/request.rs (L86-93)
```rust
	// Verify membership proof
	let state = host.state_machine_commitment(msg.proof.height)?;
	let commitments = msg
		.requests
		.iter()
		.map(|post| hash_request::<H>(&Request::Post(post.clone())))
		.collect();
	state_machine.verify_membership(host, commitments, state, &msg.proof)?;
```

**File:** modules/pallets/ismp/src/lib.rs (L373-382)
```rust
		pub fn handle_unsigned(
			origin: OriginFor<T>,
			messages: Vec<Message>,
		) -> DispatchResultWithPostInfo {
			ensure_none(origin)?;

			Self::execute(messages.clone())?;

			Ok(().into())
		}
```
