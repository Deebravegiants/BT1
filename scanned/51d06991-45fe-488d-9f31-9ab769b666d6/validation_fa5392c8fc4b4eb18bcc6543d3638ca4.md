## Analog Vulnerability Found

### Title
Response cache key omits `WorkflowID`, causing cross-workflow HTTP response confusion in the CRE HTTP gateway's outbound-action cache - (File: `core/services/gateway/handlers/capabilities/v2/response_cache.go`)

### Summary
The Sherlock/DODO report describes a shared, un-partitioned pool of value (base/quote token balances) that any caller can consume because the contract tracks aggregate balances instead of per-depositor ownership, letting one user's `sellBase` call spend tokens another user transferred in. The analogous pattern in this repo's internet-facing HTTP Handlers V2 gateway is the outbound HTTP `responseCache`: it is documented as "workflow-scoped" and "Workflow Isolation: … scoped by workflow ID to prevent cross-workflow data leakage," but the actual cache key computed by `OutboundHTTPRequest.Hash()` does **not** include `WorkflowID` — only `WorkflowOwner` plus method/URL/headers/body. This is proven directly by the shipped unit test asserting the opposite of the documented guarantee.

### Finding Description
`responseCache` stores HTTP action responses keyed by `req.Hash()`: [1](#0-0) 

The `Fetch` method uses this hash as the sole cache key when deciding whether to return a cached response for a workflow's outbound HTTP action, without any additional per-workflow scoping check: [2](#0-1) 

Called from the node-message handling path where any workflow node's outbound HTTP action request can hit the shared cache: [3](#0-2) 

The package's own README explicitly claims workflow-level isolation is enforced by the cache key: [4](#0-3) 

But the shipped test suite proves the opposite — `WorkflowID` is explicitly excluded from the hash, while only `WorkflowOwner` differentiates entries: [5](#0-4) 

This mirrors the GSP root cause exactly: the system tracks/serves a pooled resource (here, a cached HTTP response payload) keyed by a coarser identity (owner) than the one the design/documentation promises (workflow), so a request from workflow B (same owner, different `WorkflowID`, but identical method/URL/headers/body) will transparently receive and reuse workflow A's cached response — including any owner-scoped but workflow-sensitive body/headers set by `CacheSettings.Store` on a prior fetch — without any check that the two requests originate from the same logical workflow execution context.

### Impact Explanation
An owner running multiple workflows that call the same external endpoint with identical request shape (same method/URL/headers/body, common for shared upstream APIs or templated calls) will have one workflow silently receive another workflow's cached HTTP response. This breaks the workflow-isolation invariant the system explicitly documents and can lead to: stale/wrong data being fed into a different workflow's execution and consensus aggregation, potential response reuse across differently-trusted or differently-configured workflows under the same owner, and in the `Store: true` + no-`MaxAgeMs` write path, one workflow's fetch populating a cache entry that a second, unrelated (but same-owner) workflow's `Fetch` call (with `MaxAgeMs>0`) will read back as its own response. This is a cross-workflow (cross "user request") response confusion in the gateway's caching layer, which the review scope explicitly calls out as an acceptable finding category.

### Likelihood Explanation
This is reachable purely from the standard HTTP Action capability flow — any onboarded, unprivileged workflow owner deploying two workflows that issue matching outbound requests (a common, non-adversarial scenario: same third-party API, same headers/body template) will trigger this collision without any special network position, timing race, or malicious intent required. No authentication bypass is needed; the confusion happens entirely within the cache key design itself.

### Recommendation
Include `WorkflowID` (and/or `WorkflowExecutionID` if response reuse across executions of the same workflow is also undesired) in the `Hash()` computation used as the `responseCache` key, matching the documented "Workflow Isolation" guarantee, and update/extend the existing `TestRequestHash` cases (currently asserting equality across different `WorkflowID`s) to assert the corrected behavior.

### Proof of Concept
1. Workflow A (owner `X`, `WorkflowID=wf-A`) issues an HTTP action `GET https://api.example.com/data` with `CacheSettings{Store:true, MaxAgeMs:60000}`; the gateway calls `responseCache.Fetch`, executes the request, and caches the result under `req.Hash()` (which does not include `wf-A`).
2. Workflow B (same owner `X`, `WorkflowID=wf-B`, different logic/config) issues the identical `GET https://api.example.com/data` with `CacheSettings.MaxAgeMs>0` within the TTL window.
3. Because `Hash()` produces the same key for both requests (confirmed by `TestRequestHash`'s `"having different workflowID results in same Hash"` subtest), `responseCache.Fetch` returns workflow A's cached response to workflow B instead of executing B's own HTTP call — a direct cross-workflow response confusion analogous to the GSP token-pool cross-user consumption bug.

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

**File:** core/services/gateway/handlers/capabilities/v2/README.md (L66-72)
```markdown

- **Cacheable Responses**: 2xx (success) and 4xx (client error) status codes.
- **Cache TTL**: Configurable, default 10 minutes
- **Cache Key**: Generated from workflow ID and request hash
- **Cache Invalidation**: Time-based expiration with periodic cleanup
- **Cache Strategy**: All cacheable responses are cached; Non-zero `CacheSettings.MaxAgeMs` determines whether to return a cached value or make a fresh request
- **Workflow Isolation**: Cache entries are scoped by workflow ID to prevent cross-workflow data leakage
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
