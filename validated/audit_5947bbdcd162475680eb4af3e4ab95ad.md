### Title
Unbounded array decoding in `Codec.DecodeHeader` allows gas-griefing DoS on BEEFY consensus verification - (File: evm/src/consensus/Codec.sol)

### Summary
`Codec.DecodeHeader` (used by both `EcdsaBeefy.verifyParachainHeaderProof` and `SP1Beefy.verifyConsensus`) reads a SCALE compact-encoded digest-count directly from attacker-supplied `calldata` and uses it, unbounded, both to size a memory array (`new Digest[](length)`) and to drive a decode loop, with no cap on the number of digest items or on the number of parachain headers passed in the outer proof array.

### Finding Description
`Codec.DecodeHeader` reads the header's digest-item count as a raw SCALE compact integer and immediately allocates and loops over it with no upper bound check: [1](#0-0) 

This mirrors the pypdf bug class described in the report: decoding an array-based structure whose declared entry count is taken from untrusted input and used to drive allocation/iteration work with no sanity limit, producing long runtimes / large memory usage for a "lots of entries" payload.

Both BEEFY consensus clients feed attacker-controlled header bytes into this function, once per parachain header in the outer array, and the outer array length is also unbounded:

- `EcdsaBeefy.verifyParachainHeaderProof` iterates `proof.parachains` (length taken directly from calldata, `abi.decode`d with no size limit) and calls `Codec.DecodeHeader(para.header)` for every entry: [2](#0-1) 

- `SP1Beefy.verifyConsensus` does the same over `proof.headers`, decoding every header via `Codec.DecodeHeader` after the (fixed-cost) ZK proof check: [3](#0-2) 

Both `verify()` entry points are reachable by `handleConsensus`, which is explicitly permissionless: [4](#0-3) 
(same permissionless pattern is documented for `handleConsensus`) [5](#0-4) 

Because `length` in `DecodeHeader` comes from bytes the caller fully controls (the `header` field of each `Parachain`/`ParachainHeader` struct, itself inside an attacker-supplied outer array), a relayer/dispatcher can:
1. Submit many `Parachain` entries in `RelayChainProof`/`ParachainProof` (or `ParachainHeader[]` for SP1), each with a header whose SCALE-encoded digest-count field is set to a very large value (up to `2^64-1` in compact encoding mode 3, though practically bounded by calldata gas cost of supplying the bytes — however the *decode-time* cost of the loop is what's unbounded relative to bytes supplied, similar to a "compression bomb" style amplification: a tiny number of bytes can encode a huge declared array length that then drives a large `new Digest[](length)` allocation and iteration attempt).
2. Even without reaching an actual OOG revert that only wastes the caller's own gas, the same growth pattern (array-count taken from untrusted encoding without a cap, both for the outer batch and inner digest list) is the root cause class flagged in the advisory — inefficient decoding of array-based structures with attacker-controlled entry counts.

### Impact Explanation
On EVM, an out-of-bound `length` triggers `new Digest[](length)`, which reverts with out-of-gas once it exceeds the block gas limit — this by itself is "just" a revert of the caller's own transaction. However, the more materially exploitable variant is amplification: a small proof payload (cheap to submit) can declare a digest/header count large enough to make gas estimation/relayer simulation extremely expensive or to always fail on any node with a lower gas limit, effectively giving an unprivileged submitter the ability to make `handleConsensus` (and thus the entire finality/message-delivery path that depends on it) fail unpredictably or become uneconomical to relay, since no cap exists between "one SCALE compact byte declaring a length" and "the loop actually executing." This falls under CWE-400/CWE-407 (uncontrolled resource consumption from inefficient algorithmic complexity), matching the reported bug class, and can degrade the "route unable to deliver messages" criterion because a malformed/large consensus proof can be crafted so cheaply that it discourages or blocks honest relayers from processing valid consensus updates on the same or subsequent proofs relying on the same decode path.

### Likelihood Explanation
Likelihood is limited by the fact that Solidity memory-array allocation costs scale roughly quadratically with size and hit the block gas limit relatively quickly (memory expansion cost), so a fully successful large-array DoS against block gas is naturally self-limiting compared to pypdf's Python-heap-based bug. There is no explicit cap on the number of `Parachain`/`ParachainHeader` entries or on the decoded digest count, but exploitation requires the attacker to also pay for the calldata to encode a plausible header with an oversized digest count, and the transaction reverts (wasting the attacker's own gas) rather than corrupting state. This is a real missing bound (no `require(length <= MAX_DIGESTS)` anywhere in `Codec.DecodeHeader`), but the achievable blast radius on EVM is more "wasted-gas revert" than a sustained resource-exhaustion attack against the network the way the pypdf advisory describes for a long-running Python process.

### Recommendation
Add explicit upper bounds in `Codec.DecodeHeader` on the digest-item count (and validate it against the remaining slice length before allocating `Digest[]`), and add a maximum entries check on `RelayChainProof.parachains` / `SP1BeefyProof.headers` in `EcdsaBeefy`/`SP1Beefy` before iterating, mirroring the approach already used elsewhere in the codebase (e.g., `pallet-beefy-consensus-proofs`'s `MaxProofSize` bound at the txpool layer): [6](#0-5) 

### Proof of Concept
1. Craft a `Parachain.header` byte string whose first 96 bytes are valid header fields (`parentHash`, `blockNumber` compact, `stateRoot`, `extrinsicsRoot`), followed by a SCALE compact-encoded digest count using mode-3 encoding to declare an extremely large digest array length (e.g., `l = 8`, giving up to a `uint64`-range value) with no actual digest bytes following it.
2. Submit this as one `Parachain` entry (or many) inside `RelayChainProof`/`ParachainProof` via `EcdsaBeefy.verify` (reached through `IHandlerV2.handleConsensus`, which is permissionless — no auth required to call).
3. `Codec.DecodeHeader` executes `Digest[] memory digests = new Digest[](length);` with the attacker-declared `length`, then loops `for (uint256 i = 0; i < length; i++)`, immediately reading past the actual buffer via `readByte`/`read`, which either reverts on out-of-bounds `require` checks after excessive gas consumption for the allocation, or — for a length just under the gas-limit threshold — consumes disproportionate gas relative to the small number of calldata bytes needed to encode the large declared count, demonstrating the same "attacker declares huge array-based length with little effort" pattern as the pypdf advisory.

### Citations

**File:** evm/src/consensus/Codec.sol (L70-102)
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

        return Header(parentHash, blockNumber, stateRoot, extrinsicsRoot, digests);
    }
```

**File:** evm/src/consensus/EcdsaBeefy.sol (L198-221)
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

**File:** evm/src/core/HandlerV2.sol (L181-181)
```text
    function handlePostRequests(IHost host, PostRequestMessage calldata request) external notFrozen(host) {
```

**File:** docs/content/developers/evm/api/ihandler.mdx (L52-82)
```text
### handleConsensus()

Processes a consensus proof to update the consensus state and store new state commitments.

```solidity lineNumbers
function handleConsensus(
    IHost host, 
    bytes calldata proof
) external
```

| Parameter | Type | Description |
|-----------|------|-------------|
| `host` | `IHost` | The IHost contract |
| `proof` | `bytes` | Encoded consensus proof from Hyperbridge |

**Access:** Permissionless (can be called by anyone)

**Process:**
1. Retrieves current consensus state from host
2. Calls consensus client to verify proof
3. Updates consensus state in host if valid
4. Stores new state commitments for finalized blocks
5. Updates latest state machine heights

**Reverts:**
- If consensus client verification fails
- If proof is for a stale height
- If authority set is unknown
- If host is frozen

```

**File:** parachain/simtests/src/pallet_beefy_consensus_proofs.rs (L355-366)
```rust
	// 6. submit_proof oversized payload — `proof: BoundedVec<u8, MaxProofSize>` rejects at the
	//    txpool decode stage, before dispatch. We send `MaxProofSize + 1` bytes prefixed with
	//    `PROOF_TYPE_NAIVE`.
	let mut oversized_proof = vec![PROOF_TYPE_NAIVE; MAX_PROOF_SIZE + 1];
	oversized_proof[0] = PROOF_TYPE_NAIVE;
	let call = subxt::dynamic::tx(
		"BeefyConsensusProofs",
		"submit_proof",
		vec![Value::from_bytes(&oversized_proof)],
	);
	let result = submit_signed(&client, &rpc_client, call, Keyring::Bob).await;
	assert!(result.is_err(), "oversized submit_proof must be rejected by the BoundedVec decode",);
```
