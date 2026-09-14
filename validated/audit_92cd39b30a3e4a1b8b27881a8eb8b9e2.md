### Title
Response cache in Gateway HTTP capability handler ignores mTLS client identity, enabling cross-credential response disclosure - (File: core/services/gateway/handlers/capabilities/v2/response_cache.go)

### Summary
The Spring advisory concerns a static resource cache that fails to bind cached content to the correct request/authorization context, causing one caller's response to be served to another. The analogous defect in this repo is the `responseCache` used by the Gateway `gatewayHandler` for outbound HTTP action requests: cache entries are keyed only by `OutboundHTTPRequest.Hash()`, and that hash explicitly ignores the mTLS client-certificate material (`OutboundHTTPRequest.Mtls`) used to authenticate the outbound request to the external endpoint.

### Finding Description
`gatewayHandler.makeOutgoingRequest` reads cache settings from the untrusted, node-supplied `OutboundHTTPRequest` and either serves a cached response or issues a fresh request through `responseCache.Fetch`/`Set`, keyed by `req.Hash()`: [1](#0-0) 

The cache itself stores/retrieves purely by that hash: [2](#0-1) [3](#0-2) 

Tests confirm what fields participate in `Hash()`: it varies with `WorkflowOwner` but is documented/verified as **not** varying with `WorkflowID`, and does not vary with `CacheSettings`: [4](#0-3) [5](#0-4) 

Critically, `OutboundHTTPRequest` also carries an optional `Mtls` credential (`PrivateKey`/`Certificate`) that determines *which client identity* is presented to the external endpoint: [6](#0-5) 

The `send` function explicitly documents that a fresh, throwaway HTTP client is instantiated per-mTLS-request specifically "to ensure that we don't accidentally leak auth'd connections to other users," and the network layer disables keep-alives for the same reason: [7](#0-6) [8](#0-7) 

However, this defense-in-depth is bypassed by `responseCache`: the response fetched using one workflow node's mTLS certificate is cached under a key derived only from method/URL/headers/body/WorkflowOwner — **not** the mTLS certificate/key used to obtain it. A second request with the same method/URL/headers/body/owner but a *different* (or no) mTLS certificate will be served the cached response without ever presenting its own credentials to the external endpoint, because `Fetch`/`isExpiredOrNotCached` never inspect `req.Mtls` when computing or checking the cache key.

### Impact Explanation
Any content that the external endpoint returns based on the client-certificate identity used for mTLS authentication (e.g., an mTLS-gated API that returns account-specific or credential-scoped data) can be disclosed to a second, differently-authenticated (or unauthenticated) requester, as long as the two requests are cacheable (2xx/4xx) and share the same method/URL/headers/body/WorkflowOwner within the TTL window. This directly matches the CWE-524 "information disclosure via cache" bug class from the advisory: cached content that should be scoped to a specific authentication/authorization context is instead served across contexts. The engineering comment in `send()` shows the developers were aware that connection/credential leakage across users was a risk they mitigated at the transport layer — but that mitigation is undermined by the response cache sitting above it.

### Likelihood Explanation
Exploitation requires: (1) response caching enabled (`CacheSettings.Store=true`/`MaxAgeMs>0`, both attacker-controlled fields on the untrusted `OutboundHTTPRequest`), (2) two requests from the same workflow owner (who may run multiple workflows, some legitimately using different mTLS identities per workflow) with identical method/URL/headers/body, and (3) the target external endpoint returning identity-dependent content for a cacheable status code. Since `CacheSettings` and `Mtls` are both attacker/node-controlled and the hash function is shared code (not something this repo defines but consumes from `chainlink-common`), the gateway operator has no server-side knob to prevent this. Likelihood is moderate — it depends on a specific but plausible usage pattern (same owner using different per-workflow mTLS certificates against the same URL).

### Recommendation
Include a canonical representation of `req.Mtls` (e.g., a hash of certificate+key, or at minimum a flag distinguishing "no mTLS" vs a specific credential fingerprint) in the cache key so responses obtained under different client-authentication contexts are never conflated. Alternatively, disable response caching entirely whenever `req.Mtls != nil`, consistent with the existing "no auth'd connection leaking across users" design intent already present in `send()`.

### Proof of Concept
1. Workflow owner `O` deploys Workflow A, which issues an `OutboundHTTPRequest{Method:"GET", URL:"https://gated.example.com/data", Mtls: certA, CacheSettings:{Store:true, MaxAgeMs:600000}}`. The gateway calls `send`, which authenticates with `certA`, receives a 200 response containing account-A-specific data, and `responseCache.Set` stores it keyed by `Hash()` (owner `O`, method, URL, headers, body — `Mtls` excluded).
2. Workflow owner `O` deploys Workflow B (different workflow, different/no mTLS cert `certB`), issuing the identical `OutboundHTTPRequest{Method:"GET", URL:"https://gated.example.com/data", Mtls: certB or nil, CacheSettings:{MaxAgeMs:600000}}`.
3. Because `Hash()` is identical (same owner, method, URL, headers, body — `Mtls` not included), `responseCache.Fetch` returns the cached response obtained under `certA`'s identity without ever calling `send`/presenting `certB`'s credentials, confirmed by the caching flow in `makeOutgoingRequest`: [1](#0-0)  and the cache lookup logic in `response_cache.go`: [9](#0-8) .

### Citations

**File:** core/services/gateway/handlers/capabilities/v2/http_handler.go (L298-338)
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

	// We don't have access to the org here, so this will fall back to the environment default (=false).
	// That's appropriate because all fields set on the request come from untrusted nodes.
	// The capability separately applies an org-specific check.

	// Note: we intentionally consume the rate-limit after instantiating the client so that a malicious user
	// can't send requests with invalid mtls credentials and thus cheaply consume global tokens.
	if !h.mtlsRequestRateLimiter.Allow(ctx) {
		return nil, fmt.Errorf("global mtls request rate limit exceeded: %w", network.ErrBlockedRequest)
	}

	return client.Send(ctx, httpReq)
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

**File:** core/services/gateway/network/httpclient.go (L296-312)
```go
	if config.Mtls != nil {
		// Defence-in-depth protection against accidental reuse
		// of the HTTP client leading to auth'd connections leaking across
		// users.
		defaultTransport.DisableKeepAlives = true
		defaultTransport.TLSHandshakeTimeout = 10 * time.Second

		cert, err := tls.X509KeyPair(config.Mtls.Certificate, config.Mtls.PrivateKey)
		if err != nil {
			return nil, fmt.Errorf("failed to parse MtlsAuth into KeyPair: %w", err)
		}

		defaultTransport.TLSClientConfig = &tls.Config{
			Certificates: []tls.Certificate{cert},
			MinVersion:   tls.VersionTLS12,
		}
		safeConfigBuilder.SetTransport(defaultTransport)
```
