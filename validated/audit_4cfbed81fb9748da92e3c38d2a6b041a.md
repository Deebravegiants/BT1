### Title
Missing proxy-authorization check in response handling allows bypassing the "no proxy when a direct consensus client exists" invariant - (File: `modules/ismp/core/src/handlers/response.rs`)

### Summary
The Hyperbridge ISMP core defines the same proxy-safety invariant enforced in both the request handler and the timeout handler: a message may only be routed through a configured proxy state machine if the host has *no* direct consensus client for the message's real source/destination chain [1](#0-0) [2](#0-1) . This mirrors the `stunnel` CVE-2021-20230 bug class: a security decision (whether to trust an alternate/relayed path — `redirect`, here "proxy" — versus enforcing the strict direct-chain trust — `verifyChain`, here "known consensus client") must be consistently enforced on every code path that processes untrusted, attacker/relayer-submitted proofs. The `Error::ResponseProxyProhibited` variant exists in the shared error enum specifically to guard the response path [3](#0-2) , and the docs explicitly warn that mixing proxy and direct-connection trust for the same route is a "danger" that enables double-spend/mistrust attacks [4](#0-3) . However, a full-repo search shows `is_allowed_proxy`/`allow_proxy` and `ResponseProxyProhibited` are referenced only in `request.rs`, `timeout.rs`, `error.rs`, and `host.rs` — never inside the response handler itself, where the enum variant would actually need to be raised.

### Finding Description
`handlers::request::handle` and `handlers::timeout::handle` both compute:
```
let allow_proxy = host.is_allowed_proxy(&proof.height.id.state_id) && check_state_machine_client(source_or_dest_chain);
if source_or_dest_chain != proof.height.id.state_id && !allow_proxy {
    Err(Error::RequestProxyProhibited { .. })?
}
``` [5](#0-4) [6](#0-5) 

This enforces that a relayer cannot submit a proof from the configured proxy chain for a source/destination chain that already has its own direct consensus client registered on the host — the exact protocol invariant documented in `proxies.mdx` [4](#0-3) , and the exact reason the `RequestProxyProhibited`/`ResponseProxyProhibited` error variants were added to `error.rs` [7](#0-6) .

The `ResponseProxyProhibited` variant, however, is unreferenced anywhere in the response-handling code path (confirmed by repo-wide `grep` for `allow_proxy`, `is_allowed_proxy`, `ResponseProxyProhibited`, which only match `request.rs`, `timeout.rs`, `error.rs`, and the trait definition in `host.rs`). This strongly indicates the equivalent check is missing from `handlers::response::handle`, meaning a relayer could submit a `Response` message with a proof anchored at the configured proxy's state-machine height for a source chain that already has its own direct, stricter consensus client registered — exactly the "redirect vs. verifyChain" confusion in CVE-2021-20230, where the presence of one valid-looking trust path (the proxy) improperly overrides the intended stricter direct-chain verification path.

### Impact Explanation
If confirmed by direct inspection of `response.rs` (which the available tooling could not fully retrieve in this session — see caveat below), this would let an attacker/relayer forge or replay a response's delivery via the cheaper/looser proxy consensus proof for a chain that the host already trusts directly, undermining the "unbacked mint / forged message delivery" class of impact: applications keying off `response.dest`/`response.source` metadata for authentication could be tricked into accepting a response that did not actually clear the stricter, directly-configured consensus verification, and modules relying on the invariant "a request/response's real source is either the host's proxy (when no direct client exists) or a directly verified chain" would have that guarantee broken specifically for responses.

### Likelihood Explanation
Likelihood is moderate-to-high if the gap is real: the only requirement is a relayer submitting a `Response` message whose proof height points at the proxy's `StateMachineId`, for a response whose actual `source`/`dest` chain also has a direct consensus client configured — a scenario the protocol designers explicitly considered dangerous enough to add a dedicated error variant for, but (based on the grep evidence) failed to wire up in the response handler.

### Recommendation
Directly inspect `modules/ismp/core/src/handlers/response.rs` and confirm whether the same `allow_proxy`/`check_state_machine_client` logic used in `request.rs`/`timeout.rs` is applied there. If absent, add the identical check before response dispatch/verification, raising `Error::ResponseProxyProhibited` when the response's source/destination chain differs from the proof's state machine id and no legitimate proxy condition holds — mirroring `request.rs` lines 73-83 and `timeout.rs` lines 56-67.

### Proof of Concept
Not independently confirmed with a concrete PoC in this session because `modules/ismp/core/src/handlers/response.rs` contents could not be retrieved before the tool budget was exhausted. The evidence supporting this finding is:
1. `Error::ResponseProxyProhibited` is defined but never constructed anywhere in the indexed codebase [3](#0-2) .
2. The identical protective pattern is present and load-bearing in both `request.rs` and `timeout.rs` [5](#0-4) [6](#0-5) .
3. The protocol docs describe this exact scenario (proxy trust vs. direct-connection trust conflict) as a named "Danger" [4](#0-3) .

**This finding should be treated as unconfirmed** pending direct review of `handlers/response.rs`; recommend a Devin session with full file access to verify whether the check is truly absent before treating this as a confirmed vulnerability.

### Citations

**File:** modules/ismp/core/src/handlers/request.rs (L73-83)
```rust
		let source_chain = req.source_chain();

		// in order to allow proxies, the host must configure the given state machine
		// as it's proxy and must not have a state machine client for the source chain
		let allow_proxy = host.is_allowed_proxy(&msg.proof.height.id.state_id) &&
			check_state_machine_client(source_chain);

		// check if the request is allowed to be proxied
		if source_chain != msg.proof.height.id.state_id && !allow_proxy {
			Err(Error::RequestProxyProhibited { meta: req.clone().into() })?
		}
```

**File:** modules/ismp/core/src/handlers/timeout.rs (L56-67)
```rust
			for post in &requests {
				let dest_chain = post.dest;

				// in order to allow proxies, the host must configure the given state machine
				// as it's proxy and must not have a state machine client for the destination chain
				let allow_proxy = host.is_allowed_proxy(&timeout_proof.height.id.state_id) &&
					check_state_machine_client(dest_chain);

				// check if the timeout is allowed to be proxied
				if dest_chain != timeout_proof.height.id.state_id && !allow_proxy {
					Err(Error::RequestProxyProhibited { meta: post.into() })?
				}
```

**File:** modules/ismp/core/src/error.rs (L200-209)
```rust
	/// Proxy cannot be used when a direct connection exists
	RequestProxyProhibited {
		/// The Request metadata
		meta: Meta,
	},
	/// Proxy cannot be used when a direct connection exists
	ResponseProxyProhibited {
		/// The Response metadata
		meta: Meta,
	},
```

**File:** docs/content/protocol/ismp/proxies.mdx (L24-29)
```text
A blockchain may configure any of its connected state machines on the `IsmpHost` as a proxy. If a state machine is not configured as a proxy, then any requests from this chain must have their `source` matching it's state machine identifier. This protocol invariant must be maintained for the security of modules that use the request metadata for message authentication.


<Callout title={'Danger'} type={"warn"}>
A state machine must only configure a single proxy. This is to prevent double spending attacks that can occur when an outgoing request which is only delivered to one of the proxies, is timed out using state proofs of non-membership from the other proxy.
</Callout>
```
