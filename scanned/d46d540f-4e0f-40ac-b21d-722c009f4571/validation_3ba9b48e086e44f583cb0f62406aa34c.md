### Title
Unbounded per-request state accumulation in the Confidential Relay Gateway handler enables memory exhaustion from unprivileged HTTP callers - (File: core/services/gateway/handlers/confidentialrelay/handler.go)

### Summary
The Gateway's Confidential Relay handler accepts user-originated JSON-RPC requests (`SecretsGet` / `CapabilityExec`) over the internet-facing HTTP gateway and, for every accepted request, allocates a long-lived `*activeRequest` tracked in an in-memory map (`h.activeRequests`). No admission-time cap on the number of concurrently tracked requests was found in the code reviewed; the only rate limiters present (`globalNodeRateLimiter`, `perNodeRateLimiters`) bound fan-out sends to DON member nodes, not acceptance of the initial user request. This mirrors the CL-2026-05 bug class (mplex): an attacker who can reach a single logical inbound channel repeatedly triggers server-side per-request resource allocation (there, goroutines-per-stream; here, map entries/contexts/mutexes-per-request) with no backpressure, causing unbounded memory growth until each entry's timeout (`RequestTimeoutSec`, default 30s) expires.

### Finding Description
`NewHandler` initializes `activeRequests: make(map[string]*activeRequest)` with no fixed capacity or admission gate [1](#0-0) . `HandleJSONRPCUserMessage` is the entrypoint invoked directly for user (unprivileged, HTTP client) requests routed through the Gateway's `ProcessRequest` dispatch [2](#0-1) ; it only validates the request ID length before proceeding [3](#0-2) . Each accepted request creates an `activeRequest` struct (containing a mutex, a responses map, and callback state) that is only removed by the periodic cleanup goroutine after `requestTimeout` elapses (`removeExpiredRequests`, run every `defaultCleanUpPeriod` = 1s but gated on `now.Sub(createdAt) > h.requestTimeout`, i.e., up to 30s of retention per request) [4](#0-3) . The only rate limiting present (`globalNodeRateLimiter`, `perNodeRateLimiters`) is applied to the downstream fan-out toward DON nodes, not to whether a new `activeRequest` is admitted into the map [5](#0-4) .

This is structurally analogous to CL-2026-05: mplex spawned an unbounded goroutine per multiplexed stream without capping the number of concurrently outstanding streams/goroutines, letting a single peer exhaust memory. Here, the Gateway's HTTP entrypoint spawns an unbounded, time-bounded-but-uncapped-in-count `activeRequest` allocation per accepted JSON-RPC request, with the request's identity fully controlled by the caller (`req.ID`, capped only at 200 chars) and no visible cap on total concurrent entries.

Note: I was only able to review `HandleJSONRPCUserMessage` through line ~400; I could not confirm within the reviewed context whether a later portion of the function (beyond what was fetched) enforces an admission-level concurrency cap on `h.activeRequests` before insertion. This uncertainty should be resolved by inspecting the remainder of `HandleJSONRPCUserMessage` and any call to `h.globalNodeRateLimiter`/size checks against `h.activeRequests` prior to insertion.

### Impact Explanation
If no admission control exists (as the reviewed code suggests), an unauthenticated or low-privilege actor with HTTP access to the Gateway's public endpoint can flood it with distinct-ID `SecretsGet`/`CapabilityExec` requests faster than the 30-second expiry sweep can reclaim them, growing `h.activeRequests` without bound and exhausting Gateway process memory — a High-severity availability impact on the Gateway component, consistent with the reported bug's severity and reward tier.

### Likelihood Explanation
Likelihood is moderate-to-high if confirmed: the entrypoint is reachable from any client able to send Gateway HTTP JSON-RPC requests (no special authorization beyond a valid, unique request ID under 200 chars), and generating unique IDs to bypass in-flight-dedup protections (as seen in related dedup logic elsewhere in the codebase) is trivial for an attacker.

### Recommendation
Add an explicit bound on the number of concurrently tracked `activeRequest` entries in `h.activeRequests` (e.g., a semaphore/limiter consulted in `HandleJSONRPCUserMessage` before allocation, rejecting or queuing beyond a configured maximum), independent of the existing node-fan-out rate limiters. Consider also shortening `defaultCleanUpPeriod`/`RequestTimeoutSec` bounds or adding per-caller quotas if caller identity is available at the Gateway layer.

### Proof of Concept
1. From an unprivileged HTTP client, send a rapid burst of JSON-RPC requests to the Gateway's public endpoint targeting `confidentialrelay.MethodSecretsGet` (or `MethodCapabilityExec`), each with a unique `id` field (e.g., UUIDs), faster than the DON can respond and faster than the 30s default expiry.
2. Observe that each request causes `HandleJSONRPCUserMessage` to insert a new `*activeRequest` into `h.activeRequests` without any admission-time rejection based on total in-flight count.
3. Continue the flood; measure Gateway process memory growth proportional to the number of outstanding unique request IDs, independent of the downstream `globalNodeRateLimiter`/`perNodeRateLimiters` which only throttle sends to DON nodes, not acceptance into the map.

### Citations

**File:** core/services/gateway/handlers/confidentialrelay/handler.go (L263-275)
```go
	globalNodeRateLimiter, err := limitsFactory.MakeRateLimiter(cresettings.Default.GatewayConfidentialRelayGlobalRate)
	if err != nil {
		return nil, fmt.Errorf("failed to create global node rate limiter: %w", err)
	}

	perNodeRateLimiters := make(map[string]limits.RateLimiter, len(donConfig.Members))
	for _, member := range donConfig.Members {
		rl, makeErr := limitsFactory.MakeRateLimiter(cresettings.Default.GatewayConfidentialRelayPerNodeRate)
		if makeErr != nil {
			return nil, fmt.Errorf("failed to create per-node rate limiter for %s: %w", member.Address, makeErr)
		}
		perNodeRateLimiters[member.Address] = rl
	}
```

**File:** core/services/gateway/handlers/confidentialrelay/handler.go (L282-297)
```go
	return &handler{
		donConfig:             donConfig,
		don:                   don,
		lggr:                  logger.Named(lggr, "ConfidentialRelayHandler:"+donConfig.DonID),
		requestTimeout:        time.Duration(cfg.RequestTimeoutSec) * time.Second,
		nodeSendTimeout:       time.Duration(cfg.NodeSendTimeoutSec) * time.Second,
		quorumGrace:           time.Duration(cfg.QuorumGraceMillis) * time.Millisecond,
		globalNodeRateLimiter: globalNodeRateLimiter,
		perNodeRateLimiters:   perNodeRateLimiters,
		activeRequests:        make(map[string]*activeRequest),
		mu:                    sync.RWMutex{},
		stopCh:                make(services.StopChan),
		metrics:               metrics,
		bundler:               &bundler{},
		clock:                 clock,
	}, nil
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

**File:** core/services/gateway/handlers/confidentialrelay/handler.go (L394-400)
```go
func (h *handler) HandleJSONRPCUserMessage(ctx context.Context, req jsonrpc.Request[json.RawMessage], callback gwhandlers.Callback) error {
	if req.ID == "" {
		return errors.New("request ID cannot be empty")
	}
	if len(req.ID) > 200 {
		return errors.New("request ID is too long: " + strconv.Itoa(len(req.ID)) + ". max is 200 characters")
	}
```

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
