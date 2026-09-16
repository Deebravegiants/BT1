### Title
Unchecked numeric-overflow panic in SP1 BEEFY proof conversion, before any cryptographic verification - ([File: evm/rust/src/conversions.rs])

### Summary
The SP1 BEEFY consensus-proof ingestion path decodes an ABI-encoded, attacker-supplied proof and immediately converts several `uint256` fields into narrower Rust integer types (`u32`) using `.try_into().expect(...)`. This conversion happens **before** any BEEFY authority-set check, MMR verification, or SP1 zero-knowledge proof verification takes place. A relayer can submit a proof whose `blockNumber` or `validatorSetId` fields exceed `u32::MAX`, causing an unrecoverable Rust panic during proof processing — the same bug class as CVE-2024-0841 (an unchecked failure reachable from untrusted input before validation, causing a crash), except here the crash surface is the on-chain consensus-update path rather than a kernel filesystem call.

### Finding Description
`modules/pallets/beefy-consensus-proofs/src/lib.rs::verify_and_apply` handles both SP1 and naive BEEFY proof types submitted by relayers: [1](#0-0) 

For `PROOF_TYPE_SP1`, the raw calldata is ABI-decoded into `ismp_abi::sp1_beefy::SP1Beefy::SP1BeefyProof` and immediately converted with `.into()` into the internal `Sp1BeefyProof` type — this conversion runs before `handlers::handle_incoming_message` (and thus before any consensus-client cryptographic verification) is invoked.

The `From` implementation performing that conversion is: [2](#0-1) 

and the nested MMR-leaf conversion it calls into does the same pattern: [3](#0-2) 

Both use `try_into().expect("... out of bounds")` on fields (`blockNumber`, `validatorSetId`, `parentNumber`, authority-set `id`/`len`) that are fully attacker-controlled `uint256` ABI values with no prior bounds check. Supplying a value greater than `u32::MAX` (or `u8::MAX` for the leaf `version` field) makes `try_into()` return `Err`, and `.expect(...)` panics immediately — well before the SP1 ZK proof or BEEFY signatures are checked.

This is the exact bug class the codebase has already proactively hardened against elsewhere: comments in `modules/consensus/beefy/verifier/src/lib.rs:229-236` and `modules/consensus/sync-committee/verifier/src/lib.rs:184-192` explicitly describe fixing prior unchecked-index/`.unwrap()` panics reachable from unsigned/relayer-submitted proof data. The `.expect()` calls in `evm/rust/src/conversions.rs` were apparently missed in that hardening pass and remain in the same class of "unvalidated, attacker-reachable data reaching an infallible-looking conversion that can abort."

### Impact Explanation
A panic triggered inside pallet/runtime code executed as part of extrinsic dispatch is a denial-of-service condition for the consensus-update path: it can abort the executing transaction/block context, and depending on how the panic unwinds relative to Substrate's `panic_handler`/`AssertUnwindSafe` boundaries in the runtime, it can be far more severe than a reverted transaction — potentially destabilizing block execution for the BEEFY consensus-update extrinsic across the network, since every collator/validator executing the same malicious proof hits the same unchecked `.expect()`. This blocks Hyperbridge's ability to advance BEEFY consensus state (a "route unable to deliver messages" condition), which the task's Validate criteria explicitly accepts as impact.

### Likelihood Explanation
`verify_and_apply` is on the relayer-facing path for submitting BEEFY/SP1 consensus proofs — the same permissionless proof-submission mechanism used to advance the trusted consensus state that every downstream Hyperbridge message relies on. Constructing an ABI-encoded `SP1BeefyProof` tuple with an oversized `blockNumber`/`validatorSetId`/`parentNumber` field requires no signature forgery, no valid ZK proof, and no privileged role — only the ability to submit the extrinsic, which is the same capability any ordinary relayer already has.

### Recommendation
Replace every `try_into().expect(...)` in `evm/rust/src/conversions.rs` (lines 251, 255, 263, 268, 280, 403-409, and the analogous ones in the ecdsa/naive `From<SpCommitment>` paths) with fallible conversions that propagate a typed decode error (e.g. `Error::AbiDecodeFailed` / a new `ProofFieldOutOfBounds` variant) up through `verify_and_apply`, mirroring the pattern already used for `Error::AbiDecodeFailed` on `abi_decode_params` failures. No consensus-proof field should ever reach an `.expect()`/`.unwrap()` before the proof has been cryptographically verified.

### Proof of Concept
1. Craft an SP1 proof submission using the `PROOF_TYPE_SP1` wire format expected by `verify_and_apply`.
2. ABI-encode the `SP1Beefy::SP1BeefyProof` tuple with `commitment.blockNumber` (or `validatorSetId`) set to a `uint256` value greater than `u32::MAX` (e.g. `2^32`). Leave the SP1 ZK proof bytes empty/garbage — they are never checked because the panic happens first.
3. Submit this payload as the `proof` argument to the pallet's `submit_proof`-style extrinsic (which calls `Self::verify_and_apply(proof)`), as any ordinary relayer would.
4. Execution reaches `evm/rust/src/conversions.rs:403` (`commitment.blockNumber.try_into().expect("block number out of bounds")`), which panics before the SP1 verifier or any BEEFY authority check runs.

Note: I was unable to fully confirm, within the available tool budget, whether the extrinsic that calls `verify_and_apply` is permissionless/unsigned (as ISMP consensus-proof submission is elsewhere in this codebase, e.g. the pallet-ismp `handle_unsigned` path) or requires a signed, fee-paying account — this distinction affects the ease of repeated DoS but not the existence of the panic itself. A Devin session with terminal access could confirm the extrinsic's dispatch origin/weight annotations in `modules/pallets/beefy-consensus-proofs/src/lib.rs` to close out this uncertainty.

### Citations

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

**File:** evm/rust/src/conversions.rs (L249-274)
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
