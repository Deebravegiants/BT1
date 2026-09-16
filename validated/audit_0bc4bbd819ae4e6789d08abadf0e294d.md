I have enough evidence to confirm the vulnerability. Both the Rust BEEFY verifier (`modules/consensus/beefy/verifier/src/lib.rs`) and the Solidity `EcdsaBeefy.sol` build their supermajority participation count directly from the raw length of the submitted signature/vote list, and separately verify authority-set membership via a merkle multi-proof keyed on `sig.index`/`vote.authorityIndex` — but neither path checks that the submitted indices are distinct. A relayer submitting a BEEFY consensus proof can duplicate the same authority's `(index, signature)` pair repeatedly to inflate the counted participation past the 2/3+1 threshold while only holding a minority of real signatures.

### Title
Duplicate authority signatures inflate BEEFY supermajority threshold, allowing forged consensus finality with less than 2/3+1 real signers - (File: modules/consensus/beefy/verifier/src/lib.rs, evm/src/consensus/EcdsaBeefy.sol)

### Summary
The BEEFY consensus verifiers (both the Rust `pallet`/off-chain verifier used by `ismp-beefy` and the on-chain `EcdsaBeefy.sol` contract) compute the supermajority-participation check from the raw count of submitted signatures/votes, and separately verify each submitted `(authorityIndex, recoveredAddress)` pair against the authority-set merkle root. Neither function rejects a submission that repeats the same `authorityIndex` (and the corresponding signature) multiple times. This lets an attacker who controls (or has intercepted) valid signatures from fewer than `2/3 * len + 1` authorities pad the signature/vote list with duplicates of an already-valid `(index, signature)` entry to pass `check_participation_threshold`/`checkParticipationThreshold`, even though the number of *distinct* signing authorities is below the required supermajority.

### Finding Description
In `verify_mmr_update_proof` [1](#0-0) , `signatures_length` is simply `mmr.signed_commitment.signatures.len()` and is checked against the threshold with `check_participation_threshold` [2](#0-1) . The loop that follows builds `authority_leaves`/`authority_indices` from each entry in `mmr.signed_commitment.signatures` without deduplicating `sig.index` [3](#0-2) , and the resulting arrays are passed straight into `merkle_proof.verify` [4](#0-3) . A duplicated `(index, leaf)` pair is still a valid statement about the tree (the same leaf really is at that index), so the merkle multi-proof verification succeeds even when the same authority index/leaf appears more than once in the list — it does not enforce that indices are unique.

The identical pattern exists in the Solidity verifier: `sigLen = relayProof.signedCommitment.votes.length` is checked with `checkParticipationThreshold` [5](#0-4) , then each `vote.authorityIndex`/recovered address is pushed into the `authorities` leaf array with no uniqueness check before `MerkleMultiProof.VerifyProof` [6](#0-5) .

By contrast, other consensus verifiers in this same codebase explicitly guard against this exact class of bug: the Tendermint verifier's `ensure_unique_addresses` rejects a validator set with a repeated address [7](#0-6) , and the Pharos verifier's `verify_validator_membership` explicitly rejects duplicate participant keys with `Error::DuplicateParticipant` [8](#0-7) . The BEEFY verifiers (both Rust and Solidity) are missing this equivalent check.

Since BEEFY consensus updates gate `EvmHost`/`ismp-beefy` state-commitment intake (which in turn permits `HandlerV2`/pallet-ismp message delivery from the relay chain and its parachains into Hyperbridge), an attacker who can obtain signatures from fewer than a supermajority of the current or next authority set (e.g., through a validator-set churn window, a leaked subset of keys, or any partial-signature collection scenario) can forge a consensus update that the verifier accepts as if it met the 2/3+1 threshold, by duplicating those signatures under their true index.

### Impact Explanation
This breaks the fundamental soundness guarantee of the BEEFY light client: state commitments (and therefore ISMP message delivery, request/response proofs, and any downstream mint/settlement logic that trusts these state commitments) can be advanced or forged using fewer real signatures than the protocol's stated 2/3+1 supermajority. This is a consensus-soundness break enabling forged message delivery / unsound state commitment, which can lead to unauthorized state transitions being accepted by Hyperbridge and any relaying app built on top of it (token bridges, intents, etc.) that rely on the correctness of BEEFY-verified state commitments.

### Likelihood Explanation
Exploitation requires the attacker to already hold valid signatures from some subset of authorities under the current/next validator set id that is below supermajority (e.g., collected off-chain, exposed during set rotation, or via a compromised minority of validators) — it does not require any additional cryptographic breaking. Given such signatures, forging the padded proof is a trivial, purely off-chain data-construction step; there is no on-chain protection against it today in either the Rust or Solidity verifier.

### Recommendation
In both `verify_mmr_update_proof` (Rust) and `verifyMmrUpdateProof` (Solidity), deduplicate signatures/votes by `authorityIndex` before computing `signatures_length`/`sigLen` (e.g., using a `BTreeSet`/similar uniqueness check as done in `ensure_unique_addresses` and `verify_validator_membership` elsewhere in the codebase), and reject the proof if a duplicate index is found. The participation threshold must be computed only over the count of distinct authority indices with a valid signature.

### Proof of Concept
1. Suppose the current authority set has `len = 30` authorities, so the supermajority threshold is `(2*30)/3 + 1 = 21`.
2. An attacker collects only `k = 11` genuine, valid `(index, signature)` pairs (well under the 21 threshold) for a commitment they want finalized (e.g. via partial key exposure at set-rotation, or by colluding with a minority of authorities).
3. The attacker constructs `mmr.signed_commitment.signatures` (or `relayProof.signedCommitment.votes` for the Solidity path) by repeating each of the 11 genuine `(index, signature)` entries so the list length is 21 (e.g., duplicate entry 0 ten times).
4. `signatures_length`/`sigLen` is now `21`, satisfying `check_participation_threshold`/`checkParticipationThreshold`.
5. Each duplicated `(index, leaf)` pair is a true statement about the authority-set merkle tree (the same leaf really is at that index), so `merkle_proof.verify`/`MerkleMultiProof.VerifyProof` succeeds.
6. The proof is accepted as a valid BEEFY consensus update, advancing the trusted state/MMR root despite only 11 of 30 authorities (well below supermajority) having actually signed.

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

**File:** modules/consensus/beefy/verifier/src/lib.rs (L145-162)
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
```

**File:** modules/consensus/beefy/verifier/src/lib.rs (L164-175)
```rust
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
