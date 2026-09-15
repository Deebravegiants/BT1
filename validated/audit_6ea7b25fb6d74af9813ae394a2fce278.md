The Hash() function itself lives in an external dependency (`chainlink-common/pkg/types/gateway`), not in this repo, but its documented and tested behavior is confirmed here.Audit Report

## Title
Cache-key collision across workflows (same owner) causes cross-workflow response confusion in Gateway HTTP action cache - (File: core/services/gateway/handlers/capabilities/v2/response_cache.go)

## Summary
The Gateway's HTTP action `responseCache` keys cached HTTP responses solely by `OutboundHTTPRequest.Hash()`, which per the struct comment and test suite is derived from method, URL, headers, body, and `WorkflowOwner`, but explicitly excludes `WorkflowID` [1](#0-0) . This directly contradicts the module's own README, which documents "Workflow Isolation: Cache entries are scoped by workflow ID to prevent cross-workflow data leakage" [2](#0-1) . Two different workflows sharing the same `WorkflowOwner` that issue identical HTTP requests will collide on the same cache entry and receive each other's cached responses.

## Finding Description
`Fetch` and `Set` both compute the cache key via `req.Hash()` [3](#0-2) [4](#0-3) . The test suite explicitly documents and asserts that varying `WorkflowID` alone does not change the hash, while varying `WorkflowOwner` does [5](#0-4) [6](#0-5) . This path is reachable from `HandleNodeMessage` → `makeOutgoingRequest`, where the cache's `Fetch`/`Set` calls are driven entirely by attacker-controlled `CacheSettings.MaxAgeMs`/`Store` fields on the incoming `OutboundHTTPRequest`, with no additional authorization or scoping check applied before hitting the cache [7](#0-6) . No existing middleware, rate limiter, or auth check in this code path re-derives or enforces workflow-level cache isolation — the `checkRateLimit`/`authorizeRequest` logic exists only in the HTTP *trigger* handler (`http_trigger_handler.go`), not in the outbound HTTP action/cache path.

## Impact Explanation
This breaks the documented workflow-isolation guarantee for the HTTP capability's response cache. A workflow can receive HTTP action results that were actually fetched (and potentially attacker-influenced in content, since the attacker workflow fully controls the request that populates the cache) on behalf of a different, unrelated workflow under the same owner. Since HTTP action results can drive downstream workflow logic (e.g., decision-making, on-chain report submission), this constitutes concrete cross-user/cross-workflow response corruption — an in-scope impact category.

## Likelihood Explanation
The vulnerable code is reachable by any workflow node dispatching an `OutboundHTTPRequest` through the normal HTTP action flow — no gateway operator or admin privileges are required [7](#0-6) . The only precondition is that two workflows share a `WorkflowOwner` (a realistic scenario for a tenant running multiple workflows) and issue requests with matching method/URL/headers/body — plausible for shared/public API endpoints. `CacheSettings.Store` and `MaxAgeMs` are fully attacker-supplied on the request itself, making the collision trivially triggerable and repeatable.

## Recommendation
Include `WorkflowID` (in addition to `WorkflowOwner`) in the `OutboundHTTPRequest.Hash()` computation (defined in the `chainlink-common` dependency's `pkg/types/gateway` package) so cache entries are strictly scoped per-workflow, matching the documented "Workflow Isolation" guarantee.

## Proof of Concept
1. Workflow A (`WorkflowID="workflow-123"`, `WorkflowOwner="0xOwner"`) issues `OutboundHTTPRequest{Method:"GET", URL:"https://api.example.com/data", CacheSettings:{Store:true}}`; the response is cached under `req.Hash()`.
2. Workflow B (`WorkflowID="workflow-456"`, same `WorkflowOwner="0xOwner"`) issues an identical-shape request with `CacheSettings:{MaxAgeMs: N}`.
3. Per `TestRequestHash`'s "having different workflowID results in same Hash" assertion [5](#0-4) , Workflow B's `Fetch` call hits the cache entry populated by Workflow A and returns Workflow A's cached response despite being a distinct workflow — demonstrable via a Go unit test asserting `Fetch` returns the same cached `OutboundHTTPResponse` for two requests differing only in `WorkflowID`.

### Citations

**File:** core/services/gateway/handlers/capabilities/v2/response_cache.go (L15-17)
```go
// responseCache is a thread-safe cache for storing HTTP responses.
// It uses a map to store responses keyed by a hash of the request (method, URL, headers, body, workflowOwner).
type responseCache struct {
```

**File:** core/services/gateway/handlers/capabilities/v2/response_cache.go (L66-67)
```go
func (rc *responseCache) Fetch(ctx context.Context, req gateway.OutboundHTTPRequest, fetchFn func() gateway.OutboundHTTPResponse, storeOnFetch bool) gateway.OutboundHTTPResponse {
	cacheKey := req.Hash()
```

**File:** core/services/gateway/handlers/capabilities/v2/response_cache.go (L111-119)
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
```

**File:** core/services/gateway/handlers/capabilities/v2/README.md (L69-72)
```markdown
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
