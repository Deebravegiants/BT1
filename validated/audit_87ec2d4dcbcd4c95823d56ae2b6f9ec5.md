### Title
Reachable assertion / panic (`.expect()` on `try_into()`) when converting attacker-controlled Solidity ABI proof fields into SCALE types during SP1 BEEFY proof submission - ([File: evm/rust/src/conversions.rs])

### Summary
`pallet-beefy-consensus-proofs::submit_proof` lets any signed account submit an SP1 proof whose payload is ABI-decoded from raw, attacker-controlled bytes and then converted into internal SCALE consensus types via `From<crate::sp1_beefy::SP1Beefy::SP1BeefyProof> for Sp1BeefyProof` and its nested conversions in `evm/rust/src/conversions.rs`. Those conversions repeatedly do `some_u256_or_larger_field.try_into().expect("... out of bounds")` before any cryptographic verification happens. Any oversized numeric field (e.g. `blockNumber`, `parentNumber`, `nextAuthoritySet.id/len`, `parachain.index`, `parachain.id`) that doesn't fit the narrower Rust integer causes `.expect()` to panic, which traps the wasm runtime — an on-chain reachable assertion failure directly analogous to CVE-2018-9055 (reachable assertion causing DoS from attacker-controlled decode input).

### Finding Description
The dispatch path is:
1. `pallet_beefy_consensus_proofs::Pallet::submit_proof` (signed, unprivileged) → `do_submit_proof` → for `PROOF_TYPE_SP1`, ABI-decodes the submitted bytes into `ismp_abi::sp1_beefy::SP1Beefy::SP1BeefyProof` [1](#0-0) .
2. `verify_and_apply` (also reachable via the same dispatch, and via the uncle-retry path) repeats the same ABI decode and then converts it with `let scale_proof: beefy_verifier_primitives::Sp1BeefyProof = abi_proof.into();` before any signature/finality check occurs [2](#0-1) .
3. That `Into` implementation is `impl From<crate::sp1_beefy::SP1Beefy::SP1BeefyProof> for Sp1BeefyProof` in `evm/rust/src/conversions.rs`, which unconditionally calls `.try_into().expect(...)` on `commitment.blockNumber`, `commitment.validatorSetId`, and recursively on the MMR leaf and parachain-header fields [3](#0-2) .
4. The nested conversions used by this path (`PartialBeefyMmrLeaf -> MmrLeaf`, `ParachainHeader -> beefy_verifier_primitives::ParachainHeader`) each panic via `.expect("... out of bounds")` on `version`, `parentNumber`, `nextAuthoritySet.id`, `nextAuthoritySet.len`, and `para_id` if the attacker-supplied Solidity numeric field (typically `uint256`/wider) does not fit the target Rust type (`u8`/`u32`) [4](#0-3) .
5. The `From<Parachain> for BvpParachainHeader` conversion used by the NAIVE proof path has the same pattern for `index`/`para_id`/`total_leaves`/MMR-leaf fields [5](#0-4) [6](#0-5) .

None of these numeric fields is range-checked before the `.expect()` — the proof bytes only need to pass the outer `BoundedVec<u8, MaxProofSize>` length bound and the ABI decode shape check (`abi_decode_params`), both of which succeed for arbitrary values within the field width. Because these conversions run inside a pallet extrinsic body (no `catch_unwind` in the wasm runtime), the `.expect()` panic becomes an unrecoverable trap for the whole transaction/block execution rather than a graceful `DispatchError`.

This class of bug (unchecked "reachable assertion"/panic triggered purely by decoding attacker-controlled input) is the exact analog of CVE-2018-9055 in JasPer, where `jpc_firstone` asserted instead of erroring on adversarial input. The codebase's own commit history and inline comments show the team has repeatedly hardened equivalent spots elsewhere (GRANDPA verifier `RelayHeaderNotInUnknownHeaders`, sync-committee multiproof length guard, Pharos `MAX_PROOF_DEPTH`, `StateMachine::from_str` length check, RLP `empty_hp_prefix_returns_error_not_panic`) but the SP1/naive BEEFY ABI→SCALE conversion helpers in `evm/rust/src/conversions.rs` were missed and still use `.expect()` unconditionally.

### Impact Explanation
A successful trigger panics/traps block execution while processing the `submit_proof` extrinsic, before any BEEFY/SP1 cryptographic verification takes place. Depending on how the runtime handles a wasm trap during extrinsic execution, this can abort the whole block's execution (denial of service for the chain / consensus-client update pipeline), which blocks all downstream users (relayers, token bridgers, intent solvers) from advancing BEEFY consensus state and therefore from delivering any cross-chain messages that depend on it. This matches the "route unable to deliver messages" / DoS impact category and is rated medium-severity consistent with the CVE (denial of service, not fund theft).

### Likelihood Explanation
High reachability: `submit_proof` is a plain signed extrinsic open to any account (no fee-based, non-privileged sender), the proof bytes are entirely attacker-supplied, and the ABI decode step (`abi_decode_params`) does not constrain the numeric ranges of `blockNumber`, `parentNumber`, `nextAuthoritySet.id/len`, or `parachain.index/id`. An attacker only needs to craft a syntactically valid ABI-encoded `SP1BeefyProof` (or `BeefyConsensusProof` for the NAIVE path) with one numeric field exceeding the narrower Rust integer width (e.g. a `uint256`/`u64` value that doesn't fit a `u32`) to reach the panic deterministically, with no signature validity or state precondition required beforehand.

### Recommendation
Replace every `.try_into().expect(...)` in `evm/rust/src/conversions.rs` (and any equivalent SCALE↔ABI boundary conversions used from an untrusted-input path) with fallible conversions that surface a typed error, mirroring the pattern already applied in `modules/consensus/grandpa/verifier/src/error.rs` and `modules/consensus/sync-committee/verifier/src/lib.rs`. Concretely:
- Change the `From<...>` impls that are used on the ABI→SCALE decode path to `TryFrom`, returning a dedicated error variant (e.g. `Error::FieldOutOfBounds`) instead of panicking.
- Update `beefy-consensus-proofs::do_submit_proof`/`verify_and_apply` and `ismp-beefy`'s SP1/naive decode call sites to propagate this error as a normal `DispatchResult`/`Err`, so a malformed proof simply fails the extrinsic instead of trapping the runtime.
- Add regression tests analogous to `from_str_rejects_non_four_byte_consensus_ids` and `test_over_deep_proof_rejected` that submit an SP1/naive proof with an out-of-range numeric field and assert a typed error rather than a panic.

### Proof of Concept
1. Construct an ABI-encoded `SP1Beefy::SP1BeefyProof` (or `BeefyConsensusProof` for the NAIVE variant) where `commitment.blockNumber` (or any of `nextAuthoritySet.id`, `nextAuthoritySet.len`, `parachain.index`, `parachain.id`) is set to a value larger than `u32::MAX` (e.g. `2^32`), while keeping the outer ABI shape valid so `abi_decode_params` succeeds.
2. Prefix the bytes with `PROOF_TYPE_SP1` (or `PROOF_TYPE_NAIVE`) and submit via `BeefyConsensusProofs::submit_proof(origin, proof)` from any signed account, within `MaxProofSize`.
3. Execution reaches `verify_and_apply` → `abi_decode_params` succeeds → `Into::<Sp1BeefyProof>::into(abi_proof)` (or `Into::<ConsensusMessage>`) runs `.try_into().expect("... out of bounds")` on the oversized field and panics, before any BEEFY/SP1 signature check is performed [3](#0-2) .

### Citations

**File:** modules/pallets/beefy-consensus-proofs/src/lib.rs (L468-482)
```rust
			let account = match proof_type {
				types::PROOF_TYPE_SP1 => {
					let p =
						<ismp_abi::sp1_beefy::SP1Beefy::SP1BeefyProof as SolType>::abi_decode_params(
							&proof[1..],
						)
						.map_err(|_| Error::<T>::AbiDecodeFailed)?;
					let nonce = H256(p.nonce.0);
					// `T::AccountId` is `AccountId32` in hyperbridge runtimes, which SCALE-encodes
					// to its 32 raw bytes; compare those against the committed nonce.
					if submitter.encode().as_slice() != nonce.as_bytes() {
						Err(Error::<T>::UnauthorizedProof)?
					}
					Some(nonce)
				},
```

**File:** modules/pallets/beefy-consensus-proofs/src/lib.rs (L818-827)
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
```

**File:** evm/rust/src/conversions.rs (L249-285)
```rust
	impl From<PartialBeefyMmrLeaf> for sp_consensus_beefy::mmr::MmrLeaf<u32, H256, H256, H256> {
		fn from(value: PartialBeefyMmrLeaf) -> Self {
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

	impl From<ParachainHeader> for beefy_verifier_primitives::ParachainHeader {
		fn from(value: ParachainHeader) -> Self {
			beefy_verifier_primitives::ParachainHeader {
				header: value.header.to_vec(),
				para_id: value.id.try_into().expect("para id out of bounds"),
				// SP1 proves inclusion directly so any value here is fine.
				index: 0,
			}
		}
	}
```

**File:** evm/rust/src/conversions.rs (L287-333)
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

**File:** evm/rust/src/conversions.rs (L397-416)
```rust
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
