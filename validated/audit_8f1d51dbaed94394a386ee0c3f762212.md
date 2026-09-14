## Title
Unbounded HTTP action response cache in gateway allows memory-exhaustion DoS - (File: `core/services/gateway/handlers/capabilities/v2/response_cache.go`)

### Summary
The Mattermost advisory (GHSA-w496-f5qq-m58j) describes a memory-exhaustion bug where the `/api/v4/redirect_location` endpoint caches large fetched items without any limit on cache size, letting an attacker fill up server memory. The Gateway's HTTP Action capability (`gatewayHandler`) has an analogous unbounded cache: `responseCache` stores every distinct cacheable outbound-HTTP response in an in-memory map keyed only by a request hash, with no cap on entry count or total cached bytes.

### Finding Description
`responseCache` is a plain Go map (`cache map[string]*cachedResponse`) protected only by a mutex and a TTL, with no maximum size or eviction policy other than time-based expiry that runs on a periodic cleanup interval (`CleanUpPeriodMs`, default 10 minutes): [1](#0-0) 

Every response that is "cacheable" (2xx or 4xx status) is stored when `CacheSettings.Store` is true, regardless of how many distinct keys have already been cached: [2](#0-1) 

Cache entries are only removed by `DeleteExpired`, invoked on the `CleanUpPeriodMs` interval — there is no size-based eviction: [3](#0-2) 

Compare this to the sibling cache implementation `requestCache` in `core/services/gateway/handlers/common/requestcache.go`, which explicitly enforces a `maxCacheSize` and rejects new entries once full: [4](#0-3) 

The `responseCache` has no equivalent bound. The cache key is derived from `req.Hash()` (method, URL, headers, body, workflow owner), so any workflow that issues HTTP actions with distinct URLs/bodies/headers and `CacheSettings.Store=true` creates a new, permanent (until TTL) entry. Each entry can hold a response body up to `MaxResponseBytes` (configurable per request/client), so a workflow that issues many distinct cacheable requests can accumulate large amounts of cached response data in the gateway process's memory: [5](#0-4) 

The `HTTPClientConfig.MaxResponseBytes` field bounds only a single response's size, not the aggregate cache footprint: [6](#0-5) 

### Impact Explanation
A workflow owner (an unprivileged caller relative to the DON operator/gateway operator) can define a workflow that triggers HTTP Action capability calls with `CacheSettings.Store=true` and many distinct request variations (varying URL query strings, bodies, or headers), each returning a response near the configured `MaxResponseBytes` limit. Because the cache has no entry-count or total-size ceiling, and cleanup only runs periodically and only removes TTL-expired entries, the gateway process's memory usage grows proportionally to the number of distinct cached keys times response size, until the process is exhausted (OOM) or severely degraded — a denial of service for all workflows sharing that gateway process. This matches CWE-400 (uncontrolled resource consumption) in the same way as the Mattermost advisory.

### Likelihood Explanation
The HTTP Action path is a standard, documented capability of the CRE gateway (see `README.md` describing `responseCache`), reachable by any workflow that a workflow owner deploys and that a DON node executes on their behalf. No special privilege beyond normal workflow authoring is required to set `CacheSettings.Store=true` and vary request parameters to defeat the TTL-based dedup. The only mitigating factors are the per-response `MaxResponseBytes` cap and the default 10-minute cleanup/TTL interval, which slow but do not prevent unbounded growth within that window (and the workflow can simply keep generating new unique keys continuously).

### Recommendation
Add a maximum cache size (entry count and/or total byte budget) to `responseCache`, similar to the `maxCacheSize` enforcement in `common/requestcache.go`, and reject or evict (e.g., LRU) when the limit is reached. Consider also bounding the cache per-workflow (or per-owner) to prevent one workflow from starving cache capacity for others.

### Proof of Concept
1. Deploy a workflow that repeatedly invokes the HTTP Action capability with `CacheSettings.Store=true` and `CacheSettings.MaxAgeMs>0`, using a unique query parameter or body on every call to bypass the singleflight/cache-hit path.
2. Point each request at a controlled/public endpoint that returns a 200 response close to the configured `MaxResponseBytes`.
3. Repeat the pattern rapidly across many distinct keys (well within `OutboundRequestCacheTTLMs`/`CleanUpPeriodMs`, both default 10 minutes) so entries accumulate in `responseCache.cache` faster than `DeleteExpired` reclaims them.
4. Observe gateway process memory grow unbounded with the number of distinct cached responses, since `responseCache` in `core/services/gateway/handlers/capabilities/v2/response_cache.go` never rejects new entries based on size.

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

**File:** core/services/gateway/handlers/common/requestcache.go (L27-66)
```go
type requestCache[T any] struct {
	cache        map[globalID]*pendingRequest[T]
	maxCacheSize uint32
	timeout      time.Duration
	mu           sync.Mutex
}

type globalID struct {
	sender string
	id     string
}

type pendingRequest[T any] struct {
	handlers.Callback
	responseData *T
	timeoutTimer *time.Timer
	mu           sync.Mutex
}

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

**File:** core/services/gateway/network/httpclient.go (L32-34)
```go
type HTTPClientConfig struct {
	MaxResponseBytes uint32
	DefaultTimeout   time.Duration
```
