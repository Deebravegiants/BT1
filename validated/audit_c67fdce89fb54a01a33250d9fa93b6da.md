## Title
Integer overflow panic in `bls_data_slots_from_header` on unverified Pharos storage-proof header values - (File: `modules/consensus/pharos/verifier/src/state_proof.rs`)

### Summary
The Pharos light-client validator-set-proof verifier computes the number of BLS "string" data slots to expect from a **claimed, not-yet-verified** storage value taken directly from the relayer-supplied proof. The computation `(str_len + 31) / 32` performs an unchecked `usize` addition on a value derived from an attacker-controlled 256-bit field, which can be driven close to `usize::MAX`, triggering an arithmetic-overflow panic. This mirrors CVE-2017-5333's root cause: an integer overflow in a size-derivation routine that is fed directly from untrusted, unvalidated input before any bounds/crypto check is performed.

### Finding Description
`compute_all_storage_keys` is called first inside `verify_validator_set_proof`, **before** `verify_all_storage_proofs` runs the actual Merkle/state-proof check: [1](#0-0) 

Within `compute_all_storage_keys`, for each validator the code calls `bls_data_slots_from_header(&storage_values[idx])`, where `storage_values` is attacker-supplied and has not yet been checked against the state root: [2](#0-1) 

`bls_data_slots_from_header` decodes an arbitrary 32-byte value into a `U256`, derives `length = (header_val - 1) / 2`, truncates it to a `u64`/`usize` via `low_u64()`, and then performs `(str_len + 31) / 32`: [3](#0-2) 

Because `header_val` is fully attacker-controlled (it is merely a byte blob the relayer places in `storage_values`, not yet checked against `storage_proof`/`state_root`), `low_u64()` can return any `u64` value, including one in the range `[usize::MAX - 30, usize::MAX]`. The subsequent `str_len + 31` then overflows `usize`. In a Substrate runtime built with `overflow-checks` enabled (the standard configuration for on-chain arithmetic correctness), this triggers a Rust arithmetic-overflow panic, which traps the WASM execution and causes the extrinsic/consensus-update to abort abnormally rather than being rejected gracefully via an `Err(...)`. This is functionally the same bug class as the external CVE: a size/length value computed via unchecked arithmetic on attacker data, prior to any validation, leading to a crash.

The identical unchecked-arithmetic pattern also exists in `decode_bls_key_from_string_slot`, which is reachable via `decode_validator_set_from_storage` and repeats `(header_val - 1) / 2`, `length.low_u64() as usize`, and `remaining = str_len - (i * 32)`, `slots_needed = (str_len + 31) / 32` on unverified header bytes: [4](#0-3) 

### Impact Explanation
The Pharos validator-set proof path is part of consensus-state verification for the Pharos light client, reachable from a relayed/unsigned consensus update message. Triggering the overflow panic during proof-key computation (before cryptographic verification even runs) allows any party submitting a consensus/validator-set-update message with a crafted `storage_values[idx]` to abort verification via a runtime panic instead of a clean rejection. Depending on how the executor/host handles the WASM trap, this can halt block production/import for that extrinsic, denying the ability to update the Pharos consensus state and thus **preventing message delivery on that route** (a core "route unable to deliver messages" impact per the validation criteria), which qualifies as a Medium/High-severity availability issue for the light client.

### Likelihood Explanation
Likelihood is high: the attacker only needs to submit a `ValidatorSetProof` with one crafted 32-byte "header" value among `storage_values`, with no other proof material required to be valid, since the vulnerable computation runs strictly before the Merkle/state-proof check (`verify_all_storage_proofs`). No special privileges are needed — any relayer able to submit a Pharos consensus/validator-set update can trigger it.

### Recommendation
Replace the unchecked arithmetic in `bls_data_slots_from_header` and `decode_bls_key_from_string_slot` with checked/saturating operations, and clamp/validate `str_len` against a sane maximum (e.g., a small constant like 128 bytes, consistent with the expected 96/98-character BLS key string) immediately after decoding, before performing any further arithmetic:
```rust
let str_len = length.low_u64() as usize;
if str_len > MAX_EXPECTED_STRING_LEN {
    return Err(Error::InvalidBlsStringLength);
}
let slots_needed = str_len.saturating_add(31) / 32;
```
Apply the same guard to `decode_bls_key_from_string_slot`'s `remaining = str_len - (i * 32)` (already order-safe due to the `take` loop bound, but should use `checked_sub`/`saturating_sub` defensively) and to the `(str_len + 31) / 32` computation there as well.

### Proof of Concept
1. Craft a `ValidatorSetProof` where `storage_values[idx]` (the BLS "header" slot for some validator) is a 32-byte value whose lowest byte is odd (marking it as a "long string") and whose decoded `U256` value `header_val` is chosen such that `((header_val - 1) / 2).low_u64()` falls in `[usize::MAX - 30, usize::MAX]` (e.g., set the low 8 bytes of `header_val` to `0xFFFFFFFFFFFFFFFF` while keeping the low bit set to mark it "long").
2. Submit this proof through the Pharos consensus/validator-set update path so it reaches `verify_validator_set_proof` → `compute_all_storage_keys` → `bls_data_slots_from_header`.
3. The expression `(str_len + 31) / 32` overflows `usize`, panicking before `verify_all_storage_proofs` ever runs, aborting the update instead of returning a clean `Err`.

### Citations

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
