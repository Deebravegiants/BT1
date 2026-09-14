Based on my investigation, I found a concrete analog to the FreshRSS favicon cache-poisoning bug class in the gateway's HTTP capability response cache.

### Title
Cross-workflow HTTP response cache poisoning due to WorkflowID being excluded from cache key - (File: core/services/gateway/handlers/capabilities/v2/response_cache.go)

### Summary
The gateway's `responseCache`, used to cache outbound HTTP Action responses for CRE workflow nodes, keys cached entries using `gateway.OutboundHTTPRequest.Hash()`. The package README explicitly documents "Cache Key: Generated from workflow ID and request hash" and "Workflow Isolation: Cache entries are scoped by workflow ID to prevent cross-workflow data leakage" [1](#0-0) , but the actual cache key comment and tests show the hash is built from "method, URL, headers, body, workflowOwner" — explicitly excluding `WorkflowID` [2](#0-1) .

### Finding Description
`responseCache.Fetch` and `responseCache.Set` both key the cache map purely on `req.Hash()` [3](#0-2) . The dedicated test suite directly proves that two requests with different `WorkflowID` values but the same URL/method/headers/body/owner produce the *same* hash: `"having different workflowID results in same Hash"` asserts `require.Equal(t, hash1, hash2, "Hash should be the same regardless of WorkflowID")` [4](#0-3) . This is the exact structural analog of the FreshRSS bug: a cache/poisoning-relevant identity field (there, proxy/SSL settings; here, `WorkflowID`) is silently omitted from the hash used as the cache key, while consumer-facing documentation/behavior implies per-identity isolation that does not actually exist.

Any workflow node request flowing through `makeOutgoingRequest` populates the cache using this hash and, when `CacheSettings.MaxAgeMs > 0`, subsequent requests for the same URL/method/headers/body (regardless of `WorkflowID`) served by any workflow sharing that `WorkflowOwner` will be served the previously cached response via `Fetch` [5](#0-4) .

### Impact Explanation
If an owner runs multiple distinct workflows (e.g., differing security assumptions, using the shared cache unintentionally), a response fetched/cached by one workflow can be served to a completely different workflow under the same owner without a fresh fetch, defeating the "workflow isolation" guarantee stated in the design doc. This can lead to stale/cross-workflow data being consumed by an unrelated workflow execution, and — depending on how the HTTP Action capability is otherwise scoped/authorized per workflow — could allow one workflow's cached HTTP response (potentially attacker-influenced content from an external endpoint) to be delivered into a different workflow's execution context, similar in effect to the favicon cache poisoning across unrelated FreshRSS feeds/users.

### Likelihood Explanation
This requires only that: (1) the same `WorkflowOwner` runs (or can register) two workflows that hit HTTP Action requests with identical method/URL/headers/body, and (2) `CacheSettings.MaxAgeMs > 0` on the request (attacker/workflow-controlled from `OutboundHTTPRequest`). No privileged access beyond normal workflow-node/owner capability is needed — the request parameters, including `CacheSettings`, are controlled by the workflow itself when constructing the `OutboundHTTPRequest` sent through the HTTP Action capability [5](#0-4) .

### Recommendation
Include `WorkflowID` (or an execution-scoped identifier) in the cache key computed in `req.Hash()`/`responseCache`, or explicitly document and enforce that the cache is scoped at the owner level rather than workflow level, and audit whether that weaker scope is acceptable. Add a regression test asserting `WorkflowID` *does* affect the hash if per-workflow isolation is the intended guarantee (the current test asserts the opposite).

### Proof of Concept
1. Workflow A (owner `0xABC`, `WorkflowID = "wf-1"`) issues an HTTP Action request: `GET https://victim.example/data`, `CacheSettings.MaxAgeMs = 600000, Store = true`. The gateway fetches and caches the response keyed by `req.Hash()` (method+URL+headers+body+owner, no `WorkflowID`) [2](#0-1) [6](#0-5) .
2. Workflow B (same owner `0xABC`, different `WorkflowID = "wf-2"`) issues the identical request shape. Per `TestRequestHash`'s `"having different workflowID results in same Hash"` case, this computes the same cache key [4](#0-3) .
3. `responseCache.Fetch` returns Workflow A's cached response to Workflow B without making a new HTTP call, violating the documented "Workflow Isolation" cache scoping [1](#0-0) .

**Uncertainty note**: The actual `Hash()` method implementation lives in the external `chainlink-common` package (`github.com/smartcontractkit/chainlink-common/pkg/types/gateway`), which is outside this repo's index; I could not directly inspect its full field list, but the in-repo comment and comprehensive test suite in this repository conclusively confirm the exclusion of `WorkflowID` and inclusion of `WorkflowOwner`. If `chainlink-common` is treated strictly as an external dependency, this could be classified as "dependency-only" per the scope rules — however, the cache poisoning surface and impact are realized entirely within this repo's gateway handler code path (`response_cache.go`, `http_handler.go`), which is why I'm reporting it as a reachable, in-scope analog rather than a pure dependency bug.

### Citations

**File:** core/services/gateway/handlers/capabilities/v2/README.md (L66-72)
```markdown

- **Cacheable Responses**: 2xx (success) and 4xx (client error) status codes.
- **Cache TTL**: Configurable, default 10 minutes
- **Cache Key**: Generated from workflow ID and request hash
- **Cache Invalidation**: Time-based expiration with periodic cleanup
- **Cache Strategy**: All cacheable responses are cached; Non-zero `CacheSettings.MaxAgeMs` determines whether to return a cached value or make a fresh request
- **Workflow Isolation**: Cache entries are scoped by workflow ID to prevent cross-workflow data leakage
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
