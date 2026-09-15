Audit Report

## Title
Unbounded growth of in-memory `activeRequests` map allows unprivileged-client memory exhaustion DoS - (File: core/services/gateway/handlers/confidentialrelay/handler.go)

## Summary
`HandleJSONRPCUserMessage` in the confidential relay gateway handler accepts any caller-supplied request ID (only validated for non-empty/≤200 chars) and unconditionally allocates a new `activeRequest` entry, keyed by that ID, with no authentication/authorization gate and no cap on the number of concurrently outstanding entries. Cleanup is purely time-based (a 1s ticker evicting entries older than `requestTimeout`, default 30s), so an unprivileged caller sending a sustained stream of uniquely-IDed requests can grow the map, each entry's per-node `responses` map, and the associated fan-out goroutines without bound, consuming gateway memory/goroutines.

## Finding Description
`HandleJSONRPCUserMessage` [1](#0-0)  validates only ID length, extracts logging labels, and immediately calls `h.newActiveRequest` followed by `h.fanOutToNodes` — there is no authorization, signature, or allowlist check comparable to what the sibling `vault` handler performs before creating its own `activeRequest` [2](#0-1) . The `handler` struct stores these in an unbounded `map[string]*activeRequest` guarded only by a mutex, with no size cap or per-sender quota [3](#0-2) . Each `activeRequest` carries its own `responses` map and mutex [4](#0-3) . Reclamation is entirely time-based, running once per second and only removing entries older than `requestTimeout` (default 30s) [5](#0-4) [6](#0-5) .

Checking the outer layers: the gateway HTTP server (`core/services/gateway/network/httpserver.go`) enforces a request *body size* limit via `MaxRequestBytesLimiter` [7](#0-6) , but no per-caller/global cap on the *number* of concurrent or per-second requests reaching `ProcessRequest`/`HandleJSONRPCUserMessage`. The only rate limiters present in this handler (`globalNodeRateLimiter`, `perNodeRateLimiters`) throttle node-originated messages via `HandleNodeMessage`, not the user-originated path that creates `activeRequest` entries [8](#0-7) . The `WebServer.RateLimit` config found in `core/config/docs/core.toml` applies to the node's separate web/API server (`core/web/router.go`), not the gateway's user JSON-RPC server, so it does not bound this attack surface.

## Impact Explanation
Sustained flooding with unique-ID `MethodCapabilityExec`/`MethodSecretsGet` requests grows `h.activeRequests` and per-request response maps for up to `requestTimeout` (30s default) per entry, and each request also spawns an `errgroup` fan-out to every DON member, multiplying goroutine/memory pressure. This can degrade or crash the gateway process serving legitimate workflow/vault traffic — an availability impact triggerable by any client able to reach the gateway's user JSON-RPC endpoint, with no authentication required for this handler's request path (unlike the `vault` handler, which enforces `ProcessRequest` authorization before creating its equivalent state).

## Likelihood Explanation
This is straightforward to trigger by any client with network access to the gateway's user-facing endpoint (no credentials or signed workflow authorization required, since `HandleJSONRPCUserMessage` in this handler performs no such check before allocating state). The reviewed outer layers (HTTP body-size limiter, node-message rate limiters) do not bound the number of distinct concurrent request IDs a caller can create, so the described unbounded growth is realistic under default configuration.

## Recommendation
Add an explicit cap on the number of concurrently outstanding `activeRequests` (globally and/or per sender/caller), reject or rate-limit new requests once the cap is reached, and/or shrink the cleanup interval relative to `requestTimeout` (or evict on an LRU/quota basis) so outstanding state cannot grow proportionally to attacker request rate. Consider adding a lightweight authentication/authorization or per-caller rate-limiting step to `HandleJSONRPCUserMessage` before creating an `activeRequest`, analogous to the `vault` handler's `ProcessRequest` authorization gate.

## Proof of Concept
An unprivileged client with network access to the gateway's user JSON-RPC endpoint (e.g., default port from `UserServerConfig`) repeatedly POSTs `MethodCapabilityExec` (or `MethodSecretsGet`) JSON-RPC requests, each with a fresh, valid (≤200-char) `req.ID`, at a rate exceeding what `removeExpiredRequests` reaps within `requestTimeout` (default 30s). Each request causes `HandleJSONRPCUserMessage` → `newActiveRequest` → `fanOutToNodes` to allocate and retain a new map entry (plus a fan-out goroutine group to every DON member) until expiry, driving unbounded growth of `h.activeRequests` and associated memory/goroutines — observable via process RSS growth and goroutine count under sustained load, without any authentication step blocking the requests.

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

**File:** core/services/gateway/handlers/confidentialrelay/handler.go (L337-356)
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

**File:** core/services/gateway/handlers/vault/handler.go (L422-438)
```go
	if !vaulttypes.IsGatewaySecretsMethod(req.Method) {
		return h.sendImmediateUserResponse(ctx, req, callback, api.UnsupportedMethodError, errors.New("this method is unsupported: "+req.Method))
	}

	_, cachedPublicKey := h.getCachedPublicKey()
	authorized, err := h.requestProcessor.ProcessRequest(ctx, &req, cachedPublicKey)
	if err != nil {
		if vaultcap.IsInvalidVaultParamsError(err) {
			return h.sendImmediateUserResponse(ctx, req, callback, api.InvalidParamsError, err)
		}
		h.lggr.Errorw("request not authorized", "method", req.Method, "requestID", req.ID, "hasAuth", req.Auth != "", "error", err)
		return errors.New("request not authorized: " + err.Error())
	}
	authorizedOwner := authorized.AuthResult.AuthorizedOwner()

	h.lggr.Debugw("handling authorized vault request", "method", req.Method, "requestID", req.ID, "authorizedOwner", authorizedOwner)
	ar, activeRequestErr := h.newActiveRequest(req, callback)
```

**File:** core/services/gateway/network/httpserver.go (L211-224)
```go
	maxRequestBytes, err := s.config.MaxRequestBytesLimiter.Limit(r.Context())
	if err != nil {
		msg := "Failed to get request size limit"
		s.lggr.Errorw(msg, "err", err)
		http.Error(w, msg, http.StatusInternalServerError)
		return
	}
	source := http.MaxBytesReader(nil, r.Body, int64(maxRequestBytes))
	rawMessage, err := io.ReadAll(source)
	if err != nil {
		s.lggr.Error("error reading request", err)
		w.WriteHeader(http.StatusBadRequest)
		return
	}
```
