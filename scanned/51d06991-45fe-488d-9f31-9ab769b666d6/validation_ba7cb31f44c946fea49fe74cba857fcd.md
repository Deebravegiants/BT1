## Title
Unbounded HTTP action response cache growth in gateway with no entry-count cap, only TTL-based eviction - (File: `core/services/gateway/handlers/capabilities/v2/response_cache.go`)

### Summary
The gateway's `responseCache` used to cache outbound HTTP action responses is a plain `map[string]*cachedResponse` that is only pruned periodically by TTL expiry (`DeleteExpired`), with no cap on the number of distinct entries it may hold. Any workflow whose HTTP action requests vary the cache key (URL, headers, body, method, workflow owner) accumulates one entry per distinct combination until the periodic cleanup ticks, and cleanup itself only removes *expired* entries, not enforcing any size bound — the same missing-eviction pattern as the reported browserslist advisory (unbounded cache growth via distinct query results, no size cap, TTL-only mitigation).

### Finding Description
`responseCache` is defined with a single `cache map[string]*cachedResponse` protected by `cacheMu`, and entries are written either through `Fetch` or `Set`: [1](#0-0) [2](#0-1) [3](#0-2) 

The only reclamation mechanism is `DeleteExpired`, invoked on a fixed timer (`CleanUpPeriodMs`, defaulting to 10 minutes) — it iterates the whole map and deletes entries whose TTL has passed, but never limits how many entries can accumulate between ticks: [4](#0-3) [5](#0-4) 

The cache key is derived from `req.Hash()`, computed over the outbound HTTP request's method, URL, headers, body, and workflow owner — all fields that originate from a workflow's HTTP action capability request and are attacker/user-controllable via the workflow definition executed by the DON. The request reaches the cache through `makeOutgoingRequest`, invoked from `HandleNodeMessage` for every `MethodHTTPAction` node response, with the cache lookup/store gated only on whether the workflow set `CacheSettings.Store`/`MaxAgeMs`, both of which are also part of the attacker-controlled request: [6](#0-5) 

Because the cache size is unbounded between cleanup ticks and the TTL used for eviction is itself workflow-configurable data (`req.CacheSettings.MaxAgeMs`), a workflow that issues many HTTP actions against distinct URLs/bodies/headers (with `Store: true` and a large `MaxAgeMs`) causes the map to grow without bound until the next `CleanUpPeriodMs` tick, and even then only entries whose `MaxAgeMs` has actually elapsed are purged. This mirrors the root cause in the external advisory: a plain object/map cache with no fixed maximum entry count or LRU-style eviction, so any calling code (here, workflow-originated HTTP action requests processed by the internet-facing gateway) that varies the cache key across many distinct values accumulates unbounded cached entries.

### Impact Explanation
Gateway process memory grows proportionally to the number of distinct outbound HTTP action requests cached, which is influenced by workflow owners (unprivileged relative to gateway operators) through ordinary use of the HTTP action capability. Sustained volume of distinct requests can exhaust gateway memory, causing an out-of-memory crash / denial of service of the shared gateway process serving the whole DON, consistent with CWE-770 (Allocation of Resources Without Limits or Throttling).

### Likelihood Explanation
Global and per-node rate limiters (`globalNodeRateLimiter`, `perNodeRateLimiters`) throttle the *rate* of node messages but do not bound the *number of distinct cache keys* accumulated over time, nor the cache's total size; a low-and-slow stream of distinct HTTP action requests spread over the default 10-minute cleanup window (or configured with a long `MaxAgeMs`) can still accumulate substantial unbounded state, matching the "volumetric, not single-request" characterization in the original advisory.

### Recommendation
Bound `responseCache.cache` by a fixed maximum entry count (e.g., LRU eviction or a hard cap enforced on write in `Fetch`/`Set`), independent of TTL-based cleanup, and consider clamping the workflow-supplied `MaxAgeMs` to a server-enforced maximum so TTL-based cleanup cannot be defeated by attacker-chosen values.

### Proof of Concept
1. As a workflow owner, submit a workflow whose HTTP action capability issues many requests with distinct URLs (or bodies/headers) and `CacheSettings.Store: true`, `MaxAgeMs` set to a large value.
2. Each request produces a unique `req.Hash()`, causing `rc.cache[cacheKey]` in `Set`/`Fetch` to add a new entry (`core/services/gateway/handlers/capabilities/v2/response_cache.go:93-120`).
3. Repeat across many distinct URLs/executions before the `CleanUpPeriodMs` ticker fires (`core/services/gateway/handlers/capabilities/v2/http_handler.go:476-487`); the map grows unboundedly since there is no entry-count cap, only TTL-gated cleanup.

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

**File:** core/services/gateway/handlers/capabilities/v2/response_cache.go (L93-102)
```go
		response := fetchFn()

		if storeOnFetch && isCacheableStatusCode(response.StatusCode) {
			rc.cacheMu.Lock()
			rc.cache[cacheKey] = &cachedResponse{
				response: response,
				storedAt: time.Now(),
			}
			rc.cacheMu.Unlock()
		}
```

**File:** core/services/gateway/handlers/capabilities/v2/response_cache.go (L111-120)
```go
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

**File:** core/services/gateway/handlers/capabilities/v2/http_handler.go (L476-487)
```go
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
```
