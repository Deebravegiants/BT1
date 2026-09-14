## Title
Unbounded `activeRequests` map growth from unauthenticated gateway user requests enables memory-exhaustion DoS - ([File: core/services/gateway/handlers/confidentialrelay/handler.go])

### Summary
The confidential relay gateway handler's `HandleJSONRPCUserMessage` inserts every incoming user request into an in-memory map (`activeRequests`) keyed by the caller-supplied request ID, with no authentication, no per-caller rate limiting, and no cap on the map's size before insertion. This is structurally analogous to the reported bug class: an unbounded collection that grows in response to externally-controlled input and is only trimmed by a periodic sweep, allowing a low-privilege/unauthenticated actor to force resource exhaustion.

### Finding Description
`HandleJSONRPCUserMessage` only validates that `req.ID` is non-empty and ≤200 characters before calling `newActiveRequest`, which unconditionally locks the handler mutex and inserts the request into `h.activeRequests[req.ID]`: [1](#0-0) [2](#0-1) 

Unlike `HandleNodeMessage`, which is gated by `perNodeRateLimiters` and `globalNodeRateLimiter` before any state is touched, there is no equivalent limiter applied to `HandleJSONRPCUserMessage` in this handler, and no maximum size check on `h.activeRequests` (contrast with `core/services/gateway/handlers/common/requestcache.go`, which enforces `maxCacheSize` before inserting a new entry — `len(c.cache) >= int(c.maxCacheSize)` returns an error). The confidential relay handler has no analogous bound.

Entries are only removed by a periodic sweep, `removeExpiredRequests`/cleanup tied to `defaultCleanUpPeriod` (1 second) and `defaultRequestTimeoutSec` (30 seconds), or when a request completes: [3](#0-2) 

The top-level gateway dispatcher `gateway.ProcessRequest` performs no authentication before routing to the handler — it only checks message-format validity and request-ID length, then calls `h.HandleJSONRPCUserMessage` directly: [4](#0-3) 

This means any unauthenticated HTTP caller reaching the gateway's public endpoint can submit a stream of requests with unique IDs, each of which is durably held in memory (`activeRequest` struct with maps and locks) for up to ~30 seconds, faster than the once-per-second sweep can reclaim memory, causing the map to grow without bound and consuming increasing memory/CPU — the same failure mode as the reported unbounded linked-list DoS, but realized as an unbounded Go map keyed by attacker-controlled request IDs on the internet-facing gateway.

### Impact Explanation
An unauthenticated caller can exhaust gateway node memory by flooding it with distinct request IDs, each of which triggers `fanOutToNodes` (additional CPU/network work per request) and is retained in `activeRequests` until timeout. Sustained flooding faster than the reclaim rate leads to unbounded memory growth and can crash or degrade the gateway service, denying availability to legitimate DON users. This is consistent with the "cannot award/complete" DoS impact in the analog report, translated to gateway service availability.

### Likelihood Explanation
Likelihood is high for any deployment where the gateway's confidential relay endpoint is reachable without authentication/allowlisting prior to `HandleJSONRPCUserMessage`, since the only preconditions are a non-empty request ID ≤200 characters — trivial for any client to satisfy repeatedly with unique IDs. No special privilege is required.

### Recommendation
- Enforce a maximum size on `activeRequests` (mirroring `requestcache.maxCacheSize`) and reject new requests once the cap is reached, returning a clear error/backpressure to the caller.
- Add a per-caller and/or global rate limiter on `HandleJSONRPCUserMessage` (as already exists for `HandleNodeMessage`) before any map insertion or fan-out work occurs.
- Consider reducing the cleanup sweep interval or making cleanup proportional to load, and eagerly evict once size thresholds are exceeded rather than relying solely on time-based expiry.

### Proof of Concept
1. Reach the gateway's public HTTP endpoint for the confidential relay handler's DON/service without any authentication.
2. Repeatedly POST JSON-RPC requests with `method` = `MethodSecretsGet` or `MethodCapabilityExec` and a fresh, unique `id` value (any string ≤200 chars) on each request, at a rate exceeding one request per second (the cleanup sweep interval) sustained for the `defaultRequestTimeoutSec` (30s) window.
3. Each request passes the minimal validation in `HandleJSONRPCUserMessage` and is inserted into `h.activeRequests` via `newActiveRequest`, with no size cap, no authentication, and no per-caller rate limit.
4. Continue at a high rate; the map grows unbounded (bounded only by attacker's request rate), consuming increasing gateway memory and triggering fan-out work per request, degrading or exhausting the node before the periodic sweep can catch up.

### Citations

**File:** core/services/gateway/handlers/confidentialrelay/handler.go (L30-37)
```go
const (
	// defaultCleanUpPeriod is how often expired requests are swept and closed grace
	// windows are forwarded, so it also bounds how far past its deadline a grace
	// window can run.
	defaultCleanUpPeriod = time.Second

	defaultRequestTimeoutSec  = 30
	defaultNodeSendTimeoutSec = 10
```

**File:** core/services/gateway/handlers/confidentialrelay/handler.go (L394-412)
```go
func (h *handler) HandleJSONRPCUserMessage(ctx context.Context, req jsonrpc.Request[json.RawMessage], callback gwhandlers.Callback) error {
	if req.ID == "" {
		return errors.New("request ID cannot be empty")
	}
	if len(req.ID) > 200 {
		return errors.New("request ID is too long: " + strconv.Itoa(len(req.ID)) + ". max is 200 characters")
	}

	labels := h.extractRequestLabels(req)
	l := h.requestLogger(req, labels)
	l.Debugw("handling confidential relay request", "nodes", len(h.donConfig.Members), "f", h.donConfig.F)

	ar, err := h.newActiveRequest(req, labels, callback)
	if err != nil {
		return err
	}

	return h.fanOutToNodes(ctx, l, ar)
}
```

**File:** core/services/gateway/handlers/confidentialrelay/handler.go (L414-430)
```go
func (h *handler) newActiveRequest(req jsonrpc.Request[json.RawMessage], labels requestLabels, callback gwhandlers.Callback) (*activeRequest, error) {
	h.mu.Lock()
	defer h.mu.Unlock()
	if h.activeRequests[req.ID] != nil {
		h.lggr.Errorw("request id already exists", "requestID", req.ID, "executionID", labels.ExecutionID)
		return nil, errors.New("request ID already exists: " + req.ID)
	}
	ar := &activeRequest{
		Callback:  callback,
		req:       req,
		labels:    labels,
		createdAt: h.clock.Now(),
		responses: map[string]*jsonrpc.Response[json.RawMessage]{},
	}
	h.activeRequests[req.ID] = ar
	return ar, nil
}
```

**File:** core/services/gateway/gateway.go (L267-279)
```go
	startTime := time.Now()
	var method string
	callback := handlerscommon.NewCallback()
	if isLegacyRequest {
		method = msg.Body.Method
		err = h.HandleLegacyUserMessage(ctx, msg, callback)
	} else {
		method = jsonRequest.Method
		err = h.HandleJSONRPCUserMessage(ctx, jsonRequest, callback)
	}
	if err != nil {
		return newError(jsonRequest.ID, api.HandlerError, err.Error())
	}
```
