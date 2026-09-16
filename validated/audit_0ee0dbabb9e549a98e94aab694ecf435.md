### Title
Unbounded, unweighted `Vec` fields in free unsigned ISMP extrinsics allow CPU/memory exhaustion DoS - ([File: modules/pallets/ismp/src/lib.rs])

### Summary
`pallet-ismp::handle_unsigned` and `pallet-state-coprocessor::handle_unsigned` are unsigned (fee-free) extrinsics whose payloads (`messages: Vec<Message>`, each `RequestMessage.requests: Vec<PostRequest>`, `ResponseMessage.requests`, `GetRequestsWithProof.requests: Vec<GetRequest>`, and per-request `keys: Vec<Vec<u8>>`) are plain, unbounded `Vec`s. `ValidateUnsigned::validate_unsigned` for both pallets fully executes `Self::execute(messages)` / `Self::handle_get_requests(message)` — including proof verification and per-item hashing — before returning a fixed `priority: 100` and fixed `weight()`/DbWeight, with no per-item cap. This mirrors CVE-2023-30798: unlimited "parts" (here, messages/requests/keys) accepted and fully parsed/processed before any bound check, so an attacker with zero balance and no signature can force expensive work on every node validating the transaction.

### Finding Description
`handle_unsigned` in `modules/pallets/ismp/src/lib.rs` is declared `ensure_none(origin)` (unsigned, free) and takes `messages: Vec<Message>` with no bound: [1](#0-0) 

Its `ValidateUnsigned::validate_unsigned` calls `Self::execute(messages.clone())` directly — the *same* full execution path (proof verification, membership/non-membership checks, per-request hashing, dispatch to router callbacks) that later occurs at block-inclusion time — every time a node validates the transaction for admission into the pool (and again during propagation/re-validation), before assigning a fixed `priority: 100`: [2](#0-1) 

`Self::execute` itself maps over the entire `messages` vector unconditionally, invoking `handle_incoming_message` for each entry with no upper bound on `messages.len()`: [3](#0-2) 

Inside a single `Message::Request`, `RequestMessage.requests: Vec<PostRequest>` is likewise unbounded, and `handlers::request::handle` iterates and hashes every request to build the membership-proof commitment set before verification even starts: [4](#0-3) 

`RequestMessage` itself is defined with a plain `Vec` for `requests`, not a `BoundedVec`: [5](#0-4) 

The same pattern exists in `pallet-state-coprocessor`: its `handle_unsigned` is also `ensure_none`-gated and unbounded, and its `validate_unsigned` fully runs `Self::handle_get_requests(message.clone())` — which loops over `requests` performing `verify_state_proof` for every entry, including for every key in each request's `keys: Vec<Vec<u8>>` — before emitting a fixed `priority: 100`: [6](#0-5) [7](#0-6) 

No `MaxMessages`/`MaxRequests`/`MaxKeys` bound exists anywhere in the codebase (searched for `MaxMessages`, `max_messages` — no matches), and the `weight()` used for `handle_unsigned` in `modules/pallets/ismp/src/lib.rs:370` is a fixed constant, not scaled by `messages.len()` or nested `requests.len()`, so Substrate's weight-based fee/throttling mechanism does not account for the attacker-controlled batch size before `validate_unsigned` runs the real work.

### Impact Explanation
Because these calls are unsigned and free, and because `validate_unsigned` performs full cryptographic/hashing/state-proof work proportional to attacker-chosen `Vec` lengths *before* any bound is enforced, a single crafted extrinsic (or a flood of such extrinsics) can force disproportionate CPU and memory consumption on every node that validates it in its transaction pool — full nodes, collators, and relayer nodes alike — with no cost to the attacker (no fee, no valid proof required to trigger the work; the bulk of the cost is incurred attempting to parse/hash/verify before rejection). This can degrade or halt block production and transaction propagation network-wide, a resource-exhaustion/availability impact consistent with High severity DoS classes (CWE-400), directly analogous to the reported `python-multipart`/Starlette issue where unbounded parts caused OOM before any per-item limit was applied.

### Likelihood Explanation
High. The extrinsics are explicitly designed to be callable by anyone without a signature ("This allows users execute ISMP datagrams for free. Use with caution." — comment directly above the `ValidateUnsigned` impl), require no funds, and the vulnerable code path (`validate_unsigned` → `execute`/`handle_get_requests`) is on the hot path of every node's mempool validation. No specialized access or state is needed — just constructing a `Vec` with many entries (empty/garbage `PostRequest`/`GetRequest`/key values are sufficient to trigger the iteration/hash work; well-known SCALE-encoding size limits notwithstanding, achievable well within default block-length limits and easily rebroadcast for sustained pressure).

### Recommendation
Bound all attacker-controlled vector fields reachable pre-inclusion: convert `RequestMessage.requests`, `ResponseMessage.requests`, `Message`-batch `Vec<Message>` in `handle_unsigned`, and `GetRequestsWithProof.requests` / `GetRequest.keys` to `BoundedVec` with sane, configurable maxima (e.g., mirroring Starlette's `max_fields=1000`/`max_files=1000` defaults), and reject-early in `validate_unsigned` before any hashing/proof-verification work is performed. Additionally, scale `weight()` for `handle_unsigned` with the actual batch size so the runtime's weight metering reflects real work, and consider charging a minimal deposit or rate-limiting unsigned submissions per account/IP at the transaction-pool level.

### Proof of Concept
1. Construct `pallet_ismp::Call::handle_unsigned { messages: vec![Message::Request(RequestMessage { requests: vec![<large N of minimal/garbage PostRequest entries>], proof: <dummy/invalid Proof>, signer: vec![] }); M] }` with N and M chosen to maximize `requests.len()` within the extrinsic size limit.
2. Submit as an unsigned extrinsic via `subxt::dynamic::tx("Ismp", "handle_unsigned", ...)` as shown in the existing test harness pattern at `parachain/simtests/src/pallet_ismp.rs:282-290`.
3. Observe that `ValidateUnsigned::validate_unsigned` (modules/pallets/ismp/src/lib.rs:614) invokes `Self::execute` which iterates and hashes every `PostRequest` in every `Message` (modules/ismp/core/src/handlers/request.rs:86-98) before the (invalid) proof causes rejection — repeat submission at scale to measure CPU/memory amplification versus payload size, analogous to the unbounded multipart-field DoS in the referenced advisory.
4. Repeat against `pallet-state-coprocessor::handle_unsigned` with an oversized `GetRequestsWithProof.requests`/`keys` payload to trigger repeated `verify_state_proof` calls in `handle_get_requests` (modules/pallets/state-coprocessor/src/impls.rs:126-156) prior to rejection.

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

**File:** modules/pallets/ismp/src/lib.rs (L614-644)
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

			if let Some((state_machine_id, latest_height)) = events.iter().find_map(|event| {
				if let ismp::events::Event::StateMachineUpdated(state_machine_updated_event) = event
				{
					Some((
						state_machine_updated_event.state_machine_id.clone(),
						state_machine_updated_event.latest_height,
					))
				} else {
					None
				}
			}) {
				return Ok(ValidTransaction {
					priority: latest_height,
					requires: vec![],
					provides: vec![sp_io::hashing::keccak_256(&state_machine_id.encode()).to_vec()],
					longevity: 25,
					propagate: true,
				});
```

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

**File:** modules/ismp/core/src/handlers/request.rs (L86-98)
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
```

**File:** modules/ismp/core/src/messaging.rs (L116-120)
```rust
/// A request message holds a batch of requests to be dispatched from a source state machine
#[derive(
	Debug, Clone, Encode, DecodeWithMemTracking, Decode, scale_info::TypeInfo, PartialEq, Eq,
)]
pub struct RequestMessage {
```

**File:** modules/pallets/state-coprocessor/src/lib.rs (L90-149)
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

			let mut messages = message
				.requests
				.iter()
				.map(|get| hash_request::<<T as Config>::IsmpHost>(&Request::Get(get.clone())))
				.collect::<Vec<_>>();
			messages.sort();

			// this is so we can reject duplicate batches at the mempool level
			let msg_hash = sp_io::hashing::keccak_256(&messages.encode()).to_vec();

			Ok(ValidTransaction {
				priority: 100,
				requires: vec![],
				provides: vec![msg_hash],
				longevity: 25,
				propagate: true,
			})
		}
	}
```

**File:** modules/pallets/state-coprocessor/src/impls.rs (L126-156)
```rust
		// Insert GetResponses into mmr
		let mut responses = vec![];
		// Total payload bytes across this batch, used to mint reputation to
		// the relayer named in `address`. Each response contributes its
		// abi-encoded size — the same quantity the bandwidth gate charges —
		// so the mint stays proportional to the work paid for.
		let mut total_bytes: u32 = 0;
		for req in requests {
			let values: Vec<StorageValue> = dest_state_machine
				.verify_state_proof(&host, req.keys.clone(), state_root.state_root, &response)?
				.into_iter()
				.map(|(key, value)| StorageValue { key, value })
				.collect();

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

			responses.push(response);
		}

```
