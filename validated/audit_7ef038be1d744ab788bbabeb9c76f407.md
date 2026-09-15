### Title
Cross-workflow response cache confusion via workflow-owner-scoped-only cache key - (File: core/services/gateway/handlers/capabilities/v2/response_cache.go)

### Summary
The gateway's HTTP-action `responseCache` caches outbound HTTP responses under `req.Hash()`, a key that the codebase's own test suite documents as *not* including `WorkflowID`, only `WorkflowOwner` (plus method/URL/headers/body). Any workflow owned by the same address that issues an HTTP action with an identical method/URL/headers/body will read another workflow's cached response instead of executing its own request, similar in spirit to the reported bug: an artifact produced under one context (a private upload / one workflow's request) becomes retrievable by another, unrelated context with no way for the original owner to scope or invalidate it per-consumer.

### Finding Description
`responseCache.Fetch` and `responseCache.Set` key the cache purely off `gateway.OutboundHTTPRequest.Hash()`: [1](#0-0) [2](#0-1) 

The struct's own comment states the hash is built from "method, URL, headers, body, workflowOwner": [3](#0-2) 

The package's own test suite proves `WorkflowID` is excluded from the hash while `WorkflowOwner` is included: [4](#0-3) 

This directly contradicts the documented design intent in the handler's README, which claims cache entries are scoped by workflow ID specifically to prevent cross-workflow data leakage: [5](#0-4) 

Because the cache key omits `WorkflowID`, any two different workflows registered under the same `WorkflowOwner` address (a common, unprivileged, low-barrier condition — one EOA can own many workflows) that issue an HTTP action with the same method/URL/headers/body will collide on the same cache entry in `makeOutgoingRequest`: [6](#0-5) 

The first workflow to populate the cache "wins"; every other workflow sharing that owner and request shape silently receives the first workflow's previously fetched response for up to `CacheSettings.MaxAgeMs` (attacker-controlled, default up to 10 minutes per the README), rather than executing its own independent request.

### Impact Explanation
This is a cross-user/cross-execution response confusion bug reachable purely from unprivileged workflow-authoring: an actor who controls (or later re-deploys) multiple workflows under one owner address can have one workflow's HTTP action response leak into a sibling workflow's execution context whenever the request shape (method/URL/headers/body) coincides — including staler, poisoned, or attacker-influenced responses being replayed into an unrelated workflow's decision logic. Because chainlink workflows can drive fund movement or job execution based on external data fetched via HTTP actions, silently substituting one workflow's cached response for another's is a genuine data-integrity/isolation break, analogous to the reported bug where one context's generated artifact became uncontrollably shared/exposed to another context. Severity is bounded by the requirement that both workflows share the same `WorkflowOwner` and issue identical request parameters, and by the cache TTL window.

### Likelihood Explanation
Reaching this requires no privileged access — only the ability to register/operate more than one workflow under the same owner address (or two callers coincidentally sharing owner identity and hitting the same external endpoint with identical parameters within the TTL window), which is a normal, permission-free workflow-authoring action. The comment block and dedicated test (`"having different workflowID results in same Hash"`) confirm this is the actual, verified runtime behavior rather than a hypothetical.

### Recommendation
Include `WorkflowID` (and ideally `ExecutionID`/`ReferenceID` if per-execution isolation is desired) in the cache key computed by `OutboundHTTPRequest.Hash()`, or explicitly namespace the `responseCache` map by `WorkflowID` in addition to the request hash, so that the implementation matches the documented "workflow-scoped caching" guarantee in the README.

### Proof of Concept
1. Register two workflows, `wfA` and `wfB`, both owned by the same `WorkflowOwner` address.
2. `wfA` issues an HTTP action: `GET https://example.com/api` with `CacheSettings.Store=true`.
3. Gateway executes the real request, caches the response keyed by `Hash()` (owner+method+url+headers+body, no `WorkflowID`), as shown in `TestFetch`/`TestRequestHash`: [7](#0-6) 
4. `wfB` issues the identical `GET https://example.com/api` HTTP action within `MaxAgeMs`.
5. `wfB` receives `wfA`'s previously cached response without the gateway ever executing `wfB`'s own request — verified by the test's explicit assertion that identical `WorkflowOwner` but differing `WorkflowID` produce the *same* hash: [8](#0-7)

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

**File:** core/services/gateway/handlers/capabilities/v2/response_cache.go (L66-108)
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

	// Slow path: singleflight deduplicates concurrent fetches per key.
	// Cache check + store happen inside the flight so the key isn't released
	// until the result is cached, closing the race window between singleflight
	// completion and cache write.
	result, _, _ := rc.flight.Do(cacheKey, func() (any, error) {
		// Re-check cache: a previous flight may have just stored the result.
		rc.cacheMu.RLock()
		cachedResp, exists := rc.cache[cacheKey]
		rc.cacheMu.RUnlock()
		if exists && cachedResp.storedAt.Add(cacheMaxAge).After(time.Now()) {
			rc.metrics.IncrementCacheHitCount(ctx, rc.lggr)
			return cachedResp.response, nil
		}

		response := fetchFn()

		if storeOnFetch && isCacheableStatusCode(response.StatusCode) {
			rc.cacheMu.Lock()
			rc.cache[cacheKey] = &cachedResponse{
				response: response,
				storedAt: time.Now(),
			}
			rc.cacheMu.Unlock()
		}

		return response, nil
	})

	return result.(gateway.OutboundHTTPResponse)
}
```

**File:** core/services/gateway/handlers/capabilities/v2/response_cache_test.go (L139-176)
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
}
```

**File:** core/services/gateway/handlers/capabilities/v2/response_cache_test.go (L210-228)
```go
func TestFetch(t *testing.T) {
	testMetrics := createCacheTestMetrics(t)
	cache := newResponseCache(logger.Test(t), 10000, testMetrics) // 10 seconds TTL

	t.Run("calls fetchFn when cache miss", func(t *testing.T) {
		req := createTestRequest("GET", "https://example.com/miss")
		expectedResp := createTestResponse(200, "fresh data")

		var fetchCalled bool
		fetchFn := func() gateway_common.OutboundHTTPResponse {
			fetchCalled = true
			return expectedResp
		}

		result := cache.Fetch(t.Context(), req, fetchFn, true)

		require.True(t, fetchCalled)
		require.Equal(t, expectedResp, result)
	})
```

**File:** core/services/gateway/handlers/capabilities/v2/README.md (L65-73)
```markdown
### 3.2 Caching Behavior

- **Cacheable Responses**: 2xx (success) and 4xx (client error) status codes.
- **Cache TTL**: Configurable, default 10 minutes
- **Cache Key**: Generated from workflow ID and request hash
- **Cache Invalidation**: Time-based expiration with periodic cleanup
- **Cache Strategy**: All cacheable responses are cached; Non-zero `CacheSettings.MaxAgeMs` determines whether to return a cached value or make a fresh request
- **Workflow Isolation**: Cache entries are scoped by workflow ID to prevent cross-workflow data leakage
---
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
