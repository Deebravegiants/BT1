### Title
Unbounded `activeRequests` map growth in the Gateway Vault handler's unauthenticated `PublicKeyGet` path enables a persistent memory-exhaustion DoS - (File: core/services/gateway/handlers/vault/handler.go)

### Summary
The Gateway's vault handler creates one `activeRequest` entry per incoming JSON-RPC user request keyed only by `req.ID`, with no cap on the total number of concurrently pending entries. For the `MethodPublicKeyGet` method, the handler explicitly skips authorization ("Public key requests don't require authorization") whenever the public key is not currently cached, meaning any unauthenticated caller reaching the gateway's HTTP endpoint can create arbitrarily many of these entries, each of which persists in memory until a periodic reaper (`removeExpiredRequests`, default every 5s per `defaultCleanUpPeriod`) expires it after `requestTimeout`.

### Finding Description
`HandleJSONRPCUserMessage` [1](#0-0)  takes the `MethodPublicKeyGet` fast-path when the cached public key is empty and calls `h.newActiveRequest(req, callback)` without going through `h.requestProcessor.ProcessRequest` (the authorization step used for all other vault methods, see lines 422-434). `newActiveRequest` only rejects a request if the exact same `req.ID` is already present in the map; it performs no check against any maximum size of `h.activeRequests`: [2](#0-1) 

Because request IDs are attacker-supplied and only bounded in length (200 chars, checked at line 398-401), an attacker can generate an unbounded number of unique IDs and flood the gateway's public HTTP endpoint (`gateway.ProcessRequest` → `HandleJSONRPCUserMessage`) with `PublicKeyGet` requests. Each request allocates a new `activeRequest` struct (holding the raw request, a `responses` map, a callback, and timestamps) that is inserted into the shared `h.activeRequests` map and is not released until either a node quorum responds or the periodic reaper removes it after `requestTimeout` elapses: [3](#0-2) 

The reaper runs on a fixed interval (`defaultCleanUpPeriod = 5 * time.Second`) [4](#0-3) , so an attacker sending requests faster than the reaper drains them (trivial over a high-throughput connection) can grow the map unbounded between reaper passes, and can sustain that growth indefinitely by maintaining request rate above the expiry/cleanup rate. This mirrors the bitswap CVE pattern: unauthenticated/untrusted requests are queued into an in-memory structure with allocations that persist independent of whether the request is legitimate, and the only bound is a time-based reaper rather than a size-based admission control.

### Impact Explanation
An unauthenticated remote attacker (any client able to reach the gateway's user-facing HTTP endpoint) can cause the gateway node process to accumulate unbounded heap memory via repeated `PublicKeyGet` requests, leading to OOM / process crash / degraded service for legitimate users and other DON member nodes relying on gateway availability. Because the fast-path bypasses `requestProcessor.ProcessRequest`, no signature, auth header, or workflow ownership is required to trigger allocation.

### Likelihood Explanation
Likelihood is high whenever the public key cache is empty (e.g., freshly-started gateway, or after `defaultPublicKeyGetCacheDurationSeconds` (300s) expiry window before a fresh fetch completes, or if `h.getCachedPublicKey()` transiently returns nil for other reasons) — the attacker only needs unique JSON-RPC IDs (trivial to generate) and a `POST` to the gateway's exposed endpoint. Once the cache is populated the fast synchronous path (`handlePublicKeyGetSynchronously`) is used instead, so the exposure window is time-bound to cache-miss periods, but is still reachable and repeatable by an attacker who can force cache misses or who races the startup window.

### Recommendation
Add a hard cap on the size of `h.activeRequests` (similar to `RequestCache`'s `maxCacheSize` pattern seen elsewhere in the gateway, e.g. `core/services/gateway/handlers/common/requestcache.go`) and reject/rate-limit new entries once the cap is reached, particularly for the unauthenticated `PublicKeyGet` path. Consider requiring at least basic per-IP/per-connection request throttling before allocating an `activeRequest` for methods that bypass `requestProcessor.ProcessRequest`.

### Proof of Concept
1. Start a gateway node with an empty/expired vault public-key cache.
2. From an unauthenticated client, repeatedly POST JSON-RPC requests to the gateway's user HTTP endpoint with `method: vaulttypes.MethodPublicKeyGet` and a fresh unique `id` on each request, at a rate higher than the 5-second reaper interval can drain (`defaultCleanUpPeriod`).
3. Observe `h.activeRequests` map size (via memory profiling / heap dump) grow without bound as long as the attacker sustains send rate, since each request bypasses `requestProcessor.ProcessRequest` and is admitted into the map with no size check in `newActiveRequest`.

### Citations

**File:** core/services/gateway/handlers/vault/handler.go (L43-46)
```go
const (
	defaultCleanUpPeriod                    = 5 * time.Second
	defaultPublicKeyGetCacheDurationSeconds = 300
)
```

**File:** core/services/gateway/handlers/vault/handler.go (L360-384)
```go
// removeExpiredRequests removes expired requests from the pending requests map
func (h *handler) removeExpiredRequests(ctx context.Context) {
	h.mu.RLock()
	var expiredRequests []*activeRequest
	now := h.clock.Now()
	for _, userRequest := range h.activeRequests {
		if now.Sub(userRequest.createdAt) > h.requestTimeout {
			expiredRequests = append(expiredRequests, userRequest)
		}
	}
	h.mu.RUnlock()

	for _, er := range expiredRequests {
		responses := er.copiedResponses()
		var nodeResponses strings.Builder
		for nodeKey, nodeResponse := range responses {
			_, _ = fmt.Fprintf(&nodeResponses, "%s ---::: %v               ", nodeKey, nodeResponse)
		}
		nodeResponsesStr := nodeResponses.String()
		err := h.sendResponse(ctx, er, h.errorResponse(er.req, api.RequestTimeoutError, errors.New("request expired without getting quorum of responses from nodes. Available responses: "+nodeResponsesStr), []byte(nodeResponsesStr)))
		if err != nil {
			h.lggr.Errorw("error sending response to user", "requestID", er.req.ID, "error", err)
		}
	}
}
```

**File:** core/services/gateway/handlers/vault/handler.go (L394-420)
```go
func (h *handler) HandleJSONRPCUserMessage(ctx context.Context, req jsonrpc.Request[json.RawMessage], callback gwhandlers.Callback) error {
	if req.ID == "" {
		return errors.New("request ID cannot be empty")
	}
	if len(req.ID) > 200 {
		// Arbitrary limit to prevent abuse
		return errors.New("request ID is too long: " + strconv.Itoa(len(req.ID)) + ". max is 200 characters")
	}

	h.lggr.Debugw("handling vault request", "method", req.Method, "requestID", req.ID, "request", req)
	if req.Method == vaulttypes.MethodPublicKeyGet {
		// Public key requests don't require authorization,
		// Let's process this request right away.
		// Note we cache this value quite aggressively so don't need to worry about DoS.
		publicKeyResponseBytes, cachedPublicKey := h.getCachedPublicKey()
		if cachedPublicKey == nil {
			// Not found in cache. Fetch from nodes.
			ar, err := h.newActiveRequest(req, callback)
			if err != nil {
				h.lggr.Errorw("failed to create new activeRequest", "error", err)
				return err
			}
			return h.handlePublicKeyGet(ctx, ar)
		}
		h.lggr.Debugw("returning cached public key response")
		return h.handlePublicKeyGetSynchronously(ctx, req, publicKeyResponseBytes, callback)
	}
```

**File:** core/services/gateway/handlers/vault/handler.go (L457-472)
```go
func (h *handler) newActiveRequest(req jsonrpc.Request[json.RawMessage], callback gwhandlers.Callback) (*activeRequest, error) {
	h.mu.Lock()
	defer h.mu.Unlock()
	if h.activeRequests[req.ID] != nil {
		h.lggr.Errorw("request id already exists", "requestID", req.ID)
		return nil, errors.New("request ID already exists: " + req.ID)
	}
	ar := &activeRequest{
		Callback:  callback,
		req:       req,
		createdAt: h.clock.Now(),
		responses: map[string]*jsonrpc.Response[json.RawMessage]{},
	}
	h.activeRequests[req.ID] = ar
	return ar, nil
}
```
