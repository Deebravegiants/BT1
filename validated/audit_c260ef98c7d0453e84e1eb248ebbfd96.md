### Title
Unbounded, unauthenticated `handle_unsigned` batch causes network-wide validation resource exhaustion - (File: `modules/pallets/ismp/src/lib.rs`)

### Summary
`pallet-ismp`'s `handle_unsigned` extrinsic accepts an unbounded `Vec<Message>` and is validated for free by every node's `validate_unsigned` hook, which fully executes the batch (proof verification, hashing, membership checks) before any fee or block-weight accounting applies. This mirrors the engine.io long-polling POST DoS (GHSA-j4f2-536g-r55m): an unauthenticated, cheap-to-send request triggers disproportionate server-side resource consumption.

### Finding Description
`Call::handle_unsigned` is dispatched via `ensure_none(origin)` and is intentionally fee-less ("This allows users execute ISMP datagrams for free. Use with caution.") [1](#0-0) .

Its `ValidateUnsigned::validate_unsigned` implementation does not perform a cheap sanity/size check before doing real work — it directly calls `Self::execute(messages.clone())`, which is the *same* full execution path used at actual dispatch time (hashing every request, running `dedup_requests`, and performing Merkle/state-membership proof verification for every request in the batch) [2](#0-1) , [3](#0-2) .

`validate_unsigned` runs on **every** node that receives the unsigned transaction over the network (gossip/import-queue validation), independent of whether the transaction is ever included in a block. There is no `MaxMessages` bound, no `BoundedVec`, and no cheap pre-check limiting `messages.len()` or the size of nested fields (e.g., `PostRequest.body`, `GetRequest.keys`, MMR/state proofs) before the expensive per-message cryptographic verification in `handlers::request::handle` runs [4](#0-3) .

Because the call is unsigned, an attacker pays no fee and needs no account balance to construct an arbitrarily large `Vec<Message>` (e.g., thousands of `PostRequest`/`GetRequest` entries each carrying maximal-size proofs or `keys`), and can resubmit different such batches repeatedly (each new batch produces a distinct `provides` tag via message-specific hashing, so the transaction pool does not dedupe them) [5](#0-4) . Each submission forces every full node in the network to perform full membership-proof verification work for free during transaction-pool validation, before the (correct) rejection for bad proofs or duplicate commitments even occurs.

The declared `#[pallet::weight(weight())]` is used for post-inclusion block-weight accounting only; it does not gate the pre-inclusion `validate_unsigned` cost that every peer incurs on receipt/gossip, so `frame_system::CheckWeight`/block weight limits provide no protection against this specific resource-exhaustion vector. Documentation itself acknowledges the risk in passing ("Malformed messages or those with invalid proofs are filtered out by the transaction pool validation logic preventing unnecessary processing") [6](#0-5)  but that filtering itself is what performs the expensive work.

### Impact Explanation
An unprivileged actor can submit unsigned, feeless `handle_unsigned` extrinsics with unbounded batch size/content to force full/validator/collator nodes across the network to repeatedly execute expensive cryptographic proof-verification work during mempool validation, at effectively zero cost to the attacker. Sustained submission can degrade node responsiveness and consensus-critical message processing (a form of route/message-delivery denial), satisfying the "route unable to deliver messages" impact criterion for resource-exhaustion class bugs.

### Likelihood Explanation
High: no signature, no fee, no account balance, and no size bound are required — only network access to submit a transaction, exactly as in the analog CVE (unauthenticated POST to a long-polling endpoint).

### Recommendation
Add a cheap, size-bound pre-check in `validate_unsigned` (batch length cap, e.g., `MaxMessages`, plus per-message payload/key/proof size caps) executed *before* any hashing or proof verification, so malformed/oversized batches are rejected at negligible cost. Consider also bounding message vectors with `BoundedVec` in the extrinsic signature itself so the constraint is enforced at the codec/decoding layer for every receiving node.

### Proof of Concept
1. Construct `pallet_ismp::Call::handle_unsigned` with `messages: Vec<Message>` containing e.g. thousands of `Message::Request(RequestMessage { requests: <many PostRequest with large `body`/`keys`>, proof: <large membership proof>, .. })`.
2. Submit as an unsigned transaction (as done in existing tests, e.g. `parachain/simtests/src/pallet_ismp.rs:282-293` and `modules/pallets/testsuite/src/tests/pallet_call_decompressor.rs:149-198`, which already show 1000-request batches being accepted for `validate_unsigned`/execution processing without a batch-size limit).
3. Resubmit repeatedly with varied content (e.g., different `nonce`/`from` per request) so each batch produces a unique `provides` tag and bypasses pool deduplication, forcing every receiving node to redo full proof verification on each submission.

Note: I was unable to fully confirm within available context whether any runtime-level `BaseCallFilter` (beyond `IsmpCallFilter` in `parachain/runtimes/gargantua/src/lib.rs`, which only blocks BEEFY consensus messages and `fund_message`) imposes an additional batch-size limit on `handle_unsigned` before `validate_unsigned` runs; if such a limit exists elsewhere in a specific runtime's `Config`, it would mitigate this finding for that runtime only.

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

**File:** modules/pallets/ismp/src/lib.rs (L604-644)
```rust
	/// This allows users execute ISMP datagrams for free. Use with caution.
	#[pallet::validate_unsigned]
	impl<T: Config> ValidateUnsigned for Pallet<T> {
		type Call = Call<T>;

		// empty pre-dispatch do we don't modify storage
		fn pre_dispatch(_call: &Self::Call) -> Result<(), TransactionValidityError> {
			Ok(())
		}

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

			if let Some((state_machine_id, latest_height)) = events.iter().find_map(|event| {
				if let ismp::events::Event::StateMachineUpdated(state_machine_updated_event) = event
				{
					Some((
						state_machine_updated_event.state_machine_id.clone(),
						state_machine_updated_event.latest_height,
					))
				} else {
					None
				}
			}) {
				return Ok(ValidTransaction {
					priority: latest_height,
					requires: vec![],
					provides: vec![sp_io::hashing::keccak_256(&state_machine_id.encode()).to_vec()],
					longevity: 25,
					propagate: true,
				});
```

**File:** modules/pallets/ismp/src/impls.rs (L37-51)
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
```

**File:** modules/ismp/core/src/handlers/request.rs (L30-93)
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

		// either the host is a router and can accept requests on behalf of any chain
		// or the request must be intended for this chain
		if req.dest_chain() != host.host_state_machine() && !host.is_router() {
			Err(Error::InvalidRequestDestination { meta: req.clone().into() })?
		}

		let source_chain = req.source_chain();

		// in order to allow proxies, the host must configure the given state machine
		// as it's proxy and must not have a state machine client for the source chain
		let allow_proxy = host.is_allowed_proxy(&msg.proof.height.id.state_id) &&
			check_state_machine_client(source_chain);

		// check if the request is allowed to be proxied
		if source_chain != msg.proof.height.id.state_id && !allow_proxy {
			Err(Error::RequestProxyProhibited { meta: req.clone().into() })?
		}
	}

	// Verify membership proof
	let state = host.state_machine_commitment(msg.proof.height)?;
	let commitments = msg
		.requests
		.iter()
		.map(|post| hash_request::<H>(&Request::Post(post.clone())))
		.collect();
	state_machine.verify_membership(host, commitments, state, &msg.proof)?;
```

**File:** docs/content/developers/polkadot/pallet-ismp/overview.mdx (L256-259)
```text
## Transaction fees

Pallet ISMP uses unsigned transactions for executing cross-chain messages. This means all cross-chain messages received are executed for free as unsigned transactions. The upside to this is that it cannot be exploited as a spam vector, since the transaction pool will check if the submitted extrinsics are valid before they are included in the pool. This validity check ensures that the transaction can be successfully executed and contains valid proofs. Malformed messages or those with invalid proofs are filtered out by the transaction pool validation logic preventing unnecessary processing and potential network congestion.

```
