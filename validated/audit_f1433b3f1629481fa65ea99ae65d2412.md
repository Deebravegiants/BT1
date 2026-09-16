Found it — a concrete analog to the EXIF-stripping DOS bug class exists in `pallet-state-coprocessor::handle_get_requests`. The bandwidth gate charge in `impls.rs` is only applied **after** the expensive `verify_state_proof` work is done per request, and the `GetRequest.keys` field carried in the unsigned `handle_unsigned` extrinsic has no bound on its length or count before that verification runs.

### Title
Unbounded per-key state-proof verification before bandwidth metering allows free CPU-exhaustion DoS via `handle_unsigned` GetResponse messages - (File: modules/pallets/state-coprocessor/src/impls.rs)

### Summary
`pallet_state_coprocessor::handle_get_requests` runs `dest_state_machine.verify_state_proof(&host, req.keys.clone(), state_root.state_root, &response)` for every `GetRequest` in a `ResponseMessage` batch *before* charging the app's bandwidth allowance for the resulting bytes [1](#0-0) . This mirrors the BIT-2021-39907 bug class: expensive, attacker-triggerable per-item processing (there: EXIF stripping; here: trie/storage-proof membership verification per key) happens unconditionally before any cost/authorization gate is applied.

### Finding Description
The call path is reachable by any unsigned relayer through `pallet_state_coprocessor::Call::handle_unsigned` [2](#0-1) , which is also exercised directly in `validate_unsigned` during mempool validation [3](#0-2)  — i.e. proof verification work is paid for by every node validating the transaction, not just the one that includes it.

`GetRequestsWithProof.requests` is an unbounded `Vec<GetRequest>`, and each `GetRequest.keys` is itself an unbounded `Vec<Vec<u8>>` (the `pallet_call_decompressor` docs even acknowledge Get requests carry "a nested vector of keys" requiring extra decode depth) [4](#0-3) . In `handle_get_requests`, the loop over `requests` calls `verify_state_proof` for each request's full key set, and only *after* that expensive cryptographic verification computes the byte size and calls `BandwidthGate::try_consume` [5](#0-4) . The code comment even documents that this ordering is intentional ("Charged after proof verification so the value sizes are final") without bounding the number of keys/requests that can be submitted per batch before that charge occurs.

Because `handle_unsigned` is an unsigned extrinsic (no fee, no origin-based rate limiting), and the gate rejection (`Insufficient`/`NoAllowance`) only fires after verification completes, an attacker with no bandwidth allowance at all — or with a small one — can submit a `ResponseMessage`/`GetRequestsWithProof` batch with a very large number of requests and/or keys per request, forcing every validating node to perform the full membership-proof verification workload for free before the batch is ultimately rejected by the bandwidth gate or fails for other reasons.

### Impact Explanation
This is a DoS on validator/collator CPU analogous to the GitLab EXIF-stripping CPU exhaustion: unauthorized, unbounded expensive computation triggered by an unprivileged submitter, executed during transaction-pool validation (`validate_unsigned`) as well as block execution, before any cost is charged. Sustained abuse can degrade block production and mempool throughput for the Hyperbridge coprocessor pipeline, a core routing path for GetResponse delivery.

### Likelihood Explanation
Reachable by any relayer/message submitter with no signature or bandwidth prerequisite, since `handle_unsigned` accepts fee-less unsigned transactions and the mempool itself performs the expensive verification during `validate_unsigned`. No privileged role is required, only network access to submit the extrinsic.

### Recommendation
Bound the total work performed before the bandwidth (or any other) gate check: cap the number of `GetRequest`s per `GetRequestsWithProof` batch and the number of `keys` per `GetRequest`, and/or move a cheap size-based bandwidth pre-check (e.g. against `sum(keys.len())` before verification, as already hinted at in the `BandwidthGate` doc comment "charges `max(sum(keys.len()) + context.len(), 32)` bytes ... before any state proof work" for the dispatch path) so the ledger is checked before, not only after, `verify_state_proof` runs for GetResponse batches in `handle_get_requests`.

### Proof of Concept
1. Submit an unsigned `StateCoprocessor::handle_unsigned` extrinsic with a `GetRequestsWithProof` whose `requests` vector contains many `GetRequest`s, each with a large `keys` vector, and a source/response `Proof` chosen to pass the early metadata checks.
2. Observe that `verify_membership`/`verify_state_proof` (trie walking, hashing per key) executes fully for every key in every request before `BandwidthGate::try_consume` is ever invoked [6](#0-5) .
3. Because this occurs inside `validate_unsigned` for every node validating the transaction pool entry, repeated submission from an account with zero bandwidth allowance still consumes full verification CPU cycles across the network before ultimately being rejected.

### Citations

**File:** modules/pallets/state-coprocessor/src/impls.rs (L46-55)
```rust
pub struct GetRequestsWithProof {
	/// The associated Get requests
	pub requests: Vec<GetRequest>,
	/// Proof of these requests on the source chain
	pub source: Proof,
	/// State proof of the requested values in the Get requests.
	pub response: Proof,
	/// Address that should be credited with fees
	pub address: Vec<u8>,
}
```

**File:** modules/pallets/state-coprocessor/src/impls.rs (L105-152)
```rust
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

		// Verify response proof
		let dest_state_machine = validate_state_machine(&host, response.height)?;
		let state_root = host.state_machine_commitment(response.height)?;

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
```

**File:** modules/pallets/state-coprocessor/src/lib.rs (L90-104)
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
```

**File:** modules/pallets/state-coprocessor/src/lib.rs (L121-129)
```rust
		fn validate_unsigned(_source: TransactionSource, call: &Self::Call) -> TransactionValidity {
			let Call::handle_unsigned { message } = call else {
				return Err(TransactionValidityError::Invalid(InvalidTransaction::Call));
			};

			if let Err(err) = Self::handle_get_requests(message.clone()) {
				log::error!(target: "ismp", "{:?}", err);
				return Err(TransactionValidityError::Invalid(InvalidTransaction::Call));
			}
```
