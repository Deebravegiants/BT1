### Title
Missing response-receipt re-check before dispatching GET timeouts allows double settlement of the same GET request - (File: `modules/ismp/core/src/handlers/timeout.rs`)

### Summary
This is not a strong analog. The OSV report describes a use-after-free/double-free in OpenJPEG caused by processing a mix of valid and invalid files without properly invalidating a shared object between iterations (`opj_image_destroy` called twice). The closest logical analog in Hyperbridge is the batch-processing code in `pallet-ismp`'s message handlers, which explicitly defend against the equivalent bug class (double-invocation of an app callback for the same request within one batch) by re-checking receipts/commitments immediately before each dispatch — see the documented fixes in `modules/ismp/core/src/handlers/request.rs` lines 103-110 and `modules/ismp/core/src/handlers/timeout.rs` lines 96-105 (POST) and 172-181 (GET), and `modules/ismp/core/src/handlers/response.rs` lines 94-101. [1](#0-0) [2](#0-1) [3](#0-2) 

### Finding Description
In the `TimeoutMessage::Get` branch of `handle` in `modules/ismp/core/src/handlers/timeout.rs`, the up-front validation loop (lines 143-164) checks that no `response_receipt` exists for the request before allowing it into the batch. However, the per-item dispatch loop (lines 166-202) only re-checks `request_commitment` right before deleting it and invoking `cb.on_timeout` (lines 178-181) — it does **not** re-check `response_receipt` a second time, unlike the pattern deliberately used elsewhere in the same file and in `response.rs`/`request.rs` to guard against reentrancy within a single batch. [4](#0-3) 

Because a batch can contain multiple GET requests, and `cb.on_timeout` for an earlier item is an arbitrary untrusted module callback that can re-enter the ISMP dispatcher (as explicitly called out in the comments for the analogous POST case and in `response.rs`), it is architecturally possible for a later item in the same GET-timeout batch to receive its response mid-batch (storing a `response_receipt`) without the timeout loop detecting it, since only `request_commitment` is rechecked, not `response_receipt`. This mirrors the OpenJPEG bug class: a batch mixing "still valid" and "already invalidated mid-run" items, where the code's second-pass validation is incomplete relative to what changed during the first pass, permitting a resource that should be considered "already consumed" (a request that already has a response) to be handled again through a second code path (`on_timeout`).

### Impact Explanation
If reachable, this would allow the same GET request commitment to be settled through both `on_response` and `on_timeout` in the same or adjacent transactions, i.e., double-processing/finalization of a single cross-chain request by application logic (e.g., a fisherman/token/intents module implementing `on_timeout`/`on_response` differently), matching the "unauthorized app action" impact bucket.

### Likelihood Explanation
Low-to-uncertain. This requires: (1) an app module's `on_timeout` callback to actually perform a reentrant call back into the dispatcher/response handler for a *different* GET request within the same batch, and (2) that reentrant path to successfully call `handle_unsigned`/the response handler mid-execution of the timeout batch. I could not verify from the indexed code that any shipped module (`hyper-fungible-token`, `state-coprocessor`, `IntentGatewayV2`, etc.) actually performs such reentrant cross-calls from within `on_timeout`; the `Request::Get` arm of `on_timeout` in `hyper-fungible-token/src/module.rs` simply errors out (`UnsupportedTimeoutType`), and I did not find another GET-consuming module with reentrant behavior in the parts of the codebase the index returned. Given the size limits on the index, I cannot rule out or confirm a concrete reentrant module exists elsewhere.

### Recommendation
For defense-in-depth and consistency with the pattern already applied to `request_commitment`, `request_receipt`, and `response_receipt` elsewhere, add a `response_receipt` re-check immediately before `host.delete_request_commitment(&request)` in the `TimeoutMessage::Get` dispatch loop in `modules/ismp/core/src/handlers/timeout.rs`, mirroring the existing recheck comments/pattern at lines 96-107 and 172-181.

### Proof of Concept
Not constructible with confidence from the available index: no concrete reentrant `on_timeout` module implementation was found to trigger the described mid-batch response delivery, so this cannot be demonstrated as an exploitable end-to-end path with the code currently available. This should be treated as a hardening gap rather than a confirmed exploitable vulnerability.

### Citations

**File:** modules/ismp/core/src/handlers/request.rs (L103-110)
```rust
				// Re-check the receipt right before dispatch. The up-front pass above
				// runs before any callback executes; a prior request's on_accept in
				// this same batch could have stored a receipt for this request
				// (directly or by re-entering the handler), and we must not invoke
				// on_accept a second time.
				if host.request_receipt(&wrapped_req).is_some() {
					Err(Error::DuplicateRequest { meta: wrapped_req.clone().into() })?
				}
```

**File:** modules/ismp/core/src/handlers/timeout.rs (L96-107)
```rust
					// Re-check the commitment right before dispatch. The up-front
					// pass above runs before any callback executes; a prior
					// on_timeout in this same batch could have caused the
					// commitment for this request to be removed (directly or by
					// re-entering the handler), and we must not invoke
					// on_timeout for a request that is no longer pending.
					let commitment = hash_request::<H>(&request);
					if host.request_commitment(commitment).is_err() {
						Err(Error::UnknownRequest { meta: (&post).into() })?
					}
					// Delete commitment to prevent rentrancy attack
					let meta = host.delete_request_commitment(&request)?;
```

**File:** modules/ismp/core/src/handlers/timeout.rs (L166-184)
```rust
			let router = host.ismp_router();
			requests
				.into_iter()
				.map(|get| {
					let cb = router.module_for_id(get.from.clone())?;
					let request = Request::Get(get.clone());
					// Re-check the commitment right before dispatch. The up-front
					// pass above runs before any callback executes; a prior
					// on_timeout in this same batch could have caused the
					// commitment for this request to be removed (directly or by
					// re-entering the handler), and we must not invoke
					// on_timeout for a request that is no longer pending.
					let commitment = hash_request::<H>(&request);
					if host.request_commitment(commitment).is_err() {
						Err(Error::UnknownRequest { meta: (&get).into() })?
					}
					// Delete commitment to prevent reentrancy
					let meta = host.delete_request_commitment(&request)?;
					let res = cb.on_timeout(request.clone()).map(|weight| {
```

**File:** modules/ismp/core/src/handlers/response.rs (L94-101)
```rust
			// Re-check the receipt right before dispatch. The up-front pass above
			// runs before any callback executes; a prior response's on_response in
			// this same batch could have stored a receipt for this response
			// (directly or by re-entering the handler), and we must not invoke
			// on_response a second time.
			if host.response_receipt(&response).is_some() {
				Err(Error::DuplicateResponse { meta: (&response).into() })?
			}
```
