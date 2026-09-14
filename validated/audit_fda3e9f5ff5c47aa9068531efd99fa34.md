### Title
Unbounded response-header caching enables gateway memory-exhaustion DoS analogous to CVE-2022-32205 - (File: `core/services/gateway/handlers/capabilities/v2/response_cache.go`)

### Summary
The gateway's HTTP capability handler makes outbound HTTP requests to URLs supplied in a workflow's `OutboundHTTPRequest` and caches the full response — including all `Set-Cookie`/other response headers — in an in-process map keyed by a request hash, with no per-entry size limit and no cap on the number of headers or total cache size, only TTL-based expiry.

### Finding Description
`httpClient.Send` bounds only the response **body** size via `http.MaxBytesReader` using `MaxResponseBytes` (default ~26.4KB) [1](#0-0) , but it does not configure `MaxResponseHeaderBytes` on the transport, and response headers are copied wholesale into `HTTPResponse.MultiHeaders`/`Headers` without any size or count cap [2](#0-1) .

That unbounded response, including its headers, is then stored verbatim in `responseCache.cache`, a plain map protected only by a mutex, with entries evicted solely by TTL-based `DeleteExpired` sweeps run on a periodic cleanup timer (default 10 minutes) — there is no maximum entry count or maximum stored-bytes limit [3](#0-2) [4](#0-3) . `Set`/`Fetch` cache any 2xx/4xx response as long as `CacheSettings.Store` is true [5](#0-4) , and the cache key is derived from `req.Hash()` (method/URL/headers/body/workflow owner), so an unprivileged workflow author can generate an effectively unlimited number of distinct cache keys against their own attacker-controlled external endpoint.

This mirrors the CVE-2022-32205 bug class: a remote endpoint response floods a client-side store (curl's cookie jar there, the gateway's shared response cache here) with excessive header data that is retained far past a sane size threshold, degrading service for the whole client (curl process there; the multi-tenant gateway process here).

### Impact Explanation
A workflow author who controls the target of their own `OutboundHTTPRequest` (a legitimate but unprivileged capability of any workflow) can point the HTTP Action capability at a server they control, which returns a very large volume of headers (bounded only by Go's default ~10MB header-read limit, since `MaxResponseHeaderBytes` is unset) per response, and repeat with many distinct request variants (different URL query strings, header sets, bodies) to generate many distinct cache keys. Because the response cache has no entry-count or total-size cap, this can inflate gateway process memory across all tenants sharing that gateway instance, potentially causing degraded performance or OOM for the shared gateway service — a resource-exhaustion/DoS impact analogous to the curl advisory, though bounded in severity by the 10-minute cache TTL and (default) response body size cap.

### Likelihood Explanation
Any workflow author capable of submitting an `OutboundHTTPRequest` with `CacheSettings.Store: true` can trigger this without any special privileges, and they fully control the responding server's headers, making exploitation straightforward for someone willing to run a small external server. The lack of Go-level `MaxResponseHeaderBytes` configuration and lack of any cache-size bound in `responseCache` make this a real, reachable gap rather than a purely theoretical one, though actual DoS severity depends on how much gateway memory is available and how aggressively an attacker automates distinct cache-key generation.

### Recommendation
- Set an explicit `MaxResponseHeaderBytes` on the HTTP client's transport (in `core/services/gateway/network/httpclient.go`) to a small, sane limit, rather than relying on Go's large default.
- Enforce a per-response header size/count cap before storing into `HTTPResponse`.
- Add a maximum total cache size (bytes or entry count) with LRU/size-based eviction in `responseCache` (`core/services/gateway/handlers/capabilities/v2/response_cache.go`), independent of the TTL sweep, so a burst of large cacheable responses cannot unboundedly grow the map between cleanup cycles.
- Consider capping cached response header size specifically, separate from the (already-capped) body size.

### Proof of Concept
1. Deploy a workflow that issues an `OutboundHTTPRequest` with `CacheSettings.Store: true` targeting an attacker-controlled HTTPS server.
2. Configure that server to respond 200 OK with thousands of large `Set-Cookie` (or other) headers, up to the Go default header-read ceiling.
3. Repeat step 1–2 many times with varying request parameters (URL path/query, header sets) to generate many distinct `req.Hash()` cache keys.
4. Observe the gateway process's memory grow proportionally to `(number of distinct requests) × (header bytes per response)`, persisting for up to the configured `OutboundRequestCacheTTLMs` (default 10 minutes) before `DeleteExpired` reclaims it — during which other tenants' gateway traffic may be degraded.

### Citations

**File:** core/services/gateway/network/httpclient.go (L220-232)
```go
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

**File:** core/services/gateway/handlers/capabilities/v2/response_cache.go (L93-137)
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
