### Title
Cross-workflow-owner HTTP response cache poisoning/disclosure via unauthenticated `WorkflowOwner` field - ([File: core/services/gateway/handlers/capabilities/v2/response_cache.go])

### Summary
The gateway's HTTP Action response cache partitions cached HTTP responses by a hash that includes `WorkflowOwner`, but that field is taken verbatim from the `OutboundHTTPRequest` JSON payload sent by a workflow DON node — a value the code itself documents as attacker-controlled/untrusted. Any node able to speak the gateway's HTTP-action protocol can therefore forge another tenant's `WorkflowOwner` and either poison that tenant's cache entry with attacker-chosen response content or read back an already-cached response that was produced for a different tenant.

### Finding Description
`responseCache` is described as scoping HTTP action cache entries by "a hash of the request (method, URL, headers, body, workflowOwner)" so that different workflow owners don't share cache entries: [1](#0-0) 

The test suite confirms `WorkflowOwner` (not `WorkflowID`) is the actual isolation key baked into `Hash()`: [2](#0-1) 

However, `WorkflowOwner` arrives inside the `OutboundHTTPRequest` that is unmarshalled directly from the node's message with no verification against the node's authenticated identity: [3](#0-2) 

The code explicitly acknowledges this trust gap when handling the same struct for mTLS purposes: "all fields set on the request come from untrusted nodes": [4](#0-3) 

`makeOutgoingRequest` then uses this untrusted `req` (including its `WorkflowOwner`) directly as the cache key for both read (`Fetch`) and write (`Set`): [5](#0-4) 

`Fetch`/`Set` perform no additional check that the caller is actually authorized for the `WorkflowOwner` embedded in the request; they just hash it and read/write the shared map: [6](#0-5) 

Because node→gateway authentication only establishes which DON member sent the message (`nodeAddr`), not which workflow owner the payload legitimately belongs to, any compromised or malicious workflow node in the DON can set an arbitrary `WorkflowOwner` value in its own `OutboundHTTPRequest` and thereby:
1. **Poison** the cache entry for a victim owner's request (same method/URL/headers/body) with attacker-controlled response content, which will later be served to the victim's real workflow when it makes the same call with `CacheSettings.MaxAgeMs>0`.
2. **Read** a response that was cached for a victim owner's earlier request, disclosing whatever data (potentially containing secrets/tokens/PII returned by the external endpoint) was stored under that owner's key.

This mirrors the Indodax root cause referenced in the report: a system trusted an unverified "identity"/routing field embedded in an operation to make security-relevant decisions ("withdrawals that looked legitimate"), rather than deriving that identity from an authenticated source.

### Impact Explanation
A single malicious or compromised workflow-DON node can compromise the confidentiality and integrity of HTTP Action results belonging to a different workflow owner sharing the same gateway/DON. This can lead to:
- Disclosure of another tenant's cached HTTP response bodies/headers (potential secret leakage).
- Injection of attacker-controlled data into another tenant's workflow execution via a poisoned cache entry, which can corrupt downstream on-chain/off-chain decisions made by that workflow (e.g., forged price/oracle-style HTTP data), a cross-user response confusion with real business impact.

### Likelihood Explanation
Exploitation requires only the ability to act as (or compromise) one workflow-DON node capable of issuing `HTTPAction`/`OutboundHTTPRequest` messages through the gateway — no gateway-admin or cross-DON privilege is needed, and the vulnerable field (`WorkflowOwner`) is plain, attacker-supplied JSON. The main constraint is guessing/matching the exact `method+URL+headers+body` combination the victim will request, which is feasible for common/well-known integrations (e.g., predictable public APIs) reused across workflows.

### Recommendation
Do not derive cache-partition identity (`WorkflowOwner`) from client-supplied request fields. Instead:
- Bind the cache key to the authenticated node/owner context established at the connection or job-run level (the same trusted identity used for rate limiting and org resolution), not to a field copied out of the JSON payload.
- If per-owner cache scoping must come from workflow metadata, cross-check the claimed `WorkflowOwner` against the workflow registry/metadata already synced from onchain state (as is done elsewhere, e.g., `WorkflowMetadataHandler`) before using it as a cache key.
- Alternatively, scope the cache per authenticated `nodeAddr`/DON membership rather than a self-reported owner string, or require signed/attested workflow metadata binding request to owner.

### Proof of Concept
1. Malicious/compromised workflow node `M`, member of the same DON as victim node/workflow `V`, learns (or guesses) that `V`'s workflow periodically issues `OutboundHTTPRequest{Method: "GET", URL: "https://api.example.com/price", ...}` with `CacheSettings.Store=true, MaxAgeMs>0`.
2. `M` sends its own `HTTPAction` response message to the gateway with the same `Method`/`URL`/`Headers`/`Body`, but sets `WorkflowOwner = "<victim-owner-address>"` and lets the fetch return (or forges) a malicious body.
3. Gateway's `makeOutgoingRequest` computes `req.Hash()` (which folds in the forged `WorkflowOwner`) and, per `Set`/`Fetch` logic in `response_cache.go`, stores this response under the victim's cache key.
4. When `V`'s legitimate workflow subsequently issues the same request within the TTL, `Fetch` returns the poisoned/forged entry instead of hitting the real external endpoint — `V`'s workflow now consumes attacker-controlled data.
5. Symmetrically, `M` can set `WorkflowOwner = "<victim-owner-address>"` on a request matching one `V` already made, causing `Fetch` to return `V`'s previously cached (potentially sensitive) response body to `M`.

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

**File:** core/services/gateway/handlers/capabilities/v2/http_handler.go (L326-330)
```go

	// We don't have access to the org here, so this will fall back to the environment default (=false).
	// That's appropriate because all fields set on the request come from untrusted nodes.
	// The capability separately applies an org-specific check.

```

**File:** core/services/gateway/handlers/capabilities/v2/http_handler.go (L404-421)
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
