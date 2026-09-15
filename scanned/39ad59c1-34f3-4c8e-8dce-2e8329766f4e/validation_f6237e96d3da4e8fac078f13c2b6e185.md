Based on the evidence gathered, I found a concrete analog: the gateway's HTTP action response cache key omits the field intended to scope cache isolation, causing cross-workflow response sharing — analogous to the Ajna bug where a hash that should uniquely bind an entity omits/mangles the actual identity data, causing distinct logical entities to collide.

### Title
Outbound HTTP response cache key omits WorkflowID, allowing cross-workflow response cache poisoning/leakage - (File: core/services/gateway/handlers/capabilities/v2/response_cache.go)

### Summary
The gateway's `responseCache` for outbound HTTP actions keys cached responses solely by `req.Hash()` [1](#0-0) , and the accompanying test explicitly demonstrates that two requests with different `WorkflowID` values produce the *same* hash: `require.Equal(t, hash1, hash2, "Hash should be the same regardless of WorkflowID")` [2](#0-1) . This contradicts the documented design intent stated in the handler's own README: "Workflow Isolation: Cache entries are scoped by workflow ID to prevent cross-workflow data leakage" [3](#0-2) .

### Finding Description
The `Fetch` and `Set` methods on `responseCache` use `req.Hash()` as the sole cache map key [4](#0-3) [5](#0-4) . The struct's doc comment claims the hash is derived from "method, URL, headers, body, workflowOwner" [6](#0-5) , and workflowOwner differences do change the hash per the test suite, but `WorkflowID` differences do not [7](#0-6) . Since `WorkflowID` is not part of the hash, two different workflows belonging to the same owner (or any two requests whose hash inputs collide by design, e.g. identical method/URL/headers/body issued under the same owner but different workflows) will resolve to the same cache entry. The `req` used to compute the hash and drive routing comes directly from an untrusted `OutboundHTTPRequest` payload unmarshalled from a node message on the internet-facing gateway [8](#0-7) . This is the same root-cause pattern as the ERC721 pool factory bug: the identity-binding hash function does not actually capture the full scope-defining field it's supposed to, allowing distinct logical namespaces (workflows) to unintentionally collapse into one bucket.

### Impact Explanation
A workflow can retrieve or "poison" the cached outbound HTTP response of a different workflow under the same owner if their requests hash identically (same method/URL/headers/body), even though the README explicitly promises workflow-scoped isolation to prevent cross-workflow data leakage. This is a cross-user/cross-workflow response confusion: one workflow's cached response (which may include response bodies, headers, or sensitive endpoint data) can be served to another workflow, or a malicious workflow node can pre-populate the cache to feed stale/attacker-influenced data to a different workflow that later issues an identical request pattern.

### Likelihood Explanation
Requires two workflows with the same owner (or two workflows that happen to have hash-input collisions) issuing outbound HTTP requests with identical method/URL/headers/body and caching enabled (`CacheSettings.Store`/`MaxAgeMs` set) — a plausible scenario given multiple workflows commonly querying the same external API endpoint. No special privilege beyond normal workflow node access is required to trigger it.

### Recommendation
Include `WorkflowID` (not just `WorkflowOwner`) as part of the `OutboundHTTPRequest.Hash()` input, or otherwise namespace the cache key by `WorkflowID` before using it in `responseCache.Fetch`/`Set`, so that responses are only ever shared within the same workflow, matching the documented isolation guarantee.

### Proof of Concept
1. Workflow A (owner X) issues an `OutboundHTTPRequest{Method: "GET", URL: "https://api.example.com/data", CacheSettings:{Store:true, MaxAgeMs: 600000}}`; gateway caches the response keyed by `req.Hash()`.
2. Workflow B (same owner X, different WorkflowID) issues an identical `OutboundHTTPRequest` (same method/URL/headers/body) with caching enabled.
3. Per `TestRequestHash`'s "having different workflowID results in same Hash" assertion [2](#0-1) , Workflow B's request computes the identical cache key as Workflow A's, so `responseCache.Fetch` returns Workflow A's cached response to Workflow B without making a new HTTP call, violating the intended workflow isolation.

### Citations

**File:** core/services/gateway/handlers/capabilities/v2/response_cache.go (L15-17)
```go
// responseCache is a thread-safe cache for storing HTTP responses.
// It uses a map to store responses keyed by a hash of the request (method, URL, headers, body, workflowOwner).
type responseCache struct {
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

**File:** core/services/gateway/handlers/capabilities/v2/README.md (L69-72)
```markdown
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
