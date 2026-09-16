Based on my research, I found the exact analog: an out-of-bounds index panic in the RLP node decoder that mirrors the ImageMagick `DrawImage` bug class — untrusted, attacker-supplied byte data indexed without a length check before use, causing a crash on a permissionless code path. This was already found and fixed in `modules/trees/ethereum/src/node_codec.rs`, with a regression test documenting the exact issue.I have sufficient evidence to write the final answer now — the vulnerability was already found and fixed (with a regression test), so the correct output is a confirmed analog citing the fix location.

### Title
Heap/index-out-of-bounds panic on adversarial RLP trie-node input in the Ethereum state proof `NodeCodec` — (File: `modules/trees/ethereum/src/node_codec.rs`)

### Summary
The CVE describes ImageMagick's `DrawImage` indexing crafted, attacker-controlled image data without validating that the offset/length it reads is within bounds, causing a heap-based buffer overflow and crash. The structurally identical bug class — indexing into attacker-controlled byte data without a bounds/emptiness check before dereferencing — existed in Hyperbridge's `RlpNodeCodec::decode_plan`, which parses Ethereum Patricia-Merkle-trie proof nodes supplied inside relayer-submitted state proofs. A crafted leaf/extension node whose hex-prefix (HP) partial key is the empty byte string caused `data[0]` to be read on a zero-length slice, panicking with an index-out-of-bounds error inside on-chain/runtime execution triggered by a completely unauthenticated relayer-submitted proof.

### Finding Description
`decode_plan` parses each RLP-encoded trie node handed to it via a state/storage proof. For the `Prototype::List(2)` case (leaf or extension node) it extracts the first RLP item's payload as `data` and then immediately reads `data[0] & 16` / `data[0] & 32` to determine node kind and nibble parity: [1](#0-0) 

Before the current fix, there was no check that `data` (the HP-encoded partial key) was non-empty. A well-formed leaf/extension node's partial key can never be empty per the Merkle-Patricia-trie spec, but nothing in the RLP layer enforces that invariant — a relayer can submit `rlp([b"", b""])` as a "proof node." Indexing `data[0]` on that zero-length slice panics.

This proof data is not attacker-owned/local state — it flows in from **any unprivileged relayer** delivering `PostRequest`/`GetResponse`/timeout messages against an EVM source chain, through `EvmStateMachine::verify_membership` / `verify_non_membership` / `verify_state_proof` (`modules/ismp/state-machines/evm/src/lib.rs`), which builds a `TrieDB<EIP1186Layout<H>>` over the submitted `StorageProof` and calls `decode_plan` on every supplied node before any cryptographic root-check can reject a malformed proof. The regression test the fix added confirms both the trigger and prior impact: [2](#0-1) 

### Impact Explanation
This is on the message-delivery/state-verification hot path reachable from a single, permissionless proof submission (`handlePostRequests`, `handleGetResponses`, `handlePostRequestTimeouts`, `handleGetRequestTimeouts` on the Solidity side reaching into `pallet-ismp`'s EVM state-machine client, or the equivalent Substrate-runtime handler). A panic while decoding a trie node aborts the runtime call that processes the batch of incoming messages/proofs — i.e. a single crafted node inside an otherwise-plausible proof denies delivery of that whole batch, and if triggered inside consensus-critical runtime execution (e.g. a parachain block importing an extrinsic that calls into this path) it can crash the node process executing it, per the comment accompanying the fix ("index-out-of-bounds inside on-chain execution (e.g. parachain block verification)"). This matches the "route unable to deliver messages" / denial-of-service acceptance criterion for a Medium-severity analog of the CVE's crash-on-crafted-input class.

### Likelihood Explanation
Low complexity, no privilege required: any relayer or message submitter can construct a `PostRequestMessage`/`GetResponseMessage`/timeout message whose EVM storage proof contains one adversarial RLP node `rlp([b"", b""])`. The node is trivial to construct and the check happens before any hash/root binding rejects the structurally invalid node, so the crash is reachable pre-authentication of the proof's correctness.

### Recommendation
The fix is already present in the current codebase: reject an empty HP-encoded partial key with a proper `DecoderError` instead of indexing into it, as shown at `modules/trees/ethereum/src/node_codec.rs:82-84`. Confirm equivalent guards exist for every other place raw trie/RLP proof bytes are indexed without a length check (the codebase shows a similar audit already applied to `nibble_at_depth` in the Pharos SPV verifier and to `ByteVector<N>` SCALE decoding), and keep the `empty_hp_prefix_returns_error_not_panic` regression test in CI to prevent recurrence.

### Proof of Concept [2](#0-1) 

The adversarial node bytes `[0xc2, 0x80, 0x80]` RLP-decode to a 2-item list `[b"", b""]` (an empty partial key and empty value). Feeding this into `RlpNodeCodec::<KeccakHasher>::decode_plan` prior to the fix executed `data[0]` on the empty slice at `node_codec.rs:88/90`, panicking with an index-out-of-bounds error. Such a node can be embedded as one entry of the `storage_proof` field inside any EVM `StateProof` submitted through `verify_membership`/`verify_state_proof` in `modules/ismp/state-machines/evm/src/lib.rs`, reachable from a permissionless `handlePostRequests`/`handleGetResponses`/timeout call.

### Citations

**File:** modules/trees/ethereum/src/node_codec.rs (L76-91)
```rust
			Prototype::List(2) => {
				let (rlp, offset) = r.at_with_offset(0)?;
				let (data, i) = (rlp.data()?, rlp.payload_info()?);
				// The first byte of a leaf/extension node's partial key is the
				// hex-prefix flag byte. A well-formed HP-encoded key is never
				// empty, so reject here to avoid a panic on adversarial input.
				if data.is_empty() {
					return Err(DecoderError::Custom("empty HP-encoded partial key").into());
				}
				match (
					NibbleSlicePlan::new(
						(offset + i.header_len)..(offset + i.header_len + i.value_len),
						if data[0] & 16 == 16 { 1 } else { 2 },
					),
					data[0] & 32 == 32,
				) {
```

**File:** modules/trees/ethereum/src/tests.rs (L73-85)
```rust
#[test]
fn empty_hp_prefix_returns_error_not_panic() {
	// Regression: a leaf/extension node is RLP-encoded as a 2-item list whose
	// first item is the hex-prefix-encoded partial key. Before the fix at
	// `node_codec.rs` the decoder indexed `data[0]` without checking that the
	// HP payload was non-empty, so an adversarial proof node of the form
	// `rlp([b"", b""])` panicked with index-out-of-bounds inside on-chain
	// execution (e.g. parachain block verification). It must now return an
	// `Err` cleanly.
	let adversarial_node: [u8; 3] = [0xc2, 0x80, 0x80];
	let result = <RlpNodeCodec<KeccakHasher> as NodeCodec>::decode_plan(&adversarial_node);
	assert!(result.is_err(), "decoder must reject empty HP prefix, got {:?}", result);
}
```
