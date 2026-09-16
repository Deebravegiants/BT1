### Title
Unbounded `handle_unsigned` message batch causes attacker-triggered resource exhaustion during transaction-pool validation - ([File: modules/pallets/ismp/src/lib.rs])

### Summary
`pallet_ismp::Pallet::validate_unsigned` executes a full, unbounded `Vec<Message>` batch (via `Self::execute(messages.clone())`) before any transaction has been included in a block or paid for, mirroring the Scriban DoS class: attacker-controlled input sizes drive unbounded loops/allocations in a "safety-checked" path whose actual bound (weight/fee) never applies.

### Finding Description
`handle_unsigned` is an unsigned, free-to-submit extrinsic that accepts an arbitrary-length `messages: Vec<Message>`: [1](#0-0) 

Every node's transaction pool calls `ValidateUnsigned::validate_unsigned` for such extrinsics — before inclusion, before any weight/fee is charged, and repeatedly on re-validation (the transaction has `longevity: 25`, so it is re-checked across ~25 blocks of gossip/pool revalidation). That validation function fully executes the batch: [2](#0-1) 

`Self::execute` in turn walks every message and calls `handle_incoming_message`, which for `Message::Request`/`Message::Response`/`Message::Timeout` performs full state-machine proof verification (trie walks, storage-proof key iteration, consensus checks): [3](#0-2) [4](#0-3) 

Neither `messages: Vec<Message>` nor the nested `requests`/`keys` fields inside `RequestMessage`/`GetRequest` are bounded (`BoundedVec` or an explicit length cap) — grep across the codebase found no `MaxRequests`/`MaxKeys`/`BoundedVec<Message` type anywhere constraining these. The only weight declared for `handle_unsigned` is a static placeholder, not scaled by content size: [5](#0-4) 

The per-key trie verification loops (e.g. Substrate/EVM/Pharos state machines) iterate over the caller-supplied `keys: Vec<Vec<u8>>` with no cap, so a message batch with an extremely large number of requests/keys drives proportionally large trie lookups, key-hashing, and map construction inside `verify_state_proof`/`verify_membership`/`verify_non_membership`: [6](#0-5) [7](#0-6) 

This is the same bug class as the Scriban report: a nominal safety control exists (weight-based fees, `LoopLimit`-style bounding in the ISMP protocol design), but the actual code path that performs the expensive work (`validate_unsigned` executing the full batch) is reached and fully executed *before* that control (fee/weight enforcement, block inclusion) applies, and the batch/key sizes themselves are unbounded.

### Impact Explanation
Any unprivileged party can submit a single unsigned extrinsic to `handle_unsigned` with a very large `messages` vector (many `RequestMessage`/`GetRequest` entries, each carrying large `keys`/`requests` vectors) or with proof blobs that decode into large intermediate structures. Because this transaction is unsigned and free, and `validate_unsigned` executes the entire batch synchronously to determine pool validity, every full node that receives the transaction over p2p (before it ever lands in a block, and again on every pool re-validation cycle for up to ~25 blocks) performs the full cost of trie verification/hashing for that batch. This can be used to degrade or crash relayer/full nodes network-wide (CPU/memory exhaustion) without spending any fee, since a message batch that ultimately fails proof verification is simply dropped from the pool with no cost to the attacker, while every node still paid the full computational cost of trying to validate it.

### Likelihood Explanation
High: the attack requires only crafting and broadcasting a single unsigned extrinsic, requires no signature, no stake, no prior state, and no privileged role — squarely the "unprivileged message dispatcher/relayer" surface called out as in-scope. The lack of any explicit cap on `Vec<Message>` size or on nested `keys`/`requests` vectors, combined with `validate_unsigned` unconditionally running `Self::execute` to completion, makes this straightforward to trigger repeatedly and cheaply.

### Recommendation
- Bound `messages: Vec<Message>` in `handle_unsigned` (and the nested `RequestMessage::requests`, `GetRequest::keys`, etc.) with `BoundedVec<_, MaxX>` limits enforced at the SCALE-decode boundary, so oversized batches are rejected before `validate_unsigned` ever executes them.
- In `validate_unsigned`, perform cheap size/sanity checks (message count, aggregate key count, proof byte length) and reject batches exceeding a configured maximum *before* calling `Self::execute`.
- Make the declared weight for `handle_unsigned` scale with the actual batch size (number of messages, keys, proof bytes) rather than using the static `weight()` placeholder, so genuinely large batches are priced/rejected proportionally rather than executed for free.

### Proof of Concept
1. Construct an unsigned `pallet_ismp::Call::handle_unsigned` extrinsic with `messages` containing many `Message::Request(RequestMessage { requests: <very large Vec<PostRequest>>, .. })` or `GetRequest` entries whose `keys: Vec<Vec<u8>>` contain many large byte vectors (unbounded, per `modules/pallets/testsuite/.../pallet_call_decompressor.rs` test fixtures that already construct 1000-request / 256-key batches without hitting any cap).
2. Submit this extrinsic to a node's RPC. `pallet_ismp::Pallet::<T>::validate_unsigned` invokes `Self::execute(messages.clone())`, which calls `handle_incoming_message` for every entry, performing full trie/storage-proof verification work for the whole batch synchronously.
3. Because the transaction is unsigned, this costs the attacker nothing; because it is gossiped with `longevity: 25`, every peer node repeats this validation work on each of ~25 subsequent blocks until it expires or is rejected — for a batch large enough (bounded only by network/RPC payload limits, not by pallet-level caps), this consumes disproportionate CPU/memory across the network for free.

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

**File:** modules/ismp/core/src/handlers.rs (L86-100)
```rust
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
}
```

**File:** modules/ismp/state-machines/substrate/src/lib.rs (L240-277)
```rust
	fn verify_state_proof(
		&self,
		_host: &dyn IsmpHost,
		keys: Vec<Vec<u8>>,
		root: H256,
		proof: &Proof,
	) -> Result<BTreeMap<Vec<u8>, Option<Vec<u8>>>, Error> {
		// The trie root is supplied by the caller, bound to the calling context, so a relayer
		// cannot steer verification at the wrong trie.
		let StateMachineProof { hasher, storage_proof } =
			codec::Decode::decode(&mut &*proof.proof)
				.map_err(SubstrateStateMachineError::ProofDecodeError)?;
		let data = match hasher {
			HashAlgorithm::Keccak => {
				let db = StorageProof::new(storage_proof).into_memory_db::<Keccak256>();
				let trie = TrieDBBuilder::<LayoutV0<Keccak256>>::new(&db, &root).build();
				keys.into_iter()
					.map(|key| {
						let value = trie
							.get(&key)
							.map_err(|e| SubstrateStateMachineError::TrieError(format!("{e:?}")))?;
						Ok::<_, SubstrateStateMachineError>((key, value))
					})
					.collect::<Result<BTreeMap<_, _>, _>>()?
			},
			HashAlgorithm::Blake2 => {
				let db = StorageProof::new(storage_proof).into_memory_db::<BlakeTwo256>();
				let trie = TrieDBBuilder::<LayoutV0<BlakeTwo256>>::new(&db, &root).build();
				keys.into_iter()
					.map(|key| {
						let value = trie
							.get(&key)
							.map_err(|e| SubstrateStateMachineError::TrieError(format!("{e:?}")))?;
						Ok::<_, SubstrateStateMachineError>((key, value))
					})
					.collect::<Result<BTreeMap<_, _>, _>>()?
			},
		};
```

**File:** modules/ismp/state-machines/evm/src/lib.rs (L149-198)
```rust
pub fn verify_state_proof<H: Keccak256 + Send + Sync>(
	keys: Vec<Vec<u8>>,
	root: H256,
	proof: &Proof,
	ismp_address: H160,
) -> Result<BTreeMap<Vec<u8>, Option<Vec<u8>>>, Error> {
	// Reject repeats before doing any work at all. They are already an error — repeats collapse
	// in the map returned below, so the caller's key-count check fails — but reaching that
	// check means every repeat has been verified first, and for account queries that is a
	// clone of the whole contract proof each time.
	let mut seen_keys = BTreeSet::new();
	for key in &keys {
		if !seen_keys.insert(key.as_slice()) {
			return Err(EvmStateMachineError::DuplicateKey.into());
		}
	}

	let evm_state_proof = decode_evm_state_proof(proof)?;
	let mut map = BTreeMap::new();
	let mut contract_to_keys = BTreeMap::new();
	let mut contract_account_queries = Vec::new();

	// Group keys by the contract address they belong to
	for key in keys {
		// For keys that are 52 bytes we expect the first 20 bytes to be the contract address and
		// the last 32 bytes the slot hash.
		// For keys that are 20 bytes we expect that to the
		// contract or account address.
		// For keys that are 32 bytes we expect that to be a slothash in
		// the Ismp EVM host
		let contract_address = if key.len() == 52 {
			H160::from_slice(&key[..20])
		} else if key.len() == 32 {
			ismp_address
		} else if key.len() == 20 {
			contract_account_queries.push(H160::from_slice(&key));
			continue;
		} else {
			return Err(EvmStateMachineError::UnsupportedKeyLength.into());
		};
		let entry = contract_to_keys.entry(contract_address.0.to_vec()).or_insert(vec![]);

		let slot_hash = if key.len() == 52 {
			H::keccak256(&key[20..]).0.to_vec()
		} else {
			H::keccak256(&key).0.to_vec()
		};

		entry.push((key, slot_hash));
	}
```
