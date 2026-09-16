### Title
Unbounded digest-count allocation in `Codec.DecodeHeader` from attacker-controlled parachain header bytes causes BEEFY consensus proof relaying to revert/DoS - (File: `evm/src/consensus/Codec.sol`)

### Summary
`Codec.DecodeHeader` reads a SCALE compact-encoded digest count directly from the untrusted parachain header bytes and immediately allocates a Solidity array of that size, with no check against the remaining bytes actually available in the header. Any unprivileged relayer submitting a BEEFY consensus proof controls this field and can force the EVM to attempt an out-of-bounds/oversized memory allocation, causing consensus proof processing for that state machine to revert. This is the same bug class as CVE-2017-6436 (libplist's `parse_string_node`, which trusted an attacker-controlled length field to drive a memory allocation without validating it against the actual data available).

### Finding Description
`DecodeHeader` reads a compact length and allocates an array of `Digest` structs sized by it before validating that the underlying byte slice actually contains that many digest items: [1](#0-0) 

`ScaleCodec.decodeUintCompact` can return values up to ~4.5 * 10^15 (mode-3 compact encoding), so `length` is fully attacker-controlled and unrelated to the actual size of `encoded`. `Digest[] memory digests = new Digest[](length)` then attempts to allocate this many structs in EVM memory before any subsequent read validates the byte slice has that much content — each iteration of the following loop calls `Bytes.readByte`/`Codec.read`, which do bound-check reads, but by then the array itself has already been allocated at the attacker-chosen size, and memory-expansion gas cost for a large `length` grows quadratically, making the call revert (out-of-gas) well before any of the per-item bound checks even execute.

`DecodeHeader` is invoked once per parachain header supplied in a `ParachainProof` from `verifyParachainHeaderProof`: [2](#0-1) 

which is reached from the `IConsensusV2` entry point `verify(bytes previousState, bytes proof)`, the function any relayer calls (via the host's consensus-update dispatch) to submit a new BEEFY consensus proof: [3](#0-2) 

Since `proof` (containing `ParachainProof.parachains[i].header`) is ABI-decoded from calldata supplied by the caller, an attacker fully controls the raw header bytes fed into `Codec.DecodeHeader`, including the digest-count compact integer.

### Impact Explanation
A malicious or unprivileged relayer can craft a `ParachainProof` whose embedded parachain header encodes a very large digest count, causing `new Digest[](length)` to attempt an oversized allocation. This reliably reverts the BEEFY consensus `verify()` call for that submission (denial of service on consensus-proof relaying), which in turn stalls delivery of any ISMP messages depending on that parachain's finalized state being updated on the destination `EvmHost`. Because `verify` is `pure` and stateless, this does not corrupt on-chain state, but it can be used to grief legitimate relayers by making their otherwise-valid consensus update transactions revert if attacker-controlled header content is mixed into the proof, and more importantly demonstrates that header parsing performs no sanity bound on a length field before committing to an allocation — a general decode-time DoS primitive reachable from any submitted consensus proof.

### Likelihood Explanation
Any address can call `verify` (directly or via the host's untrusted consensus-update path) with an arbitrary ABI-encoded `RelayChainProof`/`ParachainProof`, and crafting a header with an oversized compact digest-count prefix requires no special privileges or off-chain infrastructure — only knowledge of the SCALE header format, which is public.

### Recommendation
Bound the decoded `length` in `DecodeHeader` against the remaining bytes in `encoded` (e.g., `require(length <= (encoded.length - slice.offset))` or a fixed sane maximum digest count) before allocating the `Digest[]` array, mirroring the length-vs-available-data check that `libimobiledevice/libplist` added in its fix for CVE-2017-6436 (commit `32ee5213`).

### Proof of Concept
1. Construct a `ParachainProof.parachains[0].header` byte string consisting of: 32-byte parent hash, a valid compact block number, 32-byte state root, 32-byte extrinsics root, followed by a compact-encoded digest count using mode-3 encoding to specify an extremely large value (e.g., close to `2^53`).
2. Submit this as part of a `BeefyConsensusProof`/`ParachainProof` to `EcdsaBeefy.verify(previousState, proof)` (or through the host's consensus-update path that forwards to it).
3. Execution reaches `Codec.DecodeHeader` → `ScaleCodec.decodeUintCompact` returns the attacker-chosen huge value → `new Digest[](length)` triggers excessive memory-expansion gas cost, causing the transaction to run out of gas and revert before any subsequent bounds-checked read on the digest data occurs.

### Citations

**File:** evm/src/consensus/Codec.sol (L77-99)
```text

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

**File:** evm/src/consensus/EcdsaBeefy.sol (L96-114)
```text
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

**File:** evm/src/consensus/EcdsaBeefy.sol (L204-211)
```text
        uint256 len = proof.parachains.length;
        MerkleMultiProof.Leaf[] memory leaves = new MerkleMultiProof.Leaf[](len);
        IntermediateState[] memory intermediates = new IntermediateState[](len);

        for (uint256 i = 0; i < len; i++) {
            Parachain memory para = proof.parachains[i];
            Header memory header = Codec.DecodeHeader(para.header);
            if (header.number == 0) revert IllegalGenesisBlock();
```
