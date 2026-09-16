Based on my research, I found a concrete analog to the HTTP/2 Rapid Reset bug class (cheap request triggers expensive, uncompensated server-side work, repeatable at will) in `pallet-ismp`'s unsigned message path.

### Title
Fee-less `handle_unsigned` triggers full, uncapped ISMP message execution (crypto proof verification) during mempool validation, allowing unbounded free CPU consumption that starves message delivery - ([File: modules/pallets/ismp/src/lib.rs])

### Summary
`pallet_ismp::Call::handle_unsigned` is designed to let anyone relay ISMP messages "for free" as an unsigned extrinsic [1](#0-0) . The pallet's `ValidateUnsigned::validate_unsigned` implementation does not perform a lightweight pre-check — it directly calls `Self::execute(messages.clone())`, which runs the *entire* message-handling pipeline including full state-proof/consensus-proof cryptographic verification, exactly the same work that block execution will later redo [2](#0-1) .

### Finding Description
`execute()` is the real work function: for every message in the batch it calls `handle_incoming_message`, which for `RequestMessage`/`ResponseMessage`/`TimeoutMessage` performs Merkle/trie state-membership or non-membership verification against a stored state commitment, and for `ConsensusMessage` runs the full consensus-client verification logic [3](#0-2) . This same `execute` is invoked both from `validate_unsigned` (mempool/gossip validation stage) and from the dispatchable `handle_unsigned` call itself (block execution stage) [4](#0-3) .

Because the extrinsic is unsigned, there is no fee and no signer to penalize — the documentation explicitly acknowledges the intended mitigation is "the transaction pool will check if the submitted extrinsics are valid before they are included," relying on the assumption that the validity check itself is cheap [5](#0-4) . In reality the validity check *is* the expensive operation (full proof verification over an attacker-controlled batch of `requests`/`responses`/`timeouts`, with no visible cap on batch size enforced before verification runs).

This mirrors the HTTP/2 Rapid Reset bug class precisely: a cheap, permissionless message (an unsigned transaction gossiped to every node on the network) forces the recipient to perform expensive setup work (full cryptographic proof verification) before the "stream"/transaction can be rejected as invalid — and the requester can repeat this indefinitely at zero cost, since a failed unsigned transaction incurs no fee or penalty. Every full node that receives the gossiped transaction (not just the block author) independently re-executes `validate_unsigned` and therefore re-runs the full proof verification, multiplying the attacker's cost-asymmetry advantage across the entire validator/collator set.

### Impact Explanation
An attacker can flood the network with a stream of unsigned `handle_unsigned` extrinsics carrying syntactically valid but ultimately-failing (or maximally-sized) proofs. Each one forces every full node in the network to perform full Merkle/state-trie/consensus verification before rejecting it, for free, unboundedly. Sustained at scale this consumes collator/validator CPU that would otherwise be used to include legitimate relayed messages, effectively creating a route that becomes unable to deliver messages — the concrete "route unable to deliver messages" impact.

### Likelihood Explanation
The path is fully permissionless and unauthenticated by design (`ensure_none(origin)`), reachable directly from any relayer/dispatcher on the p2p network with no economic cost. The only friction is that the attacker must craft plausible messages (valid-looking heights/state ids) to reach the expensive verification branches, which is straightforward since consensus state and state-commitment metadata are public on-chain.

### Recommendation
Split `validate_unsigned` into a cheap, bounded pre-check (e.g. check known state-machine height exists, batch-size limits, structural sanity) from the expensive cryptographic verification, and only run full proof verification once during actual block execution (in the dispatchable), not during every node's mempool validation. Alternatively, impose a strict, low bound on the number of requests/responses/timeouts per unsigned batch and rate-limit/charge computational cost proportionally even for unsigned submissions (e.g. via a bandwidth/reputation gate similar to what `pallet-state-coprocessor` already does for its own unsigned call) [6](#0-5) .

### Proof of Concept
1. Craft an unsigned `Ismp::handle_unsigned` extrinsic carrying a `RequestMessage` with a large `requests` vector and a matching but ultimately-invalid state proof (e.g. mismatched leaf at the last index) targeting a real, previously-stored state commitment.
2. Submit many distinct such extrinsics (varying content so `provides` tags differ and the pool does not dedupe them) to the network in rapid succession.
3. Each node receiving these via gossip calls `validate_unsigned`, which calls `Self::execute`, performing full membership/non-membership verification over the entire batch before ultimately failing and dropping the transaction — at zero cost to the attacker and full crypto-verification cost to every node [7](#0-6) .
4. Repeating this continuously starves nodes' CPU for message-pool validation and block authoring of legitimate ISMP traffic.

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

**File:** modules/pallets/ismp/src/lib.rs (L604-625)
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

**File:** docs/content/developers/polkadot/pallet-ismp/overview.mdx (L256-258)
```text
## Transaction fees

Pallet ISMP uses unsigned transactions for executing cross-chain messages. This means all cross-chain messages received are executed for free as unsigned transactions. The upside to this is that it cannot be exploited as a spam vector, since the transaction pool will check if the submitted extrinsics are valid before they are included in the pool. This validity check ensures that the transaction can be successfully executed and contains valid proofs. Malformed messages or those with invalid proofs are filtered out by the transaction pool validation logic preventing unnecessary processing and potential network congestion.
```

**File:** modules/pallets/state-coprocessor/src/impls.rs (L140-152)
```rust
			let response = GetResponse { get: req, values };

			// Meter the app's bandwidth using the full size of the
			// abi-encoded GetResponse. Charged after proof verification
			// so the value sizes are final.
			let bytes = ismp::abi::encode_get_response(&response).len() as u32;
			<T as Config>::BandwidthGate::try_consume(
				&response.get.source,
				&response.get.from,
				bytes,
			)
			.map_err(|err| Error::Custom(alloc::format!("bandwidth gate: {err}")))?;
			total_bytes = total_bytes.saturating_add(bytes);
```
