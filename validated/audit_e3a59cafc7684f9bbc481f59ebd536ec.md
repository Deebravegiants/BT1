## Title
Unbounded BEEFY signature-recovery loop reachable via free unsigned `handle_unsigned` extrinsics enables mempool CPU-exhaustion DoS - (File: `modules/consensus/beefy/verifier/src/lib.rs`)

### Summary
`verify_mmr_update_proof` in the BEEFY consensus verifier iterates over every signature in an attacker-supplied `signed_commitment.signatures` vector and performs a full `secp256k1_recover` for each one, with no upper bound on the vector's length. This function runs to completion inside `pallet_ismp::ValidateUnsigned::validate_unsigned`, which is invoked for every gossiped `handle_unsigned` extrinsic before any fee is charged — the same "attacker-controlled count drives an unbounded loop of expensive work with no early size check" bug class as CVE-2017-14175's XBM row/column loop.

### Finding Description
`pallet-ismp` intentionally allows anyone to submit ISMP messages, including consensus updates, as unsigned, fee-less extrinsics via `handle_unsigned`: [1](#0-0) 

Its `ValidateUnsigned::validate_unsigned` implementation actually executes the full message batch — not a lightweight pre-check — before the extrinsic is admitted to the pool or a block: [2](#0-1) 

When the batch contains a `Message::Consensus` targeting a BEEFY consensus client, this routes into `verify_mmr_update_proof`, which loops over `relayProof`/`mmr.signed_commitment.signatures` performing one `secp256k1_recover` per entry: [3](#0-2) 

The only check applied to `signatures_length` is a **lower**-bound supermajority threshold: [4](#0-3) 

There is no upper bound on `mmr.signed_commitment.signatures.len()` before the expensive recovery loop runs. An attacker can pad the vector with garbage 65-byte signature entries (bounded only by the extrinsic/block size limit, not by any semantic cap), driving thousands of `secp256k1_recover` calls to completion — each one individually valid input to the function, so no single iteration hits an early bounds failure — before the proof is ultimately rejected downstream (e.g., by the authority Merkle-multi-proof check). This mirrors the XBM CVE precisely: the loop bound comes directly from attacker-supplied data with no upfront cap, and the expensive work happens before any EOF/limit check can short-circuit it.

Because this all happens inside `validate_unsigned`, it executes on every full node's transaction pool for every gossiped copy of the extrinsic, before any fee is paid and before the extrinsic is ever included in a block — a classic "free computation" DoS surface, the same class explicitly called out and defended against elsewhere in this codebase (see the `call-decompressor` pallet's comment about the fee-less `validate_unsigned` path being a "zstd bomb" vector): [5](#0-4) 

### Impact Explanation
An unprivileged relayer/attacker can submit a single unsigned `handle_unsigned` extrinsic carrying a BEEFY consensus message with a bloated `signatures` vector. Every node that receives this extrinsic over the network (and every node re-validating it before block inclusion) is forced to perform the full, unbounded ECDSA-recovery loop for free. Repeated/broadcast submission of such extrinsics can degrade transaction-pool throughput and block-authoring capacity network-wide — a route-unable-to-deliver-messages condition (Medium severity DoS), without requiring any stake, fee payment, or malicious admin/governance/node role.

### Likelihood Explanation
Likelihood is high: `handle_unsigned` is explicitly designed to accept unsigned submissions from any relayer with "valid proofs" (per the pallet's own documentation), and the vulnerable loop is unconditionally reached by any message whose consensus client is BEEFY. No privileged role or prior state is required — only a syntactically well-formed `RelayChainProof`/`MmrProof` structure with an oversized signature list, which fits comfortably within normal extrinsic/block size limits.

### Recommendation
Enforce a hard upper bound on `signed_commitment.signatures.len()` (e.g., tied to the maximum plausible authority-set size) immediately after decoding and before the `for sig in ... { secp256k1_recover(...) }` loop in `verify_mmr_update_proof`, both in `modules/consensus/beefy/verifier/src/lib.rs` and the Solidity analog `evm/src/consensus/EcdsaBeefy.sol::verifyMmrUpdateProof`. Reject the message early via `TransactionValidityError` in `validate_unsigned` if the bound is exceeded, so the expensive recovery work is never attempted for oversized inputs.

### Proof of Concept
1. Construct a `ConsensusMessage::Polkadot`/`Relaychain` message whose `RelayChainProof.signedCommitment.votes` (or `MmrProof.signed_commitment.signatures`) contains, say, 50,000 syntactically valid-length (65-byte) but bogus signature entries — well within typical block/extrinsic size limits.
2. Wrap it in `pallet_ismp::Call::handle_unsigned { messages: vec![Message::Consensus(...)] }` and submit as an unsigned transaction.
3. Observe that every receiving node's `validate_unsigned` calls `Self::execute` → `verify_mmr_update_proof`, performing 50,000 `secp256k1_recover` operations before ultimately failing the authority Merkle-multi-proof check — all before any fee is charged, and repeatable at will by gossiping more copies with varied nonces/content to bypass pool de-duplication tags.

### Citations

**File:** modules/pallets/ismp/src/lib.rs (L360-382)
```rust
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

**File:** modules/consensus/beefy/verifier/src/lib.rs (L105-162)
```rust
pub fn verify_mmr_update_proof<H: Keccak256 + EcdsaRecover + Send + Sync>(
	mut trusted_state: ConsensusState,
	mmr: MmrProof,
) -> Result<(ConsensusState, H256), Error> {
	let signatures_length = mmr.signed_commitment.signatures.len();
	let latest_height = mmr.signed_commitment.commitment.block_number;

	if trusted_state.latest_beefy_height >= latest_height {
		return Err(Error::StaleHeight {
			trusted_height: trusted_state.latest_beefy_height,
			current_height: latest_height,
		});
	}

	let commitment = mmr.signed_commitment.commitment.clone();

	// Pick the authority set the commitment claims to be signed under, then judge
	// participation against that set alone.
	let authority_set = if commitment.validator_set_id == trusted_state.current_authorities.id {
		&trusted_state.current_authorities
	} else if commitment.validator_set_id == trusted_state.next_authorities.id {
		&trusted_state.next_authorities
	} else {
		return Err(Error::UnknownAuthoritySet { id: commitment.validator_set_id });
	};

	if !check_participation_threshold(signatures_length as u32, authority_set.len) {
		return Err(Error::SuperMajorityRequired);
	}

	let mmr_root_data = commitment
		.payload
		.get_raw(&MMR_ROOT_PAYLOAD_ID)
		.ok_or(Error::MmrRootHashMissing)?;

	if mmr_root_data.len() != 32 {
		return Err(Error::InvalidMmrRootHashLength { len: mmr_root_data.len() });
	}
	let mmr_root = H256::from_slice(mmr_root_data);

	let commitment_hash = H::keccak256(&commitment.encode());
	let mut authority_leaves: Vec<[u8; 32]> = Vec::new();
	let mut authority_indices = Vec::new();

	for sig in mmr.signed_commitment.signatures.iter() {
		let uncompressed = H::secp256k1_recover(&commitment_hash.0, &sig.signature)
			.map_err(|_| Error::FailedToRecoverPublicKey)?;

		let hashed_uncompressed = H::keccak256(&uncompressed);

		let mut eth_address = [0u8; 20];
		eth_address.copy_from_slice(&hashed_uncompressed.as_ref()[12..]);

		let authority_address_hash = H::keccak256(&eth_address);

		authority_leaves.push(authority_address_hash.into());
		authority_indices.push(sig.index as usize);
	}
```

**File:** modules/consensus/beefy/verifier/src/lib.rs (L258-261)
```rust
/// Checks for supermajority participation
fn check_participation_threshold(len: u32, total: u32) -> bool {
	len >= ((2 * total) / 3) + 1
}
```

**File:** modules/pallets/call-decompressor/src/lib.rs (L224-231)
```rust
		// Bound the claimed decompressed size against the configured maximum here,
		// at the single choke point every caller flows through. Previously this
		// gate lived only in `decompress_call` (the dispatch path); the unsigned
		// `validate_unsigned` mempool path called `decompress` directly with no
		// bound, so a fee-less attacker could claim `encoded_call_size = u32::MAX`
		// and have a tiny zstd "bomb" expanded to gigabytes during transaction-pool
		// validation, before any size check. Enforcing it here protects both paths.
		ensure!(encoded_call_size < T::MaxCallSize::get() * ONE_MB, Error::<T>::CallSizeOutOfBound);
```
