### Title
Unbounded digest-count allocation in `Codec.DecodeHeader` lets a relayer-submitted BEEFY parachain header consume unbounded memory/gas before any length validation - (File: `evm/src/consensus/Codec.sol`)

### Summary
`Codec.DecodeHeader` reads a SCALE compact-encoded digest count directly from an attacker-supplied parachain header byte string and immediately allocates a memory array of that size — `Digest[] memory digests = new Digest[](length);` — before any check that `length` is plausible relative to the remaining bytes in the header. This mirrors the ALPINE-CVE-2025-43857 pattern: a length field read from an untrusted peer is used to pre-allocate memory before the parser has confirmed the underlying bytes actually exist.

### Finding Description
`DecodeHeader` decodes the digest count with `ScaleCodec.decodeUintCompact(slice)` and allocates the `Digest[]` array from that raw value with no upper bound and no check that `length` bytes (at minimum, 1 byte digest-kind marker per entry) remain in `encoded`: [1](#0-0) 

The only later protection is the per-item `read`/`readByte` bounds checks (`require(self.offset + len <= self.data.length)`), which only fire once the loop starts trying to consume entries — but the array allocation itself (`new Digest[](length)`) happens unconditionally before the loop, sized directly from the untrusted `length` value: [2](#0-1) 

This function is reached from the unprivileged, permissionless BEEFY consensus-update path: `EcdsaBeefy.verify` → `verifyParachainHeaderProof`, which calls `Codec.DecodeHeader(para.header)` for every parachain header included in a submitted `ParachainProof`, with `para.header` fully attacker-controlled bytes supplied in the proof argument to the public `verify` entry point: [3](#0-2) 

Any address can submit a BEEFY consensus proof (this is the permissionless consensus-update path that any relayer uses), and each `para.header` is decoded before any signature/merkle validation is performed on its contents, meaning a malformed header with a huge SCALE-compact digest count reaches `new Digest[](length)` before the header is even verified to belong to a legitimate finalized parachain block.

### Impact Explanation
On the EVM this manifests as gas-cost blow-up rather than classic heap exhaustion (Solidity's `new T[](n)` triggers quadratic memory-expansion gas cost), but the underlying bug class is identical to the CVE: a length value taken straight off the wire is used to size an allocation before the parser has validated it against the actual remaining payload. A crafted header (`length` set to a very large compact integer, e.g. via the 4-byte SCALE-compact encoding which allows values up to `2^32-1`) forces `verifyParachainHeaderProof`/`DecodeHeader` to attempt a huge array allocation, causing the transaction to revert with out-of-gas once memory-expansion cost exceeds the block gas limit. Because the consensus-update path is unauthenticated and callable by anyone, a malicious relayer can craft (or splice into) a `ParachainProof` a header with an inflated digest count, forcing any relayer's consensus submission that includes it to fail/burn gas, and — more importantly — the same class of unchecked length can be reused as a griefing primitive against the light-client's ability to deliver otherwise-valid parachain state commitments, i.e., a route unable to deliver messages if legitimate consensus updates are consistently front-run/griefed with malformed headers.

### Likelihood Explanation
Likelihood is high for the surface being reachable: the function is on the primary, permissionless BEEFY consensus-verification path (`EcdsaBeefy.verify`), requires no privileged role, and the header bytes are taken as-is from proof data with no upstream sanitation before `DecodeHeader` is invoked. The cost to the attacker is only the gas for the reverted call attempt; there is no economic bond required to submit a consensus proof.

### Recommendation
Bound `length` in `DecodeHeader` against `slice.data.length - slice.offset` (or a fixed sane maximum digest count) before allocating `Digest[] memory digests = new Digest[](length)`, mirroring the defensive pattern already applied to the zstd/`call-decompressor` pallet's claimed-size bound (`ensure!(encoded_call_size < T::MaxCallSize::get() * ONE_MB, ...)`) — reject headers whose claimed digest count cannot possibly fit in the remaining bytes before doing any allocation.

### Proof of Concept
1. Construct a `Parachain` proof entry whose `header` bytes are a valid 32-byte parent hash + block number + state root + extrinsics root, followed by a SCALE-compact-encoded digest-count value close to `2^32-1` (mode `3`, 4-byte length encoding) and no further digest bytes.
2. Call `EcdsaBeefy.verify(previousState, proof)` with this crafted `ParachainProof` (no valid signatures/merkle proof required to reach `DecodeHeader`, since `verifyParachainHeaderProof` is called with attacker-supplied `parachains` and only checked against `MerkleMultiProof.VerifyProof` *after* every header's `Digest[]` has already been allocated in the loop).
3. Observe `Codec.DecodeHeader` attempt `new Digest[](4294967295)`, which either reverts with out-of-gas or consumes gas disproportionate to the size of the submitted calldata, before the malformed header is ever rejected by signature/merkle validation. [4](#0-3) [5](#0-4)

### Citations

**File:** evm/src/consensus/Codec.sol (L70-102)
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

        return Header(parentHash, blockNumber, stateRoot, extrinsicsRoot, digests);
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

**File:** evm/src/consensus/EcdsaBeefy.sol (L198-226)
```text
    // @dev Verifies that some parachain header has been finalized, given the current trusted consensus state.
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

        if (len > 0) {
            bool valid = MerkleMultiProof.VerifyProof(headsRoot, proof.proof, leaves, proof.leafCount);
            if (!valid) revert InvalidMmrProof();
        }
```
