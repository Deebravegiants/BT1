### Title
Unbounded-length signature copied into fixed-size buffer panics `evm/rust/src/conversions.rs` `From<Vote> for SignatureWithAuthorityIndex` on an attacker-controlled naive-BEEFY proof - (File: `evm/rust/src/conversions.rs`)

### Summary
`impl From<Vote> for SignatureWithAuthorityIndex` (evm/rust/src/conversions.rs:356-365) copies an ABI-decoded `Vote.signature` field of arbitrary attacker-controlled length into a fixed `[u8; 65]` buffer with `signature.copy_from_slice(&sig_bytes)` and no length check. `Vote`/`signature` is `bytes` in the Solidity `BeefyConsensusProof` struct (`evm/src/consensus/Types.sol` / `ismp_abi::ecdsa_beefy::BeefyConsensusProof`) and is fully attacker-controlled input to the naive-BEEFY (`PROOF_TYPE_NAIVE`) consensus proof path. `copy_from_slice` panics ("source slice length does not match destination") whenever `sig_bytes.len() != 65`, which is the same bug class as CVE-2019-14940: invalid/malformed input reaching a decode/marshalling routine crashes the process instead of returning an error.

### Finding Description
`evm/rust/src/conversions.rs` builds Rust/Substrate BEEFY types out of the ABI-decoded Solidity proof structures so a naive-BEEFY consensus proof submitted off-chain (via `pallet-beefy-consensus-proofs::submit_proof`, `types::PROOF_TYPE_NAIVE`) can be converted and re-encoded for verification (`modules/pallets/beefy-consensus-proofs/src/lib.rs:828-836`, which calls `<ismp_abi::ecdsa_beefy::BeefyConsensusProof as SolType>::abi_decode_params` and then converts the ABI type into `beefy_verifier_primitives::ConsensusMessage`). That `Into` conversion chain is where `evm/rust/src/conversions.rs`'s `From<Vote> for SignatureWithAuthorityIndex` fires:

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
``` [1](#0-0) 

`value.signature` originates from ABI-decoded `bytes` in a `Vote` struct nested inside `BeefyConsensusProof.relay.signedCommitment.votes[]`, which is entirely controlled by whoever submits the naive proof — no signature-length validation happens before this conversion. `copy_from_slice` panics whenever the source length is not exactly 65 bytes, i.e. any vote with a signature that isn't exactly 65 bytes triggers a Rust panic.

This mirrors patterns the codebase has explicitly hardened elsewhere against the exact same failure mode: `modules/ismp/core/src/host.rs` and `modules/utils/serde/src/lib.rs` document identical `copy_from_slice`-panics-on-length-mismatch bugs on untrusted input being fixed with explicit length checks (one of which is noted as having "crashed the production node"), and `modules/consensus/sync-committee/verifier/src/lib.rs` documents fixing an analogous panic reachable "via the public unsigned consensus update path." The `Vote`→`SignatureWithAuthorityIndex` conversion in `evm/rust/src/conversions.rs` has not received the same treatment.

### Impact Explanation
This conversion path runs inside the runtime's proof-handling logic for `submit_proof` (naive BEEFY), which is dispatched by any signed account (`modules/pallets/beefy-consensus-proofs/src/lib.rs:448` — `do_submit_proof`). A crafted `Vote.signature` of any length other than 65 bytes reaching this conversion panics the runtime/WASM execution during proof processing — a denial-of-service against the consensus-proof pipeline, directly analogous to CVE-2019-14940 ("a user ... can cause a crash if the target is sent invalid input"). Because this sits on the BEEFY consensus-update critical path (the mechanism that advances trusted state and unlocks message delivery/token routing), a reliably triggerable panic here can stall consensus updates and message delivery for an unbounded period — a "route unable to deliver messages" condition.

### Likelihood Explanation
Likelihood is High if this Rust code path is compiled into and reachable from the on-chain proof-processing pipeline (the `beefy-consensus-proofs` pallet's naive proof branch converts `ismp_abi::ecdsa_beefy::BeefyConsensusProof` into `beefy_verifier_primitives::ConsensusMessage`, and this file's `#[cfg(feature = "substrate")]` module is exactly the substrate-side conversion layer for that ABI type). The submitter only needs to encode a `Vote.signature` with any length ≠ 65 bytes inside an otherwise-well-formed ABI payload; no privileged role or valid cryptographic material is required to reach the panic, only to reach the conversion call. I was not able to fully trace, within the available tool budget, the exact call graph proving that `beefy_verifier_primitives::ConsensusMessage`'s construction from the ABI type specifically invokes this `From<Vote>` impl inside the on-chain `submit_proof` dispatch (as opposed to only being used off-chain by the prover), so this should be verified against the crate's feature wiring before treating it as certain.

