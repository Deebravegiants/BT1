Audit Report

## Title
Cache key in `responseCache` omits `WorkflowID`, causing cross-workflow HTTP response confusion in the gateway's outbound response cache - ([File: core/services/gateway/handlers/capabilities/v2/response_cache.go])

## Summary
The gateway's `responseCache` keys cached HTTP Action responses solely by `req.Hash()`, and `Hash()` (as proven by the repo's own test suite) only incorporates `Method`, `URL`, headers, `Body`, and `WorkflowOwner` — not `WorkflowID`. This directly contradicts the module's own documentation, which promises per-workflow cache isolation, and allows two different workflows owned by the same address to collide on the same cache entry when their outbound requests are shape-identical.

## Finding Description
`responseCache.Fetch` and `isExpiredOrNotCached` key the cache map exclusively by `req.Hash()`: [1](#0-0) [2](#0-1) 

The struct's doc comment itself states the hash is derived from "method, URL, headers, body, workflowOwner" — `WorkflowID` is absent: [3](#0-2) 

This is confirmed by the repository's own test suite for `Hash()`, which explicitly asserts identical hashes when only `WorkflowID` differs, while differing `WorkflowOwner` produces different hashes: [4](#0-3) [5](#0-4) 

Meanwhile, the module's design documentation explicitly promises the opposite: that the cache key is "Generated from workflow ID and request hash" and that "Cache entries are scoped by workflow ID to prevent cross-workflow data leakage": [6](#0-5) 

The request path confirms this cache is reached directly from workflow-node-originated HTTP Action requests, with the full `OutboundHTTPRequest` (including `WorkflowOwner`/`WorkflowID`) passed straight into `responseCache.Fetch`/`Set`: [7](#0-6) 

No other check (e.g., an explicit `WorkflowID` comparison before returning a cached entry) exists in `Fetch` or `isExpiredOrNotCached` to compensate for the missing field in the hash — the map lookup is the sole authorization/isolation boundary, and it is keyed on data that does not include `WorkflowID`.

## Impact Explanation
This is a cross-workflow response confusion/data-isolation bug in the gateway component that brokers HTTP Action results between external endpoints and DON workflow nodes. Two workflows under the same `WorkflowOwner` that happen to issue identically-shaped outbound HTTP requests (same method, URL, headers, body) will transparently share cached responses via the same `rc.cache[cacheKey]` entry, and `singleflight.Group.Do` further coalesces concurrent in-flight requests from different workflows under that same key. This breaks the explicitly documented "Workflow Isolation" guarantee and maps to the in-scope "cross-user response corruption" impact class, since a workflow can receive a response payload actually produced for a different workflow's request context.

## Likelihood Explanation
This requires no privilege escalation and no attacker action beyond normal, unprivileged workflow-node-originated HTTP Action requests — it can occur accidentally whenever an owner runs multiple workflows that call the same external endpoint with identical parameters, and can be deliberately triggered by any workflow owner controlling two of their own workflows with matching request shapes and `CacheSettings.Store=true`/`MaxAgeMs>0`.

## Recommendation
Include `WorkflowID` in the data hashed by `OutboundHTTPRequest.Hash()` (in the chainlink-common dependency where this type is defined) so `responseCache` keys are genuinely scoped per workflow, matching the documented design. Add a regression test asserting that varying `WorkflowID` alone changes `Hash()`'s output, inverting the current assertion at `response_cache_test.go:139-149`, and verify `Fetch`, `Set`, and `isExpiredOrNotCached` all continue to function correctly with the corrected hash.

## Proof of Concept
1. Owner `X` runs Workflow `A` and Workflow `B`, each issuing an HTTP Action request with identical `Method`, `URL`, `MultiHeaders`, and `Body` (e.g., `GET https://api.example.com/data`), both with `CacheSettings.Store = true` and `CacheSettings.MaxAgeMs > 0`.
2. Workflow `A`'s request reaches `gatewayHandler.makeOutgoingRequest` → `responseCache.Fetch`, executes the real HTTP call, and stores the response under `cacheKey := req.Hash()`.
3. Workflow `B` issues the same-shaped request; since `Hash()` ignores `WorkflowID` (confirmed by `TestRequestHash/having_different_workflowID_results_in_same_Hash` in `response_cache_test.go:139-149`), `cacheKey` matches Workflow `A`'s entry, and `Fetch` returns Workflow `A`'s previously cached response to Workflow `B` without a fresh HTTP call — directly reproducible by extending the existing test to assert `Fetch` returns a cross-workflow cached value, or by adding an integration test that calls `Fetch` twice with only `WorkflowID` differing and confirming the second call returns the first call's response without invoking `fetchFn`.

### Citations

**File:** core/services/gateway/handlers/capabilities/v2/response_cache.go (L15-19)
```go
// responseCache is a thread-safe cache for storing HTTP responses.
// It uses a map to store responses keyed by a hash of the request (method, URL, headers, body, workflowOwner).
type responseCache struct {
	cacheMu sync.RWMutex
	cache   map[string]*cachedResponse
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

**File:** core/services/gateway/handlers/capabilities/v2/http_handler.go (L404-438)
```go
func (h *gatewayHandler) makeOutgoingRequest(ctx context.Context, resp *jsonrpc.Response[json.RawMessage], nodeAddr string) error {
	requestID := resp.ID
	h.lggr.Debugw("handling outgoing message", "requestID", requestID, "nodeAddr", nodeAddr)
	var req gateway_common.OutboundHTTPRequest
	err := json.Unmarshal(*resp.Result, &req)
	if err != nil {
		return fmt.Errorf("failed to unmarshal HTTP request from node %s: %w", nodeAddr, err)
	}
	timeout := time.Duration(req.TimeoutMs) * time.Millisecond
	httpReq := network.HTTPRequest{
		Method:           req.Method,
		URL:              req.URL,
		Headers:          req.Headers, //nolint:staticcheck // forward deprecated Headers for backward compatibility; request uses MultiHeaders when set
		MultiHeaders:     req.MultiHeaders,
		Body:             req.Body,
		MaxResponseBytes: req.MaxResponseBytes,
		Timeout:          timeout,
	}

	sendResponseTimeout := time.Duration(defaultSendResponseTimeoutMs) * time.Millisecond

	// send response to node async
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
```
