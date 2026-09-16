### Title
Unbounded array allocation from attacker-controlled SCALE digest count in BEEFY header decoding causes gas-exhaustion DoS - (File: evm/src/consensus/Codec.sol)

### Summary
`Codec.DecodeHeader` decodes a SCALE-compact-encoded "digest count" directly from an untrusted, relayer-supplied parachain header and uses it—without any upper bound check—to allocate a Solidity memory array (`new Digest[](length)`). This mirrors the seroval advisory's root cause: trusting an encoded length field to size an in-memory collection during deserialization, allowing a value orders of magnitude larger than the real payload to blow up processing cost.

### Finding Description
`DecodeHeader` reads the digest-count as a SCALE compact integer and immediately allocates an array of that size before validating that the underlying byte slice actually contains that many digest entries: [1](#0-0) 

`decodeUintCompact`'s mode-3 branch allows values up to `2^53`-ish territory read from 4–8 attacker-controlled bytes: [2](#0-1) 

`DecodeHeader` is invoked once per parachain entry inside `EcdsaBeefy.verifyParachainHeaderProof`, iterating over `proof.parachains[i].header`, which is fully attacker-supplied calldata decoded in the top-level `verify()` entry point: [3](#0-2) [4](#0-3) 

Because Solidity zero-initializes newly allocated memory arrays and EVM memory-expansion gas cost is quadratic in size, allocating `new Digest[](length)` with a maliciously large `length` (crafted by putting a bogus 4-byte compact-mode-2 or 8-byte mode-3 prefix in the digest-count position of the header) causes gas consumption far beyond any realistic block gas limit before the per-digest loop even executes its bounds-checked `readByte`.

### Impact Explanation
Any unprivileged relayer submitting a BEEFY consensus update (`EcdsaBeefy.verify`, reachable via `ConsensusRouter`/`EvmHost`) fully controls the `header` bytes for each `Parachain` entry in `ParachainProof.parachains`. By embedding one crafted header with an inflated digest-count field alongside otherwise-legitimate parachain headers in the same batched proof, the relayer forces the entire consensus-update transaction to revert from gas exhaustion. If consensus updates are batched with pending message deliveries in the same transaction/workflow (as is standard for keeping relayer gas costs down), this can be used to grief and stall delivery of legitimate cross-chain messages routed through affected parachains, i.e., "a route unable to deliver messages," until an honest relayer submits a clean, isolated update. This satisfies the CWE-770 (uncontrolled resource consumption) bug class from the seroval advisory, mapped onto Hyperbridge's on-chain BEEFY consensus verification path.

### Likelihood Explanation
High likelihood of triggerability: the digest-count field is a single, simple, unauthenticated compact-integer prefix inside `para.header`, and the header content is neither hash-committed nor length-validated before `DecodeHeader` runs — the crafted header only needs to pass through as calldata; the digest loop's `require` bounds checks fire only after the oversized allocation already incurred its gas cost. No signature or authority-set validity is needed to *cause* the DoS since the revert happens during header parsing, which occurs before/independent of validator-set membership checks completing for that specific header in the loop.

### Recommendation
In `Codec.DecodeHeader`, bound the decoded digest `length` against the remaining bytes in the slice (e.g., `require(length <= (slice.data.length - slice.offset))`) or against a fixed sane maximum before allocating `Digest[] memory digests = new Digest[](length)`. Consider validating that the SCALE compact length cannot exceed a realistic maximum (e.g., a small constant reflecting real Substrate header digest counts) before performing the allocation, analogous to how seroval was patched to derive array length from the actual decoded content rather than from an untrusted length field.

### Proof of Concept
1. Craft a `Header` byte string per the SCALE header format: 32-byte parentHash, compact blockNumber, 32-byte stateRoot, 32-byte extrinsicsRoot, then a compact-encoded digest count using mode-3 encoding (`(len_byte, ...8 bytes)`) set to a very large value (e.g., `0xFFFFFFFFFFFFFFFF`-derived compact form), followed by no further bytes.
2. Submit this as one `Parachain.header` inside `ParachainProof.parachains[]`, alongside minimal valid data to satisfy the outer `abi.decode`, via `EcdsaBeefy.verify(previousState, proof)` (reached through `ConsensusRouter`/`EvmHost` consensus update entry point).
3. Observe that `Codec.DecodeHeader` executes `Digest[] memory digests = new Digest[](length)` with the attacker-chosen huge `length`, causing the transaction to run out of gas and revert, consuming the submitting relayer's full gas allowance and failing the batched update. [5](#0-4)

### Citations

**File:** evm/src/consensus/Codec.sol (L70-99)
```text
    // @dev Deserializes a substrate header
    function DecodeHeader(bytes memory encoded) internal pure returns (Header memory) {
        ByteSlice memory slice = ByteSlice(encoded, 0);
        bytes32 parentHash = Bytes.toBytes32(Bytes.read(slice, 32));
        uint256 blockNumber = ScaleCodec.decodeUintCompact(slice);
        bytes32 stateRoot = Bytes.toBytes32(Bytes.read(slice, 32));
        bytes32 extrinsicsRoot = Bytes.toBytes32(Bytes.read(slice, 32));

        uint256 length = ScaleCodec.decodeUintCompact(slice);
        Digest[] memory digests = new Digest[](length);

        for (uint256 i = 0; i < length; i++) {
            uint8 kind = Bytes.readByte(slice);
            Digest memory digest;
            if (kind == DIGEST_ITEM_OTHER) {
                digest.isOther = true;
            } else if (kind == DIGEST_ITEM_CONSENSUS) {
                digest.isConsensus = true;
                digest.consensus = decodeDigestItem(slice);
            } else if (kind == DIGEST_ITEM_SEAL) {
                digest.isSeal = true;
                digest.seal = decodeDigestItem(slice);
            } else if (kind == DIGEST_ITEM_PRERUNTIME) {
                digest.isPreRuntime = true;
                digest.preruntime = decodeDigestItem(slice);
            } else if (kind == DIGEST_ITEM_RUNTIME_ENVIRONMENT_UPDATED) {
                digest.isRuntimeEnvironmentUpdated = true;
            }
            digests[i] = digest;
        }
```

**File:** evm/src/consensus/Codec.sol (L162-171)
```text
        } else if (mode == 3) {
            // [1073741824, 4503599627370496]
            uint8 l = (b >> 2) + 4; // remove mode bits
            require(l <= 8, "unexpected prefix decoding Compact<Uint>");
            return ScaleCodec.decodeUint256(read(data, l));
        } else {
            revert("Code should be unreachable");
        }
        return (value);
    }
```

**File:** evm/src/consensus/EcdsaBeefy.sol (L96-114)
```text
    function verify(bytes calldata previousState, bytes calldata proof)
        external
        pure
        returns (bytes memory, IntermediateState[] memory, uint256)
    {
        BeefyConsensusState memory consensusState = abi.decode(previousState, (BeefyConsensusState));
        (RelayChainProof memory relay, ParachainProof memory parachain) =
            abi.decode(proof, (RelayChainProof, ParachainProof));

        // Stale proofs are a no-op: return the previous state with no intermediates so the caller
        // can treat replays as idempotent rather than having to guard against reverts.
        if (consensusState.latestHeight >= relay.signedCommitment.commitment.blockNumber) {
            return (abi.encode(consensusState), new IntermediateState[](0), consensusState.nextAuthoritySet.id);
        }
        (BeefyConsensusState memory newState, bytes32 headsRoot) = verifyMmrUpdateProof(consensusState, relay);
        IntermediateState[] memory intermediates = verifyParachainHeaderProof(headsRoot, parachain);

        return (abi.encode(newState), intermediates, newState.nextAuthoritySet.id);
    }
```

**File:** evm/src/consensus/EcdsaBeefy.sol (L199-221)
```text
    function verifyParachainHeaderProof(bytes32 headsRoot, ParachainProof memory proof)
        internal
        pure
        returns (IntermediateState[] memory)
    {
        uint256 len = proof.parachains.length;
        MerkleMultiProof.Leaf[] memory leaves = new MerkleMultiProof.Leaf[](len);
        IntermediateState[] memory intermediates = new IntermediateState[](len);

        for (uint256 i = 0; i < len; i++) {
            Parachain memory para = proof.parachains[i];
            Header memory header = Codec.DecodeHeader(para.header);
            if (header.number == 0) revert IllegalGenesisBlock();

            leaves[i] = MerkleMultiProof.Leaf(
                para.index,
                keccak256(bytes.concat(ScaleCodec.encode32(uint32(para.id)), ScaleCodec.encodeBytes(para.header)))
            );

            StateCommitment memory commitment = header.stateCommitment();
            intermediates[i] =
                IntermediateState({stateMachineId: para.id, height: header.number, commitment: commitment});
        }
```
