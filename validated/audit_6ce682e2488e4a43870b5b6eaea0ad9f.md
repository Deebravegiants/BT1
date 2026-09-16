## Title
Unbounded array allocation from attacker-controlled SCALE compact length in BEEFY parachain header decoding causes gas-exhaustion DoS - (File: evm/src/consensus/Codec.sol)

### Summary
`Codec.DecodeHeader`, used by `EcdsaBeefy.verifyParachainHeaderProof` (and `SP1Beefy`) to decode a Substrate parachain header from a submitted BEEFY consensus proof, reads a SCALE compact-encoded digest count directly off attacker-supplied bytes and immediately allocates a Solidity memory array sized to that value — with no upper bound check — before any subsequent byte is validated as actually present.

### Finding Description
`Codec.decodeUintCompact` decodes SCALE `Compact<uint>` values, including mode 3 which returns a value read via `decodeUint256(read(data, l))` for `l` up to 8 bytes [1](#0-0) . This lets an attacker encode an almost arbitrary 64-bit length using a handful of bytes.

`DecodeHeader` uses this decoded value directly as the size of a Solidity dynamic array allocation before consuming or validating any of the corresponding digest data: [2](#0-1) 

```solidity
uint256 length = ScaleCodec.decodeUintCompact(slice);
Digest[] memory digests = new Digest[](length);

for (uint256 i = 0; i < length; i++) {
```

This mirrors the reported veraPDF bug class exactly: a hardcoded allocation primitive (`array N` / `new Digest[](length)`) applied to an attacker-controlled length with no sanity bound, so a single small malicious input can force an enormous up-front allocation.

`DecodeHeader` is called for every parachain header inside a submitted BEEFY consensus proof, in `EcdsaBeefy.verifyParachainHeaderProof`, which is reached from the public, `pure` `IConsensusV2.verify` entry point invoked whenever any relayer submits a consensus update: [3](#0-2) 

The header bytes (`para.header`) are fully attacker-controlled proof payload; the only "check" on the digest count happens implicitly later when reads run out of bounds via `Bytes.read`'s `require`, but that guard fires only *after* the array has already been allocated at the attacker-chosen size [4](#0-3) .

### Impact Explanation
A relayer (an unprivileged, permissionless caller — anyone can submit a consensus proof to the ISMP host) can craft a BEEFY consensus proof containing a parachain header whose digest-count compact integer decodes to a very large number (e.g., close to `2^63`/`2^64`). `Codec.DecodeHeader` will attempt `new Digest[](length)`, which in the EVM either exhausts all available gas or reverts with an out-of-gas condition, consuming the caller's entire gas budget and failing the consensus-update transaction. Because this is `pure`/stateless and gas cost scales with the declared (not actual) array size, it is a low-cost, repeatable denial-of-service against the BEEFY light-client verification path used by `EcdsaBeefy`/`SP1Beefy` on the EVM `IsmpHost`, which can be used to grief consensus-update delivery and block state commitments from being accepted (a route unable to deliver messages/consensus updates).

### Likelihood Explanation
High. Exploitation requires only crafting a parachain header byte string with a single malformed compact-length prefix for the digest count and does not require any privileged role, valid signatures, or expensive computation — any address able to call the BEEFY consensus client's `verify` (via the ISMP host's consensus-update path) can trigger it. Solidity's `new T[](n)` for a large `n` fails deterministically via out-of-gas, so the attack is reliable and cheap relative to the disruption caused.

### Recommendation
Bound the decoded digest `length` in `Codec.DecodeHeader` against a sane maximum (e.g., the remaining bytes in `slice`, since each digest requires at minimum several bytes) before allocating the `Digest[]` array — for example, require `length <= (slice.data.length - slice.offset)` or enforce an explicit protocol-level maximum digest count, mirroring the pattern already used elsewhere in the codebase (e.g., `MAX_VALIDATORS`, `MAX_PROOF_DEPTH` bounds seen in `modules/consensus/pharos`).

### Proof of Concept
1. Construct `para.header` bytes for `EcdsaBeefy.verify`'s `ParachainProof` such that after the 32-byte `parentHash`, compact `blockNumber`, `stateRoot`, and `extrinsicsRoot`, the next SCALE compact integer (digest count) is encoded using mode-3 (4-byte prefix + up to 8 length bytes) to decode to a very large value (e.g. `0xFFFFFFFFFFFFFFFF`).
2. Submit this as part of a `RelayChainProof`/`ParachainProof` to `EcdsaBeefy.verify` (reached from the ISMP host's consensus-update dispatch for a permissionless relayer).
3. Execution reaches `Codec.DecodeHeader` at line `evm/src/consensus/Codec.sol:79`, which executes `Digest[] memory digests = new Digest[](length)` with the attacker-chosen huge `length`, causing the transaction to run out of gas before any digest is actually read or validated — denying the consensus update.

### Citations

**File:** evm/src/consensus/Codec.sol (L77-82)
```text

        uint256 length = ScaleCodec.decodeUintCompact(slice);
        Digest[] memory digests = new Digest[](length);

        for (uint256 i = 0; i < length; i++) {
            uint8 kind = Bytes.readByte(slice);
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
