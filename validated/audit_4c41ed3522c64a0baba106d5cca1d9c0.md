This confirms the finding: `From<RelayChainProof> for MmrProof` (used to convert an externally-submitted `RelayChainProof` from the EVM BEEFY consensus client, `evm/rust/src/conversions.rs:368-389`) maps `signedCommitment.votes` (attacker-controlled `Vote[]`, each holding an arbitrary-length `bytes signature`) through `Into::into`, which resolves to `From<Vote> for SignatureWithAuthorityIndex` at `evm/rust/src/conversions.rs:356-366`. That conversion does `signature.copy_from_slice(&sig_bytes)` into a fixed `[0u8; 65]` array without checking `sig_bytes.len() == 65` first.

### Title
Unchecked length `copy_from_slice` on attacker-controlled BEEFY vote signature causes panic-based denial of service - (File: evm/rust/src/conversions.rs)

### Summary
`From<Vote> for SignatureWithAuthorityIndex` copies a caller-supplied, variable-length Solidity `bytes signature` field into a fixed `[u8; 65]` array using `copy_from_slice` without first validating the length, mirroring the nanoMODBUS root cause (writing untrusted-length data into a fixed buffer before validating the length matches expectations).

### Finding Description
`RelayChainProof.signedCommitment.votes` is a `Vote[]` decoded from calldata/proof bytes submitted to the BEEFY consensus client (`Vote { signature: bytes, authorityIndex: uint256 }`, declared in `evm/src/consensus/Types.sol`). Nothing in the Solidity ABI type or the Rust conversion path enforces that `signature` is exactly 65 bytes before `From<Vote> for SignatureWithAuthorityIndex` runs: [1](#0-0) 
This is reached from `From<RelayChainProof> for MmrProof`, which maps every vote in the submitted commitment through this conversion: [2](#0-1) 
If `sig_bytes.len() != 65` (either shorter or longer than 65), `copy_from_slice` panics immediately (`source slice length (N) does not match destination slice length (65)`), rather than returning a decode/verification error.

### Impact Explanation
Unlike the nanoMODBUS CVE (C stack overflow enabling RCE), Rust's `copy_from_slice` performs a length check and panics rather than corrupting memory — there is no memory-safety/RCE impact here. However, an unauthenticated party submitting a consensus/relay-chain proof to the BEEFY light client can trigger a Rust panic during proof conversion before any cryptographic signature verification occurs, since this is a light-client-side host conversion path invoked ahead of `beefy_verifier_primitives` verification logic. Depending on how this code is compiled/executed (e.g., inside a relayer binary, a prover service, or an FFI/host function bridging to the on-chain verifier), an unrecoverable panic can abort the calling process/thread, denying service to whatever component performs BEEFY proof conversion for that submission — a relayer or node process. This does not itself allow theft of funds, forged messages, or unsound state commitment (verification hasn't happened yet, and a panic aborts the whole update, so it can't be exploited to slip forged data through), so it falls short of the "concrete theft/forged delivery/unsound commitment" bar in the validation rules; the reachable, provable impact is process-level DoS in the proof-conversion path.

### Likelihood Explanation
Likelihood is high for triggering the panic in principle: it only requires a `Vote.signature` field of any length other than 65 bytes, which is trivial to construct in the ABI encoding of `RelayChainProof`. But whether this Rust conversion code executes in a persistent, crash-sensitive process (vs. being invoked per-call in a way that isolates panics, or being unreachable because upstream code already validates commitment signatures/lengths before calling `.into()`) could not be fully confirmed — I was not able to trace the exact caller that invokes `From<RelayChainProof> for MmrProof` (i.e., where the on-chain/off-chain BEEFY proof submission entry point lives and whether it wraps this conversion in panic-safe boundaries such as `catch_unwind` or WASM/host-call isolation).

### Recommendation
Validate `value.signature.len() == 65` in `From<Vote> for SignatureWithAuthorityIndex` (or better, change the conversion to a fallible `TryFrom` returning an error) before calling `copy_from_slice`, consistent with the fix pattern already used elsewhere in this codebase (e.g., `ByteVector<N>::decode` rejecting non-`N`-length input, and `decode_address_from_storage_value` bounding RLP-decoded lengths before padding/copying) — see the length-validation pattern at `modules/utils/bls-utils/src/ssz/byte_vector.rs:48-56`.

### Proof of Concept
Construct a `RelayChainProof` ABI payload whose `signedCommitment.votes[0].signature` is any length other than 65 bytes (e.g., 0 or 64 bytes) and submit it through whatever entry point calls `From<RelayChainProof> for MmrProof` for BEEFY proof processing; the conversion panics at `signature.copy_from_slice(&sig_bytes)` (`evm/rust/src/conversions.rs:360`) before any BEEFY signature/threshold verification is performed.

**Confidence caveat:** I could not verify the exact call site/binary that invokes `From<RelayChainProof> for MmrProof` (e.g., whether it's a relayer CLI, an SP1 program, or FFI boundary with panic isolation), which affects whether this DoS is remotely triggerable against a persistent service or only crashes an isolated per-request worker. A Devin session with full repo/build access would be needed to trace this call graph precisely.

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

**File:** evm/rust/src/conversions.rs (L368-389)
```rust
	impl From<RelayChainProof> for MmrProof {
		fn from(value: RelayChainProof) -> Self {
			let leaf_index: u64 =
				value.latestMmrLeaf.leafIndex.try_into().expect("mmr leaf index out of bounds");
			let items: Vec<H256> = value.mmrProof.into_iter().map(|h| H256(h.0)).collect();
			let mmr_proof = LeafProof {
				leaf_indices: vec![leaf_index],
				leaf_count: leaf_index.saturating_add(1),
				items,
			};

			MmrProof {
				signed_commitment: BvpSignedCommitment {
					commitment: value.signedCommitment.commitment.into(),
					signatures: value.signedCommitment.votes.into_iter().map(Into::into).collect(),
				},
				latest_mmr_leaf: value.latestMmrLeaf.into(),
				mmr_proof,
				authority_proof: value.proof.into_iter().map(|h| h.0).collect(),
			}
		}
	}
```
