### Title
Cross-workflow HTTP action response cache confusion due to Hash() omitting WorkflowID - ([File: core/services/gateway/handlers/capabilities/v2/response_cache.go])

### Summary
The gateway's outbound HTTP action response cache keys entries by `gateway_common.OutboundHTTPRequest.Hash()`, which is documented and tested to include method, URL, headers, body, and `WorkflowOwner`, but explicitly **excludes** `WorkflowID`. Two different workflows belonging to the same `WorkflowOwner` that issue an HTTP action with the same method/URL/headers/body will collide on the same cache key, so one workflow's cached HTTP response can be served to a completely different workflow. This directly mirrors the CVE-2026-60023 pattern: a read/cache path that authorizes/scopes at a coarser identity (owner) while failing to check the specific resource identity (workflow), exposing content that should not be accessible to the requesting context.

### Finding Description
The response cache is documented as workflow-scoped: the package README states "Cache Key: Generated from workflow ID and request hash" and "Workflow Isolation: Cache entries are scoped by workflow ID to prevent cross-workflow data leakage" [1](#0-0) .

However, the actual implementation in `responseCache` uses only `req.Hash()` as the cache key for both `Fetch` and `Set`, with no `WorkflowID` component at all: [2](#0-1) [3](#0-2) [4](#0-3) 

This is called from the gateway's `makeOutgoingRequest`, which stores/fetches based solely on the untrusted `OutboundHTTPRequest` fields sent by a node, and delivers whatever is returned back to that node as the workflow's action result: [5](#0-4) 

The test suite confirms the cache-key design gap explicitly: hashes are equal despite different `WorkflowID` values, and only differ when `WorkflowOwner` differs: [6](#0-5) 

Because `WorkflowID` is not part of the key, any two workflows sharing the same `WorkflowOwner` (a very common case — a single user/org typically deploys multiple workflows under one owner address) that issue an outbound HTTP action with an identical method+URL+headers+body will read/write the same cache slot. This breaks the intended workflow-level isolation that the README describes and that a Byzantine-safe multi-tenant gateway is expected to enforce.

### Impact Explanation
A workflow's cached HTTP action response (which may contain secrets, tokens, PII, or business-sensitive data returned by the external endpoint) can be delivered to a different, unrelated workflow under the same owner simply by crafting/matching the outbound request shape. This is a cross-workflow (cross-tenant, from the DON's perspective) response confusion, matching the CVE's "unauthorized disclosure" bug class where content intended for one context leaks through a shared read/cache path that checks a coarser scope (owner) instead of the specific resource (workflow). Even though the immediate reader is a DON member node rather than an external HTTP client, the gateway is the internet-facing/multi-tenant trust boundary here, and this cache is explicitly in the class of "internet-facing gateway ... handlers/caches" called out as in-scope.

### Likelihood Explanation
Exploitation does not require any privileged action or protocol violation — it only requires two workflows under the same owner to make an HTTP action call with an equal method/URL/headers/body (e.g., both calling the same public API endpoint with the same static headers), which is a routine occurrence for legitimate workflows (not an attacker-crafted edge case). No authentication bypass or malicious-node behavior is needed; it is a natural consequence of the cache-key design as demonstrated by the project's own unit tests.

### Recommendation
Include `WorkflowID` (not just `WorkflowOwner`) in the cache key computed by `OutboundHTTPRequest.Hash()`, or otherwise namespace `responseCache`'s map by `WorkflowID` in addition to the request hash, so cached responses are strictly scoped per-workflow as the README already claims. Add a regression test asserting that identical requests from different `WorkflowID`s (even under the same `WorkflowOwner`) produce distinct cache entries/hashes.

### Proof of Concept
1. Workflow A (`WorkflowID = "wf-A"`, `WorkflowOwner = "0xOwner"`) issues an `HTTPAction` with `CacheSettings.Store = true`, `Method = GET`, `URL = https://api.example.com/data`, no distinguishing headers/body. The gateway calls `responseCache.Set(req, resp)` keyed by `req.Hash()` (method+url+headers+body+owner), caching Workflow A's response (which may include Workflow-A-specific secret data returned by the endpoint based on prior state).
2. Workflow B (`WorkflowID = "wf-B"`, same `WorkflowOwner = "0xOwner"`) issues an outbound HTTP action with the same `Method`, `URL`, headers, and body, and `CacheSettings.MaxAgeMs > 0`.
3. In `makeOutgoingRequest`, since `CacheSettings.MaxAgeMs > 0`, the gateway calls `responseCache.Fetch(ctx, req, callback, ...)`, which computes the same `req.Hash()` as Workflow A's request (WorkflowID is not part of the hash) and returns Workflow A's cached response directly to Workflow B's node — as confirmed by `TestRequestHash`'s "having different workflowID results in same Hash" case. [7](#0-6)

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
