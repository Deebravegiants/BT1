### Title
Unbounded memory allocation from unvalidated SCALE compact-length in `Codec.DecodeHeader` allows gas-exhaustion DoS of BEEFY/SP1 consensus verification - (File: `evm/src/consensus/Codec.sol`)

### Summary
`Codec.DecodeHeader` reads a SCALE compact-encoded digest count directly from attacker-supplied header bytes and uses it, unchecked, to size an in-memory array before any authentication of that header against the trusted MMR/parachain-heads root.

### Finding Description
`Codec.DecodeHeader` decodes the digest-item count via `ScaleCodec.decodeUintCompact(slice)` and immediately allocates `Digest[] memory digests = new Digest[](length)` with no upper bound on `length`: [1](#0-0) 

`decodeUintCompact`'s mode-3 branch can return a value derived from up to 8 attacker-controlled bytes (`decodeUint256(read(data, l))` with `l <= 8`), i.e. values up to ~2^64: [2](#0-1) 

Unlike `Codec.read`/`Codec.readByte`, which bound-check the cursor against `self.data.length`, the digest-count value used for allocation has no such bound check before the `new Digest[](length)` call, so a crafted header (only a handful of bytes) can request an array whose Solidity memory-expansion cost exceeds any realistic block gas limit, deterministically consuming all available gas and reverting the call.

Critically, `DecodeHeader` is invoked on `para.header` *before* that header is authenticated against the trusted BEEFY MMR/parachain-heads root: in `EcdsaBeefy.verifyParachainHeaderProof`, the header is decoded first, and only afterward is the corresponding leaf checked with `MerkleMultiProof.VerifyProof`: [3](#0-2) 

The same unauthenticated decode-before-verify pattern exists in the SP1 BEEFY consensus path: [4](#0-3) 

Both `EcdsaBeefy.verify` and `SP1Beefy`'s consensus update path are the `IConsensusV2` implementations invoked whenever a relayer submits a BEEFY/SP1 consensus proof through the permissionless `handleConsensus` entrypoint (also reachable via `IHandlerV2.batchCall`, which delegatecalls into the same handler logic for batched messages): [5](#0-4) 

This is directly analogous to CVE-2017-12143: an attacker-controlled length field taken from untrusted input data is used to drive a memory allocation without any sanity bound, causing the parser to fail/abort (here, via gas exhaustion) on a crafted input, rather than rejecting the malformed length up front.

### Impact Explanation
Because the decode occurs before the header is checked against the merkle multi-proof, an attacker does not need a real/valid parachain header — any bytes with a crafted compact-length prefix suffice to force the entire enclosing transaction (which may batch legitimate consensus updates and pending message deliveries via `batchCall`) to revert from gas exhaustion. This can be used to grief/DoS specific consensus-update or message-delivery submissions that include such headers, satisfying the "route unable to deliver messages" impact class, since the malformed header can be embedded in a `ParachainProof.parachains[]` entry processed ahead of its own authentication check.

### Likelihood Explanation
Triggering the allocation only requires crafting a `bytes` header whose SCALE `Compact<u32>`-encoded digest-length field decodes to a very large value (a handful of bytes) — no cryptographic material, signatures, or privileged access is needed, and the vulnerable code path executes unconditionally on every `DecodeHeader` call, for every parachain header entry in the proof, before proof-of-inclusion is checked.

### Recommendation
Bound the decoded digest count against a sane maximum (e.g. the remaining slice length divided by the minimum digest-item encoding size) before allocating `Digest[]` in `Codec.DecodeHeader`, and reject the proof early if the declared count cannot fit within the remaining bytes — mirroring the bounds-checking already applied in `Codec.read`/`Codec.readByte`. More generally, move merkle-membership verification of `para.header` ahead of `Codec.DecodeHeader` so unauthenticated bytes are never parsed with attacker-controlled length fields.

### Proof of Concept
1. Construct a `Parachain` proof entry whose `header` bytes are: 32 bytes parent hash + a small compact block number + 32 bytes state root + 32 bytes extrinsics root + a `Compact<u32>` digest-count prefix encoded in mode-3 form with all 8 length bytes set to `0xFF` (or another value that decodes to a huge count).
2. Submit this as part of a `ParachainProof.parachains[]` array to `EcdsaBeefy.verify` (or the SP1 equivalent) via the host's `handleConsensus`/`batchCall` entrypoint.
3. `Codec.DecodeHeader` executes `new Digest[](length)` with `length` in the billions/quintillions before the merkle multi-proof check runs, causing the call to exhaust gas and revert, regardless of whether the header is otherwise valid.

### Citations

**File:** evm/src/consensus/Codec.sol (L78-79)
```text
        uint256 length = ScaleCodec.decodeUintCompact(slice);
        Digest[] memory digests = new Digest[](length);
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

**File:** evm/src/consensus/EcdsaBeefy.sol (L199-226)
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

**File:** tesseract/messaging/evm/src/tx.rs (L335-353)
```rust
/// Build the per-message inner calldata array for an `IHandlerV2.batchCall`.
///
/// Each entry is an ABI-encoded HandlerV1 call (`handleConsensus`,
/// `handlePostRequests`) — `batchCall` delegatecalls
/// self so those selectors still dispatch correctly against HandlerV2.
async fn build_batch_inner_calls(
	client: &EvmClient,
	messages: &[Message],
) -> anyhow::Result<Vec<Bytes>> {
	let handler_addr = Address::from_slice(&client.handler().await?.0);
	let contract = HandlerV2Instance::new(handler_addr, client.signer.clone());
	let ismp_host = Address::from_slice(&client.ismp_host.0);

	let mut inner = Vec::with_capacity(messages.len());
	for msg in messages {
		let calldata = match msg {
			Message::Consensus(msg) => contract
				.handleConsensus(ismp_host, Bytes::from(msg.consensus_proof.clone()))
				.calldata()
```
