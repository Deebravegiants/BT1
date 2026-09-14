### Title
Outbound HTTP action response cache is keyed only by owner, not by workflow, allowing cross-workflow cache-result confusion - ([File: core/services/gateway/handlers/capabilities/v2/response_cache.go])

### Summary
The gateway's outbound HTTP action `responseCache` deduplicates and serves cached HTTP responses using `OutboundHTTPRequest.Hash()` as the sole cache key. That hash intentionally excludes `WorkflowID` and `CacheSettings`, including only method/URL/headers/body/`WorkflowOwner`. This contradicts the component's own documented invariant ("Workflow Isolation: Cache entries are scoped by workflow ID to prevent cross-workflow data leakage") and lets a cached response produced for one workflow be transparently served to a different workflow belonging to the same owner, as long as method/URL/headers/body match.

### Finding Description
`gatewayHandler.makeOutgoingRequest` receives an `OutboundHTTPRequest` originating from a workflow-run HTTP Action capability (attacker/workflow-controlled fields: `Method`, `URL`, `Headers`/`MultiHeaders`, `Body`, `CacheSettings`, `WorkflowID`, `WorkflowOwner`) and, when `CacheSettings.MaxAgeMs > 0`, calls `h.responseCache.Fetch(...)`: [1](#0-0) 

`responseCache.Fetch`/`Set` key the cache map purely by `req.Hash()`: [2](#0-1) 

The package comment even documents the intended key composition ("method, URL, headers, body, workflowOwner") — `WorkflowID` is deliberately absent: [3](#0-2) 

This is explicitly confirmed by the test suite, which asserts that two requests with different `WorkflowID` produce the **same** hash (so they collide in the cache), while only differing `WorkflowOwner` changes the hash: [4](#0-3) 

Yet the module's own README states the opposite guarantee — that cache entries are scoped per-workflow to prevent cross-workflow data leakage, and that the cache key is generated "from workflow ID and request hash": [5](#0-4) 

This is the same class of defect as the Popsicle Finance incident: a single stored record (here, one cache entry keyed on request content) is shared/attributed to multiple distinct principals (here, multiple workflows of the same owner) because the record's key omits the field that should have partitioned it (workflow identity), so state intended to be scoped to one workflow instead "pays out" (serves) the same cached result to any other request that hashes to the same key.

### Impact Explanation
Two different workflows running under the same `WorkflowOwner` that happen to issue an HTTP Action with identical method/URL/headers/body (a very plausible collision for common APIs, e.g. shared partner/price/reference endpoints) will read and write into the exact same cache slot regardless of `WorkflowID`. Concretely:
- Workflow B can receive a response that was actually fetched/cached on behalf of Workflow A (stale/wrong business data delivered cross-workflow), including any response body/headers that were cached (e.g., `Set-Cookie` or other response metadata is preserved in `MultiHeaders`, as seen in the multiheaders test).
- A workflow author who intends `CacheSettings.Store=false` for a sensitive one-off call can still be served (or can pollute) a cache entry populated by another workflow's request with `Store=true`, since `CacheSettings` is also excluded from the hash.
- This violates the explicitly documented workflow-isolation guarantee, producing cross-workflow response confusion without any authentication or ownership check preventing it.

The impact is bounded to workflows sharing the same owner (the hash does include `WorkflowOwner`, so cross-owner leakage does not occur), which limits severity compared to a full cross-tenant leak, but it still breaks a documented per-workflow trust/isolation boundary purely through workflow-controlled request fields.

### Likelihood Explanation
Any workflow (an unprivileged party relative to other workflows of the same owner) can trigger this simply by issuing an HTTP Action request with `CacheSettings.MaxAgeMs > 0` and a URL/method/body that coincides with another workflow's outbound call — no special permissions, races, or edge conditions are required beyond normal HTTP Action usage. It is a deterministic consequence of the cache key design, not a timing-dependent race.

### Recommendation
Include `WorkflowID` (and ideally `CacheSettings`-relevant scoping decisions) in `OutboundHTTPRequest.Hash()`/cache key computation so that `responseCache` entries are truly scoped per workflow, matching the documented isolation guarantee in `core/services/gateway/handlers/capabilities/v2/README.md`. At minimum, update either the code to match the documented workflow-scoped isolation, or update the documentation and add explicit safeguards (e.g., reject/ignore caching between different workflows) if owner-level sharing is intentional.

### Proof of Concept
1. Workflow A (owner `O`) issues an HTTP Action: `GET https://api.example.com/data`, `CacheSettings{Store:true, MaxAgeMs:600000}`, `WorkflowID:"wf-A"`. The gateway fetches from the external endpoint and calls `responseCache.Set`, storing under `req.Hash()` (owner+method+url+headers+body only).
2. Workflow B (same owner `O`, different `WorkflowID:"wf-B"`) issues the identical `GET https://api.example.com/data` shortly after, with `CacheSettings.MaxAgeMs > 0`.
3. Per `TestRequestHash`'s "having different workflowID results in same Hash" assertion, `req.Hash()` for Workflow B equals Workflow A's, so `responseCache.Fetch` returns Workflow A's cached response to Workflow B without ever contacting the external endpoint or checking `WorkflowID`. [6](#0-5) [7](#0-6)

### Citations

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

**File:** core/services/gateway/handlers/capabilities/v2/response_cache.go (L66-120)
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
