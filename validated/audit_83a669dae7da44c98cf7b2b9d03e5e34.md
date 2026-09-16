The strongest analog to the NFTX `distribute` unbounded-loop bug is `pallet_ismp::Pallet::handle_unsigned` in `modules/pallets/ismp/src/lib.rs`, which iterates over a caller-supplied `Vec<Message>` of unbounded length but is billed at a fixed, message-count-independent weight.

### Title
Unbounded message-array iteration in `pallet_ismp::handle_unsigned` with fixed weight billing enables free block-weight exhaustion - (File: `modules/pallets/ismp/src/lib.rs`)

### Summary
`handle_unsigned` is a permissionless, fee-less (unsigned) extrinsic that accepts an arbitrary-length `Vec<Message>` and executes every message in the batch (`Self::execute(messages.clone())`), yet its declared weight is a hard-coded constant (`weight()` → `Weight::from_parts(300_000_000, 0)`) regardless of how many messages are in the batch or how expensive their individual proof verifications are.

### Finding Description
`Pallet::execute` in `modules/pallets/ismp/src/impls.rs` maps every message in the submitted vector through `handle_incoming_message`, which performs full proof verification (state/consensus proofs, MMR/trie membership checks) for each entry: [1](#0-0) 

The dispatchable that invokes this is declared with a static weight function instead of one that scales with `messages.len()`: [2](#0-1) [3](#0-2) 

Because the call is unsigned (`ensure_none(origin)`), there is no transaction fee proportional to work done, and `ValidateUnsigned::validate_unsigned` also independently runs `Self::execute(messages.clone())` on every message in the pool-validation path, before the extrinsic is even included in a block: [4](#0-3) 

Since the on-chain weight charged does not grow with `messages.len()`, `CheckWeight`/block-weight accounting cannot bound the actual computation an attacker can force onto a single block: a submitter with valid proofs (or enough proofs to pass validation) can pack an arbitrarily large `messages` vector into one `handle_unsigned` call, causing real per-message work (hashing, trie/MMR proof verification for every request/response, consensus verification per message) far in excess of the weight reserved, while paying zero fees.

### Impact Explanation
This can push actual block execution time well past the weight the runtime believes it consumed, which can cause block production/import to overrun, threaten block time guarantees, and be used to congest/DoS the chain's ability to process legitimate ISMP messages — directly impacting the "route unable to deliver messages" criterion, since a saturated or slow-producing chain delays or blocks all cross-chain message delivery through `pallet-ismp`.

### Likelihood Explanation
The call is fully permissionless (`ensure_none` unsigned origin) and reachable by anyone submitting a properly-formed extrinsic; the docs themselves describe `handle_unsigned` as executing "the provided batch of ISMP messages for free" with no built-in limit stated on batch size in this pallet path, unlike other places in the codebase that impose explicit caps (e.g. `MAX_STATE_MACHINE_COMMITMENTS`, `MAX_COMMITMENT_EVICTIONS_PER_INSERT`) precisely to bound iteration cost: [5](#0-4) 

### Recommendation
Bound `messages: Vec<Message>` with a `BoundedVec`/explicit maximum length, and make `#[pallet::weight(...)]` a function of `messages.len()` (and/or the proof sizes) rather than a fixed constant, so both fee-free execution cost and block-weight accounting scale with the actual work performed.

### Proof of Concept
1. Construct a `handle_unsigned` call with `messages` containing far more entries than any single normal batch (e.g. thousands of valid `Message::Request`/`Message::Response` entries with valid but minimal proofs, as already demonstrated feasible for 1000 entries in the pallet's own test fixture `should_decompress_and_execute_pallet_ismp_post_request_calls_correctly`): [6](#0-5) 
2. Submit the unsigned extrinsic; `validate_unsigned` and later `handle_unsigned`'s dispatch both call `Self::execute(messages.clone())`, doing full O(n) verification work.
3. Observe that the weight charged/reserved for the call remains the fixed `weight()` constant regardless of `n`, letting the actual computation scale unboundedly while accounted weight does not.

### Citations

**File:** modules/pallets/ismp/src/impls.rs (L40-51)
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
```

**File:** modules/pallets/ismp/src/lib.rs (L93-100)
```rust
	pub const MAX_STATE_MACHINE_COMMITMENTS: u32 = 10_240;

	/// Upper bound on evictions performed by a single
	/// [`Pallet::insert_bounded_state_commitment`] call. At steady state each
	/// insertion evicts exactly one entry; the headroom lets the queue drain
	/// gradually after a per-chain cap is lowered without unbounded work in
	/// one call.
	pub const MAX_COMMITMENT_EVICTIONS_PER_INSERT: u32 = 4;
```

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

**File:** modules/pallets/testsuite/src/tests/pallet_call_decompressor.rs (L148-188)
```rust
#[test]
fn should_decompress_and_execute_pallet_ismp_post_request_calls_correctly() {
	let mut ext = new_test_ext();
	ext.execute_with(|| {
		let host = Ismp::default();
		let requests = (0..1000)
			.into_iter()
			.map(|i| {
				let post = ismp::router::PostRequest {
					source: host.host_state_machine(),
					dest: StateMachine::Evm(1),
					nonce: i,
					from: H256::random().0.to_vec(),
					to: H256::random().0.to_vec(),
					timeout_timestamp: Duration::from_millis(Timestamp::now()).as_secs() +
						2_000_000_000,
					body: H512::random().0.to_vec(),
				};
				post
			})
			.collect::<Vec<_>>();

		let msg = RequestMessage {
			requests,
			proof: Proof {
				height: StateMachineHeight {
					id: StateMachineId {
						state_id: StateMachine::Evm(1),
						consensus_state_id: MOCK_CONSENSUS_STATE_ID,
					},
					height: 3,
				},
				proof: H512::random().0.to_vec(),
			},
			signer: H512::random().0.to_vec(),
		};

		let call = RuntimeCall::Ismp(pallet_ismp::Call::handle_unsigned {
			messages: vec![Message::Request(msg)],
		})
		.encode();
```
