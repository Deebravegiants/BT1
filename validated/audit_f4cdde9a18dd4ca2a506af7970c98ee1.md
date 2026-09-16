## Analysis: Lack of Authority-Vote Deduplication in BEEFY Consensus Verifier

I found a direct structural analog to the shardus-core "no voter deduplication" bug in the BEEFY consensus verifier — both the Rust light-client verifier and the on-chain Solidity `EcdsaBeefy` verifier use the *raw, unfiltered length* of the attacker-supplied signature list to satisfy the 2/3+1 supermajority quorum check, before any check that the `authorityIndex` values are unique. This is in stark contrast to every other consensus verifier in this repo (Pharos `verify_validator_membership`, Tendermint `ensure_unique_addresses`, GRANDPA `num_duplicated_precommits`/`num_equivocations`, BSC/sync-committee bitset-based schemes), which all explicitly reject duplicate participants before counting toward quorum. BEEFY has no such guard.

### Root cause

In `verify_mmr_update_proof` [1](#0-0) , the supermajority gate is evaluated purely on `mmr.signed_commitment.signatures.len()` — the count of attacker-submitted `(index, signature)` tuples — with no deduplication of `sig.index`: [2](#0-1) 

Only *after* this quorum check passes does the code recover addresses and build `authority_indices`/`authority_leaves` from every signature entry, again without rejecting repeated indices [3](#0-2) , and hand them to `rs_merkle`'s multi-proof `verify`. Multi-proof merkle verifiers of this kind reconstruct the root from an index→hash mapping; supplying the same `(index, leaf)` pair multiple times is idempotent and does not cause a mismatch, since the reconstructed layer is built from unique index positions. There is no error variant such as `DuplicateAuthority` anywhere in the BEEFY error enum [4](#0-3) , confirming this check is entirely absent.

The identical pattern exists in the Solidity verifier used on EVM state machines: [5](#0-4) 

`sigLen` (raw `votes.length`) gates `checkParticipationThreshold` before any recovery or index-uniqueness check, and `MerkleMultiProof.VerifyProof` is fed the (possibly duplicated) authority indices/leaves directly.

### Why this is the same bug class

Exactly as in the shardus-core report — where `sync_trie_hashes` counted votes without deduplicating voters, letting one attacker manufacture a false majority — here a party holding as few as **one** compromised BEEFY authority signing key can submit that single signature repeated `⌈(2n/3)+1⌉` times (each copy carrying the same `authorityIndex`) to satisfy `check_participation_threshold`/`checkParticipationThreshold`. If the downstream merkle multi-proof step tolerates duplicate index entries (as is standard for such algorithms, since verification is idempotent per index), the entire "supermajority-signed" gate is bypassed with a single real signer, letting the attacker push an arbitrary MMR root / parachain header set into the trusted `ConsensusState`, forging state commitments for every downstream ISMP state machine client that trusts BEEFY.

### Reachability

`verify_consensus` is invoked by `ismp-beefy`'s state-machine update path from any relayed consensus proof extrinsic — a permissionless action any relayer can submit; no privileged role is required.

### Impact

Forging the BEEFY consensus state lets the attacker fabricate finalized parachain headers/state roots that Hyperbridge trusts, enabling forged `Post`/`Get` message delivery, unsound state-membership proofs, and consequently unauthorized token mint/burn or fund release on any app relying on the corresponding EVM/Substrate state machine client — a direct path to loss of funds, matching the "unsound state commitment" / "forged message delivery" impact classes.

### What needs verification before treating this as fully confirmed

I could not directly inspect the `rs_merkle` crate's exact behavior for duplicate `(index, hash)` pairs in `MerkleProof::verify`, nor the `MerkleMultiProof.VerifyProof` Solidity library's handling of duplicate `Leaf.index` entries — these determine whether the merkle-membership step also fails safe against duplicates (which would only reduce this to a false-quorum threshold miscount, still a bug, but non-exploitable without a compliant merkle library behavior). Given the size limits on the indexed codebase, I was not able to pull those library sources; a Devin session with full repo/dependency access should confirm the exact duplicate-index handling in `rs_merkle` and `MerkleMultiProof.sol` to finalize severity, and to add an explicit `authority_indices.iter().collect::<BTreeSet>().len() == authority_indices.len()` (or Solidity equivalent) dedup check before/alongside the threshold check in both `modules/consensus/beefy/verifier/src/lib.rs` and `evm/src/consensus/EcdsaBeefy.sol`.

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

**File:** modules/consensus/beefy/verifier/src/lib.rs (L145-171)
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
```

**File:** modules/consensus/beefy/verifier/src/error.rs (L17-76)
```rust
#[derive(Error, Debug)]
pub enum Error {
	// -- verifier-level --
	/// `trusted_state.latest_beefy_height >= proof.block_number`. Surfaced before any
	/// cryptographic work, so it's cheap to recognise and re-route as an uncle.
	#[error("Stale height: trusted height {trusted_height} >= current_height {current_height}")]
	StaleHeight {
		/// Trusted state height at verification time.
		trusted_height: u32,
		/// Block number reported by the proof.
		current_height: u32,
	},
	/// Fewer than the BEEFY supermajority threshold of authorities signed the commitment.
	#[error("Super majority of signatures required")]
	SuperMajorityRequired,
	/// The commitment was signed by an authority set the verifier does not know about.
	#[error("Unkown authority set id {id}")]
	UnknownAuthoritySet {
		/// Unknown authority set id from the commitment.
		id: u64,
	},
	/// The proof carries an mmr leaf other than the one appended at the commitment's block.
	/// An MMR is append-only, so historical leaves also prove against the commitment's root;
	/// accepting one would let a proof advance the height while replaying an old
	/// `beefy_next_authority_set` and suppressing the authority set rotation.
	#[error("Stale mmr leaf: leaf parent number {parent_number} is not {block_number} - 1")]
	StaleMmrLeaf {
		/// Parent block number carried by the proof's mmr leaf.
		parent_number: u32,
		/// Block number reported by the commitment.
		block_number: u32,
	},
	/// The signed commitment payload is missing its MMR root hash entry.
	#[error("MMR root hash is missing from commitment payload")]
	MmrRootHashMissing,
	/// The MMR root hash entry is the wrong length (expected 32 bytes).
	#[error("Invalid MMR root hash length: expected 32, found {len}")]
	InvalidMmrRootHashLength {
		/// Actual length found.
		len: usize,
	},
	/// `secp256k1` ecrecover did not return a public key for one of the signatures.
	#[error("Failed to recover public key from signature")]
	FailedToRecoverPublicKey,
	/// The merkle multi-proof of the signing authorities does not verify.
	#[error("Invalid authorities proof")]
	InvalidAuthoritiesProof,
	/// MMR-leaf-vs-root verification raised an internal error.
	#[error("MMR verification failed during calculation: {0}")]
	MmrVerificationFailed(String),
	/// MMR-leaf-vs-root verification ran but the calculated root differs from the proven root.
	#[error("Invalid MMR proof: calculated root does not match provided root")]
	InvalidMmrProof,
	/// The merkle proof of parachain headers does not verify.
	#[error("Invalid parachain header proof: merkle proof verification failed")]
	InvalidParachainProof,
	/// The SP1 Groth16 verifier rejected the proof bytes.
	#[error("SP1 proof verification failed")]
	Sp1VerificationFailed,

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
