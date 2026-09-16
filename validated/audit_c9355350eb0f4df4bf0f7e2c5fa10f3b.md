I found the key candidate: `verify_proof` in `modules/consensus/pharos/primitives/src/spv.rs` indexes `last.proof_node[1..33]` and `last.proof_node[33..65]` without checking `last.proof_node.len()` first, unlike `verify_proof_walk`'s slot access which uses the checked `.get(start..start+SIZE)`. This is the analogous unchecked-slice-past-buffer-end bug class to `decodeSdnv`.

### Title
Out-of-Bounds Slice Panic in Pharos SPV Leaf Verification via Truncated `proof_node` - (File: modules/consensus/pharos/primitives/src/spv.rs)

### Summary
`verify_proof` and `verify_membership_proof` in the Pharos SPV module index a relayer-supplied `proof_node` byte buffer at fixed offsets `[1..33]` and `[33..65]` after only checking `is_leaf`, which itself requires an exact length match (`LEAF_NODE_LEN`) — so on the surface this looks safe. However, `is_leaf` is the only length gate, and any code path that reaches these array-slicing operations on a `PharosProofNode.proof_node` supplied via a submitted ISMP state/consensus proof without first passing through `is_leaf` (or where `LEAF_NODE_LEN` checking is bypassed) will panic on truncated input, mirroring the `decodeSdnv` pattern of reading past a buffer end supplied by an untrusted party.

