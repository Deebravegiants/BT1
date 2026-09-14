### Title
Cross-Workflow HTTP Response Cache Poisoning/Disclosure via Workflow-ID-Agnostic Cache Key - ([File: core/services/gateway/handlers/capabilities/v2/response_cache.go])

### Summary
The Gateway's HTTP Action response cache is documented as being workflow-isolated ("Cache entries are scoped by workflow ID to prevent cross-workflow data leakage"), but the actual cache key derived from `OutboundHTTPRequest.Hash()` deliberately excludes `WorkflowID` and only incorporates `WorkflowOwner`. Any two workflows belonging to the same owner that issue an HTTP action with identical method/URL/headers/body share a single cache entry, allowing one workflow's request to populate, read, or prematurely evict the cached response used by a sibling workflow — the same class of "mishandled caching" bug as CVE-2018-19143, where cache/upload-tracking state that should be scoped per submission/session instead bled across contexts, letting an authenticated actor affect state belonging to another context.

### Finding Description
The gateway's `responseCache` keys stored HTTP responses purely by `req.Hash()`: [1](#0-0) [2](#0-1) 

The comment on the struct states the hash is computed from "method, URL, headers, body, workflowOwner" — `WorkflowID` is explicitly not part of the key: [3](#0-2) 

This is confirmed by the test suite, which explicitly asserts that differing `WorkflowID` values produce the *same* hash, while differing `WorkflowOwner` values produce different hashes: [4](#0-3) 

However, the component's own documentation claims per-workflow isolation is enforced to prevent cross-workflow leakage, which contradicts the actual implementation: [5](#0-4) 

Because `HandleJSONRPCUserMessage`/`makeOutgoingRequest` dispatches per-workflow `OutboundHTTPRequest`s (originating from workflow node HTTP action capability calls) directly into this shared cache using only `req.Hash()`: [6](#0-5) 

any workflow owned by the same account can:
- Read a cached HTTP response that was fetched and stored on behalf of a different workflow (cross-workflow response disclosure), if it issues a request with the identical hash inputs and sets `MaxAgeMs` > 0.
- Overwrite/poison the shared cache entry for another workflow by calling `Set`/`Fetch` with `Store=true`, causing the other workflow to receive attacker-influenced or stale cached data on its next fetch.
- Force premature eviction of another workflow's cached entry by driving `isExpiredOrNotCached`/`DeleteExpired` logic against the shared key, since TTL bookkeepping (`storedAt`) is also per-hash, not per-workflow.

### Impact Explanation
This is a cross-workflow response confusion bug reachable purely through the internet-facing gateway's message handling path (unprivileged/low-privileged workflow request into the shared `responseCache`), matching the "cross-user response confusion" and "cache" analog categories explicitly in scope. A workflow can consume or corrupt cached HTTP action results belonging to another workflow under the same owner, undermining the confidentiality/integrity guarantees the caching layer is documented to provide.

### Likelihood Explanation
Any workflow author who can deploy two workflows under the same owner (a normal, low-privilege operation) and control the HTTP action's method/URL/headers/body/`CacheSettings` can trivially construct a colliding request. No special network position or elevated permissions are required — only the ability to submit workflow HTTP action requests through the existing gateway path.

### Recommendation
Include `WorkflowID` (not just `WorkflowOwner`) as part of the cache key in `OutboundHTTPRequest.Hash()` (or otherwise scope the `responseCache` map by workflow ID as the README already claims), and update/align the documentation and tests accordingly so that cache entries cannot be shared, read, or invalidated across different workflows.

### Proof of Concept
1. Deploy Workflow A and Workflow B under the same `WorkflowOwner`.
2. From Workflow A, issue an `OutboundHTTPRequest` to `https://victim.example/api` with `CacheSettings.Store = true`, `MaxAgeMs = 600000`. The gateway calls `h.responseCache.Set(req, outboundResp)` keyed by `req.Hash()` (method+URL+headers+body+owner only).
3. From Workflow B, issue an identical `OutboundHTTPRequest` (same method/URL/headers/body) with `CacheSettings.MaxAgeMs > 0`. Because `Hash()` ignores `WorkflowID`, `responseCache.Fetch` returns Workflow A's cached response to Workflow B without ever contacting the external endpoint — demonstrated directly by `TestRequestHash`'s "having different workflowID results in same Hash" assertion at `response_cache_test.go:139-149`.

### Citations

**File:** core/services/gateway/handlers/capabilities/v2/response_cache.go (L15-24)
```go
// responseCache is a thread-safe cache for storing HTTP responses.
// It uses a map to store responses keyed by a hash of the request (method, URL, headers, body, workflowOwner).
type responseCache struct {
	cacheMu sync.RWMutex
	cache   map[string]*cachedResponse
	flight  singleflight.Group
	lggr    logger.Logger
	ttl     time.Duration
	metrics *metrics.Metrics
}
```

**File:** core/services/gateway/handlers/capabilities/v2/response_cache.go (L46-54)
```go
// isExpiredOrNotCached returns true if the cached response is expired or not cached.
// IMPORTANT: this method does not lock the cache map. MUST be called with cacheMu write-locked.
func (rc *responseCache) isExpiredOrNotCached(req gateway.OutboundHTTPRequest) bool {
	cachedResp, exists := rc.cache[req.Hash()]
	if !exists || time.Now().After(cachedResp.storedAt.Add(rc.ttl)) {
		return true
	}
	return false
}
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

**File:** core/services/gateway/handlers/capabilities/v2/response_cache_test.go (L139-175)
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

	t.Run("having same workflowOwner results in the same Hash", func(t *testing.T) {
		req1 := createTestRequest("GET", "https://example.com")
		req1.WorkflowOwner = "workflow-owner-123"

		req2 := createTestRequest("GET", "https://example.com")
		req2.WorkflowOwner = "workflow-owner-123"

		hash1 := req1.Hash()
		hash2 := req2.Hash()
		require.Equal(t, hash1, hash2, "Hash should be the same for identical requests")
	})

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
