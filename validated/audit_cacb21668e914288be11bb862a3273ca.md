### Title
Panic via unchecked fixed-size buffer copy from attacker-controlled BEEFY vote signature length - (File: evm/rust/src/conversions.rs)

### Summary
`evm/rust/src/conversions.rs` converts the ABI-decoded `Vote` struct (used for BEEFY consensus proofs submitted through `pallet-beefy-consensus-proofs` / the `BeefyConsensusProof` proof format) into the internal Rust `SignatureWithAuthorityIndex` type. The conversion copies the ABI `bytes` field `signature` directly into a fixed 65-byte array with `copy_from_slice` without first checking that the input is exactly 65 bytes long, causing a panic on any other length. This mirrors the root cause of CVE-2015-7547: untrusted, attacker-supplied length data is copied into a fixed-size buffer without a length check, producing memory-safety/DoS failure at the copy site.

### Finding Description [1](#0-0) 

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

`Vote.signature` is a Solidity ABI `bytes` field (variable length), decoded from proof data supplied by whoever submits a BEEFY consensus update (`BeefyConsensusProof`/`RelayChainProof.signedCommitment.votes`). `TSignature` is `[u8; 65]` (as used elsewhere for `SignatureWithAuthorityIndex`, e.g. in `modules/consensus/beefy/verifier/src/lib.rs`). `Vec<u8>::copy_from_slice` into a fixed `[u8; 65]` array panics immediately if `sig_bytes.len() != 65` — the standard library requires the destination and source slices to have matching lengths or it aborts with `slice::copy_from_slice: source slice length ... does not match destination slice length`.

This is the exact bug-class described in the CVE: a fixed-size stack/array buffer is populated from network/relay-supplied data whose length is not validated beforehand. In glibc's `send_dg`/`send_vc`, a crafted DNS response with an unexpected size overflowed a fixed stack buffer; here, a crafted BEEFY vote with a signature of any length other than 65 bytes triggers an unchecked-length copy into a fixed array, aborting the runtime thread processing it — the safe-Rust equivalent of the same defect (a panic/crash instead of raw memory corruption, but still an availability failure triggered by the identical missing-length-check pattern).

Every other signature-decoding call site found in this repository defensively checks the length first and returns a typed error otherwise (e.g. `modules/utils/crypto/src/verification.rs:41-47`, `modules/pallets/testsuite/src/tests/pallet_ismp_beefy.rs:114-118` via `try_into().expect(...)` in test code only, `modules/consensus/tendermint/verifier/src/hashing.rs`). This `From<Vote>` conversion is the one path that omits that check and unconditionally panics via `copy_from_slice`.

### Impact Explanation
This conversion is part of the BEEFY consensus proof / vote handling pipeline used to build the internal `SignedCommitment`/`MmrProof` structures consumed by `beefy_verifier_primitives::verify_mmr_update_proof`. BEEFY consensus updates are the mechanism by which the Hyperbridge parachain (and downstream EVM consumers via the mirrored Solidity `EcdsaBeefy`/SP1 proof paths) advance trusted consensus state and thereby unlock message/state verification for the whole protocol. A crash triggered while decoding/converting a malformed vote in this pipeline denies availability of consensus-state updates — a "route unable to deliver messages" condition matching the accepted-impact criteria, since no new heights can be trusted/verified while the affected process keeps crashing on the malformed input, and depending on where in the pipeline this conversion executes (coprocessor/relayer/pallet), it can be a repeatable, permissionless DoS against a node or the on-chain unsigned validation path.

### Likelihood Explanation
The `Vote.signature` field is ABI/SCALE-decoded straight from proof bytes accompanying a consensus update; nothing before this conversion enforces a length of 65 bytes (unlike other call sites in the codebase that check length explicitly before doing fixed-size copies). Any party able to submit or relay a BEEFY consensus proof — a relayer or unsigned-extrinsic submitter, consistent with how other consensus-proof intake paths in this codebase are permissionless (e.g. `pallet_ismp::Call::handle_unsigned`) — can trivially craft a `Vote` with a signature of length ≠ 65 (0, 64, 66, etc.) to hit this panic. This requires no privileged role, no compromised key, and no chain state manipulation — only a single malformed proof submission.

### Recommendation
Validate `value.signature.len() == 65` before calling `copy_from_slice`, returning a typed conversion error (or making the `From` impl a fallible `TryFrom`) instead of panicking, consistent with the length checks already used elsewhere in this codebase (e.g. `modules/utils/crypto/src/verification.rs`, `modules/pallets/ismp/src/utils.rs::from_bytes`). Audit all other `From`/`TryFrom` conversions in `evm/rust/src/conversions.rs` for the same unchecked-copy pattern on attacker-influenced ABI fields (only the `expect()`-based numeric conversions were checked here; array-copy conversions on variable-length `bytes` fields deserve the same audit).

### Proof of Concept
1. Craft a `BeefyConsensusProof`/`RelayChainProof` whose `signedCommitment.votes` array contains a `Vote { authorityIndex: <any>, signature: <bytes of length != 65> }` (e.g. an empty `bytes` or a 64-byte value).
2. Submit this proof through whichever entry point invokes `From<Vote> for SignatureWithAuthorityIndex` (the BEEFY consensus-proof intake path built on `evm/rust` bindings, compiled with the `substrate` feature).
3. `signature.copy_from_slice(&sig_bytes)` panics because `sig_bytes.len() != 65`, aborting the executing thread/process before any cryptographic or supermajority check on the proof is performed.

Note: I was not able to fully confirm, within the available tool calls, the precise runtime boundary (signed vs. unsigned origin) of the specific pallet/coprocessor call that invokes this `From<Vote>` conversion, nor trace every call site that constructs a `Vote` from external proof bytes. This should be verified directly in `modules/pallets/beefy-consensus-proofs/src/lib.rs` and `tesseract/consensus/beefy/` before remediation to confirm the exact permission model of the reachable entry point.

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
