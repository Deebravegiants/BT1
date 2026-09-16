### Title
Static, non-scaling extrinsic weight for `pallet_ismp::handle_unsigned` lets a single free unsigned extrinsic force unbounded proof-verification work, exhausting node resources - (File: `modules/pallets/ismp/src/lib.rs`)

### Summary
`pallet-ismp`'s `handle_unsigned` extrinsic accepts an arbitrary-length `Vec<Message>` and is declared with a **static** weight (`weight()` returns a fixed `Weight::from_parts(300_000_000, 0)` regardless of batch size or content), while the actual work performed — full BEEFY/SP1 signature-recovery and MMR verification, merkle multiproof verification, and state proofs for every request/response in the batch — is executed both during unsigned-transaction pool validation (`validate_unsigned`, run by every node that receives the gossiped tx) and again during block execution (`execute`). Because the declared weight does not scale with `messages.len()` or the size of embedded proofs/signature sets, an attacker can submit one "free" unsigned extrinsic carrying a very large batch of messages (or a small number of messages each carrying a large embedded signature/proof set) that consumes CPU/verification time far in excess of the weight accounted for, degrading or crashing node availability — the same bug class as the reported Traffic Server issue: framing/messages that are individually cheap to submit but disproportionately expensive to process, exhausting server/node resources.

