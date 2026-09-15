## Analysis

The reported CVE class (webp_transform plugin "decodes unsafely and mislabels degraded responses" — i.e., a proxy/cache serves a response under labels/scope that don't match its actual origin, allowing cross-consumer response confusion) has a concrete analog in the chainlink gateway's HTTP capability response cache.

### Title
Outbound HTTP response cache key omits `WorkflowID`, allowing cross-workflow response confusion for the same owner - (File: `core/services/gateway/handlers/capabilities/v2/response_cache.go`)

### Summary
The gateway's `responseCache` used to serve outbound HTTP action responses is keyed purely by `req.Hash()` [1](#0-0) , and the request hash omits `WorkflowID`, so two different workflows belonging to the same `WorkflowOwner` that issue an identical outbound HTTP request (method, URL, headers, body) will collide on the same cache entry and can be served each other's cached responses.

### Finding Description
`responseCache.Fetch` and `responseCache.Set` both use `req.Hash()` as the sole cache key [2](#0-1) [3](#0-2) . This hash is documented as being built "from method, URL, headers, body, workflowOwner" [4](#0-3) , and the repository's own test suite confirms `WorkflowID` is explicitly excluded while `WorkflowOwner` is included: [5](#0-4) 

Meanwhile, the package's own README documents a security guarantee that directly contradicts this behavior: "**Workflow Isolation**: Cache entries are scoped by workflow ID to prevent cross-workflow data leakage" [6](#0-5) . In reality, isolation only occurs at the `WorkflowOwner` level, not at the individual `WorkflowID` level.

This is invoked from `makeOutgoingRequest`, where any node's `OutboundHTTPRequest` (parsed from an untrusted, node-forwarded JSON-RPC payload) is used directly to fetch/store the cache entry when `CacheSettings.MaxAgeMs > 0` or `CacheSettings.Store` is true: [7](#0-6) 

### Impact Explanation
A `WorkflowOwner` who deploys multiple distinct workflows (different `WorkflowID`s) that call the same upstream URL/method/headers/body — a common pattern when several workflows integrate with the same shared API — can have one workflow's HTTP action response served to a completely different workflow's HTTP action request. This breaks the documented workflow-scoped isolation, potentially causing cross-workflow response/data confusion: a workflow could receive and act on data intended for (or generated in the context of) a different, unrelated workflow execution, similar in nature to the reported CVE's "mislabeled, cacheable responses" being served to the wrong consumer.

### Likelihood Explanation
Reasonably likely in normal operation, not requiring any attacker action beyond configuring `CacheSettings` (`Store: true`, `MaxAgeMs > 0`), which is an ordinary workflow-author-controlled setting exposed via `OutboundHTTPRequest.CacheSettings` [8](#0-7) . It only requires two workflows under the same owner to issue functionally identical outbound requests, which is plausible for shared integrations (e.g., common price/data feeds) authored by the same team/owner.

### Recommendation
Include `WorkflowID` (or the full workflow identity used elsewhere, e.g. the `(workflow, execution)` tuple pattern already used in `capExecKey`/`secretsKey` [9](#0-8) ) in the cache key computation for outbound HTTP responses so that cache scoping actually matches the documented "workflow isolation" guarantee, or explicitly update the README to reflect that isolation is only owner-scoped and document the resulting risk to workflow authors sharing an owner.

### Proof of Concept
1. Workflow A (`WorkflowID = wf-A`, `WorkflowOwner = 0xOwner`) issues an `OutboundHTTPRequest{Method: "GET", URL: "https://shared-api.example.com/data", CacheSettings:{Store:true, MaxAgeMs:600000}}`; the gateway fetches and caches the live response under `req.Hash()` (which does not include `wf-A`).
2. Workflow B (`WorkflowID = wf-B`, same `WorkflowOwner = 0xOwner`) issues an identical `OutboundHTTPRequest` (same method/URL/headers/body) with `CacheSettings.MaxAgeMs > 0`.
3. Because `req.Hash()` is identical for both requests (per `response_cache_test.go` `TestRequestHash`), Workflow B receives Workflow A's cached response via `responseCache.Fetch`, despite being a logically distinct workflow — contradicting the documented per-workflow isolation guarantee.

### Citations

**File:** core/services/gateway/handlers/capabilities/v2/response_cache.go (L15-16)
```go
// responseCache is a thread-safe cache for storing HTTP responses.
// It uses a map to store responses keyed by a hash of the request (method, URL, headers, body, workflowOwner).
```

**File:** core/services/gateway/handlers/capabilities/v2/response_cache.go (L48-54)
```go
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

**File:** core/services/gateway/handlers/capabilities/v2/README.md (L69-72)
```markdown
- **Cache Key**: Generated from workflow ID and request hash
- **Cache Invalidation**: Time-based expiration with periodic cleanup
- **Cache Strategy**: All cacheable responses are cached; Non-zero `CacheSettings.MaxAgeMs` determines whether to return a cached value or make a fresh request
- **Workflow Isolation**: Cache entries are scoped by workflow ID to prevent cross-workflow data leakage
```

**File:** core/services/gateway/handlers/capabilities/v2/http_handler.go (L66-77)
```go
type ResponseCache interface {
	// Set caches a response if it is cacheable (2xx or 4xx status codes) and the cache is empty or expired for the given request.
	Set(req gateway_common.OutboundHTTPRequest, response gateway_common.OutboundHTTPResponse)

	// Fetch retrieves a response from the cache if it exists and the age of cached response is less than the max age of the request.
	// If the cached response is expired or not cached, it fetches a new response from the fetchFn.
	// The response is cached if it is cacheable and storeOnFetch is true.
	Fetch(ctx context.Context, req gateway_common.OutboundHTTPRequest, fetchFn func() gateway_common.OutboundHTTPResponse, storeOnFetch bool) gateway_common.OutboundHTTPResponse

	// DeleteExpired removes all cached responses that have exceeded their TTL (Time To Live).
	DeleteExpired(ctx context.Context) int
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

**File:** core/capabilities/confidentialrelay/response_cache.go (L17-28)
```go
// capExecKey is the deterministic cache key for a capability-exec request,
// built from its logical identity: the (workflow, execution, step, capability)
// tuple the relay-DON signature binds to. Avoids hashing: the fields are
// required non-empty by Validate, so a plain join is stable and debuggable.
func capExecKey(p confidentialrelaytypes.CapabilityRequestParams) string {
	return strings.Join([]string{capabilityCallDomain, p.WorkflowID, p.ExecutionID, p.ReferenceID, p.CapabilityID}, "/")
}

// secretsKey is the deterministic cache key for a secrets-get request, built
// from its logical identity: workflow, execution, callback id.
func secretsKey(p confidentialrelaytypes.SecretsRequestParams) string {
	return strings.Join([]string{secretsGetDomain, p.WorkflowID, p.ExecutionID, strconv.Itoa(int(p.CallbackID))}, "/")
```
