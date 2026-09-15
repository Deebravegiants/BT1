This confirms the claim is accurate based on the test evidence directly visible in the repository. The test `TestRequestHash` explicitly proves that `Hash()` produces identical output regardless of `WorkflowID` while differing for `WorkflowOwner`, and the `responseCache.Fetch`/`Set`/`isExpiredOrNotCached` functions all key exclusively on `req.Hash()` with no additional workflow-scoping logic added at the call site in `http_handler.go`. The README's documented "Workflow Isolation" guarantee is contradicted by this implementation.Audit Report

## Title
Response cache key omits WorkflowID, causing cross-workflow response leakage in HTTP Action caching - (core/services/gateway/handlers/capabilities/v2/response_cache.go)

## Summary
The `responseCache.Fetch`, `Set`, and `isExpiredOrNotCached` methods key cached HTTP action responses solely on `gateway.OutboundHTTPRequest.Hash()`, and the repository's own test suite explicitly confirms `Hash()` ignores `WorkflowID` while distinguishing on `WorkflowOwner`. This contradicts the documented "Workflow Isolation" guarantee in the package README and allows two different workflows sharing the same `WorkflowOwner` to collide on the same cache entry when their requests have identical method/URL/headers/body.

## Finding Description
`isExpiredOrNotCached`, `Fetch`, and `Set` all use `req.Hash()` as the sole cache map key with no additional workflow-scoping applied anywhere in the call chain: [1](#0-0) [2](#0-1) [3](#0-2) 

The struct's own comment states the hash covers "method, URL, headers, body, workflowOwner" — omitting `WorkflowID`: [4](#0-3) 

This is directly and explicitly proven by the existing test suite, which asserts the hash is unaffected by `WorkflowID` while it does change with `WorkflowOwner`: [5](#0-4) [6](#0-5) 

The gateway handler passes the full `OutboundHTTPRequest` (including `CacheSettings`) straight to `Fetch`/`Set` without adding any workflow-level key derivation of its own, so nothing outside `Hash()` mitigates the gap: [7](#0-6) 

The package README explicitly documents an isolation guarantee that is not actually implemented in code: [8](#0-7) 

The `Hash()` implementation itself lives in the external `chainlink-common` dependency (`github.com/smartcontractkit/chainlink-common/pkg/types/gateway`) and is not vendored in this repository, so its exact implementation could not be directly inspected here; however, its behavior is unambiguously pinned down by the passing unit tests in this repo, which is sufficient to establish the root cause.

## Impact Explanation
Two different workflows belonging to the same `WorkflowOwner` that issue outbound HTTP Action requests with identical method/URL/headers/body will collide on the same cache slot. This means workflow B can receive workflow A's cached HTTP response (or vice versa) purely due to the key collision, violating the documented workflow isolation property and constituting cross-workflow response corruption/leakage — a legitimate, concrete in-scope impact category (cross-user response corruption) for HTTP Action outputs consumed by workflow execution.

## Likelihood Explanation
The precondition (same `WorkflowOwner`, multiple workflows, identical outbound request shape, with `CacheSettings.Store`/`MaxAgeMs` enabled) is a realistic and common configuration for a workflow owner running several similar workflows against shared/templated third-party APIs. No privileged access, malicious node behavior, or host-level compromise is required — any workflow author under the same owner can trigger this simply by using the caching feature of the standard HTTP Action, which is intended for use by unprivileged workflow authors.

## Recommendation
Include `WorkflowID` in the `OutboundHTTPRequest.Hash()` computation (in the `chainlink-common` package) so that responses cached for one workflow cannot be returned to a different workflow's HTTP Action call, matching the documented "Workflow Isolation" guarantee. Update the existing `TestRequestHash` subtest ("having different workflowID results in same Hash") to instead assert that differing `WorkflowID` values produce different hashes.

## Proof of Concept
1. Workflow `wf-A` (owner `0xOwner1`) issues `OutboundHTTPRequest{Method: "GET", URL: "https://api.example.com/data", WorkflowOwner: "0xOwner1", WorkflowID: "wf-A", CacheSettings: {Store: true}}`; the gateway executes it via `makeOutgoingRequest` and stores the response via `responseCache.Set`, keyed by `req.Hash()`.
2. Workflow `wf-B` (same owner, `WorkflowID: "wf-B"`, identical method/URL/headers/body) issues the same request with `CacheSettings.MaxAgeMs > 0`.
3. Because `Hash()` ignores `WorkflowID` (proven by `TestRequestHash` at `response_cache_test.go:139-149`), `Fetch` for `wf-B` resolves the same cache key as `wf-A`'s entry and returns `wf-A`'s cached response directly to `wf-B`, as shown in the `Fetch` cache-hit path at `response_cache.go:74-77` which returns `cachedResp.response` without any workflow-identity check.

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

**File:** core/services/gateway/handlers/capabilities/v2/http_handler.go (L404-443)
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
		h.metrics.IncrementActionCapabilityRequestCount(ctx, nodeAddr, h.lggr)
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
