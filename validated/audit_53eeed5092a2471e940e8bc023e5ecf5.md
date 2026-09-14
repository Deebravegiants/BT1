### Title
Response cache key omits `MaxResponseBytes`, allowing a workflow request's own response-size bound to be silently bypassed via a cached response fetched under a larger/unbounded limit - (File: core/services/gateway/handlers/capabilities/v2/response_cache.go)

### Summary
The gateway's HTTP action response cache (`responseCache`) keys cached entries by a hash of `(method, URL, headers, body, workflowOwner)` only, as documented in `response_cache.go` and confirmed by `TestRequestHash`, which explicitly asserts that different `CacheSettings` (and different `WorkflowID`) produce the *same* hash. `MaxResponseBytes` — the per-request bound that is supposed to cap how much of the response the requester is willing to receive/pay for processing — is not part of the cache key at all, and is not checked when a cache hit occurs. `MaxResponseBytes` only gets enforced in `network/httpclient.go`'s `Send()` via `maxReadBytes()`/`http.MaxBytesReader`, which is bypassed entirely on a cache hit in `response_cache.go`'s `Fetch()`. [1](#0-0) [2](#0-1) [3](#0-2) 

### Finding Description
This is the same root-cause pattern as the reported DODO issue: a caller supplies a bound/limit parameter meant to control what they will actually receive (`collateralAmount` in the report vs. `MaxResponseBytes` here), but the code path that actually delivers the result to the caller uses a different, unrelated value instead of enforcing the caller's own bound.

In `makeOutgoingRequest` (`http_handler.go`), when `req.CacheSettings.MaxAgeMs > 0`, the handler calls `h.responseCache.Fetch(httpCtx, req, callback, req.CacheSettings.Store)`. `Fetch()` computes `cacheKey := req.Hash()` and returns the previously cached `gateway.OutboundHTTPResponse.Body` directly on a hit, with no re-validation against the *current* request's `MaxResponseBytes`: [4](#0-3) [5](#0-4) 

Since the cache key is derived only from `(method, URL, headers, body, workflowOwner)`, two `OutboundHTTPRequest`s that differ only in `MaxResponseBytes` hash identically and share the same cache slot. The first request to populate the cache dictates the actual body size that gets stored (bounded only by *its own* `MaxResponseBytes`, enforced inside `httpclient.Send()`'s `maxReadBytes`); every subsequent request with a smaller `MaxResponseBytes` that hits the cache receives that larger, previously-fetched body verbatim, with its own tighter bound never applied.

### Impact Explanation
`MaxResponseBytes` exists specifically to bound resource consumption/cost for a workflow node processing an outbound HTTP action response (mirrored in `httpclient.go`'s enforcement via `http.MaxBytesReader`). Because the response cache silently ignores this field:
- A workflow (or DON member) that sets a small `MaxResponseBytes` to defend against large/adversarial responses can still receive a much larger body than it explicitly bounded itself to, if a same-owner request for the identical URL/method/headers/body with a larger (or zero/default) `MaxResponseBytes` happened to populate the cache first. This defeats the purpose of the size guard and can push unexpectedly large payloads into downstream node processing.
- This is a quota-bypass class of bug, analogous to the audit report's failure to honor the caller-specified bound (`collateralAmountMax`) — here the bound (`MaxResponseBytes`) is likewise never re-checked against the delivered result on the cache-hit path.

Severity is Medium: it is scoped to same-`workflowOwner` cache collisions (the owner is part of the key), so it is not a cross-tenant confidentiality break, but it is a genuine, reachable bypass of a caller-supplied resource bound in the internet-facing gateway's cache, reachable purely through normal HTTP-action request parameters without any privileged access.

### Likelihood Explanation
Any workflow issuing repeated `OutboundHTTPRequest`s to the same URL/method/headers/body with `CacheSettings.Store=true` and varying `MaxResponseBytes` (e.g., a workflow author intentionally tightening the bound between calls, or two concurrently-scheduled node dispatches with different config), will trigger this cache-key collision. No malicious node or peer behavior is required — it is a straightforward parameter/config combination reachable from ordinary caller-controlled request fields.

### Recommendation
Include `MaxResponseBytes` (and any other field the caller uses to bound the response, e.g. response-size-affecting settings) in `OutboundHTTPRequest.Hash()`'s cache key, or re-validate/truncate the cached response's body length against the current request's `MaxResponseBytes` before returning it from `responseCache.Fetch()`. At minimum, reject or bypass the cache when `MaxResponseBytes` differs from the value that produced the cached entry.

### Proof of Concept
1. Workflow (owner `O`) issues `OutboundHTTPRequest{Method: GET, URL: u, Body: b, Headers: h, WorkflowOwner: O, MaxResponseBytes: 1_000_000, CacheSettings: {Store: true, MaxAgeMs: 600000}}`. The endpoint returns a 900KB body; `httpclient.Send()` allows it through (under the 1MB cap); `responseCache.Set`/`Fetch` caches this 900KB response keyed by `Hash()` (method+URL+headers+body+owner).
2. Shortly after, the same or another node dispatches, on behalf of the same workflow owner `O`, an otherwise-identical `OutboundHTTPRequest` but with `MaxResponseBytes: 1000` (intending to strictly bound the response it is willing to process) and `CacheSettings.MaxAgeMs > 0`.
3. `req.Hash()` is identical to step 1's (since `MaxResponseBytes` is excluded from the hash, confirmed by `TestRequestHash`'s `CacheSettings`/`WorkflowID` hash-invariance assertions showing non-content fields are excluded). `responseCache.Fetch()` returns the cached 900KB body directly, never invoking `callback()`/`httpclient.Send()` where the 1000-byte cap would have been enforced.
4. The requester receives a 900KB payload despite specifying a 1000-byte `MaxResponseBytes` bound, confirming the bound is silently bypassed on the cache-hit path. [2](#0-1) [6](#0-5)

### Citations

**File:** core/services/gateway/handlers/capabilities/v2/response_cache.go (L15-29)
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

type cachedResponse struct {
	response gateway.OutboundHTTPResponse
	storedAt time.Time
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

**File:** core/services/gateway/network/httpclient.go (L490-522)
```go
	n := maxReadBytes(readSize{defaultSize: c.config.MaxResponseBytes, requestSize: req.MaxResponseBytes})
	c.lggr.Debugw("max bytes to read from HTTP response", "bytes", n)

	reader := http.MaxBytesReader(nil, resp.Body, int64(n))
	body, err := io.ReadAll(reader)
	if err != nil {
		c.metrics.recordTotal(ctx, req.Method, resp.StatusCode, false, traceState.connReused.Load(), time.Since(requestStart))
		c.lggr.Errorw("failed to read HTTP response body", "err", err)
		return nil, errors.Join(err, ErrHTTPRead)
	}

	c.metrics.recordTotal(ctx, req.Method, resp.StatusCode, true, traceState.connReused.Load(), time.Since(requestStart))

	headers, multiHeaders := responseHeadersFromNetHeader(resp.Header)
	c.lggr.Debugw("received HTTP response", "statusCode", resp.StatusCode)
	return &HTTPResponse{
		Headers:      headers,
		MultiHeaders: multiHeaders,
		StatusCode:   resp.StatusCode,
		Body:         body,
	}, nil
}

type readSize struct {
	defaultSize uint32
	requestSize uint32
}

func maxReadBytes(sizes readSize) uint32 {
	if sizes.requestSize == 0 {
		return sizes.defaultSize
	}
	return min(sizes.defaultSize, sizes.requestSize)
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
