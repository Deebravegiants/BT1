Found the analog. `pallet_ismp::Pallet::validate_unsigned` in `modules/pallets/ismp/src/lib.rs` runs `Self::execute(messages.clone())` on **every** unsigned `handle_unsigned` submission that hits the transaction pool — before the extrinsic is ever included in a block, and before any fee is charged (this is explicitly the free, unsigned, fee-less path). `execute()` runs the full per-message handler (`handlers::request::handle` / `handlers::response::handle`), which does dedup, receipt/timeout checks, and full state-machine proof verification (Merkle-Patricia trie walks, MMR verification, etc.) for **every request in the batch**, with no cap on `messages: Vec<Message>` or on `RequestMessage.requests: Vec<PostRequest>` / `ResponseMessage.requests: Vec<GetRequest>`. [1](#0-0) [2](#0-1) [3](#0-2) 

### Title
Unbounded item count in `pallet-ismp`'s unsigned `handle_unsigned` batch is fully re-verified during `validate_unsigned` mempool checks, enabling free, unauthenticated CPU-exhaustion DoS - (File: `modules/pallets/ismp/src/lib.rs`)

### Summary
`ValidateUnsigned::validate_unsigned` for `pallet_ismp::Call::handle_unsigned` calls `Self::execute(messages.clone())`, which fully runs the request/response handlers — including dedup, receipt lookups, and full membership-proof verification against the state-machine trie/MMR — for every entry in the caller-supplied `Vec<Message>` / `Vec<PostRequest>` / `Vec<GetRequest>`. There is no `Vec` length cap enforced before this work executes, and because the call is unsigned (fee-less by design, per the pallet's own documentation), this verification work runs for free on every node's transaction pool for every gossiped candidate transaction, mirroring the dd-trace-rb baggage bug's core defect: unbounded per-item work performed on the inbound/extract path with no item-count limit.

### Finding Description
`pallet_ismp` intentionally makes `handle_unsigned` fee-less to let relayers deliver proofs for free [4](#0-3) . This safety design assumes the "validity check" performed by the transaction pool bounds the cost of rejecting bad submissions, but the validity check *is* the full handler execution:

```rust
fn validate_unsigned(_source: TransactionSource, call: &Self::Call) -> TransactionValidity {
    let messages = match call {
        Call::handle_unsigned { messages } => messages,
        _ => Err(TransactionValidityError::Invalid(InvalidTransaction::Call))?,
    };
    let events = Self::execute(messages.clone()).map_err(|_| InvalidTransaction::BadProof)?;
    ...
``` [1](#0-0) 

`Self::execute` dispatches into `handlers::request::handle` / `handlers::response::handle` for each `Message`, and `RequestMessage`/`ResponseMessage` carry unbounded `Vec<PostRequest>` / `Vec<GetRequest>` [5](#0-4) . For each request in the batch, the handler runs dedup, receipt/timeout checks, and — critically — `state_machine.verify_membership(...)`, a full trie/MMR proof verification over all commitments in the batch [6](#0-5) . None of this — decode, dedup, or proof verification — is gated by a maximum batch size before the expensive work runs.

Because `handle_unsigned` is unsigned, an attacker pays no transaction fee to have every node's transaction pool run this validation. An attacker can gossip a single crafted extrinsic whose `messages` vector contains a very large number of `PostRequest`/`GetRequest` entries (each cheap to construct, since a bad/garbage proof will make verification fail — but only *after* the O(n) dedup/hash/proof-decode work for the whole batch has run). Every node that receives the gossiped transaction re-runs `validate_unsigned` on it, so the CPU cost is paid by the entire network of nodes, not just the submitter — the same "each dispatcher-owned worker allocates per item, cost scales with attacker-controlled item count, no cap on extract path" defect as the W3C baggage advisory (there, item-count/byte-size limits existed for injection but not extraction; here, no batch-size cap exists on the unsigned message-execution path at all).

### Impact Explanation
This is a network-wide resource-exhaustion vector reachable by any unprivileged party able to submit or relay a transaction (no signature, no fee, no prior state required): a message dispatcher/relayer entry point (`handle_unsigned`) that every full node must validate before accepting into its pool. Repeated submission of maximal-size, cheaply-constructed message batches (with garbage or mismatched proofs, which still requires the dedup + iteration + proof-decode/verify-attempt path to run before rejection) can be used to degrade transaction-pool validation throughput and consensus-critical block production across the network — a route rendered "unable to deliver messages" in the worst case, satisfying the "no impact" exclusion bar via a legitimate DoS against message delivery infrastructure.

### Likelihood Explanation
High. The entry point is explicitly permissionless and fee-less by protocol design; no economic friction currently exists to prevent an attacker from submitting arbitrarily large `Vec<Message>` batches. The only gate is `frame_system::CheckWeight`/extrinsic length limits at the block-inclusion layer, but `validate_unsigned` runs on transaction-pool ingress, which happens on every peer that receives the gossiped transaction, independent of whether it ever gets included in a block.

### Recommendation
Enforce an explicit maximum on the number of entries in `messages: Vec<Message>` (and/or per-`RequestMessage`/`ResponseMessage` request counts) at the very start of `validate_unsigned`/`execute`, rejecting oversized batches with a cheap length check before any dedup, hashing, or proof-verification work begins — analogous to the fix pattern already applied in `pallet_call_decompressor::decompress` (bounding `encoded_call_size` before the decompression loop runs) [7](#0-6) .

### Proof of Concept
1. Craft a `pallet_ismp::Call::handle_unsigned` extrinsic with `messages = vec![Message::Request(RequestMessage { requests: <N garbage PostRequests>, proof: <garbage/invalid Proof>, signer: vec![] })]` where `N` is very large (bounded only by max extrinsic/block length, which is generous).
2. Submit as unsigned via RPC / gossip to the network.
3. Every peer node's `validate_unsigned` calls `Self::execute`, which iterates and dedups all `N` requests and attempts full trie/MMR proof verification over all `N` commitments before failing — consuming CPU proportional to `N` on every receiving node, for free, repeatable indefinitely by resubmitting slightly-varied batches (varying content changes the `provides` hash so the pool's replay-dedup does not suppress repeat submissions).

### Citations

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

**File:** modules/ismp/core/src/messaging.rs (L116-147)
```rust
/// A request message holds a batch of requests to be dispatched from a source state machine
#[derive(
	Debug, Clone, Encode, DecodeWithMemTracking, Decode, scale_info::TypeInfo, PartialEq, Eq,
)]
pub struct RequestMessage {
	/// Requests from source chain
	pub requests: Vec<PostRequest>,
	/// Membership batch proof for these requests
	pub proof: Proof,
	/// Signer information. Ideally should be their account identifier
	pub signer: Vec<u8>,
}

/// A response message holds a batch of GetRequests being responded to.
///
/// Post-#840 the protocol no longer carries `PostResponse`; the only
/// responses processed by `handle_response` are GetResponses constructed
/// on-chain from the state proof. The relayer's job is to ferry the
/// original GetRequests plus the storage proof; the host produces the
/// `GetResponse` itself.
#[derive(
	Debug, Clone, Encode, Decode, DecodeWithMemTracking, scale_info::TypeInfo, PartialEq, Eq,
)]
pub struct ResponseMessage {
	/// The batch of GetRequests being responded to.
	pub requests: Vec<GetRequest>,
	/// Membership batch proof for `requests`.
	pub proof: Proof,
	/// Signer information. Ideally should be their account identifier
	pub signer: Vec<u8>,
}

```

**File:** modules/ismp/core/src/handlers/request.rs (L30-93)
```rust
pub fn handle<H>(host: &H, msg: RequestMessage) -> Result<MessageResult, anyhow::Error>
where
	H: IsmpHost,
{
	if msg.requests.is_empty() {
		Err(Error::EmptyBatch)?
	}

	let state_machine = validate_state_machine(host, msg.proof.height)?;
	let consensus_clients = host.consensus_clients();
	let check_state_machine_client = |state_machine: StateMachine| {
		consensus_clients
			.iter()
			.find_map(|client| client.state_machine(state_machine).ok())
			.is_none()
	};

	let router = host.ismp_router();

	// Reject duplicate requests within the batch. Wire format is `Vec`,
	// so this is the line of defence against an attacker padding a
	// batch with identical requests.
	let wrapped: Vec<Request> = msg.requests.iter().cloned().map(Request::Post).collect();
	dedup_requests::<H>(&wrapped)?;

	for req in msg.requests.iter() {
		let req = Request::Post(req.clone());
		// If a receipt exists for any request then it's a duplicate and it is not dispatched
		if host.request_receipt(&req).is_some() {
			Err(Error::DuplicateRequest { meta: req.clone().into() })?
		}

		// can't dispatch timed out requests
		if req.timed_out(host.timestamp()) {
			Err(Error::RequestTimeout { meta: req.clone().into() })?
		}

		// either the host is a router and can accept requests on behalf of any chain
		// or the request must be intended for this chain
		if req.dest_chain() != host.host_state_machine() && !host.is_router() {
			Err(Error::InvalidRequestDestination { meta: req.clone().into() })?
		}

		let source_chain = req.source_chain();

		// in order to allow proxies, the host must configure the given state machine
		// as it's proxy and must not have a state machine client for the source chain
		let allow_proxy = host.is_allowed_proxy(&msg.proof.height.id.state_id) &&
			check_state_machine_client(source_chain);

		// check if the request is allowed to be proxied
		if source_chain != msg.proof.height.id.state_id && !allow_proxy {
			Err(Error::RequestProxyProhibited { meta: req.clone().into() })?
		}
	}

	// Verify membership proof
	let state = host.state_machine_commitment(msg.proof.height)?;
	let commitments = msg
		.requests
		.iter()
		.map(|post| hash_request::<H>(&Request::Post(post.clone())))
		.collect();
	state_machine.verify_membership(host, commitments, state, &msg.proof)?;
```

**File:** docs/content/developers/polkadot/pallet-ismp/overview.mdx (L256-258)
```text
## Transaction fees

Pallet ISMP uses unsigned transactions for executing cross-chain messages. This means all cross-chain messages received are executed for free as unsigned transactions. The upside to this is that it cannot be exploited as a spam vector, since the transaction pool will check if the submitted extrinsics are valid before they are included in the pool. This validity check ensures that the transaction can be successfully executed and contains valid proofs. Malformed messages or those with invalid proofs are filtered out by the transaction pool validation logic preventing unnecessary processing and potential network congestion.
```

**File:** modules/pallets/call-decompressor/src/lib.rs (L220-231)
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
```
