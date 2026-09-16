### Title
BEEFY consensus proof verification counts raw signature count toward the supermajority threshold without deduplicating authority indices, allowing signature replay to forge finality - ([File: modules/consensus/beefy/verifier/src/lib.rs] / [File: evm/src/consensus/EcdsaBeefy.sol])

### Summary
Both the Rust BEEFY light-client verifier (`verify_mmr_update_proof` in `modules/consensus/beefy/verifier/src/lib.rs`) and its Solidity counterpart (`verifyMmrUpdateProof` in `evm/src/consensus/EcdsaBeefy.sol`) compute the number of participating signers as the raw length of the submitted signature/vote array (`signatures_length` / `sigLen`) and compare that count directly against the 2/3+1 supermajority threshold via `check_participation_threshold` / `checkParticipationThreshold`. Neither function checks that the `authorityIndex` values referenced by the signatures are unique before counting them toward the threshold, unlike every other consensus client in this codebase (Pharos `verify_validator_membership`, GRANDPA's `num_duplicated_precommits`/`num_equivocations` check, Tendermint's `ensure_unique_addresses`, BSC's bitset-based participant selection), which all explicitly guard against a signer/participant being counted more than once. [1](#0-0) [2](#0-1) 

### Finding Description
`verify_mmr_update_proof` derives `signatures_length` straight from `mmr.signed_commitment.signatures.len()` and checks it against the threshold *before* doing any authority-index deduplication: [3](#0-2) 

It then loops over `mmr.signed_commitment.signatures`, recovering an address for every signature and appending `sig.index as usize` to `authority_indices` without checking for repeats: [4](#0-3) 

The Solidity `EcdsaBeefy.sol` implementation follows the identical pattern: `sigLen` (the raw `votes.length`) is checked against `checkParticipationThreshold` before the loop that recovers signer addresses and builds a `MerkleMultiProof.Leaf[]` array keyed by `vote.authorityIndex`: [5](#0-4) 

This mirrors the CVE-2026-72917 bug class: a check meant to enforce a threshold of *distinct* participants ("two distinct recovery codes") is satisfied by counting raw submitted items ("recoveryCodes.length") rather than deduplicated identities. Here, a relayer/prover assembling a BEEFY consensus proof from real gossiped signatures (or replaying an old, still-valid signature for the same commitment/authority set from a signer who has already voted) can pad the `votes`/`signatures` array with repeated entries for the same `authorityIndex` to inflate `sigLen`/`signatures_length` past the 2/3+1 threshold, even though the number of *distinct* signing authorities is far below supermajority. Because `check_participation_threshold`/`checkParticipationThreshold` runs on the unfiltered length, this check can pass without a genuine supermajority of unique validators.

Contrast this with Pharos' membership check, which explicitly rejects duplicates before any threshold or signature check is performed: [6](#0-5) 

And Tendermint's explicit uniqueness guard on validator sets used in voting-power calculations: [7](#0-6) 

BEEFY has no equivalent safeguard in either its Rust or Solidity verifier.

### Impact Explanation
BEEFY consensus verification underpins Hyperbridge's relay-chain-to-EVM message delivery pipeline (`EcdsaBeefy`/`SP1Beefy` feed `ConsensusRouter` → `HandlerV2`/`EvmHost`, and the Rust verifier is used by `ismp-beefy` on the parachain side). If the participation threshold can be satisfied without a genuine 2/3+1 of distinct authorities, an attacker with access to fewer than 2/3+1 real validator signatures over a commitment (e.g., collected from public gossip, or a minority coalition) could pad the proof with duplicate signature entries to pass `SuperMajorityRequired`/`check_participation_threshold`, causing the light client to accept a state/MMR-root update and any parachain header commitments bundled with it as finalized. This is a forged-message-delivery / unsound state-commitment class of vulnerability — it could let an attacker advance the trusted BEEFY state (and thus which state commitments `HandlerV2`/`EvmHost` trust for token bridge mint/burn and message delivery) using a minority of validator signatures.

### Likelihood Explanation
Exploitability depends on whether the downstream Merkle multi-proof verification (`MerkleMultiProof.VerifyProof` in Solidity, or `rs_merkle`/`beefy_merkle_tree` `MerkleProof::verify` in Rust) actually accepts an `authority_leaves`/`authorities` array containing duplicate `(index, hash)` entries and still produces a valid root. That library code is an external dependency (`@polytope-labs/solidity-merkle-trees`, `rs-merkle`) not vendored in this repository, so I could not directly confirm whether duplicate-index leaves are silently tolerated or cause a hash mismatch that would incidentally block the attack. This uncertainty means the severity of this specific finding cannot be fully confirmed from the code available in this index — the counting logic itself (`sigLen`/`signatures_length`) is unambiguously not deduplicated, but whether the merkle-proof step provides an incidental backstop is unverified.

### Recommendation
Deduplicate signer/authority indices before computing the participation count used in `check_participation_threshold`/`checkParticipationThreshold`, e.g., collect `authority_indices` into a `BTreeSet`/mapping and use its cardinality (not the raw array length) for the threshold check, mirroring the explicit duplicate-rejection pattern already used in `verify_validator_membership` (Pharos) and `ensure_unique_addresses` (Tendermint). Apply the same fix symmetrically to both `modules/consensus/beefy/verifier/src/lib.rs::verify_mmr_update_proof` and `evm/src/consensus/EcdsaBeefy.sol::verifyMmrUpdateProof`.

### Proof of Concept
1. Obtain valid BEEFY signatures from `f` real authorities (where `f` is less than 2/3+1 of the total authority set) over a legitimate commitment for a target block/MMR root.
2. Construct a `signed_commitment.signatures` (Rust) / `signedCommitment.votes` (Solidity) array that repeats these `f` valid `(index, signature)` pairs enough times so that `signatures_length`/`sigLen` reaches `((2 * total) / 3) + 1`.
3. Submit this proof to `verify_mmr_update_proof` / `EcdsaBeefy.verifyMmrUpdateProof`. The `check_participation_threshold`/`checkParticipationThreshold` check passes because it only inspects array length, not distinct authority indices.
4. If the subsequent Merkle multi-proof verification does not itself reject duplicate leaf indices (unverified due to the external library dependency), the proof is accepted, and the light client stores a new trusted BEEFY state/MMR root backed by fewer than a genuine supermajority of validators.

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

**File:** modules/consensus/beefy/verifier/src/lib.rs (L149-162)
```rust
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

**File:** evm/src/consensus/EcdsaBeefy.sol (L122-162)
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

**File:** modules/consensus/tendermint/verifier/src/verifier.rs (L217-229)
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
}
```
