### Title
Unavoidable growth of the BEEFY authority set can make `EcdsaBeefy.verify()` exceed a host chain's per-transaction gas limit, permanently freezing consensus updates - (File: `evm/src/consensus/EcdsaBeefy.sol`)

### Summary
`EcdsaBeefy.verifyMmrUpdateProof` requires a *hard, protocol-enforced minimum* number of ECDSA signature recoveries — a 2/3+1 supermajority of the relay chain's authority set — before a BEEFY consensus proof can be accepted [1](#0-0) . The size of that authority set is decided entirely off-chain by the relay chain (Polkadot/Kusama), not by the relayer submitting the proof or by any Hyperbridge contract parameter. As the authority set grows, the number of `ECDSA.recover` calls that MUST be included in a single `handleConsensus` transaction grows with it and cannot be reduced by the caller, `checkParticipationThreshold` rejects anything below the threshold [2](#0-1) . This is directly analogous to the LooksRare finding: a fixed, externally-imposed gas ceiling (there: Chainlink VRF's 2,500,000 gas callback limit; here: each EVM host chain's block/tx gas limit) versus a loop whose iteration count is dictated by a parameter the transaction submitter cannot shrink (there: `AGENTS_TO_WOUND_PER_ROUND_IN_BASIS_POINTS`; here: the relay chain's live validator-set size).

