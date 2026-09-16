### Title
Unbounded, fee-free `handle_unsigned` message batches let an unprivileged relayer trigger repeatable CPU-exhaustion DoS during transaction-pool validation - ([File: modules/pallets/ismp/src/lib.rs])

### Summary
`pallet-ismp`'s `handle_unsigned` extrinsic accepts an arbitrary-length `Vec<Message>`, each of which may itself carry an arbitrary-length `Vec<PostRequest>`/`Vec<GetRequest>` plus a proof. This call is `ensure_none`-gated (fully permissionless) and is validated for free via `ValidateUnsigned::validate_unsigned`, which runs the *entire* `Pallet::<T>::execute(messages.clone())` pipeline — full membership-proof verification, signature checks, and dispatch — before any fee is charged and before the fixed extrinsic `weight()` is enforced against actual batch size. This is directly analogous to the nghttp2 SETTINGS-frame bug class: an attacker-controlled batch whose internal element count is unbounded, processed in full by cheap/free validation logic, causing disproportionate CPU consumption that can be repeated indefinitely at near-zero cost.

### Finding Description
`handle_unsigned` is declared as:
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
``` [1](#0-0) 

and its mempool gate:
```rust
fn validate_unsigned(_source: TransactionSource, call: &Self::Call) -> TransactionValidity {
    let messages = match call {
        Call::handle_unsigned { messages } => messages,
        _ => Err(TransactionValidityError::Invalid(InvalidTransaction::Call))?,
    };
    let events = Self::execute(messages.clone()).map_err(|_| InvalidTransaction::BadProof)?;
    ...
}
``` [2](#0-1) 

`Self::execute` iterates over every message and runs `handle_incoming_message`, which for a `RequestMessage`/`ResponseMessage` performs, per element: a duplicate-request scan, timeout checks, and — crucially — a full membership-proof verification over the *entire batch* of requests/keys (`state_machine.verify_membership(...)` / `verify_state_proof(...)`), as shown in the request/response handlers:
```rust
pub fn handle<H>(host: &H, msg: RequestMessage) -> Result<MessageResult, anyhow::Error>
...
    let wrapped: Vec<Request> = msg.requests.iter().cloned().map(Request::Post).collect();
    dedup_requests::<H>(&wrapped)?;
    for req in msg.requests.iter() { ... }
    ...
    state_machine.verify_membership(host, commitments, state, &msg.proof)?;
``` [3](#0-2) 

Nowhere in `execute`, `handle_unsigned`, or `validate_unsigned` is there a cap on `messages.len()`, on `RequestMessage::requests.len()`/`GetRequest::keys.len()`, or on the size of proof structures (e.g., GRANDPA justification `precommits`/`votes_ancestries`, whose verification runs one Ed25519 signature check and ancestry-set insertion per precommit, or EVM/Substrate `verify_state_proof` which loops over every supplied key). Any consensus client wired into `T::ConsensusClients` inherits this: a message referencing a GRANDPA/BEEFY/sync-committee proof with thousands of signature entries, or a `RequestMessage`/`ResponseMessage` with thousands of `PostRequest`/`GetRequest` keys, is fully decoded and cryptographically verified inside `validate_unsigned` before it is rejected for being invalid or duplicate (`InvalidTransaction::BadProof`).

Because `handle_unsigned` is unsigned, this validation runs at zero cost to the sender and can be resubmitted continuously (only `longevity: 25` and the `provides` tag deduplicate identical batches, but varying the batch trivially bypasses that), giving an unprivileged relayer/message dispatcher a repeatable, free lever to force full-batch verification work on every full/validating node — the direct on-chain analogue of the nghttp2 SETTINGS-frame flood: attacker-controlled, unbounded-size payload fully parsed/verified by cheap validation logic before rejection, causing CPU spikes.

### Impact Explanation
This is a network/consensus-layer availability issue: validating nodes (and the runtime executing `handle_unsigned` in a block) spend unbounded CPU per submitted unsigned extrinsic performing proof/signature verification proportional to attacker-chosen batch size, with no economic cost gating it (it is explicitly "free" per the pallet's own documentation: "all cross-chain messages received are executed for free as unsigned transactions"). Repeated submission of maximal-size, ultimately-invalid batches can degrade block production and transaction-pool throughput for the whole parachain, denying service to legitimate relayers and applications — a route that can render Hyperbridge unable to reliably deliver messages under load. This meets the "route unable to deliver messages" acceptance criterion.

### Likelihood Explanation
High. `handle_unsigned` is deliberately permissionless (`ensure_none`) and is the intended path for "anyone" to relay messages; no additional signature, deposit, or per-call size limit gates the size of `Vec<Message>` or the nested `Vec<PostRequest>`/`Vec<GetRequest>`/proof vectors before the pallet performs full verification. An attacker needs only network access to a validating node's RPC/transaction-pool to submit maximal-size unsigned extrinsics repeatedly.

### Recommendation
- Enforce a hard, cheap-to-check upper bound on `messages.len()` and on the length of nested vectors (`RequestMessage::requests`, `ResponseMessage::requests`, `GetRequest::keys`, GRANDPA `precommits`/`votes_ancestries`, etc.) at the very start of `validate_unsigned`/`handle_unsigned`, before any decoding-heavy or cryptographic work is performed.
- Make the extrinsic's declared `weight()` scale with the actual (bounded) batch size so `CheckWeight` and block-weight accounting reflect real cost, rather than a size-independent fixed weight.
- Consider a lightweight, size-based rejection or increasing `longevity`/anti-spam tagging so that varying batch content cannot trivially defeat the existing `provides` dedup tag.

### Proof of Concept
1. An attacker crafts a `handle_unsigned` extrinsic carrying a single `Message::Request(RequestMessage)` whose `requests: Vec<PostRequest>` contains the maximum number of entries the codec/extrinsic size limits allow (or, for a GRANDPA-secured chain, a `Message::Consensus` wrapping a `GrandpaJustification` with a maximal `precommits`/`votes_ancestries` list), with an invalid or stale proof so the call ultimately fails validation.
2. Submit this unsigned extrinsic directly via RPC (`author_submitExtrinsic` / `submit_and_watch`), bypassing normal fee/weight gating since the origin is `None`.
3. `validate_unsigned` executes `Self::execute(messages.clone())`, which runs `dedup_requests`, per-request checks, and full membership-proof verification (or, for GRANDPA, one Ed25519 `check_message_signature` per precommit plus ancestry-set bookkeeping) over the entire attacker-chosen batch before returning `InvalidTransaction::BadProof`.
4. Resubmit continuously with cosmetically varied (still maximal) batches to bypass the `provides` dedup tag, at zero fee cost, sustaining elevated CPU usage on every validating node — mirroring the nghttp2 SETTINGS-frame flood pattern of unbounded, attacker-controlled entry counts being fully processed before rejection.

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
