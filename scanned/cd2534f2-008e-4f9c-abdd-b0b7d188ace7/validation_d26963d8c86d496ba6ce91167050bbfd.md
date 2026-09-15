### Title
Unauthenticated per-request map growth in the Vault gateway handler enables memory-exhaustion DoS - (File: core/services/gateway/handlers/vault/handler.go)

### Summary
The Vault gateway handler accepts `PublicKeyGet` requests from any unauthenticated, unprivileged client and unconditionally inserts a new entry into a shared in-memory map (`h.activeRequests`) keyed by the caller-supplied `req.ID`, with cleanup happening only on a periodic timer (`defaultCleanUpPeriod = 5s`) once `requestTimeout` (default 30s) has elapsed. This mirrors the CVE-2021-42219 bug class (uncontrolled resource consumption from a flood of attacker-controlled messages) in a Chainlink-specific, internet-facing entry point.

### Finding Description
`HandleJSONRPCUserMessage` is the gateway's public entry point for vault requests [1](#0-0) . For `vaulttypes.MethodPublicKeyGet`, the code explicitly documents that "Public key requests don't require authorization" and, when the public key is not cached, calls `h.newActiveRequest(req, callback)` before any authentication or per-user rate limiting is applied [2](#0-1) .

`newActiveRequest` takes a lock and inserts a new `*activeRequest` struct into the shared `h.activeRequests` map keyed by the caller-supplied `req.ID`, rejecting only exact ID collisions [3](#0-2) . The only validation performed on `req.ID` before this point is a length check (≤200 chars) and non-emptiness [4](#0-3) ; there is no limit on the number of distinct IDs, and no per-caller/global rate limiter guards this unauthenticated path (the only rate limiter present, `h.nodeRateLimiter`, governs node *responses*, not user requests, per `HandleNodeMessage`) [5](#0-4) .

Entries are only removed by `removeExpiredRequests`, which runs on a fixed timer (every `defaultCleanUpPeriod = 5s`) and evicts entries only once they are older than `h.requestTimeout` (default 30s) [6](#0-5) [7](#0-6) . An unauthenticated client that sends a high volume of `PublicKeyGet` requests, each with a unique `req.ID`, can therefore accumulate a large number of live map entries (each holding the request, a `responses` map, and a callback) for up to the full `requestTimeout` window before cleanup runs, unbounded by any admission control.

### Impact Explanation
Because the vulnerable code path is reachable without authorization ("Public key requests don't require authorization" per the code's own comment) [8](#0-7) , any unprivileged client of the gateway can drive sustained memory/goroutine-adjacent growth in the gateway process shared across the whole DON's vault-request handling, potentially degrading or crashing the gateway node and disrupting legitimate vault operations (secrets create/update/delete/list) for all workflows relying on that gateway.

### Likelihood Explanation
Likelihood is High for triggering the condition (no auth or rate limit stands in the way of the `PublicKeyGet` branch) but the resulting resource growth is bounded by the fixed 30s timeout window and 5s sweep cadence, so the practical severity depends on achievable request throughput versus the sweep interval — a sustained, moderate request rate is sufficient to keep the map perpetually large.

### Recommendation
Apply a per-caller and/or global rate limiter (similar to `nodeRateLimiter`) to unauthenticated `PublicKeyGet` requests before calling `newActiveRequest`, and/or cap the maximum size of `h.activeRequests` (evicting oldest entries when exceeded, as already done for `savedCallbacks` in the capabilities handler's `pruneCallbacks`) [9](#0-8) , so unauthenticated traffic cannot cause unbounded map growth ahead of the periodic cleanup.

### Proof of Concept
1. As an unauthenticated client, send a flood of JSON-RPC requests to the gateway's Vault handler with `method: "vault.PublicKeyGet"`, each with a unique `id` (e.g., UUID), faster than the 5-second cleanup cadence and within the 30-second `requestTimeout` window.
2. Because `req.Method == vaulttypes.MethodPublicKeyGet` bypasses `requestProcessor.ProcessRequest` authorization entirely (see the early branch in `HandleJSONRPCUserMessage`), every request with a cache miss reaches `newActiveRequest` and inserts a new map entry unconditionally.
3. Observe growth of `h.activeRequests` (and associated goroutines/response buffers) in the gateway process memory proportional to the flood rate, until `removeExpiredRequests` eventually sweeps entries older than `requestTimeout`.

Note: I was unable to fully confirm from the indexed code whether an outer, gateway-wide HTTP/connector-level rate limiter or body-size cap applies to inbound user JSON-RPC messages before they reach `HandleJSONRPCUserMessage` (the `HandleUserMessage`/connector dispatch layer was not found in the indexed portion of `core/services/gateway/`), so this could mitigate real-world exploitability — I recommend verifying this via a Devin session with full file access if precise confirmation is needed.

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

**File:** core/services/gateway/handlers/vault/handler.go (L480-487)
```go
func (h *handler) HandleNodeMessage(ctx context.Context, resp *jsonrpc.Response[json.RawMessage], nodeAddr string) error {
	l := logger.With(h.lggr, "method", resp.Method, "requestID", resp.ID, "nodeAddr", nodeAddr)
	l.Debugw("handling node response")

	if !h.nodeRateLimiter.Allow(nodeAddr) {
		l.Debugw("node is rate limited", "nodeAddr", nodeAddr)
		return nil
	}
```

**File:** core/services/gateway/handlers/capabilities/handler_test.go (L518-539)
```go
	t.Run("enforces max size by evicting oldest", func(t *testing.T) {
		// maxSize=2: trims to maxSize/2=1, so only the newest entry survives
		handler.config.MaxSavedCallbacks = 2

		handler.mu.Lock()
		handler.savedCallbacks = make(map[string]*savedCallback)
		now := time.Now()
		handler.savedCallbacks["a"] = &savedCallback{id: "a", createdAt: now.Add(-3 * time.Second)}
		handler.savedCallbacks["b"] = &savedCallback{id: "b", createdAt: now.Add(-2 * time.Second)}
		handler.savedCallbacks["c"] = &savedCallback{id: "c", createdAt: now.Add(-1 * time.Second)}
		handler.savedCallbacks["d"] = &savedCallback{id: "d", createdAt: now}
		handler.mu.Unlock()

		handler.pruneCallbacks()

		handler.mu.Lock()
		require.Len(t, handler.savedCallbacks, 1)
		require.Contains(t, handler.savedCallbacks, "d")
		handler.mu.Unlock()

		handler.config.MaxSavedCallbacks = defaultMaxSavedCallbacks
	})
```
