### Title
Response cache scoped by `WorkflowOwner` instead of `WorkflowID` allows cross-workflow disclosure of cached HTTP responses despite per-workflow access changes - (File: core/services/gateway/handlers/capabilities/v2/response_cache.go)

### Summary
The Gateway's HTTP Handlers V2 `responseCache` caches outbound HTTP action responses keyed by a hash of `(method, URL, headers, body, workflowOwner)`. `WorkflowID` is explicitly excluded from the hash, so any workflow belonging to the same owner that issues an identical outbound HTTP request (same method/URL/headers/body) will receive the cached response originally fetched on behalf of a *different* workflow, even though the module's own documentation states caching is meant to be workflow-scoped.

### Finding Description
`responseCache.Fetch`/`Set`/`isExpiredOrNotCached` all key the cache map by `req.Hash()`: [1](#0-0) [2](#0-1) 

The struct-level comment confirms the hash is built from `(method, URL, headers, body, workflowOwner)` — `WorkflowID` is not part of the key: [3](#0-2) 

This is explicitly validated by the test suite, which asserts identical hashes for requests differing only by `WorkflowID`, while different `WorkflowOwner` values do change the hash: [4](#0-3) 

However, the package's own README documents the intended security property as workflow-level isolation ("Cache entries are scoped by workflow ID to prevent cross-workflow data leakage" / "Cache Key: Generated from workflow ID and request hash"): [5](#0-4) 

Because the actual implementation only scopes by `workflowOwner`, any two workflows under the same owner (which is the unprivileged, external-facing "unit of trust" enforced elsewhere in the gateway, e.g. rate limiting and JWT authorization are done per-workflow via `WorkflowMetadataHandler.Authorize`/`authorizedKeys[workflowID]`) can silently receive each other's HTTP action response bodies/headers if they happen to construct an identical outbound request. This is directly analogous to the Mahara CVE-2020-9386 pattern: a cached artifact (here, an HTTP response) continues to be served to a party (a different workflow under the same owner, potentially with different authorized signer keys or a different execution context) that no longer has an independent right to that specific cached artifact, because the cache's access-scoping (workflowOwner) is coarser than the entity the system's documentation/design claims to isolate (workflowID).

### Impact Explanation
- Sensitive response data (e.g., API keys returned in response bodies, cookies/`Set-Cookie` values which the handler explicitly captures via `MultiHeaders`, or any per-request-scoped result) fetched by one workflow can be transparently returned to a sibling workflow of the same owner that never made that specific outbound call and may run under different authorization/signing keys or security boundaries.
- Because caching also stores 4xx responses (potentially containing internal diagnostic detail) and any 2xx bodies, information originally intended for a narrower workflow context leaks across workflow boundaries within the same owner — the same class of impact as the CVE: metadata/content disclosed to a party without an independent right to it, mediated by a stale/misscoped cache.
- Impact is limited to disclosure between workflows owned by the same account/owner (not across owners, since `workflowOwner` is part of the hash), so it is not full cross-tenant compromise, but it does violate the module's own stated workflow-isolation guarantee and can leak workflow-specific secrets/results to a different workflow context that should not see them.

### Likelihood Explanation
Any owner who operates multiple workflows that make outbound HTTP calls with identical method/URL/headers/body — a very plausible occurrence in the Chainlink Runtime Environment where a template or shared library constructs the same request across workflows (e.g., calling a common external API with fixed headers) — will hit this shared cache entry as a normal side effect of `CacheSettings.Store`/`MaxAgeMs` being honored (default TTL 10 minutes, see README §3.2 and §6.1 `OutboundRequestCacheTTLMs`). No attacker action beyond normal use of two workflows under one owner is required, and the sharing is deterministic once `req.Hash()` collides.

### Recommendation
Include `WorkflowID` (not just `WorkflowOwner`) in the cache key computed by `req.Hash()` (defined in the `chainlink-common` `gateway` package's `OutboundHTTPRequest`), matching the documented "Workflow Isolation" behavior in the README. Alternatively, update the README/design intent if owner-level scoping is truly intended, and audit whether any owner-level shared caching of secrets/headers is acceptable given the JWT/authorized-key model that scopes authorization at the workflow level (`WorkflowMetadataHandler.authorizedKeys[workflowID]`).

### Proof of Concept
1. Workflow A (WorkflowID = "workflow-A", WorkflowOwner = "owner-1") issues an `OutboundHTTPRequest{Method: "GET", URL: "https://api.example.com/data", Headers: {...}, CacheSettings:{Store:true, MaxAgeMs: 600000}}`. The gateway fetches and caches the response under `req.Hash()`, which per `response_cache.go` only incorporates `(method, URL, headers, body, workflowOwner)`.
2. Workflow B (WorkflowID = "workflow-B", same WorkflowOwner = "owner-1") — a different workflow with its own registered authorized signer key and potentially different access rights — issues the byte-identical `OutboundHTTPRequest` (same method/URL/headers/body) with `CacheSettings.MaxAgeMs` non-zero.
3. Per `responseCache.Fetch`, the cache lookup by `req.Hash()` matches Workflow A's cached entry (since `WorkflowID` is not part of the hash, confirmed by `TestRequestHash`'s "having different workflowID results in same Hash" case), and Workflow B receives Workflow A's previously-fetched response without any new outbound HTTP call or independent authorization check against the target resource for workflow B specifically.

Note: I could not locate the exact `OutboundHTTPRequest.Hash()` implementation in `chainlink-common` (it lives outside this repo's indexed scope), so the precise byte-level construction of the hash could not be directly verified beyond the comment and the confirming test assertions in this repo. This limitation should be verified by inspecting `chainlink-common/pkg/types/gateway` directly in a full session.

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
