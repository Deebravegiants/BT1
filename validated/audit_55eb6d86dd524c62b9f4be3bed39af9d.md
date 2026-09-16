## Finding

Both `pallet-ismp`'s `handle_unsigned` extrinsic and `pallet-state-coprocessor`'s `handle_unsigned` extrinsic charge a **fixed, batch-size-independent weight** for processing a `Vec<Message>` (or `Vec<GetRequest>`) whose actual execution cost scales linearly (or worse, due to per-item trie proofs) with the number of requests packed into the call. This is the same bug class as the reported issue: an attacker floods a single call with many small items, and the O(n) work done inside exceeds the computation budget that was actually reserved for it, degrading or blocking legitimate message delivery.

### Title
Denial of Service via Unbounded Batch Size in `pallet_ismp::handle_unsigned` With Fixed Declared Weight - (File: `modules/pallets/ismp/src/lib.rs`)

### Summary
`handle_unsigned` accepts an arbitrary-length `Vec<Message>` and is annotated with a static weight `weight()` that always returns `Weight::from_parts(300_000_000, 0)`, independent of `messages.len()` or the number of `PostRequest`/`GetRequest` items nested inside each message. [1](#0-0) [2](#0-1) 

### Finding Description
Every message in the batch is executed by `Pallet::<T>::execute`, which iterates all messages, calling `handle_incoming_message` for each: [3](#0-2) 

For a `RequestMessage`, handling loops over every `PostRequest` in the message to (a) compute a commitment hash and run a full trie membership proof verification per commitment, and (b) dispatch to the destination module's `on_accept` callback: [4](#0-3) 

The membership check itself loops once per commitment key doing a full Merkle-trie lookup (`trie.get`), which is markedly more expensive than the reported bug's `vec_set::remove`: [5](#0-4) 

Crucially, `validate_unsigned` for `handle_unsigned` fully executes this same `Self::execute(messages.clone())` path during **transaction-pool validation**, before the extrinsic is even included in a block: [6](#0-5) 

Because the extrinsic's weight is a fixed constant rather than proportional to `messages.len()` (or the aggregate number of requests across all messages), `frame_system::CheckWeight`'s pre-dispatch/pool checks see this call as "cheap" no matter how many `PostRequest`/`GetRequest` entries it contains. The only real ceiling on batch size is the block/extrinsic length limit, which is typically large enough (megabytes) to admit thousands of minimal-size `PostRequest`s (empty `body`, zero `timeout_timestamp`, short `from`/`to`). This lets an attacker submit (and freely re-submit, since it's an unsigned/no-fee call by design, per `docs/content/developers/polkadot/pallet-ismp/overview.mdx` lines 256-258) a single call whose real CPU cost (trie proof verification × N + module dispatch × N) is far above the 300,000,000-weight budget the runtime believes it is charging.

The pallet-state-coprocessor `handle_unsigned` has the analogous structure: it fully executes `handle_get_requests` (module state-proof verification over an attacker-controlled `keys`/`requests` list) inside `validate_unsigned`, under a fixed `reads_writes(1, 2)` weight, again decoupled from the size of `message.requests`. [7](#0-6) 

### Impact Explanation
An attacker can craft a single `handle_unsigned` transaction with a very large number of minimal `PostRequest`/`GetRequest` entries (each requiring valid commitments/receipts and a correspondingly sized proof, which is attacker-controllable at low cost since the attacker also controls the source-side dispatch that creates those commitments). Because the declared weight does not scale with batch size:
- Every node's mempool validation (and every block producer's dispatch) spends CPU proportional to the true (unbounded) size of the batch while believing it is doing ~300M-weight worth of work.
- This can starve block production time and/or the actual computation budget for that block, causing legitimate `handle_unsigned` calls (real cross-chain message delivery) to be delayed, evicted from the pool, or fail to be included — a direct availability/DoS impact on message routing through Hyperbridge, matching "a route unable to deliver messages" in the validation criteria.

### Likelihood Explanation
The call is deliberately unsigned/free-to-submit by design so that anyone can relay ISMP messages without paying fees; that same permissionlessness makes it directly reachable by any actor submitting an extrinsic/RPC call — no privileged role, governance, or off-chain component is required. The prerequisite (obtaining valid low-cost proofs for many small requests) is within a single unprivileged actor's control since they can also be the source-chain dispatcher creating the corresponding commitments cheaply.

### Recommendation
Make the declared weight of `handle_unsigned` (and `pallet-state-coprocessor::handle_unsigned`) scale with the size of the batch (`messages.len()` and/or the total number of nested `PostRequest`/`GetRequest`/response items), and enforce an explicit maximum on the number of items processed per call (and ideally per proof) so that `validate_unsigned`'s eager full-execution cost is bounded and consistent with the weight actually charged and enforced by `CheckWeight`.

### Proof of Concept
1. Attacker (or attacker-controlled source chain) dispatches N minimal `PostRequest`s (empty `body`, `from`/`to` of length 1) so N commitments exist in `RequestCommitments`.
2. Attacker builds one `RequestMessage { requests: <N posts>, proof, signer }` inside `Message::Request`, wraps it in `Vec<Message>`, and submits it via `Ismp::handle_unsigned`.
3. `validate_unsigned` (run by every node on gossip) executes `Self::execute` which performs N trie membership lookups plus N `router.module_for_id`/`on_accept` calls — real cost grows with N — while the call is treated by `CheckWeight`/the transaction pool as costing the fixed `weight()` of 300,000,000, letting N be scaled up (bounded only by extrinsic/block length limits) to consume disproportionate validation/execution time relative to its accounted weight.

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

**File:** modules/ismp/core/src/handlers/request.rs (L86-133)
```rust
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

**File:** modules/ismp/state-machines/substrate/src/lib.rs (L145-172)
```rust
		let keys = self.commitment_state_trie_key(commitments);
		let read_value = |key: Vec<u8>, value: Option<Vec<u8>>| {
			value
				.ok_or_else(|| SubstrateStateMachineError::MissingMembershipValue(key.clone()))
				.map(|v| (key, v))
		};
		match hasher {
			HashAlgorithm::Keccak => {
				let db = StorageProof::new(storage_proof).into_memory_db::<Keccak256>();
				let trie = TrieDBBuilder::<LayoutV0<Keccak256>>::new(&db, &root).build();
				for key in keys {
					let value = trie
						.get(&key)
						.map_err(|e| SubstrateStateMachineError::TrieError(format!("{e:?}")))?;
					read_value(key, value)?;
				}
			},
			HashAlgorithm::Blake2 => {
				let db = StorageProof::new(storage_proof).into_memory_db::<BlakeTwo256>();
				let trie = TrieDBBuilder::<LayoutV0<BlakeTwo256>>::new(&db, &root).build();
				for key in keys {
					let value = trie
						.get(&key)
						.map_err(|e| SubstrateStateMachineError::TrieError(format!("{e:?}")))?;
					read_value(key, value)?;
				}
			},
		}
```

**File:** modules/pallets/state-coprocessor/src/lib.rs (L90-129)
```rust
		#[pallet::call_index(0)]
		#[pallet::weight(<T as frame_system::Config>::DbWeight::get().reads_writes(1, 2))]
		pub fn handle_unsigned(
			origin: OriginFor<T>,
			message: GetRequestsWithProof,
		) -> DispatchResult {
			ensure_none(origin)?;

			Self::handle_get_requests(message).map_err(|err| {
				log::error!(target: "ismp", "pallet-coprocessor: {:?}", err);
				Error::<T>::HandlingError
			})?;

			Ok(())
		}
	}

	#[pallet::validate_unsigned]
	impl<T: Config> ValidateUnsigned for Pallet<T>
	where
		T::AccountId: AsRef<[u8]>,
		<T as frame_system::Config>::AccountId: From<[u8; 32]>,
		<T as pallet_ismp::Config>::Balance: Into<u128>,
	{
		type Call = Call<T>;

		// empty pre-dispatch so we don't modify storage
		fn pre_dispatch(_call: &Self::Call) -> Result<(), TransactionValidityError> {
			Ok(())
		}

		fn validate_unsigned(_source: TransactionSource, call: &Self::Call) -> TransactionValidity {
			let Call::handle_unsigned { message } = call else {
				return Err(TransactionValidityError::Invalid(InvalidTransaction::Call));
			};

			if let Err(err) = Self::handle_get_requests(message.clone()) {
				log::error!(target: "ismp", "{:?}", err);
				return Err(TransactionValidityError::Invalid(InvalidTransaction::Call));
			}
```
