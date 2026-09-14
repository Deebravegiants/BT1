## Finding: Gateway HTTP Action response cache leaks cached response headers (including session/auth tokens) across different workflows of the same owner

### Title
Cross-Workflow HTTP Response Cache Poisoning/Leakage in Gateway HTTP Action Handler - ([File: core/services/gateway/handlers/capabilities/v2/response_cache.go])

### Summary
The Gateway's HTTP Action v2 handler caches outbound HTTP responses (including all response headers such as `Set-Cookie`, auth tokens, etc.) keyed by a hash of the request. The documentation claims the cache is workflow-scoped ("Workflow Isolation: Cache entries are scoped by workflow ID to prevent cross-workflow data leakage"), but the actual `Hash()` implementation deliberately excludes `WorkflowID` from the key, keying only on method/URL/headers/body/`WorkflowOwner`. This is directly analogous to the CouchDB bug class: a shared execution surface (the design-document script sandbox in CouchDB; the HTTP response cache here) exposes response data — including session/authorization headers — to a different consumer than the one that originated the request.

### Finding Description
`responseCache.Fetch`/`Set` key entries by `req.Hash()`: [1](#0-0) [2](#0-1) 

The test suite explicitly documents and asserts that identical requests with different `WorkflowID` produce the *same* hash, while different `WorkflowOwner` produces a different hash: [3](#0-2) 

This contradicts the component's own documented guarantee: [4](#0-3) 

The cached value is the full `OutboundHTTPResponse`, including headers/`MultiHeaders` (e.g. `Set-Cookie`, bearer/session tokens returned by the external endpoint), body, and status code, as populated in `createHTTPRequestCallback`: [5](#0-4) 

Because the cache key omits `WorkflowID`, any two workflows deployed under the same workflow owner that issue the same method/URL/headers/body combination (a routine occurrence for common HTTP Action calls, e.g. hitting the same third-party API endpoint with the same static headers) will silently share the cached response for the configured TTL (`Store`/`MaxAgeMs`), as driven from `makeOutgoingRequest`: [6](#0-5) 

If the external endpoint returns a session cookie, CSRF token, or per-caller authorization artifact tied to the requesting workflow's specific context (e.g. an OAuth/session exchange endpoint, or an endpoint that embeds a per-workflow token in the response), a second, unrelated workflow belonging to the same owner receives that first workflow's session/auth material via the cache — a direct HTTP-header/session leak across workflow boundaries, matching the CouchDB CVE's "leak session headers to whoever accesses the shared resource" bug class.

### Impact Explanation
An unprivileged workflow author (any workflow deployed under a given owner address) can obtain another workflow's cached HTTP response — including any session cookies, CSRF tokens, or authorization headers returned by an external endpoint for that other workflow's request — simply by crafting an HTTP Action request with an identical method/URL/headers/body and enabling caching (`CacheSettings.Store`/`MaxAgeMs`). This is a cross-workflow information disclosure / session-hijacking primitive, since sensitive response headers are shared outside the intended workflow-scoped boundary that the system explicitly claims to enforce.

### Likelihood Explanation
Exploitation requires: (1) the same workflow owner operating multiple workflows (common in production, and trivially satisfiable by an attacker who owns/controls two workflow deployments), (2) both workflows issuing byte-identical outbound HTTP requests (method, URL, headers, body) with caching enabled, which is a normal, unprivileged, documented capability configuration (`gateway_common.CacheSettings`). No malicious node, gateway operator, or network-layer compromise is required — an ordinary workflow developer can trigger this purely through the HTTP Action capability's public request interface.

### Recommendation
Include `WorkflowID` (not just `WorkflowOwner`) in the cache key computation (`OutboundHTTPRequest.Hash()`) so that cached entries are truly workflow-scoped, matching the documented guarantee. Additionally, review whether `Set-Cookie`/authorization-bearing headers should be excluded from caching entirely, or the cache should only store idempotent/non-session-bearing response fields.

### Proof of Concept
1. Workflow A (owner `0xOwner`) issues an HTTP Action request: `GET https://api.example.com/session` with `Content-Type: application/json`, `CacheSettings{Store: true, MaxAgeMs: 600000}`. The endpoint returns `Set-Cookie: sessionid=<A's-secret>` bound to workflow A's request context.
2. Gateway caches the response keyed by `Hash(method, url, headers, body, workflowOwner)` — note `workflowID` is not part of the key, as demonstrated in `TestRequestHash` ("having different workflowID results in same Hash").
3. Workflow B, deployed under the same owner `0xOwner` but otherwise unrelated, issues the identical `GET https://api.example.com/session` request with the same headers/body and `CacheSettings.MaxAgeMs > 0`.
4. Because the hash matches, the gateway serves Workflow A's cached response — including `Set-Cookie: sessionid=<A's-secret>` — to Workflow B, in violation of the intended workflow isolation.

### Citations

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

**File:** core/services/gateway/handlers/capabilities/v2/response_cache.go (L66-108)
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

	// Slow path: singleflight deduplicates concurrent fetches per key.
	// Cache check + store happen inside the flight so the key isn't released
	// until the result is cached, closing the race window between singleflight
	// completion and cache write.
	result, _, _ := rc.flight.Do(cacheKey, func() (any, error) {
		// Re-check cache: a previous flight may have just stored the result.
		rc.cacheMu.RLock()
		cachedResp, exists := rc.cache[cacheKey]
		rc.cacheMu.RUnlock()
		if exists && cachedResp.storedAt.Add(cacheMaxAge).After(time.Now()) {
			rc.metrics.IncrementCacheHitCount(ctx, rc.lggr)
			return cachedResp.response, nil
		}

		response := fetchFn()

		if storeOnFetch && isCacheableStatusCode(response.StatusCode) {
			rc.cacheMu.Lock()
			rc.cache[cacheKey] = &cachedResponse{
				response: response,
				storedAt: time.Now(),
			}
			rc.cacheMu.Unlock()
		}

		return response, nil
	})

	return result.(gateway.OutboundHTTPResponse)
}
```

**File:** core/services/gateway/handlers/capabilities/v2/response_cache_test.go (L139-176)
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

**File:** core/services/gateway/handlers/capabilities/v2/http_handler.go (L375-385)
```go
		l.Debugw("Received HTTP response", "responseBodySize", len(resp.Body), "statusCode", resp.StatusCode, "numHeaders", len(resp.Headers))
		h.metrics.IncrementCustomerEndpointResponseCount(ctx, strconv.Itoa(resp.StatusCode), h.lggr)
		h.metrics.RecordCustomerEndpointRequestLatency(ctx, time.Since(start).Milliseconds(), h.lggr)
		return gateway_common.OutboundHTTPResponse{
			StatusCode:              resp.StatusCode,
			Headers:                 resp.Headers, //nolint:staticcheck // Headers is deprecated in OutboundHTTPResponse, but populated for backwards compatibility
			MultiHeaders:            resp.MultiHeaders,
			Body:                    resp.Body,
			ExternalEndpointLatency: externalEndpointLatency,
		}
	}
```

**File:** core/services/gateway/handlers/capabilities/v2/http_handler.go (L425-442)
```go
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
