## Analysis

I verified the core technical claims against the codebase:

- `responseCache` stores entries in a plain `map[string]*cachedResponse` with no capacity/size bound, and `DeleteExpired` only removes entries by TTL, never by count or aggregate size. [1](#0-0) [2](#0-1) 
- The cache is populated in `makeOutgoingRequest` whenever `CacheSettings.Store` is true or `MaxAgeMs>0`, keyed by `req.Hash()`. [3](#0-2) 
- The only mitigations are per-node/global rate limiting (default `PerSenderRPS: 100`, `GlobalRPS: 500`) and a per-response byte cap (`MaxResponseBytes: 50_000_000` by default), neither of which bounds aggregate cache memory over the TTL window (default 10 minutes). [4](#0-3) [5](#0-4) 
- By contrast, the sibling cache `requestCache` in `handlers/common/requestcache.go` enforces an explicit `maxCacheSize` and rejects new entries once full, confirming this safeguard is a known, applied pattern in this codebase that is absent from `responseCache`. [6](#0-5) 
- Requests reaching `makeOutgoingRequest` originate from `HandleNodeMessage`, i.e., from DON/capability nodes forwarding workflow-defined HTTP Actions — not directly from an arbitrary internet client — but the request content (URL, headers, body, cache settings) is attacker-influenceable through the workflow definition itself, which a workflow owner controls. [7](#0-6) 

The code fully supports the claim as written: there is no cap on the number of entries or aggregate memory used by `responseCache`, and a workflow that issues many uniquely-keyed cacheable HTTP Action requests with `Store=true` against large-body endpoints can accumulate memory bounded only by `(rate limit) × TTL × MaxResponseBytes`, which at default settings is very large (500 rps × 600s × 50MB, subject to real bandwidth/target-serving constraints).

Audit Report

## Title
Unbounded in-memory HTTP response cache in Gateway HTTP Action handler enables memory-exhaustion DoS - (File: core/services/gateway/handlers/capabilities/v2/response_cache.go)

## Summary
`responseCache` in the Gateway's HTTP Handlers V2 caches outbound HTTP Action responses in a Go map keyed by `req.Hash()` with no maximum entry count or byte-size bound; entries are reclaimed only via time-based (TTL) expiry through a periodic sweep, not memory pressure. A workflow that issues sustained, uniquely-keyed HTTP Action requests with `CacheSettings.Store=true` (or `MaxAgeMs>0`) against endpoints returning large cacheable bodies can grow the cache unboundedly within the TTL window, risking gateway process OOM/denial of service.

## Finding Description
`responseCache.cache` is a `map[string]*cachedResponse` guarded only by a mutex, with no capacity limit at construction (`newResponseCache`) or insertion (`Set`/`Fetch`). The sole cleanup mechanism, `DeleteExpired`, iterates the map and deletes entries strictly by `storedAt.Add(rc.ttl)` comparison against `time.Now()`, never evicting based on entry count or total size. `makeOutgoingRequest` populates the cache from every outbound HTTP Action forwarded by a workflow node when `CacheSettings.Store` is true or `MaxAgeMs>0`, using `req.Hash()` (method/URL/headers/body/workflow scope) as the key — meaning varying any of those fields per call produces a new, independently-cached entry. The only existing safeguards are per-node/global rate limiters (bounding request *rate*, not distinct-key *count*) and `MaxResponseBytes` (bounding per-entry size, not aggregate cache size). This is an explicit contrast to the sibling `requestCache` in `handlers/common/requestcache.go`, which enforces `maxCacheSize` and rejects insertion once full — a safeguard pattern known to the codebase but not applied here.

## Impact Explanation
Uncontrolled growth of `responseCache` can exhaust Gateway process memory, causing crashes/OOM that disrupt HTTP Action processing for all DONs and workflows served by that Gateway instance — a classic CWE-400 resource-exhaustion/availability impact. Severity is bounded by real-world constraints: the attacker (workflow owner) must actually drive that much distinct, sustained traffic and have external endpoints capable of serving large response bodies repeatedly, and the rate limiter still throttles velocity. This is an availability/DoS concern on the Gateway service rather than a confidentiality/integrity/authorization bypass.

## Likelihood Explanation
Any workflow owner able to define an HTTP Action node with `CacheSettings.Store=true` (or `MaxAgeMs>0`) and vary the request per call (query params/headers/body) can grow the cache — no elevated/administrative privilege beyond ordinary workflow-authoring capability is required. However, exploitation requires sustained traffic near the configured rate limit for a duration comparable to the TTL (default 10 minutes) against endpoints returning large bodies, which is a real but moderately costly attack to sustain in practice, and is throttled somewhat by the existing per-sender/global rate limiters.

## Recommendation
Add a hard cap on `responseCache` (max entry count and/or max aggregate byte size), evicting oldest/least-recently-used entries when the limit is reached, mirroring the `maxCacheSize` enforcement already present in `handlers/common/requestcache.go`. Consider tracking cumulative cached bytes (not just per-response `MaxResponseBytes`) and enforcing a ceiling, using the already-collected `metrics.RecordCacheSize` as the basis for an enforced limit rather than pure observability.

## Proof of Concept
1. Deploy a workflow whose HTTP Action node sets `CacheSettings.Store = true` and targets an attacker-controlled endpoint that returns large (near `MaxResponseBytes`) 2xx bodies.
2. Vary a request parameter (query string/header/body) on each invocation so `req.Hash()` produces a new cache key per call.
3. Sustain calls at a rate within the per-node/global rate limiter's allowance for a duration approaching the configured `OutboundRequestCacheTTLMs` (default 600000ms).
4. Observe Gateway process memory grow roughly proportional to `(sustained rate) × TTL × response size`, since `DeleteExpired` only reclaims memory after TTL expiry and enforces no ceiling during accumulation.

### Citations

**File:** core/services/gateway/handlers/capabilities/v2/response_cache.go (L15-38)
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

**File:** core/services/gateway/handlers/capabilities/v2/http_handler.go (L239-256)
```go
func (h *gatewayHandler) HandleNodeMessage(ctx context.Context, resp *jsonrpc.Response[json.RawMessage], nodeAddr string) error {
	if resp.ID == "" {
		return fmt.Errorf("received response with empty request ID from node %s", nodeAddr)
	}
	h.lggr.Debugw("handling incoming node message", "requestID", resp.ID, "nodeAddr", nodeAddr)
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
	// Node messages follow the format "<methodName>/<workflowID>/<uuid>" or
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

**File:** deployment/cre/jobs/pkg/gateway_job.go (L185-189)
```go
	httpCfg := httpClientConfig{
		MaxResponseBytes: 50_000_000,
		AllowedPorts:     []int{443},
		AllowedSchemes:   []string{"https"},
	}
```

**File:** deployment/cre/jobs/pkg/gateway_job.go (L474-488)
```go
func newDefaultHTTPCapabilitiesHandler() handler {
	return handler{
		Name:        GatewayHandlerTypeHTTPCapabilities,
		ServiceName: ServiceNameWorkflows,
		Config: httpCapabilitiesHandlerConfig{
			CleanUpPeriodMs: 10 * 60 * 1000, // 10 minutes
			NodeRateLimiter: nodeRateLimiterConfig{
				GlobalBurst:    100,
				GlobalRPS:      500,
				PerSenderBurst: 100,
				PerSenderRPS:   100,
			},
		},
	}
}
```

**File:** core/services/gateway/handlers/common/requestcache.go (L60-66)
```go
	_, ok := c.cache[key]
	if ok {
		return errors.New("request already exists")
	}
	if len(c.cache) >= int(c.maxCacheSize) {
		return errors.New("request cache is full")
	}
```
