Based on my investigation, I found a concrete analog on Hyperbridge's `pallet-state-coprocessor::handle_unsigned`/`validate_unsigned` path — this is a free, unsigned, unbounded-fan-out entrypoint reachable by any peer with no fee paid up front, directly analogous to `ws`'s "verify tiny fragments before accounting for their cost" bug class.

### Title
Unmetered, unbounded `GetRequestsWithProof.requests` array lets an unsigned submitter force expensive per-key state-proof verification before the bandwidth gate ever runs, enabling free memory/CPU exhaustion — ([File: modules/pallets/state-coprocessor/src/impls.rs])

### Summary
`pallet-state-coprocessor::handle_unsigned` is a `ensure_none` (free, unsigned) extrinsic [1](#0-0) , additionally executed once more inside `validate_unsigned` for every transaction that even reaches the pool [2](#0-1) . Its handler, `handle_get_requests`, iterates an attacker-controlled `Vec<GetRequest>` and calls `verify_state_proof` (full Merkle/trie key verification, allocating per-key `StorageValue`s) for *every* request **before** the per-request bandwidth gate charge is ever applied [3](#0-2) . The gate check happens only after verification completes, using the *result* size (`ismp::abi::encode_get_response(&response).len()`), not a pre-check size cap [4](#0-3) .

### Finding Description
The `ws` advisory describes a peer sending many minimally-sized fragments/chunks that are individually accepted and buffered/allocated as structural wrappers before the accumulated cost is checked against `maxPayload`. The analogous pattern here: `GetRequestsWithProof.requests: Vec<GetRequest>` has no length cap, and each `GetRequest.keys: Vec<Vec<u8>>` also has no cap on key count or key size [5](#0-4) . Since `handle_unsigned` is submitted with `ensure_none` (unsigned) and is re-executed at `validate_unsigned` time on every node in the pool, a submitter pays **no fee** to have the runtime run `verify_state_proof` over an arbitrarily large batch of GET requests, each with an arbitrarily large `keys` vector, and the bandwidth "gate" that is documented to be the sole cost-accounting mechanism (`type BandwidthGate ... charges max(sum(keys.len())+context.len(),32) bytes ... before any state proof work`, per the doc comment) is in fact only invoked *after* `verify_state_proof` runs per-request, not before [6](#0-5) [3](#0-2) . The doc comment's claimed invariant ("before any state proof work") is contradicted by the actual ordering in `impls.rs`, where `verify_state_proof` (line 135) runs strictly before `try_consume` (line 146). Each `validate_unsigned` call on every full/validator node in the network independently performs this same expensive verification work for every submission that reaches the transaction pool — multiplying the cost by the number of validating nodes.

### Impact Explanation
An unprivileged party can submit unsigned `StateCoprocessor::handle_unsigned` transactions with a large `requests` array (each `GetRequest` carrying many/large `keys`) and a source/response proof crafted to look plausible enough to reach the verification stage, forcing every node's transaction-pool validation and block-execution logic to allocate and process large amounts of proof/key data at zero cost — a network-wide, gas/fee-less resource-exhaustion vector against Hyperbridge validator nodes. This matches the CWE-400/CWE-770 "allocate structural wrappers disproportionate to declared cost" pattern in the `ws` advisory and is reachable directly from an unprivileged relayed message (a GET-request proof submission), one of the explicitly in-scope paths (pallet-ismp `handle_unsigned` / state membership proofs).

### Likelihood Explanation
High: no signature, no fee, no stake is required to submit the extrinsic; the attacker only needs a `GetRequestsWithProof` that passes the early cheap checks (timeouts, source/dest chain match, height match) before hitting the expensive `verify_state_proof` loop, and `validate_unsigned` performs this same expensive work on every node's mempool ingestion, so a single spammed submission is amplified across the entire validator set.

### Recommendation
Move the `BandwidthGate::try_consume` check (or an equivalent, cheap, pre-verification size/key-count bound) to run **before** `verify_state_proof` is invoked per request, using the declared `keys` length/size (as the doc comment already claims is the design), and additionally enforce a hard cap on `requests.len()` and per-request `keys.len()`/key size in `GetRequestsWithProof` so that unsigned/unfee'd submissions cannot trigger unbounded verification work.

### Proof of Concept
1. Construct a `GetRequestsWithProof` with `requests` containing many `GetRequest`s, each with a large `keys: Vec<Vec<u8>>` (e.g., thousands of near-empty keys), all sharing matching `source`/`dest`/`height` fields to pass the early metadata checks in `handle_get_requests` [7](#0-6) .
2. Submit as `StateCoprocessor::handle_unsigned(message)` via an unsigned extrinsic (as the tesseract relayer client does at `tesseract/messaging/substrate/src/calls.rs:321-331`) — no signer, no fee.
3. Every node in the network runs `validate_unsigned`, which calls `handle_get_requests` in full, including the `verify_state_proof` loop over all requests/keys, before any bandwidth/cost check gates the work [2](#0-1) .
4. Repeat with a stream of such submissions to induce sustained memory/CPU load across the validator set at zero cost to the attacker.

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

**File:** modules/pallets/state-coprocessor/src/impls.rs (L76-107)
```rust
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
```

**File:** modules/pallets/state-coprocessor/src/impls.rs (L133-152)
```rust
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

**File:** modules/ismp/core/src/router.rs (L101-137)
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
	/// Height at which to read the state machine.
	pub height: u64,
	/// Some application-specific metadata relating to this request
	#[serde(with = "serde_hex_utils::as_hex")]
	pub context: Vec<u8>,
	/// Host timestamp at which this request expires in seconds
	#[serde(rename = "timeoutTimestamp")]
	pub timeout_timestamp: u64,
}
```
