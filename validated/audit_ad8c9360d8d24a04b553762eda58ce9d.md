Audit Report

## Title
HTTP Action response cache key omits `WorkflowID`, allowing cross-workflow response confusion within the same workflow owner — (`core/services/gateway/handlers/capabilities/v2/response_cache.go`)

## Summary
The gateway's HTTP Action response cache (`responseCache`) keys cached entries solely by `req.Hash()`, and the request hash intentionally excludes `WorkflowID`, including only method, URL, headers, body, and `WorkflowOwner`. This contradicts the package's own `README.md`, which documents that the "Cache Key" is "Generated from workflow ID and request hash" and that cache entries are "scoped by workflow ID to prevent cross-workflow data leakage."

## Finding Description
`responseCache.Fetch` and `responseCache.Set` both use `req.Hash()` as the sole cache key: [1](#0-0) [2](#0-1) 

The struct's own doc comment states the key is derived from "method, URL, headers, body, workflowOwner" — `workflowID` is not mentioned: [3](#0-2) 

This is confirmed by the test suite, which explicitly asserts that requests with different `WorkflowID`s produce the *same* hash, while requests with different `WorkflowOwner`s produce *different* hashes: [4](#0-3) [5](#0-4) 

Meanwhile the `README.md` for this exact package documents the opposite behavior, claiming workflow-level isolation: [6](#0-5) 

The cache is invoked from the ordinary HTTP Action request-handling path (`req.CacheSettings.MaxAgeMs > 0` → `Fetch`), which is reachable by any workflow node issuing an outbound HTTP Action capability request through the gateway: [7](#0-6)  There is no additional authorization or workflow-identity check performed before the cache lookup that would compensate for the missing `WorkflowID` in the key — the only isolation dimension enforced is `WorkflowOwner`.

## Impact Explanation
Since `WorkflowID` is excluded from the cache key, two distinct workflows belonging to the same `WorkflowOwner` that issue a request with the same method/URL/headers/body and `CacheSettings.MaxAgeMs > 0` will collide on the same cache entry. `TestFetch`'s "returns cached response when cache hit" test demonstrates that on a cache hit, `fetchFn` (the actual outbound HTTP call) is never invoked and the previously cached response is returned instead: [8](#0-7)  This means a workflow can receive another workflow's previously fetched/cached HTTP response transparently, violating the documented workflow-isolation guarantee and potentially causing a workflow to act on data it never actually requested. This maps to a cross-user/cross-workflow response corruption impact class.

## Likelihood Explanation
No attacker interaction, privilege escalation, or unusual configuration is required — this triggers under ordinary multi-workflow usage whenever one owner runs two or more workflows that call the same external endpoint with a matching request shape (e.g., a shared utility/API endpoint), which is a realistic and common pattern for CRE workflows.

## Recommendation
Include `WorkflowID` in the `OutboundHTTPRequest.Hash()` computation (in the `chainlink-common` `gateway` package) as already documented in the README, or otherwise namespace `responseCache.cache` by `WorkflowID` in addition to the existing request fields, so cache entries cannot cross workflow boundaries.

## Proof of Concept
1. Run `TestRequestHash`'s "having different workflowID results in same Hash" subtest in `core/services/gateway/handlers/capabilities/v2/response_cache_test.go` (lines 139-149) — it passes today, confirming `Hash()` ignores `WorkflowID`.
2. Construct two `gateway.OutboundHTTPRequest`s with identical `Method`, `URL`, `Headers`, `Body`, `WorkflowOwner`, but distinct `WorkflowID`s ("wf-A", "wf-B"), both with `CacheSettings.MaxAgeMs > 0`.
3. Call `responseCache.Fetch` for wf-A with a `fetchFn` returning response R1 (gets cached).
4. Call `responseCache.Fetch` for wf-B with a `fetchFn` that would return response R2 but asserts it is never invoked — per `TestFetch`'s cache-hit behavior, wf-B receives R1 instead of invoking its own fetch, demonstrating cross-workflow response leakage.

### Citations

**File:** core/services/gateway/handlers/capabilities/v2/response_cache.go (L15-17)
```go
// responseCache is a thread-safe cache for storing HTTP responses.
// It uses a map to store responses keyed by a hash of the request (method, URL, headers, body, workflowOwner).
type responseCache struct {
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
