### Title
Unhandled reserved/unknown SCALE `DigestItem` kind byte desyncs the BEEFY header decoder, allowing a relayer-submitted consensus proof to corrupt or crash header parsing - (File: `evm/src/consensus/Codec.sol`)

### Summary
`Codec.DecodeHeader` parses a SCALE-encoded Substrate header supplied inside a BEEFY consensus proof. For each digest item it reads a 1-byte `kind` discriminant and only branches on five known values (`DIGEST_ITEM_OTHER=0`, `CONSENSUS=4`, `SEAL=5`, `PRERUNTIME=6`, `RUNTIME_ENVIRONMENT_UPDATED=8`). Any other byte value (the SCALE-reserved/undefined region) falls through without consuming the payload that a genuine (or adversarial) digest item of that kind would carry, exactly as CVE-2016-5353 describes Wireshark's UMTS FP dissector mishandling a reserved C/T field value and crashing on malformed input.

### Finding Description
```solidity
for (uint256 i = 0; i < length; i++) {
    uint8 kind = Bytes.readByte(slice);
    Digest memory digest;
    if (kind == DIGEST_ITEM_OTHER) {
        digest.isOther = true;
    } else if (kind == DIGEST_ITEM_CONSENSUS) {
        digest.isConsensus = true;
        digest.consensus = decodeDigestItem(slice);
    } else if (kind == DIGEST_ITEM_SEAL) {
        ...
    } else if (kind == DIGEST_ITEM_PRERUNTIME) {
        ...
    } else if (kind == DIGEST_ITEM_RUNTIME_ENVIRONMENT_UPDATED) {
        digest.isRuntimeEnvironmentUpdated = true;
    }
    digests[i] = digest;
}
``` [1](#0-0) 

Every branch except `DIGEST_ITEM_OTHER`/`RUNTIME_ENVIRONMENT_UPDATED` advances the cursor by reading a length-prefixed payload (`decodeDigestItem`, which reads a 4-byte engine id plus a compact-length-prefixed byte vector) [2](#0-1) . If `kind` is any value outside the five handled constants, none of the branches execute and the loop advances to `digests[i] = digest` without reading the bytes that the real header actually encodes for that digest item's payload. The cursor (`slice.offset`) is now desynchronized from the true SCALE layout for every subsequent digest item and for the remainder of the header — all later reads (`Bytes.read`, `readByte`, `decodeUintCompact`) operate on the wrong bytes.

This header decoder is invoked from the on-chain BEEFY light-client verification path (`EcdsaBeefy.sol` / `SP1Beefy.sol` both call `Codec.DecodeHeader`) as part of processing a relayer-submitted consensus/finality proof — i.e., a value fully attacker-controlled by any unprivileged relayer who submits a BEEFY update to `EvmHost`.

### Impact Explanation
A single malformed/adversarial digest kind byte in the header bytes of a submitted consensus proof desynchronizes the SCALE cursor. Because subsequent `Bytes.read`/`readByte` calls use `require(self.offset + len <= self.data.length)` [3](#0-2) , the most likely outcome is that the offset runs past the buffer and the transaction reverts — a denial-of-service that prevents legitimate consensus updates from being processed if a relayer (malicious or simply buggy) ever submits a header containing a non-standard digest kind, effectively making the BEEFY light-client route unable to deliver messages for that update. In less likely but more severe cases, the misaligned read could cause downstream fields (state root, digests used for the ISMP overlay-root digest) to be misinterpreted, since the loop keeps going with a shifted cursor and stores a `Digest` that doesn't reflect what was actually encoded.

### Likelihood Explanation
Reaching this path requires only submitting a BEEFY consensus update whose embedded parachain/relay header contains a digest item with an unrecognized `kind` byte — something any relayer can construct, since digest kind bytes beyond the five hardcoded constants are never rejected before parsing. Real Substrate runtimes can and do emit additional digest kinds (e.g., custom consensus engines), so this is not purely an adversarial-only path — a legitimately different chain configuration could trigger it too, but a deliberately malicious relayer can trivially craft it to force a revert or corrupt parsing on demand.

### Recommendation
Add an explicit `else` branch (or an upfront known-kind check) in `Codec.DecodeHeader`'s digest loop that rejects any `kind` not in the handled set with a clear revert, or — matching Substrate's own digest encoding — always decode the item as `(4-byte engine id, compact-length-prefixed data)` regardless of kind so the cursor stays correctly aligned even for unknown/reserved kinds, then classify it as "other" for kinds not otherwise needed by the verifier.

### Proof of Concept
1. Construct a SCALE-encoded Substrate header whose digest log contains one item with `kind = 7` (or any byte not in {0,4,5,6,8}) followed by bytes that, under the real encoding, would be a 4-byte engine id + compact-length + payload.
2. Wrap it into a BEEFY (or SP1Beefy) consensus proof and submit it via the public consensus-update entry point that eventually calls `Codec.DecodeHeader`.
3. Observe the loop skips consuming the digest's payload bytes, causing either a `require` revert in a later `Bytes.read`/`readByte` call (transaction reverts, consensus update fails) or a subsequent digest/root field to be parsed from the wrong offset.

### Citations

**File:** evm/src/consensus/Codec.sol (L78-99)
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

**File:** evm/src/consensus/Codec.sol (L112-120)
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
```
