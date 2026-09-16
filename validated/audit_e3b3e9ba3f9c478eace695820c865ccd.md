### Title
Unbounded-length BEEFY vote signature causes a `copy_from_slice` panic that halts block execution - ([File: evm/rust/src/conversions.rs])

### Summary
`From<Vote> for SignatureWithAuthorityIndex` in [1](#0-0)  copies an attacker-supplied, variable-length ABI `bytes` field (`Vote.signature`) into a fixed-size `[u8; 65]` buffer with `copy_from_slice`, which panics whenever the input is not exactly 65 bytes. This is functionally the same bug class as CVE-2016-6830 (fixed-size buffer fed with unchecked, attacker-controlled variable-length data): instead of a native buffer overrun, Rust's bounds-checked `copy_from_slice` converts the same root cause into a hard panic, but that panic executes inside the chain's state-transition function.

### Finding Description
`pallet-beefy-consensus-proofs::submit_proof` (any signed, otherwise-unprivileged account, per [2](#0-1) ) accepts a raw `proof: &[u8]`. For `PROOF_TYPE_NAIVE`, `verify_and_apply` ABI-decodes it as `ismp_abi::ecdsa_beefy::BeefyConsensusProof` and converts it with `.into()` into the SCALE `ConsensusMessage` **before any cryptographic BEEFY/authority check runs**: [3](#0-2) 

That conversion chain descends `BeefyConsensusProof → RelayChainProof → MmrProof`, mapping every vote in `signedCommitment.votes` through `From<Vote> for SignatureWithAuthorityIndex`: [1](#0-0) 

`Vote.signature` is a dynamic Solidity `bytes` (there is no native 65-byte fixed type for an ECDSA signature), so its length is entirely attacker-controlled at the ABI-decode stage — `SolValue::abi_decode` places no constraint on `bytes` length. If the caller supplies any length other than 65, `signature.copy_from_slice(&sig_bytes)` panics with a length-mismatch, aborting execution inside the pallet's dispatchable/`validate_unsigned`-adjacent decode path.

This is the exact class of bug the project has already found and fixed elsewhere in the same codebase — copying untrusted, variable-length input into a fixed-size buffer without a length check first:
- [4](#0-3)  (previously crashed the node's RPC worker on untrusted `consensus_state_id`).
- [5](#0-4)  (guarded against an attacker-controlled `multi_proof` panicking the unsigned consensus-update path).
- [6](#0-5)  (regression test for a panic on adversarial trie-proof nodes).

The `Vote → SignatureWithAuthorityIndex` conversion in `evm/rust/src/conversions.rs` has not received the same guard.

### Impact Explanation
A single malicious `submit_proof` extrinsic with a malformed `Vote.signature` length panics inside the runtime while processing a consensus message. Because this happens deterministically for every collator/validator that re-executes the same extrinsic (block authoring and block import both call the identical `verify_and_apply` → conversion path), the panic is not a local/node-specific DoS but a state-transition-function crash: it can prevent the offending block from being produced/imported consistently across the network, halting BEEFY consensus-client updates and, by extension, all cross-chain message relaying that depends on that consensus client being advanced. This matches the "route unable to deliver messages" / unsound consensus-processing criteria — it is not a mere resource-exhaustion or network-level DoS, since the trigger is a single, deterministically-reproducible malformed vote in an unprivileged extrinsic body.

### Likelihood Explanation
High. `submit_proof` is reachable by any account holding minimal fee balance; no special permission is required (`ensure_signed`, not an admin/root origin). Constructing a `BeefyConsensusProof` with an off-length `Vote.signature` requires no cryptographic material — the panic fires during ABI-to-SCALE conversion, before the signature is checked for validity, so the caller does not even need a valid BEEFY signature to trigger it.

### Recommendation
Replace the panicking `copy_from_slice` in `From<Vote> for SignatureWithAuthorityIndex` (evm/rust/src/conversions.rs) with a fallible `TryFrom` that validates `value.signature.len() == 65` and returns a decode/verification error (mirroring the fixes already applied in `modules/utils/serde/src/lib.rs` and `modules/consensus/sync-committee/verifier/src/lib.rs`), and propagate that error through `verify_and_apply` as `Error::<T>::AbiDecodeFailed` instead of allowing the underlying `expect`/panic to reach the dispatchable. Audit all other `From<...>` impls in `evm/rust/src/conversions.rs` that call `copy_from_slice` or `try_into().expect(...)` on ABI-decoded dynamic-length fields for the same pattern.

### Proof of Concept
1. Craft a `BeefyConsensusProof` (or the underlying `RelayChainProof.signedCommitment.votes` array) where one `Vote.signature` is, e.g., 64 or 66 bytes instead of 65.
2. ABI-encode it and prefix with `PROOF_TYPE_NAIVE`, as done by `submit_proof`'s callers (see the fixture-building pattern in [7](#0-6) ).
3. Submit it as a signed extrinsic to `BeefyConsensusProofs::submit_proof` from any funded account.
4. `verify_and_apply` → `abi_proof.into()` reaches `From<Vote> for SignatureWithAuthorityIndex`, and `signature.copy_from_slice(&sig_bytes)` panics because `sig_bytes.len() != 65`, aborting execution rather than returning `Error::<T>::AbiDecodeFailed`.

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

**File:** parachain/simtests/src/pallet_beefy_consensus_proofs.rs (L387-404)
```rust
	let result = submit_signed(&client, &rpc_client, call, Keyring::Bob).await;
	assert!(result.is_err(), "malformed naive proof must fail (AbiDecodeFailed)",);

	// 9. submit_proof rejects an unsigned origin. We try to author the same call as an unsigned
	//    extrinsic and expect the txpool / runtime to refuse it (the pallet only accepts
	//    `ensure_signed`).
	let call = subxt::dynamic::tx(
		"BeefyConsensusProofs",
		"submit_proof",
		vec![Value::from_bytes(&malformed_naive)],
	);
	let unsigned_result = client.tx().create_unsigned(&call)?.submit_and_watch().await;
	let Err(subxt::Error::Rpc(RpcError::ClientError(_))) = unsigned_result else {
		panic!("unsigned submit_proof should have been rejected, got {unsigned_result:?}");
	};

	Ok(())
}
```

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

**File:** modules/utils/serde/src/lib.rs (L529-532)
```rust
	// `as_utf8_string` deserializes into a fixed `[u8; 4]`. It used to `copy_from_slice`
	// straight from the input, which panics on any length mismatch — and it runs on
	// untrusted RPC input (`consensus_state_id`), so the panic aborted the node's `rpc`
	// worker thread and took the process down. Wrong lengths must be serde errors.
```

**File:** modules/consensus/sync-committee/verifier/src/lib.rs (L184-192)
```rust
	// `calculate_multi_merkle_root` panics on a short `multi_proof` because its final
	// `objects.get(&GeneralizedIndex(1)).unwrap()` cannot reconstruct the root. Reject
	// proofs whose helper-node count does not match what the algorithm requires so an
	// attacker-controlled `multi_proof` cannot panic the runtime via the public unsigned
	// consensus update path.
	if execution_payload.multi_proof.len() != get_helper_indices(&execution_payload_indices).len()
	{
		Err(Error::InvalidMerkleBranch("Execution payload multiproof length".into()))?;
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
