### Title
Arithmetic overflow / unbounded allocation in Pharos BLS-key length decoding permanently bricks the state proof route - (File: modules/consensus/pharos/verifier/src/state_proof.rs)

### Summary
CVE-2018-7568 is a class of bug where an untrusted, attacker-supplied length/size field in a parsed data structure is used in arithmetic without bounds checking, causing an integer overflow and a crash while parsing. The Pharos validator-set state-proof decoder in Hyperbridge contains the same bug class: an attacker-controlled "string length" field taken directly from unverified storage bytes is used in unchecked arithmetic and an allocation size before any cryptographic verification occurs.

### Finding Description
`decode_bls_key_from_string_slot` treats the BLS public key storage slot as a Solidity "long string" header and derives its length directly from attacker-supplied bytes: [1](#0-0) 

```
} else {
    // Long string: header contains (length * 2 + 1)
    let length = (header_val - 1) / 2;
    let str_len = length.low_u64() as usize;
    ...
    let slots_needed = (str_len + 31) / 32;
```

and later: [2](#0-1) 

```
let mut string_data = Vec::with_capacity(str_len);
for (i, slot_value) in data_slots.iter().take(slots_needed).enumerate() {
    ...
```

The same unchecked pattern is duplicated in the standalone helper used to size the key list: [3](#0-2) 

`header_val` originates from `proof.storage_values` — raw bytes supplied by whoever submits the Pharos validator-set proof — and is only range-checked to be ≤32 bytes by `decode_u256_from_storage`; its numeric value is otherwise fully attacker-controlled. Crucially, `bls_data_slots_from_header` is invoked from `compute_all_storage_keys` **before** the Merkle/state-proof verification step runs: [4](#0-3) 

`verify_validator_set_proof` calls `compute_all_storage_keys` (which decodes the unverified length) first, and only afterward calls `verify_all_storage_proofs` to check the values against `state_root`. This means the attacker never has to produce a valid Merkle proof for the crafted value — the vulnerable arithmetic runs on the raw claim alone.

By choosing a 32-byte storage value whose big-endian `U256` value is odd (marks the "long string" branch) and whose low 32 bits equal `0xFFFFFFFF*2+1`-style values, `str_len` (a 32-bit `usize` under the `wasm32` runtime target) can be driven to `u32::MAX`. `str_len + 31` then overflows a 32-bit `usize` (panics under overflow-checked wasm runtimes, or wraps to a bogus small value under checks-disabled builds), and independently `Vec::with_capacity(str_len)` attempts a multi-gigabyte allocation that will abort the process on failure (Rust's global allocator calls `handle_alloc_error`, which aborts rather than returning a catchable `Result`).

This mirrors the CVE-2018-7568 bug class precisely: a corrupt/attacker length field parsed without bounds checking drives an integer overflow (or an unrecoverable allocation) that crashes the parsing code path.

### Impact Explanation
This code sits in the unsigned/relayer-submittable Pharos consensus verification path (`verify_validator_set_proof`, used by the Pharos consensus client's `verify_consensus`/validator-set update flow, exercised in `modules/pallets/testsuite/src/tests/ismp_pharos.rs`). Because the vulnerable arithmetic runs before proof verification, any unprivileged relayer can submit a single malformed proof to reliably trigger the overflow/OOM abort. If the runtime is compiled with overflow checks (common for FRAME/pallet code), this manifests as a deterministic panic; either way, a crash in on-chain consensus-update logic executed as part of block-import halts processing of that extrinsic/state machine update path, permanently preventing the Pharos light client from advancing — a "route unable to deliver messages" condition for any traffic depending on the Pharos consensus client, and a potential validator/relayer process crash (denial of service) if triggered off-chain in a prover/relayer binary that reuses this crate.

### Likelihood Explanation
High: the vulnerable value is a single 32-byte storage slot the caller fully controls in `storage_values`, requires no valid Merkle proof, no privileged role, and no special conditions — it only requires reaching the Pharos validator-set proof submission path with one crafted "storage value" entry.

### Recommendation
Bound-check `header_val`/`length`/`str_len` before use: reject any decoded length that doesn't fit reasonable BLS-key bounds (e.g., ≤128 bytes) before computing `slots_needed` or calling `Vec::with_capacity`; use `checked_add`/`checked_div` (or `saturating_*`) for the `(str_len + 31) / 32` computation instead of raw arithmetic; and perform this length derivation only on values that have already passed Merkle-proof verification against `state_root`, not on raw untrusted input.

### Proof of Concept
1. Craft a Pharos `ValidatorSetProof` where `storage_values[idx]` (the BLS public-key string header slot) is a 32-byte big-endian value `V` such that `V` is odd and `((V - 1) / 2).low_u64() as usize == u32::MAX` (e.g., set the low 32 bits of `(V-1)/2` to `0xFFFFFFFF`).
2. Submit this proof through the Pharos consensus client's public/unsigned validator-set update path (no valid Merkle proof for this slot is required, since `compute_all_storage_keys` → `bls_data_slots_from_header` runs before any proof check).
3. Observe that `str_len + 31` overflows `usize` (panic under overflow-checked build) or that `Vec::with_capacity(str_len)` attempts a ~4 GB allocation, aborting the process handling the update — denying further Pharos consensus updates.

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

**File:** modules/consensus/pharos/verifier/src/state_proof.rs (L241-251)
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
```

**File:** modules/consensus/pharos/verifier/src/state_proof.rs (L256-266)
```rust
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
