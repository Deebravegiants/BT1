### Title
Unbounded array allocation from untrusted SCALE length before proof verification enables DoS via out-of-gas revert - (File: evm/src/consensus/Codec.sol, evm/src/consensus/EcdsaBeefy.sol)

### Summary
`Codec.DecodeHeader` allocates a `Digest[]` array sized directly from an attacker-controlled SCALE compact-encoded length field, before any bound check against the remaining calldata/buffer size, and — critically — in `EcdsaBeefy.verifyParachainHeaderProof` this decode is executed *before* the parachain header bytes are validated against `headsRoot` via the Merkle multi-proof. This mirrors the Cryptacular `CiphertextHeader` bug class: an untrusted length taken from header/proof bytes drives a memory allocation with no upper bound, ahead of any authentication of the data supplying that length.

### Finding Description
`Codec.DecodeHeader` reads a SCALE compact integer and immediately allocates an array sized to it: [1](#0-0) 

Unlike `Codec.read`, which bound-checks `offset + len <= data.length` before returning any slice: [2](#0-1) 

the `new Digest[](length)` allocation at line 79 has no such check — `length` can be any value the compact encoding can represent (up to ~2^64), and the array is allocated before the decode loop ever touches `Bytes.readByte`/`read`, which would otherwise revert on out-of-bounds access.

More importantly, `EcdsaBeefy.verifyParachainHeaderProof` calls `Codec.DecodeHeader(para.header)` on each parachain header *inside* the loop that builds the Merkle multi-proof leaves, and only calls `MerkleMultiProof.VerifyProof` (the actual authentication of `para.header` against the previously-verified `headsRoot`) *after* the loop completes: [3](#0-2) 

Because `para.header` is decoded before it is proven to be part of the finalized `headsRoot`, the bytes are fully attacker-controlled calldata at decode time — the same "decode-before-verify" structure that made `CiphertextHeader.java`'s untrusted nonce-length field reachable prior to CVE-2020-7226's fix.

`EcdsaBeefy.verify` is the `IConsensusV2` entry point invoked by the ISMP/consensus message-handling path when any relayer submits a `BeefyConsensusProof`, so this is reachable from a single unprivileged relayed transaction, not a privileged operation.

### Impact Explanation
An attacker can craft a `ParachainProof.parachains[i].header` whose SCALE-encoded digest-count compact integer is large enough that `new Digest[](length)` at `Codec.sol:79` triggers Solidity's quadratic memory-expansion gas cost, forcing an out-of-gas revert of the entire `verify()` call regardless of the gas limit supplied (a length on the order of ~10^5 is already enough to exceed typical block gas limits, since EVM memory-expansion cost grows with the square of the highest touched memory word). Because this happens before the Merkle proof that authenticates `para.header` against `headsRoot`, any submitted consensus/parachain-header proof payload — valid or fabricated — can be made to always fail via OOG rather than being cheaply rejected by the intended `InvalidMmrProof` check.

This is a griefing/availability issue against the specific transaction/submitter rather than a mechanism for theft, unbacked minting, or forged message delivery: EVM gas metering caps the blast radius to the calling transaction (unlike unmetered JVM heap allocation in the original CVE), so it cannot corrupt state, drain funds, or by itself permanently brick the BEEFY light client, since other relayers can still submit differently-shaped (non-malicious) proofs to advance `latestHeight`.

### Likelihood Explanation
Trivial to trigger: any party who can call the consensus-proof submission path (an unsigned/permissionless ISMP message flow per `pallet_ismp`/`handle_unsigned` documentation) can supply a crafted `ParachainHeader.header` byte string with an inflated SCALE-compact digest count. No signatures, authority-set membership, or valid Merkle proof are required to reach the vulnerable allocation, since it executes before those checks.

### Recommendation
- In `Codec.DecodeHeader`, bound the decoded digest `length` against the remaining bytes in `slice` (e.g., `require(length <= (encoded.length - slice.offset))`) or impose an explicit protocol-level maximum digest count before calling `new Digest[](length)`.
- In `EcdsaBeefy.verifyParachainHeaderProof` (and the analogous loop in `SP1Beefy.verifyConsensus`), reorder verification so `MerkleMultiProof.VerifyProof`/the SP1 proof check authenticates `para.header` bytes before `Codec.DecodeHeader` is called on them, so unauthenticated attacker bytes are never decoded.

### Proof of Concept
1. Construct a `ParachainProof` with one `Parachain{ header: bytes }` entry.
2. Set `header` to: 32 bytes parent hash + a valid compact block number + 32 bytes state root + 32 bytes extrinsics root + a SCALE compact integer encoding a large digest count (e.g., mode `3`, encoding a value in the hundreds of thousands), with no further bytes required to trigger the allocation.
3. Submit this as `proof` to `EcdsaBeefy.verify(previousState, proof)` (or via the higher-level consensus message dispatch that invokes it) with any (or maximum) gas limit.
4. Observe that `Codec.DecodeHeader` reverts with out-of-gas at `Digest[] memory digests = new Digest[](length);` (`evm/src/consensus/Codec.sol:79`), before `MerkleMultiProof.VerifyProof` in `EcdsaBeefy.verifyParachainHeaderProof` (`evm/src/consensus/EcdsaBeefy.sol:224`) is ever reached — i.e., the call fails via unbounded-allocation OOG rather than the intended proof-validity check.

### Citations

**File:** evm/src/consensus/Codec.sol (L78-79)
```text
        uint256 length = ScaleCodec.decodeUintCompact(slice);
        Digest[] memory digests = new Digest[](length);
```

**File:** evm/src/consensus/Codec.sol (L112-122)
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
```

**File:** evm/src/consensus/EcdsaBeefy.sol (L204-226)
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

        if (len > 0) {
            bool valid = MerkleMultiProof.VerifyProof(headsRoot, proof.proof, leaves, proof.leafCount);
            if (!valid) revert InvalidMmrProof();
        }
```
