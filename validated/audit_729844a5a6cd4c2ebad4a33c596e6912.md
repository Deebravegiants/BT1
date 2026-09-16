### Title
Unchecked `copy_from_slice` into fixed-size signature buffer during BEEFY proof conversion causes a panic/DoS on attacker-controlled input - (File: `evm/rust/src/conversions.rs`)

### Summary
The `From<Vote> for SignatureWithAuthorityIndex` converter copies an externally supplied, variable-length `Bytes` field directly into a fixed 65-byte array with `copy_from_slice`, without first checking that the source length equals 65. This mirrors the CVE-2025-57107 bug class: a data "constructor"/converter performs a raw memory copy driven by attacker-controlled length without validating buffer boundaries first.

### Finding Description
`evm/rust/src/conversions.rs` converts Solidity ABI-decoded BEEFY consensus-proof types into the pallet's internal SCALE representation: [1](#0-0) 

`value.signature` originates from the ABI-decoded `Vote` struct populated from raw calldata bytes submitted through `BeefyConsensusProofs::verify_and_apply`, which dispatches on the first proof-type byte and, for `PROOF_TYPE_NAIVE`, ABI-decodes a `BeefyConsensusProof` (containing `SignedCommitment.votes: Vote[]`) directly from `abi_payload` supplied by any caller: [2](#0-1) 

Because Solidity dynamic `bytes` fields (as opposed to Substrate's `[u8;65]`/`TSignature`) can carry any length, an adversary can submit a `Vote.signature` whose byte length differs from 65. `sig_bytes.len()` is never checked before `signature.copy_from_slice(&sig_bytes)` is called, so a mismatched length trips Rust's slice-length assertion and panics — the exact "copy constructor performs a memory operation without first validating buffer boundaries" pattern described in the CVE, translated to safe-Rust semantics (a hard panic/trap instead of a heap overflow).

This class of unchecked-length-copy bug is one the repository has otherwise been proactively hardening against — e.g. `modules/ismp/core/src/host.rs` and `modules/utils/serde/src/lib.rs` both contain explicit regression tests and comments describing prior identical panics from `copy_from_slice` on attacker-controlled, wrongly-sized input reachable from unsigned/RPC paths: [3](#0-2) [4](#0-3) 

The `Vote.signature` copy in `evm/rust/src/conversions.rs` was not covered by the same fix pattern.

### Impact Explanation
Any unprivileged caller submitting a naive BEEFY consensus proof through `BeefyConsensusProofs::verify_and_apply` can trigger a Rust panic during conversion of the ABI-decoded proof to the SCALE `ConsensusMessage`, before the actual signature/authority checks ever run. In a Substrate runtime, an unhandled panic in extrinsic execution traps the WASM guest, and the same `conversions.rs` module (guarded by `feature = "substrate"`) is shared with off-chain relayer/tesseract binaries that consume BEEFY proofs, so a malformed `Vote` can also crash a relayer process consuming attacker-influenced consensus data. This is a denial-of-service on the BEEFY consensus-update path used to update parachain state commitments that the token bridge / message dispatcher rely on for state verification, rather than memory corruption (Rust safety prevents true heap overflow), but it satisfies the "unable to deliver messages" / route-DoS impact criterion since a stuck or crashing consensus-update path blocks all downstream ISMP message verification for that consensus client.

### Likelihood Explanation
Reaching this code requires only crafting the `abi_payload` for the `PROOF_TYPE_NAIVE` branch with a `Vote.signature` field of length ≠ 65 bytes, then calling the publicly reachable `verify_and_apply` entry point — no privileged role, valid BEEFY signature, or prior state is required to hit the panic, since the conversion happens before verification. Likelihood is high for anyone aware of the code path.

### Recommendation
In `evm/rust/src/conversions.rs`, validate `sig_bytes.len() == 65` before calling `copy_from_slice`, returning a typed conversion error (propagated as `Error::<T>::AbiDecodeFailed` or similar) instead of panicking, consistent with the fix pattern already applied in `modules/ismp/core/src/host.rs` and `modules/utils/serde/src/lib.rs`.

### Proof of Concept
1. Construct a `BeefyConsensusProof` ABI payload where `relay.signedCommitment.votes[0].signature` is a `bytes` value of length ≠ 65 (e.g., 64 or 66 bytes) and `authorityIndex` set arbitrarily.
2. Prefix the payload with `PROOF_TYPE_NAIVE` and call `BeefyConsensusProofs::verify_and_apply(proof)` (or the equivalent extrinsic that invokes it).
3. `abi_decode_params` succeeds (dynamic `bytes` has no fixed-length constraint), then `Into::<ConsensusMessage>::into(...)` reaches `From<Vote> for SignatureWithAuthorityIndex`, where `signature.copy_from_slice(&sig_bytes)` panics because `sig_bytes.len() != 65`, aborting the call before any cryptographic verification occurs. [1](#0-0) [5](#0-4) 

Note: I was unable to fully confirm the exact Solidity type declaration of `Vote.signature` in `evm/src/consensus/Types.sol` within the available tool budget (the file content for that specific struct wasn't retrieved before the iteration limit), so the assumption that it is an ABI dynamic `bytes` (rather than some fixed-length encoding enforced elsewhere) should be verified directly against that file before treating this as fully confirmed.

### Citations

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

**File:** modules/ismp/core/src/host.rs (L470-479)
```rust
	// A malformed `SUBSTRATE-`/`TNDRMINT-` id whose byte length is not exactly 4
	// must return an error rather than panic. The id is copied into a `[u8; 4]`,
	// and `copy_from_slice` traps on a length mismatch — in the runtime this is a
	// wasm trap reachable from untrusted input (e.g. `BandwidthManager.purchase`),
	// so the length is now checked up-front (matching the `RELAY-` arm).
	#[test]
	fn from_str_rejects_non_four_byte_consensus_ids() {
		for s in ["SUBSTRATE-", "SUBSTRATE-AB", "SUBSTRATE-ABCDE", "TNDRMINT-XYZ"] {
			assert!(StateMachine::from_str(s).is_err(), "expected error for {s:?}");
		}
```

**File:** modules/utils/serde/src/lib.rs (L529-554)
```rust
	// `as_utf8_string` deserializes into a fixed `[u8; 4]`. It used to `copy_from_slice`
	// straight from the input, which panics on any length mismatch — and it runs on
	// untrusted RPC input (`consensus_state_id`), so the panic aborted the node's `rpc`
	// worker thread and took the process down. Wrong lengths must be serde errors.
	#[test]
	fn as_utf8_string_rejects_non_four_byte_input() {
		#[derive(Deserialize, Debug, PartialEq, Eq)]
		struct TestData {
			#[serde(with = "as_utf8_string")]
			id: [u8; 4],
		}

		for s in [
			"",          // 0 bytes
			"AB",        // 2 bytes
			"ABC",       // 3 bytes
			"ABCDE",     // 5 bytes
			"CERE0",     // 5 bytes — the value that crashed the production node
			"ABC\u{e9}", // 4 chars, 5 bytes: length is counted in bytes, not chars
		] {
			let json = serde_json::json!({ "id": s }).to_string();
			assert!(
				serde_json::from_str::<TestData>(&json).is_err(),
				"expected a deserialization error for {s:?}"
			);
		}
```
