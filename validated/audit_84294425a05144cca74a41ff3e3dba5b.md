### Title
Unsigned `handle_unsigned` messages force full ISMP proof/consensus verification during `validate_unsigned` with no fee and no rate limit, enabling free-of-charge DoS - ([File: modules/pallets/ismp/src/lib.rs])

### Summary
`pallet_ismp::Call::handle_unsigned` is deliberately unsigned and free — a design choice documented as letting relayers "execute ISMP datagrams for free" [1](#0-0) . To decide whether such a transaction may enter the pool, `ValidateUnsigned::validate_unsigned` calls `Self::execute(messages.clone())` directly — i.e., it runs the *entire* message-handling pipeline (state-machine validation, consensus-client lookup, request/response de-duplication, and full state/consensus membership proof verification) purely to populate the transaction pool, before any block inclusion or fee is charged [2](#0-1) . `Self::execute` itself iterates the whole batch and invokes `handle_incoming_message` for every message, which performs cryptographic/state proof verification per `ismp::handlers` [3](#0-2) . Unlike Discourse's `POST /uploads`, which lacked a rate limit on a resource-intensive upload-processing operation, `handle_unsigned` has no per-caller throttle, quota, or fee gate protecting this expensive verification path — any unprivileged network peer can gossip an unlimited stream of syntactically-valid-but-cryptographically-failing (or successful) message batches, each one forcing every validating/full node to redo full proof verification for free.

### Finding Description
- The call is explicitly unsigned (`ensure_none(origin)`) and documented as executing "for free" [4](#0-3) .
- `validate_unsigned` does not perform a cheap, bounded pre-check before running the expensive path; it calls `Self::execute(messages.clone())` unconditionally for every submitted batch, which is the same function that performs full state-machine validation and per-message request/response handling — the only differentiation from real dispatch is that the resulting mutations are discarded on validation failure by pool semantics, but the CPU work (crypto/proof verification) has already been spent [2](#0-1) .
- `Self::execute` fans out over `messages.iter().map(|msg| handle_incoming_message(&host, msg.clone()))`, so a single extrinsic can carry an arbitrarily large `Vec<Message>` (bounded only by block/extrinsic size limits, not by a dedicated rate limiter), each entry independently invoking consensus-client and state-proof verification logic (BEEFY/GRANDPA/SP1/state membership, per `modules/ismp/core/src/handlers/request.rs`) [5](#0-4) .
- Only the *sibling* `pallet-state-coprocessor` module bandwidth-gates its own unsigned `handle_unsigned` for `GetRequestsWithProof` via `T::BandwidthGate::try_consume` [6](#0-5) , but that gate is applied only after proof verification has already run, and does not exist at all for the core `pallet-ismp` `handle_unsigned` path that handles Post/Response/Consensus/Timeout messages. No equivalent per-source-chain / per-relayer / per-block quota exists in `modules/pallets/ismp/src/lib.rs` for consensus or request/response messages.
- The only mempool protections present are generic dedup via `provides` tags (identical batches collapse to one tag) and `longevity: 25` [7](#0-6)  — neither of which prevents an attacker from submitting *many distinct* batches (e.g., varying nonces, or minor proof mutations) that each force a fresh, full verification pass with no cost to the submitter, since the transaction is unsigned and carries no fee.

### Impact Explanation
Because verification of BEEFY/GRANDPA/SP1 consensus proofs and Merkle/trie state-membership proofs is computationally expensive (signature aggregation checks, trie traversal, potentially SP1 zkVM verification), and this work is triggered during `validate_unsigned` — which every full/validating node runs on every gossiped transaction, before it is ever included in a block — an attacker can flood the network with computationally heavy, free, unsigned `handle_unsigned` calls. This degrades transaction-pool validation throughput network-wide, delaying legitimate relayer message delivery (a route unable to deliver messages) and potentially starving block production/validation resources on collators/validators. This is a resource-exhaustion DoS reachable by any unprivileged party who can gossip a transaction — no relayer registration, fee payment, or prior state is required.

### Likelihood Explanation
High. `handle_unsigned` is explicitly designed to be callable by anyone without payment; the only barrier to spamming it is producing syntactically valid `Message` structures (not necessarily proofs that verify successfully — verification cost is incurred regardless of the outcome). An attacker needs no special access, funds beyond network bandwidth, or privileged role — this is directly reachable from a single unprivileged network peer submitting arbitrary unsigned extrinsics, matching the "unprivileged relayer" threat profile explicitly in scope.

### Recommendation
Add a cheap, bounded pre-validation stage in `validate_unsigned` before invoking `Self::execute` — e.g., structural/size limits on `messages.len()` and per-message proof size, and/or a lightweight signature/format sanity check — so that expensive cryptographic verification is only performed once a message has passed inexpensive filters. Additionally, consider applying a bandwidth/rate-limiting gate (similar to `BandwidthGate` already used in `pallet-state-coprocessor`) to the core `pallet-ismp::handle_unsigned` path, and/or require a bond or per-source-chain quota that is refunded on success but slashed/consumed on repeated invalid submissions, to make sustained spam economically costly.

### Proof of Concept
1. An attacker crafts an unsigned extrinsic `pallet_ismp::Call::handle_unsigned { messages }` where `messages` is a large `Vec<Message>` of `Message::Request(RequestMessage)` or `Message::Consensus(ConsensusMessage)` entries with plausible but ultimately invalid/expensive-to-check proofs (e.g., large membership proofs or crafted consensus proof bytes that require full cryptographic evaluation before failing).
2. The attacker gossips many such distinct extrinsics (varying nonces/proof bytes to avoid the `provides`-tag dedup) to the network with no signature and no fee.
3. Every node's transaction pool calls `ValidateUnsigned::validate_unsigned`, which calls `Self::execute(messages.clone())`, forcing full state-machine/consensus/proof verification for every batch, for every peer, at zero cost to the attacker [2](#0-1) .
4. Sustained submission degrades transaction-pool validation capacity network-wide, delaying inclusion of legitimate relayer messages — the described route-unable-to-deliver-messages impact.

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

**File:** modules/pallets/ismp/src/lib.rs (L604-612)
```rust
	/// This allows users execute ISMP datagrams for free. Use with caution.
	#[pallet::validate_unsigned]
	impl<T: Config> ValidateUnsigned for Pallet<T> {
		type Call = Call<T>;

		// empty pre-dispatch do we don't modify storage
		fn pre_dispatch(_call: &Self::Call) -> Result<(), TransactionValidityError> {
			Ok(())
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

**File:** modules/pallets/ismp/src/lib.rs (L638-644)
```rust
				return Ok(ValidTransaction {
					priority: latest_height,
					requires: vec![],
					provides: vec![sp_io::hashing::keccak_256(&state_machine_id.encode()).to_vec()],
					longevity: 25,
					propagate: true,
				});
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

**File:** modules/pallets/state-coprocessor/src/impls.rs (L142-151)
```rust
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
```
