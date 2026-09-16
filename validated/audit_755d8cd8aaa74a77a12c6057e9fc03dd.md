### Title
Attacker-controlled BEEFY proof fields cause a runtime panic via unchecked `.expect()`/`copy_from_slice` conversions in `verify_and_apply` (File: `evm/rust/src/conversions.rs`)

### Summary
`pallet_beefy_consensus_proofs::submit_proof` (a **signed** extrinsic, callable by anyone) decodes a caller-supplied ABI payload into a `BeefyConsensusProof` / `ConsensusMessage` and passes it into `handlers::handle_incoming_message`, which for the naive path calls `.into()` on Solidity-ABI-decoded structs (`Commitment`, `Vote`, `RelayChainProof`, etc.) via the `From` impls in `evm/rust/src/conversions.rs`. Several of these conversions use `.expect(...)` on `try_into()` and a raw `copy_from_slice` that panics on any length mismatch, rather than returning a typed error.

### Finding Description
`pallet_beefy_consensus_proofs::verify_and_apply` (`modules/pallets/beefy-consensus-proofs/src/lib.rs:805-838`) ABI-decodes an attacker-controlled `abi_payload` into `ismp_abi::ecdsa_beefy::BeefyConsensusProof` for `PROOF_TYPE_NAIVE`, then calls `scale_proof: beefy_verifier_primitives::ConsensusMessage = abi_proof.into();` before ever running any cryptographic verification (`beefy_verifier::verify_consensus`). This `.into()` conversion chain routes through `evm/rust/src/conversions.rs`, where multiple `From` impls panic on malformed-but-ABI-decodable input:

- `From<Commitment> for SpCommitment` (line 334-354): `value.payload.into_iter().next().expect("commitment has at least one payload entry")` — panics if the attacker submits a `Commitment` with an **empty payload array** (a valid, ABI-decodable but semantically empty `Payload[]`).
- `From<Vote> for SignatureWithAuthorityIndex` (line 356-366): `signature.copy_from_slice(&sig_bytes)` into a fixed `[u8; 65]` **panics if `sig_bytes.len() != 65`** — the ABI type for `Vote.signature` is a dynamic `bytes`, so an attacker can submit any length.
- Multiple `.try_into().expect("... out of bounds")` calls (`blockNumber`, `validatorSetId`, `authorityIndex`, MMR-leaf fields, etc.) panic when the attacker supplies `U256` values exceeding `u32`/`u64` range.

All of this data originates from the raw bytes the caller passes to the public `submit_proof` extrinsic — this is exactly the "improper cleanup upon a thrown exception" pattern in CVE-2022-37428: malformed-but-parseable input reaches deep conversion logic and throws before the code path can cleanly reject it, aborting the runtime's execution of the extrinsic (a Substrate panic inside a dispatchable is caught by `frame_support`'s panic handler and turned into a failed block/`Invalid Transaction`, but repeated submission is trivial and cheap, and worse, a panic during block execution — as opposed to pool validation — can disrupt collator/validator execution rather than being cleanly rejected by `ValidateUnsigned`).

### Impact Explanation
Because `submit_proof` is a signed extrinsic reachable by any account with a minimal balance, an attacker can craft a `BeefyConsensusProof` ABI payload with an empty `Commitment.payload` array or an oversized `Vote.signature`/`U256` field and trigger a panic deep inside consensus-message conversion, before any cryptographic check runs. This is a Medium-severity availability issue: it does not directly cause fund loss, but it allows cheap, repeatable denial-of-service against the BEEFY consensus proof submission pipeline, analogous to CVE-2022-37428 where a crafted DNS answer property caused a daemon crash before proper cleanup. Given the codebase otherwise contains many hardened, deliberately-fixed analogs of this exact bug class (index-out-of-bounds panics on adversarial proofs in GRANDPA, sync-committee, ethereum trie, and pharos verifiers — all converted to typed `Result` errors with explicit regression tests), this file appears to be an overlooked instance of the same pattern that was not swept in those hardening passes.

### Likelihood Explanation
High likelihood of triggerability: no cryptographic proof is required to reach the panic — merely well-formed ABI encoding of a `BeefyConsensusProof` with the pathological field values described above. The attacker only needs a funded account to submit the extrinsic.

