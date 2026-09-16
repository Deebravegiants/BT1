### Title
Integer overflow panic in Pharos validator-set proof key derivation, reachable before Merkle proof verification - ([File: modules/consensus/pharos/verifier/src/state_proof.rs])

### Summary
The Nicolet-WFT CVE class is "an untrusted length field is used to size/index a buffer without first validating it against real bounds, causing memory corruption." The closest reachable analog in this codebase is in the Pharos consensus verifier's storage-key derivation, where an attacker-controlled length field encoded in an *unverified* storage value is used in unchecked arithmetic before the Merkle proof that would otherwise attest to that value's authenticity has even been checked.

### Finding Description
`verify_validator_set_proof` [1](#0-0)  first calls `compute_all_storage_keys(&proof.storage_values, &layout)` to derive the storage keys it will check against the state root, and only afterwards calls `verify_all_storage_proofs` to actually verify those keys/values against the trusted `state_root`. This means `proof.storage_values` — fully attacker-controlled, supplied by whoever submits the Pharos consensus/state update — is parsed and used in arithmetic *before* it is cryptographically proven to correspond to real chain state.

Inside `compute_all_storage_keys`, for each claimed validator the code calls `bls_data_slots_from_header(&storage_values[idx])` [2](#0-1) . This function decodes a Solidity "long string" length header directly from attacker-supplied bytes:

```
let length = (header_val - 1) / 2;
let str_len = length.low_u64() as usize;
Ok((str_len + 31) / 32)
```

`str_len` is derived by truncating an arbitrary `U256` to its low 64 bits (`low_u64()`), so an attacker can pick a `header_val` such that `str_len` lands close to `u64::MAX`. The subsequent `str_len + 31` addition is unchecked/non-saturating, unlike the `saturating_add` used a few lines later in `compute_all_storage_keys` [3](#0-2) . Substrate runtimes are conventionally built with overflow checks enabled, so this addition panics on overflow, and even without overflow checks the wrapped value corrupts the derived `slots_needed`/`data_slots` count used to size subsequent slices in `decode_bls_key_from_string_slot` [4](#0-3) , which itself repeats the same unchecked `str_len` computation and uses it to slice/allocate (`Vec::with_capacity(str_len)`, `data_slots.len() < slots_needed` checks based on the same possibly-wrapped arithmetic).

Because none of this data has been checked against the trusted `state_root` yet, the whole computation runs on values that are indistinguishable from garbage to the verifier — exactly the WFT-parser bug class: a length field taken from untrusted input is trusted for arithmetic/sizing ahead of validation.

### Impact Explanation
This code path is invoked whenever a Pharos consensus/state update carrying a `ValidatorSetProof` is processed by the light client verifier (`pharos-verifier`), which is reachable by any relayer submitting such a proof through ISMP's Pharos state-machine/consensus-client update path — an unprivileged, single-message action. A crafted `storage_values` entry can panic the runtime (denial of service against the Pharos light client) before any cryptographic check rejects the bogus data, i.e. before the "false" proof would normally be thrown away. Repeated submission can make the Pharos route on Hyperbridge permanently unable to process consensus/state updates, which the rules explicitly recognize as an acceptable impact ("a route unable to deliver messages"). This is High severity given the ease of triggering and the criticality of the consensus-verification path to security-critical apps built on top of Hyperbridge.

### Likelihood Explanation
Likelihood is high: no privileged role, signature, or state precondition is required to submit a state/consensus proof to this verifier, and the vulnerable computation happens unconditionally before the Merkle-proof check, so a single malformed value in `storage_values` is enough to reach the unchecked arithmetic.

### Recommendation
- Reject or clamp `header_val`/`length`/`str_len` to a sane maximum (e.g. bounded by the actual number of supplied `data_slots`) before doing any arithmetic on it, and use `checked_add`/`saturating_add` consistently everywhere `str_len`, `slots_needed`, and `idx` are combined (mirroring the `saturating_add` already used elsewhere in `compute_all_storage_keys`).
- More fundamentally, verify the Merkle/state proof for each storage value *before* trusting any length/count field decoded from that value, so that attacker-controlled data is only interpreted after being proven genuine against `state_root`.

### Proof of Concept
1. Submit a Pharos state/consensus update whose `ValidatorSetProof.storage_values` includes, at the BLS-header slot for some validator, a 32-byte value encoding a `U256` `header_val` that is odd (marking it as a "long string") and whose value makes `(header_val - 1)/2` truncate via `low_u64()` to a number within 31 of `u64::MAX` (e.g. `header_val = 2*(u64::MAX - 10) + 1`).
2. Submit this as the relevant relayed message to the Pharos light client's `verify_validator_set_proof` entry point (via the normal ISMP consensus/state-machine update flow for the Pharos state machine).
3. `compute_all_storage_keys` → `bls_data_slots_from_header` computes `str_len + 31`, which overflows `u64`, panicking (or, if overflow checks are disabled, wrapping to a small/incorrect `slots_needed` that corrupts subsequent key derivation) — all before any Merkle proof of the value has been checked.

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

**File:** modules/consensus/pharos/verifier/src/state_proof.rs (L243-256)
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
```

**File:** modules/consensus/pharos/verifier/src/state_proof.rs (L349-349)
```rust
		let next_idx = idx.saturating_add(data_slots).saturating_add(2);
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
