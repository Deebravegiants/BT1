Based on the investigation, the strongest reachable analog is the unbounded `responseCache` in the gateway's HTTP capability handler, which caches outbound HTTP responses keyed by request hash with no maximum entry count — only TTL-based eviction, mirroring the Acala bug class of "no minimum/no cap enforcement leading to storage bloat."

### Title
Unbounded HTTP Action Response Cache Allows Gateway Memory Bloat via Low-Cost Distinct Requests - (File: core/services/gateway/handlers/capabilities/v2/response_cache.go)

### Summary
The gateway's `responseCache` used by the HTTP Capability Handler stores one entry per distinct `(method, URL, headers, body, workflowOwner)` hash with no cap on the number of entries. Growth is bounded only by a time-based sweep (`DeleteExpired`), not by count, size, or a minimum-cost threshold, similar to Acala's `deposit_dex_share` allowing unlimited low-value positions with no minimum deposit.

### Finding Description
`responseCache.Set` and `responseCache.Fetch` insert a `cachedResponse` into the `cache map[string]*cachedResponse` for every cacheable (2xx/4xx) `OutboundHTTPRequest` whose hash is not already present or has expired [1](#0-0) , and `Set` similarly inserts unconditionally when cacheable [2](#0-1) . There is no maximum cache size field or eviction based on capacity — the only cleanup path is `DeleteExpired`, run on a periodic timer (`CleanUpPeriodMs`, default 10 minutes) [3](#0-2) . The cache key is derived from the full request (method/URL/headers/body/workflowOwner) via `req.Hash()`, so any workflow that varies the URL, query string, or body on each outbound HTTP action call creates a brand-new, permanent (until TTL) cache entry — there is no minimum request cost, no per-owner cap, and no dedup beyond exact hash match. The default TTL is 10 minutes (`defaultOutboundRequestCacheTTLMs`) [4](#0-3) . A workflow owner able to schedule/trigger many distinct outbound HTTP actions (a normal capability available to any onboarded workflow, not an operator-only feature) can therefore fill the gateway's in-memory cache with an unbounded number of entries within any 10-minute window, with the only mitigating control being the node-level rate limiters (`globalNodeRateLimiter`, `perNodeRateLimiters`) [5](#0-4) , which throttle request *rate* but do not cap the total number of *distinct cached keys* accumulated before the next cleanup cycle.

### Impact Explanation
Because the cache has no maximum size or minimum-cost gate, and its cleanup is purely time-based rather than capacity-based, an attacker-controlled workflow can drive unbounded memory growth on the gateway node between cleanup cycles, directly analogous to the referenced storage-bloat bug class (many low-cost/near-free operations creating persistent state with no floor). This can degrade gateway availability/performance for all workflows sharing that gateway instance (DoS-adjacent impact), though it does not by itself cause fund loss or cross-user data leakage since cache entries are scoped per-hash including `workflowOwner`.

### Likelihood Explanation
Likelihood is limited by the existing node/global rate limiters, which constrain how many requests (and thus how many new cache entries) a single workflow node can generate per unit time; however, no config parameter caps the *total number of distinct entries* resident in the cache at once, so sustained triggering by many workflow owners, or a rate limit set loosely relative to available memory, can still accumulate a large working set before the next `DeleteExpired` sweep. Whether this is practically exploitable to the point of DoS depends on the configured rate limits, TTL, and gateway memory headroom, none of which impose an explicit cap on cache entry count — the actual severity cannot be fully verified without profiling actual production rate-limit configuration and memory budgets.

### Recommendation
Add a maximum entry-count (or byte-size) bound to `responseCache`, evicting oldest/least-recently-used entries once the bound is reached, in addition to the existing TTL-based sweep — mirroring the Acala fix of introducing a floor/cap to prevent unbounded low-cost state creation. Consider also bounding per-workflow-owner cache usage independently of the global limiter.

### Proof of Concept
Not independently executable from this review (read-only index access), but the code path is deterministic:
1. A workflow owner triggers repeated HTTP Actions varying the URL/body each call.
2. Each call reaches `gatewayHandler.HandleNodeMessage` → `responseCache.Fetch`/`Set` [6](#0-5) .
3. Each distinct hash inserts a new, uncapped map entry, persisting until the next `DeleteExpired` run (default 10-minute interval) [4](#0-3) .
4. Repeating within the rate-limit budget across the TTL window accumulates cache entries with no absolute ceiling.

### Citations

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

**File:** core/services/gateway/handlers/capabilities/v2/response_cache.go (L122-136)
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
```

**File:** core/services/gateway/handlers/capabilities/v2/http_handler.go (L29-44)
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
)
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
