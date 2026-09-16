### Title
Unbounded `.expect()`/`copy_from_slice` panics in BEEFY ABI→SCALE conversion reachable from the unprivileged `submit_proof` extrinsic - ([File: evm/rust/src/conversions.rs](evm/rust/src/conversions.rs))

### Summary
`pallet-beefy-consensus-proofs::submit_proof` lets any signed account submit a naive (ECDSA) BEEFY consensus proof, which is ABI-decoded and converted into the SCALE `ConsensusMessage`/`MmrProof` types used by the on-chain verifier via a chain of `From` impls in `evm/rust/src/conversions.rs`. Several of those conversions call `.expect()` on attacker-controlled numeric fields and `copy_from_slice` on an attacker-controlled variable-length `bytes` field, all of which panic on out-of-range or wrong-length input instead of returning an error. This is the same bug class as CVE-2019-18420: untrusted, attacker-shaped input drives an unchecked assertion/format-style operation that traps the host (here, the Substrate runtime) instead of failing gracefully.

### Finding Description
`verify_and_apply` in the beefy-consensus-proofs pallet dispatches on the proof-type byte and, for `PROOF_TYPE_NAIVE`, ABI-decodes the remaining bytes into `ismp_abi::ecdsa_beefy::BeefyConsensusProof`, then converts it with `.into()`: [1](#0-0) 

That `.into()` call resolves to `impl From<BeefyConsensusProof> for ConsensusMessage`, which recurses through `value.relay.into()`: [2](#0-1) 

`impl From<RelayChainProof> for MmrProof` immediately does an unchecked `try_into().expect(...)` on the attacker-supplied `leafIndex`, and maps every submitted `Vote` through `Into::into`: [3](#0-2) 

`impl From<Vote> for SignatureWithAuthorityIndex` copies the attacker-controlled `signature: bytes` field into a fixed `[u8; 65]` array with `copy_from_slice`, which panics whenever the submitted signature length is not exactly 65 bytes, and also `.expect()`s on `authorityIndex`: [4](#0-3) 

The commitment conversion `impl From<Commitment> for SpCommitment` also panics via `.expect("commitment has at least one payload entry")` if the submitted `payload` array is empty, and via two further `.expect()`s on `blockNumber`/`validatorSetId` out-of-range values: [5](#0-4) 

None of these values are validated before the ABI-decode → SCALE conversion boundary: `abi_decode_params` only checks Solidity ABI encoding shape, not domain constraints such as "signature bytes must be 65 long", "payload must be non-empty", or "leafIndex/blockNumber/authorityIndex must fit the narrower Rust integer type". Any signed account can call `submit_proof` (confirmed by the pallet's own simulation test, which submits it as a normal signed extrinsic from a non-privileged keyring account rather than `root`): [6](#0-5) 

This mirrors the pattern the codebase has already fixed elsewhere for the exact same reason — untrusted, attacker-shaped input reaching a `copy_from_slice`/`.expect()`/index panic inside on-chain execution, as documented in the regression tests for `StateMachine::from_str`, `as_utf8_string`, the Pharos SPV `nibble_at_depth`/`ProofTooDeep` guard, and the Ethereum trie `empty_hp_prefix` fix: [7](#0-6) [8](#0-7) 

The BEEFY ABI-decode conversions in `evm/rust/src/conversions.rs` have not received the same treatment.

### Impact Explanation
A runtime panic triggered while executing a signed extrinsic during block execution/`apply_extrinsic` traps the Wasm runtime. Depending on how the transactional context handles the trap, this ranges from failing the whole block's execution (halting block production until the offending transaction is purged, effectively a chain-availability DoS for the parachain and, transitively, every ISMP route whose consensus is anchored to the BEEFY client) to crashing the collator/validator process executing it. Since BEEFY consensus underlies state-machine updates for downstream messaging (mint/burn, intents, bandwidth purchases, general request/response delivery per the CVE-2019-18420 mapping rules), a successful trigger is a "route unable to deliver messages" / protocol-availability event, not merely a resource-exhaustion nuisance.

### Likelihood Explanation
High. `submit_proof` is callable by any signed account with no special permission (confirmed by the pallet's own test harness using a plain keyring account), and only requires crafting an ABI-encoded `BeefyConsensusProof` whose `Vote.signature` is not 65 bytes, whose `Commitment.payload` array is empty, or whose numeric fields (`leafIndex`, `blockNumber`, `validatorSetId`, `authorityIndex`) exceed the target Rust integer width. No cryptographic material or prior state is needed to reach the panic — the invalid shape triggers before any signature/authority verification occurs.

### Recommendation
Replace every `.expect()` and `copy_from_slice` in the `evm/rust/src/conversions.rs` `beefy` module's `From` impls that operate on attacker-controlled ABI-decoded fields with fallible `TryFrom`/`Result`-returning conversions, mirroring the fix pattern already applied to `StateMachine::from_str`, `as_utf8_string`, and the Pharos SPV proof-depth guard: validate `Vote.signature.len() == 65`, `Commitment.payload` non-empty, and that every numeric field fits its target type, propagating a typed error (e.g. `beefy_verifier::error::Error`) up through `verify_and_apply` instead of panicking.

### Proof of Concept
1. Construct an ABI-encoded `ismp_abi::ecdsa_beefy::BeefyConsensusProof` where `relay.signedCommitment.votes[0].signature` is set to a `bytes` value of length ≠ 65 (e.g., empty bytes), leaving other fields well-formed enough to pass ABI decoding.
2. Prepend `PROOF_TYPE_NAIVE` and submit via `BeefyConsensusProofs::submit_proof` as any signed account (as done in the existing malformed-proof test at [9](#0-8) , but with a valid ABI shape and an invalid signature length instead of `AbiDecodeFailed`-triggering junk).
3. Execution reaches `verify_and_apply` → `abi_proof.into()` → `From<BeefyConsensusProof> for ConsensusMessage` → `From<RelayChainProof> for MmrProof` → `From<Vote> for SignatureWithAuthorityIndex`, where `signature.copy_from_slice(&sig_bytes)` panics because `sig_bytes.len() != 65`, aborting the extrinsic's execution with a Wasm trap instead of a `DispatchError`.

### Citations

**File:** modules/pallets/beefy-consensus-proofs/src/lib.rs (L828-838)
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
				_ => Err(Error::<T>::UnknownProofType)?,
			};
```

**File:** evm/rust/src/conversions.rs (L334-351)
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

**File:** parachain/simtests/src/pallet_beefy_consensus_proofs.rs (L360-366)
```rust
	let call = subxt::dynamic::tx(
		"BeefyConsensusProofs",
		"submit_proof",
		vec![Value::from_bytes(&oversized_proof)],
	);
	let result = submit_signed(&client, &rpc_client, call, Keyring::Bob).await;
	assert!(result.is_err(), "oversized submit_proof must be rejected by the BoundedVec decode",);
```

**File:** parachain/simtests/src/pallet_beefy_consensus_proofs.rs (L378-387)
```rust
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

**File:** modules/ismp/core/src/host.rs (L470-474)
```rust
	// A malformed `SUBSTRATE-`/`TNDRMINT-` id whose byte length is not exactly 4
	// must return an error rather than panic. The id is copied into a `[u8; 4]`,
	// and `copy_from_slice` traps on a length mismatch — in the runtime this is a
	// wasm trap reachable from untrusted input (e.g. `BandwidthManager.purchase`),
	// so the length is now checked up-front (matching the `RELAY-` arm).
```

**File:** modules/consensus/pharos/primitives/src/spv.rs (L1023-1029)
```rust
		// Regression: depth beyond the hash length must surface as `None`
		// rather than panicking on an out-of-bounds index. Without this
		// guard an adversarial proof of length >= 66 drives `byte_index`
		// past the end of the 32-byte key hash.
		assert_eq!(nibble_at_depth(&full_hash, 64), None);
		assert_eq!(nibble_at_depth(&full_hash, 65), None);
	}
```
