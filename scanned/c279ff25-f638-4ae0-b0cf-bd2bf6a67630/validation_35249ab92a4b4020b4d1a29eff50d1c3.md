### Title
Outbound HTTP response cache key omits WorkflowID, allowing cross-workflow response confusion - (File: core/services/gateway/handlers/capabilities/v2/response_cache.go)

### Summary
The gateway's HTTP-action response cache computes its cache key via `gateway_common.OutboundHTTPRequest.Hash()`, which is documented and tested to intentionally ignore `WorkflowID` while incorporating `WorkflowOwner`. Just as the GMX report's `Keys.poolAmountAdjustmentKey()` omitted the long/short side and thus conflated two distinct logical contexts under one key, the response cache's hash omits the workflow identity field needed to fully distinguish requesting contexts, so cache entries meant for one workflow are served to another workflow that happens to share the same owner and issue an identical outbound HTTP request.

### Finding Description
`responseCache.Fetch` and `responseCache.Set` key the cache map using `req.Hash()`: [1](#0-0) [2](#0-1) 

The struct comment on `responseCache` states the hash is built from "method, URL, headers, body, workflowOwner" — notably not `WorkflowID`: [3](#0-2) 

This is explicitly confirmed by the test suite, which asserts that two requests differing only by `WorkflowID` produce the **same** hash, while requests differing by `WorkflowOwner` produce **different** hashes: [4](#0-3) [5](#0-4) 

However, the package's own design documentation states the opposite guarantee: "Cache Key: Generated from workflow ID and request hash" and "Workflow Isolation: Cache entries are scoped by workflow ID to prevent cross-workflow data leakage": [6](#0-5) 

This mirrors the GMX analog exactly: the key-construction function was built from an identity tuple that leaves out a dimension (long/short side in GMX; workflow identity here) that the surrounding logic assumes is present, so two logically distinct contexts (two different workflow executions) collapse onto one cache entry whenever the remaining fields (owner, method, URL, headers, body) coincide.

### Impact Explanation
Because the gateway's HTTP action handler stores/fetches cache entries only by this hash (`makeOutgoingRequest` → `h.responseCache.Fetch`/`Set`), any two workflows owned by the same `WorkflowOwner` that issue byte-identical outbound HTTP requests (same method, URL, headers, body) will read each other's cached HTTP responses: [7](#0-6) 

This is a cross-workflow response confusion: data or errors intended for one workflow execution (e.g., a response containing workflow-specific state, an authorization decision, or sensitive payload data returned by an external API keyed on request parameters) can be served to a different workflow under the same owner, bypassing the "workflow isolation" that the cache is documented to provide.

### Likelihood Explanation
Multiple workflows under the same owner commonly hit the same external endpoints with identical parameters (e.g., shared HTTP action templates, common price/data feeds, retried or duplicated workflow deployments). Any owner deploying more than one workflow that calls the same URL/method/body combination with caching enabled (`CacheSettings.Store` / `MaxAgeMs`) will trigger the collision without any attacker action — it is a reachable, deterministic consequence of normal usage, not requiring malicious input.

### Recommendation
Include `WorkflowID` (in addition to `WorkflowOwner`) in `OutboundHTTPRequest.Hash()` so the cache key uniquely scopes entries per workflow, matching the documented "Workflow Isolation" guarantee. Update `TestRequestHash`'s "having different workflowID results in same Hash" case to instead assert a different hash, and audit other callers/tests relying on the old (owner-only) key derivation.

### Proof of Concept
1. Create two `OutboundHTTPRequest` values with the same `Method`, `URL`, `MultiHeaders`, `Body`, and `WorkflowOwner`, but different `WorkflowID` (as in the existing test at `response_cache_test.go:139-149`).
2. Call `req1.Hash()` and `req2.Hash()` — they are equal, as asserted by the existing test.
3. Workflow A (WorkflowID=1) issues the request, `Fetch` executes `fetchFn`, and `Set`/`Fetch` stores the response under this shared key.
4. Workflow B (WorkflowID=2, same owner) issues the byte-identical request before TTL expiry; `Fetch` returns Workflow A's cached response instead of making its own HTTP call, violating workflow isolation.

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

**File:** core/services/gateway/handlers/capabilities/v2/README.md (L66-72)
```markdown

- **Cacheable Responses**: 2xx (success) and 4xx (client error) status codes.
- **Cache TTL**: Configurable, default 10 minutes
- **Cache Key**: Generated from workflow ID and request hash
- **Cache Invalidation**: Time-based expiration with periodic cleanup
- **Cache Strategy**: All cacheable responses are cached; Non-zero `CacheSettings.MaxAgeMs` determines whether to return a cached value or make a fresh request
- **Workflow Isolation**: Cache entries are scoped by workflow ID to prevent cross-workflow data leakage
```

**File:** core/services/gateway/handlers/capabilities/v2/http_handler.go (L433-442)
```go
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
