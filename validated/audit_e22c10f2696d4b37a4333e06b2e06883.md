Confirmed: `verify()` requires a valid supermajority of ECDSA signatures over the BEEFY commitment before `verifyParachainHeaderProof` (and hence `Codec.DecodeHeader`) is ever reached — `verifyMmrUpdateProof` performs the `ECDSA.recover` + `MerkleMultiProof.VerifyProof` check against the trusted authority set first, and only its returned `headsRoot` feeds into `verifyParachainHeaderProof`. So the header-decode call sits *after* signature/authority verification, not before it. The genuinely unauthenticated input at the decode point is only the `Parachain[].header` bytes themselves (each header's inclusion in `headsRoot` is checked only *after* `Codec.DecodeHeader` runs on it in the loop), meaning a relayer holding a legitimate valid BEEFY commitment can still smuggle an arbitrary, unauthenticated `para.header` blob into `DecodeHeader` and force an oversized `Digest[]` allocation before the Merkle inclusion check catches the forged header.

### Title
Unbounded digest-count allocation in `Codec.DecodeHeader` allows gas-exhaustion DoS on BEEFY parachain-header verification - (File: evm/src/consensus/Codec.sol)

### Summary
`Codec.DecodeHeader` reads a SCALE compact-encoded digest count directly from untrusted header bytes and immediately allocates a Solidity memory array of that size, with no upper bound check, before the header content is authenticated against the MMR/parachain-heads Merkle root.

### Finding Description
`DecodeHeader` decodes `length` via `ScaleCodec.decodeUintCompact(slice)` and immediately does `Digest[] memory digests = new Digest[](length);` [1](#0-0) . `decodeUintCompact` places no ceiling on the returned value — SCALE compact mode 2 alone can encode values up to `1,073,741,823` in just 4 bytes [2](#0-1) .

`DecodeHeader` is invoked inside `verifyParachainHeaderProof`'s loop over `proof.parachains[i].header` *before* that header's Merkle-multi-proof membership in `headsRoot` is checked (the `MerkleMultiProof.VerifyProof` call happens only after the loop completes) [3](#0-2) . The same unguarded call exists in the SP1 variant, decoding `proof.headers[i].header` directly from calldata as well [4](#0-3) .

This mirrors the phpseclib ASN1 bug class exactly: a length field parsed straight out of untrusted, not-yet-authenticated bytes is used to size an allocation with no bound, so a crafted length triggers pathological memory-expansion cost before the data's authenticity is checked.

### Impact Explanation
Any relayer that can produce (or replay) one valid BEEFY commitment with a legitimate supermajority signature set can pair it with a `ParachainProof` whose `header` field is *not* the real chain header but a short, crafted blob encoding a huge digest count (e.g. via SCALE compact mode 2, ~4 bytes suffice for over a billion). Solidity's memory-expansion gas cost grows quadratically, so `new Digest[](length)` for such a count will exhaust the block gas limit and revert the entire consensus-update transaction — deterministically, for a nearly-free crafted input, on every submission attempt using that forged header. Because this occurs before the Merkle inclusion check, an attacker doesn't need the forged header to actually correspond to any finalized parachain block. This is a targeted denial-of-service on the BEEFY consensus-update path (`EvmHost`/`HandlerV2` message delivery relies on this consensus client staying updatable) — it can be used to grief/waste gas of anyone attempting to relay parachain headers alongside a given commitment, though it does not by itself corrupt state, since the transaction simply reverts and does not persist a bad `trustedState`.

### Likelihood Explanation
Medium. Exploitation requires the attacker to have (or intercept/replay) an otherwise-valid signed BEEFY commitment — this is not fully permissionless since forging authority signatures is not possible, but a relayer who already possesses a legitimate commitment (which is public information broadcast by any relay-chain full node) can freely attach malicious `header` bytes to the `ParachainProof` array, since nothing authenticates those bytes prior to `DecodeHeader`.

### Recommendation
Bound the digest length read in `Codec.DecodeHeader` (and any other `decodeUintCompact`-driven array size) against the remaining bytes in the slice or a sane maximum before allocating, e.g. `require(length <= slice.data.length - slice.offset)` before `new Digest[](length)`, and/or move the Merkle-proof membership check for each `para.header` before decoding its contents in `verifyParachainHeaderProof` / `SP1Beefy.verifyConsensus`.

### Proof of Concept
1. Obtain any legitimately signed BEEFY commitment (`RelayChainProof`) that meets the supermajority threshold for the current trusted authority set — no privileged access needed, these are public.
2. Construct a `ParachainProof.parachains[0].header` byte string consisting of: 32 bytes parent hash + compact-encoded block number + 32 bytes state root + 32 bytes extrinsics root + a SCALE compact-mode-2 length field encoding `1_000_000_000` (4 bytes) — no further trailing data is needed, since the huge `new Digest[](length)` allocation itself triggers gas exhaustion before any further byte reads occur.
3. Call `EcdsaBeefy.verify(previousState, abi.encode(relay, parachain))` with this crafted proof.
4. Observe the transaction revert with an out-of-gas condition inside `Codec.DecodeHeader`, before `MerkleMultiProof.VerifyProof` ever runs to reject the bogus header — confirming the allocation-before-authentication ordering.

### Citations

**File:** evm/src/consensus/Codec.sol (L78-79)
```text
        uint256 length = ScaleCodec.decodeUintCompact(slice);
        Digest[] memory digests = new Digest[](length);
```

**File:** evm/src/consensus/Codec.sol (L150-161)
```text
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

**File:** evm/src/consensus/SP1Beefy.sol (L157-168)
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
