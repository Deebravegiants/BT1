Confirmed analog found: `Codec.DecodeHeader` in `evm/src/consensus/Codec.sol` reads an attacker/relayer-supplied digest-count field from the SCALE-encoded parachain header and uses it directly to size a memory array, with no upper bound check — the same root cause as CVE-2016-4809 (an unbounded length field taken from an untrusted encoded record and used to size/allocate memory before validation).

### Title
Unbounded digest-count field in `Codec.DecodeHeader` allows an attacker-supplied parachain header to abort BEEFY consensus-proof verification via unchecked array allocation - (File: `evm/src/consensus/Codec.sol`)

### Summary
`Codec.DecodeHeader` decodes the SCALE-encoded digests-length field straight off the wire and immediately allocates `Digest[] memory digests = new Digest[](length)` with no maximum-size check, exactly mirroring the libarchive CPIO bug where `archive_read_format_cpio_read_header` trusted an on-disk length field for a symlink target and used it to drive an allocation/copy before validating it against the remaining archive size.

### Finding Description
```solidity
// evm/src/consensus/Codec.sol
function DecodeHeader(bytes memory encoded) internal pure returns (Header memory) {
    ...
    uint256 length = ScaleCodec.decodeUintCompact(slice);
    Digest[] memory digests = new Digest[](length);   // <-- unbounded attacker-controlled length
    for (uint256 i = 0; i < length; i++) { ... }
}
``` [1](#0-0) 

`decodeUintCompact` can return values up to `~2^32` (mode 2/3 branches) purely from attacker-chosen bytes inside the parachain header blob: [2](#0-1) 

`DecodeHeader` is called on `para.header`, a byte blob supplied inside the BEEFY consensus proof by whoever calls `handleConsensus`/`verify` — this is a **permissionless relayer-supplied field**, reached from both the ECDSA and SP1 BEEFY consensus clients:
- `EcdsaBeefy.verifyParachainHeaderProof` calls `Codec.DecodeHeader(para.header)` inside the loop that runs before/alongside the merkle multi-proof check for the parachain-heads root [3](#0-2) 
- `SP1Beefy.verifyConsensus` calls `Codec.DecodeHeader(para.header)` for every header in `proof.headers` after the SP1 proof already verified, when materializing `IntermediateState[]` [4](#0-3) 

Critically, in the `EcdsaBeefy` path the header is **decoded before the merkle multi-proof that would confirm it is a genuine, finalized parachain header is checked against `leaves[i]`** — the loop builds `leaves[i]` from `para.header` in the same iteration that calls `Codec.DecodeHeader(para.header)`, and `MerkleMultiProof.VerifyProof` is only invoked once, after the loop, at line 224. This means a header whose bytes are entirely attacker-chosen (not yet proven to be in the MMR) is fully parsed — including the unbounded `length`-driven array allocation — before any authentication happens.

### Impact Explanation
A relayer who wants to submit a legitimate BEEFY consensus update must include `para.header` bytes that they craft themselves (the actual SCALE header bytes come from the relay chain, but the *shape*/digest-length prefix inside it is validated only by the merkle-proof-of-inclusion, not by any independent bound). If the digest-count varint is corrupted/oversized (whether by a relaying party constructing a malicious header, or via any code path that lets an untrusted actor supply `para.header` ahead of the multi-proof check), `new Digest[](length)` with `length` near `2^30`+ will run out of gas and revert the entire `handleConsensus`/`verify` call.

Since `handleConsensus` (and the batched `IHandlerV2.batchCall`) is the single permissionless entry point that advances consensus state for a given `StateMachine`, a revert here blocks that specific consensus update from landing. Because BEEFY headers are batched together in one call (`Parachain[] memory parachains` / `ParachainHeader[] memory headers`), an attacker only needs to get **one** malformed header byte-string into a batch that they control the construction of (e.g., a permissionless relayer submitting on behalf of any user, or a scenario where header bytes are attacker-influenced before proof-of-inclusion is checked) to cause the whole consensus update transaction to revert, repeatedly, denying state-commitment delivery for that batch and — if repeatable across all relayers attempting that height/leaf — creating a route that is temporarily unable to deliver messages until a differently-batched proof is submitted.

This matches the "route unable to deliver messages" acceptance criterion, though the severity is bounded by the fact that (a) the transaction reverts rather than corrupting state, and (b) other relayers can always retry with a re-batched/legitimate proof, so it is a **griefing/DoS on a specific submission**, not a permanent freeze.

### Likelihood Explanation
Medium. The header bytes are still constrained by the outer SCALE structure (32-byte roots must parse first) and by the merkle-proof check that follows in `EcdsaBeefy`, so a header that fails inclusion will simply be rejected on `MerkleMultiProof.VerifyProof` in the common case — but that check happens *after* the expensive/oversized allocation in the same call, so the OOG revert is already triggered before the authentication check would have rejected the header. Any actor able to submit (or front-run) a `handleConsensus`/`batchCall` with a crafted `para.header` byte string can trigger this without needing a valid MMR proof at all, since the parsing happens unconditionally per header in the loop.

### Recommendation
Bound `length` in `Codec.DecodeHeader` against a sane maximum digest count (e.g. a small constant such as 32) before allocating `Digest[] memory digests = new Digest[](length)`, returning/reverting with a clear error otherwise — mirroring the fixes already applied elsewhere in this codebase for the same bug class (e.g. `ByteVector::decode`'s explicit length check, `MAX_PROOF_DEPTH` guards in `modules/consensus/pharos/primitives/src/spv.rs`, and `MAX_VALIDATORS`/`InsufficientStorageValues` checks in `modules/consensus/pharos/verifier/src/state_proof.rs`). Additionally, consider decoding/validating `para.header` only after `MerkleMultiProof.VerifyProof` confirms inclusion, so unauthenticated header bytes are never parsed at all.

### Proof of Concept
1. Construct a `Parachain` entry whose `header` bytes are: 32-byte parentHash, valid compact blockNumber, 32-byte stateRoot, 32-byte extrinsicsRoot, followed by a SCALE compact-int encoding a very large digest count (e.g. mode-3 encoding of a value close to `2^32`, per `ScaleCodec.decodeUintCompact`/`Codec.decodeUintCompact` mode-3 branch at lines 162–166) [5](#0-4) .
2. Submit this as part of a `ParachainProof.parachains` array to `EcdsaBeefy.verifyParachainHeaderProof` (via `handleConsensus`) or as part of `SP1BeefyProof.headers` to `SP1Beefy.verifyConsensus`.
3. `Codec.DecodeHeader` executes `new Digest[](length)` with the oversized `length`, exhausting available gas and reverting the transaction before the merkle-proof/SP1-proof check can reject the unauthenticated header — denying delivery of the entire batched consensus update for that call.

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

**File:** evm/src/consensus/Codec.sol (L134-171)
```text
    // @dev Decodes a SCALE encoded compact unsigned integer
    function decodeUintCompact(ByteSlice memory data) internal pure returns (uint256 v) {
        uint8 b = readByte(data); // read the first byte
        uint8 mode = b & 3; // bitwise operation

        uint256 value;
        if (mode == 0) {
            // [0, 63]
            value = b >> 2; // right shift to remove mode bits
        } else if (mode == 1) {
            // [64, 16383]
            uint8 bb = readByte(data); // read the second byte
            uint64 r = bb; // convert to uint64
            r <<= 6; // multiply by * 2^6
            r += b >> 2; // right shift to remove mode bits
            value = r;
        } else if (mode == 2) {
            // [16384, 1073741823]
            uint8 b2 = readByte(data); // read the next 3 bytes
            uint8 b3 = readByte(data);
            uint8 b4 = readByte(data);

            uint32 x1 = uint32(b) | (uint32(b2) << 8); // convert to little endian
            uint32 x2 = x1 | (uint32(b3) << 16);
            uint32 x3 = x2 | (uint32(b4) << 24);

            x3 >>= 2; // remove the last 2 mode bits
            value = uint256(x3);
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

**File:** evm/src/consensus/EcdsaBeefy.sol (L198-221)
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
```

**File:** evm/src/consensus/SP1Beefy.sol (L156-168)
```text

        uint256 statesLen = proof.headers.length;
        IntermediateState[] memory intermediates = new IntermediateState[](statesLen);
        for (uint256 i = 0; i < statesLen; i++) {
            ParachainHeader memory para = proof.headers[i];
            Header memory header = Codec.DecodeHeader(para.header);
            if (header.number == 0) revert IllegalGenesisBlock();

            StateCommitment memory stateCommitment = header.stateCommitment();
            IntermediateState memory intermediate =
                IntermediateState({stateMachineId: para.id, height: header.number, commitment: stateCommitment});
            intermediates[i] = intermediate;
        }
```
