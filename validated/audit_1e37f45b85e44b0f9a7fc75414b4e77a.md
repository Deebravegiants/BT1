# #Vulnerability found for this question

### Title
Unbounded BEEFY authority-set size can render `EcdsaBeefy` consensus verification impossible within the block gas limit, permanently freezing the light client - (File: `evm/src/consensus/EcdsaBeefy.sol`)

### Summary
`EcdsaBeefy.verifyMmrUpdateProof` requires a supermajority (`>2/3+1`) of individual `ecrecover` calls to accept a new BEEFY commitment, and rotates `nextAuthoritySet`/`currentAuthoritySet` forward with no upper bound on `AuthoritySetCommitment.len`. If the Polkadot relay chain's authority set size grows large enough (through ordinary, non-malicious validator-set growth — no admin/governance abuse required), the number of on-chain `ECDSA.recover` calls needed to clear the threshold can exceed what fits in a single block's gas limit. At that point no relayer can ever submit a valid consensus proof again, permanently freezing the BEEFY consensus client and every message route that depends on it.

### Finding Description
`EcdsaBeefy.verifyMmrUpdateProof` selects the authority set named by the commitment's `validatorSetId` and checks participation via `checkParticipationThreshold(sigLen, authoritySet.len)`: [1](#0-0) 

