## Analog Found

### Title
Unauthenticated attacker can exhaust the gateway's Confidential Relay `activeRequests` queue, causing an O(n) DoS on request processing - (File: `core/services/gateway/handlers/confidentialrelay/handler.go`)

### Summary
The Casimir report describes an unbounded, unmetered FIFO queue (`requestUnstake`) that any caller can grow for free, combined with O(n) queue processing (`remove()`), which lets an attacker inflate the queue until legitimate queue processing (`fulfillUnstake()`) exceeds resource limits. The Chainlink gateway's Confidential Relay handler has the same structural pattern in `HandleJSONRPCUserMessage`: every inbound JSON-RPC user request is admitted into an in-memory map with no admission control, and background loops walk that entire map on every tick.

### Finding Description
`handler.HandleJSONRPCUserMessage` in `core/services/gateway/handlers/confidentialrelay/handler.go` accepts any JSON-RPC request whose `req.ID` is non-empty and ≤200 chars, then unconditionally calls `h.newActiveRequest` and fans it out to every DON member, with **no authentication, no authorization, and no per-sender or global rate limiter on the ingress path**: [1](#0-0) 

`newActiveRequest` inserts unconditionally into `h.activeRequests`, a plain `map[string]*activeRequest` with **no maximum size / capacity check**, unlike the sibling `common.requestCache`, which enforces a `maxCacheSize` and rejects new entries once full: [2](#0-1) [3](#0-2) 

The only rate limiters present (`globalNodeRateLimiter`, `perNodeRateLimiters`) guard `HandleNodeMessage` (responses coming back from DON nodes), not the inbound user request path: [4](#0-3) 

Every request that is admitted stays in `activeRequests` for up to `requestTimeout` (default 30s) and is swept by two background loops that run every second (`defaultCleanUpPeriod = time.Second`) and **linearly scan the entire map**: [5](#0-4) [6](#0-5) [7](#0-6) 

This is structurally identical to the reported bug class: an unprivileged caller can add entries to a shared queue/map at effectively no cost (`requestUnstake()` accepting any amount, including 0, vs. this handler accepting any `req.ID` with no auth/rate limit), and the periodic maintenance work over that structure is O(n) per tick (`remove()` vs. `removeExpiredRequests`/`forwardGracedRequests`), so growing the structure directly increases per-tick CPU cost and each fan-out additionally amplifies work by sending to every DON member (`fanOutToNodes`/`SendToNode`), multiplying attacker cost-to-impact.

### Impact Explanation
An attacker with no credentials can flood the gateway's public HTTP ingress (`gateway.ProcessRequest` → `HandleJSONRPCUserMessage`) with unique `req.ID` values targeting `MethodSecretsGet`/`MethodCapabilityExec`. Each request:
- allocates an `activeRequest` struct and a map entry that lives for up to 30 seconds,
- triggers a full fan-out `SendToNode` call to every relay DON member,
- is picked up by two O(n) sweep loops running every second.

Because there is no bound on `len(h.activeRequests)` and no per-sender/global ingress rate limiting, an attacker can drive the map size, per-tick scan cost, and node fan-out volume arbitrarily high, degrading the gateway's ability to process legitimate confidential-relay/vault requests (memory growth, goroutine/lock contention under `h.mu`, and increased load on the relay DON nodes). This matches the report's core impact: legitimate processing becomes prohibitively expensive or gets denied due to attacker-inflated queue size.

### Likelihood Explanation
High. The entry point is the internet-facing gateway HTTP endpoint, requires no authentication, and no code path rejects requests once a size threshold is hit — this is a pure availability/gas(analog: CPU/memory)-cost asymmetry, not a hard-to-reach edge case. The `common.requestCache` used elsewhere in the same package demonstrates the team is aware of and normally applies a `maxCacheSize` guard; its absence here is the concrete divergence enabling this analog.

### Recommendation
- Add a maximum size to `h.activeRequests` (mirroring `common.requestCache.maxCacheSize`) and reject new requests once the limit is reached, returning a `LimitExceededError`/`ErrLimitExceeded` to the caller.
- Add a per-sender and/or global rate limiter on the `HandleJSONRPCUserMessage` ingress path in `core/services/gateway/handlers/confidentialrelay/handler.go`, similar to `userRateLimiter` already used in `core/services/gateway/handlers/capabilities/v2/http_trigger_handler.go`.
- Consider bounding `removeExpiredRequests`/`forwardGracedRequests` sweep cost independent of map growth (e.g., time-ordered eviction structure) so a large backlog cannot inflate per-tick scan latency.

### Proof of Concept
1. Stand up (or point at) a gateway configured with the Confidential Relay handler for a DON.
2. Send repeated HTTP requests to the gateway's public endpoint with JSON-RPC method `confidentialrelay_secretsGet` (or `capabilityExec`), each with a freshly generated unique `id`, no valid `Auth`, and arbitrary/garbage `params` (label extraction failure is only logged at debug and does not block admission — see `extractRequestLabels`).
3. Because `HandleJSONRPCUserMessage` performs no admission control before `newActiveRequest`, each request is added to `h.activeRequests` and fanned out to every DON member via `SendToNode`.
4. Repeat rapidly (e.g., thousands of requests per second) faster than the 1-second/`requestTimeout`-second cleanup cadence can drain them; observe unbounded growth of `len(h.activeRequests)`, increasing per-tick CPU time in `removeExpiredRequests`/`forwardGracedRequests`, and amplified outbound traffic to DON nodes — degrading service for legitimate vault/confidential-relay users. [8](#0-7)

### Citations

**File:** core/services/gateway/handlers/confidentialrelay/handler.go (L205-226)
```go
type handler struct {
	services.StateMachine
	donConfig *config.DONConfig
	don       gwhandlers.DON
	codec     api.JSONRPCCodec
	lggr      logger.Logger
	mu        sync.RWMutex
	stopCh    services.StopChan

	globalNodeRateLimiter limits.RateLimiter
	perNodeRateLimiters   map[string]limits.RateLimiter
	requestTimeout        time.Duration
	nodeSendTimeout       time.Duration
	quorumGrace           time.Duration

	activeRequests map[string]*activeRequest
	metrics        *metrics

	bundler relayBundler

	clock clockwork.Clock
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

**File:** core/services/gateway/handlers/confidentialrelay/handler.go (L337-369)
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

	for _, er := range expiredRequests {
		responses := er.copiedResponses()
		l := h.requestLogger(er.req, er.labels)
		l.Debugw("request expired, evaluating collected relay responses",
			"collected", len(responses),
			"nodes", len(h.donConfig.Members),
			"unanswered", len(h.donConfig.Members)-len(responses),
		)
		summary, err := h.bundler.Bundle(er.req, responses, l)
		if err != nil {
			l.Errorw("failed to build relay response bundle", "error", err)
			if sendErr := h.sendResponseAndClearRequest(ctx, er, h.constructErrorResponse(er.req, api.FatalError, err)); sendErr != nil {
				l.Errorw("error returning bundle failure on expiry", "error", sendErr)
			}
			continue
		}
		// Expiry makes further responses unavailable to this request. The common
		// readiness path forwards a viable partial bundle or returns a timeout.
		if err := h.forwardBundleOrTerminateIfReady(ctx, l, er, summary, 0, true); err != nil {
			l.Errorw("error forwarding bundle on expiry", "error", err)
		}
	}
```

**File:** core/services/gateway/handlers/confidentialrelay/handler.go (L394-430)
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

**File:** core/services/gateway/handlers/confidentialrelay/handler.go (L605-619)
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

	for _, ar := range graced {
		h.forwardAfterGrace(ctx, ar)
	}
}
```

**File:** core/services/gateway/handlers/common/requestcache.go (L50-66)
```go
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
