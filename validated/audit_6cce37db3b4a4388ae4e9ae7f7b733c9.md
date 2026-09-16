### Title
Unbounded `.expect()` on attacker-controlled ABI-decoded U256 fields in BEEFY/SP1 proof conversion panics the runtime before cryptographic verification (Client/Node DoS) - ([File: evm/rust/src/conversions.rs])

### Summary
The `do_submit_proof` extrinsic on `pallet-beefy-consensus-proofs` accepts a raw `proof: Vec<u8>` from any signed account and, for `PROOF_TYPE_SP1`, ABI-decodes it into `ismp_abi::sp1_beefy::SP1Beefy::SP1BeefyProof` and immediately converts it to the internal SCALE type via `.into()`. That conversion chain (`Sp1BeefyProof::from`, `Commitment::from`, `PartialBeefyMmrLeaf::from`, `Vote::from`, etc.) uses `U256/u128::try_into().expect("... out of bounds")` on fields taken directly from the untrusted ABI payload — `blockNumber`, `validatorSetId`, MMR leaf `version`, `parentNumber`, `nextAuthoritySet.id`/`len`, `authorityIndex`, `leafIndex` — before any cryptographic (SP1/BEEFY signature) verification occurs.

### Finding Description
`do_submit_proof` in `modules/pallets/beefy-consensus-proofs/src/lib.rs:448-516` does: [1](#0-0) 
which decodes attacker-supplied bytes with `SP1Beefy::SP1BeefyProof::abi_decode_params` and only checks the nonce — no cryptographic proof check yet.

`verify_and_apply` (called right after) re-decodes and performs the same lossy conversion before dispatching to the actual verifier: [2](#0-1) 

The `.into()` used in both places resolves to: [3](#0-2) 
which itself calls `Commitment::into()` and `BeefyMmrLeaf::into()`, both riddled with `.expect("... out of bounds")` on values taken straight from attacker-controlled `uint256`/`uint64` ABI fields: [4](#0-3) [5](#0-4) [6](#0-5) 

Any submitter can set, e.g., `commitment.blockNumber` or `commitment.validatorSetId` (Solidity `uint256`) to a value that doesn't fit in `u64`/`u32`. `try_into()` fails and `.expect(...)` panics — this happens purely from ABI decoding, before the SP1 zk-proof or BEEFY signature is checked, so the attacker needs no valid cryptographic proof at all, only correctly-shaped ABI bytes with an oversized numeric field.

This is the same bug class as the FreeRDP CVE: a missing bounds check in an untrusted-input decode/normalize path that is guarded only by a reachable `assert`/`expect`→panic instead of a typed error, causing the node to abort mid-execution.

### Impact Explanation
A panic during on-chain extrinsic execution inside the runtime is not a safely-recoverable `Result::Err`; depending on how the executor handles unwinding, this either aborts block execution for that node/validator or is treated as an execution fault, which can knock a collator/validator out of consensus for that block — a Denial of Service against message/consensus delivery for the whole route that depends on the BEEFY consensus client. This satisfies the "route unable to deliver messages" bar: since `IsmpCallFilter` (see `parachain/runtimes/nexus/src/lib.rs`) forces BEEFY updates through `beefy-consensus-proofs::submit_proof` rather than raw `handle_unsigned`, this pallet's dispatch is the sole path for advancing the BEEFY light client that gates all Polkadot/Nexus message delivery.

### Likelihood Explanation
High feasibility: the call is a normal signed extrinsic (`do_submit_proof`), requires no relayer privilege, no valid SP1/BEEFY proof, and no economic stake beyond a single transaction fee. The attacker only needs to craft ABI-encoded bytes with `PROOF_TYPE_SP1` and an out-of-range `uint256` in one of several fields (`blockNumber`, `validatorSetId`, MMR leaf `version`/`parentNumber`, authority-set `id`/`len`, vote `authorityIndex`, MMR `leafIndex`).

### Recommendation
Replace every `.try_into().expect("... out of bounds")` in the ABI→SCALE conversion path (`evm/rust/src/conversions.rs`, especially the `Commitment`, `BeefyMmrLeaf`/`PartialBeefyMmrLeaf`, `Vote`, `ParachainHeader`, `Parachain`, `ParachainProof`, and `RelayChainProof` `From` impls) with fallible `TryFrom` returning a typed error (e.g. `AbiDecodeFailed`/`ValueOutOfBounds`) that `do_submit_proof`/`verify_and_apply` can propagate as a normal `DispatchResult` error instead of panicking. This mirrors the fix pattern already applied elsewhere in this codebase (e.g. the GRANDPA `RelayHeaderNotInUnknownHeaders`, BEEFY `InvalidMmrProof` empty-`leaf_indices` guard, and sync-committee multi-proof length guard).

### Proof of Concept
1. Construct `ismp_abi::sp1_beefy::SP1Beefy::SP1BeefyProof` with a valid shape but set `commitment.blockNumber` (or `validatorSetId`) to `U256::MAX` (or any value `> u64::MAX`).
2. ABI-encode it, prefix with `types::PROOF_TYPE_SP1` byte, and submit via `beefy_consensus_proofs::submit_proof(origin, proof)` from any funded account.
3. `do_submit_proof` decodes the nonce successfully (independent field), passes the nonce check trivially by using the submitter's own account bytes as `nonce`, then calls `Self::verify_and_apply(&proof)`.
4. Inside `verify_and_apply`, `abi_proof.into()` invokes `Sp1BeefyProof::from`, which calls `value.commitment.blockNumber.try_into().expect("block number out of bounds")` — this panics before any SP1/BEEFY cryptographic check runs, aborting execution of the extrinsic/block.

Note: I could not directly confirm from the index whether the runtime/executor treats this panic as a full node crash versus a caught unrecoverable-error state (this depends on Substrate/FRAME panic-handling configuration not fully visible in the indexed files), so the exact blast radius (full node crash vs. block-production halt for that collator) should be validated in a live/test environment before treating severity as High rather than Medium.

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

**File:** evm/rust/src/conversions.rs (L249-273)
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
```

**File:** evm/rust/src/conversions.rs (L334-353)
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
