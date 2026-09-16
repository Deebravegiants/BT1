### Title
BEEFY consensus verifier counts duplicate authority indices toward the 2/3+1 supermajority threshold, permitting forged consensus updates without a genuine majority - (File: modules/consensus/beefy/verifier/src/lib.rs)

### Summary
The reported ML-DSA bug is a missing uniqueness/strict-ordering check on a set of indices that is used to gate a security property (signature validity). `verify_mmr_update_proof` in Hyperbridge's BEEFY verifier has the same class of defect: it never checks that the authority indices attached to submitted signatures are unique before using the raw count of submitted signatures to satisfy the 2/3+1 supermajority requirement.

### Finding Description
`verify_mmr_update_proof` builds `authority_leaves`/`authority_indices` directly from `mmr.signed_commitment.signatures` without deduplicating by `sig.index`: [1](#0-0) 

The supermajority check is performed on `signatures_length = mmr.signed_commitment.signatures.len()` — the raw length of the attacker-controlled signature array — compared against `authority_set.len`: [1](#0-0) 

There is no check anywhere in this function, or in `ConsensusMessage`/`MmrProof` decoding, that `sig.index` values are distinct. A relayer submitting a consensus proof can include the *same* valid `(index, signature)` pair multiple times in `mmr.signed_commitment.signatures`. Each duplicate entry recovers to the same already-validated authority address and produces the same leaf/index pair fed into `MerkleProof::verify`, but each duplicate still increments `signatures_length`, which is the only quantity checked against the 2/3+1 threshold. This mirrors the ML-DSA `monotonic` regression: a value that is supposed to represent a set of *distinct* participants (hint indices there, authority indices here) is validated with a check that tolerates repeats, letting an attacker inflate a count that a downstream security decision depends on.

### Impact Explanation
If duplicate `(index, signature)` entries are accepted by the merkle multi-proof step (each entry still correctly proves membership of that one real authority, so there's no reason for `MerkleProof::verify` to reject a repeated but internally-consistent leaf/index pair), an attacker who controls or colludes with fewer than 2/3+1 of the current BEEFY authority set can pad the signature array with duplicates of the genuine signatures they do have, satisfy `check_participation_threshold`, and get `verify_mmr_update_proof` to accept a new trusted MMR root / authority-set rotation. This is a forged consensus update: it can be used to inject an unsound state commitment into `ConsensusState`, from which downstream state-proof verification (parachain header inclusion, and eventually ISMP message/state proofs) inherits false trust — directly enabling forged message delivery or unbacked state claims reachable by any relayer submitting a consensus proof.

### Likelihood Explanation
Exploitability hinges on whether the underlying `rs_merkle::MerkleProof::verify` multi-proof implementation tolerates a repeated `(index, leaf)` pair in its input list without rejecting it (I could not fully verify `rs_merkle`'s internal handling of duplicate indices within this session, as it is a third-party dependency without inspectable source in this index). If `rs_merkle` internally deduplicates or rejects repeated indices, this specific bypass is closed at that layer; if it does not, the Hyperbridge-side counting bug is directly exploitable by any relayer that already possesses a sub-threshold set of genuine authority signatures — a realistic scenario after partial authority-set compromise or collusion.

### Recommendation
In `verify_mmr_update_proof`, deduplicate `mmr.signed_commitment.signatures` by `sig.index` (e.g., via a `BTreeSet`) before computing `signatures_length`, and reject the proof if any index repeats — mirroring the fix pattern of rejecting non-unique/non-strictly-increasing indices from the reported ML-DSA advisory. Apply the analogous fix to the Solidity `EcdsaBeefy.verifyMmrUpdateProof`, which has the identical structure (`sigLen = relayProof.signedCommitment.votes.length` used directly as the threshold count without duplicate-index checking): [2](#0-1) 

### Proof of Concept
1. Obtain genuine BEEFY signatures from authorities `{A1 … Ak}` where `k < 2/3 * authority_set.len + 1`.
2. Construct `mmr.signed_commitment.signatures` by repeating each `(index_i, signature_i)` enough times so that `signatures.len() >= 2/3 * authority_set.len + 1`.
3. Submit this as a `ConsensusMessage` to `verify_consensus`. `check_participation_threshold` passes on the padded length; each duplicate entry still recovers a valid, already-authorized address and (if the merkle multi-proof library does not reject repeated index/leaf pairs) `MerkleProof::verify` succeeds, since every proven leaf is a real, unaltered leaf of the authority tree.
4. The forged commitment is accepted, updating `trusted_state.latest_beefy_height` and potentially rotating in an attacker-influenced `next_authorities` set, without ever having collected a genuine 2/3+1 supermajority.

### Citations

**File:** modules/consensus/beefy/verifier/src/lib.rs (L109-133)
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
```

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
