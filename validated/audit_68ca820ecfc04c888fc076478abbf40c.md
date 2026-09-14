## Analysis Result

<title>Unbounded HTTP Response Cache Growth in Gateway Causes Memory Exhaustion - (File: core/services/gateway/handlers/capabilities/v2/response_cache.go)</title>

### Summary
The gateway's HTTP capability handler caches outbound HTTP action responses in an in-memory map keyed by a hash of the request (method, URL, headers, body, workflowOwner). This cache has no maximum size/entry-count bound — the only cleanup mechanism is a periodic TTL sweep run on a fixed interval. A workflow author (an unprivileged actor relative to the gateway process — they do not need node-operator or admin privileges) fully controls the fields that make up the cache key and can set `CacheSettings.Store`/`MaxAgeMs` to force caching. By causing many distinct cacheable HTTP action requests to be issued faster than the periodic cleanup can reclaim expired entries, an attacker can grow the cache map unbounded between cleanup cycles, exhausting gateway memory. This mirrors the root-cause pattern in CVE-2023-39180 — memory not being released for the effective lifetime of a resource, leading to a DoS — mapped here to an unbounded, attacker-keyed cache instead of a kernel SMB2_READ buffer.

### Finding Description
`responseCache` stores entries in a plain map with no capacity limit: [1](#0-0) 

Entries are only removed by a periodic `DeleteExpired` sweep, which only deletes entries whose TTL (`rc.ttl`, sourced from `OutboundRequestCacheTTLMs`, default 10 minutes) has elapsed: [2](#0-1) 

This sweep runs on a fixed timer (`CleanUpPeriodMs`) started in `gatewayHandler.Start`: [3](#0-2) 

Cache entries are created in `makeOutgoingRequest`, which handles outgoing HTTP action requests forwarded from a DON node on behalf of a workflow. The cache key is derived from request fields (`req.Hash()`) that come directly from the outbound HTTP action request — method, URL, headers, body, and `CacheSettings` — all of which are set by workflow logic (i.e., ultimately controlled by whoever authored/deployed the workflow, not just the node operator): [4](#0-3) 

Because `req.Hash()` incorporates the full request (URL/headers/body/owner), an attacker can trivially generate an unbounded number of distinct cache keys (e.g., varying a query parameter or header per call) while setting `CacheSettings.Store = true` and a nonzero `MaxAgeMs`, forcing each unique response into the cache via `Set`/`Fetch`: [5](#0-4) 

Existing mitigations (global/per-node rate limiters) only throttle request *throughput*, not the *number of distinct cache keys* accumulated. As long as the sustained rate of unique cacheable requests exceeds the reclamation rate of the periodic `DeleteExpired` sweep (bounded by the `CleanUpPeriodMs`/TTL window), the map — holding full response bodies/headers per entry — grows without bound, consuming gateway process memory. This is the same underlying flaw class as CVE-2023-39180: a resource (here, cached response memory) is not reclaimed within its effective lifetime under sustained, low-privilege-triggered load, producing a availability impact.

### Impact Explanation
Unbounded memory growth on the gateway process can lead to OOM and denial of service for the entire gateway (all workflows/DON members routed through it), not just the attacker's own workflow. This is a high-availability-impact issue matching the CVSS profile of the referenced CVE (`AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H`).

### Likelihood Explanation
Likelihood is moderate-to-high: no special privileges are required beyond the ability to author/deploy a workflow that issues outbound HTTP actions with cacheable settings and varying request parameters, which is a normal capability available to workflow authors. The attack requires sustained request volume but is not otherwise constrained by any per-workflow cache-size quota.

### Recommendation
- Enforce a maximum entry count (or maximum aggregate memory size) on `responseCache.cache`, evicting oldest/least-recently-used entries (e.g., LRU) when the limit is exceeded, similar to the `maxCacheSize` bound already used in `core/services/gateway/handlers/common/requestcache.go`.
- Consider a per-workflow-owner cache-entry quota so a single workflow cannot monopolize gateway cache memory.
- Bound cached response body size explicitly (beyond `MaxResponseBytes` per response) against total cache memory usage, and expose a metric/alert for cache size approaching configured limits.

### Proof of Concept
1. Deploy a workflow whose action capability issues outbound HTTP requests with `CacheSettings.Store = true` and `MaxAgeMs > 0`.
2. Vary a request field that participates in `req.Hash()` (e.g., a query string parameter or header value) on each invocation so every request produces a unique cache key.
3. Repeatedly trigger the workflow (within the allowed rate limit) so that the number of new unique cache entries created per `CleanUpPeriodMs` window exceeds the number of entries expiring/being purged by `DeleteExpired` in that same window.
4. Observe gateway process memory grow proportionally to the number of accumulated unique cached responses until reclaimed by the next TTL sweep or until the process is exhausted.

### Citations

**File:** core/services/gateway/handlers/capabilities/v2/response_cache.go (L17-24)
```go
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

**File:** core/services/gateway/handlers/capabilities/v2/http_handler.go (L465-489)
```go
func (h *gatewayHandler) Start(ctx context.Context) error {
	return h.StartOnce(handlerName, func() error {
		h.lggr.Info("Starting " + handlerName)
		err := h.triggerHandler.Start(ctx)
		if err != nil {
			return fmt.Errorf("failed to start HTTP trigger handler: %w", err)
		}
		err = h.metadataHandler.Start(ctx)
		if err != nil {
			return fmt.Errorf("failed to start HTTP auth handler: %w", err)
		}
		h.wg.Go(func() {
			ticker := time.NewTicker(time.Duration(h.config.CleanUpPeriodMs) * time.Millisecond)
			defer ticker.Stop()
			for {
				select {
				case <-ticker.C:
					h.responseCache.DeleteExpired(ctx)
				case <-h.stopCh:
					return
				}
			}
		})
		return nil
	})
```
