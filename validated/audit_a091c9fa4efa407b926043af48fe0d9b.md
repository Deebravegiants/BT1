### Title
Deprecated TokenGateway address filter in `ProxyModule` permanently freezes in-flight transfers dispatched before deprecation - (File: `parachain/runtimes/nexus/src/ismp.rs`)

### Summary
The Hyperbridge coprocessor's `ProxyModule` (the `IsmpRouter`/`IsmpModule` implementation used by `pallet-ismp` on the nexus runtime) unconditionally rejects **every** incoming `PostRequest` and **every** `PostRequest` timeout whose `from` field matches a hard-coded `DEPRECATED_TOKEN_GATEWAY_ADDRESSES` entry, with no distinction between messages dispatched before and after the address was deprecated. This mirrors the referenced UXD finding: revoking authorization for an asset/contract (`whitelistAsset(false)` there, deprecation-list entry here) also blocks the completion/cancellation path for positions/transfers that were legitimately opened before the revocation, permanently freezing user funds.

### Finding Description
`ProxyModule::on_accept` rejects any request from a deprecated `TokenGateway` address before any further processing: [1](#0-0) 

`ProxyModule::on_timeout` applies the identical unconditional rejection to `PostRequest` timeouts originating from the same deprecated addresses: [2](#0-1) 

The deprecation list itself is a static, hard-coded constant baked into the runtime (activated via a runtime upgrade), not a per-message or per-block-height gated check: [3](#0-2) 

The `TokenGateway`/`HyperFungibleToken` cross-chain-transfer flow locks or burns user funds on the source chain at dispatch time, and only releases/refunds them when either (a) the corresponding request is successfully delivered and accepted on the destination side, or (b) the request times out and the timeout proof is successfully relayed and processed. Both of these completion paths for a `PostRequest` whose `from` is a listed address are unconditionally rejected by `ProxyModule`, regardless of whether the request was dispatched long before the address was added to the deprecation list.

Consequently, any legitimate cross-chain transfer dispatched from one of these `TokenGateway` deployments that is still in flight (not yet delivered, or delayed past its timeout) at the moment the runtime upgrade activating the deprecation list is enacted becomes **permanently unrecoverable**: it can neither complete (delivery is rejected in `on_accept`) nor be refunded (timeout is rejected in `on_timeout`). This is functionally identical to the referenced report's scenario, where unwhitelisting a collateral asset blocked `_redeem()` for already-open PERP positions, forcing them toward liquidation with no way to close out — here, the escrowed/burned source-chain funds for the affected in-flight message become frozen indefinitely with no code path to recover them.

### Impact Explanation
Funds escrowed or burned on the source chain for any in-flight `TokenGateway`/`HyperFungibleToken` transfer that was dispatched by an ordinary, unprivileged user through a soon-to-be-deprecated gateway contract become permanently frozen the moment governance/ops rolls out the deprecation list, because:
- successful delivery is rejected in `on_accept` (`Err(anyhow!(...))`, so `pallet-ismp` cannot mark the request as accepted), and
- the compensating timeout is rejected in `on_timeout`, so the sender cannot recover the locked/burned funds either.

This is a concrete, permanent freezing of user funds triggered purely by ordinary protocol maintenance (deprecating superseded `TokenGateway` deployments) colliding with normal transaction timing — no malicious actor is required, matching the Medium-severity classification of the referenced report.

### Likelihood Explanation
Likelihood is moderate: `TokenGateway` deployments are deprecated in the ordinary course of protocol upgrades (the code comment and constant name confirm this is an anticipated, recurring operational event, and the list already contains three separate deployments). Any user transfer that is in flight at the exact moment such a runtime upgrade activates — which is unavoidable given normal ISMP delivery/timeout latencies — is affected, with no admin override or recovery mechanism available afterward.

### Recommendation
Do not apply the deprecated-address rejection to messages that were already in flight prior to deprecation. Options:
- Scope the block on `on_accept`/`on_timeout` by request/dispatch timestamp (nonce or timeout height) so only *newly dispatched* requests from a deprecated address are rejected, while already-dispatched in-flight requests are still allowed to complete or time out normally.
- Alternatively, enforce the deprecation solely at the dispatch entrypoint (prevent new outbound sends to/through a deprecated address) rather than at the delivery/timeout-acceptance stage, so already-initiated transfers can always be finalized or refunded.

### Proof of Concept
1. User calls `teleport`/`send` on a `TokenGateway`/`HyperFungibleToken` EVM contract (e.g. `Fd413e3AFe560182C4471F4d143A96d3e259B6dE` on Ethereum) before it is deprecated; funds are locked/burned on the source chain and a `PostRequest` with `from = Fd41...B6dE` is dispatched toward Hyperbridge/destination.
2. Before the request is delivered or times out, governance enacts a runtime upgrade on nexus adding this address to `DEPRECATED_TOKEN_GATEWAY_ADDRESSES`.
3. A relayer submits the delivery proof for the pending request: `ProxyModule::on_accept` sees `is_deprecated_token_gateway(&request.from) == true` and returns `Err`, so the transfer is never completed.
4. After the timeout window elapses, a relayer submits the timeout proof for the same request: `ProxyModule::on_timeout` sees the same match and returns `Err`, so the refund/timeout can never be processed either.
5. The user's funds, locked/burned on the source chain, remain frozen with no available code path to release them.

### Citations

**File:** parachain/runtimes/nexus/src/ismp.rs (L49-67)
```rust
/// Deprecated TokenGateway contract addresses whose incoming ISMP Post requests
/// must be rejected unconditionally by the nexus runtime.
/// Any [`PostRequest`] whose `from` field matches any of these 20-byte addresses
/// is rejected in [`ProxyModule::on_accept`] before any other processing — the
/// message is neither dispatched locally nor forwarded onwards.
pub const DEPRECATED_TOKEN_GATEWAY_ADDRESSES: &[[u8; 20]] = &[
	// Ethereum / Arbitrum / Optimism / Base / BSC / Gnosis TokenGateway
	hex_literal::hex!("Fd413e3AFe560182C4471F4d143A96d3e259B6dE"),
	// Polygon / Unichain TokenGateway
	hex_literal::hex!("8b536105b6Fae2aE9199f5146D3C57Dfe53b614E"),
	// Soneium TokenGateway
	hex_literal::hex!("Ce304770236f39F9911BfCC51afBdfF3b8635718"),
];

/// Returns `true` if `from` is exactly one of the deprecated TokenGateway
/// contract addresses in [`DEPRECATED_TOKEN_GATEWAY_ADDRESSES`].
fn is_deprecated_token_gateway(from: &[u8]) -> bool {
	DEPRECATED_TOKEN_GATEWAY_ADDRESSES.iter().any(|deprecated| deprecated == from)
}
```

**File:** parachain/runtimes/nexus/src/ismp.rs (L363-373)
```rust
	fn on_accept(&self, request: PostRequest) -> Result<Weight, anyhow::Error> {
		// Permanently reject any request originating from a deprecated TokenGateway
		// deployment, regardless of destination. This short-circuits both the
		// forwarding path (dest != host) and the locally-dispatched path below.
		if is_deprecated_token_gateway(&request.from) {
			return Err(anyhow!(
				"rejecting request from deprecated TokenGateway address {:?} on {:?}",
				request.from,
				request.source,
			));
		}
```

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
