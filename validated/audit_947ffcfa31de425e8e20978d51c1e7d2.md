### Title
Out-of-bounds/short-read of ISMP consensus digest data in `HeaderImpl.stateCommitment` via `Bytes.substr` on attacker-supplied parachain header digest — (File: `evm/src/consensus/Types.sol`)

### Summary
`HeaderImpl.stateCommitment` reads a BEEFY/SP1-supplied, SCALE-decoded parachain header's `ISMP` consensus digest and slices it with `Bytes.substr(data, 0, 32)` and `Bytes.substr(data, 32)` to extract the MMR root and child-trie root, with no check that `data.length >= 64` before slicing. [1](#0-0) 

### Finding Description
The digest's `data` field is decoded by `Codec.decodeDigestItem`, which reads exactly the length prefix embedded in the untrusted proof bytes (`ScaleCodec.decodeUintCompact` then `Bytes.read(slice, length)`), so an attacker fully controls both the content and the length of `consensus.data` for a digest tagged with consensus id `ISMP` (`bytes4("ISMP")`). [2](#0-1)  `stateCommitment` then unconditionally does `Bytes.substr(self.digests[j].consensus.data, 0, 32)` and `Bytes.substr(self.digests[j].consensus.data, 32)` for any digest whose `consensusId == ISMP_CONSENSUS_ID`, without ever validating `data.length == 64`. [3](#0-2)  This is the same bug class as CVE-2017-15021: a fixed-size, offset-based read of an attacker-supplied length-prefixed blob without validating that the blob is long enough to satisfy the read, which upstream (`bfd_get_debug_link_info_1`/`bfd_getl32`) caused a heap buffer over-read/crash on a crafted ELF section.

This code path is reachable directly from `EcdsaBeefy.verifyParachainHeaderProof` and `SP1Beefy.verifyConsensus`, both of which call `Codec.DecodeHeader(para.header)` on relayer-submitted parachain headers and then `header.stateCommitment()` — i.e., any unprivileged relayer submitting a BEEFY/SP1 consensus proof controls the raw header bytes, hence the digest bytes, end to end. [4](#0-3) [5](#0-4) 

Whether `Bytes.substr` in the external `@polytope-labs/solidity-merkle-trees` library reverts safely on a short `data` (< 64 bytes) or instead reads adjacent/out-of-bounds memory could not be confirmed from this repository — that library's source is not indexed here, so the precise memory-safety consequence (revert vs. actual out-of-bounds memory read/garbage value) is unverified.

### Impact Explanation
If `Bytes.substr` reverts cleanly on a too-short slice, the practical effect is a denial-of-service: a malicious relayer can craft a parachain header whose `ISMP` digest has `data.length < 64`, causing `stateCommitment()` to always revert for that header and therefore for any BEEFY/SP1 consensus proof batch containing it, blocking delivery of that parachain's state commitments (a "route unable to deliver messages" condition). If instead `Bytes.substr` silently returns truncated/garbage bytes (undefined based on the unavailable library source), a short digest could produce an incorrect `mmrRoot`/`childTrieRoot` pair that is accepted as a valid `StateCommitment`, which is a state-commitment integrity issue that could feed forged state roots into downstream message/relayer verification.

### Likelihood Explanation
Medium-High: no privileged role is required — any relayer/prover submitting a BEEFY (`EcdsaBeefy`) or SP1 (`SP1Beefy`) consensus update controls the raw parachain header bytes that flow into `Codec.decodeDigestItem` and then `stateCommitment()`; the SCALE length prefix on the digest data is entirely attacker-chosen and unvalidated against the 64-byte requirement before slicing.

### Recommendation
In `HeaderImpl.stateCommitment` (`evm/src/consensus/Types.sol`), before slicing the `ISMP` consensus digest, explicitly require `self.digests[j].consensus.data.length == 64` (or `>= 64`) and revert with a typed error otherwise, mirroring the existing `TimestampNotFound()` sanity check pattern already present in the function.

### Proof of Concept
1. As an unprivileged relayer, construct a SCALE-encoded parachain header whose digest list includes a `DIGEST_ITEM_CONSENSUS` entry with `consensusId = bytes4("ISMP")` and a data payload shorter than 64 bytes (e.g., 0 or 32 bytes), using `Codec.decodeDigestItem`'s length-prefix format so it decodes successfully.
2. Submit this header inside a `ParachainProof`/`SP1BeefyProof` to `EcdsaBeefy.verify` or `SP1Beefy.verify`.
3. Observe that `Codec.DecodeHeader` succeeds (the digest item is well-formed per SCALE rules) and `header.stateCommitment()` proceeds to call `Bytes.substr(consensus.data, 0, 32)` / `Bytes.substr(consensus.data, 32)` on the short buffer — behavior (revert-as-DoS vs. reading beyond the buffer) depends on the external `Bytes.substr` implementation, which was not available to verify in this repository's index.

### Citations

**File:** evm/src/consensus/Types.sol (L211-224)
```text
    function stateCommitment(Header memory self) internal pure returns (StateCommitment memory) {
        bytes32 mmrRoot;
        bytes32 childTrieRoot;
        uint256 timestamp;

        for (uint256 j = 0; j < self.digests.length; j++) {
            if (self.digests[j].isConsensus && self.digests[j].consensus.consensusId == ISMP_CONSENSUS_ID) {
                mmrRoot = Bytes.toBytes32(Bytes.substr(self.digests[j].consensus.data, 0, 32));
                childTrieRoot = Bytes.toBytes32(Bytes.substr(self.digests[j].consensus.data, 32));
            }

            if (self.digests[j].isConsensus && self.digests[j].consensus.consensusId == ISMP_TIMESTAMP_ID) {
                timestamp = ScaleCodec.decodeUint256(self.digests[j].consensus.data);
            }
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

**File:** evm/src/consensus/EcdsaBeefy.sol (L208-220)
```text
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
```

**File:** evm/src/consensus/SP1Beefy.sol (L159-167)
```text
        for (uint256 i = 0; i < statesLen; i++) {
            ParachainHeader memory para = proof.headers[i];
            Header memory header = Codec.DecodeHeader(para.header);
            if (header.number == 0) revert IllegalGenesisBlock();

            StateCommitment memory stateCommitment = header.stateCommitment();
            IntermediateState memory intermediate =
                IntermediateState({stateMachineId: para.id, height: header.number, commitment: stateCommitment});
            intermediates[i] = intermediate;
```
