All claims in the report are directly verified against the code. `responseCache.Fetch` and `Set` key exclusively on `req.Hash()` <cite repo="Alyssadaypin/chainlink--004" path="core/services/gateway/handlers/capabilities/v2/response_cache.go" start="66,111" end="77,120" />, the request flows to the cache unmodified from `makeOutgoingRequest` based purely on `CacheSettings` [1](#0-0) , the test suite explicitly documents that `Hash()` is identical across different `WorkflowID` values but differs across `WorkflowOwner` values [2](#0-1) , and the README documents a contradictory "Workflow Isolation" guarantee scoped by workflow ID [3](#0-2) . No authentication, rate-limiting, or other check in `http_handler.go` mitigates this key collision — request routing to the cache is unconditional on cacheable `CacheSettings`.

This is a genuine discrepancy between documented behavior and code, and a real design flaw in per-workflow isolation. However, I need to assess strictly against scope/impact rules before confirming a full vulnerability report.

Audit Report

## Title
Outbound HTTP response cache in the CRE gateway is keyed by `workflowOwner`/request-shape only (not `workflowID`), causing cross-workflow response reuse contrary to documented workflow-scoped isolation - ([File: core/services/gateway/handlers/capabilities/v2/response_cache.go])

## Summary
The gateway's `responseCache` for outbound HTTP Action requests keys cached entries solely on `OutboundHTTPRequest.Hash()`, which per the test suite covers method, URL, headers, body, and `WorkflowOwner`, but explicitly excludes `WorkflowID`. This contradicts the package README's documented guarantee that "Cache entries are scoped by workflow ID to prevent cross-workflow data leakage," so two distinct workflows belonging to the same owner that issue identical-shaped outbound HTTP requests with `CacheSettings.Store=true` will share a cache entry.

## Finding Description
`responseCache.Fetch` and `responseCache.Set` both index the cache map exclusively by `req.Hash()` [4](#0-3) [5](#0-4) . `TestRequestHash` in the package's own test suite asserts as intended behavior that requests differing only in `WorkflowID` produce the *same* hash, while requests differing in `WorkflowOwner` produce different hashes [2](#0-1) . The README for the same package states the opposite contract: "Cache Key: Generated from workflow ID and request hash" and "Workflow Isolation: Cache entries are scoped by workflow ID to prevent cross-workflow data leakage" [6](#0-5) . In `makeOutgoingRequest`, the gateway unmarshals `OutboundHTTPRequest` directly from a node message and passes it unmodified into `responseCache.Fetch`/`Set` keyed on `CacheSettings` alone, with no workflow-ID-based scoping applied at this layer [7](#0-6) . There is no additional check elsewhere in the handler that re-introduces workflow-ID scoping before the cache lookup/store.

## Impact Explanation
This is a real defect: the documented "Workflow Isolation... to prevent cross-workflow data leakage" contract does not hold in the code as-shipped. If two workflows under the same `WorkflowOwner` issue outbound HTTP Action requests with identical method/URL/headers/body and `Store: true`, one workflow's fetched HTTP response can be served to the other, unrelated workflow. That said, the severity here is bounded: the colliding workflows must belong to the *same* `WorkflowOwner` (i.e., the same customer/tenant), and the request itself (URL, headers, body) must already be identical across those workflows — meaning both workflows are, by construction, making the exact same external call. There is no cross-tenant/cross-owner data leakage (that dimension is explicitly covered and correctly isolated per `TestRequestHash`), and no authentication/authorization bypass, key exfiltration, fund movement, or gateway impersonation is enabled by this bug. The realistic impact is confined to a same-owner cache-sharing/staleness anomaly (e.g., workflow B might get a response cached moments earlier for workflow A's identical request rather than making a fresh call) rather than one customer's data being exposed to a different, unrelated customer.

## Likelihood Explanation
Likelihood of the underlying code behavior is high and deterministic — it's directly exercised and asserted by `response_cache_test.go`, not a hypothetical race. However, likelihood of an actual harmful outcome is more limited: it requires an owner running multiple distinct workflows that happen to issue byte-for-byte identical outbound HTTP requests with caching explicitly enabled, which is a fairly narrow, same-tenant scenario rather than a cross-tenant confidentiality break.

## Recommendation
Include `WorkflowID` in `OutboundHTTPRequest.Hash()` (or otherwise scope cache keys per workflow) so cached entries cannot be shared across distinct workflows even under the same owner, aligning the implementation with the documented "Workflow Isolation" guarantee in `README.md`. Alternatively, if same-owner sharing of identical requests is an intentional deduplication optimization, correct the README to remove the "prevents cross-workflow data leakage" language and clarify that isolation is enforced only at the `WorkflowOwner` level.

## Proof of Concept
1. Workflow A (`WorkflowID=wf-A`, `WorkflowOwner=0xOwner1`) sends `OutboundHTTPRequest{Method:"GET", URL:"https://api.example.com/data", CacheSettings:{Store:true, MaxAgeMs:600000}}` via `MethodHTTPAction`; the gateway calls `responseCache.Fetch`, misses, fetches externally, and stores the result keyed by `req.Hash()`.
2. Workflow B (`WorkflowID=wf-B`, same `WorkflowOwner=0xOwner1`) sends an identical request shortly after.
3. `responseCache.Fetch` returns Workflow A's cached response to Workflow B without a fresh external call, confirmed by `TestRequestHash`'s "having different workflowID results in same Hash" subtest at `response_cache_test.go:139-149`, which directly asserts `hash1 == hash2` for requests differing only in `WorkflowID`.

### Citations

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
