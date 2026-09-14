### Title
Cross-workflow HTTP response cache poisoning in gateway HTTP capability handler (missing `WorkflowID` scoping) - ([File: core/services/gateway/handlers/capabilities/v2/response_cache.go])

### Summary
The Gateway's v2 HTTP capability handler caches outbound HTTP action responses (including 4xx error bodies) keyed by a hash of the request that is scoped by `WorkflowOwner` but explicitly **not** by `WorkflowID`, contradicting the component's own documented isolation guarantee. This allows a workflow-controlled request (from a DON node, i.e., an unprivileged actor relative to other workflows owned by the same address) to poison or read cached HTTP responses belonging to a different workflow owned by the same address, causing cross-workflow response confusion / loss of confidentiality — the same bug class as the referenced Discourse CVE (cache poisoning via crafted request causing cached error/response leakage).

### Finding Description
The gateway's `responseCache` stores `OutboundHTTPResponse` values for any 2xx or 4xx status code when `CacheSettings.Store` is true, and serves them back via `Fetch` when `CacheSettings.MaxAgeMs > 0`, keyed by `req.Hash()`: [1](#0-0) [2](#0-1) 

The request flow that populates/reads this cache is driven entirely by node-originated `OutboundHTTPRequest` messages parsed from JSON-RPC results and dispatched per-workflow: [3](#0-2) 

The project's own README documents that the cache key is "Generated from workflow ID and request hash" and that "Cache entries are scoped by workflow ID to prevent cross-workflow data leakage": [4](#0-3) 

However, the actual test suite for `req.Hash()` proves the opposite: two requests differing only in `WorkflowID` produce the **same** hash (cache key), while requests differing in `WorkflowOwner` produce different hashes: [5](#0-4) [6](#0-5) 

`req.Hash()` itself is implemented outside this repository, in the `chainlink-common` dependency (`github.com/smartcontractkit/chainlink-common/pkg/types/gateway`), so I could not inspect its exact source in this codebase — the behavior above is inferred from the test assertions in `response_cache_test.go`, which are authoritative for the observable cache-key semantics but not the literal implementation. This should be flagged as a point requiring direct verification of the `OutboundHTTPRequest.Hash()` source.

Because `WorkflowID` is excluded from the cache key, any two workflows sharing the same `WorkflowOwner` that issue an `OutboundHTTPRequest` with the same method/URL/headers/body will collide on the same cache entry. A workflow under attacker control (same owner, different workflow) can:
1. Issue a request matching a victim workflow's outbound call shape (same method/URL/body/headers) with `CacheSettings.Store=true`, causing its (possibly attacker-influenced or error) response to be cached under the shared key.
2. When the victim workflow later issues the same request with `CacheSettings.MaxAgeMs > 0`, it receives the poisoned/attacker's cached response instead of a fresh fetch — matching the "cache poisoning ... loss of confidentiality for some content" bug class from the reference CVE.

Additionally, 4xx error responses are cached by design (`isCacheableStatusCode`), which is the exact mechanism flagged in the Discourse advisory (error responses cached and served to other consumers).

### Impact Explanation
A workflow belonging to the same owner as a victim workflow can cause response confusion: reading another workflow's cached HTTP response (potential data/confidentiality leak) or injecting a crafted response that the victim workflow will treat as a legitimate external HTTP result (integrity impact on downstream workflow logic). This directly matches "cross-user response confusion" in the validation criteria, since different workflows are logically distinct consumers even when owned by the same address (e.g., multi-workflow deployments, marketplace-style workflow catalogs).

### Likelihood Explanation
Exploitability requires: (a) attacker control of a workflow under the same `WorkflowOwner` as the victim workflow, (b) knowledge/prediction of the victim's exact outbound request shape (method, URL, headers, body), and (c) the victim using `CacheSettings.Store=true` / `MaxAgeMs > 0`. This is a realistic scenario in CRE deployments where a single owner runs multiple workflows with predictable, well-known external API calls (e.g., calling a well-known price/data API). No cross-owner exploitation is possible given `WorkflowOwner` is part of the hash.

### Recommendation
Include `WorkflowID` (or an equivalent immutable workflow-scoped identifier) in `OutboundHTTPRequest.Hash()` so cache entries are strictly isolated per workflow, matching the documented design intent in `README.md`. Add/restore a regression test asserting that differing `WorkflowID` produces differing hashes (the current test at `response_cache_test.go:139-149` asserts the opposite and should be corrected as part of the fix). Also consider not caching 4xx bodies that may contain reflected sensitive request data unless explicitly opted in per-workflow.

### Proof of Concept
1. Workflow A and Workflow B share `WorkflowOwner = "0xabc"` but have distinct `WorkflowID`s.
2. Workflow A sends an `OutboundHTTPRequest{Method: "GET", URL: "https://api.example.com/data", CacheSettings: {Store: true}}` which returns (or is crafted to return, e.g. via a compromised/malicious node-controlled response path) a 200 response with attacker-chosen body.
3. Per `http_handler.go` `makeOutgoingRequest`, since `Store=true`, `h.responseCache.Set(req, outboundResp)` is called, keyed by `req.Hash()` — a hash that does not include `WorkflowID` [7](#0-6) .
4. Workflow B later sends the identical `OutboundHTTPRequest{Method: "GET", URL: "https://api.example.com/data", CacheSettings: {MaxAgeMs: 600000}}`. Because the cache key matches (same owner, same method/URL/body/headers, different `WorkflowID`), `Fetch` returns Workflow A's cached (potentially poisoned) response instead of issuing a fresh request, as directly demonstrated by the unit test asserting `WorkflowID` differences do not change the hash [5](#0-4) .

### Citations

**File:** core/services/gateway/handlers/capabilities/v2/response_cache.go (L40-44)
```go
// isCacheableStatusCode returns true if the HTTP status code indicates a cacheable response.
// This includes successful responses (2xx) and client errors (4xx)
func isCacheableStatusCode(statusCode int) bool {
	return (statusCode >= 200 && statusCode < 300) || (statusCode >= 400 && statusCode < 500)
}
```

**File:** core/services/gateway/handlers/capabilities/v2/response_cache.go (L110-120)
```go
// Set caches a response if it is cacheable (2xx or 4xx and cache is empty or expired for the given request)
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

**File:** core/services/gateway/handlers/capabilities/v2/README.md (L66-72)
```markdown

- **Cacheable Responses**: 2xx (success) and 4xx (client error) status codes.
- **Cache TTL**: Configurable, default 10 minutes
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
