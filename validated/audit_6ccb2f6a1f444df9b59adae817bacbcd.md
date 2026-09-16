### Title
Unbounded integer arithmetic on attacker-influenced BLS string length causes `Vec::with_capacity` panic in Pharos consensus verification - (File: `modules/consensus/pharos/verifier/src/state_proof.rs`)

### Summary
`decode_bls_key_from_string_slot` and `bls_data_slots_from_header` in the Pharos consensus verifier derive a string length (`str_len`) from a raw on-chain storage slot value without validating that it is a sane, small size before using it in arithmetic and allocation. `str_len` is only bounded by `u64::MAX` (via `U256::low_u64()`), so a crafted BLS-public-key storage slot on the Pharos staking contract can drive `Vec::with_capacity(str_len)` to request an allocation that exceeds Rust's `isize::MAX` capacity limit, which is a guaranteed, unconditional panic in `Vec::with_capacity` — not a recoverable error. This mirrors the CVE's bug class: an integer/length value taken from untrusted, "escaped"/decoded input is used unchecked in a buffer-sizing operation, producing memory-safety-adjacent failure (here, a hard Rust panic/abort) instead of the intended `Result` error path.

### Finding Description
In `modules/consensus/pharos/verifier/src/state_proof.rs`: [1](#0-0) 

```rust
// Long string: header contains (length * 2 + 1)
let length = (header_val - 1) / 2;
let str_len = length.low_u64() as usize;
...
let slots_needed = (str_len + 31) / 32;
if data_slots.len() < slots_needed { ... }
let mut string_data = Vec::with_capacity(str_len);
```

`header_val` is a `U256` decoded from a raw storage-proof value (`decode_u256_from_storage`). The high 192 bits of this `U256` are silently discarded by `.low_u64()`, so an attacker who controls the corresponding storage slot content on the real Pharos staking contract can make `str_len` an arbitrary value up to `u64::MAX`, regardless of the "true" size of any string. The same truncation and unchecked usage exist in the sibling helper: [2](#0-1) 

No upper bound is enforced on `str_len` anywhere before it reaches `Vec::with_capacity(str_len)`. `Vec::with_capacity` panics with `"capacity overflow"` whenever the requested capacity multiplied by the element size exceeds `isize::MAX` — an unconditional abort, unlike a normal allocation failure, and unlike every other error condition in this module which is surfaced as `Result<_, Error>`.

This function is reached from the fully permissionless, unsigned `pallet-ismp` message-handling path:

- `pallet_ismp::Pallet::handle_unsigned` (unsigned extrinsic, `ensure_none` origin) → `Self::execute(messages)` [3](#0-2) 
- which for a `Message::Consensus` dispatches to `ConsensusClient::verify_consensus` for the Pharos client: [4](#0-3) 
- → `verify_pharos_block` → on an epoch-boundary update → `state_proof::verify_validator_set_proof` → `decode_validator_set_from_storage` → `decode_bls_key_from_string_slot`: [5](#0-4) 

Note that `ValidateUnsigned::validate_unsigned` for `pallet-ismp` also unconditionally calls `Self::execute(messages.clone())` while merely *validating* an incoming transaction for the pool: [6](#0-5) . This means the vulnerable code runs on every node that merely receives the malicious extrinsic over the p2p mempool gossip layer, not only on a node that includes it in a block — and again unconditionally on every node during actual block execution when the extrinsic is included (`pre_dispatch` is a no-op, so the panic-prone dispatch body always runs).

Although `header_val` must correspond to a value that passes the real Merkle/state-proof verification against the trusted Pharos state root (`spv::verify_proof` inside `verify_all_storage_proofs`), that only proves the value is *authentic on-chain data* at that slot — it does not constrain its magnitude. Any account able to register/update a validator's BLS public key string field on the real Pharos staking contract (a normal, permissionless on-chain action on the Pharos side) can plant an oversized "long string" header there. Once that state exists, any permissionless Hyperbridge relayer that later relays the corresponding epoch-boundary consensus update triggers the panic on every Hyperbridge node that processes or even just receives the extrinsic.

### Impact Explanation
This is reachable via a single relayed consensus proof / unsigned extrinsic (`handle_unsigned`), matching the "relayer submits a proof" attack surface explicitly in scope. The impact is a hard Rust panic (`"capacity overflow"`) rather than a graceful `Err(...)`, which:
- Aborts extrinsic validation on every node that merely receives the transaction via gossip (denial-of-service against transaction-pool processing network-wide), and
- If included in a block, aborts extrinsic dispatch during block execution on every full node importing that block — a route (the Pharos consensus/state-machine route) becoming unable to deliver or process further messages until a runtime fix is deployed.

This lines up with the "route unable to deliver messages" acceptance criterion, and is the direct structural analog of the reported CVE's "integer overflow in length-derived value causing corrupted allocation size / DoS."

### Likelihood Explanation
Likelihood is moderate: it requires (a) control over a BLS-public-key string storage slot on the actual Pharos staking contract (achievable by any account able to register/update as a Pharos validator on the source chain, a permissionless action on that chain), and (b) a permissionless relayer relaying the resulting epoch-boundary block to Hyperbridge (also permissionless, and economically incentivized to relay all valid updates). No Hyperbridge-side privilege or governance action is required.

### Recommendation
Bound `str_len` to a small sane maximum (e.g. the expected ≤98-character BLS key length) immediately after decoding it and before using it in any arithmetic or `Vec::with_capacity` call, in both `decode_bls_key_from_string_slot` and `bls_data_slots_from_header`. Use checked/saturating arithmetic for `str_len + 31` and reject the proof with a typed `Error` (e.g. `InvalidBlsStringLength`) rather than allowing an unchecked value to reach an allocation call that can panic.

### Proof of Concept
1. On the Pharos chain, as any account permitted to set a validator's `blsPublicKey` string field, write a "long string" encoding into that field's storage slot such that the header value's low 64 bits, after `(header_val - 1) / 2`, are close to `u64::MAX` (e.g., set the low 8 bytes of the slot so that `low_u64()` of `(header_val-1)/2` yields a value like `0xFFFF_FFFF_FFFF_FFFF - 30`).
2. Wait for/trigger the epoch boundary containing this validator's data so a `ValidatorSetProof` including this slot is produced.
3. As any permissionless relayer, submit a `pallet_ismp::Call::handle_unsigned` extrinsic carrying a `Message::Consensus` for the Pharos consensus client with this epoch-boundary `VerifierStateUpdate`/`ValidatorSetProof`.
4. Any node that validates (`validate_unsigned`) or executes (`handle_unsigned` dispatch body) this extrinsic calls `decode_bls_key_from_string_slot`, which executes `Vec::with_capacity(str_len)` with `str_len` near `u64::MAX`, triggering an unconditional Rust `"capacity overflow"` panic instead of returning `Err(Error::...)`.

### Citations

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

**File:** modules/pallets/ismp/src/lib.rs (L370-382)
```rust
		#[pallet::weight(weight())]
		#[pallet::call_index(0)]
		#[frame_support::transactional]
		pub fn handle_unsigned(
			origin: OriginFor<T>,
			messages: Vec<Message>,
		) -> DispatchResultWithPostInfo {
			ensure_none(origin)?;

			Self::execute(messages.clone())?;

			Ok(().into())
		}
```

**File:** modules/pallets/ismp/src/lib.rs (L614-626)
```rust
		fn validate_unsigned(_source: TransactionSource, call: &Self::Call) -> TransactionValidity {
			use ismp::{
				messaging::{hash_request, ConsensusMessage, FraudProofMessage, RequestMessage},
				router::Request,
			};
			let messages = match call {
				Call::handle_unsigned { messages } => messages,
				_ => Err(TransactionValidityError::Invalid(InvalidTransaction::Call))?,
			};

			let events =
				Self::execute(messages.clone()).map_err(|_| InvalidTransaction::BadProof)?;

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
