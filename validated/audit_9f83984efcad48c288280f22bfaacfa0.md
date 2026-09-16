### Title
Permanent rejection of deprecated TokenGateway `on_timeout` calls in nexus's `ProxyModule` bricks refunds for in-flight requests, permanently freezing escrowed/locked funds - (File: `parachain/runtimes/nexus/src/ismp.rs`)

### Summary
The nexus `ProxyModule::on_timeout` implementation unconditionally rejects (returns `Err`) any POST-request timeout whose `from` address matches `is_deprecated_token_gateway`, before any other handling runs. This mirrors the reported bug class where a dependency (Olympus's `MINTR`) can become "inactive" and permanently brick a permissionless settlement path (`claimDefault`) — except here the rejection is not transient (unlike a paused/frozen module that might later be re-activated), it is a hardcoded, unconditional `Err` for every timeout from that source, forever.

### Finding Description [1](#0-0) 
shows that `on_timeout` immediately returns an error for any `Request::Post` whose `from` is a deprecated `TokenGateway` address, regardless of the specific request being timed out:
```
if let Request::Post(post) = &timeout {
    if is_deprecated_token_gateway(&post.from) {
        return Err(anyhow!(
            "rejecting Post-request timeout from deprecated TokenGateway address {:?}",
            post.from,
        ));
    }
}
```

Per the ISMP timeout handler contract, in both the Substrate `handlers::timeout::handle` implementation and the general design documented in `docs/content/protocol/ismp/timeouts.mdx`, if `IsmpModule::on_timeout` does not return `Ok`, the request commitment is **not deleted**, so the timeout can be resubmitted/retried later: [2](#0-1) 

This retry design assumes the failure condition is *transient* — e.g., an application temporarily out of gas, a temporarily paused token, or (as in the referenced Olympus MINTR bug) an external dependency that is temporarily inactive but might resume later. However, `is_deprecated_token_gateway` is a static/permanent classification: any POST request that originated from the deprecated TokenGateway module before it was decommissioned will have its timeout permanently rejected on every retry, with no path to ever succeed, because the check has no time-bound or reactivation condition — it always evaluates true for that source.

This means users who locked/escrowed funds by sending a request through the (now deprecated) TokenGateway, whose request subsequently times out (e.g., due to relayer failure to deliver, destination liveness issues, or challenge-period delays), can never have their `on_timeout` refund callback execute successfully. The relayer/user can call `handle_unsigned` with the timeout message indefinitely, but `on_timeout` will always return `Err`, the request commitment will never be deleted, and the escrow will never be released.

### Impact Explanation
This is a permanent freezing-of-funds bug: any user with an in-flight POST request from the deprecated TokenGateway at the time of migration (or any residual/late request still referencing it) has no way to recover their escrowed/locked tokens if that request times out. Unlike the referenced Olympus MINTR issue — where the underlying dependency (module `active` flag) could conceivably be turned back on, making the bricking transient — this rejection is unconditional and permanent, so it results in unrecoverable loss of user funds locked in the deprecated escrow, a stronger impact than the original analog.

### Likelihood Explanation
Likelihood is moderate: it requires (a) a request to have been dispatched through the deprecated TokenGateway before/around its deprecation, and (b) that specific request to time out (rather than being delivered successfully). Since the deprecation event itself is a deliberate migration point, there is a realistic window where in-flight requests from the old gateway could still be pending and could time out — at which point their refund path is unconditionally and permanently blocked.

### Recommendation
Scope the deprecated-gateway rejection so it does not affect legitimate pending refunds: e.g., only apply the rejection to *newly dispatched* on_accept flows (to stop new usage) while still allowing `on_timeout` for requests that were validly in-flight before the deprecation cutoff to be processed through the original TokenGateway timeout logic. Alternatively, provide a one-time migration/sweep mechanism that force-releases escrow for outstanding requests from the deprecated module, so no request is left in a state where its commitment can never be cleared.

### Proof of Concept
1. Prior to TokenGateway deprecation, a user dispatches a POST request via the (soon to be deprecated) TokenGateway module, locking tokens in escrow on nexus, with `timeoutTimestamp` set in the future.
2. The TokenGateway is deprecated and `is_deprecated_token_gateway` begins matching its module address.
3. Before the destination processes the request, its `timeoutTimestamp` elapses without delivery.
4. A relayer/user submits a `TimeoutMessage::Post` via `pallet_ismp::Call::handle_unsigned`, routing to `ProxyModule::on_timeout`.
5. `on_timeout` sees `post.from` matches the deprecated TokenGateway and returns `Err(...)` unconditionally (`parachain/runtimes/nexus/src/ismp.rs:426-432`), so per `modules/ismp/core/src/handlers/timeout.rs:122-133` the request commitment is restored/never deleted, allowing indefinite resubmission but never success.
6. Repeat step 4 any number of times — the outcome is always the same `Err`, and the user's escrowed funds in the deprecated TokenGateway pallet are permanently locked with no code path to release them.

### Citations

**File:** parachain/runtimes/nexus/src/ismp.rs (L421-433)
```rust
	fn on_timeout(&self, timeout: Request) -> Result<Weight, anyhow::Error> {
		// Permanently reject Post-request timeouts whose originating module is a
		// deprecated TokenGateway deployment, before any other handling runs. Only
		// Post requests are subject to this — Get requests and Response timeouts
		// are untouched.
		if let Request::Post(post) = &timeout {
			if is_deprecated_token_gateway(&post.from) {
				return Err(anyhow!(
					"rejecting Post-request timeout from deprecated TokenGateway address {:?}",
					post.from,
				));
			}
		}
```

**File:** modules/ismp/core/src/handlers/timeout.rs (L113-134)
```rust
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
```
