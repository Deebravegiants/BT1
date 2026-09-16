### Title
Unbounded BLS key string length in Pharos validator-set decoding causes allocation-panic DoS in consensus verification - (File: modules/consensus/pharos/verifier/src/state_proof.rs)

### Summary
`decode_bls_key_from_string_slot` in the Pharos consensus verifier decodes a Solidity "long string" length directly from a storage-proof value and uses it, unbounded, in `Vec::with_capacity(str_len)` and in an unchecked `str_len + 31` addition. A legitimately-registered Pharos validator can set the BLS-key header slot in the staking contract to an adversarial value so that any future `verify_validator_set_proof` call that must include this validator panics, permanently breaking Pharos validator-set updates on Hyperbridge — the same bug class as CVE-2018-14598 (an unvalidated length field from untrusted/remote data corrupting downstream memory handling and crashing the consumer).

### Finding Description
`verify_validator_set_proof` [1](#0-0)  first verifies each storage value against the state root via Merkle proof, then calls `decode_validator_set_from_storage`, which for every validator calls `decode_bls_key_from_string_slot` on the BLS-key header slot [2](#0-1) .

Inside `decode_bls_key_from_string_slot`, for the Solidity "long string" branch the code computes:
```
let length = (header_val - 1) / 2;
let str_len = length.low_u64() as usize;
...
let slots_needed = (str_len + 31) / 32;
if data_slots.len() < slots_needed { return Err(...) }
let mut string_data = Vec::with_capacity(str_len);
``` [3](#0-2) 

`header_val` is only bounded to 32 bytes by `decode_u256_from_storage` [4](#0-3) , but `low_u64()` truncates the derived length to the low 64 bits with no upper bound check against a sane string size (e.g. the expected 96/98-character BLS hex string). This lets `str_len` be crafted up to `u64::MAX`, which either:
- panics on `str_len + 31` (arithmetic overflow, if overflow-checks are enabled in the runtime build), or
- reaches `Vec::with_capacity(str_len)` with an enormous value, which panics with a capacity/allocation error.

Because verification of the storage proof happens *before* this decode step, the only requirement for exploitation is that the malicious header value is genuinely committed in the staking contract's storage (i.e., an actual, currently-registered validator's BLS-key slot on the Pharos chain) — not a fabricated proof. Since Pharos validators self-register and control the content written to their own BLS key storage slot, an unprivileged validator can set this header field to a poisoned value once, and from then on every relayed consensus/validator-set proof that must enumerate the active validator set (which necessarily includes this validator) will panic when decoded by Hyperbridge's Pharos light client.

### Impact Explanation
A single malicious/self-registered Pharos validator can permanently break Hyperbridge's ability to ingest new Pharos validator-set (consensus) proofs, since every future `verify_validator_set_proof` call touching that validator's storage slot panics deterministically. This freezes the Pharos consensus client route — no further state/consensus updates for the Pharos state machine can be delivered, which blocks all downstream cross-chain messages that depend on Pharos state proofs (a "route unable to deliver messages" condition), qualifying as High severity per the rules (unsound consensus verification / permanent freezing of a message route).

### Likelihood Explanation
Likelihood is high for a determined validator: registering a BLS key with a crafted header slot is a one-time, low-cost, self-contained action requiring no special privilege beyond being a Pharos validator (same actor class as the "state membership/consensus verification" reachable paths explicitly in scope), and it deterministically poisons all subsequent verification attempts touching that validator.

### Recommendation
Bound `str_len` to a sane maximum (e.g., the expected 96–98 character BLS key length, or at most 32 * data_slots.len() from the actually supplied slots) before computing `slots_needed` or allocating, and use checked arithmetic (`checked_add`/`checked_mul`) instead of raw `+`/`Vec::with_capacity` on a value derived directly from untrusted storage. Reject the proof with a typed error (e.g. `InvalidBlsStringLength`) instead of allowing decode to reach an unbounded allocation or unchecked addition.

### Proof of Concept
1. A Pharos validator registers/updates their BLS key storage such that the header slot value `header_val` decodes (via `(header_val - 1) / 2`) to a `low_u64()` in the range `[u64::MAX-30, u64::MAX]` (long-string marker: `header_val` odd).
2. Any relayer subsequently submits a legitimate `ValidatorSetProof` covering the current validator set (which must include this validator) to Hyperbridge's Pharos consensus client.
3. `verify_validator_set_proof` → `decode_validator_set_from_storage` → `decode_bls_key_from_string_slot` computes `str_len` from the poisoned header, then evaluates `str_len + 31` (overflow panic) or `Vec::with_capacity(str_len)` (allocation panic), aborting verification for every subsequent submission touching this validator, permanently blocking Pharos consensus updates.

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

**File:** modules/consensus/pharos/verifier/src/state_proof.rs (L161-181)
```rust
		// BLS header at current index
		if idx >= values.len() {
			return Err(Error::InsufficientStorageValues { expected: idx + 1, got: values.len() });
		}
		let data_slots = bls_data_slots_from_header(&values[idx])?;

		let bls_string_slot = &Some(values[idx].clone());
		idx += 1;

		// BLS data slots (dynamic count)
		if idx + data_slots > values.len() {
			return Err(Error::InsufficientStorageValues {
				expected: idx + data_slots,
				got: values.len(),
			});
		}
		let bls_data_slots: Vec<Option<Vec<u8>>> =
			values[idx..idx + data_slots].iter().map(|v| Some(v.clone())).collect();
		idx += data_slots;

		let bls_key = decode_bls_key_from_string_slot(bls_string_slot, Some(&bls_data_slots))?;
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
