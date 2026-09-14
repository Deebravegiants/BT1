## Title
Response cache key omits mTLS credentials, allowing cross-trust-boundary response reuse - ([File: core/services/gateway/handlers/capabilities/v2/response_cache.go])

### Summary
The gateway's HTTP Action response cache (`responseCache`) keys cached responses using `gateway_common.OutboundHTTPRequest.Hash()`, which is documented and tested to hash only `method, URL, headers, body, workflowOwner` [1](#0-0) . The mutual-TLS client certificate/key carried on `OutboundHTTPRequest.Mtls` is not part of the cache key, as confirmed by the request-hash test suite which exercises method, URL, CacheSettings, WorkflowID, and WorkflowOwner but never Mtls [2](#0-1) . This mirrors the mod_ssl CVE-2025-23048 pattern: a shared cache keyed on identity-agnostic attributes returns a response fetched under one trust configuration (client certificate) to a different, unauthenticated or differently-authenticated requester that hits the same key.

### Finding Description
`makeOutgoingRequest` reads an `OutboundHTTPRequest` (including its optional `Mtls` field) from a node message and, when `CacheSettings.MaxAgeMs > 0`, calls `h.responseCache.Fetch(httpCtx, req, callback, req.CacheSettings.Store)` [3](#0-2) . `Fetch`/`Set`/`isExpiredOrNotCached` all key exclusively off `req.Hash()` [4](#0-3) .

`gatewayHandler.send` explicitly builds a fresh, throwaway mTLS-configured HTTP client per request specifically "to ensure that we don't accidentally leak auth'd connections to other users" [5](#0-4) , and the underlying `network.NewHTTPClient` disables keep-alives as defense-in-depth against connection reuse across users [6](#0-5) . This is exactly the class of protection the mod_ssl advisory shows is necessary — resumable/reusable state (there: TLS session; here: cached HTTP response) must be scoped to the trust boundary that produced it (there: per-vhost client CA config; here: per-mTLS-identity).

However, that connection-level isolation is undermined at the response-cache layer: two `OutboundHTTPRequest`s with identical method/URL/headers/body/workflowOwner but *different* `Mtls` certificates (or one with `Mtls` set and one without) hash identically and therefore collide in the cache. A response that was only obtainable because a caller presented a specific client certificate can be served, via cache hit, to a subsequent caller that presents no certificate or a different (unauthorized) certificate.

### Impact Explanation
Where an outbound HTTP action targets an endpoint gated by mutual TLS (client-certificate-based access control), the gateway's own cache — not the origin server — becomes the enforcement point once a response is stored. Because the cache key ignores `Mtls`, a workflow (or node acting on behalf of a workflow with the same `WorkflowOwner`) that lacks the correct client certificate can retrieve a cached response that was only returned by the origin server because a different, properly-authenticated caller presented valid mTLS credentials. This is a direct access-control bypass / cross-caller response confusion, analogous to the vhost/session-resumption bypass in the reference CVE, and can leak data intended to be restricted to holders of a specific client certificate.

### Likelihood Explanation
The path is reachable from any workflow node message handled by `HandleNodeMessage` → `makeOutgoingRequest`, gated only by the existing node/global rate limiters (not by trust separation) [7](#0-6) . Any two requests sharing method/URL/headers/body/workflowOwner and non-zero `CacheSettings.MaxAgeMs`/`Store` will collide regardless of `Mtls`, so triggering the collision requires no special privilege — just knowledge of the target URL/method/body pattern used by a higher-trust mTLS-gated action under the same workflow owner.

### Recommendation
Include a value derived from `Mtls` (e.g., a hash of the certificate/key, or simply whether `Mtls != nil`) in `OutboundHTTPRequest.Hash()` so cache entries are scoped per credential/trust context, mirroring the “Workflow Isolation” design intent already documented for `WorkflowID`/`WorkflowOwner` scoping [8](#0-7) . At minimum, disable caching (`Store`) entirely for requests where `Mtls != nil`.

### Proof of Concept
1. Workflow owner `O` submits HTTP action A: `GET https://private.example.com/data`, `Mtls` = cert `C1` (authorized), `CacheSettings.Store=true`, `MaxAgeMs=600000`. Gateway fetches via `h.send` using a throwaway mTLS client with `C1` and caches the 200 response under `req.Hash()` (which does not include `C1`) [9](#0-8) .
2. Workflow owner `O` (same `WorkflowOwner`) submits HTTP action B with identical method/URL/headers/body but `Mtls=nil` (or a different, unauthorized cert), `MaxAgeMs>0`.
3. `responseCache.Fetch` computes the same `cacheKey` for B as for A (since Mtls is excluded from `Hash()`) and returns A's cached, mTLS-authenticated response to B without ever contacting the origin server or presenting valid credentials [10](#0-9) .

### Citations

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

**File:** core/services/gateway/handlers/capabilities/v2/response_cache.go (L46-120)
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

// Fetch fetches a response from the cache if it exists and
// the age of cached response is less than the max age of the request.
// If the cached response is expired or not cached, it fetches a new response from the fetchFn
// and caches the response if it is cacheable and storeOnFetch is true.
//
// The mutex is only held during cache map access (microseconds), not during fetchFn execution.
// Singleflight deduplicates concurrent requests to the same cache key so only one fetchFn
// runs per key, while requests to different keys execute in parallel.
// Cache read and write happen inside the singleflight callback to ensure the key remains
// in-flight until the result is stored, preventing duplicate fetches.
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

**File:** core/services/gateway/handlers/capabilities/v2/response_cache_test.go (L94-176)
```go
func TestRequestHash(t *testing.T) {
	req := createTestRequest("GET", "https://example.com")

	t.Run("generates consistent hash", func(t *testing.T) {
		hash1 := req.Hash()
		hash2 := req.Hash()
		require.Equal(t, hash1, hash2)
	})

	t.Run("different requests generate different hashes", func(t *testing.T) {
		req1 := createTestRequest("GET", "https://example.com/path1")
		req2 := createTestRequest("GET", "https://example.com/path2")

		hash1 := req1.Hash()
		hash2 := req2.Hash()
		require.NotEqual(t, hash1, hash2)
	})

	t.Run("same request with different method generates different hash", func(t *testing.T) {
		req1 := createTestRequest("GET", "https://example.com")
		req2 := createTestRequest("POST", "https://example.com")

		hash1 := req1.Hash()
		hash2 := req2.Hash()
		require.NotEqual(t, hash1, hash2)
	})

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

**File:** core/services/gateway/handlers/capabilities/v2/http_handler.go (L239-296)
```go
func (h *gatewayHandler) HandleNodeMessage(ctx context.Context, resp *jsonrpc.Response[json.RawMessage], nodeAddr string) error {
	if resp.ID == "" {
		return fmt.Errorf("received response with empty request ID from node %s", nodeAddr)
	}
	h.lggr.Debugw("handling incoming node message", "requestID", resp.ID, "nodeAddr", nodeAddr)
	nodeRateLimiter, ok := h.perNodeRateLimiters[nodeAddr]
	if !ok {
		return fmt.Errorf("received message from unexpected node %s", nodeAddr)
	}
	if !nodeRateLimiter.Allow(ctx) {
		h.metrics.IncrementCapabilityNodeThrottled(ctx, nodeAddr, h.lggr)
		return fmt.Errorf("rate limit exceeded for node %s", nodeAddr)
	}
	if !h.globalNodeRateLimiter.Allow(ctx) {
		h.metrics.IncrementGlobalThrottled(ctx, h.lggr)
		return errors.New("global rate limit exceeded")
	}
	// Node messages follow the format "<methodName>/<workflowID>/<uuid>" or
	// "<methodName>/<workflowID>/<workflowExecutionID>/<uuid>". Messages are routed
	// based on the method in the ID.
	// Any messages without "/" is assumed to be a trigger response to a prior user request.
	if strings.Contains(resp.ID, "/") {
		if resp.Result == nil {
			h.lggr.Errorw("received response with empty result from node", "nodeAddr", nodeAddr, "error", resp.Error)
			return fmt.Errorf("received response with empty result from node %s", nodeAddr)
		}
		parts := strings.Split(resp.ID, "/")
		methodName := parts[0]
		switch methodName {
		case gateway_common.MethodHTTPAction:
			start := time.Now()
			h.metrics.IncrementActionRequestCount(ctx, nodeAddr, h.lggr)
			err := h.makeOutgoingRequest(ctx, resp, nodeAddr)
			if err != nil {
				h.metrics.IncrementActionRequestFailures(ctx, nodeAddr, h.lggr)
			}
			h.metrics.RecordActionRequestLatency(ctx, time.Since(start).Milliseconds(), h.lggr)
			return err
		case gateway_common.MethodPushWorkflowMetadata:
			h.metrics.IncrementMetadataRequestCount(ctx, nodeAddr, gateway_common.MethodPushWorkflowMetadata, h.lggr)
			err := h.metadataHandler.OnMetadataPush(ctx, resp, nodeAddr)
			if err != nil {
				h.metrics.IncrementMetadataProcessingFailures(ctx, nodeAddr, gateway_common.MethodPushWorkflowMetadata, h.lggr)
			}
			return err
		case gateway_common.MethodPullWorkflowMetadata:
			h.metrics.IncrementMetadataRequestCount(ctx, nodeAddr, gateway_common.MethodPullWorkflowMetadata, h.lggr)
			err := h.metadataHandler.OnMetadataPullResponse(ctx, resp, nodeAddr)
			if err != nil {
				h.metrics.IncrementMetadataProcessingFailures(ctx, nodeAddr, gateway_common.MethodPullWorkflowMetadata, h.lggr)
			}
			return err
		default:
			return fmt.Errorf("unsupported method %s in node message ID %s", methodName, resp.ID)
		}
	}
	return h.triggerHandler.HandleNodeTriggerResponse(ctx, resp, nodeAddr)
}
```

**File:** core/services/gateway/handlers/capabilities/v2/http_handler.go (L298-337)
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
