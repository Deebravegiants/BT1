## Title
Batched ISMP request/response delivery is DOSed by front-running a single request into `handle_unsigned`, reverting the entire message and every honest request bundled with it - (File: `modules/ismp/core/src/handlers/request.rs`)

### Summary
`pallet-ismp`'s `handle_unsigned` extrinsic accepts a `Vec<Message>`, where each `RequestMessage`/`ResponseMessage` bundles many independent POST requests or GET responses under a single membership proof. The request/response handler validates *every* item in the batch up front and short-circuits the whole call with `?` on the first invalid item (most notably a duplicate receipt, i.e. an item that was already delivered). Because `handle_unsigned` is `#[frame_support::transactional]` and its outer `execute()` also collects results with `?`, a single already-delivered (or otherwise invalid) request inside a large batch reverts the *entire* extrinsic - failing delivery for every other, perfectly valid request bundled alongside it. This mirrors the reported Y2K/Earthquake bug class where a first-in-last-out batch (`mintRollovers`) reverts entirely because one participant's precondition fails, DOSing everyone queued with them.

### Finding Description
In `handle<H>(host, msg: RequestMessage)`, the pre-dispatch validation loop iterates over every request in the batch and aborts the whole function on the first failure: [1](#0-0) 

Specifically, `host.request_receipt(&req).is_some()` returning `true` for *any single request* in the batch raises `Error::DuplicateRequest` via `?`, aborting `handle()` before `verify_membership` or any dispatch happens for the other requests in the same message: [2](#0-1) 

This bubbles up through `Pallet::<T>::execute`, which maps `handle_incoming_message` over the outer `Vec<Message>` and collects with `?`, so one failing `Message` fails the whole call: [3](#0-2) 

`handle_unsigned` wraps this in `#[frame_support::transactional]`, guaranteeing that any error rolls back *all* storage writes for the entire batch, not just the offending item: [4](#0-3) 

An attacker (or even a competing/careless relayer) who observes a pending relayer submission containing N requests can front-run it by delivering just one of those N requests in a smaller, separate `handle_unsigned` transaction (itself perfectly valid). Once that single request now has a stored receipt, the original larger batch's re-check at line 58 fails with `DuplicateRequest`, and the *entire* original batch — including the N-1 requests that were never delivered — reverts. The relayer must detect this, strip the poisoned request, and resubmit, and the attacker can repeat this against every subsequent batch attempt containing overlapping requests, effectively DOSing message delivery for that route. The exact same batch-wide short-circuit pattern exists for GET responses in `handle<H>(host, msg: ResponseMessage)`: [5](#0-4) 

### Impact Explanation
This is a "route unable to deliver messages" condition: a low-cost griefer can indefinitely stall cross-chain message delivery for any state machine by continuously front-running one item out of every relayer-submitted batch, forcing atomic reverts of otherwise-valid bundled requests/responses. Since `handle_unsigned` is unsigned and free to submit (any account can call it with a valid proof for a single request), the cost of the attack is minimal relative to the disruption caused — legitimate requests/responses (including time-sensitive settlement messages, e.g. IntentGateway `RedeemEscrow`/`RefundEscrow`) can be delayed past their timeout, causing funds to be stuck until timeout-refund paths execute, or simply delaying protocol operation indefinitely if relayers keep re-batching the same poisoned set.

### Likelihood Explanation
Front-running a single unsigned `handle_unsigned` call with the same commitment/proof data (or a subset of it) targeting one request in an observed pending batch is straightforward on a public mempool, requires no special privilege, and can be repeated cheaply and continuously against any relayer's future batches.

### Recommendation
Do not fail the entire `RequestMessage`/`ResponseMessage` batch when an individual item is a duplicate or otherwise already-processed. Instead, skip that specific request/response (emitting an event/log) and continue processing the remaining valid items in the same membership-proof batch, consistent with how `Error::DuplicateRequest` should be treated as "already delivered, nothing to do" rather than "abort everything." This mirrors the original report's recommendation of skipping the individual poisoned queue entry instead of reverting the whole batch.

### Proof of Concept
1. Relayer A observes N pending, undelivered POST requests destined for the same chain and assembles `RequestMessage { requests: [r1..rN], proof }` to submit via `handle_unsigned`.
2. Attacker observes this pending transaction in the mempool and quickly submits their own `handle_unsigned` with `RequestMessage { requests: [r_k], proof_k }` for a single request `r_k` (`1 <= k <= N`) using a valid, independently-obtainable membership proof for that one request, and it lands first.
3. `request_receipt(r_k)` is now set. When Relayer A's original batch executes, the validation loop in `handle()` hits `host.request_receipt(&req).is_some()` for `r_k` and returns `Err(Error::DuplicateRequest)` via `?` at [2](#0-1) .
4. Because `execute()` collects with `?` ( [3](#0-2) ) and `handle_unsigned` is `#[frame_support::transactional]` ( [4](#0-3) ), the entire batch reverts — none of `r1..rN` (except the attacker's own `r_k`) are delivered, despite all being valid and undelivered before the attack.
5. Repeat for every subsequent resubmitted batch to indefinitely stall delivery on that route.

### Citations

**File:** modules/ismp/core/src/handlers/request.rs (L55-65)
```rust
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
```

**File:** modules/pallets/ismp/src/impls.rs (L43-51)
```rust
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

**File:** modules/ismp/core/src/handlers/response.rs (L47-68)
```rust
	for get in &msg.requests {
		let req = Request::Get(get.clone());

		if req.timed_out(host.timestamp()) {
			Err(Error::RequestTimeout { meta: (&req).into() })?
		}

		if req.dest_chain() != proof.height.id.state_id {
			Err(Error::RequestProofMetadataNotValid { meta: (&req).into() })?
		}

		let commitment = hash_request::<H>(&req);
		if host.request_commitment(commitment).is_err() {
			Err(Error::UnknownRequest { meta: (&req).into() })?
		}

		let res = GetResponse { get: get.clone(), values: Default::default() };

		if host.response_receipt(&res).is_some() {
			Err(Error::DuplicateResponse { meta: (&res).into() })?
		}
	}
```
