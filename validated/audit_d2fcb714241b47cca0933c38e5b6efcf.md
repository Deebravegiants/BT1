All findings confirmed: `Hash()` is defined in the external `chainlink-common` module and is asserted by this repo's own test to exclude `WorkflowID` while including `WorkflowOwner`, and the README explicitly claims workflow-ID-level cache isolation which the implementation doesn't provide.

Audit Report

## Title
Response cache key omits `WorkflowID`, causing cross-workflow cached HTTP response reuse for the same workflow owner - ([File: core/services/gateway/handlers/capabilities/v2/response_cache.go])

## Summary
The gateway's `responseCache` keys cached HTTP responses solely by `OutboundHTTPRequest.Hash()`, which per the repo's own `TestRequestHash` test explicitly excludes `WorkflowID` from the hash input while including `WorkflowOwner`. This contradicts the component's README, which states that the cache is "scoped by workflow ID to prevent cross-workflow data leakage," so two distinct workflows owned by the same `WorkflowOwner` that issue outbound HTTP requests with identical method/URL/headers/body will collide on the same cache entry.

## Finding Description
`responseCache.Fetch`, `Set`, and `isExpiredOrNotCached` all key cache entries by `req.Hash()` [1](#0-0) [2](#0-1) . The struct's own comment documents the hash as being derived from "method, URL, headers, body, workflowOwner" — `WorkflowID` is absent [3](#0-2) .

This is confirmed directly by the repository's unit test `TestRequestHash`, which asserts that differing `WorkflowID` values produce an *identical* hash, while differing `WorkflowOwner` values produce different hashes: [4](#0-3) [5](#0-4) .

Yet the README explicitly documents workflow-ID-level isolation as a security property: "Cache Key: Generated from workflow ID and request hash" and "Workflow Isolation: Cache entries are scoped by workflow ID to prevent cross-workflow data leakage" [6](#0-5) . The cache is populated via `makeOutgoingRequest`, driven by workflow/node-supplied `OutboundHTTPRequest` fields with no additional per-workflow-instance scoping applied before calling `Fetch`/`Set` [7](#0-6) .

Note: `OutboundHTTPRequest.Hash()` itself is implemented in the external `chainlink-common` module (`github.com/smartcontractkit/chainlink-common/pkg/types/gateway`), not in this repository, so the exact hash implementation cannot be directly inspected here — but its documented/tested behavior (as asserted by this repo's own test suite) is unambiguous.

## Impact Explanation
Impact is bounded by the owner boundary — collisions only occur between workflows sharing the same `WorkflowOwner`, since `WorkflowOwner` is part of the hash. This does not allow a cross-tenant secret leak between unrelated owners; it is a violation of the documented workflow-instance isolation guarantee, allowing one workflow instance's cached HTTP response (potentially containing that workflow's request-specific data baked into headers/body) to be served to a sibling workflow owned by the same account when `CacheSettings.MaxAgeMs > 0` and method/URL/headers/body coincide. This is a data-integrity/correctness issue rather than an authentication or fund-movement bypass, and the actor triggering it (a workflow owner) can only affect their own other workflows.

## Likelihood Explanation
Likelihood is high for accidental (non-malicious) triggering: any owner running multiple workflows that call the same external endpoint with identical or templated-to-identical parameters will silently share cache entries whenever caching is enabled with a nonzero `MaxAgeMs`. No privilege escalation or attacker action beyond normal workflow deployment is required, but the affected party is limited to the workflow owner's own workflows.

## Recommendation
Include `WorkflowID` (or another workflow-instance-scoping identifier) as part of the input to `OutboundHTTPRequest.Hash()` in `chainlink-common`, so cached entries are genuinely scoped per the README's documented guarantee. Update `TestRequestHash`'s "having different workflowID results in same Hash" test case to assert the corrected behavior once fixed.

## Proof of Concept
1. Deploy two workflows (Workflow A, Workflow B) under the same `WorkflowOwner`, both making HTTP Action calls with identical `Method`/`URL`/`Headers`/`Body` and `CacheSettings.Store=true`, `CacheSettings.MaxAgeMs>0`.
2. Workflow A's request executes first via `gatewayHandler.makeOutgoingRequest` → `responseCache.Fetch`, populating the cache keyed by `req.Hash()` [8](#0-7) .
3. Workflow B issues the same request shape (different `WorkflowID`, same owner/method/URL/headers/body); per `TestRequestHash`'s asserted behavior, `req.Hash()` is identical, so `Fetch`'s cache-hit path returns Workflow A's stored response to Workflow B without a fresh outbound call [9](#0-8) .

### Citations

**File:** core/services/gateway/handlers/capabilities/v2/response_cache.go (L15-17)
```go
// responseCache is a thread-safe cache for storing HTTP responses.
// It uses a map to store responses keyed by a hash of the request (method, URL, headers, body, workflowOwner).
type responseCache struct {
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

**File:** core/services/gateway/handlers/capabilities/v2/README.md (L69-72)
```markdown
- **Cache Key**: Generated from workflow ID and request hash
- **Cache Invalidation**: Time-based expiration with periodic cleanup
- **Cache Strategy**: All cacheable responses are cached; Non-zero `CacheSettings.MaxAgeMs` determines whether to return a cached value or make a fresh request
- **Workflow Isolation**: Cache entries are scoped by workflow ID to prevent cross-workflow data leakage
```

**File:** core/services/gateway/handlers/capabilities/v2/http_handler.go (L404-442)
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
			if req.CacheSettings.Store {
				h.responseCache.Set(req, outboundResp)
			}
		}
```
