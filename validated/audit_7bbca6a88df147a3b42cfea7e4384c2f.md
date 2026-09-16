This confirms the reachable path: `PharosClient::verify_consensus` (dispatched by any relayer via `pallet-ismp`'s `handle_unsigned`/consensus update path) decodes the `VerifierStateUpdate` proof and calls `verify_pharos_block`, which for epoch-boundary updates calls `state_proof::verify_validator_set_proof` [1](#0-0) , which calls `compute_all_storage_keys` **before** any of `proof.storage_values` is cryptographically checked against `state_root` [2](#0-1) .

### Title
Unbounded memory allocation from untrusted BLS string-header length in Pharos validator-set proof decoding - (File: `modules/consensus/pharos/verifier/src/state_proof.rs`)

### Summary
`bls_data_slots_from_header` and `decode_bls_key_from_string_slot` derive a slot/byte count directly from an attacker-controlled, **not-yet-verified** storage value and use it to drive loop bounds and `Vec::with_capacity` allocations, mirroring the Apache Thrift "Memory Allocation with Excessive Size Value" bug class (CWE-789/CWE-1285): a length field taken from untrusted wire data is used for allocation before any bound check against the actual proof/trusted data size.

### Finding Description
`verify_validator_set_proof` first calls `compute_all_storage_keys`, which reads `storage_values[idx]` (a raw `Vec<u8>` supplied by the caller inside `ValidatorSetProof`, itself decoded from an arbitrary, permissionlessly-submitted `VerifierStateUpdate`/consensus proof) and passes it to `bls_data_slots_from_header` [3](#0-2) .

`bls_data_slots_from_header` decodes this untrusted bytes as a `U256` "Solidity long-string header", computes `length = (header_val - 1) / 2`, and casts to `usize` via `.low_u64() as usize` — this arithmetic is performed on data that has not yet been checked against any Merkle/state proof: [4](#0-3) 

This `str_len`-derived `slots_needed`/`bls_data_slot_count` (up to `~2^64/32`) is then used as the loop bound in `get_validator_keys`, which pushes one `H256` (32 bytes) into a `Vec` for every slot: [5](#0-4) 

The only real limit at this point is `next_idx > storage_values.len()`, but that check happens *after* `bls_data_slots_from_header` has already returned the huge count and `get_validator_keys` is invoked with it — so the loop/allocation itself is unbounded by the actual number of storage values submitted [6](#0-5) . Only afterward does `verify_all_storage_proofs` cryptographically check the (small, legitimately-provided) `storage_values` against `state_root` — but by then the excessive allocation/loop has already executed [7](#0-6) .

The same untrusted-length-before-verification pattern recurs in `decode_bls_key_from_string_slot`'s `Vec::with_capacity(str_len)` [8](#0-7) , though this second call path is bounded somewhat by the `slots_needed`/`data_slots.len()` check just before it — the first occurrence in `compute_all_storage_keys` is the one that runs unchecked.

`MAX_VALIDATORS` bounds only the *validator count*, not the per-validator BLS string-header length, so it provides no protection here [9](#0-8) .

### Impact Explanation
This is reachable by any relayer submitting a `VerifierStateUpdate` consensus proof via `PharosClient::verify_consensus`, invoked from `pallet-ismp`'s permissionless consensus-update path [1](#0-0) . A crafted `ValidatorSetProof.storage_values` entry with a huge fake "long string header" value drives `get_validator_keys` to loop and allocate up to ~2^59 `H256` entries (18 exabytes) before any cryptographic check occurs, causing an out-of-memory abort/panic of the node processing the update — a denial of service against consensus-update processing for the Pharos state machine (route unable to deliver/verify further messages).

### Likelihood Explanation
High: the trigger requires only submitting a single ISMP consensus-update extrinsic/proof with attacker-chosen `storage_values` bytes; no privileged role, valid signature, or prior state is needed to reach the vulnerable computation, since key/length computation happens strictly before Merkle-proof verification.

### Recommendation
Bound `str_len`/`bls_data_slot_count` derived from `bls_data_slots_from_header` to a small constant (e.g. enough for a 128-byte hex string, matching the expected 96–98 char BLS key encoding) before it is used for any loop bound or allocation, and reject the update immediately if it exceeds that bound — do this check inside `bls_data_slots_from_header` itself so both call sites (`compute_all_storage_keys` and `decode_bls_key_from_string_slot`) are protected regardless of ordering relative to Merkle-proof verification.

### Proof of Concept
1. Construct a `VerifierStateUpdate` with an epoch that is `trusted_epoch + 1`, so `validator_set_proof` is required and processed.
2. In `ValidatorSetProof.storage_values`, set `storage_values[1]` (validator count) to `1`, and craft a pool-id entry so `compute_all_storage_keys` reaches index for the BLS header.
3. Set the corresponding `storage_values[idx]` (BLS header slot for that validator) to a `U256` big-endian encoding of a very large odd number (e.g. `0xFFFF...FFFF`, low bit set to mark "long string").
4. Submit this `update.encode()` as `proof` to `PharosClient::verify_consensus`.
5. `bls_data_slots_from_header` computes an astronomically large `slots_needed`, which is passed to `get_validator_keys`'s `for i in 0..bls_data_slot_count { keys.push(...) }` loop, causing the node to attempt an unbounded allocation/loop and abort — before `verify_all_storage_proofs` ever validates `storage_values` against `state_root`.

### Citations

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

**File:** modules/consensus/pharos/verifier/src/state_proof.rs (L74-94)
```rust
pub fn verify_validator_set_proof<H: Keccak256 + Send + Sync>(
	state_root: H256,
	proof: &ValidatorSetProof,
	epoch: u64,
) -> Result<ValidatorSet, Error> {
	let layout = StakingContractLayout::default();

	// Recompute expected storage keys from the storage values
	let keys = compute_all_storage_keys::<H>(&proof.storage_values, &layout)?;

	// Verify each storage value against its per-key proof path.
	// Pharos uses a flat trie — storage proofs verify directly against state_root.
	verify_all_storage_proofs(&keys, &proof.storage_values, &proof.storage_proof, &state_root)?;

	// Decode the verified storage values into a ValidatorSet
	let decoded_set = decode_validator_set_from_storage::<H>(&proof.storage_values, epoch)?;

	validate_validator_set(&decoded_set)?;

	Ok(decoded_set)
}
```

**File:** modules/consensus/pharos/verifier/src/state_proof.rs (L129-133)
```rust
	let count = validator_count.low_u64() as usize;

	if count > MAX_VALIDATORS {
		return Err(Error::TooManyValidators { count, max: MAX_VALIDATORS });
	}
```

**File:** modules/consensus/pharos/verifier/src/state_proof.rs (L243-258)
```rust
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
```

**File:** modules/consensus/pharos/verifier/src/state_proof.rs (L331-360)
```rust
	let mut idx = pool_ids_end;
	for i in 0..count {
		let v = &storage_values[pool_set_start + i];
		let mut bytes = [0u8; 32];
		if v.len() <= 32 {
			bytes[32 - v.len()..].copy_from_slice(v);
		}
		let pool_id = H256::from(bytes);

		// The BLS header value is at the current index
		if idx >= storage_values.len() {
			return Err(Error::InsufficientStorageValues {
				expected: idx + 1,
				got: storage_values.len(),
			});
		}
		let data_slots = bls_data_slots_from_header(&storage_values[idx])?;

		let next_idx = idx.saturating_add(data_slots).saturating_add(2);
		if next_idx > storage_values.len() {
			return Err(Error::InsufficientStorageValues {
				expected: next_idx,
				got: storage_values.len(),
			});
		}

		let validator_keys = layout.get_validator_keys::<H>(&pool_id, data_slots);
		keys.extend(validator_keys);

		idx = next_idx;
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

**File:** modules/consensus/pharos/verifier/src/state_proof.rs (L616-622)
```rust
		// Data is stored at keccak256(string_slot) for `bls_data_slot_count` slots
		let bls_data_base = self.string_data_slot::<H>(&bls_string_slot);
		let bls_data_base_pos = U256::from_big_endian(bls_data_base.as_bytes());
		for i in 0..bls_data_slot_count {
			let slot_pos = bls_data_base_pos + U256::from(i);
			keys.push(H256(slot_pos.to_big_endian()));
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
