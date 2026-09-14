## Finding: Unbounded HTTP Action response cache growth in the CRE gateway (memory-exhaustion DoS analog)

### Title
Unbounded Growth of Gateway HTTP-Action Response Cache Enables Memory-Exhaustion DoS - (File: core/services/gateway/handlers/capabilities/v2/response_cache.go)

### Summary
The CVE-2025-32424 report describes a resource-exhaustion bug in AutoGPT where a workflow block (`ScreenshotWebPageBlock`) writes attacker-controlled data to disk with no size cap, and a looping construct (`StepThroughItemsBlock`) has no bound on iteration count, letting an unprivileged workflow author exhaust disk space. The Chainlink CRE gateway's HTTP Handlers V2 component contains an analogous unbounded-resource pattern: the `responseCache` that backs outbound HTTP Action caching has no maximum entry count or size cap, only a time-based (TTL) cleanup that runs periodically. An unprivileged workflow (driven by capability/DON nodes acting on workflow-author-controlled inputs) can generate an unbounded number of distinct, cacheable HTTP Action responses that accumulate in gateway memory until the next cleanup cycle.

### Finding Description
`http_handler.go`'s `makeOutgoingRequest` stores every cacheable outbound HTTP response keyed by a hash of the request (method, URL, headers, body, workflow owner) whenever `CacheSettings.Store` is true: [1](#0-0) 

The underlying `responseCache` implementation stores entries in a plain map with no maximum size, no LRU eviction, and no memory budget — the only reclamation mechanism is `DeleteExpired`, invoked on a periodic timer (`CleanUpPeriodMs`, default 10 minutes): [2](#0-1) [3](#0-2) 

This is in clear contrast with the other cache implementation in the same codebase, `RequestCache`, which explicitly enforces a `maxCacheSize` and rejects new entries once the bound is reached: [4](#0-3) [5](#0-4) 

The `responseCache` has no equivalent guard. Cache keys are derived from the full request (`req.Hash()`), which a workflow author fully controls (URL query strings, headers, body). Since node message rate is only throttled per-request-rate (not per unique-cache-key or aggregate cache size), a workflow can drive its DON nodes to issue a high volume of distinct, `Store: true`-tagged, cacheable (2xx/4xx) HTTP Action requests. Each unique request creates a new, retained cache entry (up to `MaxResponseBytes`, default 50MB per gateway config) that persists in gateway process memory for up to the TTL/cleanup interval, regardless of rate limiting on request throughput: [6](#0-5) 

Default gateway rate limits (e.g. `globalRPS = 500`, `MaxResponseBytes = 50000000`) permit substantial sustained request volume, and none of this is checked against total cache footprint, only against the number of requests per second: [7](#0-6) 

### Impact Explanation
An unprivileged workflow author (a party with only the ability to register/execute a workflow, not an operator of gateway infrastructure) can cause the gateway process to accumulate an unbounded amount of cached HTTP response data in memory. Because the cache has no eviction-by-size policy and cleanup is purely time-based, sustained triggering of unique, cacheable outbound HTTP Action requests can grow memory usage without bound between cleanup cycles, eventually exhausting available memory and crashing or degrading the gateway process — a denial-of-service affecting all DONs and workflows served by that gateway instance, not just the attacker's own workflow. This matches the "internet-facing gateway ... caches" unprivileged-actor analog class.

### Likelihood Explanation
The workflow author only needs to register a workflow that issues HTTP Action capability calls with `CacheSettings.Store = true` and varying request parameters (e.g., varying query strings or headers) to generate distinct cache keys. This requires no special privilege beyond normal workflow authoring/execution rights, and the existing rate limiters bound request throughput, not aggregate cache memory, so the attack is straightforward to sustain over the TTL window (default 10 minutes) before any cleanup occurs.

### Recommendation
Add a maximum entry count and/or maximum aggregate byte-size bound to `responseCache` (mirroring the `maxCacheSize` pattern already used in `common.RequestCache`), evicting oldest/LRU entries when the bound is exceeded, in addition to the existing TTL-based cleanup in `response_cache.go`.

### Proof of Concept
1. Author a workflow whose HTTP Action requests set `CacheSettings.Store = true` and vary the URL/query string (or headers/body) on each invocation, targeting an endpoint that returns 2xx/4xx.
2. Trigger the workflow repeatedly (within normal per-node/global rate limits) so that many distinct outbound requests flow through `gatewayHandler.makeOutgoingRequest` → `responseCache.Set`/`Fetch`.
3. Because each unique request hash creates a new cache entry with no size/count cap, and cleanup only runs every `CleanUpPeriodMs` (default 600000ms), the `responseCache.cache` map grows continuously, consuming gateway process memory proportional to `unique_requests_per_ttl_window × response_size (up to MaxResponseBytes)`.

### Citations

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

**File:** core/services/gateway/handlers/common/requestcache.go (L27-32)
```go
type requestCache[T any] struct {
	cache        map[globalID]*pendingRequest[T]
	maxCacheSize uint32
	timeout      time.Duration
	mu           sync.Mutex
}
```

**File:** core/services/gateway/handlers/common/requestcache_test.go (L125-141)
```go
func TestRequestCache_MaxSize(t *testing.T) {
	t.Parallel()

	cache := common.NewRequestCache[requestState](time.Hour, 2)
	callback := common.NewCallback()
	lggr := logger.Test(t)
	initialState := &requestState{}

	req := &api.Message{Body: api.MessageBody{MessageID: "aa", Sender: "0x1234"}}
	require.NoError(t, cache.NewRequest(lggr, req, callback, initialState))

	req.Body.MessageID = "bb"
	require.NoError(t, cache.NewRequest(lggr, req, callback, initialState))

	req.Body.MessageID = "cc"
	require.Error(t, cache.NewRequest(lggr, req, callback, initialState))
}
```

**File:** deployment/cre/jobs/pkg/gateway_job_test.go (L337-348)
```go
[[gatewayConfig.Services.Handlers]]
Name = 'http-capabilities'
ServiceName = 'workflows'

[gatewayConfig.Services.Handlers.Config]
CleanUpPeriodMs = 600000

[gatewayConfig.Services.Handlers.Config.NodeRateLimiter]
globalBurst = 100
globalRPS = 500
perSenderBurst = 100
perSenderRPS = 100
```
