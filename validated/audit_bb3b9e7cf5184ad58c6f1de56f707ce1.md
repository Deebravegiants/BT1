### Title
Uncontrolled Resource Consumption via Constant-Weight `handle_unsigned` ISMP Message Batches - (File: `modules/pallets/ismp/src/lib.rs`)

### Summary
`pallet_ismp::Call::handle_unsigned` is a free, permissionless, unsigned extrinsic that accepts an unbounded `Vec<Message>` batch and executes every message in it, but is charged a fixed, size-independent weight (`Weight::from_parts(300_000_000, 0)`), decoupling declared computational cost from actual computational cost. Worse, that same full execution (`Self::execute(messages.clone())`) also runs inside `ValidateUnsigned::validate_unsigned`, i.e. on every node's transaction-pool validation path, not only at block-inclusion time.

### Finding Description
`handle_unsigned` is declared with a static weight regardless of how many `Message`s (and how many `PostRequest`/`GetRequest`/`GetResponse` entries per message) are in the batch: [1](#0-0) 

The weight function used for the `#[pallet::weight(weight())]` annotation is a hard-coded constant, independent of `messages.len()` or the size of `requests`/`responses` inside each message: [2](#0-1) 

`Self::execute` iterates over the *entire* batch, calling `handle_incoming_message` for each `Message` — which performs full merkle/MMR membership-proof verification, per-request hashing, duplicate/timeout checks, and dispatches to `IsmpModule::on_accept` callbacks for every request in the batch: [3](#0-2) 

Because the extrinsic is unsigned (`ensure_none(origin)?`), anyone can submit it for free — there is no economic bound tying the size of the batch to a cost. Compounding this, `ValidateUnsigned::validate_unsigned` performs the *same full execution* of `Self::execute(messages.clone())` merely to validate the transaction for pool admission: [4](#0-3) 

This means every node that receives the gossiped unsigned extrinsic — including nodes that will never include it in a block — must fully execute the entire batch (proof verification, hashing, callback dispatch) just to decide whether to accept it into the transaction pool. Individual `RequestMessage`/`ResponseMessage` handlers themselves loop over every request in the batch performing a membership-proof check plus per-item hashing and callback dispatch, with no explicit cap on batch size at this layer: [5](#0-4) [6](#0-5) 

This is directly analogous to the reported Elasticsearch CWE-400/CAPEC-130 issue: an unprivileged submitter can construct a specially crafted "bulk" request (here, a large `Vec<Message>` with many `PostRequest`/`GetRequest` entries and a correspondingly large membership proof) that forces sustained high CPU consumption on every validating/relaying node, while the protocol's weight/fee accounting treats it as a fixed, cheap 300M-weight call.

### Impact Explanation
An attacker can repeatedly submit (and have gossiped) `handle_unsigned` extrinsics carrying maximally-sized message batches (limited only by the runtime's max extrinsic/block length, not by weight). Each such extrinsic forces:
1. Full execution during `validate_unsigned` on every peer that receives it via gossip (even if ultimately rejected because the block producer already included a competing message), and
2. Full execution again at block-application time if included, but charged only the fixed 300M weight, understating the true resource cost relative to the block's weight budget.

Sustained submission of such extrinsics can degrade block-production/import time and transaction-pool throughput network-wide, denying service to legitimate relayers trying to deliver real cross-chain messages — a network-reachable, permissionless resource-exhaustion vector consistent with the "Medium" severity of the analog report.

### Likelihood Explanation
High likelihood of reachability: `handle_unsigned` is explicitly designed to be callable by anyone with valid proofs and is free (no signed origin, no fee). An attacker only needs a valid-looking large batch of requests/responses with a correct (or minimally, proof-format-valid) membership proof to pass `validate_unsigned` and trigger the expensive path; even proofs that ultimately fail still force the verification work to run before being rejected. No further privileged access is required.

### Recommendation
- Make the declared weight of `handle_unsigned` proportional to the actual size of the submitted batch (number of messages, number of requests/responses per message, and proof size), so the runtime's weight-limiting mechanism can reject over-large batches before they consume disproportionate resources.
- Enforce an explicit maximum on the number of messages and per-message request/response counts accepted by `handle_unsigned` (e.g. via a `BoundedVec` or an early length check) before any proof verification or execution occurs.
- Consider adding lightweight, cheap pre-validation (e.g., size/format checks) ahead of the full `Self::execute` call inside `validate_unsigned`, so pool validation does not need to perform full membership-proof verification and callback dispatch for oversized or malformed batches.

### Proof of Concept
1. An unprivileged actor crafts a `pallet_ismp::Call::handle_unsigned` extrinsic whose `messages: Vec<Message>` contains a single (or few) `Message::Request(RequestMessage)` with the maximum number of `PostRequest` entries that fits within the runtime's max extrinsic/block length, each requiring hashing and inclusion in the merkle/MMR membership proof verified in `modules/ismp/core/src/handlers/request.rs` (`handle`, lines 86-133).
2. The actor submits this extrinsic as unsigned to a node's transaction pool.
3. `ValidateUnsigned::validate_unsigned` (`modules/pallets/ismp/src/lib.rs`, lines 614-626) fully executes `Self::execute(messages.clone())`, performing full proof verification and per-request dispatch for the entire batch, on every peer node that receives the gossiped transaction — all while the extrinsic is still only "provisionally" being validated and is charged nothing.
4. Because `#[pallet::weight(weight())]` returns the same fixed `Weight::from_parts(300_000_000, 0)` regardless of batch size (`fn weight()`, lines 727-730), the runtime's weight accounting does not reflect or limit this actual cost, allowing the attacker to repeat this at effectively no cost across many extrinsics/blocks to sustain high CPU load network-wide.

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

**File:** modules/pallets/ismp/src/impls.rs (L37-58)
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

**File:** modules/ismp/core/src/handlers/request.rs (L30-65)
```rust
pub fn handle<H>(host: &H, msg: RequestMessage) -> Result<MessageResult, anyhow::Error>
where
	H: IsmpHost,
{
	if msg.requests.is_empty() {
		Err(Error::EmptyBatch)?
	}

	let state_machine = validate_state_machine(host, msg.proof.height)?;
	let consensus_clients = host.consensus_clients();
	let check_state_machine_client = |state_machine: StateMachine| {
		consensus_clients
			.iter()
			.find_map(|client| client.state_machine(state_machine).ok())
			.is_none()
	};

	let router = host.ismp_router();

	// Reject duplicate requests within the batch. Wire format is `Vec`,
	// so this is the line of defence against an attacker padding a
	// batch with identical requests.
	let wrapped: Vec<Request> = msg.requests.iter().cloned().map(Request::Post).collect();
	dedup_requests::<H>(&wrapped)?;

	for req in msg.requests.iter() {
		let req = Request::Post(req.clone());
		// If a receipt exists for any request then it's a duplicate and it is not dispatched
		if host.request_receipt(&req).is_some() {
			Err(Error::DuplicateRequest { meta: req.clone().into() })?
		}

		// can't dispatch timed out requests
		if req.timed_out(host.timestamp()) {
			Err(Error::RequestTimeout { meta: req.clone().into() })?
		}
```

**File:** modules/ismp/core/src/handlers/request.rs (L86-133)
```rust
	// Verify membership proof
	let state = host.state_machine_commitment(msg.proof.height)?;
	let commitments = msg
		.requests
		.iter()
		.map(|post| hash_request::<H>(&Request::Post(post.clone())))
		.collect();
	state_machine.verify_membership(host, commitments, state, &msg.proof)?;

	let mut total_weights = Weight::zero();
	let result = msg
		.requests
		.into_iter()
		.map(|request| {
			let wrapped_req = Request::Post(request.clone());
			let mut lambda = || {
				let cb = router.module_for_id(request.to.clone())?;
				// Re-check the receipt right before dispatch. The up-front pass above
				// runs before any callback executes; a prior request's on_accept in
				// this same batch could have stored a receipt for this request
				// (directly or by re-entering the handler), and we must not invoke
				// on_accept a second time.
				if host.request_receipt(&wrapped_req).is_some() {
					Err(Error::DuplicateRequest { meta: wrapped_req.clone().into() })?
				}
				// Store request receipt to prevent reentrancy attack
				let signer = host.store_request_receipt(&wrapped_req, &msg.signer)?;
				let res = cb.on_accept(request.clone()).map(|weight| {
					total_weights.saturating_accrue(weight);

					let commitment = hash_request::<H>(&wrapped_req);
					Event::PostRequestHandled(RequestResponseHandled {
						commitment,
						relayer: signer,
					})
				});
				// Delete receipt if module callback failed so it can be timed out
				if res.is_err() {
					host.delete_request_receipt(&wrapped_req)?;
				}
				Ok(res)
			};

			let res = lambda().and_then(|res| res);
			res
		})
		.collect::<Vec<_>>();

```
