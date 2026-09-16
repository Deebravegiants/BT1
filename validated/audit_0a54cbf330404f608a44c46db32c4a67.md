## Title
Unbounded, statically-weighted `pallet_ismp::handle_unsigned` batches permit resource exhaustion via mempool/execution amplification - (File: `modules/pallets/ismp/src/lib.rs`)

### Summary
`pallet_ismp::Pallet::handle_unsigned` is a permissionless, free (`ensure_none`) unsigned extrinsic that accepts an **unbounded** `Vec<Message>` and is annotated with a **fixed** weight of `Weight::from_parts(300_000_000, 0)` regardless of how many messages the batch contains [1](#0-0) . The same batch is fully executed twice per submission attempt — once inside `ValidateUnsigned::validate_unsigned` (mempool/gossip validation) and again at dispatch — via `Self::execute(messages.clone())`, which iterates every message and runs `handle_incoming_message` (full consensus/state-proof/trie verification per message) [2](#0-1) [3](#0-2) . Because the declared weight used for block-inclusion accounting is a static constant rather than scaling with `messages.len()` or the size/type of each message, an attacker can submit large batches whose real CPU/storage cost vastly exceeds the weight charged for them — the same "excessive resource consumption from improperly-bounded batch parsing/verification" bug class as CVE-2022-41725 (mime/multipart `ReadForm` not accounting for real per-part overhead against its declared budget).

### Finding Description
`handle_unsigned` takes `messages: Vec<Message>` with no `BoundedVec`/length cap at the call-site [4](#0-3) . The only external constraint is the runtime's generic max extrinsic/block-length limit, which is measured in raw bytes, not in verification cost. Each `Message` variant (`Request`, `Response`, `Timeout`, `Consensus`) triggers non-trivial cryptographic/trie work per element inside `handle_incoming_message` (e.g., state/non-membership trie proof verification, as seen for GET responses at `modules/ismp/core/src/handlers/response.rs`) [5](#0-4) .

The pallet weight annotation is a fixed constant explicitly documented as a placeholder ("Static weights because these should get overridden by the FeeHandler") [6](#0-5) , meaning Substrate's block-weight accounting (which gates how many extrinsics fit in a block and how much execution time is reserved) does not scale with the number or type of messages actually processed. Any per-message fee correction happens only in `T::FeeHandler::on_executed` *after* the batch has already been fully executed [7](#0-6) , i.e., after the resource consumption has already occurred, not before it, and it does not retroactively affect the weight already reserved for block-building.

Additionally, `validate_unsigned` performs the *entire* `execute()` pass (full message handling, not just signature/format checks) on every node that receives the transaction via gossip, before the transaction is even included in a block [2](#0-1) . Because the call is free (unsigned, no fee, `ensure_none`), an attacker does not need to pay for this validation-time cost, and can repeatedly resubmit differently-tagged (to avoid `provides` dedup) batches to force full re-validation across the network's mempools.

This mirrors the CVE's root cause: a size/resource-accounting parameter (`maxMemory`/weight) that is declared but not actually enforced proportionally to real work, permitting an unauthenticated caller to force consumption far beyond the declared/charged budget.

### Impact Explanation
Because `handle_unsigned` is reachable by any unprivileged relayer via a single unsigned extrinsic (matching the "unprivileged message dispatcher / relayer" reachability requirement), and its weight is statically under-declared relative to actual per-message trie-verification cost, an attacker can:
- Submit maximally-sized batches (bounded only by raw byte size, not verification cost) that consume disproportionate CPU/storage-read time during block authoring/import relative to the weight reserved, risking block-production slowdowns or missed block deadlines (a route becoming unable to reliably deliver/process messages).
- Force full-batch execution during `validate_unsigned` on every gossiping node for free, amplifying network-wide CPU cost per submitted transaction with no fee cost to the attacker.

This is a resource-exhaustion / potential liveness-degradation vector on the message-delivery pallet, not a funds-theft bug, so it maps to "a route unable to deliver messages" under the validation criteria.

### Likelihood Explanation
`handle_unsigned` is explicitly permissionless and free by design (documented as "This allows users execute ISMP datagrams for free. Use with caution.") [8](#0-7) , so no privileged access or governance action is needed to reach this path — only crafting a large `Vec<Message>` with valid-enough proofs/format to pass validation (or even invalid ones, since the full `execute()` cost is paid before rejection). The only mitigations in place are message-content-level validity checks (proofs must decode/verify) and generic block/extrinsic byte-size limits, neither of which bounds the number of expensive verification operations per batch nor scales the declared weight to match.

### Recommendation
Scale the weight annotation for `handle_unsigned` with `messages.len()` (and ideally per-message-type cost, e.g., number of proof keys/trie nodes) instead of using a fixed constant, so block-weight accounting reflects real work. Consider adding an explicit cap (e.g., `BoundedVec<Message, MaxMessagesPerBatch>`) on the number of messages per unsigned call, and/or a cheaper pre-check in `validate_unsigned` that rejects oversized/anomalous batches before running the full `execute()` path.

### Proof of Concept
No code execution environment is available to demonstrate this at runtime; the finding is derived from static analysis of `modules/pallets/ismp/src/lib.rs` (`handle_unsigned`, `validate_unsigned`, `weight()`) and `modules/pallets/ismp/src/impls.rs` (`execute`), showing (1) no length bound on `messages: Vec<Message>`, (2) a fixed weight constant independent of `messages.len()`, and (3) full-batch execution occurring inside `validate_unsigned` for every gossip validation pass.

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

**File:** modules/pallets/ismp/src/lib.rs (L604-606)
```rust
	/// This allows users execute ISMP datagrams for free. Use with caution.
	#[pallet::validate_unsigned]
	impl<T: Config> ValidateUnsigned for Pallet<T> {
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

**File:** modules/pallets/ismp/src/lib.rs (L727-730)
```rust
	/// Static weights because these should get overridden by the FeeHandler
	fn weight() -> Weight {
		Weight::from_parts(300_000_000, 0)
	}
```

**File:** modules/pallets/ismp/src/impls.rs (L37-87)
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

		let events = message_results
			.into_iter()
			// check that requests will be successfully dispatched
			// so we can not be spammed with failing txs
			.map(|result| match result {
				MessageResult::Request { events, .. } |
				MessageResult::Response { events, .. } |
				MessageResult::Timeout { events, .. } => events,
				MessageResult::ConsensusMessage(events) => events.into_iter().map(Ok).collect(),
				MessageResult::FrozenClient(_) => vec![],
			})
			.flatten()
			.collect::<Result<Vec<_>, _>>()
			.map_err(|err| {
				log::debug!(target: "ismp", "Handling Error {:#?}", err);
				Pallet::<T>::deposit_event(Event::<T>::Errors { errors: vec![err.into()] });
				Error::<T>::InvalidMessage
			})?;

		T::FeeHandler::on_executed(messages_with_weights, events.clone())
			.map_err(|_| Error::<T>::ErrorChargingFee)?;

		for event in events.clone() {
			// deposit any relevant events
			Pallet::<T>::deposit_event(event.into());
		}

		Ok(events)
	}
```

**File:** modules/ismp/core/src/handlers/response.rs (L76-90)
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

```
