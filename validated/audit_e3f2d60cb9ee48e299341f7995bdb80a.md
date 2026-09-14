This is a confirmed cross-user cache confusion bug rather than the Vault-style "unbounded accumulator" pattern, but it maps to the same root-cause family required by the rules (unauthorized quota/allowlist/isolation bypass in the internet-facing gateway's response cache).

### Title
Outbound HTTP response cache key omits `WorkflowID`, causing cross-workflow response leakage within a shared owner - (File: core/services/gateway/handlers/capabilities/v2/response_cache.go)

### Summary
The gateway's `responseCache` used for HTTP Action caching is documented as being workflow-scoped ("Cache Key: Generated from workflow ID and request hash", "Workflow Isolation: Cache entries are scoped by workflow ID to prevent cross-workflow data leakage") [1](#0-0) , but the actual cache key, `req.Hash()`, is computed from method/URL/headers/body/workflowOwner only and explicitly does **not** vary with `WorkflowID` [2](#0-1) .

### Finding Description
The cache stores and looks up entries purely by `req.Hash()` in both `Fetch` and `Set` [3](#0-2) . A unit test explicitly documents and locks in this behavior: identical requests from two different `WorkflowID`s produce the *same* hash ("Hash should be the same regardless of WorkflowID"), while different `WorkflowOwner`s do produce different hashes [4](#0-3) . This means any two distinct workflows belonging to the same owner (or, if `WorkflowOwner` is ever unset/blank/attacker-influenced upstream, distinct owners) that issue an HTTP Action with the same method/URL/headers/body will read and write the same cache entry via `makeOutgoingRequest` → `responseCache.Fetch`/`Set` [5](#0-4) . This directly contradicts the documented workflow-isolation guarantee and creates a discrepancy between the intended per-workflow cache partitioning and the actual per-owner (only) partitioning enforced by the code.

### Impact Explanation
Because the cache key does not include `WorkflowID`, a workflow can receive a cached HTTP response that was fetched and stored on behalf of a *different* workflow under the same owner (e.g., different secrets/templated headers producing the same URL/body, or a legitimately shared static endpoint whose response should be scoped separately) — a cross-workflow response confusion. This is analogous to the `amount_claimable_per_share` finding: a value intended to be attributed/reset per logical unit (per-token-position in Vault.vy; per-workflow here) is instead accumulated/shared at a coarser granularity than intended, letting one caller consume/observe state meant for another. The severity is bounded by the fact that partitioning by `WorkflowOwner` is still enforced, so it is not a full unauthenticated cross-tenant leak, but it is a genuine violation of the documented workflow-level isolation guarantee for the internet-facing HTTP Action cache.

### Likelihood Explanation
Any workflow owner running multiple workflows that call the same external URL/method/headers/body (a common pattern, e.g., polling a shared public API) will trigger this by default, with `CacheSettings.Store`/`MaxAgeMs` enabled — no privileged access or malicious intent required, only two workflows under one owner making cache-eligible requests that hash identically.

### Recommendation
Include `WorkflowID` (or `WorkflowExecutionID`, depending on desired granularity) in the fields hashed by `req.Hash()` so that cache entries are correctly partitioned per workflow as documented, and update/re-verify the `TestRequestHash` cases that currently assert workflow-ID-independence.

### Proof of Concept
1. Workflow A (owner `O`) issues an `OutboundHTTPRequest{Method:"GET", URL:"https://api.example.com/data", WorkflowOwner:"O", WorkflowID:"wfA", CacheSettings:{Store:true, MaxAgeMs: 600000}}`; the gateway calls `h.responseCache.Fetch(...)`, fetches from the real endpoint, and stores the response under `req.Hash()` [6](#0-5) .
2. Workflow B (same owner `O`, different `WorkflowID:"wfB"`) issues an identical `Method`/`URL`/headers/body request with `CacheSettings.MaxAgeMs>0`.
3. Because `req.Hash()` ignores `WorkflowID` [7](#0-6) , `Fetch` returns Workflow A's cached response to Workflow B without ever calling the external endpoint, violating the documented per-workflow isolation.

### Citations

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

**File:** core/services/gateway/handlers/capabilities/v2/http_handler.go (L426-442)
```go
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