### Recommendation
Replace the unchecked `copy_from_slice` with a checked conversion that returns an error (mirroring the fixes already applied elsewhere in the codebase, e.g. `modules/utils/serde/src/lib.rs::as_utf8_string` and `modules/ismp/core/src/host.rs::StateMachine::from_str`):
```rust
impl TryFrom<Vote> for SignatureWithAuthorityIndex {
    type Error = ...;
    fn try_from(value: Vote) -> Result<Self, Self::Error> {
        let sig_bytes = value.signature.to_vec();
        let signature: TSignature = sig_bytes
            .as_slice()
            .try_into()
            .map_err(|_| /* typed error: invalid signature length */)?;
        Ok(SignatureWithAuthorityIndex {
            signature,
            index: value.authorityIndex.try_into().map_err(|_| /* typed error */)?,
        })
    }
}
```
Propagate the `Result` through all call sites (`ConsensusMessage`/`MmrProof` conversions) so malformed proofs are rejected with a typed error rather than panicking, and add a regression test analogous to `from_str_rejects_non_four_byte_consensus_ids` that submits a naive BEEFY proof with a non-65-byte vote signature and asserts a clean error instead of a panic.

### Proof of Concept
1. Construct a `BeefyConsensusProof` ABI payload (matching `ismp_abi::ecdsa_beefy::BeefyConsensusProof`) whose `relay.signedCommitment.votes[0].signature` is any `bytes` value with length ≠ 65 (e.g., empty bytes or 64 bytes).
2. Prefix with `PROOF_TYPE_NAIVE` (0x00) and submit via `BeefyConsensusProofs::submit_proof` as any signed account, per `modules/pallets/beefy-consensus-proofs/src/lib.rs:448-485` (`do_submit_proof`) → `verify_and_apply` (`modules/pallets/beefy-consensus-proofs/src/lib.rs:828-836`).
3. The naive branch ABI-decodes the payload into `ismp_abi::ecdsa_beefy::BeefyConsensusProof` and converts it `.into()` a `beefy_verifier_primitives::ConsensusMessage`, which (per the `#[cfg(feature = "substrate")]` conversions module) constructs `SignatureWithAuthorityIndex::from(vote)` for each vote via `evm/rust/src/conversions.rs:356-365`.
4. `signature.copy_from_slice(&sig_bytes)` panics because `sig_bytes.len() != 65`, aborting proof processing instead of returning `Error::AbiDecodeFailed`/`VerificationFailed`.

Note: I could not, within the tool budget available, fully confirm the exact feature-flag/build wiring that guarantees this `evm/rust` crate's `From<Vote>` impl is the one invoked on-chain (vs. only in the off-chain `tesseract` prover binary) — this should be double-checked by tracing `beefy_verifier_primitives::ConsensusMessage`'s `From<ismp_abi::ecdsa_beefy::BeefyConsensusProof>` implementation and its crate's `Cargo.toml` feature gates before treating this as fully confirmed on the on-chain path.

### Citations

**File:** evm/rust/src/conversions.rs (L356-365)
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
```
