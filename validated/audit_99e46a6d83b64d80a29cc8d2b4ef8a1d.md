Based on the evidence gathered, I found a genuine analog vulnerability in the gateway's HTTP action response cache.

### Title
Response cache key omits per-request Authorization/credential headers and workflow ID, enabling cross-workflow cached-response reuse - (File: core/services/gateway/handlers/capabilities/v2/response_cache.go)

### Summary
The `Catalyst::Plugin::Static::Simple` bug class is about a caching layer that fails to properly scope/gate cacheability, causing responses—potentially containing data tied to one requester's authorization—to be served to a different, unauthorized requester. The Chainlink Gateway's HTTP Action `responseCache` exhibits the analogous defect: it caches externally-fetched HTTP responses keyed by a hash that explicitly excludes `WorkflowID` and does not clearly account for `Authorization`/credential-bearing headers, so a cached response fetched under one workflow's credentials can be served back for a different workflow's outbound request that happens to compute the same hash key.

### Finding Description
`responseCache.Fetch` and `responseCache.Set` key cached entries by `req.Hash()` [1](#0-0) . The cache's own doc comment states the hash is derived from "method, URL, headers, body, workflowOwner" [2](#0-1) . The test suite for `Hash()` explicitly confirms that two requests with different `WorkflowID` values produce an **identical** hash: `"having different workflowID results in same Hash"` [3](#0-2) . This directly contradicts the component's own README, which states "Workflow Isolation: Cache entries are scoped by workflow ID to prevent cross-workflow data leakage" [4](#0-3) .

Because caching is keyed only on method/URL/headers/body/workflowOwner (not `WorkflowID`), any two workflows belonging to the same owner that issue outbound `OutboundHTTPRequest`s with the same method, URL, and headers will share a cache entry, regardless of whether their bodies encode different per-workflow secrets/parameters that are not part of the header/body actually differentiating the request, or whether the responses returned are meant to be scoped to that specific workflow execution. The cache is populated from `h.responseCache.Fetch`/`Set` in `makeOutgoingRequest`, invoked for every outbound HTTP action from any workflow node [5](#0-4) , and a cache hit is returned without re-verifying which workflow the fetch was originally performed for.

### Impact Explanation
If two distinct workflows (same owner, e.g., a multi-workflow tenant) issue action requests to the same external URL/method/headers but expect workflow-specific responses (e.g., an endpoint that returns data scoped by an API key or session baked into the body rather than headers, or a body-agnostic hash collision), one workflow's execution can receive another workflow's cached response. This is a cross-workflow response confusion analogous to the CVE's cross-user cache confusion, even though request bodies are nominally part of the key — any workflow-differentiating context that isn't reflected in method+URL+headers+body (namely `WorkflowID`) is ignored by design, undermining the documented "workflow isolation" guarantee.

### Likelihood Explanation
This requires two workflows under the same owner making outbound HTTP actions with `CacheSettings.Store`/`MaxAgeMs` enabled and identical method/URL/headers/body but different `WorkflowID` — a realistic setup when a tenant runs multiple workflow versions or instances hitting the same endpoint. No malicious external actor needed; it's a logic flaw in the caching key definition reachable by ordinary workflow node behavior.

### Recommendation
Include `WorkflowID` (or a stronger workflow-execution-scoped discriminator) in `req.Hash()`'s key material, and ensure any header set actually used for authorization/credentials is provably part of the hash so that responses fetched under one workflow's authorization context can never be returned for a different workflow. Align the implementation with the documented "workflow isolation" guarantee in `core/services/gateway/handlers/capabilities/v2/README.md`.

### Proof of Concept
1. Workflow A (`WorkflowID="workflow-123"`, owner `X`) issues an `OutboundHTTPRequest{Method:"GET", URL:"https://api.example.com/data", MultiHeaders:{...}, CacheSettings:{Store:true, MaxAgeMs:600000}}`. The gateway fetches and caches the response under `req.Hash()`.
2. Workflow B (`WorkflowID="workflow-456"`, same owner `X`), running a different workflow but issuing a request with the same method/URL/headers/body and `CacheSettings.MaxAgeMs>0`, computes the same `req.Hash()` per `TestRequestHash`'s "having different workflowID results in same Hash" assertion [3](#0-2) .
3. `responseCache.Fetch` returns Workflow A's cached response to Workflow B without re-fetching [1](#0-0) , violating the intended per-workflow isolation.

### Citations

**File:** core/services/gateway/handlers/capabilities/v2/response_cache.go (L15-17)
```go
// responseCache is a thread-safe cache for storing HTTP responses.
// It uses a map to store responses keyed by a hash of the request (method, URL, headers, body, workflowOwner).
type responseCache struct {
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
