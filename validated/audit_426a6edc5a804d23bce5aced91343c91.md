### Title
Unmetered Full-Verification in `pallet-ismp::validate_unsigned` Enables Network-Wide DoS via Free Crafted Messages - (File: modules/pallets/ismp/src/lib.rs)

### Summary
`pallet-ismp`'s `handle_unsigned` extrinsic is dispatched with `ensure_none` (no fee, no signature) so that "anyone [can] execute ISMP datagrams for free" [1](#0-0) . The transaction-pool gate that is supposed to cheaply filter out garbage before it costs the network anything is `validate_unsigned`, but that function does not perform a cheap pre-check — it unconditionally runs `Self::execute(messages.clone())`, i.e. the *entire* message-processing pipeline (state-machine validation, trie membership/non-membership verification, and for consensus messages, full BEEFY/SP1 verification), for every submitted unsigned extrinsic [2](#0-1) . This is functionally the same bug class as the Plone `queryCatalog` caching bypass: a cheap gate that was meant to short-circuit before expensive work instead *is* the expensive work, so a crafted request forces full-cost processing on every validating node, with no fee to throttle the attacker.

### Finding Description
The pallet's own documentation asserts this is safe because "the transaction pool will check if the submitted extrinsics are valid before they are included in the pool... preventing unnecessary processing and potential network congestion" [3](#0-2) . That claim conflates "validity checking" with "cheap check" — but the validity check *is* the costly trie-proof / consensus verification itself:

