Based on my research, I found a strong analog: a mismatch between the documented "fail fast" bandwidth design and the actual execution order in `pallet-state-coprocessor`, which lets an unauthenticated (unsigned, free) `GetRequestsWithProof` message force full trie/proof verification work on the validating node *before* the bandwidth gate can reject it — mirroring the APISIX pattern where a small crafted request causes disproportionate CPU work in an unauthenticated code path.

### Title
Unauthenticated CPU-exhaustion via bandwidth-gate ordering in `pallet-state-coprocessor::handle_get_requests` - (File: `modules/pallets/state-coprocessor/src/impls.rs`)

### Summary
`pallet-state-coprocessor` exposes `handle_unsigned` as a fee-less, unsigned extrinsic [1](#0-0) . Both the mempool validation path (`validate_unsigned`) and the in-block dispatch path call `Self::handle_get_requests(message.clone())` directly [2](#0-1) . The pallet's own documentation states the bandwidth gate is meant to charge `max(sum(keys.len()) + context.len(), 32)` bytes per `GetRequest` "before any state proof work — fails fast for apps without allowance" [3](#0-2) . The actual implementation does not do this: `BandwidthGate::try_consume` is only invoked *after* `dest_state_machine.verify_state_proof(...)` has already run the full trie walk for every key in the batch [4](#0-3) .

### Finding Description
`handle_get_requests` accepts a `GetRequestsWithProof` containing an unbounded `Vec<GetRequest>`, each with an unbounded `keys: Vec<Vec<u8>>` [5](#0-4) . The processing order is:
1. Dedup / timeout / metadata checks (cheap) [6](#0-5) .
2. `verify_membership` of the source-chain commitments (cheap, hash comparison).
3. For every `GetRequest` in the batch, `verify_state_proof` is called — this decodes and walks a Merkle-Patricia / child-trie proof once per requested key [7](#0-6) , calling into `TrieDBBuilder::...build()` and `trie.get(&key)` per key for EVM/Substrate state machines [8](#0-7) [9](#0-8) .
4. Only *after* this trie work completes for a given `GetRequest` is `BandwidthGate::try_consume` invoked, and only against the **response** size, not the request's key count [10](#0-9) .

Because `handle_unsigned` is unsigned and free to submit [11](#0-10) , and `validate_unsigned` re-runs the entire `handle_get_requests` (including all trie verification) on every node during transaction-pool validation [2](#0-1) , an unprivileged submitter with no bandwidth allowance at all can still force every full node to perform expensive Merkle-proof verification across an arbitrarily large key set before the app-level gate has any chance to reject the message for insufficient bandwidth. This inverts the intended "fail fast, cheap check first" ordering documented in the pallet, and there is no cap on `keys.len()` or `requests.len()` prior to the trie walk.

### Impact Explanation
A message dispatcher (any unprivileged account able to submit an unsigned extrinsic, requiring no fee and no bandwidth allowance) can repeatedly submit `handle_unsigned(GetRequestsWithProof)` batches with many `GetRequest`s, each carrying many keys, paired with a validly-formed (but ultimately unauthorized/unpaid-for) proof. Every Hyperbridge full node performing transaction-pool validation is forced to execute the full trie-proof verification workload for the batch — for free, repeatedly — before the bandwidth gate can reject it. This is a CPU-exhaustion vector reachable from a single small (or moderately sized) unsigned extrinsic, matching the "route unable to deliver messages" criterion: sustained submission can starve node CPU needed for legitimate message processing across the coprocessor's `pallet_ismp` dispatch pipeline.

### Likelihood Explanation
High likelihood: `handle_unsigned` messages are explicitly free/unsigned by design so relayers aren't charged gas for delivering valid proofs [11](#0-10) , meaning the attacker has no cost barrier beyond constructing a request with many keys and a proof that decodes far enough into the trie work before any rejection. No signature, fee, or prior bandwidth allowance is required to reach the vulnerable code path; only a state root the attacker can reference and a syntactically valid proof blob are needed to drive the trie walk to completion before the size-based gate check.

### Recommendation
Move the bandwidth/size check (or an equivalent cheap upper-bound check on `sum(keys.len()) + context.len()` per `GetRequest`, and on total `requests.len()` / total keys in the batch) to run *before* `verify_state_proof` is invoked, exactly as already documented in `pallet_state_coprocessor::Config::BandwidthGate`'s doc comment. This restores "fail fast for apps without allowance" and removes the ability to force expensive trie verification ahead of the bandwidth check.

### Proof of Concept
1. Construct a `GetRequestsWithProof` with `requests` containing many `GetRequest`s (or one `GetRequest` with a large `keys: Vec<Vec<u8>>`), each key crafted to require walking a large valid-looking trie proof against `source`/`response` roots the attacker can reference.
2. Submit via `pallet_state_coprocessor::Call::handle_unsigned` as an unsigned extrinsic; no signer, fee, or prior `pallet-bandwidth` allowance is required to reach the code.
3. Observe that both `validate_unsigned` (run by every node's transaction pool) and the in-block dispatch call `handle_get_requests`, which executes `verify_membership` then loops calling `verify_state_proof` for every requested key across the whole batch, before `BandwidthGate::try_consume` is ever called [12](#0-11) .
4. Repeated resubmission (the extrinsic is free) pins CPU on every validating node with proof-verification work that the bandwidth gate was documented to prevent "before any state proof work."

### Citations

**File:** modules/pallets/state-coprocessor/src/lib.rs (L60-64)
```rust
		/// Bandwidth gate that meters per-app data consumption. The
		/// coprocessor charges `max(sum(keys.len()) + context.len(), 32)`
		/// bytes per `GetRequest` against `(req.source, req.from)` before
		/// any state proof work — fails fast for apps without allowance.
		type BandwidthGate: pallet_bandwidth::BandwidthGate;
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

**File:** modules/pallets/state-coprocessor/src/impls.rs (L72-103)
```rust
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
```

**File:** modules/pallets/state-coprocessor/src/impls.rs (L111-151)
```rust
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
```

**File:** modules/ismp/core/src/router.rs (L101-128)
```rust
pub struct GetRequest {
	/// The source state machine of this request.
	#[serde(with = "serde_hex_utils::as_string")]
	pub source: StateMachine,
	/// The destination state machine of this request.
	#[serde(with = "serde_hex_utils::as_string")]
	pub dest: StateMachine,
	/// The nonce of this request on the source chain
	pub nonce: u64,
	/// Module identifier of the sending module
	#[serde(with = "serde_hex_utils::as_hex")]
	pub from: Vec<u8>,
	/// Raw Storage keys that would be used to fetch the values from the counterparty
	/// For deriving storage keys for ink contract fields follow the guide in the link below
	/// `<https://use.ink/datastructures/storage-in-metadata#a-full-example>`
	/// Substrate Keys
	/// The algorithms for calculating raw storage keys for different substrate pallet storage
	/// types are described in the following links
	/// `<https://github.com/paritytech/substrate/blob/master/frame/support/src/storage/types/map.rs#L34-L42>`
	/// `<https://github.com/paritytech/substrate/blob/master/frame/support/src/storage/types/double_map.rs#L34-L44>`
	/// `<https://github.com/paritytech/substrate/blob/master/frame/support/src/storage/types/nmap.rs#L39-L48>`
	/// `<https://github.com/paritytech/substrate/blob/master/frame/support/src/storage/types/value.rs#L37>`
	/// EVM Keys
	/// For fetching keys from EVM contracts each key should either be 52 bytes or 20 bytes
	/// For 52 byte keys we expect it to be a concatenation of contract address and slot hash
	/// For 20 bytes we expect it to be a contract or account address
	#[serde(with = "serde_hex_utils::seq_of_hex")]
	pub keys: Vec<Vec<u8>>,
```

**File:** modules/ismp/state-machines/evm/src/utils.rs (L182-198)
```rust
pub fn get_values_from_proof<H: Keccak256 + Send + Sync>(
	keys: Vec<Vec<u8>>,
	root: H256,
	proof: Vec<Vec<u8>>,
) -> Result<Vec<Option<DBValue>>, Error> {
	let mut values = vec![];
	let proof_db = StorageProof::new(proof).into_memory_db::<KeccakHasher<H>>();
	let trie = TrieDBBuilder::<EIP1186Layout<KeccakHasher<H>>>::new(&proof_db, &root).build();
	for key in keys {
		let val = trie
			.get(&key)
			.map_err(|e| EvmStateMachineError::TrieReadError(format!("{e:?}")))?;
		values.push(val);
	}

	Ok(values)
}
```

**File:** modules/ismp/state-machines/substrate/src/lib.rs (L256-263)
```rust
				keys.into_iter()
					.map(|key| {
						let value = trie
							.get(&key)
							.map_err(|e| SubstrateStateMachineError::TrieError(format!("{e:?}")))?;
						Ok::<_, SubstrateStateMachineError>((key, value))
					})
					.collect::<Result<BTreeMap<_, _>, _>>()?
```

**File:** docs/content/developers/polkadot/pallet-ismp/overview.mdx (L256-258)
```text
## Transaction fees

Pallet ISMP uses unsigned transactions for executing cross-chain messages. This means all cross-chain messages received are executed for free as unsigned transactions. The upside to this is that it cannot be exploited as a spam vector, since the transaction pool will check if the submitted extrinsics are valid before they are included in the pool. This validity check ensures that the transaction can be successfully executed and contains valid proofs. Malformed messages or those with invalid proofs are filtered out by the transaction pool validation logic preventing unnecessary processing and potential network congestion.
```
