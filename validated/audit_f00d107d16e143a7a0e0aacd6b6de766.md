### Title
`EcdsaBeefy.verifyMmrLeaf` accepts a stale MMR leaf, allowing authority-set rotation to be suppressed while the trusted height still advances - (File: evm/src/consensus/EcdsaBeefy.sol)

### Summary
`EcdsaBeefy.sol`'s leaf-verification path never checks that the submitted MMR leaf is the one appended at the signed commitment's block (`parentNumber + 1 == blockNumber`). Because an MMR is append-only, an older leaf still produces a valid Merkle inclusion proof against the newer, signed MMR root. This is the same bug class as the Netty advisory: a freshness/staleness check that other, structurally identical code paths in this very codebase treat as mandatory is silently skipped, letting stale data be accepted as authoritative.

### Finding Description
`EcdsaBeefy.verifyMmrUpdateProof` verifies supermajority ECDSA signatures over a `Commitment` (which carries the current `blockNumber` and the new MMR root), then calls `verifyMmrLeaf` to check that `relay.latestMmrLeaf` is included in that MMR root: [1](#0-0) 

`verifyMmrLeaf` only verifies Merkle inclusion of the leaf at `leafIndex(activationBlock, relay.latestMmrLeaf.parentNumber)` against `mmrRoot` — it never checks that `relay.latestMmrLeaf.parentNumber + 1 == commitment.blockNumber`. Any leaf that was ever appended to the MMR (i.e., any historical leaf, since the MMR only grows) satisfies a valid inclusion proof against the current, newer root. After this call returns, `verifyMmrUpdateProof` unconditionally advances `trustedState.latestHeight = latestHeight` (the new, signed block number) and only rotates authorities if `relay.latestMmrLeaf.nextAuthoritySet.id > trustedState.nextAuthoritySet.id`: [2](#0-1) 

The sibling implementations in this same codebase treat this exact check as security-critical and enforce it explicitly:

- `SP1Beefy.verifyConsensus` (Solidity): `if (uint256(proof.mmrLeaf.parentNumber) + 1 != commitment.blockNumber) revert StaleMmrLeaf();` [3](#0-2) 

- The Rust `verify_sp1_consensus` verifier, with an explicit rationale comment: "An mmr is append-only, so a historical leaf also proves against the commitment's root. Accepting one would advance `latest_beefy_height` while replaying an old leaf, suppressing the rotation... and stranding the client on a set the relay chain has retired." [4](#0-3) 

- The equivalent Rust ECDSA-path verifier (`verify_mmr_update_proof`) that `EcdsaBeefy.sol` mirrors also enforces leaf freshness via `verify_mmr_leaf`, and the shared `Error::StaleMmrLeaf` variant documents the identical concern: [5](#0-4) [6](#0-5) 

`EcdsaBeefy.sol` is the outlier: it verifies inclusion but never pins the leaf to the commitment's block, exactly analogous to Netty's `OcspServerCertificateValidator` computing a freshness comparison but never enforcing it — the check that "should" gate acceptance is present in sibling code paths but missing here.

### Impact Explanation
`EcdsaBeefy` is Hyperbridge's on-chain EVM BEEFY consensus client — it is invoked permissionlessly via `HandlerV2.handleConsensus`, reachable by any relayer submitting a consensus proof: [7](#0-6) 

A relayer (or any attacker who can obtain historical, validly-signed BEEFY commitments — which are public, since they're broadcast by the relay chain and are not secrets) can:
1. Obtain a valid, supermajority-signed `Commitment` for a recent block `N` and its MMR root `R_N`.
2. Pair it with an **older** `latestMmrLeaf` (from block `M < N-1`) plus a valid inclusion proof of that old leaf against `R_N` (which exists because the MMR is append-only and never removes leaves).
3. Submit this to `EcdsaBeefy.verify` via `HandlerV2.handleConsensus`.

The `verifyMmrLeaf` inclusion check passes (the leaf genuinely is in `R_N`), so `trustedState.latestHeight` advances all the way to `N`, but the authority-set-rotation decision is driven by the stale leaf's `nextAuthoritySet.id`, which lags behind the true current epoch. This can suppress a legitimate authority-set rotation: the trusted state's height moves forward while it stays pinned to an authority set that the relay chain has since retired. Once stranded, if a rotation occurred between `M` and `N` and no later proof re-triggers the rotation before enough legitimate proofs are replaced with newer-but-still-stale-leaf ones, the client accepts commitments purportedly signed by an authority set that Hyperbridge (and its light clients) will keep trusting past its legitimate lifetime — an unsound consensus/state commitment vulnerability that undermines the integrity of every state-machine update and message delivery that depends on this consensus client (`HandlerV2.handlePostRequests`, `handleGetResponses`, timeout handlers, etc., all gate on `host.stateMachineCommitment`/`host.consensusState` populated by this path). This is a forged/unsound state-commitment and consensus-integrity issue with High severity, matching the CWE-299 (improper check of certificate/data expiration/freshness) class of the reference advisory.

### Likelihood Explanation
The precondition (a valid signed commitment for a later height, paired with an older but still MMR-included leaf) requires no privileged access — BEEFY commitments and MMR proofs are public consensus artifacts on the relay chain, and any relayer can freely mix a fresh signed commitment with a stale but structurally-valid leaf proof. `handleConsensus`/`EcdsaBeefy.verify` are permissionless entry points reachable from a single submitted transaction. The bug requires no compromised keys, no governance, no node-level access — only assembling a proof from public data, exactly the "message dispatcher/relayer" reachable path this scan is scoped to.

### Recommendation
Add the same leaf-freshness check present in `SP1Beefy.sol` and the Rust verifiers to `EcdsaBeefy.verifyMmrLeaf` (or `verifyMmrUpdateProof`): require `relay.latestMmrLeaf.parentNumber + 1 == commitment.blockNumber`, reverting with a `StaleMmrLeaf` error otherwise, before the leaf's `nextAuthoritySet` is trusted for rotation decisions.

### Proof of Concept
Conceptual PoC (mirrors the structure of `SP1BeefyTest.sol`/`ecdsa_beefy.rs` already in the repo):
1. Initialize `EcdsaBeefy` trusted state at height `H0` with authority set `A0`, next set `A1`.
2. Obtain (or construct in test fixtures, as the existing `evm/tests/rust/src/tests/ecdsa_beefy.rs` harness does) a valid signed `Commitment` for block `H2 > H0+1` signed by `A1` (supermajority), whose MMR root `R2` already contains the rotation leaf for `A2` at block `H1 = H0+1`.
3. Instead of submitting the fresh leaf at `H1` (which would correctly rotate to `A2`), submit `relay.latestMmrLeaf` = the leaf from an even earlier block `H0` (still `< H1`, still valid under `A0`/`A1`), together with a valid MMR inclusion proof of that `H0` leaf against `R2`.
4. Call `EcdsaBeefy.verify(previousState, proof)` (or via `HandlerV2.handleConsensus`) — observe that verification succeeds, `latestHeight` is set to `H2`, but `nextAuthoritySet` is not rotated to `A2` because the stale leaf's `nextAuthoritySet.id` does not exceed the currently trusted `nextAuthoritySet.id`. Compare against `evm/tests/rust/src/tests/ecdsa_beefy.rs` and the analogous stale-leaf rejection test `rejects_sp1_proof_carrying_a_stale_mmr_leaf` in `modules/consensus/beefy/verifier/src/test.rs`, which demonstrates the equivalent attack is explicitly blocked in the SP1/Rust paths but has no counterpart guarding `EcdsaBeefy.sol`. [8](#0-7)

### Citations

**File:** evm/src/consensus/EcdsaBeefy.sol (L122-172)
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

        verifyMmrLeaf(trustedState, relayProof, mmrRoot);
        if (relayProof.latestMmrLeaf.nextAuthoritySet.id > trustedState.nextAuthoritySet.id) {
            trustedState.currentAuthoritySet = trustedState.nextAuthoritySet;
            trustedState.nextAuthoritySet = relayProof.latestMmrLeaf.nextAuthoritySet;
        }
        trustedState.latestHeight = latestHeight;

        return (trustedState, relayProof.latestMmrLeaf.extra);
    }
```

**File:** evm/src/consensus/EcdsaBeefy.sol (L174-196)
```text
    // @dev Stack too deep, sigh solidity
    function verifyMmrLeaf(BeefyConsensusState memory trustedState, RelayChainProof memory relay, bytes32 mmrRoot)
        internal
        pure
    {
        bytes32 hash = keccak256(
            Codec.Encode(
                PartialBeefyMmrLeaf({
                    version: relay.latestMmrLeaf.version,
                    parentNumber: relay.latestMmrLeaf.parentNumber,
                    parentHash: relay.latestMmrLeaf.parentHash,
                    nextAuthoritySet: relay.latestMmrLeaf.nextAuthoritySet,
                    extra: relay.latestMmrLeaf.extra
                })
            )
        );
        uint256 leafCount = leafIndex(trustedState.beefyActivationBlock, relay.latestMmrLeaf.parentNumber) + 1;
        MerkleMountainRange.Leaf[] memory leaves = new MerkleMountainRange.Leaf[](1);
        leaves[0] = MerkleMountainRange.Leaf({index: relay.latestMmrLeaf.leafIndex, hash: hash});
        bool valid = MerkleMountainRange.VerifyProof(mmrRoot, relay.mmrProof, leaves, leafCount);

        if (!valid) revert InvalidMmrProof();
    }
```

**File:** evm/src/consensus/SP1Beefy.sol (L119-126)
```text
        MiniCommitment memory commitment = proof.commitment;
        // Stale proofs are a no-op
        if (trustedState.latestHeight >= commitment.blockNumber) {
            return (trustedState, new IntermediateState[](0));
        }

        if (uint256(proof.mmrLeaf.parentNumber) + 1 != commitment.blockNumber) revert StaleMmrLeaf();

```

**File:** modules/consensus/beefy/verifier/src/sp1.rs (L46-74)
```rust
/// Verify an SP1 BEEFY consensus proof and return the updated consensus state
/// and verified parachain headers. Mirrors the Solidity `SP1Beefy.verifyConsensus` flow:
/// SP1 proves authority-set membership, commitment signatures, MMR leaf inclusion and
/// parachain header inclusion — so no additional merkle verification is done here.
///
/// SP1 proves only that the leaf is *in* the mmr, not that it is the *latest* leaf, so leaf
/// freshness (`parent_number + 1 == block_number`) is enforced here. Keep this in step with
/// the equivalent check in `SP1Beefy.verifyConsensus`.
pub fn verify_sp1_consensus<H: Keccak256 + Send + Sync>(
	trusted_state: ConsensusState,
	proof: Sp1BeefyProof,
	vkey: &str,
) -> Result<(Vec<u8>, Vec<ParachainHeader>), Error> {
	if trusted_state.latest_beefy_height >= proof.block_number {
		Err(Error::StaleHeight {
			trusted_height: trusted_state.latest_beefy_height,
			current_height: proof.block_number,
		})?;
	}

	// An mmr is append-only, so a historical leaf also proves against the commitment's root.
	// Accepting one would advance `latest_beefy_height` while replaying an old leaf, suppressing
	// the rotation below and stranding the client on a set the relay chain has retired.
	// `parent_number` is part of the leaf preimage hashed into `leaf_hash`, so pinning it here
	// pins the leaf itself.
	let parent_number = proof.mmr_leaf.parent_number_and_hash.0;
	if parent_number.saturating_add(1) != proof.block_number {
		Err(Error::StaleMmrLeaf { parent_number, block_number: proof.block_number })?;
	}
```

**File:** modules/consensus/beefy/verifier/src/error.rs (L38-48)
```rust
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
```

**File:** modules/consensus/beefy/verifier/src/lib.rs (L164-187)
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

	verify_mmr_leaf::<H>(&mmr, mmr_root)?;

	if mmr.latest_mmr_leaf.beefy_next_authority_set.id > trusted_state.next_authorities.id {
		trusted_state.current_authorities = trusted_state.next_authorities.clone();
		trusted_state.next_authorities = mmr.latest_mmr_leaf.beefy_next_authority_set.clone();
	}

	trusted_state.latest_beefy_height = latest_height;

	Ok((trusted_state, mmr.latest_mmr_leaf.leaf_extra))
}
```

**File:** evm/src/core/HandlerV2.sol (L144-150)
```text
    function handleConsensus(IHost host, bytes calldata proof) external notFrozen(host) {
        uint256 delay = block.timestamp - host.consensusUpdateTime();
        if (delay >= host.unStakingPeriod()) revert ConsensusClientExpired();

        bytes memory previousState = host.consensusState();
        (bytes memory verifiedState, IntermediateState[] memory intermediates, uint256 nextAuthoritySetId) =
            IConsensusV2(host.consensusClient()).verify(previousState, proof);
```

**File:** modules/consensus/beefy/verifier/src/test.rs (L412-461)
```rust
#[test]
fn rejects_sp1_proof_carrying_a_stale_mmr_leaf() {
	use beefy_verifier_primitives::Sp1BeefyProof;

	const SET_ID: ValidatorSetId = 42;
	const BLOCK_NUMBER: u32 = 1_000;
	// Mainnet SP1Beefy verification key, as in the fixture test above.
	const VKEY: &str = "0x007d1720c695842ed647a1a72e981751f9b5e26fc5ca038523b23430a1292f08";

	let trusted_state = ConsensusState {
		latest_beefy_height: BLOCK_NUMBER - 1,
		beefy_activation_block: 0,
		mmr_root_hash: H256::zero(),
		current_authorities: authority_set(SET_ID, 100),
		next_authorities: authority_set(SET_ID + 1, 100),
	};

	let mut proof = Sp1BeefyProof {
		block_number: BLOCK_NUMBER,
		validator_set_id: SET_ID,
		mmr_leaf: MmrLeaf {
			version: MmrLeafVersion::new(0, 0),
			parent_number_and_hash: (BLOCK_NUMBER - 1, H256::zero()),
			beefy_next_authority_set: BeefyNextAuthoritySet {
				id: SET_ID + 1,
				len: 100,
				keyset_commitment: H256::zero(),
			},
			leaf_extra: H256::zero(),
		},
		headers: vec![],
		proof: vec![],
		nonce: H256::zero(),
	};

	// The leaf appended at `BLOCK_NUMBER` clears the freshness check and is only rejected
	// later, by the Groth16 verifier — so the check discriminates on leaf freshness alone.
	let fresh = sp_io::TestExternalities::default().execute_with(|| {
		crate::sp1::verify_sp1_consensus::<TestHost>(trusted_state.clone(), proof.clone(), VKEY)
	});
	assert!(matches!(fresh, Err(Error::Sp1VerificationFailed)), "got {fresh:?}");

	// Swap in a leaf from an earlier block, as an attacker replaying a historical leaf would.
	proof.mmr_leaf.parent_number_and_hash.0 = BLOCK_NUMBER - 500;
	let stale = sp_io::TestExternalities::default().execute_with(|| {
		crate::sp1::verify_sp1_consensus::<TestHost>(trusted_state, proof, VKEY)
	});
	assert!(matches!(stale, Err(Error::StaleMmrLeaf { .. })), "got {stale:?}");
}

```
