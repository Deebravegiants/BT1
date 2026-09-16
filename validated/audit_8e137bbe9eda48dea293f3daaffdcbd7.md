### Title
BEEFY consensus finality can be forged by padding participation with duplicate authority-index votes - ([File: modules/consensus/beefy/verifier/src/lib.rs])

### Summary
The BEEFY consensus verifier (both the Rust `verify_mmr_update_proof` and its Solidity counterpart `EcdsaBeefy.verifyMmrUpdateProof`) determines whether a commitment has supermajority (2/3+1) authority participation by counting the raw *length* of the submitted votes/signatures array, not the number of *distinct* authorities that actually signed. This mirrors the HatsSignerGate finding's root cause: a threshold/quorum check performed on a count of items rather than on verified, de-duplicated identities, which the external report explicitly calls out as a related weakness ("HSG does not check signatures for uniqueness so ... he could just add the same signature multiple times").

### Finding Description
In `verify_mmr_update_proof`, `signatures_length` is simply `mmr.signed_commitment.signatures.len()`, and the supermajority gate is: [1](#0-0) 

Each entry in `signatures` carries its own `authority_index`; nowhere in this function (or in `check_participation_threshold`) is there a check that the `authority_index` values are unique: [2](#0-1) [3](#0-2) 

A malicious relayer (or a small colluding minority of BEEFY authorities, well under 2/3+1) can take one or a few genuinely valid signatures for the target commitment and repeat the same `(authority_index, signature)` pair multiple times in the `signatures` vector. This inflates `signatures_length` past the `check_participation_threshold` bar without any additional distinct authority actually having signed. The subsequent merkle multi-proof step (`merkle_proof.verify(...)`) only confirms that each submitted `(index, leaf_hash)` pair is a valid member of the authority set commitment — it does not, and structurally cannot on its own, detect that the *same* index/leaf was supplied more than once, since each individual membership check is independently valid.

The exact same structural gap exists in the Solidity `EcdsaBeefy.verifyMmrUpdateProof`, which likewise sizes its participation check off `votes.length` before recovering signer addresses and checking merkle membership: [4](#0-3) [5](#0-4) 

This is the same bug class as the H-3 report: a threshold check is satisfied by counting entries in an attacker-controlled array instead of verifying that the required number of *distinct authorized signers* participated, allowing an unauthorized minority to be treated as if it met a supermajority requirement.

### Impact Explanation
If exploitable, this would let far fewer than 2/3+1 of the BEEFY authority set forge acceptance of an arbitrary MMR root / commitment, which is used to accept new parachain header state commitments into Hyperbridge's trusted consensus state (`EcdsaBeefy.verify` / `verify_consensus` feed directly into `HandlerV2.handleConsensus` which calls `host.storeStateMachineCommitment`). This is the核心 root of trust for cross-chain messages; a forged commitment would let an attacker forge arbitrary state commitments and thus forge message delivery (fake proofs of dispatched requests, fake token mints, etc.) — a Critical-class "forged message delivery / unsound state commitment" impact per the validation criteria.

### Likelihood Explanation
Uncertain / not conclusively proven. I could not obtain the source of the external `MerkleProof`/`MerkleMultiProof` verification libraries used here (`rs_merkle` for the Rust verifier, `@polytope-labs/solidity-merkle-trees` for the Solidity verifier) to confirm whether their multi-proof verification algorithms implicitly reject duplicate indices/leaves (e.g., by requiring a strictly sorted, deduplicated index list, or by the k-index combination logic naturally failing on a repeated position). Many binary/sparse merkle multi-proof implementations do require unique, sorted leaf indices to correctly recombine the proof layers, in which case a duplicate index would cause the multi-proof verification itself to fail or produce a wrong root — this would neutralize the issue. Because this dependency's behavior is outside this repository's indexed content, I cannot confirm the exploit is actually reachable end-to-end; the `signatures_length`/`votes.length` counting logic itself is verifiably decoupled from uniqueness, but whether the downstream merkle library silently tolerates duplicate indices is unverified.

### Recommendation
Regardless of the merkle library's exact behavior, defense-in-depth suggests: before/while building `authority_indices`/`authorities` in `verify_mmr_update_proof` (Rust) and `verifyMmrUpdateProof` (Solidity), explicitly reject duplicate `authority_index` values (e.g., require indices to be strictly increasing, or use a bitset/seen-set) prior to computing `signatures_length`/`sigLen` and running the participation-threshold check. This ensures the 2/3+1 threshold is computed over distinct authorities, matching the guarantee the merkle-membership proof is intended to provide, and removes reliance on undocumented behavior of the third-party merkle-proof library.

### Proof of Concept
Conceptual (not executed, since library internals could not be confirmed):
1. Obtain one valid BEEFY vote `(authority_index = i, signature = sig_i)` for a target (possibly malicious) `commitment`.
2. Construct `signed_commitment.signatures = [vote_i, vote_i, vote_i, ..., vote_i]` (or a small colluding set of valid votes) repeated enough times that `signatures.len() >= (2*total)/3 + 1`.
3. Submit as `MmrProof` to `verify_mmr_update_proof`. `check_participation_threshold(signatures_length, authority_set.len)` passes based on array length alone.
4. For each repeated entry, `secp256k1_recover` returns the same valid `authority_address_hash` at the same `index`, and `merkle_proof.verify` is called with duplicate `(index, leaf)` pairs — if the underlying merkle library does not reject duplicate indices, verification succeeds despite only 1 (or a minority) of authorities actually having signed. [6](#0-5)

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

**File:** modules/consensus/beefy/verifier/src/lib.rs (L146-171)
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

	let merkle_proof = MerkleProof::<MerkleHasher<H>>::new(mmr.authority_proof.clone());

	let valid = merkle_proof.verify(
		authority_set.keyset_commitment.into(),
		&authority_indices,
		&authority_leaves,
		authority_set.len as usize,
	);
```

**File:** modules/consensus/beefy/verifier/src/lib.rs (L258-262)
```rust
/// Checks for supermajority participation
fn check_participation_threshold(len: u32, total: u32) -> bool {
	len >= ((2 * total) / 3) + 1
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

**File:** evm/src/consensus/EcdsaBeefy.sol (L240-243)
```text
    // @dev Check for supermajority participation.
    function checkParticipationThreshold(uint256 len, uint256 total) internal pure returns (bool) {
        return len >= ((2 * total) / 3) + 1;
    }
```
