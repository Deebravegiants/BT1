Audit Report

## Title
HTTP Action response cache key omits `WorkflowID`, causing cross-workflow response confusion despite documented "workflow isolation" - (core/services/gateway/handlers/capabilities/v2/response_cache.go)

## Summary
The gateway's HTTP Action response cache in `core/services/gateway/handlers/capabilities/v2/response_cache.go` keys cached responses solely by `req.Hash()`, and the request's `Hash()` implementation (from `chainlink-common/pkg/types/gateway`) intentionally excludes `WorkflowID`, as explicitly confirmed by the test `TestRequestHash`'s subtest "having different workflowID results in same Hash". This directly contradicts the package's own `README.md`, which documents "Cache Key: Generated from workflow ID and request hash" and "Workflow Isolation: Cache entries are scoped by workflow ID to prevent cross-workflow data leakage."

## Finding Description
`Fetch` and `Set` both use `req.Hash()` as the sole cache key: [1](#0-0) [2](#0-1) 

The type's own doc comment states the key is derived from "method, URL, headers, body, workflowOwner" — notably omitting `WorkflowID`: [3](#0-2) 

The test suite explicitly asserts and documents this behavior as the actual implementation: two requests differing only in `WorkflowID` produce identical hashes, while a fixed `WorkflowOwner` and identical request fields also hash identically: [4](#0-3) 

Meanwhile, the `Fetch` cache-hit path returns the cached response without invoking `fetchFn` at all, which is directly demonstrated in `TestFetch`'s "returns cached response when cache hit" subtest. Since the cache is populated and consulted per (method, URL, headers, body, owner) but not per workflow, two distinct workflows belonging to the same owner that issue an identical outbound HTTP request (same URL/method/headers/body) within the TTL window will collide on the same cache entry, and the second workflow's `Fetch` call will silently return the first workflow's cached response instead of performing its own fetch. This is consulted from the node-facing request handling path in `http_handler.go`, reachable by any workflow performing an HTTP Action capability call. [5](#0-4) 

No existing check re-validates `WorkflowID` before returning a cached entry, so the documented isolation guarantee in the README is not actually enforced by the code.

## Impact Explanation
This is a cross-workflow response corruption bug: a workflow can receive another workflow's previously cached HTTP response body/status/headers instead of a fresh response corresponding to its own request, purely because they share an owner and an identical request shape. This falls into the in-scope "cross-user response corruption" impact category — a workflow's execution can silently branch on stale or foreign data it never actually requested, breaking the correctness guarantees that `CacheSettings.MaxAgeMs`/`Store` are meant to provide.

## Likelihood Explanation
No privilege escalation or attacker interaction beyond normal workflow operation is required. Any account/owner running two or more workflows that call the same external endpoint with matching method/URL/headers/body (a common pattern such as shared utility/config endpoints) will trigger this under ordinary use whenever `CacheSettings.MaxAgeMs > 0`, making this a realistic, repeatable collision rather than a contrived edge case.

## Recommendation
Include `WorkflowID` in the cache key hash computation (`OutboundHTTPRequest.Hash()` in `chainlink-common/pkg/types/gateway`) as the README already documents, or otherwise namespace `responseCache.cache` by `WorkflowID` in addition to the existing request/owner-derived key, ensuring cache entries cannot cross workflow boundaries.

## Proof of Concept
1. Run `TestRequestHash`'s "having different workflowID results in same Hash" subtest in `core/services/gateway/handlers/capabilities/v2/response_cache_test.go` (lines 139-149) — it passes, confirming two requests differing only by `WorkflowID` hash identically.
2. Extend `TestFetch` with: Workflow A (`WorkflowID: "wf-A"`, owner `X`) calls `Fetch` with a `fetchFn` returning response R1, `CacheSettings.MaxAgeMs > 0`, `Store: true`; this populates the cache under `req.Hash()`.
3. Workflow B (`WorkflowID: "wf-B"`, same owner `X`, identical method/URL/headers/body) calls `Fetch` with a `fetchFn` returning a different response R2, within the TTL window.
4. Assert `fetchFn` for Workflow B is never invoked and the returned response equals R1 (Workflow A's cached response), demonstrating the cross-workflow leak — analogous to the existing "returns cached response when cache hit" subtest at lines 230-250.

### Citations

**File:** core/services/gateway/handlers/capabilities/v2/response_cache.go (L15-16)
```go
// responseCache is a thread-safe cache for storing HTTP responses.
// It uses a map to store responses keyed by a hash of the request (method, URL, headers, body, workflowOwner).
```

**File:** core/services/gateway/handlers/capabilities/v2/response_cache.go (L66-68)
```go
func (rc *responseCache) Fetch(ctx context.Context, req gateway.OutboundHTTPRequest, fetchFn func() gateway.OutboundHTTPResponse, storeOnFetch bool) gateway.OutboundHTTPResponse {
	cacheKey := req.Hash()
	cacheMaxAge := time.Duration(req.CacheSettings.MaxAgeMs) * time.Millisecond
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

**File:** core/services/gateway/handlers/capabilities/v2/http_handler.go (L432-442)
```go
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
