### Title
Duplicate authority votes/signatures can be counted multiple times to forge BEEFY consensus supermajority - (File: evm/src/consensus/EcdsaBeefy.sol / modules/consensus/beefy/verifier/src/lib.rs)

### Summary
The BEEFY consensus verifiers (`EcdsaBeefy.sol` on EVM and the Rust `beefy/verifier`) compute the number of participating validators as simply `votes.length` / `signatures.len()`, without checking that each `authorityIndex` (or signer) appears only once. A relayer submitting a consensus proof can duplicate the same authority's vote/signature entry multiple times in the array to inflate the participation count past the 2/3+1 supermajority threshold, without any additional distinct validator actually signing — the same root-cause pattern as the reported PoolGovernance bug, where a `count` was incremented per submitted vote instead of per unique voter.

### Finding Description
In `EcdsaBeefy::verifyMmrUpdateProof`, `sigLen` is taken directly from the caller-supplied `relayProof.signedCommitment.votes.length`, and the supermajority check `checkParticipationThreshold(sigLen, authoritySet.len)` is performed against this raw count before any uniqueness check on `vote.authorityIndex`: [1](#0-0) 

Similarly, in the Rust verifier `verify_mmr_update_proof`, `signatures_length` is `mmr.signed_commitment.signatures.len()`, checked against the threshold before iterating over signatures to build `authority_leaves`/`authority_indices`, again with no de-duplication: [2](#0-1) 

Both `MerkleMultiProof.VerifyProof` (Solidity) and `rs_merkle`'s `MerkleProof::verify` (Rust) are membership proofs that verify supplied `(index, hash)` leaf pairs are consistent with a committed root — they do not, and are not designed to, reject a caller who repeats the same valid `(index, hash)` pair multiple times in their leaf list. A duplicate entry for the same authority index with the same recovered signer hash is internally consistent and will still validate against the authority-set merkle root.

Contrast this with the other consensus clients in the same codebase, which were already hardened against exactly this class of issue: BSC and sync-committee track participants via a fixed-size bitvector (a bit can only be set once, so duplicates are structurally impossible) and explicitly guard against out-of-range bits: [3](#0-2) [4](#0-3) 
and Pharos explicitly deduplicates participant keys with a `BTreeSet` check before computing stake: [5](#0-4) 

The BEEFY verifier (both the Solidity and Rust implementations) lacks this equivalent protection: it counts raw array length of votes/signatures rather than the count of distinct authority indices, exactly mirroring the root cause in the external report (`count` incremented from the raw submission rather than from de-duplicated state).

### Impact Explanation
A relayer submitting a BEEFY consensus proof to `EcdsaBeefy::verify` (or the Rust equivalent) is an unprivileged, permissionless action. By repeating one or a few real (or even self-obtained, e.g. from a single equivocating/compromised validator) signatures multiple times in the `votes`/`signatures` array, an attacker can make the on-chain/off-chain light client believe a 2/3+1 supermajority of the authority set has signed a commitment when in reality far fewer distinct validators did. This directly breaks the consensus-verification invariant Hyperbridge relies on to accept new parachain header commitments, enabling forged/unsound state commitments to be accepted, which downstream allows fraudulent state and non-membership proofs (and thus forged message delivery / unbacked mint on connected token bridges) to be treated as finalized. This is a critical/high-impact break of the fundamental bridge security assumption.

### Likelihood Explanation
Likelihood is high: constructing this proof requires no special privilege — only assembling an array with a repeated `Vote`/signature entry, which is trivial calldata manipulation. It does not require compromising a supermajority of validators; a small number of real signatures (or even a single colluding/leaked validator key, explicitly out of scope, but the base case with any handful of honestly-obtained signatures already reduces the required distinct signer count) can be replayed to pad `sigLen`/`signatures_length` past the threshold.

### Recommendation
Deduplicate on `authorityIndex` (or recovered signer) before computing `sigLen`/`signatures_length`, and before checking `checkParticipationThreshold` / `check_participation_threshold`. Concretely: build a set of unique authority indices from `votes`/`signatures`, reject the proof if any index repeats, and use the size of that unique set as the participation count that is compared against the supermajority threshold, mirroring the deduplication check already present in `pharos/verifier` (`verify_validator_membership`) and the structural uniqueness guarantee bitvectors provide in the BSC/sync-committee verifiers.

### Proof of Concept
1. Take a valid BEEFY `SignedCommitment` for which fewer than 2/3+1 of the authority set have actually signed (e.g., only 40% of validators signed).
2. Construct `relayProof.signedCommitment.votes` (Solidity) / `mmr.signed_commitment.signatures` (Rust) by repeating each real `Vote`/`SignatureWithAuthorityIndex` entry enough times (e.g., duplicating each once) so that `votes.length` / `signatures.len()` exceeds `(2 * authoritySet.len) / 3 + 1`.
3. Build `authorities`/`authority_leaves` from this padded array — each duplicated entry still recovers to a valid signer address and its correct `authorityIndex`, so `MerkleMultiProof.VerifyProof` / `rs_merkle`'s `verify` against the authority-set root succeeds (the proof only asserts that each supplied `(index, hash)` is consistent with the root, and repeated consistent pairs do not break that).
4. Call `EcdsaBeefy.verify(previousState, proof)` (or invoke `verify_mmr_update_proof`) with this padded proof.
5. Observe that `checkParticipationThreshold(sigLen, authoritySet.len)` / `check_participation_threshold` passes and the consensus state is advanced/accepted, even though actual distinct validator participation was below the real 2/3+1 supermajority.

### Citations

**File:** evm/src/consensus/EcdsaBeefy.sol (L127-162)
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

        uint256 payloadLength = commitment.payload.length;
        bytes32 mmrRoot;
        for (uint256 i = 0; i < payloadLength; i++) {
            if (commitment.payload[i].id == MMR_ROOT_PAYLOAD_ID && commitment.payload[i].data.length == 32) {
                mmrRoot = Bytes.toBytes32(commitment.payload[i].data);
            }
        }
        if (mmrRoot == bytes32(0)) revert MmrRootHashMissing();

        // verify the commitment
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

**File:** modules/consensus/beefy/verifier/src/lib.rs (L105-162)
```rust
pub fn verify_mmr_update_proof<H: Keccak256 + EcdsaRecover + Send + Sync>(
	mut trusted_state: ConsensusState,
	mmr: MmrProof,
) -> Result<(ConsensusState, H256), Error> {
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

**File:** modules/consensus/pharos/verifier/src/lib.rs (L144-157)
```rust
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
