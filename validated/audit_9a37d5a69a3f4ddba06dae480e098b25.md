## Analog Found

### Title
Supermajority signature-count check in BEEFY consensus verification can be satisfied by duplicating a single authority's vote - (File: evm/src/consensus/EcdsaBeefy.sol / modules/consensus/beefy/verifier/src/lib.rs)

### Summary
Both the Solidity and Rust BEEFY light-client verifiers derive the "supermajority" participation count from the raw length of the submitted votes/signatures array, and then verify authority membership via a merkle **multi**-proof keyed by `authorityIndex`. Neither path checks that the `authorityIndex` values in the submitted vote list are distinct. This mirrors the `QVBaseStrategy.reviewThreshold` bug: the vote *count* used to satisfy a threshold is not tied to distinct *voters*, so one real vote can be repeated to counterfeit consensus among many.

### Finding Description
In `EcdsaBeefy.sol::verifyMmrUpdateProof`, the number of signatures `sigLen` is simply `relayProof.signedCommitment.votes.length`, and this raw count is checked against the 2/3+1 supermajority threshold: [1](#0-0) 

The same votes array is then converted into merkle leaves keyed by `vote.authorityIndex` and checked for set membership with `MerkleMultiProof.VerifyProof`: [2](#0-1) 

Nowhere in this function (or its Rust counterpart) is there a check that `authorityIndex` values are unique across the submitted votes. The Rust verifier has the identical structure — `signatures_length` is the raw `Vec::len()` and is compared against the threshold before any uniqueness check on `authority_indices`: [3](#0-2) [4](#0-3) 

The threshold check itself is a plain arithmetic comparison of a length to a computed bound, with no notion of "who" is being counted: [5](#0-4) [6](#0-5) 

By contrast, the Pharos verifier in this same codebase explicitly guards against exactly this class of bug by deduplicating participant keys before computing stake participation — demonstrating that the project is aware of "same signer counted multiple times" as a real threat model, but this fix was not applied to the BEEFY (Solidity or Rust) or the fast-finality BSC path in the same way: [7](#0-6) 

Because `authorityIndex` is attacker-supplied per vote entry (the `RelayChainProof`/`ConsensusMessage` is submitted by an unprivileged relayer calling the public `verify`/`verify_consensus` entry points), a relayer holding just one legitimately-signed vote for a commitment can construct a `votes`/`signatures` array that repeats that single `(authorityIndex, signature)` pair `sigLen` times — satisfying `sigLen >= (2/3)*total + 1` — while the merkle multi-proof only needs to prove membership for the (repeated) set of indices, which any standard merkle multi-proof/verify implementation resolves per unique index/leaf pair rather than "no duplicates allowed." The BFT security assumption (2/3+1 *distinct* authorities must have signed) is reduced to "one authority signed," breaking the entire trust model of the light client.

### Impact Explanation
If exploitable, an attacker relayer could forge acceptance of a BEEFY consensus update and downstream parachain header/state commitments using only one authority's genuine signature over an otherwise-legitimate (or otherwise attacker-crafted) commitment, instead of a genuine 2/3+1 supermajority. This is a direct break of consensus verification soundness underlying `EvmHost`'s trusted state, enabling forged message delivery/unsound state commitments for cross-chain messages relayed through Hyperbridge — a Critical/High class of vulnerability per the report's own severity precedent (bypassing a threshold check meant to require multiple independent parties).

### Likelihood Explanation
The `verify`/`verify_consensus` functions are the exact reachable entry points for any relayer submitting a BEEFY consensus proof — no special privilege is required, matching the "unprivileged... relayer" reachability requirement. Constructing the duplicated-vote payload requires no cryptographic breakage, only re-use of one obtained signature, making exploitation straightforward if the underlying merkle multi-proof verification does not itself reject duplicate indices (which needs confirmation against the exact `MerkleMultiProof.VerifyProof`/`rs_merkle::MerkleProof::verify` semantics, both external to this repository).

### Recommendation
Before applying the participation threshold, deduplicate `authorityIndex` (and/or recovered `authority` addresses) across the submitted votes/signatures — as already done for the Pharos verifier — and count only the number of *distinct* authority indices, not the raw array length, in both `EcdsaBeefy.sol::verifyMmrUpdateProof` and `modules/consensus/beefy/verifier/src/lib.rs::verify_mmr_update_proof`.

### Proof of Concept
1. Relayer observes one valid BEEFY vote `(authorityIndex = k, signature = sig_k)` for commitment `C` from the real authority set (these are broadcast on the relay chain's gossip network, so obtaining one is trivial).
2. Relayer builds `relayProof.signedCommitment.votes` (or `mmr.signed_commitment.signatures`) as `[(k, sig_k), (k, sig_k), (k, sig_k), ...]` repeated until `sigLen >= (2*authoritySet.len)/3 + 1`.
3. `checkParticipationThreshold`/`check_participation_threshold` passes because it only checks array length.
4. The merkle-multi-proof step is constructed for the (repeated) index `k`, which is a real leaf in the authority set, so membership verification succeeds.
5. The consensus update is accepted as if signed by a supermajority, despite only one authority actually signing.

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

**File:** evm/src/consensus/EcdsaBeefy.sol (L151-163)
```text
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

**File:** evm/src/consensus/EcdsaBeefy.sol (L240-243)
```text
    // @dev Check for supermajority participation.
    function checkParticipationThreshold(uint256 len, uint256 total) internal pure returns (bool) {
        return len >= ((2 * total) / 3) + 1;
    }
```

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

**File:** modules/consensus/beefy/verifier/src/lib.rs (L145-175)
```rust
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

	if !valid {
		Err(Error::InvalidAuthoritiesProof)?;
	}
```

**File:** modules/consensus/beefy/verifier/src/lib.rs (L258-261)
```rust
/// Checks for supermajority participation
fn check_participation_threshold(len: u32, total: u32) -> bool {
	len >= ((2 * total) / 3) + 1
}
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
