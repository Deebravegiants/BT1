### Title
Unbounded outbound-HTTP response cache growth in Gateway HTTP handler enables memory/performance-degradation DoS - (File: core/services/gateway/handlers/capabilities/v2/response_cache.go)

### Summary
CVE-2021-25219 describes a BIND resolver flaw where an internal cache (the "lame cache") had no size bound and could "grow almost infinitely" from ordinary (if malicious) DNS traffic, causing severe performance degradation. The Gateway's `responseCache` used by the HTTP Capability Handler V2 has the same structural weakness: it is a plain `map[string]*cachedResponse` that is only ever pruned by a periodic, time-based `DeleteExpired` sweep, with no cap on the number of distinct entries it may hold between sweeps.

### Finding Description
`responseCache` stores one entry per unique request hash (method, URL, headers, body, workflowOwner): [1](#0-0) 

Entries are inserted on every cacheable outbound HTTP action via `Set`/`Fetch`, with no limit on the total number of keys the map may hold: [2](#0-1) 

The only mechanism that shrinks the map is `DeleteExpired`, which is invoked purely on a fixed timer (`CleanUpPeriodMs`, default 10 minutes) rather than being triggered by size pressure: [3](#0-2) [4](#0-3) 

The handler's rate limiters (`globalNodeRateLimiter`, `perNodeRateLimiters`) bound the *rate* of incoming HTTP action messages but do nothing to bound the *cardinality* of distinct cache keys generated (varying URL, headers, or body per request): [5](#0-4) 

Because every unique `(method, URL, headers, body, workflowOwner)` combination produces a new map entry, a workflow that is authorized to send outbound HTTP actions (the intended DON-facing consumer of this handler) can drive the cache to grow without bound for up to a full `CleanUpPeriodMs` window before any pruning occurs — structurally identical to BIND's lame-cache growth problem: an internal data structure sized only by incoming traffic and reclaimed only on a timer, not on capacity.

### Impact Explanation
Unbounded growth of `responseCache.cache` increases heap usage and lock-hold time under `cacheMu`, degrading Fetch/Set latency for *all* workflows sharing this Gateway instance — a resource-exhaustion/availability issue matching the CVE's own CVSS vector (`C:N/I:N/A:L`). It does not disclose secrets or allow privilege escalation; it is purely an availability/performance-degradation analog.

### Likelihood Explanation
Reaching this path requires only the ability to trigger outbound HTTP action requests through the existing HTTP handler v2 pipeline (an authorized DON/workflow flow, not raw unauthenticated internet traffic), and is throttled in *rate* but not in *key diversity* by the existing per-node/global rate limiters. Sustained diversity of request parameters (varying URL/headers/body) within allowed rate limits is sufficient to grow the map significantly within a single cleanup interval, making this a moderate-likelihood, low-effort resource-exhaustion vector rather than a one-shot exploit.

### Recommendation
Bound `responseCache` by a maximum entry count (e.g., LRU eviction or a hard cap with rejection/oldest-eviction on insert) in addition to the existing TTL-based `DeleteExpired` sweep, so that cache size cannot grow unbounded between cleanup cycles regardless of the diversity of incoming outbound HTTP requests.

### Proof of Concept
1. As an authorized workflow node, issue outbound HTTP action requests (`gateway_common.OutboundHTTPRequest`) with `CacheSettings.Store = true` and a unique combination of `URL`/headers/body on each call, staying within the per-node and global rate limits.
2. Each unique request produces a new `req.Hash()` key stored via `Set`/`Fetch` in `responseCache.cache` (`response_cache.go:83-120`).
3. Repeat for the duration of `CleanUpPeriodMs` (default 10 minutes); the map grows by one entry per unique request with no upper bound check.
4. Observe increased memory usage and `cacheMu`-guarded operation latency on the shared Gateway instance until the next `DeleteExpired` tick, degrading service for other workflows sharing the same Gateway handler.

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

**File:** core/services/gateway/handlers/capabilities/v2/response_cache.go (L83-120)
```go
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

**File:** core/services/gateway/handlers/capabilities/v2/response_cache.go (L122-137)
```go
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

**File:** core/services/gateway/handlers/capabilities/v2/http_handler.go (L29-43)
```go
const (
	handlerName                          = "HTTPCapabilityHandler"
	defaultCleanUpPeriodMs               = 1000 * 60 * 10 // 10 minutes
	defaultMaxTriggerRequestDurationMs   = 1000 * 60      // 1 minute
	defaultNodeSendTimeoutMs             = 1000 * 10      // 10 seconds
	defaultInitialIntervalMs             = 100
	defaultMaxIntervalTimeMs             = 1000 * 30 // 30 seconds
	defaultMultiplier                    = 2.0
	defaultMetadataPullIntervalMs        = 1000 * 60 // 1 minute
	defaultMetadataAggregationIntervalMs = 1000 * 60 // 1 minute
	defaultMetadataPullRequestTimeoutMs  = 1000 * 30 // 30 seconds
	internalErrorMessage                 = "Internal server error occurred while processing the request"
	defaultOutboundRequestCacheTTLMs     = 1000 * 60 * 10      // 10 minutes
	defaultJWTReplayPeriodMs             = 1000 * 60 * 60 * 24 // 24 hours
	defaultSendResponseTimeoutMs         = 1000 * 5            // 5 seconds
```

**File:** core/services/gateway/handlers/capabilities/v2/http_handler.go (L46-64)
```go
type gatewayHandler struct {
	services.StateMachine
	config                 ServiceConfig
	shards                 []*shardEndpoint          // all DON shards served by this handler, across the full DON×shard matrix
	nodeAddrToShard        map[string]*shardEndpoint // node address -> owning shard, for routing responses back to the correct shard conn manager
	lggr                   logger.Logger
	httpClient             network.HTTPClient
	globalNodeRateLimiter  limits.RateLimiter            // Global rate limiter shared across all incoming node requests from workflow DON
	perNodeRateLimiters    map[string]limits.RateLimiter // Per-node rate limiters keyed by node address, one independent bucket per DON member
	mtlsRequestRateLimiter limits.RateLimiter
	mtlsConcurrencyLimiter limits.ResourcePoolLimiter[int] // Bounds the number of in-flight outbound mTLS requests
	wg                     sync.WaitGroup
	stopCh                 services.StopChan
	responseCache          ResponseCache // Caches HTTP responses to avoid redundant requests for outbound HTTP actions
	triggerHandler         HTTPTriggerHandler
	metadataHandler        *WorkflowMetadataHandler // Handles authorization for HTTP trigger requests
	metrics                *metrics.Metrics
	httpClientFactory      network.HTTPClientFactory
}
```
