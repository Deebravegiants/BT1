## Analog Found

### Title
Gateway `responseCache` caches and replays `Set-Cookie`/session response headers across different workflows under the same owner, contradicting the documented workflow isolation - ([File: core/services/gateway/handlers/capabilities/v2/response_cache.go])

### Summary
The Symfony advisory concerns a reverse-proxy HTTP cache that stores `Set-Cookie` response headers and replays them to unrelated clients, leaking session identifiers. The chainlink gateway's outbound-HTTP-action `responseCache` exhibits the same bug class: it caches complete `OutboundHTTPResponse` objects (including all response headers, e.g. `Set-Cookie`) and serves them to subsequent requests whose cache key does not actually distinguish between different workflows, despite the component's own documentation claiming workflow-level isolation.

### Finding Description
`responseCache.Set` and `responseCache.Fetch` store the entire `gateway_common.OutboundHTTPResponse` — which can include arbitrary response headers such as `Set-Cookie` — keyed only by `req.Hash()`: [1](#0-0) 

The handler test suite demonstrates that responses with multiple `Set-Cookie` headers (session id, CSRF token, etc.) flow straight through the cache/response pipeline unmodified: [2](#0-1) 

The project's own README claims the cache is isolated per workflow to prevent leakage: [3](#0-2) [4](#0-3) 

However, `TestRequestHash` proves the cache key explicitly ignores `WorkflowID` while only depending on `WorkflowOwner`: [5](#0-4) [6](#0-5) 

So two *different* workflows belonging to the same owner that issue an outbound HTTP action with the same method/URL/body/headers (a very plausible scenario for shared integrations, e.g. a common webhook/login/API-key exchange endpoint reused across a customer's workflows) will collide on the same cache entry. If the external endpoint returns a per-invocation `Set-Cookie` (session token, one-time nonce, auth cookie), that header is cached and replayed verbatim to the second workflow's execution via `sendResponseToNode`, exactly mirroring the Symfony `HttpCache`/`Set-Cookie` cross-response leakage — except the boundary crossed here is "workflow" rather than "browser session," which is the isolation guarantee the code documents and fails to enforce.

The cache lookup/store path is invoked from `makeOutgoingRequest`: [7](#0-6) 

### Impact Explanation
An attacker-controlled or misbehaving workflow (or simply an unrelated legitimate workflow under the same owner) that happens to issue an outbound HTTP action identical in method/URL/headers/body to another workflow's request can receive that other workflow's cached response, including any session cookie, CSRF token, or other secret embedded in `Set-Cookie`/response headers returned by the external endpoint. This is a cross-workflow response confusion / session-token disclosure within the owner's trust boundary — the exact impact category the report is about (CWE-285, improper authorization of cached private data).

### Likelihood Explanation
Requires: (1) `CacheSettings.Store`/`MaxAgeMs` enabled by the requesting workflow (attacker-controlled, since it's set in the workflow's own outbound request), (2) two workflows under the same owner issuing byte-identical outbound requests to an endpoint that emits per-call session/auth cookies. Both conditions are plausible in shared-integration setups (e.g. an owner running several workflows against the same third-party API/login endpoint) and are entirely reachable without any additional privilege — the cache-control knob is caller-supplied.

### Recommendation
Include `WorkflowID` (and ideally `ExecutionID` for one-shot session-bearing endpoints) in the cache key so entries cannot cross workflow boundaries, matching the README's documented guarantee. Additionally, strip or refuse to cache well-known private headers (`Set-Cookie`, `Authorization`, etc.) from cached responses by default, similar to Symfony's fix of stripping `Set-Cookie` in `HttpStore`, unless the workflow explicitly opts in.

### Proof of Concept
1. Workflow A (owner `O`) issues an `OutboundHTTPRequest{Method: GET, URL: https://svc/login, Headers: {...}, CacheSettings:{Store:true, MaxAgeMs: 600000}}`. The external endpoint replies `200` with `Set-Cookie: session=abc123`.
2. `responseCache.Set`/`Fetch` stores this response keyed by `req.Hash()`, which per `TestRequestHash` depends on method/URL/headers/body/`WorkflowOwner` but **not** `WorkflowID`.
3. Workflow B, also owned by `O` but functionally unrelated, issues an outbound request with the identical method/URL/headers/body (e.g., a shared upstream dependency) within the TTL window.
4. Because the hash collides, `responseCache.Fetch` returns Workflow A's cached response — including `Set-Cookie: session=abc123` — to Workflow B, disclosing Workflow A's session token to a different workflow execution.

### Citations

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

**File:** core/services/gateway/handlers/capabilities/v2/http_handler_test.go (L151-164)
```go
		// Response with multiple Set-Cookie headers
		httpResp := &network.HTTPResponse{
			StatusCode: 200,
			Headers: map[string]string{
				"Set-Cookie": "sessionid=abc123; Path=/; HttpOnly",
			},
			MultiHeaders: map[string][]string{
				"Set-Cookie": {
					"sessionid=abc123; Path=/; HttpOnly",
					"csrf_token=xyz789; Path=/; Secure",
				},
			},
			Body: []byte(`{"result": "success"}`),
		}
```

**File:** core/services/gateway/handlers/capabilities/v2/README.md (L46-49)
```markdown
#### 2.1.4 Response Cache (`responseCache`)
- **Purpose**: Caches HTTP responses to avoid redundant outbound requests
- **Functions**: TTL-based caching that optionally returns cached values based on max age parameter
- **Key Features**: Workflow-scoped caching
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

**File:** core/services/gateway/handlers/capabilities/v2/http_handler.go (L433-442)
```go
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
