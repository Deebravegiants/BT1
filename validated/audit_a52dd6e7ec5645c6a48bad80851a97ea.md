## Title
Uncontrolled Memory Allocation in BEEFY Header Decoder via Unvalidated SCALE Digest Count - (File: `evm/src/consensus/Codec.sol`)

### Summary
`Codec.DecodeHeader` allocates a `Digest[]` array sized directly from an attacker-controlled SCALE compact-encoded integer read out of the raw parachain header bytes, with no bound check against the actual size of the supplied header blob. This mirrors the reported Ghidra Mach-O bug class: a length/count field taken from untrusted input drives a heap/memory allocation before the input's size or authenticity is validated.

### Finding Description
`Codec.DecodeHeader` decodes the digest count directly from the header bytes and immediately allocates an array of that size: [1](#0-0) 

The count comes from `ScaleCodec.decodeUintCompact`, whose "mode 3" encoding lets a handful of input bytes express a value up to `2^64`: [2](#0-1) 

Critically, this decode is invoked from `EcdsaBeefy.verifyParachainHeaderProof` (and the equivalent path in `SP1Beefy`) *before* the header bytes are authenticated against `headsRoot`. The Merkle multi-proof check that would confirm the header bytes are genuine relay-chain-committed data happens only after the whole loop has already decoded every `para.header`: [3](#0-2) 

Because `verify()` first validates the *relay-chain* MMR/BEEFY commitment (real validator signatures, which are public and freely reusable by any relayer) but only afterwards uses the resulting `headsRoot` to check parachain header authenticity, an attacker can pair a legitimate, already-public signed BEEFY commitment with an arbitrary, self-crafted `ParachainProof.parachains[i].header` blob. That blob is fully attacker-controlled at the point `Codec.DecodeHeader` runs, so the digest-count field can be set to an enormous value (e.g. `2^32`+), forcing `new Digest[](length)` to attempt an allocation whose size bears no relation to the actual (small) header buffer supplied.

### Impact Explanation
Because EVM memory expansion cost is quadratic, `new Digest[](length)` with an attacker-chosen large `length` drives gas consumption to unreasonable levels, forcing the transaction to run out of gas and revert well before the subsequent bounds-checked `Bytes.read` calls would ever catch the malformed digest. This is directly analogous to the Ghidra Mach-O `ncmds` bug: a size field taken from untrusted data drives allocation before the data's real size is checked. It allows any permissionless relayer/caller of the BEEFY consensus client's `verify()` entrypoint to force a denial-of-service revert on that consensus-update transaction using only publicly available commitment data plus a self-crafted parachain header payload, without needing to forge any signatures.

### Likelihood Explanation
`verify()` on `EcdsaBeefy`/`SP1Beefy` is reachable by any address that can submit a consensus update through the `ConsensusRouter`/`EvmHost` path, and the only "hard" precondition (a validly signed BEEFY commitment) is public, replayable data — not secret or hard to obtain. Crafting the oversized digest-count field requires only a few bytes of attacker-controlled data. Likelihood is therefore high for any actor willing to submit such a transaction, though the practical effect is limited to reverting that specific update rather than corrupting persisted state (`verify` is `pure`/`view` and does not mutate storage before reverting).

### Recommendation
Validate the decoded digest count (and any other length-prefixed field) against the remaining bytes in the slice *before* allocating the `Digest[]` array in `Codec.DecodeHeader`, e.g. require `length <= (slice.data.length - slice.offset)` (with a reasonable per-item minimum size) prior to `new Digest[](length)`, mirroring the fix pattern of validating a stated element count against actual file/buffer size before allocating.

### Proof of Concept
1. Obtain any currently valid, already-published BEEFY signed commitment/MMR proof for the target consensus state (public information any relayer already has).
2. Construct a `ParachainProof` whose `parachains[0].header` is a short byte string beginning with a SCALE compact-encoded digest-length field using the "mode 3" 8-byte encoding to express a large count (e.g., `0xFF...` bytes decoding to `~2^32`), followed by no actual digest data.
3. Submit this pair to `EcdsaBeefy.verify` (or `SP1Beefy.verify`) via the standard consensus-update entrypoint.
4. `verifyMmrUpdateProof` succeeds (the commitment/signatures are genuine), then `verifyParachainHeaderProof` calls `Codec.DecodeHeader(para.header)`, which executes `new Digest[](length)` with the inflated `length` before the header is checked against `headsRoot`, causing excessive memory-expansion gas cost and an out-of-gas revert — well before the (unreachable) `InvalidMmrProof` check that would have rejected the fabricated header.

### Citations

**File:** evm/src/consensus/Codec.sol (L77-80)
```text

        uint256 length = ScaleCodec.decodeUintCompact(slice);
        Digest[] memory digests = new Digest[](length);

```

**File:** evm/src/consensus/Codec.sol (L162-166)
```text
        } else if (mode == 3) {
            // [1073741824, 4503599627370496]
            uint8 l = (b >> 2) + 4; // remove mode bits
            require(l <= 8, "unexpected prefix decoding Compact<Uint>");
            return ScaleCodec.decodeUint256(read(data, l));
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
