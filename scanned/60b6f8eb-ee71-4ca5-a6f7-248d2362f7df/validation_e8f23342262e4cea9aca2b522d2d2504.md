### Title
Response cache keyed by `WorkflowOwner` instead of `WorkflowID` causes cross-workflow HTTP response leakage - (File: core/services/gateway/handlers/capabilities/v2/response_cache.go)

### Summary
The Gateway's HTTP-action `responseCache` deduplicates and serves cached responses using a hash that includes `WorkflowOwner` but explicitly excludes `WorkflowID`. Any two workflows owned by the same address that issue an outbound HTTP action with the same method/URL/headers/body will collide on the same cache key, so a workflow can receive an HTTP response that was actually fetched (and cached) for a different workflow. This mirrors the report's bug class: stale/incorrectly-scoped cached data (the old cached receiver) is served instead of data scoped to the current, correct context, causing data to reach the wrong destination.

### Finding Description
`responseCache` stores entries keyed by `req.Hash()`: [1](#0-0) 

The test suite explicitly documents and asserts the hashing behavior: identical `WorkflowOwner` but different `WorkflowID` produce the **same** hash, i.e. cache-key collision across workflows of the same owner: [2](#0-1) 

This directly contradicts the component's own documented design intent, which states caching should be scoped by workflow ID: [3](#0-2) 

The cache is consumed from `gatewayHandler.makeOutgoingRequest`, which is invoked for every outbound HTTP action received from a workflow node (an unprivileged/uncontrolled request path from the node/workflow side), and either does a cache `Fetch` (read+write) or a direct `Set`, both keyed the same way: [4](#0-3) 

Because `Hash()` ignores `WorkflowID`, if Workflow A (owner X) and Workflow B (owner X, different `WorkflowID`) both issue a GET to the same URL with the same headers/body (e.g., a common third-party API call pattern), Workflow B can receive the cached HTTP response that was originally fetched and stored for Workflow A — including any response body/headers that may contain workflow-specific or sensitive data returned by the external endpoint (tokens, session data, per-caller state, etc., depending on what the external API returns based on request parameters not included in the hash, such as custom auth headers keyed differently, or IP-based responses). This is a direct analog to the original bug: data intended for one context (the current receiver / the current workflow) is instead delivered using a stale, incorrectly-scoped cache entry associated with a different context that happens to share the same coarse-grained key (the receiver address / the workflow owner).

### Impact Explanation
Impact is Medium: a workflow can transparently receive an HTTP response payload that was fetched on behalf of a sibling workflow under the same owner. If the external endpoint's response varies based on data not included in the cache key (e.g., server-side session state, per-workflow secrets embedded in a header not covered by `Hash()`, or responses that differ due to timing/state), this results in cross-workflow response confusion — one workflow silently consuming data intended for another. This can lead to data leakage between workflows or a workflow acting on stale/incorrect data it did not itself request, which can cascade into incorrect on-chain writes or fund-moving actions downstream if the HTTP action result feeds decision logic.

### Likelihood Explanation
Likelihood is Medium: it requires two workflows under the same owner to issue outbound HTTP actions with an identical method, URL, header set, and body (this is plausible for common integrations, e.g., multiple workflows polling the same public API endpoint with default headers) and for `CacheSettings.Store`/`MaxAgeMs` to be enabled on the request. This is a normal, non-adversarial configuration Class scenario reachable purely by an unprivileged workflow owner running multiple workflows — no malicious node/peer or privileged access is needed.

### Recommendation
Include `WorkflowID` (not just `WorkflowOwner`) in the cache key computed by `OutboundHTTPRequest.Hash()`, matching the documented design ("Cache entries are scoped by workflow ID to prevent cross-workflow data leakage"). At minimum, update `Hash()` so that requests from different `WorkflowID`s never collide, and add/restore a test asserting different `WorkflowID` → different hash (the current test at lines 139-149 asserts the opposite and should be corrected as part of the fix).

### Proof of Concept
1. Workflow A (`WorkflowOwner = 0xabc`, `WorkflowID = "wf-A"`) issues an `OutboundHTTPRequest{Method: "GET", URL: "https://api.example.com/data", CacheSettings: {Store: true, MaxAgeMs: 600000}}`. The gateway fetches from the external endpoint and caches the response under `req.Hash()`.
2. Workflow B (`WorkflowOwner = 0xabc`, `WorkflowID = "wf-B"`), a completely different workflow belonging to the same owner, issues an outbound HTTP action with the same `Method`, `URL`, headers, and body but `CacheSettings.MaxAgeMs > 0`.
3. Per `response_cache_test.go` lines 139-149 ("having different workflowID results in same Hash"), `req.Hash()` for Workflow B equals the hash for Workflow A's request.
4. `responseCache.Fetch` (called from `makeOutgoingRequest`, `http_handler.go:434-436`) finds the existing cache entry and returns Workflow A's cached response to Workflow B without making a fresh request or verifying workflow identity — demonstrating the cross-workflow response confusion.

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

**File:** core/services/gateway/handlers/capabilities/v2/response_cache_test.go (L139-161)
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
