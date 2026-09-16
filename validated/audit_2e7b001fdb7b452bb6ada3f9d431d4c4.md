Confirmed reachability: `Codec.DecodeHeader` (`evm/src/consensus/Codec.sol:71-102`) is called from `EcdsaBeefy.verifyParachainHeaderProof` (`evm/src/consensus/EcdsaBeefy.sol:210`), which any relayer can trigger by submitting a BEEFY consensus proof through the `verify()` entrypoint — reachable from `handleConsensus` in the dispatch path [1](#0-0) .

### Title
Unbounded SCALE-decoded length used for memory array/byte allocation in `Codec.DecodeHeader`/`decodeDigestItem` enables gas-griefing/OOG DoS of BEEFY consensus proof verification - (File: evm/src/consensus/Codec.sol)

### Summary
`Codec.DecodeHeader` and its helper `decodeDigestItem` read an attacker-controlled SCALE compact-encoded length from the parachain header bytes embedded in a relayer-submitted BEEFY consensus proof, and use that length directly, with no upper bound, to size a Solidity dynamic array (`new Digest[](length)`) and to slice/copy memory (`Bytes.read(slice, length)`), before any bound check against the remaining buffer size beyond a `require` inside `read`/`readByte`.

### Finding Description
`DecodeHeader` decodes a digest-count field via `ScaleCodec.decodeUintCompact(slice)` and immediately allocates `Digest[] memory digests = new Digest[](length)` [2](#0-1) . SCALE compact-encoding can express any `uint256` value up to `2^64`-ish range depending on mode (mode 3 supports up to 8 bytes, i.e., values up to `2^64-1`) via `decodeUintCompact` [3](#0-2) . There is no ceiling check on `length` before the array allocation — only the subsequent per-item `Bytes.readByte`/`Bytes.read` calls inside the loop will eventually `require` and revert once the ByteSlice is exhausted [4](#0-3) . Likewise, `decodeDigestItem` decodes a per-digest byte length and does `Bytes.read(slice, length)` with the same lack of an upfront bound check relative to a safe maximum [5](#0-4) .

This is reachable end-to-end: a relayer submits a BEEFY consensus proof to `EcdsaBeefy.verify()` (or the SP1/other BEEFY variants that also call `Codec.DecodeHeader`), which is invoked for each parachain header in `verifyParachainHeaderProof` — a loop over attacker-supplied `proof.parachains` [6](#0-5) . Because the parachain header bytes (`para.header`) are attacker-supplied calldata, the attacker fully controls the compact-encoded digest count and the fake per-digest lengths.

Although Solidity's memory-expansion gas cost imposes a natural ceiling (quadratic gas growth eventually causes out-of-gas), a value crafted to consume the maximum allocation the block gas limit allows will cause the `handleConsensus`/BEEFY `verify()` call to revert only after burning attacker (or relayer-paid) gas doing large memory allocation/zeroing, and — more importantly — this is the same unchecked-length-to-allocation pattern flagged by CVE-2021-21847 (an untrusted length field feeding directly into buffer/array sizing without a sanity bound), just manifesting here as an EVM memory-expansion DoS rather than a heap overflow, since Solidity's memory model is bounds-checked by the VM itself.

### Impact Explanation
A malicious or malfunctioning relayer can submit a BEEFY consensus proof containing a parachain header with a maliciously large decoded digest count or bogus digest-item length. This forces the EVM to attempt allocating a correspondingly large `Digest[]` array / byte slice in memory, consuming gas quadratically via memory expansion, up to the point the transaction runs out of gas and reverts. Because this happens inside `verify()` — called from the consensus dispatch path that is a prerequisite for delivering post/get requests and responses through `HandlerV2` — repeated submission of such proofs can be used to grief relayers (forcing them to pay large gas fees for failed transactions) or to stall consensus updates for the affected route, delaying message delivery. This does not directly cause theft or unbacked mint, but it undermines the "message delivery availability" guarantee for the affected route (a route becoming temporarily unable to deliver messages while gas-griefing is ongoing), which is one of the impact categories explicitly in scope.

### Likelihood Explanation
Likelihood is limited by the fact that Solidity/EVM enforces gas-metered memory expansion, so this cannot cause true heap corruption or unbounded memory growth as in the native C/C++ GPAC bug — the EVM will always revert once gas is exhausted. Exploitation requires only that an attacker control `para.header` bytes inside a submitted BEEFY consensus proof, which any permissionless relayer can do, making the crafted input trivially reachable. However the actual DoS effect is bounded by block gas limits and mainly wastes the submitter's own gas unless multiplied across many parachains in `proof.parachains`, making it a griefing/availability nuisance rather than a High-severity fund-loss issue.

### Recommendation
Add an explicit upper bound check on the decoded digest count and on each digest item's length immediately after calling `decodeUintCompact` in both `DecodeHeader` and `decodeDigestItem`, rejecting any header whose claimed lengths exceed a small constant bound (e.g., the maximum plausible number of digests/consensus-log size for a Substrate header) before performing any array allocation or memory copy — analogous to the fix pattern already used elsewhere in this codebase (e.g., `MAX_PROOF_DEPTH`, `MaxCallSize` bounds in `modules/pallets/call-decompressor/src/lib.rs`).

### Proof of Concept
1. Craft a `Parachain` header bytes blob (`para.header`) that encodes a valid 32-byte parent hash, block number, state root, extrinsics root, followed by a SCALE compact-encoded digest count using mode-3 encoding to claim a very large value (e.g., close to `type(uint256).max` truncated to available bytes, or simply a large `uint32`/`uint64` value well beyond any real header's digest count).
2. Submit this as part of a `RelayChainProof`/`ParachainProof` to `EcdsaBeefy.verify(previousState, proof)` (or via `HandlerV2.handleConsensus`).
3. Observe that `Codec.DecodeHeader` attempts `new Digest[](length)` with the attacker-supplied `length`, causing large gas consumption in memory expansion before the loop's `Bytes.readByte` eventually reverts on buffer exhaustion — the transaction fails after consuming gas proportional to the attacker-chosen `length`, up to the block gas limit.

### Citations

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

**File:** evm/src/consensus/EcdsaBeefy.sol (L204-221)
```text
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

**File:** evm/src/consensus/Codec.sol (L78-79)
```text
        uint256 length = ScaleCodec.decodeUintCompact(slice);
        Digest[] memory digests = new Digest[](length);
```

**File:** evm/src/consensus/Codec.sol (L104-110)
```text
    /// @dev Decodes a SCALE-encoded digest item (4-byte consensus id + length-prefixed data).
    function decodeDigestItem(ByteSlice memory slice) internal pure returns (DigestItem memory) {
        bytes4 id = Bytes.toBytes4(read(slice, 4), 0);
        uint256 length = ScaleCodec.decodeUintCompact(slice);
        bytes memory data = Bytes.read(slice, length);
        return DigestItem(id, data);
    }
```

**File:** evm/src/consensus/Codec.sol (L112-132)
```text
    /// @dev Reads `len` bytes from the slice at the current offset and advances the cursor.
    function read(ByteSlice memory self, uint256 len) internal pure returns (bytes memory) {
        require(self.offset + len <= self.data.length);
        if (len == 0) {
            return "";
        }
        uint256 addr = Memory.dataPtr(self.data);
        bytes memory slice = Memory.toBytes(addr + self.offset, len);
        self.offset += len;
        return slice;
    }

    /// @dev Reads a single byte from the slice at the current offset and advances the cursor.
    function readByte(ByteSlice memory self) internal pure returns (uint8) {
        require(self.offset + 1 <= self.data.length);

        uint8 b = uint8(self.data[self.offset]);
        self.offset += 1;

        return b;
    }
```

**File:** evm/src/consensus/Codec.sol (L162-166)
```text
        } else if (mode == 3) {
            // [1073741824, 4503599627370496]
            uint8 l = (b >> 2) + 4; // remove mode bits
            require(l <= 8, "unexpected prefix decoding Compact<Uint>");
            return ScaleCodec.decodeUint256(read(data, l));
```
