### Title
Unbounded per-request linear scan + blocking retry loop over the allowlisted-requests array allows unauthenticated request flooding to stall Vault node authorization - (File: core/capabilities/vault/allow_list_based_auth.go)

### Summary
The Vault DON's allowlist-based authorization path performs an O(n) linear scan of an unboundedly-growing, in-memory `allowListedRequests` slice for *every* incoming gateway vault request that lacks a JWT (`req.Auth == ""`), and retries this full scan up to 11 times with 3-second sleeps between attempts when the digest isn't found. This mirrors the reported bug class ("unbounded loops... can lead to out-of-gas/DoS") but manifests here as unbounded CPU/latency cost per request rather than gas — any unprivileged actor able to reach the gateway can trigger repeated full-array scans and multi-second blocking delays on every DON node.

### Finding Description
`allowListBasedAuth.AuthorizeRequest` calls `findAllowlistedItemWithRetry`, which loops up to `retryCount+1` (11) times, and on each iteration calls `r.workflowRegistrySyncer.GetAllowlistedRequests(ctx)` and then `fetchAllowlistedItem`, which does a **linear scan (`for _, item := range allowListedRequests`)** over the entire allowlist to find a matching digest: [1](#0-0) 

This array (`w.allowListedRequests`) is a global, shared, in-memory slice maintained by `workflowRegistry.syncAllowlistedRequests`, which appends newly-observed on-chain allowlist entries every tick and only prunes entries once they expire: [2](#0-1) 

Its size grows with the total count of active allowlist entries across **all workflow owners on the network**, and is entirely out of the control of any single request handler — there is no cap, pagination, or map-based lookup by digest.

Critically, this scan/retry loop is on the **unauthenticated request path**: `authorizer.authorizeRequest` explicitly routes any request with an empty `Auth` field to `allowListBasedAuth` "for backwards compatibility," meaning it accepts requests from any caller without JWT verification and only relies on this linear allowlist check: [3](#0-2) 

This is reached directly from the gateway-facing entry point `GatewayHandler.HandleGatewayMessage`, which processes every incoming `MethodSecretsCreate`/`MethodSecretsUpdate`/`MethodSecretsDelete`/`MethodSecretsList` request from the gateway by calling `h.requestProcessor.ProcessRequest`, which in turn calls the authorizer before any other structural rate limiting is applied: [4](#0-3) [5](#0-4) 

No per-sender or per-IP rate limiting exists in the `core/capabilities/vault` package itself (confirmed by absence of any `RateLimiter`/`Allow(` usage in that directory) to throttle bogus/unauthorized digest lookups before they reach this expensive retry loop.

### Impact Explanation
For any request whose digest is not present in the allowlist (i.e., an unauthorized or garbage request from an unprivileged sender), the node will:
1. Perform up to 11 full linear scans of the (unboundedly growing) allowlist.
2. Block for up to ~30 seconds (`10 * 3s` sleeps) per bad request before finally rejecting it with "request not allowlisted".

As the allowlist naturally grows over time with legitimate on-chain activity by many workflow owners, the cost of each malicious/garbage request scan increases without bound, and the blocking retry window multiplies this cost across concurrently open bad requests. An attacker able to send arbitrary JSON-RPC vault requests through the gateway (no prior authentication or JWT required for this path) can amplify node-side CPU usage and hold goroutines/resources for tens of seconds per request, degrading throughput and increasing latency for all legitimate vault operations on affected DON nodes — a Medium-severity availability/DoS impact, directly analogous to the reported unbounded-loop DoS class.

### Likelihood Explanation
Likelihood is Medium: no privileged role, prior registration, or on-chain transaction is required to send an "allowlist-based" request to the gateway (empty `Auth` field triggers this path by design for backward compatibility). Any external client can reach `GatewayHandler.HandleGatewayMessage` via the gateway connector and submit crafted `MethodSecretsCreate`/`Update`/`Delete`/`List` requests with arbitrary/garbage digests, forcing the full retry+scan sequence on every DON node handling the request.

### Recommendation
- Replace the linear `fetchAllowlistedItem` scan with a map lookup keyed by request digest (`map[[32]byte]WorkflowRegistryOwnerAllowlistedRequest`) maintained alongside `allowListedRequests`, updated in `syncAllowlistedRequests`, to make lookups O(1) regardless of allowlist size.
- Apply a per-sender/per-IP rate limiter (similar to `ratelimiter.RateLimiter` used elsewhere in the gateway stack) ahead of `AuthorizeRequest` in `GatewayVaultRequestProcessor`/`GatewayHandler` so that repeated unauthorized digest probes cannot consume unbounded retry/CPU budget.
- Consider bounding or capping `allowListedRequests` size, or fail fast (skip retries) for requests whose digest cannot possibly match (e.g., no owner context), rather than always exhausting the full retry budget with multi-second sleeps.

### Proof of Concept
1. An unprivileged client connects through the internet-facing gateway and sends a `MethodSecretsList` (or `Create`/`Update`/`Delete`) JSON-RPC request with `Auth == ""` and an arbitrary/garbage payload (so its digest will never match any allowlist entry).
2. `GatewayHandler.HandleGatewayMessage` → `GatewayVaultRequestProcessor.ProcessRequest` → `authorizer.AuthorizeRequest` → `allowListBasedAuth.AuthorizeRequest` is invoked.
3. `findAllowlistedItemWithRetry` performs a full linear scan of `allowListedRequests` (size = total active allowlist entries network-wide) up to 11 times, sleeping 3 seconds between each failed attempt.
4. The node blocks/burns CPU for up to ~30 seconds processing this single bogus request before returning "request not allowlisted".
5. Repeating this from multiple concurrent unauthenticated senders (no rate limiting exists in this code path) multiplies resource consumption on every DON node relaying gateway messages, degrading availability for legitimate vault users.

Note: I was unable to fully verify whether an upstream/global gateway-level rate limiter (outside the `core/capabilities/vault` package, e.g. in the shared `gateway.go`/`connector.go` HTTP layer) mitigates this before requests reach `HandleGatewayMessage`; the index did not show such a limiter directly wired into the Vault gateway handler's inbound path. If a session confirms none exists (or it is trivially bypassable via distinct request IDs/digests), this finding stands as described.

### Citations

**File:** core/capabilities/vault/allow_list_based_auth.go (L79-120)
```go
func (r *allowListBasedAuth) findAllowlistedItemWithRetry(ctx context.Context, req jsonrpc.Request[json.RawMessage], requestDigest string, requestDigestBytes32 [32]byte) (*workflow_registry_wrapper_v2.WorkflowRegistryOwnerAllowlistedRequest, []string, error) {
	for attempt := 0; attempt <= r.retryCount; attempt++ {
		allowedRequests := r.workflowRegistrySyncer.GetAllowlistedRequests(ctx)
		allowedRequestsStrs := make([]string, 0, len(allowedRequests))
		for _, rr := range allowedRequests {
			allowedReqStr := fmt.Sprintf("AuthorizedOwner: %s, RequestDigest: %s, ExpiryTimestamp: %d", rr.Owner.Hex(), hex.EncodeToString(rr.RequestDigest[:]), rr.ExpiryTimestamp)
			allowedRequestsStrs = append(allowedRequestsStrs, allowedReqStr)
		}
		r.lggr.Debugw("AllowListBasedAuth loaded allowlisted requests", "method", req.Method, "requestID", req.ID, "attempt", attempt+1, "allowedRequests", allowedRequestsStrs)

		allowlistedRequest := r.fetchAllowlistedItem(allowedRequests, requestDigestBytes32)
		if allowlistedRequest != nil {
			return allowlistedRequest, allowedRequestsStrs, nil
		}
		if attempt == r.retryCount {
			return nil, allowedRequestsStrs, nil
		}

		r.lggr.Debugw("AllowListBasedAuth request digest not yet allowlisted, retrying",
			"method", req.Method,
			"requestID", req.ID,
			"digestHexStr", requestDigest,
			"attempt", attempt+1,
			"maxAttempts", r.retryCount+1,
			"retryInterval", r.retryInterval)
		if err := sleepWithContext(ctx, r.retryInterval); err != nil {
			r.lggr.Debugw("AllowListBasedAuth retry canceled", "method", req.Method, "requestID", req.ID, "error", err)
			return nil, nil, err
		}
	}

	return nil, nil, nil // unreachable: loop always returns
}

func (r *allowListBasedAuth) fetchAllowlistedItem(allowListedRequests []workflow_registry_wrapper_v2.WorkflowRegistryOwnerAllowlistedRequest, digest [32]byte) *workflow_registry_wrapper_v2.WorkflowRegistryOwnerAllowlistedRequest {
	for _, item := range allowListedRequests {
		if item.RequestDigest == digest {
			return &item
		}
	}
	return nil
}
```

**File:** core/services/workflows/syncer/v2/workflow_registry.go (L766-805)
```go
func (w *workflowRegistry) syncAllowlistedRequests(ctx context.Context) {
	ticker := w.getTicker(defaultTickIntervalForAllowlistedRequests)
	w.lggr.Debug("starting syncAllowlistedRequests")
	for {
		select {
		case <-ctx.Done():
			w.lggr.Debug("shutting down syncAllowlistedRequests, %s", ctx.Err())
			return
		case <-ticker:
			newAllowListedRequests, totalAllowlistedRequests, head, err := w.getAllowlistedRequests(ctx, w.contractReader)
			if err != nil {
				w.lggr.Errorw("failed to call getAllowlistedRequests", "err", err)
				continue
			}
			w.allowListedMu.Lock()
			// Prune expired requests
			activeAllowlistedRequests := []workflow_registry_wrapper_v2.WorkflowRegistryOwnerAllowlistedRequest{}
			expiredRequestsCount := 0
			for _, request := range w.allowListedRequests {
				if int64(request.ExpiryTimestamp) > time.Now().Unix() {
					activeAllowlistedRequests = append(activeAllowlistedRequests, request)
				} else {
					expiredRequestsCount++
				}
			}

			// Add new requests
			activeAllowlistedRequests = append(activeAllowlistedRequests, newAllowListedRequests...)
			w.allowListedRequests = activeAllowlistedRequests
			w.lastSeenAllowlistedRequestsCount = totalAllowlistedRequests
			w.lggr.Debugw("synced allowlisted requests",
				"newRequestsNum", len(newAllowListedRequests),
				"expiredRequestsNum", expiredRequestsCount,
				"activeRequestsNum", len(w.allowListedRequests),
				"lastSeenOnchainRequestsNum", w.lastSeenAllowlistedRequestsCount,
				"blockHeight", head.Height,
			)
			w.allowListedMu.Unlock()
		}
	}
```

**File:** core/capabilities/vault/authorizer.go (L121-137)
```go
func (a *authorizer) authorizeRequest(ctx context.Context, req jsonrpc.Request[json.RawMessage]) (*AuthResult, error) {
	// Requests without req.Auth continue using the allowlist-based path for backwards compatibility.
	// Existing clients do not populate the auth field yet, so treating an empty value as JWT would break them.
	if req.Auth == "" {
		return a.authorizeAllowListBasedAuth(ctx, req)
	}
	return a.authorizeJWTBasedAuth(ctx, req)
}

func (a *authorizer) authorizeAllowListBasedAuth(ctx context.Context, req jsonrpc.Request[json.RawMessage]) (*AuthResult, error) {
	if a.allowListBasedAuth == nil {
		err := errors.New("AllowListBasedAuth authorizer is nil")
		a.lggr.Errorw("AllowListBasedAuth unavailable", "method", req.Method, "requestID", req.ID, "error", err)
		return nil, err
	}
	return a.allowListBasedAuth.AuthorizeRequest(ctx, req)
}
```

**File:** core/capabilities/vault/gw_handler.go (L180-211)
```go
func (h *GatewayHandler) HandleGatewayMessage(ctx context.Context, gatewayID string, req *jsonrpc.Request[json.RawMessage]) (err error) {
	reqLggr := h.requestLogger(req, gatewayID)
	reqLggr.Debugw("received message from gateway", "req", req)

	var response *jsonrpc.Response[json.RawMessage]
	var authResult *AuthResult

	switch req.Method {
	case vaulttypes.MethodSecretsCreate, vaulttypes.MethodSecretsUpdate:
		publicKey, pkErr := h.getMasterPublicKey(ctx)
		if pkErr != nil {
			response = h.gatewayErrorResponse(ctx, gatewayID, req, pkErr)
			break
		}
		authorized, pipelineErr := h.requestProcessor.ProcessRequest(ctx, req, publicKey)
		if pipelineErr != nil {
			response = h.gatewayErrorResponse(ctx, gatewayID, req, pipelineErr)
			break
		}
		authResult = authorized.AuthResult
	case vaulttypes.MethodSecretsDelete, vaulttypes.MethodSecretsList:
		authorized, pipelineErr := h.requestProcessor.ProcessRequest(ctx, req, nil)
		if pipelineErr != nil {
			response = h.gatewayErrorResponse(ctx, gatewayID, req, pipelineErr)
			break
		}
		authResult = authorized.AuthResult
	case vaulttypes.MethodPublicKeyGet:
		response = h.handlePublicKeyGet(ctx, gatewayID, req)
	default:
		response = h.errorResponse(ctx, gatewayID, req, api.UnsupportedMethodError, errors.New("unsupported method: "+req.Method))
	}
```

**File:** core/capabilities/vault/gateway_vault_request_processor.go (L260-276)
```go
func (p *GatewayVaultRequestProcessor) authorizeAndStamp(
	ctx context.Context,
	req *jsonrpc.Request[json.RawMessage],
	stamp func(prefixedRequestID string) error,
) (*AuthorizedGatewayVaultRequest, error) {
	incomingOwner := ""
	if idx := strings.Index(req.ID, vaulttypes.RequestIDSeparator); idx != -1 {
		incomingOwner = req.ID[:idx]
	}

	p.lggr.Debugw("authorizing gateway vault request", "method", req.Method, "requestID", req.ID)
	authResult, err := p.authorizer.AuthorizeRequest(ctx, *req)
	if err != nil {
		authErr := fmt.Errorf("request not authorized: %w", err)
		p.lggr.Errorw("gateway vault request authorization failed", "method", req.Method, "requestID", req.ID, "hasAuth", req.Auth != "", "incomingOwner", incomingOwner, "error", authErr)
		return nil, authErr
	}
```
