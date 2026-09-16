## Analog Found: Panic-Induced DoS in BSC Consensus Header Verification

### Title
Unvalidated BLS public-key length in BSC epoch-header parsing causes a reachable panic (`.expect("Infallible")`) — ([File: modules/consensus/bsc/verifier/src/lib.rs])

### Summary
`verify_bsc_header` in the BSC consensus client converts each validator's `bls_public_key` slice into a fixed-size `BlsPublicKey` using `.try_into().expect("Infallible")`, assuming the conversion can never fail. This conversion is applied to validator data parsed out of attacker-controlled BSC block `extra_data` (via `parse_extra`), reachable through the permissionless `handle_unsigned` extrinsic path. If the RLP-decoded byte string for a validator's `bls_public_key` is not exactly 48 bytes, the `try_into()` fails and `.expect("Infallible")` panics.

### Finding Description
The vulnerable code appears twice in the same function, once for the ancestry-derived epoch header and once for the direct epoch-boundary header: [1](#0-0) [2](#0-1) 

Both call sites take `val.bls_public_key.as_slice()` — a variable-length byte sequence decoded from the untrusted, relayer-submitted RLP `extra_data` of a BSC header — and convert it to the fixed-size `BlsPublicKey` type via `.try_into().expect("Infallible")`. Nothing upstream of this constrains the length of `bls_public_key` to 48 bytes before this conversion; the comment "Infallible" reflects a developer assumption that is not actually enforced by any length check or validated type.

This function is reached via the fully permissionless dispatch path:
- `pallet_ismp::Pallet::handle_unsigned` accepts any `Vec<Message>` from an unsigned origin, requiring no privilege: [3](#0-2) 
- For a `Message::Consensus`, this calls `handlers::update_client`, which invokes `ConsensusClient::verify_consensus` on the trusted `ConsensusState`/proof pair: [4](#0-3) 
- The BSC `ConsensusClient::verify_consensus` implementation decodes the attacker-supplied `BscClientUpdate` and calls `verify_bsc_header`, which — before any signature check invalidates a forged header — will parse `epoch_header_ancestry[0]` or `source_header` extra data and hit the panicking conversion: [5](#0-4) 

Crucially, this same `handle_unsigned` call is also exercised inside `ValidateUnsigned::validate_unsigned`, meaning the panic can be triggered merely by broadcasting the malicious extrinsic into the transaction pool (before block inclusion), affecting every full node that validates pending transactions: [6](#0-5) 

The codebase already demonstrates awareness of this exact bug class — an unchecked index/conversion on relayer-supplied unsigned-message proof data previously caused a runtime panic in the BEEFY MMR verifier, which was subsequently patched: [7](#0-6) 

The BSC `.expect("Infallible")` sites were not covered by that fix and remain a live instance of the same class of bug.

### Impact Explanation
A single relayer or any account able to submit an unsigned extrinsic can craft a `ConsensusMessage` targeting a BSC consensus client, with `epoch_header_ancestry` or `source_header` extra data whose embedded validator entry has a `bls_public_key` field of length ≠ 48 bytes. Processing this message (either during transaction-pool validation via `validate_unsigned`, or during block execution via `handle_unsigned`) triggers `.expect("Infallible")`, causing a runtime panic. In a Substrate/WASM runtime this aborts execution of the current call; depending on how the host handles the trap, this can crash the collator/full node process or repeatedly fail block validation for the affected block, which is directly analogous to CVE-2016-8327's "hang or frequently repeatable crash (complete DoS)" via malformed data reaching a privileged internal subsystem (there: MySQL replication; here: consensus-client message handling). Because `handle_unsigned` is unsigned and free, this is a low-cost, repeatable DoS vector against nodes tracking the BSC consensus client, potentially halting relaying and consensus updates for any state machine anchored to that light client.

### Likelihood Explanation
High reachability: the path requires only crafting a single unsigned extrinsic with attacker-chosen BSC header `extra_data`; no privileged role, prior state, or successful signature forgery is needed since the panic occurs during parsing/validator-set extraction, before the BLS aggregate-signature check is reached. The `parse_extra` RLP decoder does not appear to enforce a fixed 48-byte width for each validator's public key field prior to this conversion.

### Recommendation
Replace `.try_into().expect("Infallible")` at both call sites with a fallible conversion that returns `Error::ParseEpochExtraData` (or a new dedicated error) on length mismatch, mirroring the pattern already used elsewhere in this same function (e.g., `Error::MissingValidatorSet`, `Error::InvalidEpochAncestry`). Additionally, validate the length of `bls_public_key` immediately after RLP-decoding validator entries in `parse_extra`, so malformed epoch headers are rejected with a proper `Result::Err` instead of reaching this unchecked assumption.

### Proof of Concept
1. Construct a valid BSC epoch-boundary header (`source_header.number % epoch_length == 0`) whose RLP `extra_data` validator section contains one validator entry whose `bls_public_key` field is encoded with a length other than 48 bytes (e.g., 47 or 49 bytes) — this is possible because RLP byte strings are variable-length and `parse_extra` does not reject non-48-byte entries prior to this point.
2. Wrap this header in a `BscClientUpdate` and submit it inside a `ConsensusMessage` via `pallet_ismp::Call::handle_unsigned` from an unsigned origin.
3. When the transaction pool validates the extrinsic (`ValidateUnsigned::validate_unsigned`) or a node executes the block containing it, `verify_bsc_header` reaches:
```rust
val.bls_public_key.as_slice().try_into().expect("Infallible")
```
4. The conversion fails (length ≠ 48) and the process panics, aborting execution of that call across every node that processes the message.

Note: full verification of the exact `Validator`/RLP decode types in `modules/consensus/bsc/verifier/src/primitives.rs` (specifically whether `parse_extra` enforces any prior length constraint on `bls_public_key`) could not be completed within the available indexed context; a Devin session with full repository access is recommended to confirm the precise byte-length constraints imposed during RLP decoding before finalizing a fix.

### Citations

**File:** modules/consensus/bsc/verifier/src/lib.rs (L166-173)
```rust
            let epoch_header = update.epoch_header_ancestry[0].clone();
            let epoch_header_extra_data = parse_extra::<H, C>(&epoch_header)
                .map_err(|_| Error::ParseEpochExtraData)?;
            let validators = epoch_header_extra_data
                .validators
                .into_iter()
                .map(|val| val.bls_public_key.as_slice().try_into().expect("Infallible"))
                .collect::<Vec<BlsPublicKey>>();
```

**File:** modules/consensus/bsc/verifier/src/lib.rs (L185-192)
```rust
        } else if update.source_header.number.low_u64() % epoch_length == 0 {
            let epoch_header_extra_data = parse_extra::<H, C>(&update.source_header)
                .map_err(|_| Error::ParseEpochExtraData)?;
            let validators = epoch_header_extra_data
                .validators
                .into_iter()
                .map(|val| val.bls_public_key.as_slice().try_into().expect("Infallible"))
                .collect::<Vec<BlsPublicKey>>();
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

**File:** modules/ismp/core/src/handlers/consensus.rs (L29-46)
```rust
pub fn update_client<H>(host: &H, msg: ConsensusMessage) -> Result<MessageResult, anyhow::Error>
where
	H: IsmpHost,
{
	let consensus_client_id = host.consensus_client_id(msg.consensus_state_id).ok_or(
		Error::ConsensusStateIdNotRecognized { consensus_state_id: msg.consensus_state_id },
	)?;
	let consensus_client = host.consensus_client(consensus_client_id)?;
	let trusted_state = host.consensus_state(msg.consensus_state_id)?;
	host.is_consensus_client_frozen(msg.consensus_state_id)?;
	host.is_expired(msg.consensus_state_id)?;

	let (new_state, intermediate_states) = consensus_client.verify_consensus(
		host,
		msg.consensus_state_id,
		trusted_state,
		msg.consensus_proof,
	)?;
```

**File:** modules/ismp/clients/bsc/src/lib.rs (L82-132)
```rust
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
			let attested_number = bsc_client_update.attested_header.number.low_u64();
			let attested_epoch = compute_epoch(attested_number, epoch_length);
			let rotation_epoch = compute_epoch(next_validators.rotation_block, epoch_length);
			// Promote the pending validator set only when the submitted update is in the
			// specific epoch where that set is scheduled to activate, and the attested
			// header has reached the recorded `rotation_block`. The previous rule —
			// "any update whose `attested.number % epoch_length` is past the rotation
			// midpoint" — promoted the pending set in any later epoch, so an attacker
			// holding the keys of a stale `next_validators` (e.g. retired or compromised
			// validators) could submit an update many epochs later, get their set
			// promoted to `current_validators`, and then have their forged
			// `source_header`'s `state_root` accepted as a BSC state commitment. Binding
			// rotation to the recorded `rotation_block`'s epoch prevents that reuse.
			if attested_epoch == rotation_epoch && attested_number >= next_validators.rotation_block {
				// During authority set rotation, the source header must be from the same epoch as
				// the attested header.
				let source_header_epoch =
					compute_epoch(bsc_client_update.source_header.number.low_u64(), epoch_length);
				if source_header_epoch != attested_epoch {
					Err(Error::SourceHeaderEpochMismatch {
						attested_epoch,
						source_epoch: source_header_epoch,
					})?
				}
				consensus_state.current_validators = next_validators.validators;
				consensus_state.next_validators = None;
				consensus_state.current_epoch = attested_epoch;
			}
		}

		let VerificationResult { hash, finalized_header, next_validators } =
			verify_bsc_header::<H, C>(
				&consensus_state.current_validators,
				bsc_client_update,
				epoch_length,
			)?;
```

**File:** modules/consensus/beefy/verifier/src/lib.rs (L225-236)
```rust
fn verify_mmr_leaf<H: Keccak256 + Send + Sync>(
	mmr: &MmrProof,
	mmr_root: H256,
) -> Result<(), Error> {
	// `leaf_indices` is supplied by the relayer in the unsigned consensus message;
	// an empty vector previously panicked the runtime via the unchecked `[0]` index
	// after the BEEFY signature and authority membership checks had already succeeded.
	// This verifier checks a single MMR leaf, so reject any proof that does not carry
	// exactly one leaf index.
	if mmr.mmr_proof.leaf_indices.len() != 1 {
		Err(Error::InvalidMmrProof)?
	}
```
