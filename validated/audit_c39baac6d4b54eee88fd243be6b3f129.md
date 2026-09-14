### Title
Response cache key omits `WorkflowID`, causing cross-workflow HTTP response leakage in the HTTP Action gateway handler - ([File: core/services/gateway/handlers/capabilities/v2/response_cache.go])

### Summary
The original report is about a fee computed from a user-supplied input (LIMIT price) that diverges from the actual execution value, letting the requester either avoid paying fees or overpay unexpectedly. The reachable Chainlink analog in the same class of "trusting a caller-controlled input where an authoritative/actual value should be used, with a caching/isolation guarantee that silently doesn't hold" is the HTTP Action `responseCache` used by the gateway's internet-facing HTTP capability handler (`core/services/gateway/handlers/capabilities/v2`). The documented invariant is that cached HTTP responses are workflow-isolated, but the actual cache key computation drops `WorkflowID` entirely, so cached responses are shared across different workflows that merely share the same `WorkflowOwner`.

### Finding Description
`responseCache` caches outbound HTTP action responses keyed by `req.Hash()`: [1](#0-0) 

The package README explicitly documents the intended security property: "Cache Key: Generated from workflow ID and request hash" and "Workflow Isolation: Cache entries are scoped by workflow ID to prevent cross-workflow data leakage": [2](#0-1) 

However, the actual `Hash()` behavior (exercised by `TestRequestHash`) proves `WorkflowID` is NOT part of the cache key — only method, URL, headers, body, and `WorkflowOwner` are: [3](#0-2) 

This is the same root-cause pattern as the audited bug: a value the system is documented/expected to authoritatively scope by (WorkflowID, analogous to "actual open price") is silently replaced by a coarser, caller-influenced scope (WorkflowOwner, analogous to "user-supplied limit price"), producing behavior that diverges from the documented/expected guarantee. Two different workflows belonging to the same owner making the same outbound HTTP action request (same method/URL/headers/body) will hit and share the same cache entry — including any cached error bodies, tokens, or endpoint responses tied to one workflow's HTTP action call.

The request flows directly from an unprivileged workflow-node message on the gateway's node-facing message path (no additional scoping applied before the cache lookup): [4](#0-3) 

### Impact Explanation
Because the cache key intentionally includes `WorkflowOwner` (to preserve some isolation) but the test proves `WorkflowID` is excluded despite the documented design, any two workflows under the same owner that issue functionally identical `OutboundHTTPRequest`s (same method, URL, headers, body) will read/write the same cache slot. This breaks the documented "Workflow Isolation" guarantee and can let one workflow silently receive a cached response (body/headers) generated for, or in response to, a different workflow's HTTP action — a cross-workflow response confusion. If per-workflow request parameters (e.g. an API key embedded identically or a body that happens to coincide) produce colliding hashes, data intended to be scoped per-workflow can leak between sibling workflows of the same owner, and stale/incorrect cached data can be served to the wrong workflow.

### Likelihood Explanation
This is reachable from an unprivileged actor: any workflow (owned by the attacker) that runs multiple concurrently-registered workflows sharing the same owner can construct identical `OutboundHTTPRequest`s from two different workflow IDs and observe cache reuse. No malicious node, peer, or operator access is required — the exposure is purely from a legitimate but multi-workflow owner sending HTTP action requests through the gateway's node message handler (`HandleNodeMessage` → `makeOutgoingRequest`). Exploitation only requires colliding request shapes across sibling workflows, which is a normal and even encouraged usage pattern (identical calls to the same third-party API from multiple workflows).

### Recommendation
Include `WorkflowID` (not just `WorkflowOwner`) in the `Hash()` computation used as the cache key, matching the documented behavior in the README, or explicitly document/enforce owner-level (not workflow-level) cache sharing if that is the intended design and update security-sensitive assumptions accordingly. Add a regression test asserting `Hash()` differs for different `WorkflowID`s under the same owner, replacing/removing the current test that asserts the opposite.

### Proof of Concept
1. Register two workflows, `wf-A` and `wf-B`, under the same `WorkflowOwner`.
2. From `wf-A`, issue an `OutboundHTTPRequest` (via the HTTP Action capability) to `https://api.example.com/data` with `CacheSettings.Store = true`, and let the gateway cache the response.
3. From `wf-B` (different `WorkflowID`, same `WorkflowOwner`), issue the identical `OutboundHTTPRequest` (same method/URL/headers/body) with `CacheSettings.MaxAgeMs > 0`.
4. Observe that `wf-B` receives the cached response originally fetched for `wf-A` without a fresh HTTP call being made — confirmed by `TestRequestHash`'s "having different workflowID results in same Hash" assertion in `response_cache_test.go`, which demonstrates the colliding cache key at the unit level.

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
