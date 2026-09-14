### Title
Outbound HTTP response cache key omits mTLS client-certificate identity, allowing cross-request/cross-workflow reuse of authenticated responses - ([File: core/services/gateway/handlers/capabilities/v2/response_cache.go])

### Summary
The `BondNFT.claim()` bug is a class of "state/accumulator scoped incorrectly, so a later reader gets data computed under a different context than its own." The closest reachable analog in this codebase is the HTTP-action `responseCache` used by the gateway's internet-facing capability handler: its cache key is derived only from `(method, URL, headers, body, workflowOwner)` and does **not** include the request's mTLS client-certificate (`Mtls`) material, even though mTLS is the mechanism used to authenticate the outbound call to the external endpoint.

### Finding Description
`gatewayHandler.makeOutgoingRequest` reads a workflow node's `OutboundHTTPRequest` and, when `CacheSettings.MaxAgeMs > 0`, serves/loads results through `responseCache.Fetch`, keyed by `req.Hash()`: [1](#0-0) 

`responseCache` documents itself as keyed "by a hash of the request (method, URL, headers, body, workflowOwner)": [2](#0-1) 

Tests confirm the hash explicitly excludes `WorkflowID` while including `WorkflowOwner`: [3](#0-2) [4](#0-3) 

Critically, the hash inputs (method/URL/headers/body/workflowOwner) do not include the `Mtls` field, yet `Mtls` is what actually authenticates/authorizes the outbound call to the external endpoint — a separate, throwaway HTTP client is instantiated per request specifically "to ensure that we don't accidentally leak auth'd connections to other users": [5](#0-4) 

However, that per-request client isolation only protects the *live* HTTP round trip. It does not protect the **cached result** of that round trip: `Fetch` stores/returns the raw `OutboundHTTPResponse` keyed without any binding to the credential that produced it: [6](#0-5) 

So the "no auth'd connection leaks between users" invariant asserted in comments and tests only holds for the direct connection, but is silently broken by the cache layer, similar to how `BondNFT.claim()`'s missing per-epoch update silently broke the accounting invariant relied on elsewhere in the same contract.

### Impact Explanation
An unprivileged workflow node request that shares the same `(method, URL, headers, body, workflowOwner)` tuple as a prior mTLS-authenticated request — but supplies no `Mtls` credential, or a different/invalid one — can receive the cached response that was originally fetched using another request's valid mTLS client certificate, as long as `CacheSettings.MaxAgeMs > 0` on the second request. This is a cross-user (cross-workflow, same-owner) response confusion: data intended to be gated behind a specific client certificate is served to a caller that never authenticated. Depending on what the external endpoint returns for an mTLS-authenticated call (e.g., account-specific data), this can leak sensitive response content to a request that did not present valid credentials.

### Likelihood Explanation
Reachable directly from an unprivileged workflow node via `HandleNodeMessage` → `makeOutgoingRequest`, with attacker control over `Method`, `URL`, `Headers`/`MultiHeaders`, `Body`, and `CacheSettings` fields of `OutboundHTTPRequest`; only `WorkflowOwner` must match a prior cached entry (same-tenant, different workflow), and the collision is deterministic (a hash match, not a race). The `Set`/`Fetch` mechanics themselves are already exercised by the existing test suite (`TestMakeOutgoingRequestCachingBehavior`, `TestFetch`), confirming the cache is populated and returned purely based on the documented hash inputs, i.e. this is a design gap rather than a rare timing bug.

### Recommendation
Include a strong, collision-resistant representation of the request's authentication context (e.g., a hash of the mTLS certificate/key pair, or a flag distinguishing "no-mTLS" from "mTLS with cert X") as part of the `responseCache` key/`Hash()` computation, so that cached responses obtained under one credential can never be served to a request presenting a different (or absent) credential. Alternatively, disable response caching entirely for `OutboundHTTPRequest`s that set `Mtls`.

### Proof of Concept
1. Workflow node sends `OutboundHTTPRequest{Method, URL, Headers, Body, WorkflowOwner: "owner-1", Mtls: certA, CacheSettings:{Store:true, MaxAgeMs: 600000}}`. The gateway authenticates with `certA`, gets an authenticated response, and `responseCache.Set`/`Fetch` stores it keyed by `Hash()` (no `Mtls` component).
2. A second `OutboundHTTPRequest` with the same `Method/URL/Headers/Body/WorkflowOwner` but `Mtls: nil` (or a different/invalid cert) and `CacheSettings:{MaxAgeMs: 600000}` is sent (e.g., from a different workflow under the same owner, or a compromised/misconfigured node).
3. `responseCache.Fetch` computes the identical `cacheKey` (since `Mtls` isn't hashed) and returns the cached, `certA`-authenticated response without ever invoking `handler.send()`/the mTLS client factory — bypassing authentication entirely as demonstrated by the existing cache-hit test pattern: [7](#0-6)

### Citations

**File:** core/services/gateway/handlers/capabilities/v2/http_handler.go (L298-325)
```go
func (h *gatewayHandler) send(ctx context.Context, httpReq network.HTTPRequest, req gateway_common.OutboundHTTPRequest) (*network.HTTPResponse, error) {
	if req.Mtls == nil {
		return h.httpClient.Send(ctx, httpReq)
	}

	if h.httpClientFactory == nil {
		return nil, errors.New("nil http client factory, cannot make mtls request")
	}

	// Instantiate a throwaway HTTP client with the provided Mtls client certificate provided.
	// We do this to ensure that we don't accidentally leak auth'd connections to other users.
	// Note: this isn't a DOS vector because
	// a) we have a global rate limit above which limits abuse
	// b) we apply rate limits limiting the ability of sending nodes to spam requests
	// c) we apply per-owner rate limits in the action capability in the
	// workflow node limiting the ability of users to abuse this flow by spamming Mtls requests.
	// The client enforces the mtls concurrency limit internally (on the request's
	// capped-timeout context) before delegating to the underlying transport.
	client, err := h.httpClientFactory(network.HTTPClientConfig{
		Mtls: &gateway_common.MtlsAuth{
			PrivateKey:  req.Mtls.PrivateKey,
			Certificate: req.Mtls.Certificate,
		},
		ConcurrencyLimiter: h.mtlsConcurrencyLimiter,
	})
	if err != nil {
		return nil, fmt.Errorf("failed to instantiate http client for mtls request: %w", err)
	}
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

**File:** core/services/gateway/handlers/capabilities/v2/response_cache_test.go (L151-161)
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
```

**File:** core/services/gateway/handlers/capabilities/v2/response_cache_test.go (L230-250)
```go
	t.Run("returns cached response when cache hit", func(t *testing.T) {
		req := createTestRequest("GET", "https://example.com/hit")
		cachedResp := createTestResponse(200, "cached data")

		// Pre-populate cache
		cache.cache[req.Hash()] = &cachedResponse{
			response: cachedResp,
			storedAt: time.Now(),
		}

		var fetchCalled bool
		fetchFn := func() gateway_common.OutboundHTTPResponse {
			fetchCalled = true
			return createTestResponse(200, "should not be called")
		}

		result := cache.Fetch(t.Context(), req, fetchFn, true)

		require.False(t, fetchCalled, "fetchFn should not be called on cache hit")
		require.Equal(t, cachedResp, result)
	})
```
