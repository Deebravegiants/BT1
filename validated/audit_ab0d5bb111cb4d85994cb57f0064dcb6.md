### Title
Gateway HTTP response cache ignores per-request `MaxAgeMs` freshness bound during concurrent singleflight coalescing, serving stale data despite an explicit no-cache/strict-freshness request - (File: core/services/gateway/handlers/capabilities/v2/response_cache.go)

### Summary
Similar to the Illuminate `ERC5095` bug where a user-specified slippage bound was silently loosened by the contract before being enforced, Chainlink's gateway HTTP response cache accepts a caller-specified freshness bound (`CacheSettings.MaxAgeMs`) but does not actually enforce it once a request is coalesced with a concurrent request via `singleflight`. The cache key used for both the map and the `singleflight.Group` deliberately excludes `CacheSettings` [1](#0-0) , so a request that wants strict freshness (including `MaxAgeMs: 0`, i.e. "do not use cache") can be transparently merged into another concurrent request's flight and receive that other request's stale answer, evaluated only against the other request's laxer bound.

### Finding Description
`responseCache.Fetch` computes `cacheMaxAge := time.Duration(req.CacheSettings.MaxAgeMs) * time.Millisecond` and checks it in a "fast path" against the caller's own request [2](#0-1) . If the fast-path check misses (no entry, or entry stale relative to *this* caller's bound), the call proceeds into `rc.flight.Do(cacheKey, ...)`, where `cacheKey := req.Hash()` [3](#0-2) .

`OutboundHTTPRequest.Hash()` is confirmed by tests to be identical regardless of `CacheSettings` (i.e., regardless of `MaxAgeMs`/`Store`) [1](#0-0) . Because `singleflight.Group.Do` executes the supplied closure only once per key and shares the result with all concurrent callers keyed the same way, only the *first* caller to enter `flight.Do` for a given URL/method/body/owner actually runs the closure; every other concurrent caller for that key is a "joiner" that receives the leader's result without its own `cacheMaxAge` ever being evaluated.

Inside the closure, the freshness re-check uses the closed-over `cacheMaxAge` variable from the flight leader's call: `cachedResp.storedAt.Add(cacheMaxAge).After(time.Now())` [4](#0-3) . If the leader's own `cacheMaxAge` is large (a lax bound) and the cache already holds an entry that is "fresh enough" for the leader but *not* fresh enough for a stricter joiner (e.g. a joiner that set `MaxAgeMs: 0` to explicitly bypass caching), the joiner nonetheless receives that stale cached response, in direct violation of its own explicit freshness request — exactly analogous to `ERC5095.withdraw()`/`redeem()` silently applying `a - (a/100)` instead of the caller-specified `a`, allowing more deviation from the requested bound than the caller asked for.

### Impact Explanation
A workflow (or DON node acting on behalf of a workflow) that explicitly requests strict freshness or no caching for an outbound HTTP action can silently receive out-of-date external data instead of the fresh data it required. Because HTTP Action results can feed downstream workflow logic (potentially including price feeds, oracle-like data, or conditions gating on-chain actions/fund movement), consuming silently stale data due to an unenforced per-request bound can produce incorrect workflow decisions — the same class of "the enforced bound is looser than what the caller asked for" impact flagged as high severity in the original report, applied here to the gateway's caching layer rather than a slippage parameter.

### Likelihood Explanation
The vector requires two or more concurrent `OutboundHTTPRequest`s to the same `method`+`URL`+headers+body+`workflowOwner` hash arriving before the first's `fetchFn` completes, with different `CacheSettings.MaxAgeMs` values (e.g. one lax, one `MaxAgeMs: 0`). This is plausible in CRE deployments where multiple workflows or workflow runs owned by the same owner independently call the same external endpoint with different caching preferences, or where a single workflow issues concurrent calls with intentionally different freshness settings (e.g. a "force refresh" retry racing a normal cached call). It is a timing-dependent race rather than a deterministic single-request bug, so likelihood is moderate rather than certain.

### Recommendation
Include the effective `MaxAgeMs` (or a normalized/bucketed cache-tolerance class, or simply always treat `MaxAgeMs: 0` as its own singleflight key/bypass path) as part of the `singleflight.Group` key so that a stricter caller can never be silently satisfied by a looser concurrent caller's fetch decision. Alternatively, always re-validate the joiner's own `cacheMaxAge` against the cached result after the flight resolves, and trigger a fresh fetch if the joiner's stricter bound is violated, rather than trusting the leader's cached-vs-fresh decision for all joiners.

### Proof of Concept
1. Configure `OutboundRequestCacheTTLMs` normally (e.g. 10 minutes) as in `newResponseCache` [5](#0-4) .
2. Have a cache entry already exist for a given `(method, URL, headers, body, workflowOwner)` that is, say, 5 seconds old.
3. Caller A issues `Fetch` with `CacheSettings.MaxAgeMs = 60000` (60s) — fast path hits, no flight entered, returns cached data (fine).
4. Simultaneously (before A's fast path completes, or in a scenario where the cache momentarily lacks an entry), Caller B issues `Fetch` with `CacheSettings.MaxAgeMs = 0` (explicitly requesting no cached data) for the identical `req.Hash()`. Because `req.Hash()` ignores `CacheSettings` [1](#0-0) , if B's fast path check misses and it joins the same `flight.Do(cacheKey, ...)` invocation already started by another concurrent caller with a lax `MaxAgeMs`, B is not guaranteed to trigger `fetchFn`; it can instead receive the shared result determined solely by the flight leader's `cacheMaxAge`, i.e., a stale cached response, despite explicitly requesting `MaxAgeMs: 0`.

Note: I was unable to directly inspect `core/services/gateway/handlers/capabilities/v2/http_handler.go`'s exact `makeOutgoingRequest` call site content in this session (only match counts were returned before the tool budget ran out), so the precise call-site wiring of `Fetch` (e.g., whether `CacheSettings` originates from workflow-controlled input reachable by an unprivileged workflow author) could not be fully confirmed from the index and should be verified directly in the repository.

### Citations

**File:** core/services/gateway/handlers/capabilities/v2/response_cache_test.go (L121-137)
```go
	t.Run("having different cacheSettings results in the same Hash", func(t *testing.T) {
		req1 := createTestRequest("GET", "https://example.com")
		req1.CacheSettings = gateway_common.CacheSettings{
			MaxAgeMs: 5000,
			Store:    true,
		}

		req2 := createTestRequest("GET", "https://example.com")
		req2.CacheSettings = gateway_common.CacheSettings{
			MaxAgeMs: 10000,
			Store:    false,
		}

		hash1 := req1.Hash()
		hash2 := req2.Hash()
		require.Equal(t, hash1, hash2, "Hash should be the same regardless of CacheSettings")
	})
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

**File:** core/services/gateway/handlers/capabilities/v2/response_cache.go (L66-77)
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
```

**File:** core/services/gateway/handlers/capabilities/v2/response_cache.go (L83-91)
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
```
