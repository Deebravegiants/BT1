### Title
Unbounded digest-count field in `Codec.DecodeHeader` lets a single relayed BEEFY consensus proof force gigantic memory allocation / out-of-gas revert - (File: evm/src/consensus/Codec.sol)

### Summary
`Codec.DecodeHeader`, used by the ECDSA and SP1 BEEFY consensus clients to decode SCALE-encoded parachain headers supplied inside a permissionless consensus-update proof, reads the digest-item count as a raw SCALE compact integer and immediately allocates a `Digest[]` array of that size before any of the claimed digest items are actually consumed from the input. There is no upper bound check on this count relative to the remaining bytes in the header. This mirrors the CVE-2024-24814 bug class: an attacker-controlled integer field is used to size/iterate over expensive work before the input is validated, letting a tiny malicious payload trigger disproportionate resource consumption.

### Finding Description
`Codec.DecodeHeader` parses a header as: [1](#0-0) 

The digest count `length` comes straight from `ScaleCodec.decodeUintCompact(slice)`, a SCALE compact integer that can encode values up to roughly `2^64` using only a handful of bytes (mode 3 allows an 8-byte payload). Immediately after decoding, the code does `Digest[] memory digests = new Digest[](length);` and then loops `for (uint256 i = 0; i < length; i++)` calling `decodeDigestItem`, with no check that `length` is plausible given the remaining bytes in `data`.

`decodeUintCompact` itself has no cap either: [2](#0-1) 

`DecodeHeader` is invoked once per parachain header inside `EcdsaBeefy.verifyParachainHeaderProof`, which is directly reachable by any unprivileged relayer submitting a BEEFY consensus proof through `EcdsaBeefy.verify`: [3](#0-2) 

`SP1Beefy.sol` uses the same `Codec.DecodeHeader` path. Because the array is allocated before a single digest byte is validated against the actual header length, an attacker can supply a `para.header` blob containing only the mandatory prefix fields (parent hash, block number, state root, extrinsics root) plus a maliciously large compact-encoded digest count, and the EVM will attempt to allocate/zero-initialize a `Digest[]` of that size. Solidity/EVM memory-expansion gas cost grows quadratically with array size, so a modestly-sized calldata payload (well under normal proof sizes) can force the transaction to consume gas wildly disproportionate to its input size, in the same spirit as the Apache module accepting an oversized integer cookie value and doing excessive work before finally erroring out.

This differs from the well-bounded patterns seen elsewhere in the codebase (e.g., the Pharos SPV verifier explicitly caps proof depth with `MAX_PROOF_DEPTH` and rejects over-deep proofs before doing any walk, and `pallet-call-decompressor` gates the claimed decompressed size against `MaxCallSize` before doing any work): [4](#0-3) 
No equivalent bound exists for the BEEFY header digest count.

### Impact Explanation
Because `verifyParachainHeaderProof` iterates over every parachain header in a submitted BEEFY consensus proof and calls `Codec.DecodeHeader` on each one, a single relayer-submitted consensus update containing one maliciously crafted header can force the whole `verify()` call — which updates on-chain consensus state and delivers intermediate parachain state commitments for the entire batch — to blow through available gas and revert. This can be used to grief BEEFY-anchored routes (all Polkadot/Kusama parachain routes relying on `EcdsaBeefy`/`SP1Beefy`) by making legitimate consensus-state advancement proofs fail whenever a batch happens to need to include such a header, denying message delivery for that route until a workaround is found. Given the route-availability framing in the report scope ("a route unable to deliver messages"), this qualifies as a High severity denial-of-service.

### Likelihood Explanation
`verify()` on the BEEFY consensus clients is a fully permissionless entry point intended to be called by any relayer submitting consensus updates; constructing a header with a valid-but-oversized SCALE compact digest count requires no special privileges, no signatures, and minimal calldata — only crafting the `Header`/`Digest` prefix and the compact-encoded count.

### Recommendation
Bound the digest `length` in `Codec.DecodeHeader` against the remaining bytes in `data` (e.g., require `length <= data.length / MIN_DIGEST_ITEM_SIZE` or impose an explicit maximum digest count) before allocating the `Digest[]` array, and/or validate that the total encoded size implied by `length` does not exceed the remaining slice length prior to allocation — mirroring the `MAX_PROOF_DEPTH`-style bound already used in `modules/consensus/pharos/primitives/src/spv.rs`.

### Proof of Concept
1. Construct a minimal SCALE-encoded header: 32-byte parent hash, 1-byte compact block number, 32-byte state root, 32-byte extrinsics root.
2. Append a SCALE compact-encoded digest count using the mode-3 (8-byte) encoding to specify a value near `2^63`.
3. Wrap this header as `para.header` inside a `ParachainProof.parachains[0]` entry of an otherwise-minimal `RelayChainProof`/`ParachainProof` pair satisfying the earlier signature/authority checks (or targeting `verifyParachainHeaderProof` directly if reachable in isolation).
4. Call `EcdsaBeefy.verify(previousState, proof)`; `Codec.DecodeHeader` executes `new Digest[](length)` with the attacker-chosen huge `length`, causing gas consumption/memory-expansion cost far exceeding the calldata size and reverting the whole consensus-update transaction with out-of-gas.

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

**File:** modules/pallets/call-decompressor/src/lib.rs (L224-231)
```rust
		// Bound the claimed decompressed size against the configured maximum here,
		// at the single choke point every caller flows through. Previously this
		// gate lived only in `decompress_call` (the dispatch path); the unsigned
		// `validate_unsigned` mempool path called `decompress` directly with no
		// bound, so a fee-less attacker could claim `encoded_call_size = u32::MAX`
		// and have a tiny zstd "bomb" expanded to gigabytes during transaction-pool
		// validation, before any size check. Enforcing it here protects both paths.
		ensure!(encoded_call_size < T::MaxCallSize::get() * ONE_MB, Error::<T>::CallSizeOutOfBound);
```