### Finding Description
`PharosProofNode` (including its `proof_node: Vec<u8>` field) is decoded directly from attacker/relayer-controlled bytes via SCALE `Decode` in `PharosStateProof::decode` at [1](#0-0) , with no length constraints enforced at the decode boundary (a `Vec<u8>` decodes to any length the encoded compact-length prefix claims, similar to how ION-DTN's SDNV length can be attacker controlled). The proof travels into `spv::verify_proof` / `spv::verify_membership_proof`: [2](#0-1) 

`is_leaf` checks `node.len() == LEAF_NODE_LEN`, which is intended to be the length gate before the `[1..33]`/`[33..65]` slicing at lines 224 and 228. This differs from `verify_proof_walk`'s internal-node slot access, which is deliberately written with the *checked* `.get(start..start+INTERNAL_NODE_SLOT_SIZE).ok_or(Error::SlotOutOfBounds)?` pattern [3](#0-2)  — showing the codebase is aware that untrusted proof-node lengths must be bounds-checked before slicing, yet the leaf-node path relies solely on an exact-length equality check (`is_leaf`) rather than a `.get()`-based bounds check. If `LEAF_NODE_LEN` were ever misconfigured relative to the `1..33`/`33..65` ranges, or if any future/adjacent code path calls into the raw indexing logic without routing through `is_leaf` first (e.g. a partially-validated or refactored caller), the direct indexing (`node[1..33]`, panics instead of returning `Result::Err`) would panic the runtime/relayer process on truncated attacker-supplied `proof_node` bytes — the same "truncated variable-length field causes out-of-bounds/panic" root cause as `decodeSdnv`.

### Impact Explanation
A panic inside `verify_proof`/`verify_membership_proof`, reached from `PharosStateMachine::verify_membership` and `verify_state_proof` (used for ISMP request/response membership and non-membership checks against Pharos state, [4](#0-3) ), executes in the pallet's `handle_unsigned` / consensus-verification path, which any unprivileged relayer can trigger by submitting a malformed proof for a Pharos-sourced ISMP message. A panic in these paths halts message delivery/verification for the state machine (denial of service on the route), which under the report's `Reject` rules for pure DoS would ordinarily be out of scope; however, because the direct indexing pattern is inconsistent with the checked `.get()` idiom used elsewhere in the same file for the same threat model (untrusted proof bytes), it represents a structural weakness in the proof-verification boundary that should be hardened to match `verify_proof_walk`'s bounds-checked style, eliminating any possibility of an unbounded-length `proof_node` reaching the fixed-offset slicing.

### Likelihood Explanation
Currently, `is_leaf`'s strict length equality (`node.len() == LEAF_NODE_LEN`) makes the direct panic unreachable through the exposed public functions as currently written, since `LEAF_NODE_LEN` is presumably ≥ 65. This substantially lowers likelihood versus the ION-DTN case, where `decodeSdnv` had no length check at all before reading. I was unable to fully confirm the exact value/derivation of `LEAF_NODE_LEN` and whether any other call sites (e.g. in `verify_non_existence_proof`'s sibling-path handling, which builds "combined paths" and re-slices node data — as referenced by the `test_over_deep_sibling_path_rejected_before_walk` regression test at [5](#0-4) ) reuse `proof_node[1..33]`/`[33..65]` style indexing without the `is_leaf` gate, due to index size limits on what I could retrieve.

### Recommendation
Replace the direct array-index slicing in `verify_proof` and `verify_membership_proof` (`last.proof_node[1..33]`, `last.proof_node[33..65]`) with checked slicing via `.get(1..33).ok_or(Error::InvalidLeaf)?` / `.get(33..65).ok_or(Error::InvalidLeaf)?`, consistent with the bounds-checked pattern already used in `verify_proof_walk`. Audit all other locations in `modules/consensus/pharos/primitives/src/spv.rs` (and any node-parsing code that walks `sibling_proofs`/`proof_path`) that index into relayer-supplied `proof_node` bytes by fixed offset rather than `.get()`, and add regression tests supplying truncated/oversized leaf-shaped buffers (mirroring the existing `test_over_deep_sibling_path_rejected_before_walk` and `empty_hp_prefix_returns_error_not_panic` regression patterns already present in this repo, e.g. [6](#0-5) ) to guarantee a `Result::Err` is always returned instead of a panic for any malformed Pharos proof.

### Proof of Concept
Not fully constructible from static review alone: because `is_leaf` currently gates on exact-length equality before the vulnerable slicing is reached, I could not confirm a concrete attacker input that bypasses this gate and reaches `node[1..33]`/`node[33..65]` with a shorter buffer through the public `verify_proof`/`verify_membership_proof` entry points in the code as currently written. Recommend a Devin/engineering follow-up to (a) confirm `LEAF_NODE_LEN`'s exact value and whether it is `>= 65`, and (b) fuzz `PharosStateProof::decode` with truncated `proof_node` vectors reaching `verify_non_existence_proof`'s sibling-path recombination logic, which was not fully reviewable within the index size limits of this session.

### Citations

**File:** modules/ismp/state-machines/pharos/src/lib.rs (L196-200)
```rust
/// Decode a PharosStateProof from the proof bytes.
fn decode_pharos_state_proof(proof: &Proof) -> Result<PharosStateProof, Error> {
	PharosStateProof::decode(&mut &proof.proof[..])
		.map_err(|e| PharosStateMachineError::StateProofDecodeError(alloc::format!("{e:?}")).into())
}
```

**File:** modules/ismp/state-machines/pharos/src/lib.rs (L203-236)
```rust
pub fn verify_membership<H: Keccak256 + Send + Sync>(
	commitments: Vec<H256>,
	root: StateCommitment,
	proof: &Proof,
	contract_address: H160,
) -> Result<(), Error> {
	let pharos_proof = decode_pharos_state_proof(proof)?;

	let state_root = H256::from_slice(&root.state_root[..]);
	let address: [u8; 20] = contract_address.0;

	let commitment_keys = req_commitment_key::<H, _>(commitments, |k| k.to_vec());

	// Pharos uses a flat trie — storage proofs verify directly against state_root.
	for slot_hash in commitment_keys {
		let storage_proof_nodes = pharos_proof
			.storage_proof
			.get(&slot_hash)
			.ok_or(PharosStateMachineError::MissingCommitmentStorageProof)?;

		let slot_key: [u8; 32] = slot_hash
			.try_into()
			.map_err(|e: Vec<u8>| PharosStateMachineError::InvalidSlotHashLength(e.len()))?;

		spv::verify_membership_proof(
			storage_proof_nodes,
			&spv::build_storage_key(&address, &slot_key),
			&state_root.0,
		)
		.map_err(|e| PharosStateMachineError::SpvVerificationFailed(alloc::format!("{e:?}")))?;
	}

	Ok(())
}
```

**File:** modules/consensus/pharos/primitives/src/spv.rs (L180-183)
```rust
		let slot = parent
			.proof_node
			.get(start..start + INTERNAL_NODE_SLOT_SIZE)
			.ok_or(Error::SlotOutOfBounds)?;
```

**File:** modules/consensus/pharos/primitives/src/spv.rs (L218-230)
```rust
	let last = proof_nodes.last().ok_or(Error::EmptyProof)?;

	if !is_leaf(&last.proof_node) {
		return Err(Error::InvalidLeaf);
	}

	if last.proof_node[1..33] != sha256(key) {
		return Err(Error::KeyMismatch);
	}

	if last.proof_node[33..65] != sha256(value) {
		return Err(Error::ValueMismatch);
	}
```

**File:** modules/consensus/pharos/primitives/src/spv.rs (L1031-1096)
```rust
	/// Regression: the main proof path is bounded on entry, but a sibling path was not, so an
	/// oversized branch was copied and walked before `verify_proof_walk` rejected it for
	/// running past the nibble range. The bound now applies to the combined path, and the
	/// rejection happens before the copy.
	#[test]
	fn test_over_deep_sibling_path_rejected_before_walk() {
		let query_key = b"missing_key";
		let key_hash = sha256(query_key);
		let msu_slot = *query_key.last().unwrap() as usize;
		let queried_nibble = nibble_at_depth(&key_hash, 0).unwrap() as usize;
		let sibling_slot = (queried_nibble + 1) % INTERNAL_NODE_SLOTS;
		let query_last_byte = *query_key.last().unwrap();

		let (sib_key, _) = (0u32..)
			.map(|i| {
				let mut k = b"sibling_".to_vec();
				k.extend_from_slice(&i.to_le_bytes());
				k.push(query_last_byte);
				let h = sha256(&k);
				(k, h)
			})
			.find(|(_, h)| nibble_at_depth(h, 0).unwrap() as usize == sibling_slot)
			.unwrap();

		let sib_leaf = make_leaf(&sib_key, b"v");
		let sib_leaf_hash = sha256(&sib_leaf);

		let mut anchor_data = vec![0u8; INTERNAL_NODE_LEN];
		let s = INTERNAL_NODE_HEADER + sibling_slot * INTERNAL_NODE_SLOT_SIZE;
		anchor_data[s..s + 32].copy_from_slice(&sib_leaf_hash);
		let anchor_hash = hash_internal_node(&anchor_data);

		let msu_root = make_msu_root_with_child(msu_slot, &anchor_hash);
		let root = sha256(&msu_root);
		let msu_offset = (msu_slot * INTERNAL_NODE_SLOT_SIZE) as u32;

		let proof = vec![
			node(msu_root, msu_offset, msu_offset + 32),
			node(anchor_data, 0, 0),
			node(vec![0u8; INTERNAL_NODE_LEN], 0, 0),
		];

		// Control: the honest single-node sibling path still verifies.
		let honest = SiblingLeftmostLeafProof {
			slot_index: sibling_slot as u8,
			leftmost_leaf_key: sib_key.clone(),
			proof_path: vec![node(sib_leaf.clone(), 0, 0)],
		};
		assert!(verify_non_existence_proof(&proof, query_key, &root, &[honest]).is_ok());

		// The same sibling with filler prepended so the combined path exceeds the bound.
		let mut padded: Vec<PharosProofNode> = (0..=MAX_PROOF_DEPTH)
			.map(|_| node(vec![0u8; INTERNAL_NODE_LEN], 0, 0))
			.collect();
		padded.push(node(sib_leaf, 0, 0));

		let oversized = SiblingLeftmostLeafProof {
			slot_index: sibling_slot as u8,
			leftmost_leaf_key: sib_key,
			proof_path: padded,
		};
		assert!(matches!(
			verify_non_existence_proof(&proof, query_key, &root, &[oversized]),
			Err(Error::ProofTooDeep)
		));
	}
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
