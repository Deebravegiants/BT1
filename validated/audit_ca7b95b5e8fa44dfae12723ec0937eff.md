### Title
BEEFY consensus verifiers count raw signature/vote count toward the supermajority threshold without deduplicating authority indices, unlike every other consensus client in the codebase - (File: `evm/src/consensus/EcdsaBeefy.sol`, `modules/consensus/beefy/verifier/src/lib.rs`)

### Summary
Both the Solidity (`EcdsaBeefy.sol`) and Rust (`beefy-verifier`) BEEFY consensus clients check the *raw count* of submitted votes/signatures against the 2/3+1 supermajority threshold before ever confirming those votes come from distinct authorities. Every other consensus verifier in this repo (Pharos, BSC, sync-committee) explicitly guards against a participant being counted more than once, but the BEEFY path does not.

### Finding Description
In `EcdsaBeefy.sol::verifyMmrUpdateProof`, the supermajority gate is evaluated purely on array length: [1](#0-0) 

and then each vote is turned into a `MerkleMultiProof.Leaf{index: vote.authorityIndex, hash: keccak256(authority)}` with no check that `authorityIndex` values are unique across the votes array: [2](#0-1) 

The exact same pattern exists in the Rust verifier used for the Substrate side, `verify_mmr_update_proof`: `signatures_length` (raw `Vec` length) is checked against the threshold, then each signature's `authority_indices` is pushed without a uniqueness check: [3](#0-2) 

This is architecturally the same bug class as the reported `QVSimpleStrategy._allocate()` issue: a threshold/limit check is performed against a *count* (`sigLen` / `signatures_length`, analogous to `voiceCreditsToAllocate`), while the actual constraint that should be enforced — one contribution per unique participant — is never validated or deducted against. Contrast this with the codebase's other three consensus clients, which all explicitly defend against the identical failure mode:
- Pharos: `verify_validator_membership` builds a `BTreeSet` of participant keys and rejects if `deduped.len() != participants.len()` (`Error::DuplicateParticipant`). [4](#0-3) 
- BSC: participation is derived from a fixed-width `Bitvector`, where each validator index maps to exactly one bit, structurally preventing a validator from being counted twice. [5](#0-4) 
- sync-committee: same bitvector-based counting, so a signer contributes at most one bit. [6](#0-5) 

BEEFY signatures are ECDSA signatures over a public commitment, gossiped/observable off-chain (unlike a secret ballot), so a relayer assembling a consensus proof can freely re-include the same authority's signature (or a different valid signature by the same authority over the same commitment, since BEEFY commitments are signed once per round but retransmitted) multiple times at will, inflating `sigLen`/`signatures_length` without needing any additional distinct authority's cooperation.

### Impact Explanation
If the merkle multi-proof step (`MerkleMultiProof.VerifyProof` in Solidity, `rs_merkle::MerkleProof::verify` in Rust) does not itself reject repeated leaf indices at the vote level, a minority (or even a single) colluding/compromised authority is sufficient to satisfy the "supermajority" gate that this consensus client relies on to advance `latestHeight`/`latest_beefy_height` and rotate the trusted authority set. This would let an attacker forge a BEEFY consensus update, forging finalized parachain state commitments that downstream ISMP request/response delivery, state proofs, and cross-chain message verification all trust — a direct unsound-state-commitment / forged-message-delivery class of impact, matching the High severity of the analog.

### Likelihood Explanation
Exploitability depends on whether the third-party `MerkleMultiProof`/`rs_merkle` multi-proof verification routines structurally reject duplicate leaf indices within a single proof (most multi-proof reconstructions sort-and-pair leaves by position, which would likely make a literal duplicate index corrupt the tree reconstruction and fail verification). **I was unable to locate or inspect the `MerkleMultiProof.sol` implementation or the `rs_merkle`/`merkle_mountain_range` crate source within the indexed codebase** (these are external dependencies not present in the index), so I cannot confirm whether submitting the same `authorityIndex` twice in `votes`/`signatures` is silently accepted (inflating the effective supermajority count) or is rejected by the multi-proof math itself. This is the central uncertainty in this finding and would need to be verified directly against the `@polytope-labs/solidity-merkle-trees` and `rs_merkle` library code (not indexed here) before treating this as confirmed-exploitable, as opposed to a defense-in-depth gap that happens to be masked by the underlying proof library's structure.

### Recommendation
- Before evaluating `checkParticipationThreshold`/`check_participation_threshold`, deduplicate `authorityIndex`/`sig.index` across the submitted votes (e.g., reject the proof if the number of *unique* indices is less than `votes.length`), mirroring the `DuplicateParticipant` check already used in the Pharos verifier.
- Add explicit unit tests (as already exist for Pharos, BSC, and sync-committee) asserting that a BEEFY proof containing a repeated `authorityIndex` is rejected even when the raw vote count clears the 2/3+1 threshold.
- Confirm and, if necessary, harden the external `MerkleMultiProof.VerifyProof` / `rs_merkle` verification to explicitly reject duplicate leaf indices, rather than relying on incidental behavior of the proof-reconstruction algorithm.

### Proof of Concept
Not independently reproducible from the indexed code alone, since the multi-proof verification library that would confirm or refute exploitability (`@polytope-labs/solidity-merkle-trees::MerkleMultiProof`, `rs_merkle`) is external and not present in this index. Conceptually:
1. Take a real, valid BEEFY signed commitment where only `k < 2/3+1` distinct authorities actually signed.
2. Duplicate one or more of those authorities' `Vote`/`SignatureWithAuthorityIndex` entries (same `authorityIndex`, same signature) in the `votes`/`signatures` array until `sigLen`/`signatures_length` reaches the `authoritySet.len` threshold.
3. Submit this proof to `EcdsaBeefy.verify` / `verify_mmr_update_proof`.
4. If the merkle multi-proof step does not reject the duplicated index, the proof passes `checkParticipationThreshold` and `InvalidAuthoritiesProof` never fires, despite only `k` distinct authorities actually having signed — analogous to `QVSimpleStrategy` allowing repeated allocation against a check that never accounts for prior consumption.

### Citations

**File:** evm/src/consensus/EcdsaBeefy.sol (L127-140)
```text
        uint256 sigLen = relayProof.signedCommitment.votes.length;
        uint256 latestHeight = relayProof.signedCommitment.commitment.blockNumber;
        Commitment memory commitment = relayProof.signedCommitment.commitment;
        if (
            commitment.validatorSetId != trustedState.currentAuthoritySet.id
                && commitment.validatorSetId != trustedState.nextAuthoritySet.id
        ) {
            revert UnknownAuthoritySet();
        }

        bool isCurrentAuthorities = commitment.validatorSetId == trustedState.currentAuthoritySet.id;
        AuthoritySetCommitment memory authoritySet =
            isCurrentAuthorities ? trustedState.currentAuthoritySet : trustedState.nextAuthoritySet;
        if (!checkParticipationThreshold(sigLen, authoritySet.len)) revert SuperMajorityRequired();
```

**File:** evm/src/consensus/EcdsaBeefy.sol (L152-162)
```text
        bytes32 commitmentHash = keccak256(Codec.Encode(commitment));
        MerkleMultiProof.Leaf[] memory authorities = new MerkleMultiProof.Leaf[](sigLen);
        for (uint256 i = 0; i < sigLen; i++) {
            Vote memory vote = relayProof.signedCommitment.votes[i];
            address authority = ECDSA.recover(commitmentHash, vote.signature);
            authorities[i] =
                MerkleMultiProof.Leaf({index: vote.authorityIndex, hash: keccak256(abi.encodePacked(authority))});
        }

        bool valid = MerkleMultiProof.VerifyProof(authoritySet.root, relayProof.proof, authorities, authoritySet.len);
        if (!valid) revert InvalidAuthoritiesProof();
```

**File:** modules/consensus/beefy/verifier/src/lib.rs (L109-171)
```rust
	let signatures_length = mmr.signed_commitment.signatures.len();
	let latest_height = mmr.signed_commitment.commitment.block_number;

	if trusted_state.latest_beefy_height >= latest_height {
		return Err(Error::StaleHeight {
			trusted_height: trusted_state.latest_beefy_height,
			current_height: latest_height,
		});
	}

	let commitment = mmr.signed_commitment.commitment.clone();

	// Pick the authority set the commitment claims to be signed under, then judge
	// participation against that set alone.
	let authority_set = if commitment.validator_set_id == trusted_state.current_authorities.id {
		&trusted_state.current_authorities
	} else if commitment.validator_set_id == trusted_state.next_authorities.id {
		&trusted_state.next_authorities
	} else {
		return Err(Error::UnknownAuthoritySet { id: commitment.validator_set_id });
	};

	if !check_participation_threshold(signatures_length as u32, authority_set.len) {
		return Err(Error::SuperMajorityRequired);
	}

	let mmr_root_data = commitment
		.payload
		.get_raw(&MMR_ROOT_PAYLOAD_ID)
		.ok_or(Error::MmrRootHashMissing)?;

	if mmr_root_data.len() != 32 {
		return Err(Error::InvalidMmrRootHashLength { len: mmr_root_data.len() });
	}
	let mmr_root = H256::from_slice(mmr_root_data);

	let commitment_hash = H::keccak256(&commitment.encode());
	let mut authority_leaves: Vec<[u8; 32]> = Vec::new();
	let mut authority_indices = Vec::new();

	for sig in mmr.signed_commitment.signatures.iter() {
		let uncompressed = H::secp256k1_recover(&commitment_hash.0, &sig.signature)
			.map_err(|_| Error::FailedToRecoverPublicKey)?;

		let hashed_uncompressed = H::keccak256(&uncompressed);

		let mut eth_address = [0u8; 20];
		eth_address.copy_from_slice(&hashed_uncompressed.as_ref()[12..]);

		let authority_address_hash = H::keccak256(&eth_address);

		authority_leaves.push(authority_address_hash.into());
		authority_indices.push(sig.index as usize);
	}

	let merkle_proof = MerkleProof::<MerkleHasher<H>>::new(mmr.authority_proof.clone());

	let valid = merkle_proof.verify(
		authority_set.keyset_commitment.into(),
		&authority_indices,
		&authority_leaves,
		authority_set.len as usize,
	);
```

**File:** modules/consensus/pharos/verifier/src/lib.rs (L143-157)
```rust
/// Verify that all participating validators are members of the trusted validator set.
fn verify_validator_membership(
	validator_set: &ValidatorSet,
	participants: &[BlsPublicKey],
) -> Result<(), Error> {
	let deduped: alloc::collections::BTreeSet<&[u8]> =
		participants.iter().map(|k| k.as_ref()).collect();
	if deduped.len() != participants.len() {
		return Err(Error::DuplicateParticipant);
	}
	if let Some(key) = participants.iter().find(|key| !validator_set.contains(key)) {
		return Err(Error::UnknownValidator { key: key.clone() });
	}
	Ok(())
}
```

**File:** modules/consensus/bsc/verifier/src/lib.rs (L63-90)
```rust
	let validators_bit_set = Bitvector::<VALIDATOR_BIT_SET_SIZE>::deserialize(
		extra_data.vote_address_set.to_le_bytes().to_vec().as_slice(),
	)
	.map_err(|_| Error::DeserializeVoteAddressSet)?;

	// `VALIDATOR_BIT_SET_SIZE` is a fixed 64-bit width; the active
	// validator set is smaller, so bits at positions `>= validators.len()`
	// have no corresponding validator. Setting them would inflate
	// `count_ones()` past the supermajority threshold without any extra
	// validator actually signing.
	if validators_bit_set
		.iter()
		.enumerate()
		.any(|(i, bit)| i >= current_validators.len() && *bit)
	{
		Err(Error::VoteAddressSetBeyondValidatorCount)?
	}

	// We have to use the same threshold specified in the bsc parlia consensus which is 2/3
	// https://github.com/bnb-chain/bsc/blob/da35ee13e2fe38efaeab2d6fb27f112332459b50/consensus/parlia/parlia.go#L557
	let participant_count = validators_bit_set
		.iter()
		.take(current_validators.len())
		.filter(|bit| **bit)
		.count();
	if participant_count < ((2 * current_validators.len()) / 3) {
		Err(Error::NotEnoughParticipants)?
	}
```

**File:** modules/consensus/sync-committee/verifier/src/lib.rs (L93-115)
```rust
	let sync_committee_bits = update.sync_aggregate.sync_committee_bits;

	// Verify sync committee has super majority participants. The bit
	// vector and the pubkey set should both be `SYNC_COMMITTEE_SIZE`,
	// but the threshold is computed against the actual pubkey set size
	// and any bit past it is treated as junk — otherwise an attacker
	// could pad `count_ones()` with positions that have no corresponding
	// validator and trivially clear the supermajority check.
	let committee_size = sync_committee_pubkeys.len();
	if sync_committee_bits
		.iter()
		.enumerate()
		.any(|(i, bit)| i >= committee_size && *bit)
	{
		Err(Error::InvalidUpdate("Sync committee bits set beyond committee size".into()))?
	}

	let sync_aggregate_participants: u64 =
		sync_committee_bits.iter().take(committee_size).filter(|b| **b).count() as u64;

	if sync_aggregate_participants < ((2 * committee_size as u64) / 3) + 1 {
		Err(Error::SyncCommitteeParticipantsTooLow)?
	}
```