- `validate_unsigned` calls `Self::execute(messages.clone())` directly with no size/complexity-independent short-circuit [4](#0-3) .
- For `Message::Request`, `handlers::request::handle` performs `dedup_requests`, receipt/timeout/proxy checks, then `state_machine.verify_membership(...)` — a full Merkle/child-trie proof verification over attacker-supplied proof bytes [5](#0-4) .
- For `Message::Consensus`, the pipeline invokes the concrete `ConsensusClient::verify_consensus`, which for BEEFY means ECDSA signature verification over the full authority set or SP1 zkVM proof verification [6](#0-5) .
- The `pallet-state-coprocessor::handle_unsigned` path is identical in shape: `validate_unsigned` calls `Self::handle_get_requests(message.clone())` directly, which performs two full state-proof verifications (`verify_membership` and `verify_state_proof`) over attacker-controlled proof bytes before returning [7](#0-6) , [8](#0-7) .

Because these are unsigned extrinsics, `validate_unsigned` runs on *every full node* that receives the transaction over gossip (and again on re-validation/re-broadcast), not just the node that authors a block. An attacker can generate a stream of syntactically-valid but ultimately-rejected `RequestMessage`/`ConsensusMessage`/`GetRequestsWithProof` payloads, each crafted to produce a unique transaction-pool `provides` tag (e.g. varying `nonce`, `timeout`, or otherwise-cosmetic fields, per the tag-construction logic itself) so the pool cannot dedupe them [9](#0-8) , and each embedding maximal-size but bogus proof blobs. Every such submission forces full trie/consensus verification cost on each receiving node before it is finally rejected — with zero cost to the attacker.

This mirrors the Plone `queryCatalog` bug class exactly: a mechanism whose entire purpose is to cheaply gate work (here, mempool admission) instead performs the full expensive operation on every crafted request, so an unprivileged actor can trigger unbounded resource consumption network-wide.

### Impact Explanation
This is a network-wide denial of service (CWE-400) reachable by any unprivileged party who can submit unsigned extrinsics/gossip transactions to Hyperbridge nodes. Sustained CPU exhaustion from repeated full membership/consensus-proof verification across the validator/full-node set can stall block production and mempool processing, which in turn means a route becomes "unable to deliver messages" — legitimate cross-chain requests (token bridge messages, intents, relayer fee claims) queued behind or competing for the same node resources are delayed or dropped, satisfying the "route unable to deliver messages" impact bar.

### Likelihood Explanation
High. No privileged role, signature, or on-chain fee is required — `ensure_none` origin means the attacker only pays for constructing proof-shaped byte blobs, which is cheap and fully automatable, and can be replayed continuously with trivially varied fields to avoid pool deduplication.

### Recommendation
- Add a cheap, size/complexity-bounded pre-check ahead of any trie or consensus verification in `validate_unsigned` for both `pallet-ismp::handle_unsigned` and `pallet-state-coprocessor::handle_unsigned` — e.g., bound proof byte length strictly, and reject messages whose referenced state/consensus height/commitment is not already known to the host before attempting full verification.
- Consider requiring a minimal bond or `SignedExtension`-style pre-charge (refunded on success) for unsigned proof-carrying extrinsics so verification cost is attributable and throttled, similar to the "cost paid on failure" model already used for `pallet-beefy-consensus-proofs` signed proof submissions [10](#0-9) .
- Rate-limit/greylist peers whose unsigned submissions repeatedly fail full verification.

### Proof of Concept
1. An attacker constructs `N` distinct `Message::Request(RequestMessage { requests, proof, signer })` batches where `proof` is a maximal-size, well-formed-but-invalid `StorageProof`/trie-node blob, and `requests` differ only in an attacker-controlled field (e.g. `nonce`) so each batch hashes to a unique `provides` tag per the tag-derivation logic [11](#0-10) .
2. The attacker submits all `N` batches as unsigned extrinsics (`ensure_none` origin, zero fee) to the network in a short window.
3. Every full node that receives each transaction via gossip runs `validate_unsigned`, which calls `Self::execute(...)` and therefore `state_machine.verify_membership(...)` over the full (bogus but maximal-size) proof before rejecting it [12](#0-11) .
4. Repeating this at scale (or interleaving with `Message::Consensus` batches targeting non-BEEFY-filtered consensus clients to force full ECDSA/SP1 verification) drives sustained CPU load across the network for zero attacker cost, degrading block production and message delivery.

### Citations

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

**File:** modules/pallets/ismp/src/lib.rs (L647-691)
```rust
			// No state machine was advanced by these messages. Build a content-unique
			// `provides` tag from the messages themselves so that distinct submissions
			// never collide in the transaction pool.
			//
			// A consensus message that doesn't advance a state machine (e.g. a
			// validator-set rotation during sync) previously mapped to an empty request
			// list via the catch-all arm. Every such message therefore produced an
			// identical `provides` tag and a fixed priority of 100, so the pool rejected
			// any two of them with "Priority is too low (100 vs 100)". Hashing the
			// consensus message (excluding the signer, so equivalent submissions from
			// different relayers dedupe) gives each update a unique tag.
			let mut has_consensus = false;
			let mut tags = messages
				.into_iter()
				.map(|message| match message {
					Message::Consensus(ConsensusMessage {
						consensus_proof,
						consensus_state_id,
						..
					}) => {
						has_consensus = true;
						vec![H256(sp_io::hashing::keccak_256(
							&(consensus_state_id, consensus_proof).encode(),
						))]
					},
					Message::FraudProof(FraudProofMessage { proof_1, proof_2, .. }) => vec![
						H256(sp_io::hashing::keccak_256(&proof_1)),
						H256(sp_io::hashing::keccak_256(&proof_2)),
					],
					Message::Request(RequestMessage { requests, .. }) => requests
						.into_iter()
						.map(|post| hash_request::<Pallet<T>>(&Request::Post(post.clone())))
						.collect::<Vec<_>>(),
					Message::Response(message) => message
						.requests()
						.iter()
						.map(|request| hash_request::<Pallet<T>>(request))
						.collect::<Vec<_>>(),
					Message::Timeout(message) => message
						.requests()
						.iter()
						.map(|request| hash_request::<Pallet<T>>(request))
						.collect::<Vec<_>>(),
				})
				.collect::<Vec<_>>();
```

**File:** docs/content/developers/polkadot/pallet-ismp/overview.mdx (L256-258)
```text
## Transaction fees

Pallet ISMP uses unsigned transactions for executing cross-chain messages. This means all cross-chain messages received are executed for free as unsigned transactions. The upside to this is that it cannot be exploited as a spam vector, since the transaction pool will check if the submitted extrinsics are valid before they are included in the pool. This validity check ensures that the transaction can be successfully executed and contains valid proofs. Malformed messages or those with invalid proofs are filtered out by the transaction pool validation logic preventing unnecessary processing and potential network congestion.
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

**File:** docs/content/protocol/ismp/consensus.mdx (L161-175)
```text
/// This function handles verification of consensus messages for consensus clients
pub fn update_client<H>(host: &H, msg: ConsensusMessage) -> Result<(), Error>
where
    H: IsmpHost,
{
  // .. implementation details
}

```

The `update_client` method is responsible for advancing the state of the consensus client. This performs the consensus verification of new `StateCommitment`s that have been finalized by a `StateMachine`'s consensus system. The `IsmpHost` must return the concrete implementation of the associated `ConsensusClient` and a previously stored `ConsensusState`. The procedure for updating the consensus client is as follows.

- First the handler must assert that the consensus client is not frozen or expired. Consensus clients can expire if the last time the consensus client was updated has exceeded the chain's unbonding period. This effectively mitigates any potential long fork attacks that may arise due to a loss of liveness of consensus clients.
- Finally the handler may perform consensus proof verification using the concrete implementation for the consensus client using `ConsensusClient::verify_consensus`. If verifications pass, the udpated `ConsensusState` and `IntermediateState`s are persisted to storage and enter a new challenge period.

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

**File:** modules/pallets/state-coprocessor/src/impls.rs (L105-136)
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
```

**File:** modules/pallets/beefy-consensus-proofs/src/lib.rs (L24-27)
```rust
//! Proofs are submitted via **signed** extrinsics: the signer of the extrinsic is the
//! reward payee. The pallet sets `Pays::No` on accepted proofs so a successful prover
//! gets their fee refunded along with the reward; failed proofs pay the transaction
//! fee normally, which keeps spam off the chain.
```
