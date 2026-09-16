### Title
Quadratic-complexity BEEFY commitment encoding enables gas-exhaustion DoS of consensus updates - (File: evm/src/consensus/Codec.sol)

### Summary
`Codec.Encode(Commitment memory commitment)` builds the SCALE encoding of a BEEFY commitment payload by repeatedly calling `bytes.concat` inside a loop over `commitment.payload`, each iteration re-allocating and copying the entire accumulated buffer. This is the same quadratic-complexity-via-repeated-concatenation bug class described in the commonmarker/cmark-gfm advisory (GHSA-636f-xm5j-pj9m), applied here to Solidity's `EcdsaBeefy` consensus-verification path, which any unprivileged relayer can trigger by submitting a consensus proof.

### Finding Description
`Codec.Encode` iterates the untrusted `commitment.payload` array and grows a `bytes memory payload` buffer via `bytes.concat` on every iteration: [1](#0-0) 

Each call to `bytes.concat` allocates a brand-new byte array sized to the sum of its operands and copies all bytes into it (Solidity has no growable-in-place `bytes memory`). Building up `payload` this way inside a loop of length `n` therefore costs O(n²) time/gas instead of O(n), because every prior byte gets re-copied on every subsequent iteration.

This function is invoked from `EcdsaBeefy.verifyMmrUpdateProof`, which is the BEEFY consensus-verification entry point reachable by any unprivileged relayer submitting a raw consensus message: [2](#0-1) 

Critically, `Codec.Encode(commitment)` (line 152) executes to compute `commitmentHash` for `ECDSA.recover` **before** the authority-set membership merkle proof is checked (line 161). This means the quadratic-cost payload encoding runs unconditionally for any submitted commitment, regardless of whether the accompanying signatures/merkle proof ultimately validate. The `payload` array length and each `Payload.data` byte length are fully attacker-controlled fields of `Commitment`: [3](#0-2) 

`EcdsaBeefy.verify` is the standard `IConsensusV2` entry point invoked when handling a consensus message via the host's message-dispatch path, which is exactly the "consensus verification" surface named in scope (BEEFY light client).

### Impact Explanation
An attacker can craft a `Commitment` with a very large `payload` array (many entries, or entries with large `data` blobs) and submit it as part of a BEEFY consensus proof. The quadratic cost of `Codec.Encode` means gas consumption grows quadratically with payload size, allowing an attacker to force a transaction that consumes gas far out of proportion to the actual data size — potentially exceeding practical block gas limits well before the (linear-sized) payload itself would. Because this SCALE-encoding is also mirrored in the SP1/ZK proof's public-input construction path and generally in any code path that must re-encode an attacker-influenced `Commitment`, a sufficiently large payload can make consensus-proof verification computationally infeasible within a single block, which can starve or delay legitimate BEEFY consensus updates — i.e., a route becoming unable to process/deliver messages that depend on that consensus client advancing.

### Likelihood Explanation
Likelihood is bounded by the following observations, which I want to flag as uncertain without further verification:
- Only a `Commitment` whose SCALE-encoded hash is later verified against real relay-chain validator signatures (via `ECDSA.recover` + `MerkleMultiProof.VerifyProof` against the trusted authority root) can ultimately be accepted as valid; an attacker cannot forge an authority-signed commitment with an arbitrarily bloated payload.
- However, the expensive `Codec.Encode` call executes **before** the merkle-proof/signature validity check fails, so even a doomed-to-fail submission still pays (and can be crafted to burn) quadratic gas — this is a genuine self-inflicted gas-griefing vector for the submitter, and could be weaponized to degrade block-level throughput or fail near the block gas limit if repeated at scale, but does not let an attacker forge a fraudulent state update.
- I was unable to confirm within available context whether there is any upstream bound on `commitment.payload.length` or `Payload.data.length` enforced elsewhere (e.g., in `ScaleCodec.encodeBytes`, in host-level message size caps, or in the off-chain relayer/prover pipeline) before this function is reached on-chain. If such a bound exists and is small (real BEEFY commitments typically carry only 1–2 payload entries), practical exploitability is low. This should be verified directly in a Devin session with full repo access.

### Recommendation
Rewrite `Codec.Encode(Commitment memory commitment)` to compute the total payload length first and write into a single pre-allocated `bytes memory` buffer once (e.g., using an accumulating byte-offset write, or `abi.encodePacked` in a single pass rather than iterative `bytes.concat`), eliminating the repeated reallocation/copy. Additionally, consider enforcing an explicit upper bound on `commitment.payload.length` (and per-entry `data.length`) at the earliest possible point in `EcdsaBeefy.verify`/`verifyMmrUpdateProof`, before any encoding or signature-recovery work is performed, so that oversized payloads are rejected cheaply.

### Proof of Concept
1. Construct a `BeefyConsensusProof` whose `relay.signedCommitment.commitment.payload` array contains `N` entries (e.g., `N = 5,000`), each with a `data` field of a few hundred bytes, and an arbitrary (even garbage) signature list.
2. Call `EcdsaBeefy.verify(previousState, proof)` (directly, or via the host's consensus-message dispatch path).
3. Observe that gas consumption in `Codec.Encode(commitment)` grows quadratically with `N` — profiling `verifyMmrUpdateProof` at increasing `N` values (e.g., 100, 1,000, 5,000) shows non-linear gas growth attributable solely to the `bytes.concat` loop, independent of whether the subsequent `MerkleMultiProof.VerifyProof` check ultimately reverts.

### Citations

**File:** evm/src/consensus/Codec.sol (L37-55)
```text
    // @dev SCALE-encodes the BEEFY finality commitment
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

**File:** evm/src/consensus/EcdsaBeefy.sol (L142-152)
```text
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

**File:** evm/src/consensus/Types.sol (L77-86)
```text
struct Payload {
    bytes2 id;
    bytes data;
}

struct Commitment {
    Payload[] payload;
    uint32 blockNumber;
    uint64 validatorSetId;
}
```
