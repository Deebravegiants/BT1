Based on my analysis, this maps to a genuine cache-key confusion bug in the gateway's HTTP capability response cache — analogous to the reward-calculation bug class in that a caching/accounting key omits an identifier that should scope state to a distinct principal, causing state (here, HTTP responses) to be incorrectly shared/reused across different logical owners of that state.

### Title
Response cache key omits WorkflowID, causing cross-workflow HTTP response reuse for HTTP Action capability requests - ([File: core/services/gateway/handlers/capabilities/v2/response_cache.go])

### Summary
The gateway's HTTP Action response cache (`responseCache`) keys cached responses using `OutboundHTTPRequest.Hash()`, which intentionally excludes `WorkflowID` and only includes `WorkflowOwner`, method, URL, headers, and body. As a result, two different workflows belonging to the same owner that issue identical HTTP action requests (same method/URL/headers/body) will collide on the same cache key, and one workflow's cached HTTP response will be served to the other workflow.

### Finding Description
`responseCache` is documented as keying entries "by a hash of the request (method, URL, headers, body, workflowOwner)" [1](#0-0) . Both `Fetch` and `Set` use `req.Hash()` as the sole cache-map key to look up and store `cachedResponse` entries [2](#0-1) . The accompanying test suite explicitly documents and asserts that `WorkflowID` does not affect the hash: `"having different workflowID results in same Hash"` while only `WorkflowOwner` differentiates entries [3](#0-2) . This directly contradicts the component's own design intent stated in the README, which claims: "Workflow Isolation: Cache entries are scoped by workflow ID to prevent cross-workflow data leakage" [4](#0-3) .

The flow reaching this code is unprivileged from the gateway's perspective of a single workflow node: HTTP Action requests originating from a workflow node are dispatched through the `gatewayHandler`, which uses `responseCache.Fetch`/`Set` keyed only on `req.Hash()` before making the outbound HTTP call [5](#0-4) .

### Impact Explanation
Because `WorkflowID` is excluded from the hash, any two workflows owned by the same address that issue an HTTP Action with identical method/URL/headers/body will read/write the same cache entry. This causes cross-workflow response confusion: a workflow could receive a cached response that was originally fetched for (and possibly intended only for) a different workflow's request, even though `CacheSettings.Store`/`MaxAgeMs` per-workflow intent differs, since `CacheSettings` is also excluded from the hash [6](#0-5) . This can leak data intended for one workflow's external API call into another workflow's execution context, or cause a workflow to act on stale/foreign data, violating the workflow-isolation guarantee the gateway claims to provide.

### Likelihood Explanation
Any workflow owner running multiple workflows that call the same external endpoint with the same parameters (a common pattern, e.g. price feeds, shared APIs) will trigger this collision without any malicious intent required — it's a straightforward correctness bug reachable by ordinary unprivileged workflow/client HTTP Action usage.

### Recommendation
Include `WorkflowID` (and ideally `CacheSettings` where semantically relevant) in the cache key computed by `Hash()`/used by `responseCache`, so that cache entries are strictly scoped per workflow as the documentation promises, not just per workflow owner.

### Proof of Concept
1. Workflow A (owner `0xabc`, ID `wf-1`) issues an HTTP Action: `GET https://example.com/data` with `CacheSettings.Store = true`.
2. The gateway executes the request and caches the response under `Hash(method, URL, headers, body, workflowOwner=0xabc)` — note `WorkflowID` is not part of this hash, as verified by the test asserting equal hashes despite differing `WorkflowID` [7](#0-6) .
3. Workflow B (same owner `0xabc`, different ID `wf-2`) issues the identical `GET https://example.com/data` request with `CacheSettings.MaxAgeMs > 0`.
4. `Fetch` finds the existing cache entry (same hash) and returns Workflow A's cached response to Workflow B without making a new request [8](#0-7) , even though the two are logically distinct workflows.

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

**File:** core/services/gateway/handlers/capabilities/v2/response_cache_test.go (L121-137)
```go
	t.Run("having different cacheSettings results in the same Hash", func(t *testing.T) {
		req1 := createTestRequest("GET", "https://example.com")
		req1.CacheSettings = gateway_common.CacheSettings{
			MaxAgeMs: 5000,
			Store:    true,
		}

		req2 := createTestRequest("GET", "https://example.com")
		req2.CacheSettings = gateway_common.CacheSettings{
			MaxAgeMs: 10000,
			Store:    false,
		}

		hash1 := req1.Hash()
		hash2 := req2.Hash()
		require.Equal(t, hash1, hash2, "Hash should be the same regardless of CacheSettings")
	})
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

**File:** core/services/gateway/handlers/capabilities/v2/http_handler.go (L64-77)
```go
}

type ResponseCache interface {
	// Set caches a response if it is cacheable (2xx or 4xx status codes) and the cache is empty or expired for the given request.
	Set(req gateway_common.OutboundHTTPRequest, response gateway_common.OutboundHTTPResponse)

	// Fetch retrieves a response from the cache if it exists and the age of cached response is less than the max age of the request.
	// If the cached response is expired or not cached, it fetches a new response from the fetchFn.
	// The response is cached if it is cacheable and storeOnFetch is true.
	Fetch(ctx context.Context, req gateway_common.OutboundHTTPRequest, fetchFn func() gateway_common.OutboundHTTPResponse, storeOnFetch bool) gateway_common.OutboundHTTPResponse

	// DeleteExpired removes all cached responses that have exceeded their TTL (Time To Live).
	DeleteExpired(ctx context.Context) int
}
```
