### Title
Outbound HTTP response cache in the CRE gateway is keyed by `workflowOwner` (not `workflowID`), causing cross-workflow response confusion despite documented workflow-scoped isolation - ([File: core/services/gateway/handlers/capabilities/v2/response_cache.go])

### Summary
The gateway's `responseCache` for outbound HTTP Action requests caches responses using `OutboundHTTPRequest.Hash()`. Per the struct comment and test suite, that hash covers method, URL, headers, body, and `workflowOwner` — explicitly *excluding* `WorkflowID`. The component's own README, however, documents the opposite contract ("Cache Key: Generated from workflow ID and request hash" / "Workflow Isolation: Cache entries are scoped by workflow ID to prevent cross-workflow data leakage"). This mirrors the Mellow M-3 bug class: a value that is supposed to guarantee correct scoping/allocation (there: the `amount` param supposed to guarantee Obol-only allocation; here: the cache key supposed to guarantee per-workflow isolation) does not actually enforce that guarantee at the point where it matters, so a downstream request can be satisfied with the wrong entity's result.

### Finding Description
`responseCache` stores entries in a map keyed by `req.Hash()`: [1](#0-0) 

`Fetch` and `Set` both key exclusively off `req.Hash()`: [2](#0-1) [3](#0-2) 

The test suite explicitly documents and locks in that `Hash()` ignores `WorkflowID` while it does vary by `WorkflowOwner`: [4](#0-3) [5](#0-4) 

Meanwhile the package README documents a different, stronger guarantee for the same component: [6](#0-5) 

Because the gateway serves multiple workflows belonging to the same `WorkflowOwner` (a single CRE customer commonly runs several distinct workflows), any two workflows under that owner that issue an `OutboundHTTPRequest` with the same method/URL/headers/body and `CacheSettings.Store=true` will collide on the same cache entry — regardless of `WorkflowID`. The gateway then serves one workflow's fetched (and potentially input-dependent) HTTP response to a completely different, unrelated workflow execution via `Fetch`/cache hit path: [7](#0-6) 

This is analogous to the Mellow finding: the contract implies a specific scoping/allocation invariant (per-validator-set in Mellow, per-workflow in this case), the parameter that is supposed to enforce it exists (`amount`/`WorkflowID`) but is not actually checked/keyed at the enforcement point, and the documented safety property silently does not hold at runtime.

### Impact Explanation
This causes cross-workflow response confusion: a workflow node can receive a cached HTTP action result that was actually fetched for a sibling workflow (same owner, different `WorkflowID`), even though the caching contract is documented as "Workflow Isolation... scoped by workflow ID to prevent cross-workflow data leakage." Depending on what data is embedded in bodies/headers that legitimately differ per-workflow-but-not-per-request-shape, this can leak one workflow's externally-fetched data into another workflow's decision logic/output. It does not require any authentication/allowlist bypass — it is purely a caching-key defect in the internet-facing gateway's HTTP handler, matching the "cross-user response confusion" acceptable-impact category.

### Likelihood Explanation
Likelihood is moderate: it requires two workflows under the same `WorkflowOwner` to issue outbound HTTP Action requests with an identical method/URL/headers/body (a realistic scenario for shared endpoints, e.g. a common price feed or webhook URL reused across a customer's workflows) with `CacheSettings.Store=true`. No malicious actor or privileged access is needed — it can occur from ordinary, non-adversarial usage patterns, and is explicitly exercised/asserted as intended behavior by the test suite (`response_cache_test.go`), meaning it is a real, current, deterministic behavior of the shipped code, not a hypothetical race.

### Recommendation
Include `WorkflowID` (or otherwise a full per-workflow-execution scope, not just `WorkflowOwner`) in `OutboundHTTPRequest.Hash()` so cached entries cannot be shared across distinct workflows, aligning the implementation with the documented "Workflow Isolation" guarantee. Alternatively, if per-owner sharing across workflows is an intentional design decision (e.g., to reduce duplicate calls to the same shared upstream endpoint), the README should be corrected to remove the "prevents cross-workflow data leakage" claim, and callers/workflow authors should be warned that `Store=true` responses may be shared with sibling workflows of the same owner.

### Proof of Concept
1. Workflow A (WorkflowID = `wf-A`, WorkflowOwner = `0xOwner1`) issues an `OutboundHTTPRequest{Method: "GET", URL: "https://api.example.com/data", CacheSettings: {Store: true, MaxAgeMs: 600000}}`. The gateway calls `responseCache.Fetch`, misses, fetches from the external endpoint, and stores the response keyed by `req.Hash()` (which does not include `wf-A`).
2. Workflow B (WorkflowID = `wf-B`, same WorkflowOwner = `0xOwner1`) issues the identical `OutboundHTTPRequest` (same method/URL/headers/body) shortly after, also with `Store: true` / non-zero `MaxAgeMs`.
3. Because `Hash()` is identical for both requests (per `TestRequestHash`'s "having different workflowID results in same Hash" assertion), `responseCache.Fetch` returns Workflow A's cached response to Workflow B without making a new external call — confirmed directly by the test at `response_cache_test.go:139-149`, which asserts `hash1 == hash2` for requests differing only in `WorkflowID`.

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

**File:** core/services/gateway/handlers/capabilities/v2/response_cache.go (L111-120)
```go
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
