## Finding

### Title
Global-only mTLS rate/concurrency limiter in HTTP Gateway handler lets any subset of workflows starve mTLS capacity for all other tenants - (File: core/services/gateway/handlers/capabilities/v2/http_handler.go)

### Summary
The Gateway's HTTP Action handler enforces mTLS outbound request throttling using a single **global** rate limiter (`mtlsRequestRateLimiter`) and a single **global** concurrency pool (`mtlsConcurrencyLimiter`), shared across every workflow/owner on the DON. There is no per-workflow or per-owner accounting for this specific shared resource at the gateway layer, so any combination of workflows/owners — each individually staying within their own separate per-owner limits enforced elsewhere — can collectively exhaust the shared mTLS capacity and deny it to all other tenants, mirroring the reported bug class where a single shared capacity pool (`VaultBorrowCapacity`) can be exhausted by a subset of its consumers, starving the rest.

### Finding Description
`NewGatewayHandler` constructs exactly one `mtlsRequestRateLimiter` and one `mtlsConcurrencyLimiter`, both scoped globally (`cresettings.Default.GatewayHTTPActionMtlsRequestRate` / `GatewayHTTPActionMtlsConcurrencyLimit`), with no per-sender/per-owner/per-workflow dimension: [1](#0-0) 

These are consumed in `send()` when an outbound HTTP action carries `Mtls` credentials: [2](#0-1) 

The comment in `send()` explicitly acknowledges the tradeoff and claims it is mitigated by (a) the global rate limit itself, (b) per-node rate limits on sending workflow-DON nodes, and (c) per-owner rate limits enforced separately in the HTTP Action **capability** running on the workflow node (a different component, outside gateway control). None of these compensating controls provide per-owner/per-workflow accounting for the *mtls-specific* shared pool at the gateway itself: many distinct workflow owners, each individually compliant with their own local per-owner cap in the capability, can still collectively drive the single global `mtlsConcurrencyLimiter`/`mtlsRequestRateLimiter` to exhaustion, since the gateway has no visibility into, or enforcement of, per-tenant fairness for this specific resource. This is structurally identical to the Notional finding: a capacity pool intended to serve many independent principals (there: maturities in a vault; here: many workflow owners' mTLS HTTP actions) is tracked only as a single aggregate counter, so any subset of principals can monopolize it and deny the rest.

### Impact Explanation
Once the shared mTLS rate limiter or concurrency pool is exhausted (whether by one large workflow owner or by many small ones collectively), all other unrelated workflows attempting mTLS-authenticated outbound HTTP actions through the same gateway are denied via `network.ErrBlockedRequest`, regardless of their own individual quota compliance. This is a availability/DoS impact against legitimate unprivileged workflow tenants sharing the same DON's gateway, reachable purely through normal HTTP Action capability usage (setting `Mtls` on an `OutboundHTTPRequest`) — no privileged access is required.

### Likelihood Explanation
Likelihood is moderate: it requires either one workflow (up to its own per-owner cap) plus other workflows/owners simultaneously issuing mTLS outbound HTTP actions, or several distinct owners coordinating (or merely operating concurrently) to saturate the small global mTLS pool (defaults are conservative, e.g., low concurrency/RPS values intended for a narrow mTLS use case). Since HTTP Action with mTLS is a normal, documented capability feature available to any workflow owner, this doesn't require any bypass of authentication — just concurrent legitimate usage by multiple tenants.

### Recommendation
Add per-owner or per-workflow scoping to the mTLS rate limiter and concurrency pool at the gateway layer (mirroring the pattern already used elsewhere in this codebase, e.g., `limits.MultiResourcePoolLimiter` combining global + per-owner + per-org pools as done in `core/services/workflows/v2/config.go`), so that no single owner or small set of owners can consume the entire shared mTLS capacity and starve others. At minimum, reserve a fraction of the global pool per owner/workflow, or track usage keyed by workflow owner similar to `perNodeRateLimiters`.

### Proof of Concept
1. Configure `cresettings.Default.GatewayHTTPActionMtlsConcurrencyLimit` and `GatewayHTTPActionMtlsRequestRate` at their (low) defaults.
2. Have N distinct workflow owners, each individually compliant with their own per-owner limit enforced in the HTTP Action capability on the workflow node, simultaneously send `OutboundHTTPRequest` with `Mtls` set through the same gateway DON.
3. Once the aggregate in-flight/rate crosses the single global limiter/pool threshold in `send()` (`core/services/gateway/handlers/capabilities/v2/http_handler.go:333`), subsequent requests from *any* other legitimate, quota-compliant owner fail with `"global mtls request rate limit exceeded"` / `"mtls concurrency limit exceeded"` (see test expectations at `core/services/gateway/handlers/capabilities/v2/http_handler_test.go:983` and `core/services/gateway/network/httpclient_mtls_test.go:427-428`), demonstrating cross-tenant denial of service from a resource pool with no per-tenant isolation.

### Citations

**File:** core/services/gateway/handlers/capabilities/v2/http_handler.go (L154-162)
```go
	mtlsRequestRateLimiter, err := lf.MakeRateLimiter(cresettings.Default.GatewayHTTPActionMtlsRequestRate)
	if err != nil {
		return nil, fmt.Errorf("failed to create mtls rate limiter: %w", err)
	}

	mtlsConcurrencyLimiter, err := limits.MakeResourcePoolLimiter(lf, cresettings.Default.GatewayHTTPActionMtlsConcurrencyLimit)
	if err != nil {
		return nil, fmt.Errorf("failed to create mtls concurrency limiter: %w", err)
	}
```

**File:** core/services/gateway/handlers/capabilities/v2/http_handler.go (L298-337)
```go
func (h *gatewayHandler) send(ctx context.Context, httpReq network.HTTPRequest, req gateway_common.OutboundHTTPRequest) (*network.HTTPResponse, error) {
	if req.Mtls == nil {
		return h.httpClient.Send(ctx, httpReq)
	}

	if h.httpClientFactory == nil {
		return nil, errors.New("nil http client factory, cannot make mtls request")
	}

	// Instantiate a throwaway HTTP client with the provided Mtls client certificate provided.
	// We do this to ensure that we don't accidentally leak auth'd connections to other users.
	// Note: this isn't a DOS vector because
	// a) we have a global rate limit above which limits abuse
	// b) we apply rate limits limiting the ability of sending nodes to spam requests
	// c) we apply per-owner rate limits in the action capability in the
	// workflow node limiting the ability of users to abuse this flow by spamming Mtls requests.
	// The client enforces the mtls concurrency limit internally (on the request's
	// capped-timeout context) before delegating to the underlying transport.
	client, err := h.httpClientFactory(network.HTTPClientConfig{
		Mtls: &gateway_common.MtlsAuth{
			PrivateKey:  req.Mtls.PrivateKey,
			Certificate: req.Mtls.Certificate,
		},
		ConcurrencyLimiter: h.mtlsConcurrencyLimiter,
	})
	if err != nil {
		return nil, fmt.Errorf("failed to instantiate http client for mtls request: %w", err)
	}

	// We don't have access to the org here, so this will fall back to the environment default (=false).
	// That's appropriate because all fields set on the request come from untrusted nodes.
	// The capability separately applies an org-specific check.

	// Note: we intentionally consume the rate-limit after instantiating the client so that a malicious user
	// can't send requests with invalid mtls credentials and thus cheaply consume global tokens.
	if !h.mtlsRequestRateLimiter.Allow(ctx) {
		return nil, fmt.Errorf("global mtls request rate limit exceeded: %w", network.ErrBlockedRequest)
	}

	return client.Send(ctx, httpReq)
```
