### Title
Unbounded `copy_from_slice` panic on attacker-controlled BEEFY vote signature length - (File: `evm/rust/src/conversions.rs`)

### Summary
`impl From<Vote> for SignatureWithAuthorityIndex` in `evm/rust/src/conversions.rs` (lines 356-366) copies an ABI-decoded, attacker-supplied `bytes` field into a fixed-size `[u8; 65]` array with `copy_from_slice` and no length check. This is the same bug class as CVE-2018-18480 (an unchecked fixed-size read/copy driven by untrusted input length causing a crash), except here the "over-read" manifests as a Rust panic (`copy_from_slice` panics on length mismatch) rather than a heap over-read.

### Finding Description
`pallet_beefy_consensus_proofs::verify_and_apply` (`modules/pallets/beefy-consensus-proofs/src/lib.rs:805-838`) accepts an arbitrary submitted `proof: &[u8]`, splits off a `proof_type` byte, and for `types::PROOF_TYPE_NAIVE` ABI-decodes the remaining bytes as `ismp_abi::ecdsa_beefy::BeefyConsensusProof` via `abi_decode_params`, then converts it into the SCALE `ConsensusMessage` type with `.into()`: [1](#0-0) 

Each `Vote` inside that ABI-decoded structure carries a Solidity `bytes signature` field, which is dynamic-length and fully attacker-controlled since it comes straight from ABI decoding of caller-supplied calldata (this call path is invoked from the unsigned/permissionless `handle_unsigned`/consensus-update flow — anyone can submit a "consensus proof" datagram). The conversion: [2](#0-1) 
does `let mut signature: TSignature = [0u8; 65]; signature.copy_from_slice(&sig_bytes);` with no `sig_bytes.len() == 65` guard. `copy_from_slice` panics immediately if the source slice length differs from the destination (65), which is exactly the analog of `ReadMCHAR`'s unchecked fixed-length read from a variable/attacker-controlled buffer that caused the upstream heap over-read/crash in CVE-2018-18480.

This is also inconsistent with the rest of the codebase, which has systematically hardened equivalent conversions elsewhere (e.g., `to_bytes_32` in `modules/ismp/state-machines/evm/src/utils.rs:118-128` checks length before `copy_from_slice`; the `as_utf8_string` deserializer in `modules/utils/serde/src/lib.rs` was fixed for the identical reason, per its regression test at lines 529-532 noting a prior in-production panic from unchecked length input). The `Vote -> SignatureWithAuthorityIndex` conversion was apparently missed in that hardening pass.

### Impact Explanation
A single attacker submitting a malformed BEEFY "naive"/ECDSA consensus proof (any `Vote.signature` whose byte length isn't exactly 65) causes an unhandled Rust panic inside the runtime call `verify_and_apply` → `handle_incoming_message`. Because this executes inside pallet dispatch (an unsigned extrinsic path is designed to be free/permissionless), a panic here aborts execution of the current transaction; depending on how panics are handled in this WASM runtime context (unwind vs abort), this can at minimum revert the current call and, in the worst case (if executed with `panic = "abort"` semantics, which is common for parachain runtimes), can crash/panic the node's runtime execution for that block, denying consensus-update processing — a route unable to deliver messages, matching the "no vulnerability with no impact" exclusion boundary only if it were purely local; here it hits the core BEEFY consensus verification path that gates all state/message delivery from the source chain, so a successful DoS blocks the relay of proofs and hence bridge liveness.

### Likelihood Explanation
High reachability: this is on the permissionless "prove BEEFY consensus with a naive/ECDSA proof" path, requiring only ABI-encoding a `BeefyConsensusProof` with one `Vote.signature` of the wrong length (e.g., 64 or 66 bytes) and submitting it as an unsigned proof. No privileged role, no prior state, and no race condition is required — it is a pure malformed-input crash, directly analogous to the CVE's "malformed file field length" trigger.

### Recommendation
Validate `sig_bytes.len() == 65` in `impl From<Vote> for SignatureWithAuthorityIndex` (or better, change the conversion to a fallible `TryFrom` that returns an error consumed by `verify_and_apply`/`handlers::handle_incoming_message`), mirroring the pattern already used in `to_bytes_32` and other hardened conversions in this repo, so an invalid signature length is rejected as `Error::AbiDecodeFailed`/`Error::VerificationFailed` rather than panicking.

### Proof of Concept
1. Construct a `BeefyConsensusProof` (Solidity ABI struct consumed by `ismp_abi::ecdsa_beefy::BeefyConsensusProof`) whose `signatures`/`votes` array contains one `Vote` with `signature` set to an arbitrary byte string of length ≠ 65 (e.g., `0x00` repeated 64 times).
2. ABI-encode this struct and prepend the `PROOF_TYPE_NAIVE` discriminator byte, forming the `proof: Vec<u8>` payload expected by `verify_and_apply`.
3. Submit this payload through the permissionless consensus-update extrinsic/message path (`handle_unsigned` → `Self::verify_and_apply` → `handlers::handle_incoming_message` with `Message::Consensus`).
4. Execution reaches `abi_decode_params` (succeeds, since ABI decoding of a dynamic `bytes` field of any length is valid), then the SCALE conversion `scale_proof: beefy_verifier_primitives::ConsensusMessage = abi_proof.into()` triggers `Vote::into()` → `signature.copy_from_slice(&sig_bytes)`, panicking because `sig_bytes.len() != 65`.

### Citations

**File:** modules/pallets/beefy-consensus-proofs/src/lib.rs (L828-836)
```rust
				types::PROOF_TYPE_NAIVE => {
					let abi_proof =
						<ismp_abi::ecdsa_beefy::BeefyConsensusProof as SolType>::abi_decode_params(
							abi_payload,
						)
						.map_err(|_| Error::<T>::AbiDecodeFailed)?;
					let scale_proof: beefy_verifier_primitives::ConsensusMessage = abi_proof.into();
					[&[types::PROOF_TYPE_NAIVE], scale_proof.encode().as_slice()].concat()
				},
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
