### Title
Threshold check counts raw BEEFY vote/signature entries instead of unique authority indices, allowing a single key holder to inflate participation past the supermajority gate - ([File: modules/consensus/beefy/verifier/src/lib.rs], [File: evm/src/consensus/EcdsaBeefy.sol])

### Summary
Both the Rust BEEFY verifier (`verify_mmr_update_proof` in [1](#0-0) ) and its Solidity twin `verifyMmrUpdateProof` in [2](#0-1)  compute the BEEFY supermajority threshold from the raw count of submitted votes/signatures (`signatures_length` / `sigLen`), before any check that the `authority_index`/`authorityIndex` values attached to those votes are distinct. This mirrors CVE-2020-15093 (tough / TUF, GHSA-5q2r-92f9-4m49), where the reference implementation counted signatures toward a quorum threshold without verifying the signing keys were unique, letting one key holder forge "supermajority" by supplying multiple valid signatures.

### Finding Description
In `verify_mmr_update_proof` [3](#0-2) , `signatures_length` is simply `mmr.signed_commitment.signatures.len()` — the number of `(index, signature)` entries the relayer supplied — and it is passed straight into `check_participation_threshold` [4](#0-3)  to gate the 2/3+1 supermajority requirement. Only *after* this gate passes does the code recover each signature's address and build `authority_indices`/`authority_leaves` [5](#0-4) , which are then checked for merkle membership. Nowhere in this path is `authority_indices` deduplicated, nor is there a check that all `sig.index` values are distinct before or after the merkle-proof step.

The Solidity `EcdsaBeefy.verifyMmrUpdateProof` follows the identical structure: `sigLen` gates `checkParticipationThreshold` [6](#0-5)  before the per-vote loop recovers addresses and builds `MerkleMultiProof.Leaf[]` entries keyed by the caller-supplied `vote.authorityIndex` [7](#0-6) .

Because `sigLen`/`signatures_length` is just the array length of relayer-controlled input, a relayer holding (or having captured/replayed) a single valid authority signature over the commitment hash can pad the `votes`/`signatures` array with repeated copies of that one signature (attached to the same or bogus `authorityIndex` values) to inflate the count past `(2*total)/3 + 1` without those entries representing distinct authorities. Whether this ultimately succeeds the merkle multi-proof step depends on the external `MerkleMultiProof.VerifyProof` (an out-of-repo dependency, `@polytope-labs/solidity-merkle-trees`) and the underlying `MerkleProof` crate's handling of duplicate indices — this repo does not vendor that library, so I could not confirm from the indexed code whether it structurally rejects duplicate leaf indices. What is certain and in-scope is that the threshold decision itself is made purely on raw vote count, with no uniqueness check on authority index anywhere in `modules/consensus/beefy/verifier/src/lib.rs` or `evm/src/consensus/EcdsaBeefy.sol`.

### Impact Explanation
If the downstream merkle multi-proof verification (external library) does not itself enforce unique/sorted, non-repeating leaf indices, an attacker controlling even a small minority of BEEFY authority keys (or a single leaked/authority key) could forge a "supermajority" commitment for an MMR root of their choosing. Since BEEFY consensus proofs are the trust root for parachain header/state finality accepted by `EcdsaBeefy`/`ismp-beefy`, a forged supermajority could let an attacker post arbitrary finalized state commitments into Hyperbridge, enabling forged message delivery and unbacked state commitments across all state machines relying on this consensus client — a critical bridge-security violation if exploitable.

### Likelihood Explanation
Exploitability hinges entirely on whether the external `MerkleMultiProof`/`MerkleProof` verification libraries silently tolerate duplicate/index-colliding leaves in a multiproof. This repo's own logic performs zero uniqueness enforcement, so the entire burden of soundness rests on a dependency not present in-scope. This is a structural gap analogous to the reported CVE, even if I cannot confirm end-to-end exploitability without access to the external library's source.

### Recommendation
Deduplicate `authority_index`/`authorityIndex` values (e.g., via a `BTreeSet`/index-uniqueness check, mirroring the `ensure_unique_addresses` pattern already used in `modules/consensus/tendermint/verifier/src/verifier.rs` [8](#0-7)  and the `DuplicateParticipant` check in `modules/consensus/pharos/verifier/src/lib.rs` [9](#0-8) ) before computing the participation count in both `verify_mmr_update_proof` (Rust) and `verifyMmrUpdateProof` (Solidity), so the supermajority threshold is judged against the count of *unique* authority indices, not raw signature/vote array length.

### Proof of Concept
Conceptual: an attacker with one valid BEEFY authority signature over `commitmentHash` submits a `RelayChainProof`/`MmrProof` whose `votes`/`signatures` array repeats that single `(authorityIndex, signature)` pair (or the same signature under several claimed indices) enough times to satisfy `sigLen >= (2*total)/3 + 1`. `checkParticipationThreshold`/`check_participation_threshold` passes based on array length alone; the actual number of *distinct* authorities that produced a signature is 1. If the merkle multi-proof primitive does not reject repeated/duplicate leaf indices, `verify`/`verifyMmrUpdateProof` returns success and updates trusted consensus state with an attacker-chosen MMR root and, transitively, forged parachain state commitments.

### Citations

**File:** modules/consensus/beefy/verifier/src/lib.rs (L105-133)
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

**File:** modules/consensus/beefy/verifier/src/lib.rs (L258-261)
```rust
/// Checks for supermajority participation
fn check_participation_threshold(len: u32, total: u32) -> bool {
	len >= ((2 * total) / 3) + 1
}
```

**File:** evm/src/consensus/EcdsaBeefy.sol (L122-141)
```text
    function verifyMmrUpdateProof(BeefyConsensusState memory trustedState, RelayChainProof memory relayProof)
        internal
        pure
        returns (BeefyConsensusState memory, bytes32)
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

**File:** modules/consensus/tendermint/verifier/src/verifier.rs (L217-228)
```rust
/// Rejects a validator set that reuses the same address twice. Each address is a
/// hash of its public key, so a duplicate signals a set that was not built honestly.
fn ensure_unique_addresses(
	validators: &[cometbft::validator::Info],
) -> Result<(), VerificationError> {
	let unique = validators.iter().map(|v| v.address).collect::<BTreeSet<_>>();
	if unique.len() != validators.len() {
		return Err(VerificationError::ValidatorSetError(
			"duplicate validator address in set".to_string(),
		));
	}
	Ok(())
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
