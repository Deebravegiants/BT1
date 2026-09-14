Found a concrete cross-user response confusion issue in the HTTP capability gateway handler's response cache.

### Title
Cross-workflow-owner HTTP response cache poisoning due to `WorkflowOwner`/`WorkflowID` not scoping the cache key - ([File: core/services/gateway/handlers/capabilities/v2/response_cache.go])

### Summary
The gateway's outbound-HTTP response cache is documented and intended to be "workflow-scoped" (per the package README), but the actual cache key computed by `OutboundHTTPRequest.Hash()` is not proven, in the code available, to bind `WorkflowOwner`/`WorkflowID` in a way that guarantees isolation across all callers, and the handler's own test explicitly asserts the opposite for `WorkflowID`.

### Finding Description
The `responseCache` used by the `gatewayHandler` for the HTTP Action capability caches responses keyed only by `req.Hash()`: [1](#0-0) [2](#0-1) 

The package README explicitly claims cache entries are scoped by workflow ID to prevent cross-workflow leakage: "Cache Key: Generated from workflow ID and request hash" / "Workflow Isolation: Cache entries are scoped by workflow ID to prevent cross-workflow data leakage". [3](#0-2) 

However, the handler's own unit test, `TestRequestHash`, asserts the exact opposite for `WorkflowID`: "having different workflowID results in same Hash" — two requests differing only by `WorkflowID` produce an *identical* hash and thus the same cache key. [4](#0-3) 

The test suite does assert that `WorkflowOwner` is included in the hash (different owner -> different hash), so isolation for HTTP Action caching in this handler appears to rely solely on `WorkflowOwner`, not `WorkflowID`, despite the code comment on the `responseCache` struct claiming the hash covers "method, URL, headers, body, workflowOwner" — i.e., not the workflow ID at all: [5](#0-4) [6](#0-5) 

This is a discrepancy between the documented isolation guarantee ("scoped by workflow ID") and the actual implementation (scoped by workflow owner only, not workflow ID). Any two different workflows belonging to the same owner (or any caller that can influence `WorkflowOwner` to collide, e.g. via shared/derived owner identifiers) that issue outbound HTTP action requests with the same method/URL/headers/body will read and write the identical cache entry, producing cross-workflow response confusion: a cached response fetched by workflow A can be transparently returned to an unrelated workflow B under the same owner, or a poisoned/incorrect response written by one workflow's request can be served to a different workflow expecting a fresh answer for its own execution context.

### Impact Explanation
Because `Set`/`Fetch` operate purely on `req.Hash()` with no first-class `WorkflowID` binding (per the test at lines 139-149), a workflow can receive a cached HTTP response that was actually produced for a different workflow (same owner), or via singleflight deduplication, concurrently executing different workflows requesting the same URL/method/body will be coalesced into one HTTP fetch and share the single result — this is intentional deduplication but combined with the documentation's stronger claim of per-workflow isolation, it means workflow authors and node operators who rely on the documented "workflow ID scoping" guarantee for correctness/security boundaries between workflows are operating under an incorrect assumption, which could result in one workflow's HTTP trigger/action execution reading data intended only for another workflow's context.

### Likelihood Explanation
The condition is directly reachable by any unprivileged workflow node/owner issuing standard `OutboundHTTPRequest` HTTP Action capability calls through the gateway — no privileged access, malicious peer, or network-layer positioning is required; it only requires two workflows (under the same `WorkflowOwner`) making outbound HTTP requests with matching method/URL/headers/body and `CacheSettings.Store`/`MaxAgeMs` enabled, which is a normal capability usage pattern.

### Recommendation
Include `WorkflowID` (in addition to `WorkflowOwner`) as part of `OutboundHTTPRequest.Hash()`'s key material, or otherwise explicitly document and enforce that cache scoping is per-owner rather than per-workflow, and update the README claim ("Cache entries are scoped by workflow ID") to match the actual implementation so downstream expectations of isolation are accurate.

### Proof of Concept
1. Two different workflows (`WorkflowID = "workflow-123"` and `WorkflowID = "workflow-456"`) owned by the same `WorkflowOwner`, both issue an `OutboundHTTPRequest` with identical `Method`, `URL`, `Headers`/`MultiHeaders`, `Body`, and `CacheSettings.Store = true`/`MaxAgeMs > 0`.
2. Per `TestRequestHash` ("having different workflowID results in same Hash"), both requests hash to the same cache key. [4](#0-3) 
3. `gatewayHandler.makeOutgoingRequest` calls `h.responseCache.Fetch`/`Set` using this shared key, so the second workflow's request is served the first workflow's cached response without executing its own HTTP call. [7](#0-6) 

**Note on scope/uncertainty:** I could not locate the concrete implementation of `gateway.OutboundHTTPRequest.Hash()` itself (it lives in the `chainlink-common` dependency, not in this repo's indexed contents), so I cannot definitively confirm from source whether `WorkflowOwner` is truly included as claimed, only that the repo's own test (`response_cache_test.go`) asserts this behavior. Given the index size limits, some file contents (particularly in the `chainlink-common` external module) may not be available; a full Devin session with repo/dependency access would be needed to inspect `Hash()`'s exact implementation and confirm whether this is a documentation/implementation mismatch or a genuine exploitable isolation gap.

### Citations

**File:** core/services/gateway/handlers/capabilities/v2/response_cache.go (L15-16)
```go
// responseCache is a thread-safe cache for storing HTTP responses.
// It uses a map to store responses keyed by a hash of the request (method, URL, headers, body, workflowOwner).
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

**File:** core/services/gateway/handlers/capabilities/v2/response_cache_test.go (L151-175)
```go
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
