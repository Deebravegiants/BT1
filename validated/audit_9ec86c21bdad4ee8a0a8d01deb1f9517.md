### Title
Unbounded length used for `Vec::with_capacity` when decoding a Pharos validator's BLS-key storage string — ([File: modules/consensus/pharos/verifier/src/state_proof.rs])

### Summary
`decode_bls_key_from_string_slot()` in the Pharos consensus verifier decodes a Solidity "long string" storage slot for a validator's BLS public key. It derives a byte length directly from the on-chain storage word and uses it, unchecked and unbounded, to allocate a `Vec` and to size a hex-decoding loop — mirroring the CVE-2024-7264 bug class where a length field parsed from an untrusted, syntactically-permissive encoding is trusted without a sanity bound before being used to size/scan a buffer.

### Finding Description
In the long-string branch of `decode_bls_key_from_string_slot`, the byte length of the BLS-key hex string is computed purely from the raw storage word (`header_val`), with no upper bound check comparable to the `MAX_VALIDATORS` cap used elsewhere in the same file: [1](#0-0) 

```
// Long string: header contains (length * 2 + 1)
let length = (header_val - 1) / 2;
let str_len = length.low_u64() as usize;
...
let slots_needed = (str_len + 31) / 32;
if data_slots.len() < slots_needed { ... }
let mut string_data = Vec::with_capacity(str_len);
```

`header_val` is a `U256` decoded straight from the verified storage word at the validator's BLS-key "header" slot [2](#0-1) . The code only checks that `lowest_byte & 1 == 1` (marking it a "long string") before computing `length = (header_val - 1) / 2` and truncating to `low_u64()`. Nothing constrains `str_len` to a sane maximum (e.g. 128 bytes for a 96/98-character hex key) the way `MAX_VALIDATORS` bounds the validator count earlier in the file [3](#0-2)  and [4](#0-3) .

This header word does pass through `verify_all_storage_proofs`, which authenticates each `storage_values[idx]` against the real Pharos state root before it is used [5](#0-4) , so the value is not fabricated out of thin air by a relayer — it must genuinely exist at that slot in the Pharos staking contract's storage. However, the Hyperbridge-side decoder places no independent trust boundary on the *decoded length itself*: whatever 256-bit word is stored there is taken at face value and converted directly into an allocation size and a slot-count multiplier, exactly the "trust the encoded length without cross-checking it against the syntactic/structural constraints of the format" pattern that caused the GTime2str flaw (an improperly-formed field producing a wildly out-of-range length that is then used unchecked).

### Impact Explanation
If a slot value that yields an attacker-influenceable large `str_len` (e.g. via a bug or unusual encoding path in the staking contract that allows writing to this "string length" header without going through Solidity's normal string-assignment bounds) reaches this code path, `Vec::with_capacity(str_len)` can request a very large allocation. Rust's global allocator aborts the process on allocation failure, and even a successful but very large allocation stalls/consumes node resources. Since this function sits directly in the consensus-update verification path for the Pharos light client (`verify_validator_set_proof` → `decode_validator_set_from_storage` → `decode_bls_key_from_string_slot`) [6](#0-5) [7](#0-6) , a crash here halts processing of new validator-set/consensus updates for the Pharos state machine — i.e., a route becomes unable to deliver/verify further messages until the node is restarted or the offending update is otherwise worked around.

### Likelihood Explanation
Likelihood depends entirely on whether the real Pharos staking contract can be made to store a "long string" header word whose decoded length is abnormally large for the BLS-key field — something this codebase's Rust decoder cannot itself prevent and which is outside this repository (the staking contract's Solidity source is not present here to confirm or rule out). Absent that external precondition, this is a defense-in-depth gap rather than a directly demonstrable exploit from this repo alone: the decoder omits a bound check that the rest of the file consistently applies (`MAX_VALIDATORS`), and I could not verify from the indexed code whether the staking contract enforces short BLS-key strings strongly enough to make this unreachable.

### Recommendation
Add an explicit upper bound on `str_len` (e.g. reject anything above a small constant such as 128 bytes, matching the expected 96/98-character hex BLS key) before computing `slots_needed` or calling `Vec::with_capacity`, mirroring the `MAX_VALIDATORS` guard already used in this file.

### Proof of Concept
Not independently reproducible from this repository alone: constructing a concrete PoC requires demonstrating that the Pharos staking contract can be made to write a storage word at the BLS-key header slot whose decoded "long string" length is abnormally large, which depends on contract logic not present in this codebase.

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

**File:** modules/consensus/pharos/verifier/src/state_proof.rs (L129-133)
```rust
	let count = validator_count.low_u64() as usize;

	if count > MAX_VALIDATORS {
		return Err(Error::TooManyValidators { count, max: MAX_VALIDATORS });
	}
```

**File:** modules/consensus/pharos/verifier/src/state_proof.rs (L181-181)
```rust
		let bls_key = decode_bls_key_from_string_slot(bls_string_slot, Some(&bls_data_slots))?;
```

**File:** modules/consensus/pharos/verifier/src/state_proof.rs (L229-231)
```rust
	let header_val = decode_u256_from_storage(header)?;
	let header_bytes = header_val.to_big_endian();
	let lowest_byte = header_bytes[31];
```

**File:** modules/consensus/pharos/verifier/src/state_proof.rs (L241-258)
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
```

**File:** modules/consensus/pharos/verifier/src/state_proof.rs (L366-399)
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
```
