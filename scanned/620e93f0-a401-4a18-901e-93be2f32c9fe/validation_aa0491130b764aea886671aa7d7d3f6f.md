Based on my investigation, I found a structurally analogous unbounded-cache-growth pattern in the gateway's HTTP capability response cache, though I could not fully trace the upstream authorization gating on the request path within my remaining tool budget — I note that uncertainty explicitly below.

### Title
Unbounded server-side response cache growth in gateway HTTP capability handler enables memory-exhaustion DoS - (File: core/services/gateway/handlers/capabilities/v2/response_cache.go)

### Summary
The gateway's `responseCache` stores every distinct outbound HTTP request/response pair in an in-memory map keyed by a hash of request attributes, with no maximum size bound — entries are removed only by a time-based sweep (`DeleteExpired`), never by a capacity limit. This mirrors the Vert.x SNI `SslContext` cache bug class (CWE-770/CWE-295 analog): a `computeIfAbsent`-style insertion pattern (`cache[key] = &cachedResponse{...}`) with cardinality controlled by the requester and no eviction other than TTL expiry.

### Finding Description
`responseCache` is defined with a plain Go map protected by a mutex, with no capacity ceiling: [1](#0-0) 

Both the `Fetch` fast/slow paths and `Set` insert new entries keyed by `req.Hash()` (built from method, URL, headers, body, and workflow owner per the type's doc comment) whenever the response is a cacheable status code, without checking or enforcing any maximum cache size: [2](#0-1) 

The only cache-shrinking mechanism is `DeleteExpired`, a TTL-based sweep that must be invoked externally on some schedule: [3](#0-2) 

This is the same defect shape as the Vert.x report: entries accumulate keyed by an externally-influenceable value (here, request method/URL/headers/body rather than SNI hostname), with growth bounded only by a periodic time-based cleanup rather than a hard capacity limit. If a caller can drive many cache-distinct outbound HTTP requests (e.g., varying URL query strings, headers, or body) faster than the TTL sweep interval reclaims them, the map grows without bound.

### Impact Explanation
Unbounded growth of `rc.cache` consumes gateway node memory proportional to the number of distinct requests seen within a TTL window, which can degrade or crash the gateway process — a resource-exhaustion/availability impact (CWE-770), matching the original advisory's `A:L` impact with no confidentiality/integrity effect.

### Likelihood Explanation
I could not confirm from the code I retrieved how `newResponseCache`/`Fetch`/`Set` are invoked from `http_handler.go` — specifically whether the HTTP capability path that generates cache keys is reachable pre-authorization by an unprivileged/unauthenticated caller, what workflow-owner scoping (if any) limits cardinality, and how frequently `DeleteExpired` is scheduled. This materially affects whether the practical likelihood is high (unauthenticated/broad reachability) or low (gated behind authenticated, rate-limited workflow execution). This is a genuine gap in my analysis, not a dismissal of the finding.

### Recommendation
Bound `responseCache` with a hard maximum entry count (evicting oldest/LRU entries on insert when full) in addition to the existing TTL-based `DeleteExpired` sweep, and verify/enforce that cache-key cardinality is scoped per authenticated workflow owner with a quota, so a single caller cannot unilaterally grow the shared cache. Confirm the invocation path and scheduling of `DeleteExpired` in `http_handler.go` to ensure sweeps run frequently enough to bound worst-case memory under load, and consider adding cache-size metrics/alerts as an operational safeguard (a `RecordCacheSize` metric already exists and could be used to detect unbounded growth in production).

### Proof of Concept
Conceptual reproduction (unverified end-to-end due to missing caller-side authorization details):
1. Trigger the gateway's HTTP capability outbound-request path repeatedly with distinct URL/header/body combinations that all yield a cacheable status code (2xx/4xx).
2. Each distinct combination produces a distinct `req.Hash()`, causing `Set`/`Fetch` to add a new entry to `rc.cache`.
3. Repeat faster than the configured TTL/sweep interval to accumulate entries without bound, growing gateway process memory until resource exhaustion.

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

**File:** core/services/gateway/handlers/capabilities/v2/response_cache.go (L93-120)
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
