### Title
`handle_unsigned` charges a static, message-count-independent extrinsic weight while discarding the actual computed weight, allowing block-weight-limit bypass and free-of-charge chain DoS - ([File: modules/pallets/ismp/src/lib.rs])

### Summary
`pallet_ismp::Pallet::handle_unsigned` is an **unsigned**, fee-less extrinsic that accepts an **unbounded** `Vec<Message>` and dispatches every message to arbitrary registered ISMP router modules via `Self::execute(messages)`. Its pre-dispatch weight is declared as a static `weight()` value rather than one that scales with the number/size of messages in the batch, and the real, message-derived weight computed later inside `execute()` is discarded instead of being returned as `actual_weight`. This mirrors the root cause of the Evmos `MsgEthereumTx`/authz advisory: a message-processing entry point whose declared cost does not reflect the true execution cost, enabling an attacker to bypass the block's resource-accounting limit and stall block production.

### Finding Description
`handle_unsigned` is declared with a fixed weight annotation and takes an arbitrary-length, arbitrary-content batch of ISMP messages: [1](#0-0) 

Internally, `Pallet::<T>::execute` runs `handle_incoming_message` for every message (invoking arbitrary destination-module callbacks such as `on_accept`/`on_response`/`on_timeout`) and only afterwards calls `T::FeeHandler::on_executed(messages_with_weights, events)` to compute the *actual* consumed weight and settle fees — but the `DispatchResultWithPostInfo` returned by `on_executed` (which carries `actual_weight`) is never propagated back to the caller: [2](#0-1) 

Because `handle_unsigned` unconditionally returns `Ok(().into())` regardless of what `execute()` computed, the substrate transaction-weight/fee subsystem only ever "sees" the static pre-dispatch weight declared by the `#[pallet::weight(weight())]` attribute — not the true, message-count-dependent cost of running potentially many nested module callbacks (`on_accept`, `on_response`, etc., which is exactly the extension point third-party pallets/apps plug expensive logic into, per the documented `WeightProvider`/`IsmpModuleWeight` interfaces): [3](#0-2) [4](#0-3) 

This is functionally the same bug class as the Evmos advisory: an entry point that lets an unprivileged party dispatch nested, unbounded execution (here: an unbounded `Vec<Message>` batch fanned out to arbitrary module callbacks) while the enclosing dispatch's accounted cost (gas in Evmos / weight here) does not scale with the actual work performed, letting the true resource usage silently exceed the limit the runtime believes it is enforcing.

### Impact Explanation
If the declared static weight for `handle_unsigned` under-represents the true cost of processing a large or adversarially-crafted batch of valid messages (each requiring proof verification plus a module `on_accept`/`on_response` callback), a single unsigned, fee-less extrinsic can consume far more actual computation than the block's weight limit accounting expects. Because the extrinsic is unsigned and pays no fee (`ensure_none(origin)`), this can be resubmitted freely by any relayer/attacker, causing block production to slow or stall — a Denial-of-Service against the whole chain, matching the "Critical" impact class described in the reference advisory (bypass of the resource limit that gates message execution, leading to chain halt/DoS).

### Likelihood Explanation
`handle_unsigned` is reachable by any unprivileged party who can submit valid ISMP proofs (its whole purpose is to let "anyone execute ISMP messages for free provided they have valid proofs"), and `messages: Vec<Message>` has no batch-size cap enforced in the pallet itself. Constructing a batch that maximizes module-callback cost while staying within transaction-pool validity checks (`validate_unsigned` re-executes the batch, so any message that "works" once will pass) is a realistic attack once mempool/tx-pool size limits are the only gate.

### Recommendation
- Make the declared `#[pallet::weight(...)]` for `handle_unsigned` a function of `messages.len()` (and ideally message type/size), using worst-case per-message weight (`IsmpModuleWeight`/`WeightProvider` benchmarks) rather than a static constant.
- Propagate the `actual_weight` computed by `T::FeeHandler::on_executed` back out of `execute()` into the `DispatchResultWithPostInfo` returned by `handle_unsigned`, so Substrate's post-dispatch weight correction/refund and block-weight accounting reflect real work done.
- Enforce an explicit maximum on `messages.len()` per `handle_unsigned` call (and reject unusually large/expensive batches at `validate_unsigned` time) to bound worst-case per-extrinsic weight.

### Proof of Concept
1. An attacker (or colluding relayer) obtains/produces valid proofs for a large number (N) of `Request`/`Response` messages destined for a module whose `on_accept`/`on_response` callback performs non-trivial, unbounded work (e.g., large storage reads/writes or loops over externally supplied data), as permitted by the `WeightProvider`/`IsmpModuleWeight` extension points.
2. The attacker submits a single unsigned `Ismp::handle_unsigned(messages: vec![msg_1, ..., msg_N])` extrinsic; because it is unsigned it costs nothing and only needs to pass `validate_unsigned`, which itself re-executes `Self::execute(messages)` — proving the batch is "valid" and thus admissible. [5](#0-4) 
3. On inclusion, `execute()` processes all N messages/callbacks, but the extrinsic's weight charged against the block is the static `weight()` value declared on `handle_unsigned`, not a function of N or the callbacks' real cost, and the true `actual_weight` from `FeeHandler::on_executed` is discarded. [6](#0-5) 
4. By repeating this with sufficiently large/expensive batches, the attacker can push actual per-block computation well past the block's real weight budget while the runtime's weight accounting believes it has stayed within limits, stalling block production chain-wide — free of charge, since the call is unsigned and unpriced up front.

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

**File:** modules/pallets/ismp/src/fee_handler.rs (L106-112)
```rust
	fn on_executed(
		messages: Vec<MessageWithWeight>,
		events: Vec<Event>,
	) -> DispatchResultWithPostInfo;
}

/// A weight-based fee handler implementation that calculates and charges fees based on message
```

**File:** modules/pallets/ismp/src/weights.rs (L24-52)
```rust
/// Interface for providing the weight information about [`IsmpModule`](ismp::module::IsmpModule)
/// callbacks
pub trait IsmpModuleWeight {
	/// Should return the weight used in processing this request
	fn on_accept(&self, request: &PostRequest) -> Weight;
	/// Should return the weight used in processing this timeout
	fn on_timeout(&self, request: &Request) -> Weight;
	/// Should return the weight used in processing this response
	fn on_response(&self, response: &GetResponse) -> Weight;
}

impl IsmpModuleWeight for () {
	fn on_accept(&self, _request: &PostRequest) -> Weight {
		Weight::zero()
	}
	fn on_timeout(&self, _request: &Request) -> Weight {
		Weight::zero()
	}
	fn on_response(&self, _response: &GetResponse) -> Weight {
		Weight::zero()
	}
}

/// An interface for querying the [`IsmpModuleWeight`] for a given
/// [`IsmpModule`](ismp::module::IsmpModule)
pub trait WeightProvider {
	/// Returns a reference to the weight provider for a module
	fn module_callback(dest_module: ModuleId) -> Option<Box<dyn IsmpModuleWeight>>;
}
```
