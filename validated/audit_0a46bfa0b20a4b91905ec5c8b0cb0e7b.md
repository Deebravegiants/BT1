Confirmed: `verify_pharos_block` calls `state_proof::verify_validator_set_proof` on epoch-transition, which calls `compute_all_storage_keys` on the raw, **unverified** `proof.storage_values` *before* `verify_all_storage_proofs` cryptographically checks them against the state root. This is exactly the CVE-2016-8620 bug-class analog: a length/count field taken directly from unauthenticated attacker input is used in unchecked arithmetic before validation.

### Title
Integer-overflow/panic in unverified BLS string-length parsing during Pharos validator-set rotation - (File: `modules/consensus/pharos/verifier/src/state_proof.rs`)

### Summary
`bls_data_slots_from_header`, invoked from `compute_all_storage_keys`, parses a Solidity long-string length header taken directly from attacker-supplied, not-yet-verified `storage_values` and performs unchecked `usize` arithmetic (`str_len + 31`) on a value derived from `header_val.low_u64()` of an arbitrary `U256`, before any cryptographic proof check runs.

### Finding Description
`verify_validator_set_proof` [1](#0-0)  first calls `compute_all_storage_keys::<H>(&proof.storage_values, &layout)` and only *afterwards* calls `verify_all_storage_proofs` to check those same values against `state_root`. This ordering means `compute_all_storage_keys` [2](#0-1)  operates on fully attacker-controlled bytes: `proof.storage_values` is submitted as part of an ISMP consensus-update message and is not yet authenticated against any trie root.

Inside that loop, `bls_data_slots_from_header(&storage_values[idx])` is called on this unverified data [3](#0-2) :
```
let header_val = decode_u256_from_storage(header_value)?;
...
let length = (header_val - 1) / 2;
let str_len = length.low_u64() as usize;
Ok((str_len + 31) / 32)
```
`header_val` is an arbitrary `U256` up to `2^256 - 1` fully chosen by whoever submits the consensus proof (it is a raw 32-byte value the caller claims lives at a storage slot, and is not yet checked against `state_root` at this point). `low_u64()` silently truncates the high bits of that `U256`, and the subsequent `str_len + 31` addition is unchecked `usize` arithmetic. With `overflow-checks` enabled (debug builds, or any WASM runtime built with checked arithmetic) a `str_len` near `usize::MAX` causes an arithmetic-overflow panic; the trap aborts the enclosing extrinsic/consensus-update execution before the legitimate cryptographic check ever runs, exactly mirroring how curl's CVE-2016-8620 glob code performed unchecked length/index arithmetic on attacker-controlled input ahead of any bounds validation.

The identical unverified-data-first pattern also drives `count` derivation (`decode_u256_from_storage(&storage_values[1])?.low_u64() as usize`) used to size the loop and index `storage_values[pool_set_start + i]`, all prior to `verify_all_storage_proofs`.

### Impact Explanation
`verify_pharos_block` is the entry point for the Pharos light-client consensus update path, reachable by any unprivileged relayer submitting a `VerifierStateUpdate` with an epoch increment and a crafted `validator_set_proof`. A panic reached here traps the WASM execution of the ISMP consensus-client update, causing that update (and consequently the Pharos state-machine route depending on it) to become permanently unable to process further consensus updates/messages — a denial of the route's message-delivery capability, which the rules explicitly count as in-scope ("a route unable to deliver messages"). Because the vulnerable arithmetic runs strictly before any state-root/Merkle authentication, it is fully attacker-triggerable with a single malformed message and requires no genuine on-chain data to match.

### Likelihood Explanation
High: the field is read straight off attacker-supplied bytes with no prior bound check (`decode_u256_from_storage` only restricts byte length to ≤32, not the encoded value), and the vulnerable code executes unconditionally on every epoch-rotation validator-set proof before any signature/Merkle validation, so it is reachable by any relayer who can submit a consensus update with `observed_epoch == trusted_epoch + 1`.

### Recommendation
- Reorder verification so `verify_all_storage_proofs` (cryptographic authentication against `state_root`) always runs before any derived length/count value from `storage_values` is used in arithmetic or indexing, i.e., authenticate before parsing.
- Replace unchecked `+`/`-` on lengths derived from `U256` values with `checked_add`/`saturating_add` and explicitly reject values whose full `U256` magnitude exceeds a sane maximum (e.g., 128 bytes) rather than truncating via `low_u64()`.
- Apply the same fix to the `count` (`activePoolSets` length) truncation in `compute_all_storage_keys`.

### Proof of Concept
1. Submit a `VerifierStateUpdate` with `observed_epoch == trusted_epoch + 1` and a `ValidatorSetProof` whose `storage_values[1]` (`activePoolSets` length) is a small valid count, but whose `storage_values[idx]` for a validator's BLS header slot encodes an odd (long-string) header value where the upper 192 bits of the `U256` are non-zero such that `header_val.low_u64()` yields a value close to `u64::MAX`.
2. `verify_pharos_block` → `verify_validator_set_proof` → `compute_all_storage_keys` → `bls_data_slots_from_header` computes `str_len = length.low_u64()` near `u64::MAX`; the following `str_len + 31` addition overflows `usize`.
3. In a checked-arithmetic build (or once `overflow-checks` is enabled for the runtime, which is common for parachain/wasm consensus-critical code), this traps before `verify_all_storage_proofs` is ever reached, aborting the update and, depending on the caller's panic-handling boundary, potentially halting further processing of that consensus client's updates. [3](#0-2) [1](#0-0) [4](#0-3)

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

**File:** modules/consensus/pharos/verifier/src/state_proof.rs (L293-364)
```rust
fn compute_all_storage_keys<H: Keccak256>(
	storage_values: &[Vec<u8>],
	layout: &StakingContractLayout,
) -> Result<Vec<H256>, Error> {
	if storage_values.len() < 2 {
		return Err(Error::InsufficientStorageValues { expected: 2, got: storage_values.len() });
	}

	let mut keys = Vec::new();

	// Index 0: totalStake
	keys.push(layout.raw_slot_key(layout.total_stake_slot));

	// Index 1: activePoolSets length
	keys.push(layout.raw_slot_key(layout.active_pool_set_slot));

	let count = decode_u256_from_storage(&storage_values[1])?.low_u64() as usize;

	if count > MAX_VALIDATORS {
		return Err(Error::TooManyValidators { count, max: MAX_VALIDATORS });
	}

	let pool_set_start = 2;
	let pool_ids_end = pool_set_start + count;

	if storage_values.len() < pool_ids_end {
		return Err(Error::InsufficientPoolIds {
			expected: pool_ids_end,
			validators: count,
			got: storage_values.len(),
		});
	}

	// Pool ID array element keys
	for i in 0..count {
		keys.push(layout.array_element_key::<H>(layout.active_pool_set_slot, i as u64));
	}

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
	}

	Ok(keys)
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

**File:** modules/consensus/pharos/verifier/src/lib.rs (L97-113)
```rust
		Ordering::Greater => {
			if observed_epoch != trusted_epoch + 1 {
				return Err(Error::EpochSkipped {
					trusted: trusted_epoch,
					observed: observed_epoch,
				});
			}

			let validator_set_proof = update
				.validator_set_proof
				.ok_or(Error::MissingValidatorSetProof { block_number: update_block_number })?;

			let new_validator_set = state_proof::verify_validator_set_proof::<H>(
				update.header.state_root,
				&validator_set_proof,
				observed_epoch,
			)?;
```