### Recommendation
Replace the `.expect(...)` calls and the raw `copy_from_slice` in `evm/rust/src/conversions.rs` (`From<Commitment> for SpCommitment`, `From<Vote> for SignatureWithAuthorityIndex`, and the other `try_into().expect(...)` conversions in this module) with fallible `TryFrom` implementations that return a typed `beefy_verifier::error::Error` (or equivalent), matching the pattern already used in `modules/consensus/grandpa/verifier/src/error.rs` and `modules/consensus/pharos/primitives/src/spv.rs` for the same bug class. Then update `verify_and_apply` in `modules/pallets/beefy-consensus-proofs/src/lib.rs` to propagate the conversion error as `Error::<T>::AbiDecodeFailed` or a new variant instead of allowing an unwind.

### Proof of Concept
1. Construct a `BeefyConsensusProof` (per `ismp_abi::ecdsa_beefy::BeefyConsensusProof`) whose naive-path `Commitment.payload` field is an empty array (still ABI-valid: a zero-length dynamic array).
2. Prefix the ABI-encoded proof bytes with `PROOF_TYPE_NAIVE`.
3. Submit as a signed extrinsic to `pallet_beefy_consensus_proofs::submit_proof`.
4. `verify_and_apply` decodes the payload successfully via `abi_decode_params`, then calls `scale_proof: ConsensusMessage = abi_proof.into()`, which reaches `From<Commitment> for SpCommitment` and panics at `value.payload.into_iter().next().expect("commitment has at least one payload entry")` before any signature/finality check executes.

Note: I was not able to directly confirm from the index whether Substrate's panic-handler / `#[frame_support::transactional]` wraps this specific dispatchable in a way that fully contains the panic without further side effects (e.g., block-execution abort vs. clean extrinsic failure) — a Devin session with full repository access and a running test harness would be needed to demonstrate the exact runtime behavior (reverted block vs. panic-aborted node) and confirm severity precisely. [1](#0-0) [2](#0-1) [3](#0-2) [4](#0-3)

### Citations

**File:** evm/rust/src/conversions.rs (L334-354)
```rust
	impl From<Commitment> for SpCommitment {
		/// BEEFY commitment reconstruction. Reassembles the `Payload` from its
		/// `(id, data)` entries, starting with the first entry and pushing the rest via
		/// `push_raw` (which re-sorts by id to keep the invariant `Payload` expects).
		fn from(value: Commitment) -> Self {
			let mut iter = value.payload.into_iter();
			let first = iter.next().expect("commitment has at least one payload entry");
			let mut payload = BeefyPayload::from_single_entry(first.id.0, first.data.to_vec());
			for p in iter {
				payload = payload.push_raw(p.id.0, p.data.to_vec());
			}
			sp_consensus_beefy::Commitment {
				payload,
				block_number: value.blockNumber.try_into().expect("block number out of bounds"),
				validator_set_id: value
					.validatorSetId
					.try_into()
					.expect("validator set id out of bounds"),
			}
		}
	}
```

**File:** evm/rust/src/conversions.rs (L356-366)
```rust
	impl From<Vote> for SignatureWithAuthorityIndex {
		fn from(value: Vote) -> Self {
			let sig_bytes = value.signature.to_vec();
			let mut signature: TSignature = [0u8; 65];
			signature.copy_from_slice(&sig_bytes);
			SignatureWithAuthorityIndex {
				signature,
				index: value.authorityIndex.try_into().expect("authority index out of bounds"),
			}
		}
	}
```

**File:** modules/pallets/beefy-consensus-proofs/src/lib.rs (L16-27)
```rust
//! # Pallet BEEFY Consensus Proofs
//!
//! Verifies BEEFY consensus proofs (primarily SP1 ZK) submitted by off-chain provers and
//! feeds the finalized parachain state commitments into `pallet-ismp`. Rewards submitters
//! from the treasury when a proof does useful work — either carries the expected next
//! authority-set rotation, or advances the latest proven parachain height past a block
//! in which new ISMP requests were dispatched.
//!
//! Proofs are submitted via **signed** extrinsics: the signer of the extrinsic is the
//! reward payee. The pallet sets `Pays::No` on accepted proofs so a successful prover
//! gets their fee refunded along with the reward; failed proofs pay the transaction
//! fee normally, which keeps spam off the chain.
```

**File:** modules/pallets/beefy-consensus-proofs/src/lib.rs (L805-838)
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
```
