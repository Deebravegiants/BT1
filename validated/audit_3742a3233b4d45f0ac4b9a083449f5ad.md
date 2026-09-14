Based on the analysis, there's a legitimate analog in the CRE gateway's HTTP capability response cache.

### Title
Cross-workflow response cache confusion due to `WorkflowID`-independent cache keys - ([File: core/services/gateway/handlers/capabilities/v2/response_cache.go])

### Summary
The `responseCache` used by the HTTP Action gateway handler caches outbound HTTP responses keyed by a hash of `(method, URL, headers, body, workflowOwner)`, explicitly excluding `WorkflowID`. Despite this, the handler's own documentation claims cache entries are workflow-scoped to prevent cross-workflow leakage. This is directly analogous to the reported bug class: a value fixed/computed for one context (a round's price, here a cached response) is reused across different logical contexts (different depositors, here different workflows) that should each be treated independently, producing incorrect/stale results for one party while looking correct for another.

### Finding Description
`responseCache.isExpiredOrNotCached` and `Fetch`/`Set` key the cache exclusively by `req.Hash()`: [1](#0-0) [2](#0-1) 

The comment on the struct documents that the hash includes `(method, URL, headers, body, workflowOwner)` but not `workflowID`: [3](#0-2) 

This is confirmed by the test suite, which explicitly asserts that two requests with different `WorkflowID` values (but the same owner, method, URL, body) hash to the **same** cache key: [4](#0-3) 

Yet the handler's own README claims the opposite guarantee — that cache entries are workflow-scoped and prevent cross-workflow data leakage: [5](#0-4) 

The cache is consumed in `makeOutgoingRequest`, which is invoked whenever any workflow node sends an `OutboundHTTPRequest` message with `CacheSettings.MaxAgeMs > 0` through this unprivileged, internet-facing gateway path: [6](#0-5) 

### Impact Explanation
Because the cache key omits `WorkflowID`, if the same workflow owner runs two different workflows that happen to issue the same outbound HTTP request (same method/URL/headers/body) with `CacheSettings.MaxAgeMs > 0`, one workflow's cached response (fetched/stored at a fixed point in time) will be transparently served to the other workflow — even though the underlying external data may have since changed. This is a cross-workflow response confusion: a stale value computed in the context of workflow A is silently substituted for workflow B's live request, exactly like the reported bug where a stale, fixed price computed for one round/depositor context is reused for a different depositor, producing incorrect economic/business outcomes for whichever workflow relies on the stale data. Depending on what the workflow does with the HTTP response (e.g., driving on-chain actions, price-sensitive decisions), this can lead to workflows acting on outdated or wrong data attributed to the wrong workflow.

### Likelihood Explanation
Reachable directly by any workflow owner controlling multiple workflows (or reusing the same request parameters across workflow versions) — no privileged or operator access is required. The condition only requires `CacheSettings.Store=true`/`MaxAgeMs>0` and issuing the same outbound HTTP request shape from two different `WorkflowID`s under the same owner, which is a normal usage pattern (e.g., re-deploying/upgrading a workflow, or running parallel workflow variants against the same external endpoint).

### Recommendation
Include `WorkflowID` in the cache key (or otherwise make caching workflow-scoped as the README already claims) so that responses cached for one workflow are never served to a different workflow. Align the implementation with the documented isolation guarantee, and add/keep test coverage that WorkflowID *does* differentiate cache entries rather than asserting the current (unintended) collapsing behavior.

### Proof of Concept
1. Workflow `wf-1` (owner `O`) issues `OutboundHTTPRequest{Method: GET, URL: https://api.example.com/price, WorkflowOwner: O, WorkflowID: wf-1, CacheSettings:{Store:true, MaxAgeMs: 600000}}`. The gateway fetches and caches the response (e.g., price = 100).
2. Shortly after, workflow `wf-2` (same owner `O`, different `WorkflowID`) issues an identical `OutboundHTTPRequest` (same method/URL/headers/body) but with `WorkflowID: wf-2`, expecting a fresh fetch since it's a logically distinct workflow/request context.
3. Per `req.Hash()`, both requests hash identically (WorkflowID excluded), so `wf-2` transparently receives `wf-1`'s cached response instead of issuing a new HTTP call — even if the real external price/data has since changed.
4. `wf-2`'s workflow logic then acts on stale data believing it queried fresh data, which is directly analogous to a depositor receiving entry points computed from an outdated price fixed by an earlier depositor's action.

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

**File:** core/services/gateway/handlers/capabilities/v2/README.md (L46-72)
```markdown
#### 2.1.4 Response Cache (`responseCache`)
- **Purpose**: Caches HTTP responses to avoid redundant outbound requests
- **Functions**: TTL-based caching that optionally returns cached values based on max age parameter
- **Key Features**: Workflow-scoped caching

---

## 3. HTTP Action Message Handling

### 3.1 Process Flow

1. **Request Reception**: Gateway receives HTTP action request from a workflow node
2. **Rate Limiting**: Validates node rate limits
3. **Request Parsing**: Extracts `OutboundHTTPRequest` from the JSON-RPC message
4. **Cache Check**: Determines if request should use cached response or fetch fresh data
5. **HTTP Execution**: Makes actual HTTP request to external endpoint
6. **Response Caching**: Stores cacheable responses (2xx, 4xx status codes) only if `CacheSettings.Store` is `true`
7. **Node Response**: Sends HTTP response back to requesting node

### 3.2 Caching Behavior

- **Cacheable Responses**: 2xx (success) and 4xx (client error) status codes.
- **Cache TTL**: Configurable, default 10 minutes
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
