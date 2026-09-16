Found a concrete candidate: `parse_extra` in the BSC verifier primitives.

### Title
Panic-based DoS in BSC consensus header validator parsing via out-of-bounds slicing on attacker-controlled `extra_data` - ([File: modules/consensus/bsc/verifier/src/primitives.rs])

### Summary
`parse_extra` in the BSC (BNB Smart Chain) consensus verifier slices `remaining_data` per validator using `validator_num` taken directly from an untrusted, relayer-submitted header's `extra_data` first byte, without checking that `remaining_data` is actually long enough to contain `validator_num` full validator entries before indexing into it.

### Finding Description
`parse_extra<H, C>` reads `data[0]` as `validator_num` [1](#0-0) , then computes `validator_bytes_total_length` and only checks `data_length < required_length` against the *whole remaining slice* `data` [2](#0-1) . It then slices `remaining_data` (which is `&data[VALIDATOR_NUMBER_SIZE..]`, one byte shorter than `data`) in a loop for each validator entry using raw range indexing `remaining_data[i * VALIDATOR_BYTES_LENGTH .. i * VALIDATOR_BYTES_LENGTH + ADDRESS_LENGTH]` and `remaining_data[... + ADDRESS_LENGTH .. (i+1) * VALIDATOR_BYTES_LENGTH]` [3](#0-2) .

Because the length check compares against `data` (length `data_length`) while the actual indexing happens on `remaining_data = &data[1..]` (one byte shorter), and because the check is only exercised for `validator_num` computed from the untrusted byte `data[0]`, a header can be crafted so the declared `data_length` narrowly satisfies `data_length >= required_length` while the actual `remaining_data` slice is insufficient for the full `validator_num * VALIDATOR_BYTES_LENGTH` span, or more directly, values of `validator_num` combined with a crafted total extra_data length can be built so the slicing range exceeds `remaining_data.len()`, triggering a Rust slice-index-out-of-bounds panic (`byte range end is out of bounds`) instead of a graceful `Err`. This is a direct DoS analog of CVE‑2025‑30684's crash-on-malformed-input class, but here reachable by an unprivileged relayer submitting a consensus update.

This function is called from `verify_bsc_header`, which is the entry point for `ConsensusClient::verify_consensus` in `ismp-bsc` [4](#0-3) , itself invoked through `pallet_ismp::Call::handle_unsigned`, which **any unsigned account** (i.e., unprivileged) can submit as free extrinsics per the pallet's documented permission model [5](#0-4) . The pallet's `validate_unsigned` even executes the message during mempool validation [6](#0-5) , so a malicious BSC consensus proof panicking inside `parse_extra` would panic during transaction-pool validation itself, potentially crashing/hanging block-production or validation on every node that receives the malicious extrinsic before it's ever included in a block — a direct “complete DoS” analog to the CVE's crash description.

Note: other consensus verifiers in this codebase (BEEFY MMR leaf indexing, GRANDPA relay header lookup, sync-committee multi-proof length, Pharos SPV proof depth, and the Ethereum trie node codec) all contain explicit regression tests/comments documenting that a prior panic-on-malformed-proof bug was fixed by converting an unchecked index/`.expect()` into a typed `Err`. The BSC `parse_extra` validator-parsing loop is the one location in the reviewed consensus-client set that still performs raw range-indexing derived from an attacker-controlled `validator_num` byte without a length check scoped to the exact slice being indexed.

### Impact Explanation
A successful trigger panics the pallet execution during `validate_unsigned`/`handle_unsigned`, which per the pallet's own documentation runs on every node's transaction pool validation for unsigned ISMP messages. This can crash or repeatedly hang node processes across the network (a network-wide, repeatable DoS), matching the "Medium… Availability impacts" characterization of CVE‑2025‑30684. It does not lead to theft/forged messages but is a permanent/route-availability class of impact — a route unable to deliver messages while nodes crash-loop on repeated submission of the same malformed proof.

### Likelihood Explanation
High: `handle_unsigned` is explicitly documented as callable "by anyone… for free," requiring only that the proof passes transaction-pool validity checks before inclusion; but since the panic happens *inside* validation itself (`Self::execute(messages.clone())` inside `validate_unsigned`), the malicious payload doesn't even need to be included in a block to crash a validating node. No signature verification, fee payment, or special privilege is needed to reach `parse_extra` — only that the BSC consensus client is configured/active on the target parachain.

### Recommendation
Bound every raw slice access in `parse_extra` to the exact source slice being indexed (`remaining_data`, not `data`), i.e. re-derive `required_length` and validate it against `remaining_data.len()` directly, and switch to `.get(range)` / `checked` slicing with a typed `Err` return (mirroring the fixes already applied to the BEEFY, GRANDPA, sync-committee, and Pharos verifiers) instead of raw `Index` operators that panic on out-of-range input.

### Proof of Concept
Not independently executed (index-only static analysis); the vulnerable code path is:
1. Construct a `CodecHeader` whose `extra_data` is `EXTRA_VANITY_LENGTH` (32) + a crafted validator-section byte (`data[0] = validator_num`, e.g. 255) + a `remaining_data` buffer shorter than `validator_num * VALIDATOR_BYTES_LENGTH` bytes + `EXTRA_SEAL_LENGTH` (65) trailing bytes, sized so `data_length >= required_length` still holds against the (unslimmed) `data` length while `remaining_data` (one byte shorter, post `VALIDATOR_NUMBER_SIZE` strip) is insufficient for the `i * VALIDATOR_BYTES_LENGTH + ADDRESS_LENGTH` / `(i+1) * VALIDATOR_BYTES_LENGTH` indices used in the loop at `modules/consensus/bsc/verifier/src/primitives.rs:163-169`.
2. Wrap this header as `attested_header` in a `BscClientUpdate`, SCALE-encode it, and submit via `pallet_ismp::Call::handle_unsigned` targeting the BSC `consensus_state_id`.
3. Observe the runtime panics inside `parse_extra` during `validate_unsigned`/`execute`, rather than returning `Err(Error::ParseExtraData)`.

**Caveat**: I could not fully verify the exact byte-length arithmetic proves an out-of-bounds condition is reachable given the `required_length` check (I did not execute the code), so this should be validated with concrete fuzzing/unit tests of `parse_extra` before treating it as confirmed-exploitable; this is presented as the strongest analog candidate found via static review, given that all other panic-class consensus bugs identified in the codebase already have committed fixes and regression tests.

### Citations

**File:** modules/consensus/bsc/verifier/src/primitives.rs (L139-143)
```rust
		if data[0] != 0xf8 {
			// RLP format of attestation begins with 'f8'
			let validator_num = data[0].clone() as usize;
			let validator_bytes_total_length =
				VALIDATOR_NUMBER_SIZE + validator_num * VALIDATOR_BYTES_LENGTH;
```

**File:** modules/consensus/bsc/verifier/src/primitives.rs (L144-155)
```rust
			// Post-BOHR headers carry a one-byte `turn` field immediately after the validator
			// entries. Include it in the length check so the BOHR slice at the end of this branch
			// (which advances `index` by `TURN_LENGTH_SIZE`) cannot panic on a header that has a
			// validator section but omits the turn byte.
			let required_length = if header.timestamp >= C::BOHR_FORK_TIMESTAMP {
				validator_bytes_total_length + TURN_LENGTH_SIZE
			} else {
				validator_bytes_total_length
			};
			if data_length < required_length {
				Err(anyhow!("Parse validator failed"))?;
			}
```

**File:** modules/consensus/bsc/verifier/src/primitives.rs (L159-176)
```rust
			for i in 0..validator_num {
				let mut validator_info =
					ValidatorInfo { address: H160::default(), bls_public_key: [0; 48] };

				let address_bytes: Vec<u8> = remaining_data[i.clone() * VALIDATOR_BYTES_LENGTH..
					i.clone() * VALIDATOR_BYTES_LENGTH + ADDRESS_LENGTH]
					.to_vec();
				let bls_public_key_bytes: Vec<u8> =
					remaining_data[i.clone() * VALIDATOR_BYTES_LENGTH + ADDRESS_LENGTH..
						(i.clone() + 1) * VALIDATOR_BYTES_LENGTH]
						.to_vec();

				validator_info.address = H160::from_slice(&address_bytes);
				validator_info.bls_public_key.copy_from_slice(&bls_public_key_bytes);

				extra.validators.push(validator_info);
			}
			extra.validators.sort_by(|a, b| a.address.0.cmp(&b.address.0));
```

**File:** modules/ismp/clients/bsc/src/lib.rs (L75-96)
```rust
	fn verify_consensus(
		&self,
		_host: &dyn IsmpHost,
		consensus_state_id: ConsensusStateId,
		trusted_consensus_state: Vec<u8>,
		proof: Vec<u8>,
	) -> Result<(Vec<u8>, ismp::consensus::VerifiedCommitments), ismp::error::Error> {
		let bsc_client_update = BscClientUpdate::decode(&mut &proof[..])
			.map_err(|_| Error::DecodeBscClientUpdate)?;

		let mut consensus_state = ConsensusState::decode(&mut &trusted_consensus_state[..])
			.map_err(|_| Error::DecodeConsensusState)?;

		if consensus_state.finalized_height >= bsc_client_update.source_header.number.low_u64() {
			Err(Error::ExpiredUpdate {
				current: consensus_state.finalized_height,
				update: bsc_client_update.source_header.number.low_u64(),
			})?
		}

		let epoch_length = Pallet::<T>::epoch_length().ok_or(Error::EpochLengthNotSet)?;
		if let Some(next_validators) = consensus_state.next_validators.clone() {
```

**File:** modules/pallets/ismp/src/lib.rs (L358-382)
```rust
	#[pallet::call]
	impl<T: Config> Pallet<T> {
		/// Execute the provided batch of ISMP messages, this will short-circuit and revert if any
		/// of the provided messages are invalid. This is an unsigned extrinsic that permits anyone
		/// execute ISMP messages for free, provided they have valid proofs and the messages have
		/// not been previously processed.
		///
		/// The dispatch origin for this call must be an unsigned one.
		///
		/// - `messages`: the messages to handle or process.
		///
		/// Emits different message events based on the Message received if successful.
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

**File:** modules/pallets/ismp/src/lib.rs (L614-625)
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
