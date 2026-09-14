## Title
HTTP Action response cache key omits `WorkflowID`, causing cross-workflow response confusion despite documented "workflow isolation" — (`core/services/gateway/handlers/capabilities/v2/response_cache.go`)

### Summary
The gateway's HTTP Action response cache is documented to isolate cached responses per workflow ("Cache Key: Generated from workflow ID and request hash" / "Workflow Isolation: Cache entries are scoped by workflow ID to prevent cross-workflow data leakage"), but the actual cache key hash function deliberately excludes `WorkflowID` and only includes method, URL, headers, body, and `WorkflowOwner`. As a result, two different workflows belonging to the same owner that issue functionally identical outbound HTTP requests will silently share the same cache entry, so one workflow can receive another workflow's cached response instead of the response it actually requested/expected — the same root-cause pattern as the referenced report, where a user pays for/requests one specific outcome but silently receives a different, unexpected one due to a missing identity/state check on a keyed lookup.

### Finding Description
The cache is keyed by `req.Hash()`, and per its own doc comment and test suite, that hash intentionally omits `WorkflowID`: [1](#0-0) [2](#0-1) 

The `Fetch`/`Set` methods use this hash as the sole cache key: [3](#0-2) [4](#0-3) 

The test suite explicitly documents and asserts that different `WorkflowID`s hash identically, while different `WorkflowOwner`s hash differently: [5](#0-4) 

Yet the package's own README claims the opposite guarantee — that the cache key includes workflow ID and isolates entries per workflow: [6](#0-5) 

The cache is consulted directly from the node message handling path (`makeOutgoingRequest`), which is reachable from unprivileged HTTP Action capability requests originating from workflow nodes: [7](#0-6) 

This is directly analogous to the Canto `Tray.buy()` bug: a caller expects a specific, freshly-computed outcome tied to their own identity/state, but the system's keyed lookup does not include the field needed to preserve that identity boundary (there, the last-minted hash; here, `WorkflowID`), so the caller can silently receive a different result than the one their request logically corresponds to — with no error/reject to signal the mismatch.

### Impact Explanation
Because `WorkflowID` is excluded from the cache key, any two workflows owned by the same workflow owner that hit the same URL/method/body/headers will collide in the cache. A workflow that intends a fresh fetch (or expects data scoped to its own execution context) can be served another workflow's previously cached response transparently, with `Fetch` returning the cached value without invoking the requesting workflow's own `fetchFn` at all when a fresh-enough entry exists. This breaks the documented workflow-isolation guarantee and can lead a workflow to act on stale/foreign data (e.g., business logic keyed to workflow identity in headers/body being masked, or one workflow's action polluting another's cache with different freshness expectations), which the code's own `CacheSettings.MaxAgeMs`/`Store` toggles imply developers rely on for correctness.

### Likelihood Explanation
This requires no attacker interaction and no privilege escalation — it triggers under ordinary operation whenever a single workflow owner runs multiple workflows that call the same external endpoint with matching request shape (a common pattern, e.g., shared utility endpoints), making it a normal-usage collision rather than a contrived edge case.

### Recommendation
Include `WorkflowID` in the cache key hash (`OutboundHTTPRequest.Hash()`) as the README already documents, or otherwise namespace `responseCache.cache` by `WorkflowID` in addition to the existing request/owner fields, so cache entries cannot cross workflow boundaries, matching the stated "Workflow Isolation" guarantee.

### Proof of Concept
1. Workflow A (owner `X`) issues an `OutboundHTTPRequest{Method: GET, URL: u, Body: b, WorkflowOwner: X, WorkflowID: "wf-A", CacheSettings:{MaxAgeMs>0, Store:true}}`; the gateway fetches and caches the response under `req.Hash()` (per `response_cache.go` `Hash` excludes `WorkflowID`).
2. Workflow B (same owner `X`, different `WorkflowID: "wf-B"`) issues an otherwise-identical `OutboundHTTPRequest` with the same method/URL/headers/body and `MaxAgeMs>0`.
3. Per `TestFetch`'s "returns cached response when cache hit" behavior (`response_cache_test.go` lines 230-250) and the `TestRequestHash` assertion that differing `WorkflowID` yields the same hash (lines 139-149), Workflow B's `Fetch` call returns Workflow A's cached response without invoking its own `fetchFn`, i.e., Workflow B receives a response it never actually requested from the origin server. [8](#0-7)

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

**File:** core/services/gateway/handlers/capabilities/v2/response_cache.go (L66-105)
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

**File:** core/services/gateway/handlers/capabilities/v2/response_cache_test.go (L230-250)
```go
	t.Run("returns cached response when cache hit", func(t *testing.T) {
		req := createTestRequest("GET", "https://example.com/hit")
		cachedResp := createTestResponse(200, "cached data")

		// Pre-populate cache
		cache.cache[req.Hash()] = &cachedResponse{
			response: cachedResp,
			storedAt: time.Now(),
		}

		var fetchCalled bool
		fetchFn := func() gateway_common.OutboundHTTPResponse {
			fetchCalled = true
			return createTestResponse(200, "should not be called")
		}

		result := cache.Fetch(t.Context(), req, fetchFn, true)

		require.False(t, fetchCalled, "fetchFn should not be called on cache hit")
		require.Equal(t, cachedResp, result)
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

**File:** core/services/gateway/handlers/capabilities/v2/http_handler.go (L432-442)
```go
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
