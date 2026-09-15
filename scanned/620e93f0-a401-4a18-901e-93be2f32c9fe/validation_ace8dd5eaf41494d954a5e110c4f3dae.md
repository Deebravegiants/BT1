### Title
Unbounded HTTP action response cache growth in gateway v2 enables node-triggered memory-exhaustion DoS - (File: core/services/gateway/handlers/capabilities/v2/response_cache.go)

### Summary
The Consul CVE-2020-13250 analog is a caching feature (HTTP API/DNS cache) that could be abused to exhaust resources and cause denial of service. The Chainlink Gateway's HTTP Handlers V2 implements an analogous response cache (`responseCache`) for outbound HTTP action requests that has no bound on the number of distinct cache entries it will hold, relying solely on time-based expiry.

### Finding Description
`responseCache` stores every cacheable outbound HTTP response in an in-memory map keyed by `req.Hash()`, gated only by `CacheSettings.Store` and TTL expiry — there is no maximum entry count or per-workflow-owner quota: [1](#0-0) 

`Set`/`Fetch` insert new entries any time the response is a 2xx/4xx and the entry is stale, with cleanup happening only periodically via `DeleteExpired` (bounded by `CleanUpPeriodMs`/TTL), not by cache size: [2](#0-1) 

The cache key is a hash of method, URL, headers, body, and workflow owner (confirmed by the accompanying test which shows `WorkflowID` is deliberately excluded and does not affect the hash, while URL/body/method do vary the hash): [3](#0-2) 

Because a workflow node can freely vary the outbound HTTP request (URL path/query params, body, headers) per HTTP Action call, and each variation produces a distinct cache key with a default TTL of 10 minutes, a single workflow (or several) issuing many distinct outbound requests with `CacheSettings.Store=true` will continuously grow the shared, gateway-wide `cache` map. The default TTL and cleanup interval documented in `ServiceConfig` govern eviction timing only, not map size: [4](#0-3) 

### Impact Explanation
The `responseCache` is shared across all workflows served by a gateway node (only scoped by owner+method+URL+headers+body hash, not per-owner bounded). Sustained high-cardinality outbound HTTP Action traffic from workflows (which are user/owner-submitted and thus a comparatively low-trust, externally-influenced input path into the gateway) can grow the map unbounded until the next `DeleteExpired` cleanup cycle, and if requests are generated faster than the TTL/cleanup can reclaim them, memory usage grows without bound — a denial-of-service condition against the gateway process affecting all workflows/tenants it serves, directly analogous to the Consul HTTP/DNS caching DoS (CVE-2020-13250).

### Likelihood Explanation
Likelihood is moderate: it requires an actor able to submit workflows with HTTP Action capabilities that generate high-cardinality outbound requests (varying URL/body) with `CacheSettings.Store=true`. This does not require any authentication bypass — it uses the intended HTTP Action caching feature as designed, with no compensating size cap identified in the reviewed code (`responseCache`, `ServiceConfig`). Whether operational limits (e.g., global rate limiting per capability node mentioned in the README) sufficiently bound cache growth in practice could not be fully confirmed from the code reviewed, since the rate-limiter implementation itself was not inspected in this pass.

### Recommendation
Add an upper bound on `responseCache` size (e.g., LRU eviction or a configurable `MaxCacheEntries`), and/or enforce per-workflow-owner cache quotas, so that cache growth cannot exceed a fixed memory budget regardless of request cardinality or cleanup cadence.

### Proof of Concept
1. Deploy a workflow with an HTTP Action capability.
2. Repeatedly invoke the action with a unique URL query parameter or body per call and `CacheSettings.Store=true`, `CacheSettings.MaxAgeMs>0` (see `TestMakeOutgoingRequestCachingBehavior`/`TestFetch` for the exact code path exercised: `core/services/gateway/handlers/capabilities/v2/http_handler_test.go:818-860`, `response_cache_test.go:210-287`).
3. Each unique request produces a distinct `req.Hash()` and a new entry in `responseCache.cache`, persisting until TTL expiry/cleanup.
4. Sustained high-rate, high-cardinality calls grow the map faster than `DeleteExpired` can reclaim entries, increasing gateway memory usage without bound.

Note: I could not verify within the available context whether the "Rate Limiting (global, per workflow owner, per capability node)" feature referenced in the README (`core/services/gateway/handlers/capabilities/v2/README.md:22`) provides an effective compensating control against this specific cache-growth vector, since the rate limiter's implementation was not reached in this investigation. If it enforces a strict cap on distinct request cardinality per owner within the TTL window, this could mitigate the impact; otherwise the cache growth remains unbounded as shown above.

### Citations

**File:** core/services/gateway/handlers/capabilities/v2/response_cache.go (L17-38)
```go
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

func newResponseCache(lggr logger.Logger, ttlMs int, metrics *metrics.Metrics) *responseCache {
	return &responseCache{
		cache:   make(map[string]*cachedResponse),
		lggr:    logger.Named(lggr, "ResponseCache"),
		ttl:     time.Duration(ttlMs) * time.Millisecond,
		metrics: metrics,
	}
}
```

**File:** core/services/gateway/handlers/capabilities/v2/response_cache.go (L110-137)
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

func (rc *responseCache) DeleteExpired(ctx context.Context) int {
	rc.cacheMu.Lock()
	defer rc.cacheMu.Unlock()
	now := time.Now()
	var expiredCount int
	for key, cachedResp := range rc.cache {
		if now.After(cachedResp.storedAt.Add(rc.ttl)) {
			delete(rc.cache, key)
			expiredCount++
		}
	}
	rc.lggr.Debugw("Removed expired cached HTTP responses", "count", expiredCount, "remaining", len(rc.cache))
	rc.metrics.IncrementCacheCleanUpCount(ctx, int64(expiredCount), rc.lggr)
	rc.metrics.RecordCacheSize(ctx, int64(len(rc.cache)), rc.lggr)
	return expiredCount
}
```

**File:** core/services/gateway/handlers/capabilities/v2/response_cache_test.go (L94-149)
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
```

**File:** core/services/gateway/handlers/capabilities/v2/http_handler.go (L79-108)
```go
type ServiceConfig struct {
	// MaxTriggerRequestDurationMs is the maximum time allowed for each trigger broadcast request to a workflow node
	MaxTriggerRequestDurationMs int `json:"maxTriggerRequestDurationMs"`

	// NodeSendTimeoutMs bounds each individual send attempt to a single workflow node. It must be smaller
	// than MaxTriggerRequestDurationMs so that one slow/unresponsive node cannot delay sending to the rest
	// of the DON; the send is retried on the next attempt if it times out.
	NodeSendTimeoutMs int `json:"nodeSendTimeoutMs"`

	// RetryConfig defines retry behavior for trigger broadcast requests to workflow nodes
	RetryConfig RetryConfig `json:"retryConfig"`

	// CleanUpPeriodMs is the interval for cleaning up expired HTTP action cache entries, HTTP trigger request callbacks and stale workflow metadata data
	CleanUpPeriodMs int `json:"cleanUpPeriodMs"`

	// MetadataPullIntervalMs is how often to poll workflow nodes for metadata updates
	MetadataPullIntervalMs int `json:"metadataPullIntervalMs"`

	// MetadataAggregationIntervalMs is how often to sync local workflow metadata state with recent metadata updates
	MetadataAggregationIntervalMs int `json:"metadataAggregationIntervalMs"`

	// MetadataPullRequestTimeoutMs is the timeout for metadata pull requests to workflow nodes
	MetadataPullRequestTimeoutMs int `json:"metadataPullRequestTimeoutMs"`

	// OutboundRequestCacheTTLMs is how long to cache outbound HTTP action responses from external endpoints before they expire
	OutboundRequestCacheTTLMs int `json:"outboundRequestCacheTTLMs"`

	// JWTReplayPeriodMs is how long JWT IDs are cached to prevent replay attacks (in milliseconds)
	JWTReplayPeriodMs int `json:"jwtReplayPeriodMs"`
}
```
