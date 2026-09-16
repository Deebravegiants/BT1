### Title
Attacker can bundle a single always-failing ISMP message to revert an entire `handle_unsigned` batch, blocking delivery of unrelated legitimate requests/responses/timeouts - (File: `modules/pallets/ismp/src/impls.rs`)

### Summary
The `Ismp::handle_unsigned` extrinsic accepts a `Vec<Message>` and processes them atomically inside `Pallet::execute`. If the on-chain callback for even a single request/response/timeout within the batch fails, the whole extrinsic reverts, discarding all other valid messages bundled in the same call — the same class of "one bad item poisons the whole batch" bug described in the source Kairos report for `useCollateral`/`useOffer`.

### Finding Description
`Pallet::<T>::execute` calls `handle_incoming_message` for every message in the batch and collects results with `.collect::<Result<Vec<_>, _>>()` [1](#0-0) . Individual message handlers (e.g. `modules/ismp/core/src/handlers/request.rs::handle`) do *not* fail the whole message when a single request's module callback (`on_accept`) fails — that per-request failure is captured as an `Err` inside a `Vec<Result<Event, Error>>` returned as part of `MessageResult::Request { events, .. }` [2](#0-1) .

However, back in `execute`, all these per-item `Result`s across *all* messages in the batch are flattened and re-collected with another `.collect::<Result<Vec<_>, _>>()` [3](#0-2) . Because this is a `Result`-collect over a `Vec` gathered from every message's events, a single failing item anywhere in the batch short-circuits the whole thing into `Err(Error::InvalidMessage)`. Since `handle_unsigned` is wrapped in `#[frame_support::transactional]` [4](#0-3) , this error causes the entire extrinsic — and therefore every other unrelated, otherwise-valid message bundled alongside it — to be rolled back, even though they had valid proofs and would have succeeded individually.

`handle_unsigned` is a permissionless unsigned extrinsic ("permits anyone execute ISMP messages for free, provided they have valid proofs") [5](#0-4) , and relayers/tesseract naturally batch multiple pending messages into a single submission for efficiency (the equivalent EVM-side pattern, `IHandlerV2.batchCall`, explicitly documents "if any inner call reverts, the whole transaction reverts") [6](#0-5) . An attacker can dispatch a genuine, provable POST request from a source chain to a destination module deliberately chosen/crafted so that `on_accept` always fails (e.g., a module that reverts on any input, or one it fully controls). Once this request is proven and relayed, a relayer that opportunistically batches it together with unrelated legitimate messages in the same `handle_unsigned` call will have the entire batch revert, denying delivery to all bundled messages.

### Impact Explanation
This is a griefing/DoS vector against message delivery: legitimate requests, responses, and timeouts from unrelated users can be repeatedly blocked from being finalized on-chain whenever a relayer batches them with an attacker-crafted always-failing message, without the attacker needing any large capital outlay (only the cost of dispatching one cheap malicious request). This matches the "route unable to deliver messages" acceptance criterion — repeated grinding can stall relayer throughput and delay/deny legitimate cross-chain message delivery.

### Likelihood Explanation
Likelihood is moderate: the attacker needs control of (or ability to target) a destination module whose `on_accept`/callback can be made to fail deterministically, and needs the malicious message to end up batched with victim messages by relayer software that bundles multiple pending messages per `handle_unsigned` call for gas efficiency. Relayer batching behavior is an implementation detail outside the attacker's direct control, which somewhat limits reliability of exploitation, but the underlying atomicity flaw in `execute` is a straightforward root cause matching the reported bug class.

### Recommendation
Do not let one message's callback failure poison the whole `handle_unsigned` batch. Rework the events-collection step in `Pallet::execute` (`modules/pallets/ismp/src/impls.rs`, lines 59-76) so that per-request/response/timeout callback failures are recorded/emitted as failure events (as `request.rs` already intends) rather than propagated via `.collect::<Result<Vec<_>,_>>()` into an outer transactional error that reverts unrelated, successfully-processed messages in the same batch.

### Proof of Concept
1. Attacker dispatches (from a chain configured as an ISMP source) a POST request destined to a module address it controls, whose `IsmpModule::on_accept` implementation always returns `Err`.
2. Attacker (or anyone) relays this request with a valid membership proof to Hyperbridge/pallet-ismp.
3. A relayer batches this request together with N other unrelated, valid, pending requests/responses in a single `Ismp::handle_unsigned(messages)` call, since batching multiple pending messages into one extrinsic is standard relayer behavior for gas/nonce efficiency.
4. Inside `Pallet::execute`, `handle` for the attacker's request returns `MessageResult::Request` containing one `Err` event (module callback failed) [7](#0-6) .
5. When `execute` flattens and `.collect::<Result<Vec<_>, _>>()`s all events across the batch [8](#0-7) , the single `Err` causes the whole function to return `Err(Error::InvalidMessage)`.
6. Because `handle_unsigned` is `#[frame_support::transactional]`, the entire extrinsic reverts, and none of the N legitimate messages are delivered in that block, despite having valid proofs.

### Citations

**File:** modules/pallets/ismp/src/impls.rs (L43-51)
```rust
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

**File:** modules/pallets/ismp/src/impls.rs (L59-76)
```rust
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
```

**File:** modules/ismp/core/src/handlers/request.rs (L95-132)
```rust
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

**File:** tesseract/messaging/evm/src/tx.rs (L441-446)
```rust
/// Submit a full batch of ISMP messages as a single `IHandlerV2.batchCall` transaction.
///
/// One tx replaces what would otherwise be N separate txs (one per message),
/// cutting gas overhead and nonce management complexity. Atomic: if any
/// inner call reverts, the whole transaction reverts.
pub async fn submit_batch_messages(
```
