### Title
Unbounded growth of the Gateway HTTP-capability `responseCache` — no maximum-size enforcement, unlike sibling `requestCache` - (File: core/services/gateway/handlers/capabilities/v2/response_cache.go)

### Summary
The Sherlock report's bug class is "lack of validation to check whether a bounded total (max supply) is respected before creating/inserting a new record, allowing unbounded growth." The direct chainlink analog is the Gateway's HTTP-capability `responseCache`, which caches `OutboundHTTPResponse` entries keyed by a hash of the outbound HTTP request, with **no check on the maximum number of cache entries** before insertion — unlike the sibling `requestCache` type in the same package tree, which explicitly enforces a `maxCacheSize` and rejects new entries once the limit is reached.

### Finding Description
`responseCache.Fetch` and `responseCache.Set` both insert new entries into the `rc.cache` map keyed by `req.Hash()` with no bound on `len(rc.cache)`: [1](#0-0) [2](#0-1) 

The only way entries are removed is time-based (`DeleteExpired`, invoked periodically by a background ticker), not size-based: [3](#0-2) 

This is called every `CleanUpPeriodMs` (default 10 minutes): [4](#0-3) 

Contrast this with `common.requestCache`, which is the pattern that should have been reused: it takes an explicit `maxCacheSize` and returns an error, refusing to add new entries once full: [5](#0-4) 

Entries are added to `responseCache` from `gatewayHandler.makeOutgoingRequest`, which is reachable whenever a workflow DON node relays an `OutboundHTTPAction` result back to the gateway; the cache key is derived from `req.Hash()` (method, URL, headers, body, workflow owner) with `CacheSettings.Store`/`MaxAgeMs` set by the workflow itself: [6](#0-5) 

Because the cache key is derived from request content that is ultimately controlled by workflow authors (unprivileged actors who submit workflows executed by the DON with `CacheSettings.Store = true`), an attacker can cause an unbounded number of distinct cache keys (e.g., by varying the URL, headers, or body across many HTTP-action calls in a workflow) to be inserted into `rc.cache`, with no size ceiling analogous to `requestCache.maxCacheSize`.

### Impact Explanation
Unbounded insertion into `rc.cache` allows memory to grow without limit until the next `DeleteExpired` sweep (up to `CleanUpPeriodMs`, default 10 minutes), and even that sweep only removes *expired* entries — an attacker generating fresh unique keys faster than the TTL will keep the cache growing indefinitely. This is a resource-exhaustion (denial-of-service) risk on the Gateway process, which is shared across all DONs/workflows served by that gateway node, directly mirroring the report's "no cap enforced, entities keep accumulating beyond the intended bound" bug class.

### Likelihood Explanation
Medium: reaching this path only requires submitting workflows with HTTP-action triggers whose `CacheSettings.Store` is true and whose request parameters vary (which are attacker/workflow-owner-controlled), causing the gateway to accumulate a distinct cache key per unique request. No node compromise or gateway-internal privilege is required — this is standard workflow behavior exploited at volume, distinguishing it from a "malicious node" scenario.

### Recommendation
Add an explicit maximum-size check to `responseCache` (mirroring `common.requestCache.NewRequest`'s `len(c.cache) >= int(c.maxCacheSize)` guard) before inserting new entries in both `Fetch`'s slow path and `Set`, e.g.:
```go
if storeOnFetch && isCacheableStatusCode(response.StatusCode) {
    rc.cacheMu.Lock()
    if len(rc.cache) < rc.maxCacheSize {
        rc.cache[cacheKey] = &cachedResponse{response: response, storedAt: time.Now()}
    }
    rc.cacheMu.Unlock()
}
```
and reject/skip caching (or evict oldest) once the configured limit is reached, with the limit sized and exposed via `ServiceConfig` like the other tunables in that struct.

### Proof of Concept
1. A workflow owner deploys a workflow that issues many HTTP action calls with `CacheSettings.Store = true` and unique request parameters (e.g., varying query string or body) on each call.
2. Each unique request produces a distinct `req.Hash()` cache key.
3. `gatewayHandler.makeOutgoingRequest` → `responseCache.Set`/`Fetch` inserts a new map entry for every unique key with no check against any maximum count.
4. Repeating this at scale grows `rc.cache` without bound until the next `DeleteExpired` sweep, and can be sustained indefinitely by generating new unique keys faster than the TTL/cleanup interval, exhausting gateway memory. [7](#0-6)

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

**File:** core/services/gateway/handlers/capabilities/v2/response_cache.go (L93-105)
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

		return response, nil
	})
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

**File:** core/services/gateway/handlers/common/requestcache.go (L46-66)
```go
func NewRequestCache[T any](timeout time.Duration, maxCacheSize uint32) RequestCache[T] {
	return &requestCache[T]{cache: make(map[globalID]*pendingRequest[T]), timeout: timeout, maxCacheSize: maxCacheSize}
}

func (c *requestCache[T]) NewRequest(lggr logger.Logger, request *api.Message, callback handlers.Callback, responseData *T) error {
	if request == nil {
		return errors.New("request is nil")
	}
	if responseData == nil {
		return errors.New("responseData is nil")
	}
	key := globalID{request.Body.Sender, request.Body.MessageID}
	c.mu.Lock()
	defer c.mu.Unlock()
	_, ok := c.cache[key]
	if ok {
		return errors.New("request already exists")
	}
	if len(c.cache) >= int(c.maxCacheSize) {
		return errors.New("request cache is full")
	}
```
