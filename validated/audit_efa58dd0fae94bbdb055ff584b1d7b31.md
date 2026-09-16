Confirmed: `Codec.DecodeHeader` at `evm/src/consensus/Codec.sol:71-102` reads a SCALE compact-encoded `length` at line 78 and immediately allocates `Digest[] memory digests = new Digest[](length)` at line 79 with no upper bound and no check against the actual remaining bytes in `encoded`. `decodeDigestItem` (lines 104-110) similarly reads a compact `length` and passes it straight into `Bytes.read(slice, length)`. Crucially, in `EcdsaBeefy.verifyParachainHeaderProof` (`evm/src/consensus/EcdsaBeefy.sol:198-229`), `Codec.DecodeHeader(para.header)` is invoked on every attacker-supplied `para.header` **inside the loop at line 210, before** the merkle multi-proof (`MerkleMultiProof.VerifyProof(headsRoot, proof.proof, leaves, proof.leafCount)`) is checked at line 224. The parachain headers are therefore decoded — and the oversized array allocated — before any authentication of their membership in the finalized BEEFY MMR/parachain-heads tree.

### Title
Unbounded array allocation from unvalidated SCALE length field in `Codec.DecodeHeader` before proof verification - (File: evm/src/consensus/Codec.sol)

### Summary
`Codec.DecodeHeader` trusts an attacker-controlled SCALE compact-encoded digest count to size a Solidity memory array, and `decodeDigestItem` similarly trusts a length field to size a byte read, both without validating the value against the actual size of the supplied header bytes. `EcdsaBeefy.verifyParachainHeaderProof` calls this decoder on every submitted parachain header *before* verifying the parachain-heads merkle multi-proof, so a relayer can force expensive/failing allocations from bytes that have not yet been authenticated as being part of any finalized consensus state — mirroring the CVE-2017-11613 pattern of sizing an allocation from an untrusted length before validating the input actually supports that size.

### Finding Description
`DecodeHeader` (`evm/src/consensus/Codec.sol:78-79`) decodes a compact integer `length` directly off the caller-supplied header bytes and executes `new Digest[](length)`. Solidity has no way to reject this prior to attempting the allocation/loop; the eventual bounds failure only surfaces later, per-item, inside `Bytes.read`/`readByte` (`Codec.sol:113-114`, `125-126`), which revert only once the loop tries to consume more bytes than exist. Likewise `decodeDigestItem` (`Codec.sol:104-110`) reads a second untrusted `length` and forwards it straight to `Bytes.read(slice, length)`.

`EcdsaBeefy.verifyParachainHeaderProof` (`evm/src/consensus/EcdsaBeefy.sol:198-229`) is reachable from the public `verify` entrypoint (`EcdsaBeefy.sol:96-114`), which any relayer can call by submitting a `BeefyConsensusProof`/`ParachainProof` for the `EcdsaBeefy` consensus client. Inside the loop (line 210) `Codec.DecodeHeader(para.header)` runs for *every* parachain entry supplied by the caller, and only *after* the full loop completes does the code call `MerkleMultiProof.VerifyProof(headsRoot, proof.proof, leaves, proof.leafCount)` (line 224) to check that these headers are actually part of the trusted parachain-heads root. This is a decode-before-verify ordering: the expensive/attacker-influenced decode work executes on data that has not been authenticated. [1](#0-0) [2](#0-1) [3](#0-2) 

### Impact Explanation
Because `para.header`/`Parachain[]` array length is itself attacker-supplied (bounded only by calldata gas cost, not by protocol logic), and header decoding happens prior to proof verification, a caller can submit a batch of bogus parachain headers whose embedded digest-count field is set to a very large value, forcing the EVM to attempt a correspondingly large memory allocation (`new Digest[](length)`) for each header before any of them are proven to belong to the finalized MMR. This wastes gas / causes reverts on decode of unauthenticated data and, in the worst case for a caller relying on a large batch, can make legitimate multi-header updates unable to complete if an adversarial header is admixed, since the whole `verify` call reverts on the very first malformed header — a denial-of-service against the light client's ability to advance/verify parachain state via this consensus client, rather than a lasting on-chain fund loss.

### Likelihood Explanation
Any address can call `EcdsaBeefy.verify` with a crafted `proof` bytes blob decoding to a `RelayChainProof`/`ParachainProof` containing an arbitrary `para.header`; no signature or prior authentication gates the header bytes before `Codec.DecodeHeader` runs on them. The BEEFY signature/authority checks (`verifyMmrUpdateProof`) happen on the relay-chain commitment, not on the individual parachain header bytes, so the unauthenticated decode path is trivially reachable by a single malicious/careless relayer submission.

### Recommendation
Bound the digest `length` read in `Codec.DecodeHeader` (and the item length in `decodeDigestItem`) against the remaining bytes in `encoded`/`slice` before allocating, e.g. `require(length <= (encoded.length - slice.offset))`, or otherwise cap it against a sane protocol maximum before calling `new Digest[](length)`. Additionally, verify `MerkleMultiProof.VerifyProof` for parachain header membership *before* calling `Codec.DecodeHeader` on each header in `EcdsaBeefy.verifyParachainHeaderProof`, so unauthenticated header bytes are never decoded.

### Proof of Concept
1. Construct a `ParachainProof` with one `Parachain` entry whose `header` bytes are: 32-byte parent hash + valid compact block number + 32-byte state root + 32-byte extrinsics root + a SCALE compact-encoded digest `length` set to a very large value (e.g., the max representable in the 4-byte compact mode, ~1,073,741,823) with no actual digest bytes following.
2. Submit this as part of a `BeefyConsensusProof`/`ParachainProof` pair to `EcdsaBeefy.verify` (through the handler that calls the consensus client) as any address (no auth required for the parachain header contents).
3. Execution reaches `verifyParachainHeaderProof` → `Codec.DecodeHeader(para.header)` at `EcdsaBeefy.sol:210`, which executes `new Digest[](length)` with the attacker-chosen huge `length` *before* `MerkleMultiProof.VerifyProof` is ever called at line 224, consuming excessive gas / reverting on the very first out-of-bounds `readByte` inside the loop — regardless of whether the header was ever a real, finalized parachain header.

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

**File:** evm/src/consensus/Codec.sol (L104-122)
```text
    /// @dev Decodes a SCALE-encoded digest item (4-byte consensus id + length-prefixed data).
    function decodeDigestItem(ByteSlice memory slice) internal pure returns (DigestItem memory) {
        bytes4 id = Bytes.toBytes4(read(slice, 4), 0);
        uint256 length = ScaleCodec.decodeUintCompact(slice);
        bytes memory data = Bytes.read(slice, length);
        return DigestItem(id, data);
    }

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
```

**File:** evm/src/consensus/EcdsaBeefy.sol (L198-229)
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

        return intermediates;
    }
```
