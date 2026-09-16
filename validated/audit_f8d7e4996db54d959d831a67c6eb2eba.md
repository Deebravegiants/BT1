### Title
Integer-overflow / unbounded-allocation DoS in unverified Pharos validator-set storage-proof parsing before Merkle verification - ([File: modules/consensus/pharos/verifier/src/state_proof.rs])

### Summary
`bls_data_slots_from_header` and `decode_bls_key_from_string_slot` in the Pharos consensus verifier derive a claimed BLS-key string length directly from an attacker-supplied raw storage value, before that value has been checked against any state-root Merkle proof. The derived length is used unchecked as an allocation size / loop bound (`Vec::with_capacity(str_len)`, `for i in 0..bls_data_slot_count`), mirroring the CVE-2025-65803 pattern where an attacker-controlled length field taken directly from untrusted input drives unchecked allocation/iteration and causes a crash/DoS.

### Finding Description
`verify_validator_set_proof` computes the expected storage keys from `proof.storage_values` **before** verifying those values against the state root: [1](#0-0) 

`compute_all_storage_keys` calls `bls_data_slots_from_header` on each validator's raw, unverified BLS-string header value: [2](#0-1) 

The header bytes come straight from `proof.storage_values`, fully controlled by whoever submits the consensus update — there is no bound on `header_val` before it is used to compute `str_len` (up to `u64::MAX`) and `slots_needed = (str_len + 31) / 32`. That count is then fed into `get_validator_keys`, which unconditionally loops `bls_data_slot_count` times pushing `H256` entries into a `Vec`: [3](#0-2) 

Only *after* this key-derivation and key-generation work is done does `verify_all_storage_proofs` check the values against the real state root: [4](#0-3) 

The same unchecked pattern repeats in `decode_bls_key_from_string_slot`, where `str_len` (again derived from unverified attacker input) is passed to `Vec::with_capacity(str_len)`: [5](#0-4) 

This is reachable from an unprivileged relayer: `PharosClient::verify_consensus` decodes a `VerifierStateUpdate` straight from the submitted proof bytes and calls `verify_pharos_block`, which eventually reaches `verify_validator_set_proof` on epoch/validator-set transitions: [6](#0-5) 

`verify_consensus` is the standard `ConsensusClient` entrypoint invoked by pallet-ismp when processing a relayed consensus-update message — a single unsigned/relayed message from any relayer, with no prior authentication of the payload contents.

### Impact Explanation
A malicious relayer can submit a crafted Pharos consensus/validator-set proof whose `storage_values` contain a BLS-key header slot encoding a near-maximal "long string" length. This forces:
1. `(str_len + 31) / 32` to compute a huge slot count consumed unbounded by a `Vec`-growing loop in `get_validator_keys`, and/or
2. `Vec::with_capacity(str_len)` in `decode_bls_key_from_string_slot` to attempt a multi-exabyte allocation,

before any cryptographic verification of the proof takes place. This causes an allocation failure/abort or excessive resource consumption in the node processing the consensus update — a Denial of Service against the Pharos light client path. Because consensus-state updates gate all subsequent state (and thus message) verification for the Pharos state machine, a stalled/crashed verifier halts the ability to deliver ISMP messages to/from Pharos, i.e., a route unable to deliver messages.

### Likelihood Explanation
High: any party able to submit a `verify_consensus` call for the Pharos client (i.e., any relayer relaying a Pharos consensus update) can supply the crafted `storage_values`; no signature over the storage values' content, and no state-root check, happens before the vulnerable arithmetic/allocation runs.

### Recommendation
Bound `str_len`/`slots_needed` derived from `bls_data_slots_from_header` and `decode_bls_key_from_string_slot` to the maximum plausible BLS key string length (e.g., ≤ 128 bytes / 4 slots) immediately after decoding, before it is used for any `Vec` allocation or loop bound, and before it is used in `compute_all_storage_keys` to derive Merkle proof keys. Reject any header value implying a string length outside that bound with an explicit error, rather than deferring the check to `next_idx > storage_values.len()`.

### Proof of Concept
1. Craft a `ValidatorSetProof` with `storage_values[1]` = a small count (e.g., 1) so the loop proceeds.
2. Set the BLS header storage value (the slot at `pool_ids_end`) to a `U256` with the low bit set (marks "long string") and a very large magnitude, e.g. `U256::MAX` (so `str_len = (U256::MAX - 1)/2 ≈ 2^255`).
3. Submit this as the `proof` bytes to `PharosClient::verify_consensus` (via the standard ISMP consensus-update message path, reachable by any relayer/unsigned extrinsic).
4. `bls_data_slots_from_header` computes `slots_needed = (str_len + 31) / 32` — an enormous number — which `get_validator_keys` then loops over, allocating an unbounded `Vec<H256>`, well before `verify_all_storage_proofs` ever validates `storage_values` against the state root, aborting or hanging the verifying node.

### Citations

**File:** modules/consensus/pharos/verifier/src/state_proof.rs (L79-89)
```rust
	let layout = StakingContractLayout::default();

	// Recompute expected storage keys from the storage values
	let keys = compute_all_storage_keys::<H>(&proof.storage_values, &layout)?;

	// Verify each storage value against its per-key proof path.
	// Pharos uses a flat trie — storage proofs verify directly against state_root.
	verify_all_storage_proofs(&keys, &proof.storage_values, &proof.storage_proof, &state_root)?;

	// Decode the verified storage values into a ValidatorSet
	let decoded_set = decode_validator_set_from_storage::<H>(&proof.storage_values, epoch)?;
```

**File:** modules/consensus/pharos/verifier/src/state_proof.rs (L241-266)
```rust
	} else {
		// Long string: header contains (length * 2 + 1)
		let length = (header_val - 1) / 2;
		let str_len = length.low_u64() as usize;

		// For BLS keys, we expect a 96 or 98 character hex string
		// This requires 3 data slots (ceil(96/32) = 3)
		let data_slots = data_slots.ok_or(Error::LongStringBlsKeyUnsupported)?;

		let slots_needed = (str_len + 31) / 32;
		if data_slots.len() < slots_needed {
			return Err(Error::InsufficientStorageValues {
				expected: slots_needed,
				got: data_slots.len(),
			});
		}

		let mut string_data = Vec::with_capacity(str_len);
		for (i, slot_value) in data_slots.iter().take(slots_needed).enumerate() {
			let slot_data = slot_value.as_ref().ok_or(Error::MissingBlsKeySlot)?;
			let decoded = decode_u256_from_storage(slot_data)?;
			let bytes = decoded.to_big_endian();

			let remaining = str_len - (i * 32);
			let take = remaining.min(32);
			string_data.extend_from_slice(&bytes[..take]);
```

**File:** modules/consensus/pharos/verifier/src/state_proof.rs (L366-400)
```rust
/// Verify each storage value against its per-key proof path in the storage trie.
fn verify_all_storage_proofs(
	keys: &[H256],
	values: &[Vec<u8>],
	storage_proof: &BTreeMap<H256, Vec<PharosProofNode>>,
	storage_hash: &H256,
) -> Result<(), Error> {
	if keys.len() != values.len() {
		return Err(Error::SlotValueLengthMismatch { slots: keys.len(), values: values.len() });
	}

	let address: [u8; 20] = STAKING_CONTRACT_ADDRESS.0 .0;

	for (key, value) in keys.iter().zip(values.iter()) {
		let proof_nodes = storage_proof
			.get(key)
			.ok_or(Error::MissingStorageValue { field: "storage proof for key" })?;

		let mut padded_value = [0u8; 32];
		if value.len() <= 32 {
			padded_value[32 - value.len()..].copy_from_slice(value);
		} else {
			return Err(Error::StorageValueTooLarge);
		}

		spv::verify_proof(
			proof_nodes,
			&spv::build_storage_key(&address, &key.0),
			&padded_value,
			&storage_hash.0,
		)?;
	}

	Ok(())
}
```

**File:** modules/consensus/pharos/verifier/src/state_proof.rs (L603-628)
```rust
	pub fn get_validator_keys<H: Keccak256>(
		&self,
		pool_id: &H256,
		bls_data_slot_count: usize,
	) -> Vec<H256> {
		let offsets = ValidatorStructOffsets::default();
		let mut keys = Vec::new();

		// BLS public key string slot (stores length for long strings)
		let bls_string_slot = self.validator_field_slot::<H>(pool_id, offsets.bls_public_key);
		keys.push(bls_string_slot);

		// BLS public key data slots (for long strings)
		// Data is stored at keccak256(string_slot) for `bls_data_slot_count` slots
		let bls_data_base = self.string_data_slot::<H>(&bls_string_slot);
		let bls_data_base_pos = U256::from_big_endian(bls_data_base.as_bytes());
		for i in 0..bls_data_slot_count {
			let slot_pos = bls_data_base_pos + U256::from(i);
			keys.push(H256(slot_pos.to_big_endian()));
		}

		// totalStake field
		keys.push(self.validator_field_slot::<H>(pool_id, offsets.total_stake));

		keys
	}
```

**File:** modules/consensus/pharos/verifier/src/state_proof.rs (L639-653)
```rust
pub fn bls_data_slots_from_header(header_value: &[u8]) -> Result<usize, Error> {
	let header_val = decode_u256_from_storage(header_value)?;
	let header_bytes = header_val.to_big_endian();
	let lowest_byte = header_bytes[31];

	if lowest_byte & 1 == 0 {
		// Short string - data is in the header itself
		Ok(0)
	} else {
		// Long string - header = length * 2 + 1
		let length = (header_val - 1) / 2;
		let str_len = length.low_u64() as usize;
		Ok((str_len + 31) / 32)
	}
}
```

**File:** modules/ismp/clients/pharos/src/lib.rs (L98-118)
```rust
	fn verify_consensus(
		&self,
		_host: &dyn IsmpHost,
		consensus_state_id: ConsensusStateId,
		trusted_consensus_state: Vec<u8>,
		proof: Vec<u8>,
	) -> Result<(Vec<u8>, ismp::consensus::VerifiedCommitments), Error> {
		let update = VerifierStateUpdate::decode(&mut &proof[..])
			.map_err(|e| Error::AnyHow(anyhow::anyhow!("{:?}", e).into()))?;

		let consensus_state =
			ConsensusState::decode(&mut &trusted_consensus_state[..]).map_err(|e| {
				Error::AnyHow(
					anyhow::anyhow!("Cannot decode trusted consensus state: {:?}", e).into(),
				)
			})?;

		let trusted_state: VerifierState = consensus_state.clone().into();

		let new_state = verify_pharos_block::<C, H>(trusted_state, update.clone())
			.map_err(|e| Error::AnyHow(anyhow::Error::from(e).into()))?;
```
