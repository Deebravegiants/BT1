### Title
BEEFY ECDSA consensus client accepts duplicate authority votes toward the supermajority threshold, allowing a minority of signers to forge a finalized consensus update - (File: evm/src/consensus/EcdsaBeefy.sol)

### Summary
`EcdsaBeefy.verifyMmrUpdateProof` counts the supermajority threshold from `relayProof.signedCommitment.votes.length` without checking that the recovered `authorityIndex`/signer values are unique. A relayer can submit the same authority's `(signature, authorityIndex)` pair repeated multiple times to inflate `sigLen` past the 2/3+1 threshold while only a minority of real authorities actually signed, exactly mirroring the reported bug class of a vote-counting mechanism that fails to track/deduplicate "who has already voted."

### Finding Description
`checkParticipationThreshold(sigLen, authoritySet.len)` at [1](#0-0)  only compares the raw count of submitted votes to the authority set size — it never verifies that each vote corresponds to a distinct authority. The subsequent loop at [2](#0-1)  recovers an address for every vote and builds a `MerkleMultiProof.Leaf[]` keyed by `vote.authorityIndex`, but nothing rejects two votes sharing the same `authorityIndex` (or the same recovered `authority` under different claimed indices) before the threshold check runs.

This is structurally the same flaw described in the external report: a mechanism designed to require N distinct approvals ("votes") checks only a raw count/threshold and never records/deduplicates who already contributed, so a single actor's repeated "vote" can be counted multiple times toward the threshold.

By contrast, the BSC verifier in this same codebase defends against exactly this pattern by using a bitset and testing for "bits set beyond validator count" and enforcing one bit per validator (see `rejects_bits_set_beyond_validator_count` test) [3](#0-2) , and the Pharos verifier explicitly checks for `DuplicateParticipant` via a `BTreeSet` dedup [4](#0-3) . The BEEFY ECDSA verifier (both the Solidity `EcdsaBeefy.sol` and its Rust counterpart in `modules/consensus/beefy/verifier/src/lib.rs`) lacks this equivalent dedup check — `verify_mmr_update_proof` similarly just pushes every signature's `authority_indices` into a list and defers entirely to `check_participation_threshold(signatures_length as u32, ...)` [5](#0-4)  and to `merkle_proof.verify(...)` [6](#0-5) .

Whether the underlying `MerkleMultiProof.VerifyProof` (imported from `@polytope-labs/solidity-merkle-trees`) or the Rust `rs_merkle`-style `MerkleProof::verify` reject duplicate leaf indices in a multiproof is a property of a third-party dependency not indexed in this repo, so I could not directly confirm from the available code whether duplicate `authorityIndex` values are rejected at the merkle-verification layer. If that library does allow duplicate indices in its multiproof verification (many "multi-proof" implementations are index-set based and can process repeated indices without additional cost/failure), the threshold check is trivially bypassable.

### Impact Explanation
`EcdsaBeefy` is a `IConsensusV2` implementation used to authenticate relay-chain/parachain state to the EVM `EvmHost`. If the supermajority check can be satisfied with a minority of real signers (by duplicating one or a few authorities' signatures), an attacker controlling even a small fraction of the BEEFY authority set could forge a consensus update, advancing `_stateCommitments` and `_latestStateMachineHeight` for a state machine with fabricated or malicious content. That directly enables forged POST/GET request delivery, unsound state commitments, and unauthorized draining of escrowed funds in downstream applications (Intent Gateway, HFT bridge, etc.) that trust the state committed via this consensus client — a Critical-severity issue if confirmed exploitable against the underlying merkle library.

### Likelihood Explanation
Reaching this path requires only submitting a single BEEFY consensus proof transaction (permissionless, callable by anyone relaying to `HandlerV2`/`EvmHost.verify`), so the attack surface is a single submitted transaction as required. The likelihood of actual exploitability hinges entirely on whether the underlying merkle multi-proof verifier accepts duplicate indices in its leaf set — this is external-library behavior I was unable to verify from the indexed codebase context.

### Recommendation
In `verifyMmrUpdateProof` (and the mirrored Rust `verify_mmr_update_proof`), explicitly reject duplicate `authorityIndex`/signer values before or during the threshold check — e.g., track seen indices in a bitmap/set (as BSC's bitset check and Pharos's `BTreeSet`-based `verify_validator_membership` already do) and revert with a `DuplicateVote`/`DuplicateParticipant`-style error if any index repeats, mirroring the exact fix pattern the external report recommends (tracking who has already "voted").

### Proof of Concept
Not independently verified against the underlying `MerkleMultiProof`/`rs_merkle` libraries (not present in the indexed codebase), so no runnable PoC could be constructed. Conceptually: construct a `RelayChainProof` where `votes` contains the same authority's valid signature repeated `⌈2N/3⌉+1` times (all with the same or valid but repeated `authorityIndex`), and submit it to `EcdsaBeefy.verify` / `verify_mmr_update_proof`; if the merkle multiproof library does not itself reject duplicate indices, `checkParticipationThreshold` passes despite only one real authority signing, and a forged consensus state is accepted.

### Citations

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

**File:** modules/consensus/bsc/verifier/src/lib.rs (L348-368)
```rust
	/// Setting a bit past `current_validators.len()` must be rejected,
	/// even when it would otherwise inflate `count_ones()` over the
	/// 2/3 threshold.
	#[test]
	fn rejects_bits_set_beyond_validator_count() {
		let validators = dummy_validators(21);
		// 10 in-range bits (below the 14-vote threshold) plus 30 bits
		// in the junk range [21, 64) — pre-fix this would clear the
		// supermajority check at 40 ones; post-fix it is rejected.
		let in_range: u64 = (1u64 << 10) - 1;
		let junk: u64 = ((1u64 << 51) - 1) << 21; // bits 21..=63 (wraps to 30 bits set)
		let header =
			header_with_vote_set(in_range | junk, B256::repeat_byte(1), B256::repeat_byte(2));

		let err = verify_bsc_header::<TestHost, Testnet>(&validators, update_with(header), 1000)
			.expect_err("junk bits must be rejected");
		assert!(
			format!("{err}").contains("Vote address set has bits set beyond validator count"),
			"unexpected error: {err:?}"
		);
	}
```

**File:** modules/consensus/pharos/verifier/src/lib.rs (L143-156)
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