### Finding Description
`verify()` decodes the proof and calls `verifyMmrUpdateProof`, which:
1. Reads `sigLen = relayProof.signedCommitment.votes.length`.
2. Reverts with `SuperMajorityRequired` unless `sigLen >= (2 * authoritySet.len) / 3 + 1` [3](#0-2) .
3. Loops over every one of those `sigLen` votes, calling `ECDSA.recover` and building a `MerkleMultiProof.Leaf` for each [4](#0-3) .

There is no mechanism to submit a partial signature set and accumulate it across multiple transactions — the entire supermajority must be proven atomically in a single call, exactly like `fulfillRandomWords()` had to complete its entire per-round healing logic atomically in a single VRF callback. `HandlerV2.handleConsensus` (the only entry point that reaches this verifier) is permissionless and mandatory: it is the sole path by which a host chain's light client advances, and every subsequent `handlePostRequests`/`handleGetResponses` call depends on state commitments this update produces [5](#0-4) .

Each EVM host chain enforces its own fixed transaction/block gas ceiling, independent of Hyperbridge governance, e.g. 4,000,000 for SEI and a planned reduction to 16,000,000 for Ethereum mainnet [6](#0-5) . If the relay chain's live authority set grows large enough that the mandated 2/3+1 supermajority of `ECDSA.recover` calls (plus the accompanying Merkle multi-proof array allocation, which itself has quadratic Solidity memory-expansion cost as `sigLen` grows) cannot fit within that ceiling, no relayer can ever construct a valid `handleConsensus` transaction for that authority-set epoch. Unlike the batching decisions relayers make elsewhere (e.g. `HandlerV2.batchCall`, `submit_batch_messages`), this constraint cannot be worked around by chunking, because the supermajority check is evaluated against the whole submitted vote set in one call.

### Impact Explanation
If the mandatory signature-verification workload for a BEEFY update exceeds a host chain's gas limit, that state machine's light client can never advance past its last verified height. Because every incoming POST request/GET response delivery on that chain is gated on a valid, up-to-date state commitment (`handlePostRequests`/`handleGetResponses` both check `stateMachineCommitmentUpdateTime`), this permanently freezes inbound message delivery to that chain — "a route unable to deliver messages." No funds are directly stolen, but the affected route becomes permanently unusable until a different consensus client (e.g. SP1Beefy) is deployed and migrated to, which is an emergency-governance action outside the scope of ordinary operation — mirroring the LooksRare judgment that this class of forced-revert DoS, while not a direct loss of funds, still warrants Medium severity because normal operation is broken and requires an out-of-band remediation.

### Likelihood Explanation
The likelihood tracks the trajectory of the tracked relay chain's validator count, a variable entirely outside Hyperbridge's control, exactly as the LooksRare report noted `AGENTS_TO_WOUND_PER_ROUND_IN_BASIS_POINTS` "could be changed in the future" independent of the auditors' initial assumptions. Polkadot/Kusama active validator sets have grown over time and are governed by on-chain democracy unrelated to Hyperbridge; the docs themselves flag `EcdsaBeefy` as "the most gas-expensive verifier" specifically because "verification cost increases linearly with the number of validators" [7](#0-6) , showing the team is aware the cost is proportional to an uncontrolled external parameter, but there is no on-chain guard preventing the threshold from exceeding a given host chain's gas ceiling.

### Recommendation
- Enforce a maximum authority-set size (or maximum tolerated `sigLen`) per deployed `EcdsaBeefy` instance, sized against the specific host chain's known gas limit, and prefer `SP1Beefy` (constant-cost ZK verification) for chains/relay-chain configurations where the ECDSA path could exceed the ceiling.
- Alternatively, support incremental/partial signature-set accumulation across multiple transactions so a supermajority can be assembled without requiring every vote in a single call.
- Monitor relay-chain authority-set growth against configured EVM host gas limits and gate governance decisions (e.g., authority-set inflation, validator count increases) with this constraint in mind.

### Proof of Concept
Conceptually mirrors the referenced LooksRare PoC:
1. Trusted relay-chain authority set grows to `N` validators (a value determined by relay-chain governance, not Hyperbridge).
2. A relayer collects a valid BEEFY commitment signed by the required `(2*N)/3 + 1` authorities and submits it via `HandlerV2.handleConsensus` → `EcdsaBeefy.verify` → `verifyMmrUpdateProof` [5](#0-4) .
3. The loop recovering `sigLen` ECDSA signatures and constructing `MerkleMultiProof.Leaf[]` of the same size [4](#0-3)  pushes total transaction gas above the deployed host chain's fixed gas ceiling, e.g. 4,000,000 on SEI [8](#0-7) .
4. The transaction always reverts (out-of-gas) regardless of which relayer submits it or how it's batched, because `checkParticipationThreshold` forbids submitting fewer signatures than the supermajority requires [2](#0-1) .
5. The light client for that host chain is stuck at its last verified height indefinitely, and every subsequent inbound message delivery to that chain is blocked.

### Citations

**File:** evm/src/consensus/EcdsaBeefy.sol (L137-140)
```text
        bool isCurrentAuthorities = commitment.validatorSetId == trustedState.currentAuthoritySet.id;
        AuthoritySetCommitment memory authoritySet =
            isCurrentAuthorities ? trustedState.currentAuthoritySet : trustedState.nextAuthoritySet;
        if (!checkParticipationThreshold(sigLen, authoritySet.len)) revert SuperMajorityRequired();
```

**File:** evm/src/consensus/EcdsaBeefy.sol (L152-159)
```text
        bytes32 commitmentHash = keccak256(Codec.Encode(commitment));
        MerkleMultiProof.Leaf[] memory authorities = new MerkleMultiProof.Leaf[](sigLen);
        for (uint256 i = 0; i < sigLen; i++) {
            Vote memory vote = relayProof.signedCommitment.votes[i];
            address authority = ECDSA.recover(commitmentHash, vote.signature);
            authorities[i] =
                MerkleMultiProof.Leaf({index: vote.authorityIndex, hash: keccak256(abi.encodePacked(authority))});
        }
```

**File:** evm/src/consensus/EcdsaBeefy.sol (L240-243)
```text
    // @dev Check for supermajority participation.
    function checkParticipationThreshold(uint256 len, uint256 total) internal pure returns (bool) {
        return len >= ((2 * total) / 3) + 1;
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

**File:** tesseract/messaging/evm/src/tx.rs (L190-205)
```rust
pub fn get_chain_gas_limit(state_machine: StateMachine) -> u64 {
	match state_machine {
		StateMachine::Evm(ARBITRUM_CHAIN_ID) | StateMachine::Evm(ARBITRUM_SEPOLIA_CHAIN_ID) =>
			32_000_000,
		StateMachine::Evm(GNOSIS_CHAIN_ID) | StateMachine::Evm(CHIADO_CHAIN_ID) => 16_000_000,
		// Gas limit is 10_000_000, we set our transaction gas limit to 40% of that
		StateMachine::Evm(SEI_CHAIN_ID) | StateMachine::Evm(SEI_TESTNET_CHAIN_ID) => 4_000_000,
		// Gas limit is 60_000_000, we set our transaction gas limit to 30% of that
		StateMachine::Evm(CRONOS_CHAIN_ID) | StateMachine::Evm(CRONOS_TESTNET_CHAIN_ID) =>
			18_000_000,
		// Gas limit is 50_000_000, we set our transaction gas limit to 30% of that
		StateMachine::Evm(INJECTIVE_CHAIN_ID) | StateMachine::Evm(INJECTIVE_TESTNET_CHAIN_ID) =>
			15_000_000,
		// Ethereum L1 max's gas limit per transaction will be reduced to 16m soon.
		StateMachine::Evm(_) => 16_000_000,
		_ => Default::default(),
```

**File:** docs/content/protocol/consensus/beefy.mdx (L55-55)
```text
While BLS precompiles are not yet available on popular EVM chains, we unfortunately have to use ECDSA signatures to prove BEEFY finality. Although ECDSA signatures are cheap to verify, the number of signatures creates high verification cost and prevents frequent posting of consensus proofs for faster finality. This is because ECDSA signatures do not support aggregation, and the verification cost increases linearly with the number of validators.
```
