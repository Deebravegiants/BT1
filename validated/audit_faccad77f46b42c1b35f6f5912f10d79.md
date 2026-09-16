## Analysis

The DeGate report describes a class of bug where **untrusted proof/witness data fed into a circuit/verifier is deserialized with unchecked assumptions**, causing an assertion/panic instead of a typed rejection — crashing the process that validates the data. Searching this codebase confirms that this exact bug class was previously widespread and has been extensively (and deliberately) hardened almost everywhere: `modules/consensus/beefy/verifier/src/lib.rs` (empty `leaf_indices` index panic), `modules/consensus/sync-committee/verifier/src/lib.rs` (`calculate_multi_merkle_root` panic on short multi-proof), `modules/consensus/pharos/primitives/src/spv.rs` (`nibble_at_depth` OOB panic, oversized proof panic), `modules/trees/ethereum/src/tests.rs` (`RlpNodeCodec` empty HP-prefix panic), `modules/ismp/core/src/host.rs` (`StateMachine::from_str` `copy_from_slice` length-mismatch panic), `modules/utils/serde/src/lib.rs` (`as_utf8_string` length-mismatch panic — explicitly noted to have crashed a production node's RPC worker), and `modules/consensus/grandpa/verifier/src/lib.rs` (`.expect()` on ancestry header lookup). Every one of these carries an explicit regression comment describing the prior crash and the fix (typed `Err`/`Option` instead of panic).

However, one location containing the same pattern remains unguarded: [1](#0-0) . This module defines a chain of `From` impls (not `TryFrom`) that convert Solidity-ABI-decoded BEEFY/SP1 consensus proof structs (`Parachain`, `ParachainProof`, `BeefyMmrLeaf`, `Commitment`, `Vote`, `RelayChainProof`, `SP1BeefyProof`, `IntermediateState` — all fields originating from a relayed/submitted consensus proof) into the internal `beefy_verifier_primitives` types consumed by consensus verification. Each conversion narrows a wider Solidity integer (`uint256`/`uint64`) into a narrower Rust integer (`u32`/`u64`/`u8`) using `.try_into().expect("... out of bounds")`: [2](#0-1) [3](#0-2) [4](#0-3) [5](#0-4) [6](#0-5) [7](#0-6) [8](#0-7) 

This is used by BEEFY/SP1 consensus-proof handling code (referenced by `tesseract/consensus/beefy/zk/src/lib.rs` and `modules/consensus/beefy/verifier/src/sp1.rs`), which is on the list of explicitly in-scope reachable paths ("consensus verification (BEEFY, SP1, ...)"). Because these are `From` (infallible-by-signature) rather than `TryFrom` conversions, any caller invoking `.into()` on relayer-supplied proof data has no way to catch an out-of-range field and must let the panic propagate — the same structural mistake the rest of the codebase has been systematically eliminating (compare to the fixed `StateMachine::from_str` / `as_utf8_string` cases, which were fixed specifically because they ran on "untrusted input" and could "abort the process").

**Caveat / uncertainty:** I was not able to fully trace, within the remaining tool budget, the exact call site that feeds attacker/relayer-controlled bytes into these `From` impls at runtime (i.e., confirm whether it executes inside the SP1 zkVM guest circuit invoked per-proof-submission, or only in prover/relayer-side tooling that assembles witnesses from already-trusted RPC data). If it is exclusively invoked in prover-only/tesseract-daemon tooling operating on data the tesseract process itself fetches (not attacker-supplied), this would fall under the excluded "prover-only"/"tesseract-daemon" categories and would not qualify. Confirming the exact reachability requires reading `tesseract/consensus/beefy/zk/src/lib.rs` and `modules/consensus/beefy/verifier/src/sp1.rs` in full, which I could not do in the remaining iterations.

### Title
Unchecked integer-width `From` conversions on relayed BEEFY/SP1 proof fields can panic the consensus verifier - ([File: evm/rust/src/conversions.rs])

### Summary
`evm/rust/src/conversions.rs` converts Solidity-ABI BEEFY/SP1 consensus-proof structures (whose numeric fields are `uint256`/`uint64` and therefore attacker-choosable up to those widths) into narrower internal Rust types via `.try_into().expect("... out of bounds")` inside plain `From` impls. A relayer/prover submitting a proof with any oversized field (parachain index, para id, MMR leaf version/parent number, authority-set id/len, commitment block number/validator-set id, authority index, MMR leaf index, state-machine id/height, timestamp) causes an unrecoverable panic rather than a typed rejection, mirroring the DeGate `bigint` assertion-failure crash pattern.

### Finding Description
Every one of these conversions (lines 291-292, 309-326, 340-352, 363, 370-371, 400-409, 423-430 in `evm/rust/src/conversions.rs`) is implemented as `impl From<X> for Y` with `.expect(...)` on a `try_into()`, meaning the conversion is advertised as infallible to the type system even though it can fail on attacker-controlled input. This is the exact class of bug the rest of the codebase has been hardened against — see the analogous, already-fixed panics in `modules/consensus/beefy/verifier/src/lib.rs` (empty `leaf_indices`), `modules/consensus/sync-committee/verifier/src/lib.rs` (short `multi_proof`), `modules/consensus/pharos/primitives/src/spv.rs` (`nibble_at_depth` OOB), and `modules/ismp/core/src/host.rs` / `modules/utils/serde/src/lib.rs` (fixed-length copy panics on untrusted RPC/consensus-id input, one of which is documented as having crashed a production node).

### Impact Explanation
If reachable from relayer-supplied BEEFY/SP1 proof data, an adversary can craft a proof with an oversized numeric field to deterministically panic the process performing this conversion, denying consensus-update processing (a route unable to deliver messages / degraded validator availability) — the same operational impact class as the DeGate finding (repeated crashes degrading validator performance/availability).

### Likelihood Explanation
Medium-High if the conversions execute on a path that ingests untrusted relayer-provided proof bytes per submission; Low/Not-applicable if strictly confined to trusted prover-side tooling constructing witnesses from already-validated RPC data. This distinction could not be conclusively resolved with the remaining investigation budget.

### Recommendation
Replace these `From` impls with `TryFrom` returning a typed error for any out-of-range field, matching the pattern already applied throughout the rest of the codebase (e.g., the `StateMachine::from_str` and `as_utf8_string` fixes), and ensure all callers on the relayed-proof path propagate the error instead of unwrapping/panicking. Add regression tests analogous to the existing `from_str_rejects_non_four_byte_consensus_ids` / `as_utf8_string_rejects_non_four_byte_input` tests, but for out-of-range numeric fields in BEEFY/SP1 proof conversions.

### Proof of Concept
Construct a `BeefyConsensusProof`/`Commitment`/`SP1BeefyProof` Solidity struct with any field exceeding the target Rust integer's range (e.g., `blockNumber > u32::MAX`, `nextAuthoritySet.id > u32::MAX`, `leafIndex > u64::MAX` is impossible but any `uint256`-to-`u32`/`u64` field can be set beyond range) and submit/feed it through whichever caller invokes `.into()` on these types; the process panics at the `.expect(...)` call instead of returning a verification error.

### Citations

**File:** evm/rust/src/conversions.rs (L287-416)
```rust
	impl From<Parachain> for BvpParachainHeader {
		fn from(value: Parachain) -> Self {
			BvpParachainHeader {
				header: value.header.to_vec(),
				index: value.index.try_into().expect("parachain leaf index out of bounds"),
				para_id: value.id.try_into().expect("para id out of bounds"),
			}
		}
	}

	impl From<ParachainProof> for BvpParachainProof {
		fn from(value: ParachainProof) -> Self {
			BvpParachainProof {
				parachains: value.parachains.into_iter().map(Into::into).collect(),
				proof: value.proof.into_iter().map(|h| h.0).collect(),
				total_leaves: value.leafCount.try_into().expect("leaf count out of bounds"),
			}
		}
	}

	impl From<BeefyMmrLeaf> for SpMmrLeaf {
		fn from(value: BeefyMmrLeaf) -> Self {
			let version: u8 = value.version.try_into().expect("mmr leaf version out of bounds");
			sp_consensus_beefy::mmr::MmrLeaf {
				version: MmrLeafVersion::new(version >> 5, version & 0b11111),
				parent_number_and_hash: (
					value.parentNumber.try_into().expect("parent number out of bounds"),
					H256(value.parentHash.0),
				),
				beefy_next_authority_set: BeefyNextAuthoritySet {
					id: value
						.nextAuthoritySet
						.id
						.try_into()
						.expect("next authority set id out of bounds"),
					len: value
						.nextAuthoritySet
						.len
						.try_into()
						.expect("next authority set len out of bounds"),
					keyset_commitment: H256(value.nextAuthoritySet.root.0),
				},
				leaf_extra: H256(value.extra.0),
			}
		}
	}

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

	impl From<BeefyConsensusProof> for ConsensusMessage {
		fn from(value: BeefyConsensusProof) -> Self {
			ConsensusMessage { mmr: value.relay.into(), parachain: value.parachain.into() }
		}
	}

	impl From<crate::sp1_beefy::SP1Beefy::SP1BeefyProof> for Sp1BeefyProof {
		fn from(value: crate::sp1_beefy::SP1Beefy::SP1BeefyProof) -> Self {
			Sp1BeefyProof {
				block_number: value
					.commitment
					.blockNumber
					.try_into()
					.expect("block number out of bounds"),
				validator_set_id: value
					.commitment
					.validatorSetId
					.try_into()
					.expect("validator set id out of bounds"),
				mmr_leaf: value.mmrLeaf.into(),
				headers: value.headers.into_iter().map(Into::into).collect(),
				proof: value.proof.to_vec(),
				nonce: H256(value.nonce.0),
			}
		}
	}
```

**File:** evm/rust/src/conversions.rs (L423-430)
```rust
				state_machine_id: value
					.stateMachineId
					.try_into()
					.expect("state machine id out of bounds"),
				height: value.height.try_into().expect("state machine height out of bounds"),
			},
			commitment: local::StateCommitment {
				timestamp: value.commitment.timestamp.try_into().expect("timestamp out of bounds"),
```
