## Analog Vulnerability Found

The `frxETHMinter.depositEther` bug class — an unbounded loop whose cost grows with the accumulated size of a state collection that is fed by an untrusted caller, with no cap on that collection's growth — has a direct analog in the Chainlink Gateway's `confidentialrelay` handler.

### Title
Unbounded growth of `activeRequests` map in `ConfidentialRelayHandler` enables DoS via periodic full-map sweep - ([File: core/services/gateway/handlers/confidentialrelay/handler.go])

### Summary
`handler.HandleJSONRPCUserMessage` is the entry point the gateway's `ProcessRequest` calls for every unauthenticated/unprivileged client request routed to the confidential relay DON handler. Each call inserts an entry into `h.activeRequests`, a `map[string]*activeRequest`, with the only guard being a duplicate-ID check — there is no maximum size enforced anywhere. A background goroutine sweeps the entire map every second (`defaultCleanUpPeriod = time.Second`) to find expired or graced requests, iterating every entry currently held.

### Finding Description
`gateway.ProcessRequest` decodes an inbound client request and dispatches it via `h.HandleJSONRPCUserMessage(ctx, jsonRequest, callback)` [1](#0-0) . For the confidential relay handler, this calls `newActiveRequest`, which only rejects a request if its ID is already present — it never checks or bounds the total map size: [2](#0-1) 

By contrast, the sibling `common.RequestCache` type used elsewhere in the gateway explicitly enforces a `maxCacheSize` and rejects new requests once full [3](#0-2) . The confidential relay handler has no equivalent bound.

The cleanup goroutine started in `Start` ticks every second and calls both `forwardGracedRequests` and `removeExpiredRequests`, each of which iterates the *entire* `activeRequests` map under `h.mu.RLock()`: [4](#0-3) [5](#0-4) [6](#0-5) 

Entries are only removed from the map when `sendResponseAndClearRequest` runs, which happens on completion, expiry (after `requestTimeoutSec`, default 30s), or grace-window elapse. As long as an attacker submits new requests (each requiring only a unique, ≤200-char ID — no rate limiter or size cap gates this insertion path) faster than the 30-second timeout retires old ones, `activeRequests` grows without bound, and the per-second sweep cost grows linearly with it — exactly the "loop cost scales with accumulated, attacker-controlled state" pattern in the reference report, except here the resource exhausted is gateway CPU/goroutine time and memory rather than gas.

### Impact Explanation
An unprivileged client sending a sustained flood of distinct-ID relay requests (`MethodSecretsGet`/`MethodCapabilityExec`) can grow `activeRequests` unbounded. This:
- Increases memory usage per pending request (holds the full request, per-node response map, and callback).
- Makes every 1-second cleanup tick progressively more expensive as it linearly scans the whole map while holding `h.mu.RLock()`, contending with the write lock taken by `newActiveRequest`/`sendResponseAndClearRequest` for every other concurrent request.
- Can degrade or stall the gateway's handling of legitimate relay requests, impairing availability of the confidential relay / vault-secrets service exposed to workflow clients — the same "impaired functionality and availability" impact that justified Medium severity in the reference finding.

This does not directly cause fund loss, so it aligns with a Medium-severity availability/DoS finding, consistent with the judge's reasoning in the reference report.

### Likelihood Explanation
`HandleJSONRPCUserMessage` is reachable directly from `gateway.ProcessRequest`, the gateway's public request-processing entry point, with the only per-request cost gates being a 200-character ID length check and (for node responses only, not for the initial client submission) per-node/global rate limiters. Nothing throttles the rate or count of *new* client-submitted requests before they are inserted into `activeRequests`, so likelihood of triggering is high for any client able to reach the gateway HTTP endpoint for a DON configured with this handler.

### Recommendation
Add an explicit maximum size to `activeRequests` (mirroring `common.RequestCache`'s `maxCacheSize`) and reject/rate-limit new requests once the cap is reached in `newActiveRequest`. Additionally, consider applying a rate limiter to inbound client requests (not just node responses) before creating an `activeRequest` entry, and/or bounding sweep cost (e.g., sharding or using a timer-indexed structure instead of a full linear scan) so cleanup cost does not scale linearly with total outstanding requests.

### Proof of Concept
1. Configure a DON with the `confidentialrelay` handler and default settings (`requestTimeoutSec=30`, cleanup tick=1s).
2. From an unprivileged client, repeatedly POST JSON-RPC requests to the gateway with unique `ID` values for `MethodCapabilityExec`/`MethodSecretsGet`, faster than nodes can respond/timeout (e.g., thousands per second).
3. Observe `activeRequests` grow unbounded (no rejection occurs besides duplicate-ID checks) and the 1-second `removeExpiredRequests`/`forwardGracedRequests` sweep taking progressively longer while holding `h.mu`, delaying processing of concurrent legitimate requests until the flood stops or the process runs out of memory.

### Citations

**File:** core/services/gateway/gateway.go (L267-276)
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
```

**File:** core/services/gateway/handlers/confidentialrelay/handler.go (L300-320)
```go
func (h *handler) Start(_ context.Context) error {
	return h.StartOnce("ConfidentialRelayHandler", func() error {
		h.lggr.Info("starting confidential relay handler")
		go func() {
			ctx, cancel := h.stopCh.NewCtx()
			defer cancel()
			ticker := h.clock.NewTicker(defaultCleanUpPeriod)
			defer ticker.Stop()
			for {
				select {
				case <-ticker.Chan():
					h.forwardGracedRequests(ctx)
					h.removeExpiredRequests(ctx)
				case <-h.stopCh:
					return
				}
			}
		}()
		return nil
	})
}
```

**File:** core/services/gateway/handlers/confidentialrelay/handler.go (L337-346)
```go
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

**File:** core/services/gateway/handlers/confidentialrelay/handler.go (L605-614)
```go
func (h *handler) forwardGracedRequests(ctx context.Context) {
	h.mu.RLock()
	var graced []*activeRequest
	now := h.clock.Now()
	for _, ar := range h.activeRequests {
		if ar.graceElapsed(now) {
			graced = append(graced, ar)
		}
	}
	h.mu.RUnlock()
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
