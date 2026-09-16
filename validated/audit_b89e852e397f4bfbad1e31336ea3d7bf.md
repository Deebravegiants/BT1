### Title
Missing duplicate-authority-index check in BEEFY consensus threshold verification allows relayer to potentially inflate signer count - ([File: evm/src/consensus/EcdsaBeefy.sol / modules/consensus/beefy/verifier/src/lib.rs])

### Summary
The BEEFY consensus verifiers (`EcdsaBeefy.sol` on EVM and the matching Rust `beefy-verifier`) compute the number of participating signers as `sigLen = relayProof.signedCommitment.votes.length` and then feed each vote's `authorityIndex` into a merkle multi-proof of authority-set membership, without ever checking that the submitted `authorityIndex`/signature pairs are unique. This is analogous to CVE-2016-15028's root cause: an integrity/quorum check ("supermajority of signatures") is computed from attacker-supplied data whose internal consistency (no duplicates) is never validated before being counted toward the security threshold.

### Finding Description
`checkParticipationThreshold(sigLen, authoritySet.len)` in `EcdsaBeefy.sol` gates supermajority acceptance purely on the *count* of submitted votes: [1](#0-0) 

The Rust counterpart does the same: `signatures_length = mmr.signed_commitment.signatures.len()` is checked against `check_participation_threshold`, and each vote's `authority_indices`/`authority_leaves` are built and passed straight into the merkle multi-proof verifier with no de-duplication: [2](#0-1) 

By contrast, other consensus clients in this codebase explicitly guard against this exact class of bug:
- The Pharos verifier de-duplicates participant keys before counting stake: `verify_validator_membership` rejects `deduped.len() != participants.len()` with `Error::DuplicateParticipant`. [3](#0-2) 
- The Tendermint verifier explicitly rejects validator sets with duplicate addresses via `ensure_unique_addresses`. [4](#0-3) 
- GRANDPA justification verification relies on `finality_grandpa::validate_commit`'s built-in `num_duplicated_precommits()` check. [5](#0-4) 
- BSC and sync-committee use bit-vectors, which are inherently incapable of representing the same validator twice.

BEEFY's ECDSA path has no equivalent safeguard: `votes` is a plain array, and nothing rejects two entries with the same `authorityIndex` (e.g., the same authority's signature submitted twice, or two different signatures both claiming the same index). If the underlying `MerkleMultiProof.VerifyProof` (external library, not visible in this index) does not itself reject duplicate leaf indices, a malicious/dishonest relayer could pad `votes` with repeated entries for authorities who did sign, inflating `sigLen` past the 2/3+1 supermajority threshold without actually gathering that many distinct signers' cooperation.

### Impact Explanation
If exploitable, this would allow a relayer to forge acceptance of a BEEFY consensus update (and therefore a forged state-commitment / MMR root) without a genuine supermajority of the relay chain's authority set signing off, directly enabling forged message delivery and unsound state commitment across Hyperbridge — a Critical-class outcome per the "Validate" criteria. Because the confirmation of this bypass depends on the exact duplicate-index handling inside the external `@polytope-labs/solidity-merkle-trees` `MerkleMultiProof.VerifyProof` implementation (not present in this repository's index) and the equivalent `MerkleProof::verify` used on the Rust side, I cannot fully confirm from the available code that the merkle proof itself accepts duplicate indices. This is the key uncertainty in this finding.

### Likelihood Explanation
The likelihood hinges entirely on whether the merkle multi-proof libraries accept duplicate leaf/index pairs. Given that every other consensus verifier in this codebase was explicitly hardened against duplicate-participant counting (pharos, tendermint, grandpa via library, bit-vector designs for bsc/sync-committee), while BEEFY's `votes` array received no equivalent treatment, this looks like a gap rather than an intentional design choice — but without visibility into the merkle proof library's duplicate-index behavior, exploitability cannot be conclusively proven from this repo's contents alone.

### Recommendation
Add an explicit uniqueness check on `authorityIndex` (Solidity) / `sig.index` (Rust) across all submitted votes before counting them toward `sigLen`/`signatures_length`, mirroring the `verify_validator_membership` de-duplication pattern already used in the Pharos verifier. Additionally, confirm (via the merkle-trees library source or targeted testing) whether `MerkleMultiProof.VerifyProof`/`MerkleProof::verify` accept duplicate indices in the leaf set, since that determines whether this gap is currently exploitable.

### Proof of Concept
Not able to construct a concrete end-to-end PoC without access to the `MerkleMultiProof`/`rs_merkle`-based multi-proof verifier implementation to confirm duplicate-index handling; this is flagged as a code-review-level gap analogous to the reference CVE's "improper validation of integrity check value," pending confirmation of the external library's behavior.

### Citations

**File:** evm/src/consensus/EcdsaBeefy.sol (L127-163)
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

**File:** modules/consensus/beefy/verifier/src/lib.rs (L105-176)
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
