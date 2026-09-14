### Title
Cross-Workflow Response Cache Confusion in Gateway HTTP Action Handler - ([File: core/services/gateway/handlers/capabilities/v2/response_cache.go])

### Summary
The gateway's outbound HTTP Action response cache keys entries by `OutboundHTTPRequest.Hash()`, which is documented and intended to scope cache entries by `workflowID` to prevent cross-workflow data leakage, but the actual `Hash()` implementation only incorporates `WorkflowOwner` (not `WorkflowID`). Two different workflows belonging to the same owner that issue an identical outbound HTTP request (same method/URL/headers/body) will collide on the same cache key and can receive each other's cached response — including status code and response body.

### Finding Description
The `README.md` for the HTTP Handlers V2 gateway component explicitly documents the intended security property: [1](#0-0) 

The `responseCache` implementation states it keys by "(method, URL, headers, body, workflowOwner)": [2](#0-1) 

The unit test explicitly confirms `WorkflowID` is *not* part of the hash, while `WorkflowOwner` is: [3](#0-2) 

Both `Fetch` and `Set` key exclusively on `req.Hash()`: [4](#0-3) 

Because `WorkflowID` is excluded from the cache key, any two workflows sharing the same `WorkflowOwner` (a very common scenario — a single customer typically owns many workflows) that make outbound HTTP Action requests with identical method/URL/headers/body will read and write the same cache slot. This directly contradicts the documented "Workflow Isolation" guarantee and results in cross-workflow response confusion: workflow A's action response can be served to workflow B (and vice-versa) as long as both requests hash identically under the current key derivation.

### Impact Explanation
This is a genuine cross-workflow data confusion bug: a workflow can receive HTTP action response data that was fetched/cached on behalf of a different workflow under the same owner. Depending on the outbound request semantics (e.g., an endpoint that returns workflow-specific data based on server-side session/state despite an identical client-visible request, or a request whose result is sensitive but not distinguishable at the HTTP layer from another workflow's), this can leak one workflow's action-capability data into another workflow's execution, undermining the "Workflow Isolation" property the component explicitly claims to enforce. It also creates a caching correctness/poisoning issue: a stale or wrong response served to workflow B due to workflow A's caching parameters (TTL windows are shared, though `CacheSettings` intentionally do not affect the hash) can silently corrupt downstream workflow logic.

### Likelihood Explanation
Likelihood is moderate: it does not require an attacker or malicious node — it can occur organically any time a tenant/owner runs multiple workflows that call the same external HTTP endpoint with the same static request shape. Because caching (`CacheSettings.Store`/`MaxAgeMs`) is opt-in per request and the TTL defaults to 10 minutes, the collision window is real but bounded, and requires the request bodies/headers to match exactly across workflows (which is plausible for simple GET/read endpoints reused across a tenant's automations).

### Recommendation
Include `WorkflowID` (or, at minimum, workflow execution context sufficient to prevent cross-workflow reuse) in `OutboundHTTPRequest.Hash()` so cache entries are truly workflow-scoped as documented, not merely owner-scoped. Update `response_cache_test.go`'s `TestRequestHash` expectations accordingly, and audit the README to match the corrected behavior.

### Proof of Concept
1. Workflow A (owner `0xOwner`, workflow ID `wf-A`) issues an `OutboundHTTPRequest{Method: GET, URL: "https://api.example.com/data", CacheSettings:{Store:true}}`.
2. The gateway executes the HTTP call, caches the response under a hash computed from `(method, URL, headers, body, workflowOwner=0xOwner)` — `WorkflowID` is not part of the key, as demonstrated by `TestRequestHash`'s `"having different workflowID results in same Hash"` subtest.
3. Workflow B (same owner `0xOwner`, different workflow ID `wf-B`) issues the identical `OutboundHTTPRequest{Method: GET, URL: "https://api.example.com/data"}` with `CacheSettings.MaxAgeMs > 0`.
4. `responseCache.Fetch` computes the same cache key and returns workflow A's cached response to workflow B, even though the two are logically distinct workflows. [5](#0-4)

### Citations

**File:** core/services/gateway/handlers/capabilities/v2/README.md (L69-72)
```markdown
- **Cache Key**: Generated from workflow ID and request hash
- **Cache Invalidation**: Time-based expiration with periodic cleanup
- **Cache Strategy**: All cacheable responses are cached; Non-zero `CacheSettings.MaxAgeMs` determines whether to return a cached value or make a fresh request
- **Workflow Isolation**: Cache entries are scoped by workflow ID to prevent cross-workflow data leakage
```

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

**File:** core/services/gateway/handlers/capabilities/v2/response_cache.go (L66-120)
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
