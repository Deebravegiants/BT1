### Title
Unbounded, fixed-weight `handle_unsigned` message batches allow fee-less compute-DoS of the ISMP mempool/validator - ([File: modules/pallets/ismp/src/lib.rs])

### Summary
`pallet_ismp::Call::handle_unsigned` and `pallet_state_coprocessor::Call::handle_unsigned` are unsigned, permissionless entry points (`ensure_none(origin)`) that accept an attacker-controlled `Vec<Message>` / `Vec<GetRequest>` payload of essentially unbounded cardinality, yet are declared with a fixed, size-independent extrinsic weight. Both pallets' `ValidateUnsigned::validate_unsigned` implementations *fully execute* the expensive message-processing logic (hashing, dedup, per-item checks) directly during transaction-pool validation, before any fee is charged and before the extrinsic is even included in a block. This mirrors the reported CVE-2026-3116 pattern: an unauthenticated/unprivileged submitter can send an oversized request that is processed with disproportionate compute cost relative to its declared/charged weight, causing service disruption (mempool validation DoS / block-time exhaustion).

### Finding Description
`pallet_ismp::Call::handle_unsigned` is declared with a static weight that does not scale with the number or size of `messages`: [1](#0-0) [2](#0-1) 

The unsigned mempool validation path (`validate_unsigned`) does not merely check a signature or cheap invariant — it calls `Self::execute(messages.clone())`, which runs the *entire* message-handling pipeline (per-message `handle_incoming_message`, hashing, event collection) for every message in the batch, for every node that receives the gossiped transaction, before the transaction is even accepted into a block: [3](#0-2) 

`Pallet::<T>::execute` iterates the full `messages` vector doing per-message hashing/verification work with no upper bound on `messages.len()` other than the runtime's generic max-extrinsic/block-length limit (which bounds byte size, not item count if entries are made small/cheap): [4](#0-3) 

The analogous `pallet_state_coprocessor::Call::handle_unsigned` has the same shape: a fixed `DbWeight::get().reads_writes(1, 2)` weight independent of `requests.len()` inside `GetRequestsWithProof`, and its `validate_unsigned` also runs the full `handle_get_requests` (dedup, per-request timeout/source/dest checks, hash computation) before any proof is verified successfully: [5](#0-4) [6](#0-5) 

Both handlers are reachable by any unprivileged relayer/dispatcher submitting an unsigned extrinsic (no stake, no fee, no prior authorization) — exactly the "unprivileged message dispatcher/relayer" class in scope. Unlike `pallet_call_decompressor`, which was explicitly hardened against an analogous "claim vs. actual size" zstd-bomb (see the size gate and accompanying comments), `pallet_ismp::handle_unsigned` and `pallet_state_coprocessor::handle_unsigned` have no equivalent cap on the number of batched messages/requests before the expensive per-item work runs: [7](#0-6) 

### Impact Explanation
Because `validate_unsigned` executes the full handling logic (not just a cheap pre-check) for a fee-less, unsigned call, and the declared weight used for block-inclusion/fee accounting does not scale with the actual batch size, an attacker can:
1. Submit a single "unsigned" extrinsic carrying a large `Vec<Message>` (or `Vec<GetRequest>`) sized just under the block/extrinsic byte limit but with many small entries, forcing every node's transaction pool (and, if accepted, every validator producing/importing the block) to perform disproportionate hashing/verification work relative to the trivial declared weight.
2. Because this happens at `validate_unsigned` time — i.e., during mempool gossip/validation, before the transaction lands on-chain — repeated submission (and re-submission after rejection) can degrade validator/node availability, a route-availability/DoS impact on Hyperbridge's message-delivery path, consistent with the "unauthenticated attacker... cause service disruption" class in the reported CVE.

### Likelihood Explanation
High reachability: `ensure_none(origin)` makes this call available to anyone able to submit an unsigned extrinsic to any node's mempool; no economic stake or prior registration is required, and the vulnerable code path (`validate_unsigned`) runs before any fee is charged.

### Recommendation
- Bound `messages.len()` (and per-message inner vector sizes such as `RequestMessage.requests`, `GetRequestsWithProof.requests`, `GetRequest.keys`) with an explicit `BoundedVec`/`MaxMessages`-style cap enforced at decode time (as already done for `BeefyConsensusProofs::submit_proof`'s `BoundedVec<u8, MaxProofSize>`).
- Make the declared extrinsic weight for `handle_unsigned` scale with the actual batch size (message count/keys count) rather than a fixed constant, so weight accounting reflects the real compute cost.
- In `validate_unsigned`, perform a cheap, size/format-only pre-check (e.g., message count bound, structural sanity) before invoking the full `execute`/`handle_get_requests` pipeline, mirroring the "gate lives at every caller's single choke point, before any expansion" pattern used in `pallet_call_decompressor::decompress`.

### Proof of Concept
1. Craft an unsigned extrinsic calling `Ismp::handle_unsigned` with `messages: Vec<Message>` containing a very large number of `Message::Request(RequestMessage { requests: vec![post], ... })` entries (each request minimally sized so the total extrinsic stays under the block/extrinsic byte limit).
2. Submit via `Extrinsic::new("Ismp", "handle_unsigned", messages.encode())`/`send_unsigned_extrinsic`, as exercised in the existing test harness (`parachain/simtests/src/pallet_ismp.rs`) but scaled up in message count. [8](#0-7) 
3. Observe that `validate_unsigned` (line 614-626 of `modules/pallets/ismp/src/lib.rs`) fully executes `Self::execute(messages.clone())` for the entire batch during mempool validation, well before the fixed `weight()` of `300_000_000` (line 727-730) is charged or the extrinsic is included in a block — demonstrating the size/computation-vs-declared-weight mismatch that enables the DoS.

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

**File:** modules/pallets/state-coprocessor/src/impls.rs (L62-120)
```rust
	pub fn handle_get_requests(
		GetRequestsWithProof { requests, source, response, address }: GetRequestsWithProof,
	) -> Result<(), Error> {
		// 1. Verify source proofs
		// 2. Extract fees
		// 3. Verify response proof
		// 4. insert GetResponse into mmr and request receipts
		// 5. emit Response events
		let host = <<T as Config>::IsmpHost>::default();

		// Reject duplicate requests within the batch.
		let wrapped: Vec<Request> = requests.iter().cloned().map(Request::Get).collect();
		dedup_requests::<<T as Config>::IsmpHost>(&wrapped)?;

		for req in requests.iter() {
			let full = Request::Get(req.clone());

			// Get requests time out are relative to Hyperbridge
			if full.timed_out(host.timestamp()) {
				Err(Error::RequestTimeout { meta: full.clone().into() })?
			}

			// Source of the request must match the proof
			if full.source_chain() != source.height.id.state_id {
				Err(Error::RequestProofMetadataNotValid { meta: full.clone().into() })?
			}

			// Proof must come from the requested chain
			if full.dest_chain() != response.height.id.state_id {
				Err(Error::RequestProofMetadataNotValid { meta: full.clone().into() })?
			}

			// This request has already been responded to. Mirror `handlers/response.rs:61`:
			// dedup against `response_receipt`, which the dispatch path writes for this exact
			// GetRequest hash after producing a response. The receipt also binds the response
			// commitment, so external auditors can attest "Hyperbridge produced response X for
			// request Y" from one map.
			let probe = GetResponse { get: req.clone(), values: Default::default() };
			if host.response_receipt(&probe).is_some() {
				Err(Error::DuplicateResponse { meta: (&probe).into() })?
			}
		}

		// Ensure the proof height is equal to each retrieval height specified in the Get
		// requests
		if !requests.iter().all(|get| get.height == response.height.height) {
			Err(Error::InsufficientProofHeight)?
		}

		// Verify source proof
		let source_state_machine = validate_state_machine(&host, source.height)?;
		let state_root = host.state_machine_commitment(source.height)?;

		// Verify membership proof to ensure that requests where committed on source chain
		let commitments = requests
			.iter()
			.map(|get| hash_request::<<T as Config>::IsmpHost>(&Request::Get(get.clone())))
			.collect();
		source_state_machine.verify_membership(&host, commitments, state_root, &source)?;
```

**File:** modules/pallets/call-decompressor/src/lib.rs (L220-253)
```rust
	pub fn decompress(
		compressed_bytes: Vec<u8>,
		encoded_call_size: u32,
	) -> Result<Vec<u8>, DispatchError> {
		// Bound the claimed decompressed size against the configured maximum here,
		// at the single choke point every caller flows through. Previously this
		// gate lived only in `decompress_call` (the dispatch path); the unsigned
		// `validate_unsigned` mempool path called `decompress` directly with no
		// bound, so a fee-less attacker could claim `encoded_call_size = u32::MAX`
		// and have a tiny zstd "bomb" expanded to gigabytes during transaction-pool
		// validation, before any size check. Enforcing it here protects both paths.
		ensure!(encoded_call_size < T::MaxCallSize::get() * ONE_MB, Error::<T>::CallSizeOutOfBound);

		let mut decoder = StreamingDecoder::new(compressed_bytes.as_slice())
			.map_err(|_| Error::<T>::DecompressionFailed)?;

		let claimed = encoded_call_size as usize;
		let mut result = Vec::new();
		let mut chunk = vec![0u8; 4096];

		loop {
			let n = decoder.read(&mut chunk).map_err(|_| Error::<T>::DecompressionFailed)?;
			if n == 0 {
				break;
			}
			if result.len() + n > claimed {
				return Err(Error::<T>::DecompressionFailed.into());
			}
			result.extend_from_slice(&chunk[..n]);
		}

		ensure!(result.len() == claimed, Error::<T>::DecompressionFailed);

		Ok(result)
```

**File:** parachain/simtests/src/pallet_ismp.rs (L309-339)
```rust
	};

	let block = rpc_client
		.request::<CreatedBlock<H256>>("engine_createBlock", rpc_params![true, false])
		.await?;

	let finalized = rpc_client
		.request::<bool>("engine_finalizeBlock", rpc_params![block.hash])
		.await?;
	assert!(finalized);
	progress.wait_for_finalized_success().await?;

	// send after block inclusion, txpool should reject it
	{
		let tx = subxt::dynamic::tx(
			"Ismp",
			"handle_unsigned",
			vec![messages_to_value(vec![Message::Request(RequestMessage {
				requests: vec![post.clone().into()],
				proof: proof.clone(),
				signer: signature.encode(),
			})])],
		);
		let error = client.tx().create_unsigned(&tx)?.submit_and_watch().await.unwrap_err();
		let subxt::Error::Rpc(RpcError::ClientError(_err)) = error else {
			panic!("Unexpected error kind: {error:?}")
		};
	};

	Ok(())
}
```
