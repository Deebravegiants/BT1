Based on my investigation, this is a confirmed finding: the gateway response cache is scoped by `WorkflowOwner` but explicitly ignores `WorkflowID`, which enables cross-workflow cached-response confusion when the same owner runs multiple workflows against the same external endpoint with differing sensitivity/authorization contexts.

### Title
HTTP Action Response Cache Key Ignores WorkflowID, Enabling Cross-Workflow Response Confusion - (File: core/services/gateway/handlers/capabilities/v2/response_cache.go)

### Summary
The gateway's `responseCache` for outbound HTTP action requests computes its cache key via `req.Hash()` on `gateway_common.OutboundHTTPRequest`, which is proven by unit tests to include `WorkflowOwner` but **explicitly exclude `WorkflowID`** from the hash [1](#0-0) . This contradicts the component's own documentation, which claims "Workflow Isolation: Cache entries are scoped by workflow ID to prevent cross-workflow data leakage" and "Cache Key: Generated from workflow ID and request hash" [2](#0-1) .

### Finding Description
`responseCache.Fetch` and `responseCache.Set` both key the cache map purely on `req.Hash()`: [3](#0-2) [4](#0-3) 

The test suite directly documents the intended (and actual) hash behavior:
- Same `WorkflowOwner` → same hash (confirmed intentional) [5](#0-4) 
- Different `WorkflowOwner` → different hash [6](#0-5) 
- Different `WorkflowID`, same everything else → **same hash** (explicitly asserted as intended behavior) [1](#0-0) 

This is the direct analog to the CVE-2026-22039/GHSA-cvq5-hhx3-f99p pattern: a scoping field that *should* isolate one tenant context from another (there, Kubernetes namespace; here, workflow ID) is present in the request struct but is not included in the isolation key used by the privileged shared component (there, the ConfigMap loader; here, the gateway's shared response cache). The root cause is architecturally identical — the isolation boundary is documented/expected but not enforced in the actual key derivation.

Because the gateway is the unprivileged, internet/DON-facing shared component that serves potentially many different workflows for the same owner (and the cache is shared across all HTTP Action requests routed through `gatewayHandler.makeOutgoingRequest`), any two workflows owned by the same address that hit the same URL/method/headers/body combination will collide on the same cache entry [7](#0-6) .

### Impact Explanation
If Workflow A (owned by address X) makes an HTTP action request with `CacheSettings.Store: true` to an endpoint, and Workflow B (also owned by X, but a different workflow with different secrets, headers, or execution context assumed to be isolated per the design doc) later issues a request that resolves to the same `Method+URL+Headers+Body` hash within the TTL window (default up to 10 minutes), Workflow B receives Workflow A's cached response instead of making its own live request. This breaks the "workflow isolation" guarantee the component explicitly claims to provide, and can lead to:
- Stale/incorrect data being fed into a different workflow's execution logic (integrity issue for downstream on-chain actions).
- Response confusion between logically separate workflow contexts for the same owner (the CWE-863 "incorrect authorization" analog: authorization/isolation is enforced at the owner level but not at the finer workflow-level boundary the system advertises).

This does not, by itself, leak data across different owners (owner is part of the hash), so the practical severity is lower than the original Kyverno CVE (which allowed full cross-namespace RBAC bypass). It is best characterized as a **workflow-level isolation bypass within a single owner's account**, not a cross-tenant secret disclosure.

### Likelihood Explanation
Reaching this requires only that an unprivileged workflow owner operate two or more workflows that issue HTTP Action requests with `CacheSettings.Store: true` to identical URLs/methods/bodies — a normal, low-privilege, self-service scenario (no special RBAC or gateway-admin access needed), since HTTP Action requests originate from workflow nodes acting on behalf of the workflow owner and are routed through the shared `gatewayHandler`/`responseCache` used by all workflows [8](#0-7) .

### Recommendation
Include `WorkflowID` (and/or `WorkflowOwner`) explicitly in the cache key derivation used by `Hash()`/`responseCache`, matching the behavior already documented in `README.md`. Add a regression test asserting that different `WorkflowID` values produce different hashes (the inverse of the current `TestRequestHash` assertion at lines 139-149), and audit any other callers relying on the documented "workflow-scoped caching" guarantee.

### Proof of Concept
1. As an unprivileged workflow owner, register two workflows (`wf-A`, `wf-B`) both owned by the same address.
2. `wf-A` issues an HTTP Action request: `GET https://example.com/api`, `CacheSettings: {Store: true, MaxAgeMs: 600000}`.
3. Gateway executes the real request and stores the response keyed by `req.Hash()` (owner-scoped, not workflow-scoped) via `responseCache.Set`.
4. `wf-B` (different `WorkflowID`, same owner) issues an HTTP Action request with identical `Method/URL/Headers/Body` and `CacheSettings.MaxAgeMs > 0`.
5. `responseCache.Fetch` computes the same `cacheKey` (since `WorkflowID` is excluded per `TestRequestHash`'s "having different workflowID results in same Hash" case) and returns `wf-A`'s cached response to `wf-B` without making a live request — demonstrating the documented workflow-isolation boundary is not enforced in code.

### Citations

**File:** core/services/gateway/handlers/capabilities/v2/response_cache_test.go (L139-149)
```go
	t.Run("having different workflowID results in same Hash", func(t *testing.T) {
		req1 := createTestRequest("GET", "https://example.com")
		req1.WorkflowID = "workflow-123"

		req2 := createTestRequest("GET", "https://example.com")
		req2.WorkflowID = "workflow-456"

		hash1 := req1.Hash()
		hash2 := req2.Hash()
		require.Equal(t, hash1, hash2, "Hash should be the same regardless of WorkflowID")
	})
```

**File:** core/services/gateway/handlers/capabilities/v2/response_cache_test.go (L151-161)
```go
	t.Run("having same workflowOwner results in the same Hash", func(t *testing.T) {
		req1 := createTestRequest("GET", "https://example.com")
		req1.WorkflowOwner = "workflow-owner-123"

		req2 := createTestRequest("GET", "https://example.com")
		req2.WorkflowOwner = "workflow-owner-123"

		hash1 := req1.Hash()
		hash2 := req2.Hash()
		require.Equal(t, hash1, hash2, "Hash should be the same for identical requests")
	})
```

**File:** core/services/gateway/handlers/capabilities/v2/response_cache_test.go (L163-175)
```go
	t.Run("having different workflowOwner results in different Hash", func(t *testing.T) {
		req1 := createTestRequest("GET", "https://example.com")
		req1.WorkflowOwner = "workflow-owner-123"

		req2 := createTestRequest("GET", "https://example.com")
		req2.WorkflowOwner = "workflow-owner-456"

		hash1 := req1.Hash()
		hash2 := req2.Hash()
		require.NotEqual(t, hash1, hash2, "Hash should be different for different workflow owner")
		require.NotEmpty(t, hash1, "Hash should not be empty")
		require.NotEmpty(t, hash2, "Hash should not be empty")
	})
```

**File:** core/services/gateway/handlers/capabilities/v2/README.md (L65-72)
```markdown
### 3.2 Caching Behavior

- **Cacheable Responses**: 2xx (success) and 4xx (client error) status codes.
- **Cache TTL**: Configurable, default 10 minutes
- **Cache Key**: Generated from workflow ID and request hash
- **Cache Invalidation**: Time-based expiration with periodic cleanup
- **Cache Strategy**: All cacheable responses are cached; Non-zero `CacheSettings.MaxAgeMs` determines whether to return a cached value or make a fresh request
- **Workflow Isolation**: Cache entries are scoped by workflow ID to prevent cross-workflow data leakage
```

**File:** core/services/gateway/handlers/capabilities/v2/response_cache.go (L66-77)
```go
func (rc *responseCache) Fetch(ctx context.Context, req gateway.OutboundHTTPRequest, fetchFn func() gateway.OutboundHTTPResponse, storeOnFetch bool) gateway.OutboundHTTPResponse {
	cacheKey := req.Hash()
	cacheMaxAge := time.Duration(req.CacheSettings.MaxAgeMs) * time.Millisecond

	// Fast path: check cache without singleflight overhead.
	rc.cacheMu.RLock()
	cachedResp, exists := rc.cache[cacheKey]
	rc.cacheMu.RUnlock()
	if exists && cachedResp.storedAt.Add(cacheMaxAge).After(time.Now()) {
		rc.metrics.IncrementCacheHitCount(ctx, rc.lggr)
		return cachedResp.response
	}
```

**File:** core/services/gateway/handlers/capabilities/v2/response_cache.go (L110-120)
```go
// Set caches a response if it is cacheable (2xx or 4xx and cache is empty or expired for the given request)
func (rc *responseCache) Set(req gateway.OutboundHTTPRequest, response gateway.OutboundHTTPResponse) {
	rc.cacheMu.Lock()
	defer rc.cacheMu.Unlock()
	if isCacheableStatusCode(response.StatusCode) && rc.isExpiredOrNotCached(req) {
		rc.cache[req.Hash()] = &cachedResponse{
			response: response,
			storedAt: time.Now(),
		}
	}
}
```

**File:** core/services/gateway/handlers/capabilities/v2/http_handler.go (L404-442)
```go
func (h *gatewayHandler) makeOutgoingRequest(ctx context.Context, resp *jsonrpc.Response[json.RawMessage], nodeAddr string) error {
	requestID := resp.ID
	h.lggr.Debugw("handling outgoing message", "requestID", requestID, "nodeAddr", nodeAddr)
	var req gateway_common.OutboundHTTPRequest
	err := json.Unmarshal(*resp.Result, &req)
	if err != nil {
		return fmt.Errorf("failed to unmarshal HTTP request from node %s: %w", nodeAddr, err)
	}
	timeout := time.Duration(req.TimeoutMs) * time.Millisecond
	httpReq := network.HTTPRequest{
		Method:           req.Method,
		URL:              req.URL,
		Headers:          req.Headers, //nolint:staticcheck // forward deprecated Headers for backward compatibility; request uses MultiHeaders when set
		MultiHeaders:     req.MultiHeaders,
		Body:             req.Body,
		MaxResponseBytes: req.MaxResponseBytes,
		Timeout:          timeout,
	}

	sendResponseTimeout := time.Duration(defaultSendResponseTimeoutMs) * time.Millisecond

	// send response to node async
	h.wg.Go(func() {
		// not cancelled when parent is cancelled to ensure the goroutine can finish
		baseCtx := context.WithoutCancel(ctx)
		httpCtx, httpCancel := context.WithTimeout(baseCtx, timeout)
		defer httpCancel()
		l := logger.With(h.lggr, "requestID", requestID, "method", req.Method, "timeout", req.TimeoutMs)
		var outboundResp gateway_common.OutboundHTTPResponse
		callback := h.createHTTPRequestCallback(httpCtx, requestID, httpReq, req)
		if req.CacheSettings.MaxAgeMs > 0 {
			h.metrics.IncrementCacheReadCount(ctx, h.lggr)
			outboundResp = h.responseCache.Fetch(httpCtx, req, callback, req.CacheSettings.Store)
		} else {
			outboundResp = callback()
			if req.CacheSettings.Store {
				h.responseCache.Set(req, outboundResp)
			}
		}
```
