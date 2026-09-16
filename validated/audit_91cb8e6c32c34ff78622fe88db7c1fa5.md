### Title
`Pallet::execute` short-circuits and reverts an entire unsigned message batch, wasting relayer gas on valid proof verification when a single message fails - ([File: modules/pallets/ismp/src/impls.rs])

### Summary
`handle_unsigned` in `modules/pallets/ismp/src/lib.rs` dispatches a permissionless, unsigned extrinsic carrying an arbitrary `Vec<Message>` batch to `Pallet::execute`. Inside `execute`, every message's consensus/state/membership proof is verified and its handler logic executed via `handle_incoming_message`, then all per-message results are collapsed with `.collect::<Result<Vec<_>, _>>()`. If a single message in the batch is invalid (duplicate request/response, already-processed receipt, expired timeout, unknown request, etc.), the whole `execute` call returns `Err(Error::InvalidMessage)`, and because `handle_unsigned` is annotated `#[frame_support::transactional]`, every state change from every other (valid) message in that same batch is rolled back. This is the direct analog of the reported `QVBaseStrategy._distribute` bug class: an entire iteration through many entries is voided by one bad entry.

### Finding Description
`handle_unsigned`: [1](#0-0) 

is `ensure_none` (unsigned, permissionless, callable by anyone with a valid proof) and wraps `Self::execute(messages.clone())` in `#[frame_support::transactional]`.

`execute` processes the whole batch and short-circuits on the first error via `collect::<Result<Vec<_>, _>>()`: [2](#0-1) 

Each message handler (`handle_incoming_message` → e.g. `request.rs`, `response.rs`, `timeout.rs`) performs expensive consensus-state lookups, Merkle/state membership or non-membership proof verification, and receipt/commitment checks before it can determine validity — e.g. duplicate-request/response checks and timeout checks happen only after proof verification: [3](#0-2) [4](#0-3) 

Because `.map(...).collect::<Result<Vec<_>,_>>()` in `execute` returns on the first `Err`, the entire batch's `handle_unsigned` call fails with `Error::<T>::InvalidMessage`, and the `transactional` wrapper reverts every state mutation performed by all messages processed before the failing one — even those that had already passed proof verification and would otherwise have succeeded.

Unlike the EVM `HandlerV2`/`EvmHost` path — where a per-request `on_accept`/`on_response` module callback failure is caught and the receipt is deleted without reverting the rest of the batch (as documented in `sdk/packages/core/docs/ai/flows/...`) — the pallet's unsigned-batch path has no such isolation: a single stale/duplicate/expired message anywhere in the batch forces the whole batch to fail.

### Impact Explanation
Because `handle_unsigned` is an unsigned extrinsic executed for free by the relayer (no fee charged for a failing unsigned call, but the relayer still burns real compute/weight and, more importantly, opportunity cost and potential retries), a large batch of otherwise-valid ISMP messages (post requests, get responses, timeouts) can be entirely voided by a single bad or already-processed entry mixed into the same batch (e.g., due to a race with another relayer, or a malicious relayer intentionally appending one duplicate/expired message to a legitimate large batch). This wastes the substantial computational work (consensus verification, MMR/Merkle membership proofs, state-proof verification against potentially large state roots) performed for every other message in the batch, and delays delivery of all messages in the batch, which can matter for time-sensitive cross-chain messages nearing their timeout window. This maps to "a route unable to deliver messages" for the entire batch rather than just the single bad entry, satisfying the required impact category.

### Likelihood Explanation
Likelihood is elevated because: (1) the extrinsic is unsigned and permissionless — any relayer or attacker can submit `handle_unsigned` with an arbitrary message list; (2) batches naturally accumulate many messages relayed concurrently by multiple actors, so a race where one message is delivered by a competing relayer before another's batch lands is realistic and not attacker-dependent; (3) a malicious actor could deliberately append a single already-delivered or expired message to a victim relayer's otherwise valid batch (if batches are constructed from a public mempool of pending messages) to grief delivery of the whole batch.

### Recommendation
Change `Pallet::execute` to process messages independently rather than short-circuiting the whole batch on the first failure: collect per-message `Result`s without early termination (e.g., iterate and continue, similar to how `EvmHost.dispatchIncoming` catches per-message failures), commit state for all successfully-handled messages, and only emit `Event::Errors` / skip the individual failing message instead of returning `Err(Error::InvalidMessage)` for the entire batch under `#[frame_support::transactional]`. If a global rollback is intentionally desired for safety, consider splitting large `Vec<Message>` batches so a single bad message's blast radius is limited, or validate all messages' basic liveness (non-duplicate, non-expired) cheaply prior to the expensive proof-verification pass so failures are caught before doing wasted proof-verification work for the rest of the batch.

### Proof of Concept
1. A relayer collects `N` valid, distinct ISMP `Message`s (post requests/get responses/timeouts) destined for delivery, each requiring real state/consensus proof verification, and submits them together via `handle_unsigned(origin, messages)`.
2. Before this transaction is included, one of the `N` messages is delivered by a separate relayer's transaction (or is a duplicate/expired message the relayer failed to filter), so its receipt/commitment is already consumed or its timeout window has passed.
3. When the batched `handle_unsigned` executes, `Pallet::execute` iterates all `N` messages via `handle_incoming_message`; the corresponding handler (`modules/ismp/core/src/handlers/request.rs`, `response.rs`, or `timeout.rs`) returns `Err` for the already-processed/expired message (e.g. `Error::DuplicateRequest`, `Error::RequestTimeoutNotElapsed`, `Error::UnknownRequest`) after having already performed proof verification for that and possibly prior messages.
4. `.collect::<Result<Vec<_>, _>>()` in `execute` surfaces this single error, `execute` returns `Err(Error::InvalidMessage)`, and because `handle_unsigned` is `#[frame_support::transactional]`, the entire extrinsic reverts — discarding successful delivery of the other `N-1` valid messages and wasting all the proof-verification work performed for the whole batch. [5](#0-4) [6](#0-5)

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

**File:** modules/ismp/core/src/handlers/response.rs (L34-68)
```rust
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
```

**File:** modules/ismp/core/src/handlers/timeout.rs (L139-164)
```rust
		TimeoutMessage::Get { requests } => {
			let wrapped: Vec<Request> = requests.iter().cloned().map(Request::Get).collect();
			dedup_requests::<H>(&wrapped)?;

			for get in &requests {
				let commitment = hash_request::<H>(&Request::Get(get.clone()));
				// if we have a commitment, it came from us
				if host.request_commitment(commitment).is_err() {
					Err(Error::UnknownRequest { meta: get.into() })?
				}

				// Reject the timeout if a response has already been received for this request
				let response = GetResponse { get: get.clone(), values: Default::default() };
				if host.response_receipt(&response).is_some() {
					Err(Error::GetResponseAlreadyReceived { meta: get.into() })?
				}

				// Ensure the get timeout has elapsed on the host
				if !get.timed_out(host.timestamp()) {
					Err(Error::RequestTimeoutNotElapsed {
						meta: get.into(),
						timeout_timestamp: get.timeout(),
						state_machine_time: host.timestamp(),
					})?
				}
			}
```
