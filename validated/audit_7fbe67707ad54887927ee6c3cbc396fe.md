### Title
Unbounded BLS string-length integer drives unbounded key-vector allocation in Pharos validator-set proof verification - (File: `modules/consensus/pharos/verifier/src/state_proof.rs`)

### Summary
`compute_all_storage_keys` and `get_validator_keys` derive a per-validator "number of BLS data slots" directly from an attacker/relayer-supplied storage value (`bls_data_slots_from_header`) and use it, unchecked, as the bound of a loop that pushes `H256` keys into a `Vec`. Unlike the `activePoolSets` count (bounded by `MAX_VALIDATORS = 4096`), this derived slot count has no upper bound, allowing a single relayed Pharos consensus/state proof to force the verifier to allocate and iterate over an astronomically large vector before any cryptographic (Merkle) check of that value is performed — a direct analog of CVE-2018-20699's "attacker-controlled large integer drives unbounded resource consumption."

### Finding Description
`verify_validator_set_proof` first calls `compute_all_storage_keys`, which for each claimed validator reads the (as-yet unverified) storage value for that validator's BLS public-key string header and computes the number of associated data slots via `bls_data_slots_from_header`: [1](#0-0) 

For a "long string" encoding, `str_len = (header_val - 1) / 2`, truncated to a `u64` via `.low_u64() as usize`, and the number of slots returned is `(str_len + 31) / 32`. `header_val` is decoded straight from `storage_values[idx]`, an attacker/relayer-supplied byte array, with no upper bound on its value: [2](#0-1) 

This unbounded `data_slots` value is passed into `get_validator_keys`, which loops `for i in 0..bls_data_slot_count` pushing one `H256` (32 bytes) per iteration with no cap: [3](#0-2) 

Crucially, this key-derivation/allocation happens in `compute_all_storage_keys` *before* `verify_all_storage_proofs` checks any Merkle proof against the real state root: [4](#0-3) 

While the number of validators (`count`) is capped at `MAX_VALIDATORS = 4096`: [5](#0-4) [6](#0-5) 

the per-validator `data_slots` value has no equivalent cap, so even a single malicious validator entry can drive `bls_data_slot_count` up to roughly `2^64/32 ≈ 5.76×10^17`, which `get_validator_keys` will attempt to materialize into a `Vec<H256>` before the corresponding storage proof for that header value is ever checked against `state_root`.

### Impact Explanation
An unprivileged relayer/prover submitting a Pharos consensus/state update can craft `storage_values` that claim an enormous BLS-string length for a validator. Processing this update causes the node (or the runtime executing `verify_validator_set_proof`/`verify_current_epoch_proof`-adjacent code) to attempt to allocate and iterate a vector sized by an attacker-chosen 64-bit-derived integer, exhausting memory/CPU and causing a denial of service on the light client / consensus verification path before the forged length is ever proven against the real state root. This blocks the Pharos consensus client from processing legitimate updates, which is a "route unable to deliver messages" condition for that state machine.

### Likelihood Explanation
Reaching this code only requires submitting a state/consensus proof for the Pharos validator set with a crafted storage value for a validator's BLS-string header slot — no special privileges, governance, or prior state are needed. The attacker fully controls `storage_values[idx]` prior to Merkle validation, so this is trivially triggerable by any party able to submit a Pharos consensus update.

### Recommendation
Enforce a strict, protocol-consistent upper bound on `bls_data_slots_from_header`'s output (e.g., cap `str_len` to a realistic BLS public-key string length such as 128 bytes, matching the expected 48/96/98-byte key encodings) and reject any header value exceeding it with an error before it is used to size any loop or allocation in `get_validator_keys` / `compute_all_storage_keys`.

### Proof of Concept
1. Construct a `ValidatorSetProof` whose `storage_values[1]` (active pool set length) is small and valid, but whose corresponding BLS string header value (`storage_values[idx]` for a chosen validator) decodes so that `lowest_byte & 1 == 1` (long-string flag) and `header_val` is set near `U256::MAX` (or any value making `(header_val - 1) / 2` truncate to a near-`u64::MAX` `str_len`).
2. Submit this as part of a Pharos consensus/state update via the normal relayer path into `verify_validator_set_proof`.
3. `bls_data_slots_from_header` returns `data_slots ≈ (u64::MAX)/32`, and `compute_all_storage_keys`/`get_validator_keys` attempt to build a `Vec<H256>` of that size, causing excessive memory allocation/CPU consumption — long before `verify_all_storage_proofs` ever validates the forged header value against `state_root`.

### Citations

**File:** modules/consensus/pharos/verifier/src/state_proof.rs (L39-39)
```rust
const MAX_VALIDATORS: usize = 4096;
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

**File:** modules/consensus/pharos/verifier/src/state_proof.rs (L309-313)
```rust
	let count = decode_u256_from_storage(&storage_values[1])?.low_u64() as usize;

	if count > MAX_VALIDATORS {
		return Err(Error::TooManyValidators { count, max: MAX_VALIDATORS });
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

**File:** modules/consensus/pharos/verifier/src/state_proof.rs (L639-652)
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
```

**File:** modules/consensus/pharos/verifier/src/state_proof.rs (L656-668)
```rust
pub fn decode_u256_from_storage(value: &[u8]) -> Result<U256, Error> {
	if value.is_empty() {
		return Ok(U256::zero());
	}

	if value.len() <= 32 {
		let mut padded = [0u8; 32];
		padded[32 - value.len()..].copy_from_slice(value);
		Ok(U256::from_big_endian(&padded))
	} else {
		Err(Error::StorageValueTooLarge)
	}
}
```
