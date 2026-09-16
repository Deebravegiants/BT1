### Title
Quadratic-cost SCALE re-encoding of attacker-controlled BEEFY commitment payload before signature verification enables gas-griefing DoS of consensus delivery - ([File: evm/src/consensus/Codec.sol])

### Summary
`Codec.Encode(Commitment memory commitment)` rebuilds the SCALE-encoded commitment bytes by repeatedly calling `bytes.concat(payload, ...)` inside a loop over `commitment.payload`, and `EcdsaBeefy.verifyMmrUpdateProof` calls this encoder to compute `commitmentHash` *before* any ECDSA signature is validated against it. Because `bytes.concat` allocates a new buffer and copies the entire accumulated array on every iteration, the cost of this step is quadratic in the number/size of payload entries, and those entries are entirely attacker-controlled calldata reaching an unauthenticated, permissionless entry point (`HandlerV2.handleConsensus`).

### Finding Description
`Codec.Encode` accumulates the payload buffer with a classic O(n²) pattern: [1](#0-0) 

This function is invoked from `verifyMmrUpdateProof` to derive `commitmentHash`, which is only afterward used to recover signer addresses via `ECDSA.recover`: [2](#0-1) 

`verifyMmrUpdateProof` is reachable from `HandlerV2.handleConsensus`, an unprivileged, unauthenticated external function that any caller can invoke with an arbitrary `proof` byte string, gated only by a freshness check (`consensusUpdateTime`/`unStakingPeriod`) and the `notFrozen` modifier — no signature or authority check happens before `IConsensusV2(...).verify(...)` runs: [3](#0-2) 

Because `Commitment.payload` is decoded directly from attacker-supplied calldata and `checkParticipationThreshold`/`ECDSA.recover` only run *after* `Codec.Encode(commitment)` completes, an attacker can submit a `Commitment` with a large number of payload entries (each carrying an arbitrary-length `data` field) purely to drive up the cost of the `bytes.concat` accumulation, independent of whether the embedded signatures are ever valid. This mirrors the pyasn1 bug class: unauthenticated, structurally-driven quadratic-time encode/decode of a variable-length sequence, executed prior to any cryptographic authentication of the data.

### Impact Explanation
`handleConsensus` gates the entire consensus-update pipeline that all downstream `handlePostRequests`/`handleGetResponses` calls depend on (via `host.storeConsensusState`/`storeStateMachineCommitment`). If a crafted, over-sized payload consumes gas disproportionately (quadratically) relative to its byte size, a single malicious "consensus" submission can be tuned to exhaust the block gas limit or a caller's configured gas limit purely from the encode step, before the mismatched/invalid signatures would otherwise cause a cheap revert. When such a call is included inside `HandlerV2.batchCall` (atomic, all-or-nothing `delegatecall` loop), it can also force reversion of an entire batch of otherwise-valid messages bundled by a relayer: [4](#0-3) 
This can be used to grief relayers and delay legitimate consensus/state updates, temporarily stalling message delivery for the route until relayers adapt gas estimates or filter payload sizes — an availability impact on the bridge's core dispatch path.

### Likelihood Explanation
The entry point (`handleConsensus`) is completely permissionless and requires no fee beyond ordinary EVM gas, and the vulnerable `Codec.Encode` call executes unconditionally before any cryptographic check on the payload contents. Any address can submit a `Commitment` with an arbitrarily large `payload` array without needing valid BEEFY signatures, since the quadratic-cost step happens ahead of `ECDSA.recover`/participation checks. No `MAX_PAYLOAD`-style bound was found on `commitment.payload.length` in `Codec.sol` or `EcdsaBeefy.sol`.

### Recommendation
Encode `Commitment.payload` using a pre-sized buffer (e.g., accumulate into a `bytes` via `abi.encodePacked` written once with `Memory`-level copy, or compute the final size up front and write into a single allocated buffer) instead of repeated `bytes.concat` reallocation, making the encode linear in total payload size. Additionally, enforce an explicit upper bound on `commitment.payload.length` (and per-entry `data.length`) before entering the encode loop, and perform this size check before any encoding work is done.

### Proof of Concept
1. Craft a `BeefyConsensusProof` calldata blob whose `relayProof.signedCommitment.commitment.payload` array contains `N` entries, each with a large `data` field (e.g., tens of KB total), with arbitrary/invalid `votes` signatures.
2. Call `HandlerV2.handleConsensus(host, proof)` directly (bypassing any batching).
3. Observe that gas consumption in `Codec.Encode(commitment)` scales quadratically with `N`/payload size, causing an out-of-gas revert (or requiring drastically higher gas than a linear-cost equivalent would need) well before `ECDSA.recover`/`checkParticipationThreshold` ever run — confirming the quadratic cost is paid purely for calldata shape, independent of proof validity. Repeating this inside `batchCall` demonstrates that an attacker-supplied consensus message alone can revert an entire batched submission.

### Citations

**File:** evm/src/consensus/Codec.sol (L38-55)
```text
    function Encode(Commitment memory commitment) internal pure returns (bytes memory) {
        uint256 payloadLen = commitment.payload.length;
        bytes memory payload = bytes("");
        for (uint256 i = 0; i < payloadLen; i++) {
            payload = bytes.concat(
                payload,
                abi.encodePacked(commitment.payload[i].id),
                ScaleCodec.encodeBytes(commitment.payload[i].data)
            );
        }

        return bytes.concat(
            ScaleCodec.encodeUintCompact(payloadLen),
            payload,
            ScaleCodec.encode32(commitment.blockNumber),
            ScaleCodec.encode64(commitment.validatorSetId)
        );
    }
```

**File:** evm/src/consensus/EcdsaBeefy.sol (L127-153)
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
```

**File:** evm/src/core/HandlerV2.sol (L129-135)
```text
    function batchCall(bytes[] memory calls) external {
        uint256 len = calls.length;
        for (uint256 i = 0; i < len; ++i) {
            (bool success, bytes memory returnData) = address(this).delegatecall(calls[i]);
            if (!success) revert BatchCallFailed(i, returnData);
        }
    }
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
