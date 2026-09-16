### Title
Unbounded, unauthenticated `handle_unsigned` batches charged fixed weight enable a validator/block-weight denial-of-service - (File: `modules/pallets/ismp/src/lib.rs`)

### Summary
`pallet_ismp::Call::handle_unsigned` accepts an unsigned, permissionless `messages: Vec<Message>` payload where each `Message::Request`/`Message::Response`/`Message::Timeout` variant itself wraps an unbounded `Vec<PostRequest>`/`Vec<GetRequest>` batch, yet the call is declared with a **fixed, size-independent weight** (`#[pallet::weight(weight())]`, `Weight::from_parts(300_000_000, 0)`), so the fee/weight charged never scales with the amount of verification work actually performed. Any relayer, dispatcher, or unprivileged network peer can exploit this asymmetry to force validators to perform disproportionate CPU work (proof verification, dedup checks, MMR/state-trie membership/non-membership verification) for a fixed, cheap cost — the same "unbounded resource consumption from unauthenticated/low-cost requests" bug class as CVE-2017-4960 (Cloud Foundry UAA OAuth client DoS).

### Finding Description
`handle_unsigned` is declared as: [1](#0-0) 

with the static weight helper: [2](#0-1) 

Because the extrinsic is unsigned, it is gated only by `ValidateUnsigned::validate_unsigned`, which itself **fully executes** the batch (`Self::execute(messages.clone())`) before it is even accepted into the transaction pool: [3](#0-2) 

`Self::execute` iterates every message in the batch and calls `handle_incoming_message` for each one, with no cap on `messages.len()` or on the number of requests inside a single message: [4](#0-3) 

Each `RequestMessage`/`ResponseMessage`/`TimeoutMessage` itself carries an unbounded `Vec<PostRequest>` / `Vec<GetRequest>`; the request handler performs a dedup pass, per-request timeout/destination/proxy checks, and a full membership-proof verification over the entire batch, all inside the same unsigned call, with no upper bound enforced anywhere in `modules/ismp/core/src/handlers/request.rs`: [5](#0-4) [6](#0-5) 

No `MaxRequests`/`MaxMessages`-style bound exists in the pallet (`grep` for `requests.len()`, `messages.len()`, `MaxRequests` in `modules/ismp/core/src` returns nothing), so a single extrinsic can carry an arbitrarily large number of proofs/leaves for the node to verify — each of which runs expensive Merkle/state-trie verification (`state_machine.verify_membership`, `PolkadotTrie.VerifyProof`-equivalent Rust paths) — yet the runtime always charges the same flat 300,000,000 weight units regardless of how much work was actually done. `validate_unsigned` re-runs this full execution on every node that receives the gossiped transaction (every peer in the network, not just the block author), amplifying the cost network-wide, and the `longevity: 25` / re-broadcast semantics mean a crafted oversized batch can be resubmitted repeatedly.

### Impact Explanation
An attacker (an ordinary, unprivileged transaction submitter — no special relayer/collator/admin privilege required, since `handle_unsigned` is `ensure_none`) can submit unsigned extrinsics with maximally sized `Vec<Message>`/`Vec<PostRequest>` batches containing syntactically valid but computationally expensive-to-verify proofs (or crafted to fail late in the pipeline after most of the expensive checks have run). Because weight is static and disconnected from actual execution cost, this:
- Forces every full node's `validate_unsigned` path (executed off-chain, in the transaction pool, on every peer) to burn disproportionate CPU verifying oversized batches, even for transactions that are never included.
- Lets a single accepted block dramatically exceed its intended computational budget while only being charged the flat weight, degrading block production time and potentially causing collators/validators to miss their block-production slot — a network-wide, permissionless DoS vector consistent with "High" severity resource-exhaustion classes like CVE-2017-4960.

This falls within the ISMP message-dispatch/pallet-ismp `handle_unsigned` reachable path explicitly in scope (pallet-ismp `handle_unsigned` and MMR/state membership proof verification).

### Likelihood Explanation
High likelihood: `handle_unsigned` is intentionally permissionless/unsigned so that anyone can relay ISMP messages "for free" — this is a documented design feature, not a bug in access control. The absence of any size cap on `messages` or the nested request/response vectors, combined with a size-independent static weight, means the attack requires no special access, no privileged role, and no capital outlay beyond gas for message construction (submission itself is free since it's unsigned).

### Recommendation
- Enforce an explicit upper bound (e.g. a configurable `MaxMessagesPerBatch` / `MaxRequestsPerMessage` constant) on both the outer `Vec<Message>` and the inner `Vec<PostRequest>`/`Vec<GetRequest>` before any verification work begins, rejecting oversized batches in `validate_unsigned` prior to running `Self::execute`.
- Replace the static `weight()` benchmark with a weight function that scales with `messages.len()` (and ideally with the aggregate number of inner requests/proofs), so `pallet::weight` accurately reflects worst-case verification cost, consistent with how `WeightFeeHandler`/`FeeHandler` already intends fees to track actual computational cost.
- Consider adding a lightweight, cheap pre-check (e.g. bounding proof length/leaf count) in `validate_unsigned` itself so malformed oversized batches are rejected before the expensive full `execute` path runs.

### Proof of Concept
1. Construct an unsigned `pallet_ismp::Call::handle_unsigned` extrinsic whose `messages: Vec<Message>` contains the maximum number of `Message::Request(RequestMessage { requests: Vec<PostRequest>, .. })` entries the encoded-length/block-size limits allow, each with a maximal `requests` vector and a large-but-structurally-valid membership proof.
2. Submit this transaction to any node's transaction pool. `ValidateUnsigned::validate_unsigned` (`modules/pallets/ismp/src/lib.rs:614-626`) invokes `Self::execute(messages.clone())`, which runs `dedup_requests`, per-request checks, and `state_machine.verify_membership` over the full oversized batch (`modules/ismp/core/src/handlers/request.rs:86-132`) on every peer that receives the gossiped transaction.
3. Repeat/rebroadcast such transactions faster than `longevity: 25` blocks expire; because the extrinsic is charged the flat `weight()` (`Weight::from_parts(300_000_000, 0)`) regardless of batch size, the attacker incurs no proportional cost while validators/collators incur disproportionate verification time, demonstrating the resource-exhaustion / block-time DoS.

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

**File:** modules/ismp/core/src/handlers/request.rs (L86-93)
```rust
	// Verify membership proof
	let state = host.state_machine_commitment(msg.proof.height)?;
	let commitments = msg
		.requests
		.iter()
		.map(|post| hash_request::<H>(&Request::Post(post.clone())))
		.collect();
	state_machine.verify_membership(host, commitments, state, &msg.proof)?;
```

**File:** modules/ismp/core/src/handlers/request.rs (L95-132)
```rust
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
