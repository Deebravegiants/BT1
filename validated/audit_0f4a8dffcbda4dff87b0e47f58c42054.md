### Title
Free, Unbounded Computation in `pallet-ismp`'s `validate_unsigned` Enables Transaction-Pool DoS via Crafted `handle_unsigned` Payload - (File: `modules/pallets/ismp/src/lib.rs`)

### Summary
`pallet_ismp::Call::handle_unsigned` is a permissionless, unsigned extrinsic that lets anyone submit an arbitrary `Vec<Message>` of ISMP datagrams "for free" [1](#0-0) . Its `ValidateUnsigned::validate_unsigned` implementation does not merely check basic shape/signature — it fully executes `Self::execute(messages.clone())`, which runs proof/consensus verification, MMR/trie membership checks, and dispatch logic for every message in the batch, before the transaction is even accepted into a block [2](#0-1) . Since this happens during mere pool validation (which every relaying full node performs, repeatedly, for every unsigned extrinsic it receives and re-validates against `longevity: 25`), an attacker can submit large/expensive but ultimately invalid message batches to force every validating node to repeatedly perform the full, expensive verification workload at zero cost to the attacker — a computational-complexity denial-of-service, directly analogous to the Jenkins CVE-2013-0331 "crafted payload causes DoS" bug class (CWE-20).

### Finding Description
`handle_unsigned` takes an unbounded `Vec<Message>` with no pallet-level cap on batch size or on the sizes of nested fields (e.g., `GetRequest.keys: Vec<Vec<u8>>`, arbitrary `context`, arbitrarily large consensus `proof` bytes, or large MMR/trie multiproofs) [3](#0-2) . Because the call is unsigned (`ensure_none(origin)?`), it has no signer to charge a pre-execution fee against, and its true computational weight is only known post-execution (`actual_weight`), not upfront [4](#0-3) .

Critically, `ValidateUnsigned::validate_unsigned` for this pallet calls `Self::execute(messages.clone())` directly to decide transaction validity [2](#0-1) . `execute` runs `handle_incoming_message` for every message, which performs full consensus-proof verification, MMR/trie membership or non-membership proof checking, and signature verification for requests/responses [5](#0-4) [6](#0-5) . This is expensive cryptographic and trie work (e.g., BEEFY/consensus verification, Merkle-Mountain-Range multi-proof verification, child-trie non-membership checks over many keys) [7](#0-6) .

Transaction-pool validation is performed by every node that receives the gossiped extrinsic, and is re-run repeatedly for as long as the transaction remains valid/pending (here `longevity: 25` blocks) [8](#0-7) . An attacker can craft a `handle_unsigned` payload containing many messages, or messages with maximal-size proofs/keys/contexts, that is guaranteed to ultimately fail (so it never lands in a block and is never charged even the notional weight/fee), yet forces every peer node's pool validation to perform the full, expensive `execute` computation on every (re-)validation attempt. This lets a single unprivileged actor (no special role required — the whole point of `handle_unsigned` is that "anyone" can submit ISMP datagrams "for free") impose disproportionate, repeated computational cost on the network with a single crafted extrinsic, and can be trivially repeated/parallelized to amplify the effect.

### Impact Explanation
This is a Medium-severity denial-of-service: it does not directly cause loss of funds, but it lets any unprivileged party degrade block-production and transaction-processing throughput of validating/collating nodes by flooding the network with crafted `handle_unsigned` payloads that are expensive to validate but cheap (free, unsigned) to submit and are not required to ever be included on-chain. This matches the reachable-path requirement ("a route unable to deliver messages") because sustained validation-time exhaustion can starve legitimate relayed message processing, delaying or preventing delivery of real cross-chain messages.

### Likelihood Explanation
Likelihood is high: `handle_unsigned` is explicitly designed to be callable by anyone without authentication or fee ("This allows users execute ISMP datagrams for free. Use with caution.") [9](#0-8) , requires no state setup, no relayer registration, and no capital at risk. Any relayer, message dispatcher, or bystander with network access to submit an unsigned extrinsic can trigger the expensive `validate_unsigned` path on demand.

### Recommendation
- Avoid performing full message execution inside `validate_unsigned`; restrict validation there to cheap, structural checks (e.g., message-type whitelist, basic bounds, cached/pre-verified state) and defer expensive cryptographic/trie verification to `pre_dispatch`/actual dispatch, which is charged against declared weight.
- Enforce a hard cap on `messages.len()` and on the sizes of nested fields (proof bytes, MMR multiproof length, key/context vectors) accepted by `handle_unsigned`, rejecting oversized batches before any verification work is attempted.
- Consider computing a cheap, size-based pre-validation weight estimate to reject clearly oversized/abusive payloads before invoking `execute`, and/or reduce `longevity` to limit the number of re-validations an unconfirmed unsigned extrinsic can trigger.

### Proof of Concept
1. An attacker constructs a `pallet_ismp::Call::handle_unsigned { messages }` where `messages` is a large `Vec<Message>` (e.g., many `Message::Response` entries each carrying maximal-size non-membership/membership proofs and large key vectors, per the `GetRequest.keys` / `StateMachineProof.storage_proof` shapes) that will ultimately fail some later check (so it's `InvalidMessage`/`BadProof` and never included on-chain).
2. Attacker submits this as an unsigned extrinsic and gossips it (or repeatedly resubmits variants) to the network.
3. Every full node that receives the extrinsic runs `ValidateUnsigned::validate_unsigned`, which calls `Self::execute(messages.clone())`, fully executing consensus/MMR/trie verification for the entire batch [2](#0-1) .
4. Because this happens at zero cost to the attacker (unsigned, no successful inclusion required) and is re-triggered on re-validation/re-gossip (`longevity: 25`), repeated submission of such crafted payloads consumes disproportionate CPU across the network's validating nodes, degrading throughput — the DoS-via-crafted-payload analog of CVE-2013-0331.

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

**File:** modules/pallets/ismp/src/lib.rs (L638-645)
```rust
				return Ok(ValidTransaction {
					priority: latest_height,
					requires: vec![],
					provides: vec![sp_io::hashing::keccak_256(&state_machine_id.encode()).to_vec()],
					longevity: 25,
					propagate: true,
				});
			}
```

**File:** modules/pallets/ismp/src/impls.rs (L40-87)
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

**File:** modules/ismp/core/src/handlers.rs (L85-99)
```rust
/// This function serves as an entry point to handle the message types provided by the ISMP protocol
pub fn handle_incoming_message<H>(
	host: &H,
	message: Message,
) -> Result<MessageResult, anyhow::Error>
where
	H: IsmpHost,
{
	match message {
		Message::Consensus(consensus_message) => consensus::update_client(host, consensus_message),
		Message::FraudProof(fraud_proof) => consensus::freeze_client(host, fraud_proof),
		Message::Request(req) => request::handle(host, req),
		Message::Response(resp) => response::handle(host, resp),
		Message::Timeout(timeout) => timeout::handle(host, timeout),
	}
```

**File:** modules/ismp/state-machines/substrate/src/lib.rs (L185-238)
```rust
	fn verify_non_membership(
		&self,
		_host: &dyn IsmpHost,
		commitments: Vec<H256>,
		root: StateCommitment,
		proof: &Proof,
	) -> Result<(), Error> {
		let StateMachineProof { hasher, storage_proof } =
			codec::Decode::decode(&mut &*proof.proof)
				.map_err(SubstrateStateMachineError::ProofDecodeError)?;

		// Request receipts live in the ISMP child trie, so non-membership is verified against
		// the overlay root — unless the request originates from the coprocessor itself, whose
		// ISMP storage is part of its global state.
		let root = match T::Coprocessor::get() {
			Some(id) if id == proof.height.id.state_id => root.state_root,
			_ => root.overlay_root.ok_or(SubstrateStateMachineError::MissingChildTrieRoot)?,
		};

		let keys = self.receipts_state_trie_key(commitments);

		let check_absent = |value: Option<Vec<u8>>| -> Result<(), SubstrateStateMachineError> {
			if value.is_some() {
				Err(SubstrateStateMachineError::DeliveredRequestsInBatch)
			} else {
				Ok(())
			}
		};

		match hasher {
			HashAlgorithm::Keccak => {
				let db = StorageProof::new(storage_proof).into_memory_db::<Keccak256>();
				let trie = TrieDBBuilder::<LayoutV0<Keccak256>>::new(&db, &root).build();
				for key in keys {
					let value = trie
						.get(&key)
						.map_err(|e| SubstrateStateMachineError::TrieError(format!("{e:?}")))?;
					check_absent(value)?;
				}
			},
			HashAlgorithm::Blake2 => {
				let db = StorageProof::new(storage_proof).into_memory_db::<BlakeTwo256>();
				let trie = TrieDBBuilder::<LayoutV0<BlakeTwo256>>::new(&db, &root).build();
				for key in keys {
					let value = trie
						.get(&key)
						.map_err(|e| SubstrateStateMachineError::TrieError(format!("{e:?}")))?;
					check_absent(value)?;
				}
			},
		}

		Ok(())
	}
```
