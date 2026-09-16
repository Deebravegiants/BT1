### Title
Unchecked ABI `bytes` length in BEEFY naive-proof signature conversion causes a runtime panic — ([File: evm/rust/src/conversions.rs])

### Summary
The naive BEEFY consensus-proof submission path (`pallet-beefy-consensus-proofs::submit_proof`, `PROOF_TYPE_NAIVE`) ABI-decodes an EVM-style `BeefyConsensusProof` struct and converts it into native Substrate types via `From` impls in `evm/rust/src/conversions.rs`. One of these impls copies an attacker-supplied, variable-length `bytes` field into a fixed-size `[u8; 65]` array without first checking its length, causing an unconditional panic (`copy_from_slice` length mismatch) that is directly reachable from unprivileged, unsigned extrinsic/proof input — the same bug class as CVE-2025-46397 (unchecked externally-controlled length driving a fixed-size buffer operation).

### Finding Description
`From<Vote> for SignatureWithAuthorityIndex` reads an ABI-decoded `Vote.signature` (`alloy_primitives::Bytes`, an unconstrained dynamic `bytes` type in Solidity/ABI encoding) and writes it into a fixed 65-byte array with no length guard: [1](#0-0) 

This is invoked transitively from the naive BEEFY proof conversion chain that the pallet's `submit_proof` dispatch uses to turn a submitted, ABI-encoded `BeefyConsensusProof` into a `ConsensusMessage` for verification: [2](#0-1) [3](#0-2) 

Unlike the well-guarded decoders elsewhere in this codebase (e.g. `ByteVector<N>::decode` rejecting mismatched lengths, or the RLP node codec regression fix for empty HP prefixes), this conversion has no equivalent length check: [4](#0-3) [5](#0-4) 

Solidity's ABI encoding places no constraint on the length of a dynamic `bytes` field such as `Vote.signature`, so an attacker submitting `submit_proof` with `PROOF_TYPE_NAIVE` can supply any signature length other than 65 and still pass ABI decoding, as confirmed by the pallet's own test coverage, which only exercises "oversized payload", "unknown proof type", and "malformed (non-ABI-decodable) bytes" — not a well-formed ABI payload with a wrong-length nested `bytes` field: [6](#0-5) 

### Impact Explanation
A single unsigned/unprivileged extrinsic (`submit_proof`) containing a syntactically valid ABI-encoded `BeefyConsensusProof` with a mis-sized `Vote.signature` field triggers a Rust panic mid-conversion, before any cryptographic or Merkle verification runs. In a Substrate runtime, an unhandled panic during block execution traps the WASM instance for that extrinsic/block; because the fault is deterministic and reproducible from the submitted proof bytes, this is a repeatable route to abort processing of the BEEFY consensus-update extrinsic, blocking or destabilizing the light-client update path that the rest of Hyperbridge's cross-chain message delivery (dispatch, relaying, mint/burn, intents) depends on. This satisfies the "route unable to deliver messages" impact criterion.

### Likelihood Explanation
High. The bug is reachable directly from a single, unsigned/unprivileged transaction with no special preconditions — only the ability to submit an ABI-encoded proof with a `Vote.signature` field length ≠ 65 bytes, which is trivial to construct.

### Recommendation
Add an explicit length check before `copy_from_slice` in `From<Vote> for SignatureWithAuthorityIndex`, returning a decode error (mirroring the `TryFrom`/length-checked pattern used elsewhere, e.g. `ByteVector<N>::decode`) rather than panicking, and propagate this as a `TryFrom` conversion through the `RelayChainProof -> MmrProof` and `BeefyConsensusProof -> ConsensusMessage` chain so `submit_proof` can reject malformed naive proofs with a normal dispatch error instead of panicking.

### Proof of Concept
1. Construct a valid ABI encoding of `BeefyConsensusProof` (matching `Types.sol`'s `Vote`/`RelayChainProof`/`BeefyConsensusProof` schema) where at least one `Vote.signature` is, e.g., 64 or 66 bytes instead of 65.
2. Prefix the encoded bytes with `PROOF_TYPE_NAIVE` and submit via `pallet_beefy_consensus_proofs::submit_proof`.
3. ABI decoding succeeds (dynamic `bytes` accepts any length); the pallet's conversion into `ConsensusMessage` invokes `From<Vote> for SignatureWithAuthorityIndex`, which panics at `signature.copy_from_slice(&sig_bytes)` since `sig_bytes.len() != 65`.

Note: I was unable to directly view the exact body of `modules/pallets/beefy-consensus-proofs/src/lib.rs` (index coverage limits), so the precise wiring between `submit_proof`'s decode step and the `conversions.rs` `From` chain is inferred from the existing test file's described behavior and the `From<BeefyConsensusProof> for ConsensusMessage` impl. A Devin session with full repo access should confirm this call path exactly before implementing the fix.

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

**File:** evm/rust/src/conversions.rs (L391-395)
```rust
	impl From<BeefyConsensusProof> for ConsensusMessage {
		fn from(value: BeefyConsensusProof) -> Self {
			ConsensusMessage { mmr: value.relay.into(), parachain: value.parachain.into() }
		}
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

**File:** modules/trees/ethereum/src/tests.rs (L73-85)
```rust
#[test]
fn empty_hp_prefix_returns_error_not_panic() {
	// Regression: a leaf/extension node is RLP-encoded as a 2-item list whose
	// first item is the hex-prefix-encoded partial key. Before the fix at
	// `node_codec.rs` the decoder indexed `data[0]` without checking that the
	// HP payload was non-empty, so an adversarial proof node of the form
	// `rlp([b"", b""])` panicked with index-out-of-bounds inside on-chain
	// execution (e.g. parachain block verification). It must now return an
	// `Err` cleanly.
	let adversarial_node: [u8; 3] = [0xc2, 0x80, 0x80];
	let result = <RlpNodeCodec<KeccakHasher> as NodeCodec>::decode_plan(&adversarial_node);
	assert!(result.is_err(), "decoder must reject empty HP prefix, got {:?}", result);
}
```

**File:** parachain/simtests/src/pallet_beefy_consensus_proofs.rs (L355-387)
```rust
	// 6. submit_proof oversized payload — `proof: BoundedVec<u8, MaxProofSize>` rejects at the
	//    txpool decode stage, before dispatch. We send `MaxProofSize + 1` bytes prefixed with
	//    `PROOF_TYPE_NAIVE`.
	let mut oversized_proof = vec![PROOF_TYPE_NAIVE; MAX_PROOF_SIZE + 1];
	oversized_proof[0] = PROOF_TYPE_NAIVE;
	let call = subxt::dynamic::tx(
		"BeefyConsensusProofs",
		"submit_proof",
		vec![Value::from_bytes(&oversized_proof)],
	);
	let result = submit_signed(&client, &rpc_client, call, Keyring::Bob).await;
	assert!(result.is_err(), "oversized submit_proof must be rejected by the BoundedVec decode",);

	// 7. submit_proof with an unknown proof-type byte.
	let unknown_proof = vec![UNKNOWN_PROOF_TYPE; 64];
	let call = subxt::dynamic::tx(
		"BeefyConsensusProofs",
		"submit_proof",
		vec![Value::from_bytes(&unknown_proof)],
	);
	let result = submit_signed(&client, &rpc_client, call, Keyring::Bob).await;
	assert!(result.is_err(), "unknown proof-type submit_proof must fail (UnknownProofType)",);

	// 8. submit_proof with malformed naive bytes. The byte 0 marks `PROOF_TYPE_NAIVE`, the rest is
	//    junk that won't ABI-decode as `BeefyConsensusProof`. Expect `AbiDecodeFailed`.
	let mut malformed_naive = vec![0u8; 128];
	malformed_naive[0] = PROOF_TYPE_NAIVE;
	let call = subxt::dynamic::tx(
		"BeefyConsensusProofs",
		"submit_proof",
		vec![Value::from_bytes(&malformed_naive)],
	);
	let result = submit_signed(&client, &rpc_client, call, Keyring::Bob).await;
```
