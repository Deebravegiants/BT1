### Title
Gateway HTTP-action response cache key omits `WorkflowID`, breaking the documented workflow-isolation guarantee and allowing cross-workflow response/cache confusion - ([File: core/services/gateway/handlers/capabilities/v2/response_cache.go])

### Summary
The `responseCache` used by the Gateway's HTTP Action handler is documented as being "workflow-scoped" and keyed by "workflow ID and request hash" to prevent cross-workflow data leakage, but the actual cache key (`req.Hash()`) does not incorporate `WorkflowID`. Two different workflows (sharing the same `WorkflowOwner`) issuing an outbound HTTP action with the same method/URL/headers/body will collide on the same cache entry and one workflow can be served the cached HTTP response that was fetched and stored in the context of a different workflow, independent of each workflow's own freshness/store settings.

### Finding Description
`gatewayHandler.makeOutgoingRequest` reads the caller-supplied `OutboundHTTPRequest` (unmarshalled directly from a node message) and dispatches it either through `responseCache.Fetch` or `responseCache.Set`, using `req.Hash()` as the sole cache key: [1](#0-0) 

The cache implementation stores/retrieves entries purely by this hash: [2](#0-1) 

The package README explicitly documents the intended security property: *"Cache Key: Generated from workflow ID and request hash"* and *"Workflow Isolation: Cache entries are scoped by workflow ID to prevent cross-workflow data leakage"*: [3](#0-2) 

However, the unit tests for `req.Hash()` prove the opposite of that documented guarantee — `WorkflowID` has no effect on the hash, while `CacheSettings` (which carries each workflow's own `MaxAgeMs`/`Store` freshness policy) is also excluded: [4](#0-3) 

So the cache key is effectively `hash(method, URL, headers, body, WorkflowOwner)`, not `hash(WorkflowID, request)` as documented. Any two distinct workflows belonging to the same owner that issue an outbound HTTP action with identical method/URL/headers/body will read and write the same cache slot, even though they are logically distinct execution contexts (`WorkflowID` differs) and may have different freshness requirements.

This is the same underlying bug class as the external report (`getDollarPriceUsd` returning a price without verifying it is not stale/foreign to the current context): the Gateway serves data from a cache entry without validating that it was actually produced for the requesting logical context (here, the requesting workflow), only checking a time-based freshness window against the *requester's own* `MaxAgeMs` — never checking that the stored entry actually belongs to the requesting workflow.

### Impact Explanation
- Violates the explicitly documented workflow-isolation security control ("prevent cross-workflow data leakage"), which auditors and integrators rely on.
- A workflow with a strict freshness requirement (e.g. small `MaxAgeMs` for near-real-time data) can be served a response that was fetched to satisfy a different, unrelated workflow's request (potentially with looser freshness needs or different trust assumptions), since `CacheSettings` are excluded from the hash and workflow identity is only partially represented (`WorkflowOwner`, not `WorkflowID`).
- If the two workflows are not intended to be equivalent trust domains (e.g. one workflow processes data destined for external disclosure while another is more sensitive), the crossed cache entry causes cross-workflow response confusion, which can leak data or cause a workflow to act on data it did not request.
- Severity is Medium: it requires the coincidence of identical outbound requests (same method/URL/headers/body) from two workflows under the same owner, and the leaked value is limited to the (identical) fetched response, but it clearly contradicts the documented isolation boundary and can misinform downstream decisions.

### Likelihood Explanation
Reachable directly from any unprivileged workflow-node acting through the Gateway HTTP capability, without any privilege escalation: the message is a normal `HandleNodeMessage` outbound HTTP action request that any node/workflow already authorized to use the HTTP capability can issue. No special network position or additional authentication bypass is needed — only that another workflow (same owner) makes a request with an identical hash input. Given multiple workflows commonly querying the same well-known third-party endpoint with default headers/body, this collision is plausible in normal usage, not merely a contrived edge case.

### Recommendation
Include `WorkflowID` (and ideally the per-request `CacheSettings`, or at minimum enforce workflow-scoped cache partitioning) in the cache key used by `responseCache`, so that `Fetch`/`Set`/`DeleteExpired` operate on workflow-scoped keys as documented, e.g. compute the key as `hash(WorkflowID, req.Hash())` rather than `req.Hash()` alone. This restores the documented isolation guarantee and prevents one workflow's HTTP action from ever reading a cache entry populated by another workflow's request.

### Proof of Concept
1. Workflow A (`WorkflowID = "wf-A"`, `WorkflowOwner = "owner-1"`) issues an `OutboundHTTPRequest{Method: "GET", URL: "https://api.example.com/data", CacheSettings:{Store:true, MaxAgeMs:600000}}` through the Gateway. The response is cached under `req.Hash()` (per `response_cache.go` `Fetch`/`Set`).
2. Workflow B (`WorkflowID = "wf-B"`, same `WorkflowOwner = "owner-1"`) issues an outbound request with the *same* method/URL/headers/body but its own freshness policy (e.g. `MaxAgeMs: 1000`, expecting near-real-time data).
3. Because `req.Hash()` does not include `WorkflowID` (proved by `TestRequestHash`'s "having different workflowID results in same Hash" subtest), Workflow B's `Fetch` call hits the same cache entry Workflow A stored, and is served Workflow A's fetched response as long as it is younger than Workflow B's own `MaxAgeMs` — despite the two calls belonging to entirely separate workflow executions. [5](#0-4)

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

**File:** core/services/gateway/handlers/capabilities/v2/response_cache_test.go (L121-149)
```go
	t.Run("having different cacheSettings results in the same Hash", func(t *testing.T) {
		req1 := createTestRequest("GET", "https://example.com")
		req1.CacheSettings = gateway_common.CacheSettings{
			MaxAgeMs: 5000,
			Store:    true,
		}

		req2 := createTestRequest("GET", "https://example.com")
		req2.CacheSettings = gateway_common.CacheSettings{
			MaxAgeMs: 10000,
			Store:    false,
		}

		hash1 := req1.Hash()
		hash2 := req2.Hash()
		require.Equal(t, hash1, hash2, "Hash should be the same regardless of CacheSettings")
	})

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
