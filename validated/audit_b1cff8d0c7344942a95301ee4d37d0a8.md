## Analysis

The Mattermost CVE-2023-5330 bug class is: an attacker-reachable endpoint caches externally-fetched data (OpenGraph metadata) with no bound on the number of cache entries, only a TTL — allowing cache-key fanout to exhaust server memory.

The Chainlink gateway's HTTP capability handler has the same pattern in its outbound-response cache.

### Root cause

`responseCache` in `core/services/gateway/handlers/capabilities/v2/response_cache.go` is a plain `map[string]*cachedResponse` guarded by a mutex, with **no maximum entry count** — only a TTL and a periodic `DeleteExpired` sweep: [1](#0-0) 

`Set`/`Fetch` insert unconditionally into this map whenever a cacheable (2xx/4xx) response with `CacheSettings.Store=true` is produced, keyed by `req.Hash()` (method, URL, headers, body, workflow owner): [2](#0-1) 

This is invoked from `gatewayHandler.makeOutgoingRequest`, which is reached whenever any DON node forwards a `MethodHTTPAction` outbound request — the URL, headers, body, and `CacheSettings` all originate from the workflow itself (i.e., attacker/customer-controlled), not from the gateway operator: [3](#0-2) 

The only protections in this path are per-node and global **request-rate** limiters, not a cache-size bound: [4](#0-3) 

Compare this to the sibling `requestCache` type in `core/services/gateway/handlers/common/requestcache.go`, which explicitly tracks a `maxCacheSize` field — showing that a bounded design pattern already exists elsewhere in this codebase but was not applied to `responseCache`: [5](#0-4) 

### Title
Unbounded outbound-HTTP response cache in gateway `v2` HTTP capability handler enables memory-exhaustion DoS - (File: `core/services/gateway/handlers/capabilities/v2/response_cache.go`)

### Summary
The gateway's HTTP-action response cache (`responseCache`) stores one entry per unique `(method, URL, headers, body, workflowOwner)` hash with no cap on the number of entries, evicting only by TTL via a periodic 10-minute sweep. A workflow (reachable through any DON member forwarding `MethodHTTPAction` messages on the workflow's behalf) fully controls the URL/headers/body/`CacheSettings.Store` fields that determine the cache key and whether an entry is stored, so it can generate an effectively unbounded number of distinct cache keys within the TTL window, growing the in-memory map without limit — the same bug class as CVE-2023-5330 (unbounded OpenGraph cache filling memory until the server becomes unavailable).

### Finding Description
`newResponseCache` allocates a `map[string]*cachedResponse` with no size ceiling, and `Set`/`Fetch` insert into it unconditionally as long as the response status is cacheable and `CacheSettings.Store` is true. Because the cache key is `req.Hash()` over attacker-supplied `Method`, `URL`, `Headers`/`MultiHeaders`, and `Body`, a workflow can trivially mint new unique keys (e.g., varying a query parameter or body per call) to force new map entries rather than cache hits. Existing mitigations — per-node and global rate limiters in `HandleNodeMessage` — bound the *rate* of requests but not the *number of distinct cache keys accumulated*, and the periodic `DeleteExpired` cleanup only removes entries after the full TTL (default 10 minutes) elapses, so entries can accumulate freely during that window and every subsequent window if new unique keys keep arriving faster than they expire.

### Impact Explanation
Since the gateway process serves the whole DON×shard matrix, unbounded growth of this single in-process map can exhaust gateway memory, causing degraded performance or crashes that affect HTTP-action/trigger processing for all workflows and DON members served by that gateway instance — a denial-of-service condition analogous to the Mattermost advisory's "server unavailable" outcome.

### Likelihood Explanation
Reaching this code path requires only that a workflow issue outbound HTTP actions with `CacheSettings.Store=true` and varying request content, relayed by its own DON member node — no operator privilege, no malicious peer/node compromise, and no bypass of authentication is needed, since a normal workflow owner already has the ability to shape outbound HTTP action parameters. The existing rate limiters slow, but do not prevent, sustained accumulation of unique keys.

### Recommendation
Add an explicit maximum entry count (or maximum total cache byte size) to `responseCache`, evicting the oldest/least-recently-used entries (or rejecting new `Set` calls) once the limit is reached, mirroring the `maxCacheSize` bound already used in `core/services/gateway/handlers/common/requestcache.go`. Consider also bounding cache growth per workflow/owner in addition to a global cap.

### Proof of Concept
1. Register/operate a workflow that issues repeated `HTTPAction` outbound requests through its DON node to the gateway, each with `CacheSettings.Store=true` and `MaxAgeMs>0`, but a unique query string or body per call (e.g., appending an incrementing counter to the URL).
2. Each call resolves to a distinct `req.Hash()`, so `gatewayHandler.makeOutgoingRequest` → `responseCache.Set`/`Fetch` inserts a brand-new map entry every time — see `core/services/gateway/handlers/capabilities/v2/http_handler.go` lines 434-442 and `response_cache.go` lines 66-120.
3. Repeating this faster than the `CleanUpPeriodMs` TTL sweep (default 10 minutes, `defaultOutboundRequestCacheTTLMs`) causes the `responseCache.cache` map to grow unbounded, consuming gateway memory until the process degrades or is OOM-killed.

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

**File:** core/services/gateway/handlers/capabilities/v2/http_handler.go (L244-255)
```go
	nodeRateLimiter, ok := h.perNodeRateLimiters[nodeAddr]
	if !ok {
		return fmt.Errorf("received message from unexpected node %s", nodeAddr)
	}
	if !nodeRateLimiter.Allow(ctx) {
		h.metrics.IncrementCapabilityNodeThrottled(ctx, nodeAddr, h.lggr)
		return fmt.Errorf("rate limit exceeded for node %s", nodeAddr)
	}
	if !h.globalNodeRateLimiter.Allow(ctx) {
		h.metrics.IncrementGlobalThrottled(ctx, h.lggr)
		return errors.New("global rate limit exceeded")
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

**File:** core/services/gateway/handlers/common/requestcache.go (L27-31)
```go
type requestCache[T any] struct {
	cache        map[globalID]*pendingRequest[T]
	maxCacheSize uint32
	timeout      time.Duration
	mu           sync.Mutex
```
