### Title
Unbounded, size-uncapped HTTP response cache in the CRE Gateway allows memory-exhaustion DoS via attacker-controlled cache keys - ([File: core/services/gateway/handlers/capabilities/v2/response_cache.go])

### Summary
The Gateway's HTTP Action response cache (`responseCache`) stores every cacheable response in an in-memory `map[string]*cachedResponse` that is only pruned by a periodic, time-based sweep (`DeleteExpired`), with no maximum entry count or maximum total size. The cache key is derived from `OutboundHTTPRequest.Hash()`, which is computed from the method, URL, headers, and body of the outbound HTTP action request — fields that are fully attacker-controlled by any workflow able to invoke the `HTTPAction` capability. This mirrors the root cause of CVE-2021-44716 (`golang.org/x/net/http2` header-canonicalization cache): an unauthenticated/low-privilege caller can grow an internal cache without bound because the cache has no capacity limit, only a delayed cleanup pass.

### Finding Description
`responseCache` is created with only a TTL, no capacity bound: [1](#0-0) 

Entries are written into the map on every cacheable response, keyed by `req.Hash()`: [2](#0-1) [3](#0-2) 

The only reclamation mechanism is a periodic full-map scan for TTL-expired keys, run on a ticker interval (`CleanUpPeriodMs`, default 10 minutes): [4](#0-3) [5](#0-4) 

The cache is populated directly from workflow-node-originated `HTTPAction` requests, whose `Method`, `URL`, `Headers`/`MultiHeaders`, and `Body` are attacker/workflow-controlled and feed straight into `req.Hash()` (per the README, the key is "generated from workflow ID and request hash," and the cache doc comment states it's keyed by "method, URL, headers, body, workflowOwner"): [6](#0-5) [7](#0-6) 

Because `req.Hash()` incorporates the full URL, headers, and body, an actor driving a workflow can trivially mint unlimited distinct cache keys (e.g., by varying a query parameter, a header value, or the body on each call) while setting `CacheSettings.Store = true` on 2xx/4xx-returning requests, causing the map to grow without bound between cleanup ticks. Rate limiters (`globalNodeRateLimiter`, `perNodeRateLimiters`, `userRateLimiter`) bound the *rate* of requests but not the *distinctness* of cache keys or the *cumulative size* of the cache, so sustained legitimate-rate traffic with varied keys still accumulates unboundedly for up to the full cleanup period (and each entry holds a full response body/headers, further multiplying memory pressure).

### Impact Explanation
An authenticated CRE workflow (a normal, non-privileged tenant/owner, not a node operator) can force the Gateway process to allocate unbounded memory for the response cache, degrading or crashing the Gateway (denial of service) for all workflows and DONs sharing that Gateway instance. This is directly analogous to CWE-400 (uncontrolled memory consumption) from the referenced CVE, where an unbounded internal cache keyed by attacker-influenced input caused OOM conditions in Go's HTTP/2 stack.

### Likelihood Explanation
Medium-to-High. No special privilege is required beyond deploying/running a workflow that performs `HTTPAction` calls with `CacheSettings.Store = true` and varying request parameters (URL query strings, headers, or body) that return 2xx/4xx responses. Existing rate limiters slow but do not prevent steady accumulation, and the cleanup interval (default 10 minutes) provides a wide window for growth.

### Recommendation
- Add a bounded eviction policy (e.g., LRU/LFU with a max entry count and/or max total cache-size budget in bytes) to `responseCache`, evicting oldest/largest entries when limits are exceeded, in addition to TTL-based cleanup.
- Consider incorporating a per-workflow-owner cap on the number of outstanding cache entries or total cached bytes, so a single tenant cannot exhaust the shared cache.
- Reduce the default `CleanUpPeriodMs` or make cleanup incremental/size-aware rather than a single periodic full sweep, and export the current cache size as an alerting metric (it already records `RecordCacheSize`, so an alert/limit could be attached to it).

### Proof of Concept
1. Deploy a CRE workflow authorized to invoke the `HTTPAction` capability on a Gateway with `OutboundRequestCacheTTLMs` at (or below) its default (10 minutes).
2. From the workflow, repeatedly issue outbound HTTP actions to an endpoint the caller controls, varying a request parameter each call (e.g. `GET https://example.com/?nonce=<random>` or a varying header/body), each with `CacheSettings.Store = true` and a response that returns 2xx.
3. Because each variation produces a distinct `req.Hash()`, `responseCache.Set`/`Fetch` inserts a new map entry per call; at sustained (rate-limited but non-trivial) throughput, thousands of entries accumulate before the next `DeleteExpired` sweep, each holding response headers/body, increasing Gateway process memory usage until cleanup runs or memory pressure causes degradation/OOM.

### Citations

**File:** core/services/gateway/handlers/capabilities/v2/response_cache.go (L15-16)
```go
// responseCache is a thread-safe cache for storing HTTP responses.
// It uses a map to store responses keyed by a hash of the request (method, URL, headers, body, workflowOwner).
```

**File:** core/services/gateway/handlers/capabilities/v2/response_cache.go (L31-38)
```go
func newResponseCache(lggr logger.Logger, ttlMs int, metrics *metrics.Metrics) *responseCache {
	return &responseCache{
		cache:   make(map[string]*cachedResponse),
		lggr:    logger.Named(lggr, "ResponseCache"),
		ttl:     time.Duration(ttlMs) * time.Millisecond,
		metrics: metrics,
	}
}
```

**File:** core/services/gateway/handlers/capabilities/v2/response_cache.go (L93-108)
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

	return result.(gateway.OutboundHTTPResponse)
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
