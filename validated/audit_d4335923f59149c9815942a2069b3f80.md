### Title
Unauthenticated, unbounded `activeRequests` map growth in the Gateway's Confidential Relay and Vault handlers enables remote memory-exhaustion DoS - ([File: core/services/gateway/handlers/confidentialrelay/handler.go])

### Summary
The Gateway's internet-facing HTTP endpoint accepts JSON-RPC user messages with no authentication requirement at the transport layer and dispatches them straight into per-DON handlers. Two of these handlers — `confidentialrelay` and `vault` — insert one entry per inbound request into an in-memory `map[string]*activeRequest` keyed by the caller-supplied `req.ID`, with **no maximum size limit**. Entries are only removed by a periodic sweep (every 1s/5s) that expires requests older than a fixed timeout (default 30s). An unauthenticated caller can therefore create an unbounded number of live map entries within any timeout window simply by sending JSON-RPC requests with unique IDs faster than the sweep can reclaim them, exhausting gateway node memory — the same "unbounded per-request resource retained until a slow time-based sweep" bug class as the Lodestar libp2p leak cited in the report.

### Finding Description
The gateway's HTTP listener reads the raw body (bounded only by `MaxRequestBytesLimiter`) and passes it straight to `gateway.ProcessRequest`, with no session/API-key/allowlist check performed before the message reaches a handler: [1](#0-0) [2](#0-1) 

For the confidential relay handler, `HandleJSONRPCUserMessage` performs only an ID-length check and then unconditionally calls `newActiveRequest`, which inserts into `h.activeRequests` — there is no authentication, authorization, or size cap applied before the map grows: [3](#0-2) 

The map is declared with no capacity/eviction bound: [4](#0-3) 

The only reclamation mechanism is a ticker-driven sweep that removes entries whose `createdAt` exceeds `requestTimeout` (default 30s), running once per second: [5](#0-4) [6](#0-5) 

The Vault handler has the identical pattern: an unbounded `activeRequests map[string]*activeRequest`, and for `vaulttypes.MethodPublicKeyGet` (explicitly documented as not requiring authorization) a new entry is created on every cache-miss request before any auth check occurs: [7](#0-6) [8](#0-7) 

Notably, the codebase already contains the correct pattern elsewhere — `handlers/common/requestcache.go`'s `RequestCache` explicitly enforces a `maxCacheSize` and rejects new entries once full: [9](#0-8) 

This shows the size-bound safeguard was a deliberate, known mitigation that was simply not applied to the `confidentialrelay` and `vault` handlers' own `activeRequests` maps.

### Impact Explanation
Any unauthenticated internet client that can reach the Gateway's user-facing HTTP port can flood either handler with JSON-RPC requests using unique `ID` values (up to the 200-character limit). Each request allocates an `activeRequest` struct (holding the request, a responses map, a mutex, timers/labels) that persists for up to `requestTimeout` (30s default) regardless of whether the DON ever answers, and each also triggers a fan-out send to every node in the DON, amplifying the attack. Sustained flooding at a rate exceeding the sweep's reclamation rate drives unbounded heap growth on the Gateway process, eventually causing an out-of-memory crash — taking the entire Gateway (and by extension all DONs/services it fronts, including Vault secrets access) offline, with no automatic recovery until the process is restarted. This mirrors the "High" severity Lodestar finding: a memory leak reachable from an unprivileged, unauthenticated network client that crashes the node process.

### Likelihood Explanation
High. No authentication, allowlist check, or per-caller rate limit gates entry into `newActiveRequest` for either handler (the `vault` handler's node-side `nodeRateLimiter` only throttles responses from DON *nodes*, not user-submitted requests; the `confidentialrelay` handler has no request-admission rate limiting at all on `HandleJSONRPCUserMessage`). The only cost to the attacker is generating unique string IDs and sending HTTP POSTs, which is trivial to script at high volume from a single machine, exactly as described in the analog report's reproduction steps.

### Recommendation
Apply the same bounded-cache discipline already used in `handlers/common/requestcache.go` to the `confidentialrelay` and `vault` handlers: enforce a `maxActiveRequests` limit in `newActiveRequest`, rejecting/erroring new requests once the map is full, and/or require authentication/rate limiting to gate admission before an entry is created. Consider also lowering the cleanup interval relative to `requestTimeout` or using a size-aware eviction policy so admission is throttled proactively rather than relying solely on time-based expiry.

### Proof of Concept
1. Stand up (or target) a Gateway node exposing the user HTTP port with a configured Confidential Relay or Vault DON.
2. Script a flood of HTTP POST requests to the gateway's JSON-RPC endpoint, each with a fresh UUID as `id` and method `confidentialrelay.secrets_get` (or `vault.publicKeyGet`), sent with no credentials.
3. Sustain request submission at a rate exceeding the cleanup sweep's reclamation (e.g., thousands/sec from a small number of threads).
4. Observe the Gateway process's heap/RSS grow unbounded as `activeRequests` accumulates faster than `removeExpiredRequests`/`removeExpiredRequests`-equivalent sweeps can clear entries, eventually leading to OOM termination of the Gateway process.

### Citations

**File:** core/services/gateway/network/httpserver.go (L211-234)
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

	// Optionally extract jwt token from authorization header
	authHeader := r.Header.Get("Authorization")
	jwtToken := ""
	if authHeader != "" {
		jwtToken = strings.TrimPrefix(authHeader, "Bearer ")
	}

	startTime := time.Now()
	rawResponse, httpStatusCode := s.handler.ProcessRequest(r.Context(), rawMessage, jwtToken)
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

**File:** core/services/gateway/handlers/vault/handler.go (L404-420)
```go
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
