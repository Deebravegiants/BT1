## Title
Unbounded digest-count trusted without validation against actual header bytes causes uncontrolled resource consumption in BEEFY header decoding - (`evm/src/consensus/Codec.sol`)

### Summary
`Codec.DecodeHeader` reads a SCALE compact-encoded "number of digest items" field from an untrusted, attacker-supplied parachain header byte string and immediately uses it to size a memory array and drive a decoding loop, without first checking that the declared count is consistent with the actual remaining bytes in the buffer. This mirrors ALPINE-CVE-2018-5784 (LibTIFF `TIFFSetDirectory`), where a declared directory-entry count was trusted without validation against the real number of entries, leading to uncontrolled resource consumption.

### Finding Description
`DecodeHeader` decodes the digest count via `ScaleCodec.decodeUintCompact(slice)` and immediately allocates and loops: [1](#0-0) 

`decodeUintCompact`'s mode-3 branch can return values up to `2^53`-ish magnitudes read straight from a single caller-controlled byte prefix, with no upper bound tied to `encoded.length`: [2](#0-1) 

`new Digest[](length)` therefore attempts to allocate memory sized by this unvalidated, attacker-chosen `length` before any per-item read even happens; the only bounds-checks that exist (`require` in `read`/`readByte`) fire per-byte inside the loop, not against the declared count up front: [3](#0-2) 

This is reached from an unprivileged relayer's consensus-proof submission: both `EcdsaBeefy.verify` and `SP1Beefy.verify` call `Codec.DecodeHeader` on every `para.header` in the submitted proof *before* the merkle/ZK proof that would authenticate those header bytes is checked: [4](#0-3) [5](#0-4) 

### Impact Explanation
Any unprivileged relayer submits `RelayChainProof`/`ParachainProof` (Ecdsa path) or the ABI-encoded `SP1BeefyProof` (SP1 path) as plain calldata — these header bytes are attacker-chosen and are decoded *before* their authenticity is verified against `headsRoot` or the SP1 proof. A single crafted `para.header` entry with an inflated digest-count prefix forces an oversized memory allocation / unbounded loop attempt that exhausts gas and reverts the whole call. Because `verifyParachainHeaderProof`/`verifyConsensus` process the *entire* batch of parachain headers atomically, one poisoned header can be interleaved with otherwise legitimate, correctly-finalized parachain state commitments in the same batch, causing the whole consensus update (and therefore delivery of the bundled intermediate states used for message/state proofs) to fail. This is denial-of-service against the BEEFY consensus-update path rather than fund theft — Medium severity, consistent with the CVE's own rating.

### Likelihood Explanation
Likelihood is limited by the fact that a malicious header must still be an entry the attacker fully controls the bytes of; it does not corrupt legitimate finalized headers. It is a griefing vector against relayers/consensus updates that batch multiple parachain headers per proof, rather than a way to steal funds or forge state directly.

### Recommendation
Bound the declared digest count against the remaining bytes in the slice before allocating (`require(length <= (slice.data.length - slice.offset))` at minimum, plus an absolute sanity cap), and/or cap `decodeUintCompact` results used as allocation sizes to a small maximum consistent with realistic Substrate header digest counts.

### Proof of Concept
1. Construct a `Parachain`/`ParachainHeader` entry whose `header` bytes are: 32-byte parentHash + compact blockNumber + 32-byte stateRoot + 32-byte extrinsicsRoot + a compact-encoded digest count using mode-3 encoding with a very large value (e.g., bytes `0x0303 0303 0303 0303`-style prefix decoding to a huge `length`), followed by only a few real bytes.
2. Submit this as one element of a multi-header `ParachainProof.parachains` array (Ecdsa) or `SP1BeefyProof.headers` (SP1), alongside otherwise valid headers/signatures.
3. Call `EcdsaBeefy.verify` / `SP1Beefy.verify`; `Codec.DecodeHeader` for the poisoned entry executes `new Digest[](length)` with the inflated `length`, exhausting gas and reverting the transaction before the merkle/ZK check ever runs, blocking delivery of the batch's other, legitimate intermediate states.

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

**File:** evm/src/consensus/Codec.sol (L112-132)
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

    /// @dev Reads a single byte from the slice at the current offset and advances the cursor.
    function readByte(ByteSlice memory self) internal pure returns (uint8) {
        require(self.offset + 1 <= self.data.length);

        uint8 b = uint8(self.data[self.offset]);
        self.offset += 1;

        return b;
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

**File:** evm/src/consensus/EcdsaBeefy.sol (L198-226)
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
```

**File:** evm/src/consensus/SP1Beefy.sol (L136-168)
```text
        uint256 headers_len = proof.headers.length;
        ParachainHeaderHash[] memory headers = new ParachainHeaderHash[](headers_len);
        for (uint256 i = 0; i < headers_len; i++) {
            headers[i] = ParachainHeaderHash({
                id: proof.headers[i].id,
                hash: keccak256(proof.headers[i].header)
            });
        }

        bytes memory publicInputs = abi.encode(
            PublicInputs({
                authorities_len: authority.len,
                authorities_root: authority.root,
                headers: headers,
                block_number: commitment.blockNumber,
                leaf_hash: keccak256(Codec.Encode(proof.mmrLeaf)),
                nonce: proof.nonce
            })
        );
        verifier.verifyProof(verificationKey, publicInputs, proof.proof);

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
