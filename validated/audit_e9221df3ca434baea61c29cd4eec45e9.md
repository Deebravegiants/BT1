Confirmed vulnerability: the Rust BEEFY consensus verifier's supermajority check has no upper bound on the number of signatures relative to the authority set size, letting a caller submit an unbounded `signatures` vector that is fully processed (each entry costs an ECDSA/secp256k1 recovery) before any rejection.

### Title
Unbounded BEEFY signature array in `verify_mmr_update_proof` enables a computation-amplification DoS on consensus message handling - (File: `modules/consensus/beefy/verifier/src/lib.rs`)

### Summary
`verify_mmr_update_proof` computes `signatures_length = mmr.signed_commitment.signatures.len()` and only checks a lower-bound supermajority ratio via `check_participation_threshold(signatures_length as u32, authority_set.len)`, which requires `len >= (2*total)/3 + 1` but never enforces `len <= total` (or any hard cap). It then iterates over every entry in `mmr.signed_commitment.signatures` performing a `secp256k1_recover` for each one, before any authority-membership merkle proof is checked. [1](#0-0) [2](#0-1) 

### Finding Description
The BEEFY consensus message is submitted via `Message::Consensus` and reaches `handle_incoming_message` → the BEEFY consensus client → `verify_consensus` → `verify_mmr_update_proof`, all of which is invoked by an unprivileged relayer submitting a consensus proof extrinsic/transaction (e.g. through `pallet-beefy-consensus-proofs::verify_and_apply`, as seen calling `handlers::handle_incoming_message` with an attacker-supplied `consensus_proof`). [3](#0-2) 

Inside `verify_mmr_update_proof`, the only gate before the expensive per-signature `secp256k1_recover` loop is `check_participation_threshold`, which is a pure ratio check (`len >= (2*total)/3 + 1`) with `total` being the trusted authority-set size (a small, bounded number, e.g. hundreds of validators). Nothing caps `signatures_length` from above — an attacker can supply an arbitrarily large `signatures` vector (e.g. tens of thousands of bogus/duplicate entries), and the loop:
```
for sig in mmr.signed_commitment.signatures.iter() {
    let uncompressed = H::secp256k1_recover(&commitment_hash.0, &sig.signature)...
    ...
}
```
will fully execute a costly cryptographic recovery for every element before the (later) merkle multi-proof check on `authority_indices`/`authority_leaves` can reject the batch. The merkle-proof rejection only happens after all recoveries have completed, so the cost is paid regardless of validity — directly analogous to the reported issue where an untrusted source can force unbounded/very large per-message work before validation completes.

This differs from the sound patterns elsewhere in the codebase (e.g. `MAX_PROOF_DEPTH` guard in `modules/consensus/pharos/primitives/src/spv.rs`, or `MAX_VALIDATORS` guard in `modules/consensus/pharos/verifier/src/state_proof.rs`), which explicitly bound untrusted-array-derived iteration counts before expensive work runs. No equivalent upper bound exists for BEEFY's `signatures` array size relative to `authority_set.len`. [4](#0-3) [5](#0-4) 

### Impact Explanation
Each secp256k1 recovery is computationally nontrivial. Because the loop runs before the merkle authority-membership proof is checked, an attacker (any address able to submit a consensus message — this only requires holding a signer for the extrinsic, not any special privilege) can submit a single message whose `signatures` vector contains a very large number of entries (bounded only by extrinsic/transaction size limits, which can still admit thousands of 65-byte signature entries), forcing the node processing consensus updates to spend proportionally excessive CPU time per submitted message. Because the check happens inside the message-dispatch/handler path used for BEEFY consensus updates, this can degrade or stall processing of legitimate consensus and messaging traffic for the affected chain (state machine unable to keep up with genuine relayed proofs), consistent with CWE-400 uncontrolled resource consumption / DoS as in the referenced advisory.

### Likelihood Explanation
High: this requires only crafting a `ConsensusMessage`/`MmrProof` with an oversized `signatures` vector, well-formed enough to pass earlier decode/height checks, and submitting it as any relayer (no special permissions). The `authority_indices`/`authority_leaves` merkle check is only ever reached after the entire expensive loop executes, so validity of the proof is irrelevant to triggering the cost.

### Recommendation
Add an explicit upper bound in `verify_mmr_update_proof` (and the analogous EVM Solidity `EcdsaBeefy.verifyMmrUpdateProof`) rejecting `signatures_length > authority_set.len` (or some fixed cap) before performing any `secp256k1_recover` calls, mirroring the `MAX_PROOF_DEPTH`/`MAX_VALIDATORS` bounding pattern already used elsewhere in the codebase (e.g. `modules/consensus/pharos/primitives/src/spv.rs`, `modules/consensus/pharos/verifier/src/state_proof.rs`).

### Proof of Concept
1. Construct a `ConsensusMessage`/`MmrProof` whose `commitment` targets a known (trusted) authority set, with a valid `block_number` greater than `trusted_state.latest_beefy_height` (to pass the staleness check).
2. Populate `signed_commitment.signatures` with, e.g., 50,000 entries of arbitrary 65-byte data and increasing `index` values — this trivially satisfies `check_participation_threshold` since there is no upper bound.
3. Submit this as a `Message::Consensus` extrinsic/transaction (e.g. via `pallet-beefy-consensus-proofs::verify_and_apply` or the equivalent EVM `EcdsaBeefy.verify` call).
4. Observe that `verify_mmr_update_proof` performs 50,000 `secp256k1_recover` operations before failing the subsequent merkle authority-membership check, consuming disproportionate CPU/gas per submitted message relative to a legitimate proof (whose signature count is bounded by the real authority-set size).

### Citations

**File:** modules/consensus/beefy/verifier/src/lib.rs (L105-163)
```rust
pub fn verify_mmr_update_proof<H: Keccak256 + EcdsaRecover + Send + Sync>(
	mut trusted_state: ConsensusState,
	mmr: MmrProof,
) -> Result<(ConsensusState, H256), Error> {
	let signatures_length = mmr.signed_commitment.signatures.len();
	let latest_height = mmr.signed_commitment.commitment.block_number;

	if trusted_state.latest_beefy_height >= latest_height {
		return Err(Error::StaleHeight {
			trusted_height: trusted_state.latest_beefy_height,
			current_height: latest_height,
		});
	}

	let commitment = mmr.signed_commitment.commitment.clone();

	// Pick the authority set the commitment claims to be signed under, then judge
	// participation against that set alone.
	let authority_set = if commitment.validator_set_id == trusted_state.current_authorities.id {
		&trusted_state.current_authorities
	} else if commitment.validator_set_id == trusted_state.next_authorities.id {
		&trusted_state.next_authorities
	} else {
		return Err(Error::UnknownAuthoritySet { id: commitment.validator_set_id });
	};

	if !check_participation_threshold(signatures_length as u32, authority_set.len) {
		return Err(Error::SuperMajorityRequired);
	}

	let mmr_root_data = commitment
		.payload
		.get_raw(&MMR_ROOT_PAYLOAD_ID)
		.ok_or(Error::MmrRootHashMissing)?;

	if mmr_root_data.len() != 32 {
		return Err(Error::InvalidMmrRootHashLength { len: mmr_root_data.len() });
	}
	let mmr_root = H256::from_slice(mmr_root_data);

	let commitment_hash = H::keccak256(&commitment.encode());
	let mut authority_leaves: Vec<[u8; 32]> = Vec::new();
	let mut authority_indices = Vec::new();

	for sig in mmr.signed_commitment.signatures.iter() {
		let uncompressed = H::secp256k1_recover(&commitment_hash.0, &sig.signature)
			.map_err(|_| Error::FailedToRecoverPublicKey)?;

		let hashed_uncompressed = H::keccak256(&uncompressed);

		let mut eth_address = [0u8; 20];
		eth_address.copy_from_slice(&hashed_uncompressed.as_ref()[12..]);

		let authority_address_hash = H::keccak256(&eth_address);

		authority_leaves.push(authority_address_hash.into());
		authority_indices.push(sig.index as usize);
	}

```

**File:** modules/consensus/beefy/verifier/src/lib.rs (L258-261)
```rust
/// Checks for supermajority participation
fn check_participation_threshold(len: u32, total: u32) -> bool {
	len >= ((2 * total) / 3) + 1
}
```

**File:** modules/pallets/beefy-consensus-proofs/src/lib.rs (L805-847)
```rust
		pub fn verify_and_apply(proof: &[u8]) -> Result<VerifyOutcome, Error<T>> {
			let proof_type = *proof.first().ok_or(Error::<T>::UnknownProofType)?;
			let abi_payload = &proof[1..];

			let host = pallet_ismp::Pallet::<T>::default();
			let prev_state_bytes = host
				.consensus_state(ismp_beefy::BEEFY_CONSENSUS_ID)
				.map_err(|_| Error::<T>::NotInitialized)?;
			let prev_state: beefy_verifier_primitives::ConsensusState =
				Decode::decode(&mut &prev_state_bytes[..])
					.map_err(|_| Error::<T>::NotInitialized)?;
			let prev_height = Self::latest_height()?;

			let consensus_proof = match proof_type {
				types::PROOF_TYPE_SP1 => {
					let abi_proof =
						<ismp_abi::sp1_beefy::SP1Beefy::SP1BeefyProof as SolType>::abi_decode_params(
							abi_payload,
						)
						.map_err(|_| Error::<T>::AbiDecodeFailed)?;
					let scale_proof: beefy_verifier_primitives::Sp1BeefyProof = abi_proof.into();
					[&[types::PROOF_TYPE_SP1], scale_proof.encode().as_slice()].concat()
				},
				types::PROOF_TYPE_NAIVE => {
					let abi_proof =
						<ismp_abi::ecdsa_beefy::BeefyConsensusProof as SolType>::abi_decode_params(
							abi_payload,
						)
						.map_err(|_| Error::<T>::AbiDecodeFailed)?;
					let scale_proof: beefy_verifier_primitives::ConsensusMessage = abi_proof.into();
					[&[types::PROOF_TYPE_NAIVE], scale_proof.encode().as_slice()].concat()
				},
				_ => Err(Error::<T>::UnknownProofType)?,
			};

			let result = handlers::handle_incoming_message(
				&host,
				Message::Consensus(IsmpConsensusMessage {
					consensus_proof,
					consensus_state_id: ismp_beefy::BEEFY_CONSENSUS_ID,
					signer: vec![],
				}),
			)
```

**File:** modules/consensus/pharos/primitives/src/spv.rs (L242-244)
```rust
	if proof_nodes.len() > MAX_PROOF_DEPTH {
		return Err(Error::ProofTooDeep);
	}
```

**File:** modules/consensus/pharos/verifier/src/state_proof.rs (L311-313)
```rust
	if count > MAX_VALIDATORS {
		return Err(Error::TooManyValidators { count, max: MAX_VALIDATORS });
	}
```
