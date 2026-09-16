## Title
Unbounded digest-count field in `Codec.DecodeHeader` allows gas-exhaustion DoS on unauthenticated parachain header data before merkle-proof verification - (File: `evm/src/consensus/Codec.sol`)

### Summary
`Codec.DecodeHeader` reads a SCALE compact-encoded digest count directly from attacker-supplied `bytes` and immediately allocates a memory array sized by that untrusted value, with no upper bound and no check that the underlying header bytes actually contain that many digest entries. `EcdsaBeefy.verifyParachainHeaderProof` calls this decoder on every submitted `para.header` *before* verifying that the header is even a member of the already-trusted `headsRoot` via the merkle multi-proof. This is the same bug class as ALPINE-CVE-2017-14056: a parser trusts a header-declared element count to drive an allocation/loop with no check against the real amount of backing data (no "EOF check"), letting a small malicious input trigger disproportionate resource consumption.

### Finding Description
`Codec.DecodeHeader` in [1](#0-0)  reads:
```
uint256 length = ScaleCodec.decodeUintCompact(slice);
Digest[] memory digests = new Digest[](length);
for (uint256 i = 0; i < length; i++) { ... }
```
`length` comes straight from `decodeUintCompact`, whose largest encoding mode can produce values up to `2^64` from as few as 5 extra bytes [2](#0-1) . Nothing bounds `length` against `slice.data.length` before the `new Digest[](length)` allocation.

`EcdsaBeefy.verifyParachainHeaderProof` invokes this decoder inside a loop over every submitted parachain header, and only checks the merkle multi-proof membership of those headers against the trusted `headsRoot` *after* all headers have been decoded:
```
for (uint256 i = 0; i < len; i++) {
    Parachain memory para = proof.parachains[i];
    Header memory header = Codec.DecodeHeader(para.header);   // <-- decode first
    ...
    leaves[i] = MerkleMultiProof.Leaf(...);
}
if (len > 0) {
    bool valid = MerkleMultiProof.VerifyProof(headsRoot, proof.proof, leaves, proof.leafCount);  // <-- verified last
    if (!valid) revert InvalidMmrProof();
}
``` [3](#0-2) 

Because decoding happens before authentication, `para.header` bytes are fully attacker-controlled at decode time: any relayer calling `EcdsaBeefy.verify` (invoked from `ConsensusRouter`/`HandlerV2` for BEEFY-based routes, see the entry point) [4](#0-3)  can embed a header blob whose SCALE-compact digest-count field claims an enormous number of digest items, forcing Solidity to allocate a correspondingly huge `Digest[]` array. Solidity memory-expansion gas cost is quadratic in the number of words (`3*words + words^2/512`), so a small calldata payload can force gas consumption far out of proportion to its size, exactly mirroring the FFmpeg `rl2_read_header` pattern of trusting a claimed count with no check against actual backing data.

### Impact Explanation
Any single crafted `parachain.parachains[]` entry inside an otherwise-legitimate BEEFY consensus/parachain-header proof forces a huge, unbounded memory allocation before the entry's authenticity is ever checked. This can push the whole `verify()` call, and therefore the entire batched `handlePostRequests`/`handleGetResponses`/consensus-update transaction it's embedded in, to exceed the block gas limit, causing that route's consensus/message-delivery submission to permanently fail to execute (a route unable to deliver messages) unless the relayer can identify and strip the poison entry — which requires bypassing the very code path that is broken. This directly affects the unprivileged relayer/dispatch path used to advance consensus state and deliver ISMP requests/responses on EVM chains secured by the ECDSA BEEFY client.

### Likelihood Explanation
Any unprivileged party can submit a `verify(previousState, proof)` call (via the consensus router) with an attacker-chosen `ParachainProof.parachains[]` array; header bytes are raw calldata under full attacker control at decode time since no proof-membership check precedes the decode. Crafting a SCALE compact "mode 3" prefix that claims an outsized digest count costs only a handful of bytes, making the attack trivial and cheap to mount repeatedly against any relayer trying to submit legitimate parachain state updates.

### Recommendation
Bound the SCALE-decoded `length` in `Codec.DecodeHeader` against a sane maximum and/or against the number of bytes actually remaining in `slice`, mirroring the "EOF check" missing in the CVE. Additionally, reorder `verifyParachainHeaderProof` to verify each header's merkle multi-proof membership in `headsRoot` *before* calling `Codec.DecodeHeader` on its bytes, so unauthenticated header blobs are never parsed.

### Proof of Concept
1. Construct a `ParachainProof.parachains[0].header` byte string that is a validly-shaped header up through `extrinsicsRoot`, followed by a SCALE compact-int mode-3 prefix encoding a very large digest count (e.g., near `type(uint64).max`), with no actual digest bytes following.
2. Submit this as one entry of `ParachainProof.parachains` in an otherwise well-formed `verify(previousState, proof)` call (or via the router path that batches it with a legitimate delivery), along with the necessary `RelayChainProof` fields to pass `verifyMmrUpdateProof` and reach `verifyParachainHeaderProof`.
3. Observe that `Codec.DecodeHeader` allocates `new Digest[](length)` for the attacker-declared `length` before `MerkleMultiProof.VerifyProof` is ever invoked, consuming gas quadratic in `length` and reverting the transaction on out-of-gas — even though the crafted header was never a member of `headsRoot`.

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

**File:** evm/src/consensus/Codec.sol (L162-166)
```text
        } else if (mode == 3) {
            // [1073741824, 4503599627370496]
            uint8 l = (b >> 2) + 4; // remove mode bits
            require(l <= 8, "unexpected prefix decoding Compact<Uint>");
            return ScaleCodec.decodeUint256(read(data, l));
```

**File:** evm/src/consensus/EcdsaBeefy.sol (L94-114)
```text
    /// @dev IConsensusV2 entry point. Decodes the proof, verifies consensus, and returns
    /// the updated state along with the latest authority set id.
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
