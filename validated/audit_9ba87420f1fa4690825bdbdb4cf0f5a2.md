### Title
Single Erroring Callback Within a Batched Timeout Message Can Abort the Entire Batch and Roll Back Already-Processed Timeouts - (File: `modules/ismp/core/src/handlers/timeout.rs`)

### Summary
`modules/ismp/core/src/handlers/timeout.rs::handle` processes a relayer-submitted batch of `PostRequestTimeout`/`GetRequestTimeout` messages in a single dispatchable call. Unlike the sibling `request.rs::handle` (which isolates per-item failures with `.collect::<Vec<_>>()`), the timeout handler's per-`Post`/`Get` loops use `.collect::<Result<Vec<_>, _>>()?`, which short-circuits on the first `Err` produced anywhere inside the per-item closure. A single bad/erroring entry in a batch can therefore cause the whole extrinsic to return `Err`, which — combined with Substrate's atomic dispatchable semantics — rolls back all storage mutations (including `delete_request_commitment`/`on_request_timeout` for other, legitimately-processed requests) performed earlier in that same batch.

### Finding Description
In `handle` for `TimeoutMessage::Post`: [1](#0-0) 

each request in the batch is processed via:
```
requests.into_iter().map(|post| {
    let cb = router.module_for_id(post.from.clone())?;
    ...
    let meta = host.delete_request_commitment(&request)?;
    ...
    let res = cb.on_timeout(request.clone()).map(...);
    if res.is_ok() {
        host.on_request_timeout(&request, meta)?;
    } else {
        host.store_request_commitment(&request, meta)?;
        ...
    }
    Ok::<_, anyhow::Error>(res)
})
.collect::<Result<Vec<_>, _>>()?
```
The `?` operators reachable from `router.module_for_id(...)`, `host.delete_request_commitment(...)`, `host.on_request_timeout(...)`, and `host.store_request_commitment(...)` all propagate an `Err` out of the closure for that single item. Because the outer type is `Result<Vec<_>, _>` (not `Vec<Result<_,_>>`), Rust's `Result: FromIterator` implementation stops iterating and returns the first `Err` immediately — the closure is never even invoked for the remaining requests in the batch, and the top-level `?` at line 137 propagates that error out of `handle`. The identical pattern exists for `TimeoutMessage::Get` at line 202.

This is structurally the same "single failing external/downstream call breaks the whole batch" class of bug as the `SponsorVault` finding: there, a single revert inside `s.sponsorVault.reimburseLiquidityFees`/`reimburseRelayerFees` aborted the entire `execute` transaction for a message that otherwise had nothing to do with the sponsor vault. Here, a single failing lookup/storage call for one timeout item in a batch aborts delivery of every other timeout in that same batch, and — because Substrate dispatchables are atomic — reverts any state changes (commitment deletion, timeout refund payout via `host.on_request_timeout`) that had already been applied for earlier, successfully-processed items in the same call.

By contrast, the sibling handler for incoming requests explicitly isolates per-item failures instead of aggregating them into a fail-fast `Result`: [2](#0-1) 

That handler collects into a plain `Vec<_>` of per-item `Result<Event, anyhow::Error>`, so one item's failure never affects the outcome of any sibling item in the batch — this is the correct fail-safe pattern that `timeout.rs` should also use but does not.

### Impact Explanation
A relayer (an unprivileged, permissionless actor able to submit `TimeoutMessage` batches) can craft or simply encounter a batch where one entry triggers an error path (e.g., `module_for_id` failing to resolve a destination module, or any other fallible storage operation reached inside the loop). Because the whole batch's processing is wrapped in a single fail-fast `collect::<Result<...>>()?`, that one bad entry denies delivery of every other timeout in the batch and — critically — rolls back state changes already committed for previously-processed entries in the same call (deleted request commitments, refunds via `on_request_timeout`). This is a denial-of-service / griefing vector on cross-chain timeout settlement: legitimate users whose timeouts were bundled alongside a problematic entry are denied their refunds/cleanup in that submission, and the route can be repeatedly griefed by relayers assembling similarly poisoned batches, undermining the timeout mechanism that is meant to safely revert state after liveness failures (as documented in `docs/content/protocol/ismp/timeouts.mdx`).

### Likelihood Explanation
Likelihood is moderate: `TimeoutMessage` batches are relayer-assembled and permissionless to submit, so a relayer (malicious or simply operating on stale/inconsistent state, e.g. a since-unregistered module id, a request commitment removed by a race with another submission) can trigger the fail-fast path. The `dedup_requests` and per-item pre-checks at lines 55–84 do not verify `router.module_for_id` resolves successfully before entering the fail-fast dispatch loop, so this failure mode is not pre-filtered.

### Recommendation
Change the per-item timeout processing in both the `Post` and `Get` branches of `modules/ismp/core/src/handlers/timeout.rs` to collect into `Vec<Result<Event, anyhow::Error>>` (as `request.rs` does) instead of `Result<Vec<_>, _>` with a trailing `?`. Each item's failure (module resolution failure, storage errors, callback failure) should be captured and reported per-item (e.g., surfaced in `MessageResult::Timeout` or an error event) rather than aborting/rolling back the entire batch. This ensures one problematic timeout entry cannot prevent delivery of, or roll back state for, unrelated timeouts processed earlier in the same batch.

### Proof of Concept
1. A relayer dispatches a `PostRequestTimeoutMessage`/`TimeoutMessage::Post` extrinsic containing two timed-out requests, R1 and R2, both with valid non-membership proofs.
2. R1 has a `from` module id that is currently registered and valid; processing R1 succeeds up through `host.delete_request_commitment` and `cb.on_timeout(...)`, and `host.on_request_timeout(&request, meta)` is executed (refund/cleanup applied).
3. R2 has a `from` module id that is no longer registered in the router (e.g., a pallet removed/upgraded since R2 was originally dispatched), so `router.module_for_id(post.from.clone())` returns `Err`.
4. Because the two items are processed via `.map(...).collect::<Result<Vec<_>, _>>()?`, the `Err` from R2 propagates out of `handle`, causing the whole extrinsic to fail.
5. Substrate's transactional dispatch semantics revert all storage writes made during this failed call, including the `delete_request_commitment`/`on_request_timeout` effects already applied for R1 — so R1's legitimate timeout settlement is silently undone even though it individually would have succeeded, and neither R1 nor R2 timeout is settled in this submission.

### Citations

**File:** modules/ismp/core/src/handlers/timeout.rs (L90-137)
```rust
			let router = host.ismp_router();
			requests
				.into_iter()
				.map(|post| {
					let cb = router.module_for_id(post.from.clone())?;
					let request = Request::Post(post.clone());
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
					let mut signer = None;
					// If it was a routed request delete the receipt
					if host.host_state_machine() != post.source {
						signer = host.delete_request_receipt(&request).ok();
					}
					let res = cb.on_timeout(request.clone()).map(|weight| {
						total_module_weight.saturating_accrue(weight);
						let commitment = hash_request::<H>(&request);
						Event::PostRequestTimeoutHandled(TimeoutHandled {
							commitment,
							source: post.source,
							dest: post.dest,
						})
					});
					if res.is_ok() {
						host.on_request_timeout(&request, meta)?;
					} else {
						// Module callback failed; restore commitment so the request
						// can be retried.
						host.store_request_commitment(&request, meta)?;
						if host.host_state_machine() != post.source && signer.is_some() {
							host.store_request_receipt(
								&request,
								&signer.ok_or_else(|| anyhow::anyhow!("Infallible"))?,
							)?;
						}
					}
					Ok::<_, anyhow::Error>(res)
				})
				.collect::<Result<Vec<_>, _>>()?
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
