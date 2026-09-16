### Title
Unbounded `requests`/`messages` batches in `pallet-ismp::handle_unsigned` allow free, unbounded resource consumption during mempool validation - (File: `modules/pallets/ismp/src/lib.rs`)

### Summary
`pallet_ismp::Call::handle_unsigned` accepts an unbounded `Vec<Message>`, and each `Message::Request`/`Message::Response` variant itself carries an unbounded `Vec<PostRequest>` / `Vec<GetRequest>` [1](#0-0) . Because this is an unsigned extrinsic, `ValidateUnsigned::validate_unsigned` runs `Self::execute(messages.clone())` — full membership-proof verification, dedup, and dispatch simulation for every request in every message — against **every submission that reaches the transaction pool**, before any fee or weight is charged [2](#0-1) . There is no `BoundedVec`, no maximum message count, and no maximum request-per-message count anywhere on this path. This is the direct analog of CVE-2026-50645/GHSA-ghvc-7hp8-2g2v: no restriction on the number of "attachment"-like items (here, `PostRequest`/`GetRequest` entries) that a single message can carry before it is deserialized/processed.

### Finding Description
`handle_unsigned` is declared with a static weight `Weight::from_parts(300_000_000, 0)` that does not scale with the number of messages or the number of requests inside each message [3](#0-2) [4](#0-3) . `Pallet::<T>::execute` iterates over every message calling `handle_incoming_message`, which for a `RequestMessage`/`ResponseMessage` computes `hash_request` over every entry and runs full merkle multi-proof verification (`verify_membership`) over the whole batch [5](#0-4) [6](#0-5) .

Critically, `ValidateUnsigned::validate_unsigned` for `pallet_ismp` calls `Self::execute(messages.clone())` directly (not a cheap check) to decide pool admission [2](#0-1) . Since `handle_unsigned` is a free/unsigned call, an attacker pays nothing to submit a transaction with an arbitrarily large `Vec<Message>`, each containing an arbitrarily large `Vec<PostRequest>`/`Vec<GetRequest>` (bounded only by the extrinsic byte-size limit of the runtime, not by an item-count cap). This forces every node's transaction pool to perform full proof verification (hashing + merkle multi-proof checks) work proportional to the attacker-chosen size for free, repeatedly, on every re-validation, with no economic cost to the attacker and no per-request cap analogous to CXF's "500 attachments per message" fix.

The `pallet-call-decompressor` mitigates a similar zstd-bomb class for compressed calls (`ONE_MB` cap enforced at the single choke point) [7](#0-6) , and `pallet-bandwidth`/coprocessor meters bytes for `GetRequest` processing in `pallet-state-coprocessor` [8](#0-7) , but no analogous cap exists on the count of `PostRequest`/`GetRequest` entries per `Message`, nor on the count of `Message`s per `handle_unsigned` call.

### Impact Explanation
This is a CWE-400 uncontrolled resource consumption / denial-of-service vector reachable by any unprivileged party submitting a single unsigned extrinsic to the network — no proofs need to be valid for the resource cost to be incurred, since the expensive verification work happens during `validate_unsigned` itself. Repeated submissions can degrade or stall Hyperbridge parachain full-node/collator transaction-pool throughput, delaying legitimate message delivery (relayed proofs, token bridge messages, intents) — i.e., a route becoming unable to deliver messages in a timely manner, which is the qualifying impact class for this analog.

### Likelihood Explanation
High likelihood: the call is permissionless, free (unsigned/no fee), requires no valid proof to trigger the expensive verification path, and there is no existing item-count bound to prevent an attacker from constructing maximal `Vec<Message>`/`Vec<PostRequest>`/`Vec<GetRequest>` payloads up to the runtime's extrinsic size limit.

### Recommendation
Introduce explicit bounds analogous to Apache CXF's fix (a maximum default cap):
- Cap the number of `Message`s accepted per `handle_unsigned` call (e.g. via a `BoundedVec<Message, T::MaxMessagesPerBatch>` or an early `ensure!(messages.len() <= T::MaxMessagesPerBatch::get())` check before any processing).
- Cap the number of `PostRequest`/`GetRequest` entries inside `RequestMessage`/`ResponseMessage`/`GetRequestsWithProof` similarly.
- Perform these cheap length checks in `validate_unsigned` before invoking `Self::execute`, so oversized batches are rejected without doing any hashing/proof-verification work.

### Proof of Concept
1. Construct `pallet_ismp::Call::handle_unsigned { messages }` where `messages` is a `Vec<Message::Request(RequestMessage)>` containing many entries, and each `RequestMessage.requests` is filled with as many `PostRequest` items as fit within the runtime's max extrinsic size (proof/signer fields can be garbage/invalid).
2. Submit repeatedly as unsigned extrinsics (per `parachain/simtests/src/pallet_ismp.rs` pattern using `subxt::dynamic::tx("Ismp", "handle_unsigned", ...)`) [9](#0-8) .
3. Observe that `ValidateUnsigned::validate_unsigned` invokes `Self::execute` on the full batch — performing `hash_request` and `verify_membership` for every request — for free, on every node's mempool validation, with no rejection based on batch/item count [2](#0-1) .

### Citations

**File:** modules/ismp/core/src/messaging.rs (L116-127)
```rust
/// A request message holds a batch of requests to be dispatched from a source state machine
#[derive(
	Debug, Clone, Encode, DecodeWithMemTracking, Decode, scale_info::TypeInfo, PartialEq, Eq,
)]
pub struct RequestMessage {
	/// Requests from source chain
	pub requests: Vec<PostRequest>,
	/// Membership batch proof for these requests
	pub proof: Proof,
	/// Signer information. Ideally should be their account identifier
	pub signer: Vec<u8>,
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

**File:** modules/pallets/ismp/src/lib.rs (L726-730)
```rust

	/// Static weights because these should get overridden by the FeeHandler
	fn weight() -> Weight {
		Weight::from_parts(300_000_000, 0)
	}
```

**File:** modules/pallets/ismp/src/impls.rs (L37-57)
```rust
impl<T: Config> Pallet<T> {
	/// Execute the provided ISMP datagrams, this will short circuit if any messages are invalid.
	/// This also charges fee on valid message delivery
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

**File:** modules/ismp/core/src/handlers/request.rs (L86-93)
```rust
	// Verify membership proof
	let state = host.state_machine_commitment(msg.proof.height)?;
	let commitments = msg
		.requests
		.iter()
		.map(|post| hash_request::<H>(&Request::Post(post.clone())))
		.collect();
	state_machine.verify_membership(host, commitments, state, &msg.proof)?;
```

**File:** modules/pallets/call-decompressor/src/lib.rs (L220-231)
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

**File:** modules/pallets/state-coprocessor/src/lib.rs (L60-65)
```rust
		/// Bandwidth gate that meters per-app data consumption. The
		/// coprocessor charges `max(sum(keys.len()) + context.len(), 32)`
		/// bytes per `GetRequest` against `(req.source, req.from)` before
		/// any state proof work — fails fast for apps without allowance.
		type BandwidthGate: pallet_bandwidth::BandwidthGate;
	}
```

**File:** parachain/simtests/src/pallet_ismp.rs (L282-293)
```rust
	let tx = subxt::dynamic::tx(
		"Ismp",
		"handle_unsigned",
		vec![messages_to_value(vec![Message::Request(RequestMessage {
			requests: vec![post.clone().into()],
			proof: proof.clone(),
			signer: signature.encode(),
		})])],
	);

	// send once
	let progress = client.tx().create_unsigned(&tx)?.submit_and_watch().await?;
```
