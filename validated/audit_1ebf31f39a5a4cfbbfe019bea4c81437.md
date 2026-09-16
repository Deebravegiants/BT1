### Title
BEEFY authority-set supermajority check counts raw signature-array length, not distinct signers, allowing duplicate-vote inflation - ([File: evm/src/consensus/EcdsaBeefy.sol])

### Summary
`EcdsaBeefy.verifyMmrUpdateProof` (and its Rust equivalent `verify_mmr_update_proof`) determines whether a BEEFY commitment has supermajority (2/3+1) authority participation by counting the raw length of the submitted `votes`/`signatures` array, without first verifying that the underlying authority identities (`vote.authorityIndex` / `sig.index`) are distinct. This is the same bug class as CVE-2022-40716: a security-critical check (participation/authorization threshold) is evaluated over a list that can contain repeated identifying values, letting an attacker inflate the counted total without actually gathering that many distinct trusted signers.

### Finding Description
In `verifyMmrUpdateProof`, the participation check is: [1](#0-0) 

`sigLen` is simply `relayProof.signedCommitment.votes.length`. This value is checked against the 2/3+1 threshold via `checkParticipationThreshold(sigLen, authoritySet.len)`: [2](#0-1) 

The code then, for every entry in `votes` (including repeats), recovers a signer address and builds a merkle leaf keyed by the attacker-supplied `vote.authorityIndex`: [3](#0-2) 

Nowhere in this function is `vote.authorityIndex` (or the recovered `authority` address) checked for uniqueness before it is counted toward `sigLen`. An attacker (any unprivileged relayer submitting a BEEFY consensus proof through `verify()`) can take one or a few genuinely valid authority signatures and repeat the identical `(authorityIndex, signature)` pair many times in the `votes` array, inflating `sigLen` to clear the supermajority threshold while the true number of distinct signing authorities remains far below 2/3+1.

The equivalent Rust BEEFY verifier has the identical structural gap — `signatures_length` is taken directly from `mmr.signed_commitment.signatures.len()` and used for the threshold check, and `authority_leaves`/`authority_indices` are built by iterating the same (potentially duplicated) signature list without a dedup step: [4](#0-3) [5](#0-4) 

This is in sharp contrast to other consensus verifiers in the same codebase that explicitly guard against exactly this class of bug: Pharos's `verify_validator_membership` rejects duplicate participant keys via a `BTreeSet` cardinality check before counting stake: [6](#0-5) 
and GRANDPA's justification verification explicitly rejects `num_duplicated_precommits() > 0`: [7](#0-6) 
BEEFY has no analogous explicit uniqueness check on `authorityIndex`/`sig.index` prior to (or independent of) the merkle multi-proof call.

### Impact Explanation
BEEFY consensus state (`currentAuthoritySet`/`nextAuthoritySet`, `latestHeight`) backs all downstream ISMP state/parachain-header verification for chains using the ECDSA BEEFY client. If the supermajority check can be satisfied by repeating a small number of real signatures rather than gathering true 2/3+1 distinct authority signatures, an attacker controlling far fewer than 2/3+1 of the authority set's private keys could forge acceptance of a malicious BEEFY commitment (arbitrary MMR root / parachain header), which is then trusted to prove parachain state commitments used for message delivery, mint/burn, and intents settlement across Hyperbridge. This is a forged-message-delivery / unsound-state-commitment class impact.

### Likelihood Explanation
Whether this is exploitable end-to-end also depends on whether the external `MerkleMultiProof.VerifyProof` (from `@polytope-labs/solidity-merkle-trees`) independently rejects leaf sets containing duplicate `index` values; that library's internals were not available for inspection in this index, so I cannot confirm with certainty that the merkle-proof step itself blocks duplicate-index leaves. However, the `checkParticipationThreshold` gate is unconditionally vulnerable to inflation by duplicate votes regardless of the merkle-proof outcome, and the codebase's own precedent (Pharos, GRANDPA) treats "reject duplicate participants before counting" as a required, independent safeguard — a safeguard absent here. The proof is submitted by any relayer calling the public `verify()` entrypoint, so the attack surface is reachable without special privileges.

### Recommendation
Before computing `sigLen`/`signatures_length` and before threshold comparison, deduplicate on `vote.authorityIndex` (Solidity) / `sig.index` (Rust) — e.g., reject the proof if the set of authority indices has fewer distinct elements than `votes.length`/`signatures.len()` — mirroring the `verify_validator_membership` pattern already used in the Pharos verifier (`modules/consensus/pharos/verifier/src/lib.rs:143-157`).

### Proof of Concept
1. Obtain one valid signed vote `(authorityIndex = i, signature = s)` from a legitimately signing BEEFY authority for a commitment hash `commitmentHash`.
2. Construct `relayProof.signedCommitment.votes` as `k` copies of `(i, s)` where `k >= ((2 * authoritySet.len) / 3) + 1`, i.e., duplicate the single valid vote enough times to satisfy `checkParticipationThreshold(sigLen, authoritySet.len)` in `evm/src/consensus/EcdsaBeefy.sol:140`.
3. Call `EcdsaBeefy.verify(previousState, proof)` with this crafted `RelayChainProof`. `sigLen` (=`k`) passes the supermajority check even though only one distinct authority actually signed; if the underlying `MerkleMultiProof.VerifyProof` call does not itself reject repeated `index` values in the `authorities` leaf array, the proof is accepted and `trustedState` is updated using an attacker-influenced MMR root/authority set, despite lacking a genuine 2/3+1 quorum of distinct signers.

### Citations

**File:** evm/src/consensus/EcdsaBeefy.sol (L126-140)
```text
    {
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

**File:** modules/consensus/beefy/verifier/src/lib.rs (L146-162)
```rust
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

**File:** modules/consensus/grandpa/primitives/src/justification.rs (L75-90)
```rust
		match finality_grandpa::validate_commit(&self.commit, voters, &ancestry_chain) {
			Ok(ref result) if result.is_valid() => {
				if result.num_duplicated_precommits() > 0 ||
					result.num_invalid_voters() > 0 ||
					result.num_equivocations() > 0
				{
					Err(anyhow!("Invalid commit, found one of `duplicate precommits`, `invalid voters`, or `equivocations` {result:?}"))?
				}
			},
			err => {
				let result = err.map_err(|_| {
					anyhow!("[verify_with_voter_set] Invalid ancestry while validating commit!")
				})?;
				Err(anyhow!("invalid commit in grandpa justification: {result:?}"))?
			},
		}
```
