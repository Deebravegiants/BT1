### Title
Unbounded outbound HTTP response cache growth via `CacheSettings.Store`/`MaxAgeMs` — no size cap analogous to missing `TOKEN_ADDRESS_LIMIT` enforcement - (File: core/services/gateway/handlers/capabilities/v2/response_cache.go)

### Summary
The `responseCache` used by the CRE Gateway's HTTP-action capability handler stores an entry per unique request hash with no upper bound on the number of entries, mirroring the reported bug class where a whitelist/limit is declared but never enforced at the insertion point.

### Finding Description
`responseCache` is a `map[string]*cachedResponse` guarded by a mutex, with insertion happening in `Set` and `Fetch`. Neither path checks any maximum size before inserting a new key: [1](#0-0) [2](#0-1) 

The cache key is `req.Hash()`, described as being derived from "method, URL, headers, body, workflowOwner": [3](#0-2) 

This is reachable from workflow-node-originated HTTP action requests processed by `gatewayHandler.makeOutgoingRequest`, which unmarshals an `OutboundHTTPRequest` from the node message and, based on `CacheSettings`, calls `responseCache.Fetch` (when `MaxAgeMs > 0`) or `responseCache.Set` (when `Store` is true) — both fully attacker/workflow-controlled fields inside the request payload: [4](#0-3) 

The only mitigation present is periodic TTL-based expiry via `DeleteExpired`, run on a fixed timer (`CleanUpPeriodMs`, default 10 minutes): [5](#0-4) [6](#0-5) 

Unlike this cache, the sibling `RequestCache` type in the same gateway handlers package does enforce an explicit size cap before insertion: [7](#0-6) 

This confirms the pattern is understood and applied elsewhere in the codebase, but was omitted for `responseCache` — directly analogous to `TOKEN_ADDRESS_LIMIT` being declared and intended, but never checked in `addToken()`.

### Impact Explanation
A workflow (an unprivileged actor relative to the gateway/node infrastructure, since workflow execution is untrusted input by design per the comment "all fields set on the request come from untrusted nodes") can vary the URL, headers, body, or timing of its HTTP action requests with `CacheSettings.Store=true` or `MaxAgeMs>0` to generate an effectively unbounded number of distinct cache keys within a single TTL window (default 10 minutes). Because entries persist until the periodic cleanup and the cleanup only removes *expired* entries (not excess entries under a cap), this can grow the in-memory map without bound, leading to memory exhaustion / denial of service on the gateway host serving the entire DON, affecting cache availability and gateway stability for all workflows sharing that gateway instance.

### Likelihood Explanation
Reasonably likely: `Store` and `MaxAgeMs`/cache-key-affecting fields are attacker-influenced fields of the `OutboundHTTPRequest` payload originating from workflow node HTTP action calls, requiring no special privilege beyond running a workflow capable of issuing HTTP actions with distinct target URLs/bodies. There is a global/per-node rate limiter on request throughput (`globalNodeRateLimiter`, `perNodeRateLimiters`), which limits the rate of cache-key generation but does not cap total cache size, so sustained (rate-limited but non-zero) traffic can still accumulate unbounded entries over the TTL window.

### Recommendation
Introduce an explicit maximum entry count (or memory budget) for `responseCache`, analogous to `RequestCache.maxCacheSize`, and reject or LRU-evict when the cap is reached, e.g., checking `len(rc.cache) >= maxSize` before insertion in both `Set` and the singleflight callback path in `Fetch`.

### Proof of Concept
1. As a workflow author, issue repeated HTTP action requests through the gateway's `MethodHTTPAction` flow, each with a unique `URL`/`Body` combination and `CacheSettings.Store = true` (or `MaxAgeMs > 0`).
2. Each request produces a distinct `req.Hash()` key, and `responseCache.Set`/`Fetch` inserts a new map entry with no bound check.
3. Repeat within the `OutboundRequestCacheTTLMs` window (default 10 minutes) at whatever rate the rate limiters permit; because there is no cap on cache size, entries accumulate rather than being rejected, growing gateway process memory until `DeleteExpired` runs on its next 10-minute tick — and even then, only expired (not excess) entries are removed.

**Uncertainty**: I could not fully verify the size of `OutboundHTTPRequest`/response payloads or the exact rate-limit throughput values (`cresettings.Default.GatewayHTTPGlobalRate`, `GatewayHTTPPerNodeRate`) that would bound how quickly memory grows, since those config defaults were not in the indexed files I could inspect. This affects the concrete severity/time-to-impact but not the underlying root-cause finding that no size limit exists on `responseCache`.

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
