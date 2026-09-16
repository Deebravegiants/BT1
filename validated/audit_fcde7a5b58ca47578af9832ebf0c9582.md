## Title
Unchecked fixed-size signature buffer copy in BEEFY `Vote → SignatureWithAuthorityIndex` conversion causes a runtime panic on attacker-controlled proof input - (File: `evm/rust/src/conversions.rs`)

### Summary
`impl From<Vote> for SignatureWithAuthorityIndex` copies an ABI-decoded, attacker-controlled `bytes` field directly into a fixed 65-byte array using `copy_from_slice` without first validating its length. [1](#0-0) 

### Finding Description
`Vote.signature` is declared as Solidity `bytes` (unbounded length) inside `SignedCommitment`/`RelayChainProof`/`BeefyConsensusProof`, which is exactly the payload an unprivileged relayer supplies as the naive BEEFY consensus proof (`PROOF_TYPE_NAIVE`). [2](#0-1) 

The conversion path is: `pallet-beefy-consensus-proofs::verify_and_apply` ABI-decodes the submitted `proof` bytes into `BeefyConsensusProof` and converts it with `.into()` into the SCALE `ConsensusMessage`, which flows through `From<Vote> for SignatureWithAuthorityIndex`. [3](#0-2) 

That conversion does:
```rust
let sig_bytes = value.signature.to_vec();
let mut signature: TSignature = [0u8; 65];
signature.copy_from_slice(&sig_bytes);
```
`copy_from_slice` panics if `sig_bytes.len() != 65`. Since `signature` is an arbitrary-length `bytes` field decoded straight from calldata, an attacker submitting `submit_proof` with a signature of any length other than exactly 65 bytes triggers this panic before any cryptographic/consensus check on the signature is performed. [1](#0-0) 

This is the direct Rust analog of the CVE's root cause: a fixed-size destination buffer written from externally-controlled, unvalidated-length source data. In C (`mdb_numeric_to_string`) that manifests as stack memory corruption; in safe Rust it manifests as a length-checked panic, but the trigger condition, root cause pattern, and exploitability by any transaction submitter are the same.

Every other struct-to-struct conversion in this file (`try_into().expect(...)`) shares the same "unwrap/expect on attacker data" anti-pattern, but those operate on scalar `U256 → u32/u64` fields where the runtime already validates ranges elsewhere in most paths; the `Vote` signature conversion is the one doing a raw, unchecked `copy_from_slice` from a variable-length byte vector into a fixed array, making it the closest match to the CVE's buffer-overflow bug class.

### Impact Explanation
A single unprivileged extrinsic (`BeefyConsensusProofs::submit_proof` with `PROOF_TYPE_NAIVE` and a malformed vote signature length) causes the runtime to panic during consensus proof processing. Because this executes inside a signed/unsigned transaction validated by the runtime's `handle_incoming_message` → `verify_and_apply` pipeline, an uncaught panic there can abort execution of the extrinsic in a way that is not gracefully handled as a `DispatchError`, unlike the rest of the pallet's carefully typed `Error<T>` variants. This can be leveraged to repeatedly disrupt BEEFY consensus-proof submission, potentially stalling delivery of new consensus state and blocking the relayer route that consensus proofs depend on ("a route unable to deliver messages"), rather than a memory-corruption / fund-theft primitive as in the original C CVE.

### Likelihood Explanation
High from a reachability standpoint: `submit_proof` is callable by any account (the ISMP/BEEFY-consensus-proofs extrinsic is meant to accept relayer-submitted proofs), and constructing a `Vote.signature` of an incorrect length (e.g., 0, 64, or 66 bytes) via standard ABI encoding requires no special privileges or cryptographic material — it does not even need to be a validly-signed vote, since the length check happens before any signature verification.

### Recommendation
Validate `value.signature.len() == 65` (or use `TryInto<[u8; 65]>`) in `From<Vote> for SignatureWithAuthorityIndex` and propagate a typed decode error instead of panicking, mirroring the fix already applied elsewhere in the codebase (e.g. `as_utf8_string::deserialize` and `ByteVector<N>::decode`, both of which were hardened specifically because `copy_from_slice` panics on untrusted-length input). [4](#0-3) [5](#0-4) 

### Proof of Concept
1. Craft `BeefyConsensusProof` ABI bytes where `relay.signedCommitment.votes[0].signature` is set to a `bytes` value of length ≠ 65 (e.g., 64 or 0 bytes) — trivially constructible with standard ABI encoders, no signing key needed.
2. Prefix with `PROOF_TYPE_NAIVE` and submit via `BeefyConsensusProofs::submit_proof(proof)`.
3. `verify_and_apply` ABI-decodes the proof and calls `.into()` on it, which calls `From<RelayChainProof> for MmrProof` → `From<Vote> for SignatureWithAuthorityIndex`, executing `signature.copy_from_slice(&sig_bytes)` with a mismatched length and panicking. [6](#0-5) [7](#0-6)

### Citations

**File:** evm/rust/src/conversions.rs (L146-184)
```rust
	impl From<MmrProof> for RelayChainProof {
		fn from(value: MmrProof) -> Self {
			let leaf_index = value.mmr_proof.leaf_indices[0];

			RelayChainProof {
				signedCommitment: SignedCommitment {
					commitment: value.signed_commitment.commitment.into(),
					votes: value
						.signed_commitment
						.signatures
						.into_iter()
						.map(|a| Vote {
							signature: Bytes::from(a.signature.to_vec()),
							authorityIndex: a.index.to_u256(),
						})
						.collect(),
				},
				latestMmrLeaf: BeefyMmrLeaf {
					version: 0,
					parentNumber: value.latest_mmr_leaf.parent_number_and_hash.0,
					parentHash: FixedBytes::from(value.latest_mmr_leaf.parent_number_and_hash.1 .0),
					nextAuthoritySet: value.latest_mmr_leaf.beefy_next_authority_set.into(),
					extra: FixedBytes::from(value.latest_mmr_leaf.leaf_extra.0),
					leafIndex: leaf_index.to_u256(),
				},
				mmrProof: value
					.mmr_proof
					.items
					.into_iter()
					.map(|h| FixedBytes::from(h.0))
					.collect(),
				proof: value
					.authority_proof
					.into_iter()
					.map(|hash| FixedBytes::from(hash))
					.collect(),
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

**File:** evm/src/consensus/Types.sol (L141-174)
```text
struct Vote {
    // secp256k1 signature from a member of the authority set
    bytes signature;
    // 0-based index of the authority in the authority set
    uint256 authorityIndex;
}

// The signed commitment holds a commitment to the latest
// finalized state as well as votes from a supermajority
// of the authority set which confirms this state
struct SignedCommitment {
    // A commitment to the finalized state
    Commitment commitment;
    // The confirming votes
    Vote[] votes;
}

struct RelayChainProof {
    // Signed commitment
    SignedCommitment signedCommitment;
    // Latest leaf added to mmr
    BeefyMmrLeaf latestMmrLeaf;
    // Proof for the latest mmr leaf
    bytes32[] mmrProof;
    // Proof for authorities in current/next session
    bytes32[] proof;
}

struct BeefyConsensusProof {
    // The proof items for the relay chain consensus
    RelayChainProof relay;
    // Proof items for parachain headers
    ParachainProof parachain;
}
```

**File:** modules/pallets/beefy-consensus-proofs/src/lib.rs (L818-838)
```rust
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

**File:** modules/utils/serde/src/lib.rs (L118-136)
```rust
	/// Deserialize a string into utf8 bytes
	///
	/// The string must be exactly 4 bytes long (bytes, not chars — a 4-char string of
	/// multi-byte codepoints is rejected). Anything else is a deserialization error; this
	/// runs on untrusted RPC input, so it must never panic.
	pub fn deserialize<'de, D, T>(deserializer: D) -> Result<T, D::Error>
	where
		D: serde::Deserializer<'de>,
		T: From<[u8; 4]>,
	{
		let s = <String>::deserialize(deserializer)?;

		// `s.len()` is the utf-8 byte length, which is what the `[u8; 4]` needs to match.
		let bytes: [u8; 4] = s
			.as_bytes()
			.try_into()
			.map_err(|_| serde::de::Error::invalid_length(s.len(), &"a 4-byte utf-8 string"))?;
		Ok(bytes.into())
	}
```

**File:** modules/utils/bls-utils/src/ssz/byte_vector.rs (L48-57)
```rust
impl<const N: usize> codec::Decode for ByteVector<N> {
	fn decode<I: codec::Input>(input: &mut I) -> Result<Self, codec::Error> {
		let bytes = Vec::<u8>::decode(input)?;
		if bytes.len() != N {
			return Err(codec::Error::from("ByteVector: decoded length does not equal N"));
		}
		ByteVector::<N>::try_from(bytes)
			.map_err(|_| codec::Error::from("ByteVector: SSZ deserialization failed"))
	}
}
```