The threshold function itself: [2](#0-1) 

Each of the `sigLen` votes triggers an `ECDSA.recover` plus a merkle-multiproof leaf hash, and the function then also runs `MerkleMultiProof.VerifyProof` over the same size (`authoritySet.len`): [3](#0-2) 

Crucially, `authoritySet.len` is rotated forward from whatever the relay chain reports in the MMR leaf, with no cap: [4](#0-3) 

The equivalent Rust verifier (`modules/consensus/beefy/verifier/src/lib.rs`) has the identical unbounded rotation and per-signature `secp256k1_recover` loop: [5](#0-4) [6](#0-5) [7](#0-6) 

Neither implementation enforces a maximum on `AuthoritySetCommitment.len`/`authority_set.len`. This is the same class of bug as the Gravity `updateValset` finding: nothing stops the trusted validator-set size from growing to a point where meeting the required signature threshold becomes computationally/gas infeasible to verify on-chain.

By contrast, Hyperbridge's own Pharos consensus verifier explicitly guards against this exact bug class with a `TooManyValidators` check (`Error::TooManyValidators { count, max }`), confirming the team recognizes an unbounded validator-set size as a real threat to on-chain verifiability: [8](#0-7) 

BSC's validator set is fixed-size (21, checked against `VALIDATOR_BIT_SET_SIZE`) and Ethereum's sync committee is a fixed 512-member set, so neither is exposed to this growth problem — only the BEEFY/Polkadot authority set, whose size is dictated entirely by the (potentially very large, and legitimately growing) relay-chain validator set, lacks this protection.

### Impact Explanation
`HandlerV2.handleConsensus` is the sole permissionless entry point that advances the BEEFY consensus state via `IConsensusV2(host.consensusClient()).verify(...)`: [9](#0-8) 

If the required number of `ecrecover` + merkle-leaf-hash operations to satisfy `checkParticipationThreshold` ever exceeds what a single transaction can execute within the destination chain's block gas limit, `verify()` will always revert (or run out of gas) for every subsequent BEEFY commitment carrying that authority set. Since `latestHeight` and the authority-set commitments can never advance past that point, all Polkadot/parachain state commitments, POST/GET request delivery, and timeouts routed through this consensus client become permanently undeliverable — a full, unrecoverable freeze of every message route relying on this BEEFY light client, matching the "route unable to deliver messages" / permanent freezing criteria.

### Likelihood Explanation
This does not require any malicious actor: it is triggered purely by the natural size of the trusted relay-chain authority set exceeding a gas-feasible threshold, exactly as described in the original Gravity Bridge report (their worked example puts the failure point around 10,000 validators for `ecrecover`, and `EcdsaBeefy`'s cost per signature is higher since it also does merkle-multiproof leaf preparation). Polkadot's validator counts are already in the hundreds and trending upward over protocol lifetime, and nothing in the client prevents this state from being reached — it only manifests once the relay chain's authority set grows past the destination chain's practical verification limit, at which point the client is permanently bricked without any attacker needing to act.

### Recommendation
Enforce an explicit maximum on `AuthoritySetCommitment.len` (both in `EcdsaBeefy.sol`'s `verifyMmrUpdateProof`/rotation logic and in the Rust `verify_mmr_update_proof`), rejecting any `nextAuthoritySet` rotation whose length exceeds a value proven to remain verifiable within the target chain's block gas limit — mirroring the `TooManyValidators` guard Hyperbridge already applies in the Pharos verifier. Alternatively/additionally, steer such large authority sets exclusively through the `SP1Beefy` (zk) verifier path, which amortizes signature verification cost independent of validator-set size, and disallow `EcdsaBeefy` from accepting authority sets above the safe ECDSA-verification bound.

### Proof of Concept
1. Track the BEEFY relay chain's authority set size over successive epochs; each legitimate epoch rotation can grow `nextAuthoritySet.len` without any check in `verifyMmrUpdateProof`/`verify_mmr_update_proof`.
2. Once `authoritySet.len` grows large enough that `(2*len)/3 + 1` individual `ECDSA.recover` + merkle-leaf-hash operations (plus the `MerkleMultiProof.VerifyProof` over `len` leaves) can no longer complete within the destination chain's block gas limit, submit (or attempt to submit) any subsequent `handleConsensus` proof for that authority set.
3. The transaction reverts/runs out of gas for every possible relayer, for every future BEEFY commitment tied to that authority set — `consensusState.latestHeight` can never advance, permanently freezing all state commitments and message delivery for every state machine anchored to this BEEFY consensus client.

### Citations

**File:** evm/src/consensus/EcdsaBeefy.sol (L126-162)
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

**File:** evm/src/consensus/EcdsaBeefy.sol (L164-169)
```text
        verifyMmrLeaf(trustedState, relayProof, mmrRoot);
        if (relayProof.latestMmrLeaf.nextAuthoritySet.id > trustedState.nextAuthoritySet.id) {
            trustedState.currentAuthoritySet = trustedState.nextAuthoritySet;
            trustedState.nextAuthoritySet = relayProof.latestMmrLeaf.nextAuthoritySet;
        }
        trustedState.latestHeight = latestHeight;
```

**File:** evm/src/consensus/EcdsaBeefy.sol (L240-243)
```text
    // @dev Check for supermajority participation.
    function checkParticipationThreshold(uint256 len, uint256 total) internal pure returns (bool) {
        return len >= ((2 * total) / 3) + 1;
    }
```

**File:** modules/consensus/beefy/verifier/src/lib.rs (L119-133)
```rust
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

**File:** modules/consensus/beefy/verifier/src/lib.rs (L179-182)
```rust
	if mmr.latest_mmr_leaf.beefy_next_authority_set.id > trusted_state.next_authorities.id {
		trusted_state.current_authorities = trusted_state.next_authorities.clone();
		trusted_state.next_authorities = mmr.latest_mmr_leaf.beefy_next_authority_set.clone();
	}
```

**File:** modules/consensus/pharos/verifier/src/error.rs (L174-176)
```rust
	/// Claimed validator count exceeds what the protocol allows
	#[error("Too many validators: {count} exceeds maximum {max}")]
	TooManyValidators { count: usize, max: usize },
```

**File:** evm/src/core/HandlerV2.sol (L144-153)
```text
    function handleConsensus(IHost host, bytes calldata proof) external notFrozen(host) {
        uint256 delay = block.timestamp - host.consensusUpdateTime();
        if (delay >= host.unStakingPeriod()) revert ConsensusClientExpired();

        bytes memory previousState = host.consensusState();
        (bytes memory verifiedState, IntermediateState[] memory intermediates, uint256 nextAuthoritySetId) =
            IConsensusV2(host.consensusClient()).verify(previousState, proof);

        if (keccak256(previousState) == keccak256(verifiedState)) return;
        host.storeConsensusState(verifiedState);
```
