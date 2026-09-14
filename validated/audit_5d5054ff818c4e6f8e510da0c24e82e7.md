This is confirmed: the `Hash()` function for `OutboundHTTPRequest` explicitly scopes cache keys by `WorkflowOwner` but **not** by `WorkflowID`. This is documented and tested behavior — the test at `core/services/gateway/handlers/capabilities/v2/response_cache_test.go:139-149` explicitly asserts "having different workflowID results in same Hash", confirming that requests from different workflows belonging to the same owner but with different `WorkflowID` collapse into the same cache entry.

### Title
Cache-key collision across workflows (same owner) causes cross-workflow response confusion in Gateway HTTP action cache - (File: core/services/gateway/handlers/capabilities/v2/response_cache.go)

### Summary
The Gateway's HTTP action `responseCache` keys cached HTTP responses solely by `OutboundHTTPRequest.Hash()`, which is documented as being derived from "method, URL, headers, body, workflowOwner" [1](#0-0) . The `WorkflowID` field is explicitly excluded from the hash, as proven by the test asserting identical hashes for differing `WorkflowID` values [2](#0-1) . The README documents the intended security property as "Workflow Isolation: Cache entries are scoped by workflow ID to prevent cross-workflow data leakage" and "Cache Key: Generated from workflow ID and request hash" [3](#0-2) , but the implementation does not honor this — the documented invariant does not match the code's actual behavior.

### Finding Description
`Fetch` and `Set` both use `req.Hash()` as the sole cache key [4](#0-3) [5](#0-4) . Two distinct workflows owned by the same `WorkflowOwner` that issue an outbound HTTP action to the same URL/method/headers/body — but which are logically unrelated workflows with different `WorkflowID` — will collide on the same cache entry. This is a permissionless, unprivileged-actor-reachable code path: any workflow node dispatching an `OutboundHTTPRequest` via `HandleNodeMessage` → `makeOutgoingRequest` reaches this cache directly [6](#0-5) , with `CacheSettings.Store`/`MaxAgeMs` fully controlled by the incoming request. An attacker-controlled or malicious workflow (sharing an owner with a victim workflow, e.g. multiple workflows deployed under one account) can pre-populate the cache with a crafted response for a given URL+headers+body combination, and a different workflow under that same owner querying an overlapping-but-logically-distinct external resource will receive the poisoned/foreign cached response — a direct cross-user/cross-workflow response confusion, mirroring the Makina root cause of "trusting a state value that wasn't actually scoped/validated for the context it was used in."

### Impact Explanation
This breaks the documented workflow-isolation guarantee for the HTTP capability's response cache. A workflow can receive HTTP action results that were actually fetched (and possibly manipulated in content) on behalf of a different workflow, without any explicit authorization check tying the cached entry to the requesting `WorkflowID`. Depending on how workflow logic consumes HTTP action results (e.g., driving on-chain report submission, feeding into oracle-like computations, or being used for automated fund-moving decisions), stale/foreign data returned across workflow boundaries can lead to incorrect execution results being propagated by the DON.

### Likelihood Explanation
Reachable by any unprivileged workflow node without gateway operator privileges — `CacheSettings.Store` and `MaxAgeMs` are attacker-supplied fields on the `OutboundHTTPRequest` itself [7](#0-6) . The only precondition is sharing a `WorkflowOwner` with a target workflow and being able to predict/match the URL, method, headers, and body of a request the victim workflow will also issue — plausible for common/public API endpoints reused across a tenant's workflows.

### Recommendation
Include `WorkflowID` (not just `WorkflowOwner`) in the `OutboundHTTPRequest.Hash()` computation so that cache entries are strictly scoped per-workflow, matching the documented "Workflow Isolation" guarantee in the README.

### Proof of Concept
1. Workflow A (WorkflowID="workflow-123", WorkflowOwner="0xOwner") issues an `OutboundHTTPRequest{Method:"GET", URL:"https://api.example.com/data", CacheSettings:{Store:true}}`; response is cached under `Hash()`.
2. Workflow B (WorkflowID="workflow-456", same WorkflowOwner="0xOwner") issues an identical `OutboundHTTPRequest` shape (same method/URL/headers/body) with `CacheSettings:{MaxAgeMs: N}`.
3. Per `TestRequestHash`'s "having different workflowID results in same Hash" assertion [2](#0-1) , Workflow B's `Fetch` call hits the cache entry populated by Workflow A and returns Workflow A's cached response, despite being a logically distinct workflow.

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