### Finding Description
`handle_unsigned` is defined with `#[pallet::weight(weight())]`: [1](#0-0) 

`weight()` is a fixed constant unrelated to the batch: [2](#0-1) 

This call is `ensure_none`-gated (permissionless, unsigned) and directly calls `Self::execute(messages.clone())`, which iterates the entire caller-supplied `messages: Vec<Message>` and fully verifies every message before any fee/weight-based gating occurs: [3](#0-2) 

The exact same unbounded verification work also runs inside `validate_unsigned`, which every node executes merely to admit the transaction into its mempool (i.e., before it is ever included in a block, and repeatedly for every propagation hop): [4](#0-3) 

Each `Message::Consensus` entry triggers cryptographic verification whose cost scales with the number of embedded validator signatures — `ecrecover`-equivalent `secp256k1_recover` calls plus merkle multi-proof verification, with **no upper bound enforced on `signed_commitment.signatures.len()`** before the loop runs: [5](#0-4) 

Each `Message::Request`/`Message::Response` entry similarly triggers full state-proof/non-membership verification per request in the batch (e.g. `verify_state_proof` in the GET-response handler, looped once per request with no batch cap): [6](#0-5) 

No length cap on `messages: Vec<Message>` or on nested proof/signature vectors was found anywhere in the call path — unlike the sibling `pallet-call-decompressor`, which explicitly gates a claimed-size DoS ("zstd bomb") at the single choke point every caller flows through before doing the expensive work: [7](#0-6) 

That pattern (bound the claimed cost before doing expensive work) is exactly what is missing for `handle_unsigned`: the declared weight is a flat constant instead of a function of `messages.len()`/proof sizes, so the runtime's `CheckWeight` extension and block-weight accounting cannot reject an oversized/expensive batch before it is executed, and worse, the same unbounded work is repeated by `validate_unsigned` for gossip/mempool admission on every node, for free, before the transaction is even included in a block.

### Impact Explanation
This is a direct resource-exhaustion vector reachable by any unprivileged party via a single submitted unsigned extrinsic (no fee, no signature, no gas payment required, matching the "abusive/asymmetric-cost framing" bug class in the report):
- CPU/time exhaustion during `validate_unsigned` on every full node/collator that receives the extrinsic via gossip, independent of whether it is ever included in a block.
- CPU/time exhaustion during block execution if it is included, since `#[pallet::weight(weight())]` under-declares the true cost, risking block-production stalls/timeouts network-wide (a chain-level DoS, i.e., "a route unable to deliver messages" and broader liveness degradation), consistent with the Medium severity of the analog CVE.
- Because the pallet's own documentation flags this call as "free" and asks callers to "use with caution," the absence of a batch-size/complexity bound in code is the concrete root cause matching the report's bug class.

### Likelihood Explanation
High reachability, low cost to the attacker: `handle_unsigned` requires no signature and no fee (unsigned origin, `ensure_none`), so anyone with node/RPC access can submit a batch with many `Message::Consensus`/`Message::Request`/`Message::Response` entries, or a small number of entries each carrying maximal embedded signature/proof arrays. The only practical bound is the runtime's generic max-extrinsic-length limit, which does not track verification cost (ecrecover + merkle-proof cost scales non-linearly with input, unlike raw byte count), so an attacker can craft a still-small-in-bytes but computationally heavy payload.

### Recommendation
- Make the declared weight for `handle_unsigned` (and `handle`) a function of `messages.len()` and of the size of nested proof/signature vectors (benchmark per-message and per-signature costs), rather than a flat constant, so `CheckWeight`/block weight accounting reflects true cost.
- Enforce an explicit maximum on `messages.len()` and on nested signature/proof array lengths (e.g., cap `signed_commitment.signatures.len()` and per-batch request/response counts) at the earliest possible choke point — ideally inside `validate_unsigned` before any cryptographic verification is attempted — mirroring the pattern already used in `pallet-call-decompressor::decompress` (reject oversized claims before doing expensive work).
- Consider rate-limiting or requiring a bond/fee for oversized unsigned batches to remove the "free and unbounded" property that makes this economically attractive to abuse.

### Proof of Concept
1. Craft a `Message::Consensus` (or a `Vec<Message>` containing many messages) whose `signed_commitment.signatures` array contains an attacker-chosen large number of syntactically valid-looking (but not necessarily passing threshold) ECDSA signatures.
2. Submit it as `pallet_ismp::Call::handle_unsigned { messages }` as an unsigned extrinsic via RPC.
3. Every node that receives it via gossip runs `validate_unsigned`, which calls `Self::execute` → `handle_incoming_message` → BEEFY verifier's `verify_mmr_update_proof`, performing one `secp256k1_recover` and one merkle-leaf construction per signature with no cap, before the extrinsic is even known to be valid or ever gets included in a block — since the declared call weight (`300_000_000`, fixed) does not reflect this, standard weight-based extrinsic-length/complexity limits do not prevent the batch from being large enough to consume disproportionate CPU time on every receiving node.

### Citations

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

**File:** modules/pallets/ismp/src/lib.rs (L727-730)
```rust
	/// Static weights because these should get overridden by the FeeHandler
	fn weight() -> Weight {
		Weight::from_parts(300_000_000, 0)
	}
```

**File:** modules/pallets/ismp/src/impls.rs (L40-57)
```rust
	pub fn execute(messages: Vec<Message>) -> Result<Vec<events::Event>, Error<T>> {
		let host = Pallet::<T>::default();

		let message_results = messages
			.iter()
			.map(|msg| handle_incoming_message(&host, msg.clone()))
			.collect::<Result<Vec<_>, _>>()
			.map_err(|err| {
				log::debug!(target: "ismp", "Handling Error {:#?}", err);
				Pallet::<T>::deposit_event(Event::<T>::Errors { errors: vec![err.into()] });
				Error::<T>::InvalidMessage
			})?;

		let messages_with_weights = message_results
			.iter()
			.zip(messages)
			.map(|(result, message)| MessageWithWeight { message, weight: result.weight() })
			.collect::<Vec<_>>();
```

**File:** modules/consensus/beefy/verifier/src/lib.rs (L146-163)
```rust
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

**File:** modules/ismp/core/src/handlers/response.rs (L76-93)
```rust
	// Since each get request can contain multiple storage keys
	// we should handle them individually
	let result = msg
		.requests
		.iter()
		.cloned()
		.map(|request| {
			let wrapped_req = Request::Get(request.clone());
			let keys = request.keys.clone();
			let values = state_machine
				.verify_state_proof(host, keys, state.state_root, &proof)?
				.into_iter()
				.map(|(key, value)| StorageValue { key, value })
				.collect();

			let router = host.ismp_router();
			let cb = router.module_for_id(request.from.clone())?;
			let response = GetResponse { get: request.clone(), values: Default::default() };
```

**File:** modules/pallets/call-decompressor/src/lib.rs (L220-232)
```rust
	pub fn decompress(
		compressed_bytes: Vec<u8>,
		encoded_call_size: u32,
	) -> Result<Vec<u8>, DispatchError> {
		// Bound the claimed decompressed size against the configured maximum here,
		// at the single choke point every caller flows through. Previously this
		// gate lived only in `decompress_call` (the dispatch path); the unsigned
		// `validate_unsigned` mempool path called `decompress` directly with no
		// bound, so a fee-less attacker could claim `encoded_call_size = u32::MAX`
		// and have a tiny zstd "bomb" expanded to gigabytes during transaction-pool
		// validation, before any size check. Enforcing it here protects both paths.
		ensure!(encoded_call_size < T::MaxCallSize::get() * ONE_MB, Error::<T>::CallSizeOutOfBound);

```
