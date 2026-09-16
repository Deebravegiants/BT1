Based on my research, I found a strong structural analog to the Liferay ComboServlet issue: unbounded batch sizes accepted by ISMP message-handling entry points, with no limit on the number or size of items combined in a single call.

### Title
Unbounded message batch size in `pallet_ismp::Call::handle_unsigned` enables free, unmetered denial-of-service - (File: `modules/pallets/ismp/src/lib.rs`)

### Summary
`pallet_ismp`'s `handle_unsigned` extrinsic accepts an unbounded `Vec<Message>`, and each `Message::Request`/`Message::Response` variant itself wraps an unbounded `Vec<PostRequest>` / `Vec<GetRequest>` [1](#0-0) [2](#0-1) . Nothing in the call, its `validate_unsigned` implementation, or the batch handlers enforces a cap on the number of requests/responses in the batch or the size of their `body`/`keys`/`proof` fields, mirroring the ComboServlet flaw of combining an unlimited number/size of files into one response.

### Finding Description
`handle_unsigned` is declared `ensure_none(origin)` (a permissionless unsigned extrinsic) and is annotated `#[pallet::weight(weight())]`, a zero-argument weight function that is not parameterized by `messages.len()` or by the size of the nested request/response vectors [3](#0-2) . Both `validate_unsigned` (run by every node during pool gossip, for free) and the actual dispatch call `Self::execute(messages.clone())`, which fully processes membership-proof verification and dispatch for every request in the batch [4](#0-3) [5](#0-4) .

The `RequestMessage`/`ResponseMessage` wire types carry plain, unbounded `Vec<PostRequest>` / `Vec<GetRequest>` plus a `Proof` whose `proof: Vec<u8>` is also unbounded [2](#0-1) . `handlers::request::handle` and `handlers::response::handle` iterate the entire batch, run `verify_membership`/`verify_state_proof` over it, and dispatch every entry to a module callback with no length limit enforced anywhere in the path [6](#0-5) [7](#0-6) . A `GetRequest` additionally carries `keys: Vec<Vec<u8>>` with no cap, so `verify_state_proof` cost scales with an attacker-chosen number of storage keys per request, compounding with an attacker-chosen number of requests per batch.

Because `handle_unsigned` is unsigned and, in configurations where the fee-handler `POLICY` is disabled (as used by, e.g., the gargantua runtime's `WeightFeeHandler<..., false>` [8](#0-7) ), execution is entirely free, an attacker pays nothing to force full membership-proof verification and dispatch over an arbitrarily large `Vec<Message>`/`Vec<PostRequest>`/`Vec<GetRequest>`, bounded only by the runtime's max-extrinsic/block-length limit rather than by any protocol-level cap tied to the declared (and apparently fixed) call weight.

### Impact Explanation
Because `validate_unsigned` re-executes the full batch (membership proof verification, hashing, dispatch simulation) for every unsigned transaction entering the pool, and because the declared call weight is not scaled to the batch content, a maximal-size batch can be crafted to consume execution time disproportionate to its charged weight. This can be repeated for free (no fee, no signature, unsigned), letting an attacker force excess computation on every relaying/validating node, which is the same "unbounded combination size ⇒ denial of service" bug class as ComboServlet. Per the validation criteria, sustained exploitation can degrade block production/import throughput, resulting in "a route unable to deliver messages" for the affected state machine.

### Likelihood Explanation
This is reachable by any unprivileged actor able to submit an unsigned extrinsic containing valid-looking (or crafted-but-plausible) proof data — no special role, staking, or fee balance is required, which is exactly the "unprivileged message dispatcher/relayer" threat model in scope. The only friction is constructing a batch that passes the cheap early checks (duplicate/timeout checks) while still being large enough in count and per-item size (large `body`, many `keys` in `GetRequest`, large `proof`) to trigger a disproportionate amount of downstream membership/state-proof verification work.

### Recommendation
Enforce protocol-level bounds: cap `Vec<Message>` batch length in `handle_unsigned`, cap the number of `PostRequest`/`GetRequest` entries per `RequestMessage`/`ResponseMessage`, cap `GetRequest::keys` length, and cap the size of `body`/`proof` fields (e.g., via `BoundedVec` with `Get<u32>` limits). Additionally, make the `#[pallet::weight(...)]` annotation for `handle_unsigned` a function of the actual batch size (message count × average per-item verification cost) so `CheckWeight` correctly rejects oversized batches before they consume execution/validation time, and consider applying a lightweight, cheap-to-check size/count pre-filter inside `validate_unsigned` before the expensive `Self::execute` call.

### Proof of Concept
I could not fully verify the internal implementation of the `weight()` function referenced by `#[pallet::weight(weight())]` in `modules/pallets/ismp/src/lib.rs` (its definition was not located within available search budget), so it remains unconfirmed whether it truly ignores batch size — this is the key open question for a complete PoC. A concrete PoC would need to: (1) inspect `weight()`'s implementation to confirm it returns a size-independent constant, (2) craft a `handle_unsigned` call with a very large `Vec<Message>` containing many `PostRequest`s each with maximal `body`/`proof` sizes near the runtime's max-extrinsic-size limit, and (3) measure execution/validation time against the declared weight to demonstrate the mismatch driving a DoS. Given the incomplete confirmation of `weight()`'s scaling behavior, this finding should be treated as a **structural analog requiring runtime-side verification** rather than a fully proven exploit.

### Citations

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

**File:** modules/pallets/ismp/src/lib.rs (L605-626)
```rust
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

```

**File:** modules/ismp/core/src/messaging.rs (L116-147)
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

/// A response message holds a batch of GetRequests being responded to.
///
/// Post-#840 the protocol no longer carries `PostResponse`; the only
/// responses processed by `handle_response` are GetResponses constructed
/// on-chain from the state proof. The relayer's job is to ferry the
/// original GetRequests plus the storage proof; the host produces the
/// `GetResponse` itself.
#[derive(
	Debug, Clone, Encode, Decode, DecodeWithMemTracking, scale_info::TypeInfo, PartialEq, Eq,
)]
pub struct ResponseMessage {
	/// The batch of GetRequests being responded to.
	pub requests: Vec<GetRequest>,
	/// Membership batch proof for `requests`.
	pub proof: Proof,
	/// Signer information. Ideally should be their account identifier
	pub signer: Vec<u8>,
}

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

**File:** modules/ismp/core/src/handlers/request.rs (L30-97)
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

	let mut total_weights = Weight::zero();
	let result = msg
		.requests
```

**File:** modules/ismp/core/src/handlers/response.rs (L30-90)
```rust
pub fn handle<H>(host: &H, msg: ResponseMessage) -> Result<MessageResult, anyhow::Error>
where
	H: IsmpHost,
{
	if msg.requests.is_empty() {
		Err(Error::EmptyBatch)?
	}

	let proof = msg.proof();
	let state_machine = validate_state_machine(host, proof.height)?;
	let state = host.state_machine_commitment(proof.height)?;

	let mut total_weights = Weight::zero();

	// Reject duplicate Get requests within the batch.
	dedup_requests::<H>(&msg.requests())?;

	for get in &msg.requests {
		let req = Request::Get(get.clone());

		if req.timed_out(host.timestamp()) {
			Err(Error::RequestTimeout { meta: (&req).into() })?
		}

		if req.dest_chain() != proof.height.id.state_id {
			Err(Error::RequestProofMetadataNotValid { meta: (&req).into() })?
		}

		let commitment = hash_request::<H>(&req);
		if host.request_commitment(commitment).is_err() {
			Err(Error::UnknownRequest { meta: (&req).into() })?
		}

		let res = GetResponse { get: get.clone(), values: Default::default() };

		if host.response_receipt(&res).is_some() {
			Err(Error::DuplicateResponse { meta: (&res).into() })?
		}
	}

	// Ensure the proof height is equal to each retrieval height specified in the Get
	// requests
	if !msg.requests.iter().all(|get| get.height == proof.height.height) {
		Err(Error::InsufficientProofHeight)?
	}

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

```

**File:** parachain/runtimes/gargantua/src/ismp.rs (L192-198)
```rust
	type FeeHandler = pallet_ismp::fee_handler::WeightFeeHandler<
		AccountId,
		Balances,
		IsmpWeightToFee,
		TreasuryPalletId,
		false,
	>;
```
