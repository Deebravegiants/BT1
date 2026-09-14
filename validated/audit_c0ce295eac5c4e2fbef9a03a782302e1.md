### Title
Unbounded HTTP response cache growth in Gateway HTTP capability handler enables memory-exhaustion DoS - ([File: core/services/gateway/handlers/capabilities/v2/response_cache.go])

### Summary
The Guzzle advisory describes storage of attacker-controlled `Set-Cookie` data with no limit on the number of cookies, their size, or generated header length, letting a malicious response drive unbounded memory use. The Chainlink Gateway's HTTP Action `responseCache` has an analogous unbounded-storage problem: it caches full HTTP responses — including arbitrary response headers such as `Set-Cookie`/`MultiHeaders` — keyed by a request hash, with no maximum entry count and no per-entry header/size cap, evicting only by TTL on a periodic timer.

### Finding Description
`responseCache` is a `map[string]*cachedResponse` guarded by a mutex, with entries added by `Set` and `Fetch` whenever `req.CacheSettings.Store` is true and the response is "cacheable" (2xx/4xx): [1](#0-0) [2](#0-1) 

Cache eviction is exclusively time-based, run periodically via `DeleteExpired`; there is no maximum entry count, no total cache memory budget, and no cap on the size/number of headers or cookies stored per entry: [3](#0-2) 

The cached `gateway.OutboundHTTPResponse` includes `MultiHeaders`, which preserves every header value returned by the target server, including all `Set-Cookie` values, without any per-header-name count or byte limit: [4](#0-3) 

The outbound HTTP request path is triggered by `makeOutgoingRequest`, where a workflow node supplies `CacheSettings.Store` and the target `req.URL`; if `Store` is true the fetched response is unconditionally handed to `h.responseCache.Set`: [5](#0-4) 

Only the response *body* is size-bounded (`MaxResponseBytes`, default ~26.4KB) via `http.MaxBytesReader`; headers are read in full up to Go's `net/http` transport default limits, which are far larger than the body cap: [6](#0-5) [7](#0-6) 

A workflow author (an authenticated but otherwise unprivileged Gateway client relative to node operators) controls the outbound URL and can point it at a server they control (or a compromised third party). By varying the request (URL/body/headers so `OutboundHTTPRequest.Hash()` differs) they can generate an unbounded number of distinct cache keys, each backed by a response carrying many/large `Set-Cookie` (or other) headers, all retained in the shared, process-wide `responseCache` until the next TTL sweep (default cleanup period 10 minutes, cache TTL configurable, default 10 minutes): [8](#0-7) 

Because the cache is shared across all DON shards/workflows served by one `gatewayHandler` instance, this growth is not isolated to the attacker's own workflow and can degrade or exhaust gateway memory for co-tenant workflows — the same "one bad actor harms unrelated consumers of a shared store" shape as the Guzzle cookie-jar issue.

### Impact Explanation
Unbounded, TTL-only-evicted caching of externally-controlled headers/cookies allows a single unprivileged workflow owner to drive unbounded memory growth in the Gateway process by repeatedly triggering cacheable outbound HTTP actions against an attacker-controlled endpoint that returns many large `Set-Cookie`/header values, with no entry-count or total-size ceiling on the cache. This can lead to memory exhaustion / degraded availability for the Gateway and any other workflows relying on the same shared handler instance (CWE-770/CWE-1325 style resource exhaustion), matching the "availability" impact class of the reference advisory.

### Likelihood Explanation
Reachable from any workflow author who can configure an HTTP Action with `CacheSettings.Store=true` pointing at a server they control — no elevated privilege beyond normal workflow authoring is required. The only friction is generating a sufficient number of distinct cache keys and waiting out the TTL window, both trivially automatable, so likelihood is moderate-to-high in a multi-tenant Gateway deployment.

### Recommendation
Bound the `responseCache`: enforce a maximum number of cache entries (with LRU/oldest-eviction) and/or a total-cache byte budget, cap the number and total size of headers (especially `Set-Cookie`) retained per cached response, and consider scoping/limiting cache usage per workflow owner so one tenant cannot exhaust cache capacity for others.

### Proof of Concept
1. Author a workflow with an HTTP Action pointing `URL` at an attacker-controlled server and set `CacheSettings.Store = true`.
2. Have the attacker server return many large `Set-Cookie` headers (or other large headers) with a 200/4xx status on each distinct request variant.
3. Repeat the request with slight variations (query params/body) to produce many distinct `OutboundHTTPRequest.Hash()` values, each triggering `responseCache.Set` to add a new, header-heavy entry.
4. Observe the `responseCache.cache` map (and process RSS) grow without bound between TTL cleanup cycles, since no entry-count or size cap exists in `Set`/`Fetch`/`DeleteExpired`.

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

**File:** core/services/gateway/handlers/capabilities/v2/response_cache.go (L110-120)
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

**File:** core/services/gateway/network/httpclient.go (L132-138)
```go
	defaultMaxResponseBytes   = uint32(26.4 * utils.KB)
	defaultMaxRequestDuration = 60 * time.Second
	defaultTimeout            = 5 * time.Second
	ErrBlockedRequest         = errors.New("blocked request")
	ErrHTTPSend               = errors.New("failed to send HTTP request")
	ErrHTTPRead               = errors.New("failed to read HTTP response body")
)
```

**File:** core/services/gateway/network/httpclient.go (L196-232)
```go
type HTTPResponse struct {
	StatusCode   int                 // HTTP status code
	Headers      map[string]string   // HTTP headers (deprecated: use MultiHeaders, contains first value only for backward compatibility)
	MultiHeaders map[string][]string // HTTP headers with all values preserved
	Body         []byte              // HTTP response body
}

// requestToNetHeader builds net/http.Header from req. Uses MultiHeaders when set, otherwise Headers.
func requestToNetHeader(req HTTPRequest) http.Header {
	out := make(http.Header)
	if len(req.MultiHeaders) > 0 {
		for k, values := range req.MultiHeaders {
			for _, v := range values {
				out.Add(k, v)
			}
		}
		return out
	}
	for k, v := range req.Headers {
		out.Add(k, v)
	}
	return out
}

// responseHeadersFromNetHeader builds Headers (comma-joined) and MultiHeaders from net/http.Header. Skips keys with no values.
func responseHeadersFromNetHeader(h http.Header) (map[string]string, map[string][]string) {
	headers := make(map[string]string, len(h))
	multiHeaders := make(map[string][]string, len(h))
	for k, v := range h {
		if len(v) == 0 {
			continue
		}
		multiHeaders[k] = slices.Clone(v)
		headers[k] = strings.Join(v, ",")
	}
	return headers, multiHeaders
}
```

**File:** core/services/gateway/network/httpclient.go (L490-499)
```go
	n := maxReadBytes(readSize{defaultSize: c.config.MaxResponseBytes, requestSize: req.MaxResponseBytes})
	c.lggr.Debugw("max bytes to read from HTTP response", "bytes", n)

	reader := http.MaxBytesReader(nil, resp.Body, int64(n))
	body, err := io.ReadAll(reader)
	if err != nil {
		c.metrics.recordTotal(ctx, req.Method, resp.StatusCode, false, traceState.connReused.Load(), time.Since(requestStart))
		c.lggr.Errorw("failed to read HTTP response body", "err", err)
		return nil, errors.Join(err, ErrHTTPRead)
	}
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
