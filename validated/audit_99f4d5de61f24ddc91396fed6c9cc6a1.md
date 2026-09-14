### Title
Unbounded growth of in-memory `activeRequests` map allows unprivileged-client memory exhaustion DoS - (File: core/services/gateway/handlers/confidentialrelay/handler.go)

### Summary
The Xen advisory describes a Denial-of-Service class where an unprivileged party (a guest) forces the trusted component (`xenstored`) to accumulate unbounded state in memory — by issuing many requests without reading responses, or creating many outstanding transactions/nodes faster than they are cleaned up — until the process runs out of memory. The `ConfidentialRelayHandler` in the Chainlink gateway exhibits the same bug class: every JSON-RPC user request opens a new in-memory `activeRequest` entry that is only reclaimed on a slow, time-based sweep, with no limit on the number of concurrently outstanding requests an unprivileged caller can create.

### Finding Description
`HandleJSONRPCUserMessage` accepts a JSON-RPC request from an external caller, validates only that `req.ID` is non-empty and ≤200 characters, then unconditionally creates a new `activeRequest` and stores it, keyed by the caller-supplied ID: [1](#0-0) 

The `handler` struct holds these in an unbounded map protected only by a mutex, with no maximum-size cap and no per-caller quota: [2](#0-1) 

Each `activeRequest` itself buffers a `responses` map (one entry per DON node) that grows as node replies arrive, plus its own mutex/state: [3](#0-2) 

Cleanup is entirely time-based: a ticker fires once per second and removes entries only once they exceed `requestTimeout` (defaulting to 30 seconds), which is calculated by scanning the whole map: [4](#0-3) [5](#0-4) 

The only rate limiters present (`globalNodeRateLimiter`, `perNodeRateLimiters`) throttle *node-originated* messages arriving via `HandleNodeMessage`, not the *user-originated* request path that creates new `activeRequest` entries: [6](#0-5) 

Because request IDs are caller-supplied and there is no cap on distinct concurrent IDs, an unprivileged client can submit a high rate of uniquely-IDed `MethodCapabilityExec`/`MethodSecretsGet` requests, each allocating a new map entry, mutex, and per-node response map, and each triggering a fan-out goroutine group to every DON member. Because eviction only happens once per second and only for entries older than the (up to 30s) timeout, the number of live entries an attacker can force into memory scales with `attack_rate × requestTimeout`, unbounded by anything else in this handler — directly analogous to Xenstore accumulating unbounded per-guest state before it is reaped.

### Impact Explanation
Sustained flooding of the gateway's user-facing endpoint with unique-ID confidential-relay requests can grow `h.activeRequests` and the per-request response maps without bound for the duration of `requestTimeout`, consuming gateway memory and goroutines (one `errgroup` fan-out per request to every DON member) and degrading or crashing the gateway process serving legitimate workflow/vault traffic — a Denial of Service triggerable by any unprivileged caller able to reach the gateway's user JSON-RPC endpoint.

### Likelihood Explanation
Likelihood is dependent on external rate limiting outside this handler (e.g., HTTP-layer/message-size/global request-rate limits configured elsewhere in the gateway) that were not confirmed to bound the number of *distinct* concurrent request IDs; nothing in this handler itself prevents the described accumulation, so if the outer layer does not enforce a strict per-caller concurrency cap, the condition is straightforward to trigger.

### Recommendation
Add an explicit cap on the number of concurrently outstanding `activeRequests` (globally and/or per caller/sender), reject or rate-limit new requests once the cap is reached, and/or shrink the cleanup interval relative to `requestTimeout` so that outstanding state cannot grow proportionally to an attacker's request rate.

### Proof of Concept
An unprivileged client with access to the gateway's user JSON-RPC endpoint repeatedly sends `MethodCapabilityExec` (or `MethodSecretsGet`) requests, each with a fresh, valid (≤200-char) `req.ID`, at a rate exceeding what `removeExpiredRequests` can reap within `requestTimeout` (default 30s). Each request causes `HandleJSONRPCUserMessage` → `newActiveRequest` → `fanOutToNodes` to allocate and retain a new map entry until expiry, so sustained flooding drives unbounded growth of `h.activeRequests` and associated goroutines/memory.

### Citations

**File:** core/services/gateway/handlers/confidentialrelay/handler.go (L110-126)
```go
type activeRequest struct {
	req       jsonrpc.Request[json.RawMessage]
	labels    requestLabels
	responses map[string]*jsonrpc.Response[json.RawMessage]
	mu        sync.Mutex
	completed atomic.Bool

	// graceStarted is set the first time the request holds F+1 signed responses, so
	// the grace deadline is armed once per request rather than moved forward by every
	// later response. graceDeadline is guarded by mu and is only meaningful once
	// graceStarted is set.
	graceStarted  atomic.Bool
	graceDeadline time.Time

	createdAt time.Time
	gwhandlers.Callback
}
```

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

**File:** core/services/gateway/handlers/confidentialrelay/handler.go (L337-370)
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
}
```

**File:** core/services/gateway/handlers/confidentialrelay/handler.go (L394-411)
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
```
