### Title
Uncontrolled Resource Consumption in `Codec.Encode(Commitment)` via Unbounded Payload Array During BEEFY Consensus Verification - (File: evm/src/consensus/Codec.sol)

### Summary
`Codec.Encode(Commitment memory commitment)` SCALE-encodes a BEEFY commitment by repeatedly reallocating and copying a growing `bytes memory payload` buffer inside a loop using `bytes.concat`, once per element of `commitment.payload`. [1](#0-0)  This is the same algorithmic-complexity bug class as CVE-2020-7212 (repeated O(N) work per element of an attacker-sized array, yielding O(N²) total cost), except here the cost is paid in EVM gas rather than CPU time, and `commitment.payload` is fully attacker-controlled input to `EcdsaBeefy.verify`.

### Finding Description
`EcdsaBeefy.verifyMmrUpdateProof` takes a `RelayChainProof` decoded directly from calldata supplied by any caller of `verify` (reachable from `ConsensusRouter`/`EvmHost` update-consensus-state flow, callable by any relayer submitting a consensus proof). The `Commitment.payload` array (`Payload[] payload`) has no length bound before it is passed to `Codec.Encode`: [2](#0-1)  `commitment.validatorSetId` and `payload` come straight from `abi.decode(proof, (RelayChainProof, ParachainProof))` with no length check performed before the loop that scans `commitment.payload` for the MMR-root entry, nor before `Codec.Encode(commitment)` is called to compute `commitmentHash`.

Inside `Codec.Encode`, each iteration does:
```
payload = bytes.concat(payload, abi.encodePacked(commitment.payload[i].id), ScaleCodec.encodeBytes(commitment.payload[i].data));
``` [3](#0-2)  `bytes.concat` in Solidity allocates a new buffer sized to the sum of its inputs and copies the accumulated `payload` (which itself grows every iteration) into it. For `n` payload entries, this is `1 + 2 + ... + n` byte copies of the running payload, i.e. `O(n²)` copy cost — algorithmically identical to urllib3's undeduplicated `percent_encodings` re-scan in `_encode_invalid_chars`. Because `Payload.data` is itself a `bytes` field with no length limit, an attacker can also make each element's `data` large, further multiplying the memory-copy cost (`O(n² · d)` where `d` is average payload-data size).

### Impact Explanation
An unprivileged relayer submitting a BEEFY consensus proof can craft a `Commitment` with a very large `payload` array (bounded only by calldata gas limits, which is far more permissive than execution gas costs of this quadratic copy). This inflates the gas required to compute `commitmentHash = keccak256(Codec.Encode(commitment))` well beyond block gas limits, causing every `verify` call with such a proof to revert with out-of-gas. Because this function sits on the critical consensus-update path used to advance BEEFY finality (`EcdsaBeefy.verify` → `verifyMmrUpdateProof`), and it is `pure`/stateless with no cost charged to the submitter for the resource consumed, a malicious relayer could use this to grief consensus updates or make crafted proofs unprocessable within gas limits, though it does not by itself cause fund loss — it is a route-availability / gas-griefing issue on the consensus update path (a route unable to deliver/settle state updates when abused, though genuine BEEFY payload lists are small in practice which limits real-world severity).

### Likelihood Explanation
Likely low-to-medium in practice: legitimate BEEFY commitments have a very small, fixed-size payload array (typically 1 entry, the MMR root), so this is not triggered by honest relayers. However, `verify` accepts arbitrary ABI-decoded `RelayChainProof` data from any caller with no upstream length validation on `commitment.payload` or `Payload.data`, so a malicious relayer can trivially construct an oversized proof to trigger the quadratic blow-up before any of the cryptographic/merkle checks reject it.

### Recommendation
Bound `commitment.payload.length` (and each `Payload.data.length`) to a small constant (e.g. 1–4 entries, matching the real BEEFY payload spec) immediately upon decoding the proof, before the MMR-root scan loop and before calling `Codec.Encode`. Additionally, rewrite `Codec.Encode(Commitment)` to build the output in a single pre-sized buffer (compute total length first, then write into one allocation) instead of repeated `bytes.concat` reallocation, eliminating the O(n²) copy pattern regardless of input size.

### Proof of Concept
1. Craft a `RelayChainProof` where `signedCommitment.commitment.payload` contains a very large number of `Payload` entries (e.g., tens of thousands), each with non-trivial `data` bytes, while `blockNumber`/`validatorSetId` are set to pass the initial staleness/authority-set checks.
2. Call `EcdsaBeefy.verify(previousState, proof)` (or the equivalent path through `EvmHost`/`ConsensusRouter` update-consensus entrypoint) with this proof.
3. Execution reaches `verifyMmrUpdateProof`, which loops over `commitment.payload` and then calls `Codec.Encode(commitment)` at line 152 of `EcdsaBeefy.sol`.
4. `Codec.Encode`'s per-element `bytes.concat` re-copies the growing `payload` buffer each iteration, causing gas consumption to grow quadratically with the number of payload entries, exceeding the block gas limit and reverting — denying processing of the (crafted) consensus proof and demonstrating the unbounded resource consumption.

### Citations

**File:** evm/src/consensus/Codec.sol (L38-47)
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
```

**File:** evm/src/consensus/EcdsaBeefy.sol (L129-152)
```text
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
```
