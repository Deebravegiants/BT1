## Analysis Result [1](#0-0) 

### Title
Unbounded, unauthenticated pending-request map growth causes gateway DoS - (File: `core/services/gateway/handlers/confidentialrelay/handler.go`)

### Summary
The Confidential Relay gateway handler's `HandleJSONRPCUserMessage`, which is the entry point for arbitrary external (unauthenticated) HTTP callers hitting the internet-facing Gateway, accepts every request with a unique ID and unconditionally inserts it into the in-memory `activeRequests` map before any authorization, allowlist check, or per-caller rate limiting is applied. This mirrors the CVE-2022-42314 bug class: a low-privilege/unauthenticated peer can force unbounded server-side memory allocation by issuing many requests that are buffered/held pending completion, faster than the cleanup routine can reclaim them.

### Finding Description
`gateway.ProcessRequest` [2](#0-1)  decodes any raw JSON-RPC payload from an HTTP client and routes it via `HandleJSONRPCUserMessage` to the resolved handler — this is the client-facing entry point that the vault handler treats as needing authorization/allowlisting before doing real work, see `h.requestProcessor.ProcessRequest` gating `newActiveRequest` in the vault handler [3](#0-2) .

In contrast, `confidentialrelay/handler.go`'s `HandleJSONRPCUserMessage` performs only an ID-length check, then immediately calls `newActiveRequest` and fans the request out to every DON member — with no authorization, no allowlist check, and no per-caller/global rate limiter on the *incoming user* path: [4](#0-3) 

`newActiveRequest` only rejects a request if the exact same string ID already exists — it enforces no cap on the total number of concurrently pending requests, unlike `common.requestCache`, which explicitly caps size via `maxCacheSize`: [5](#0-4) 

The `globalNodeRateLimiter` and `perNodeRateLimiters` fields that do exist in this handler only gate *node responses* coming back in `HandleNodeMessage`, not the initial user-submitted request that allocates the map entry: [6](#0-5) 

Each accepted request survives in memory (map entry + `sync.Mutex` + `responses` map + fan-out goroutines via `errgroup.Group`) until `requestTimeout` elapses (default 30s, configurable) and the 1-second cleanup ticker sweeps it: [7](#0-6) [8](#0-7) 

Since a caller only needs a unique `req.ID` (≤200 chars) per request, and there is no cap on the number of simultaneously pending IDs, an attacker can submit requests faster than the timeout window drains them, growing `h.activeRequests` and its associated goroutines without bound.

### Impact Explanation
An unauthenticated/unprivileged external client of the internet-facing Gateway can exhaust gateway process memory (and goroutines) by sustained flooding of unique-ID confidential-relay requests, causing denial of service to the Gateway component that also serves legitimate DON traffic (vault, capabilities, etc., which share the same `gatewayConnector`/HTTP server process). This matches the CVE's "unprivileged peer forces unbounded allocation" class exactly, applied to the equivalent unpriv-actor surface in this codebase (gateway request handling), rather than to xenstored.

### Likelihood Explanation
High for a networked attacker with basic HTTP access to the Gateway's public endpoint: no authentication token, allowlist membership, or per-caller quota is required to reach `HandleJSONRPCUserMessage` for the confidential relay methods (`MethodSecretsGet`, `MethodCapabilityExec`); only a unique request ID and valid JSON-RPC envelope shape are needed.

### Recommendation
Add a bound on the number of concurrently pending `activeRequests` (mirroring `common.requestCache`'s `maxCacheSize`), and/or apply a per-caller/global inbound rate limiter to `HandleJSONRPCUserMessage` before `newActiveRequest` is called, similar to how the vault handler gates real work behind `requestProcessor.ProcessRequest` authorization.

### Proof of Concept
1. From an unauthenticated client, repeatedly POST JSON-RPC requests to the Gateway's confidential-relay-configured DON/service endpoint with method `secretsGet` or `capabilityExec`, each with a freshly generated unique `id` (up to 200 chars).
2. Send requests at a rate exceeding `1/RequestTimeoutSec` per outstanding slot (e.g., hundreds/sec against a 30s timeout).
3. Observe `activeRequests` map size and goroutine count (via `errgroup.Group` fan-out per request) growing unbounded on the Gateway process, eventually leading to memory exhaustion / process instability, since no request-count cap or inbound rate limit exists to reject excess pending requests. [9](#0-8)

### Citations

**File:** core/services/gateway/handlers/confidentialrelay/handler.go (L236-261)
```go
func NewHandler(methodConfig json.RawMessage, donConfig *config.DONConfig, don gwhandlers.DON, lggr logger.Logger, clock clockwork.Clock, limitsFactory limits.Factory) (*handler, error) {
	var cfg Config
	if err := json.Unmarshal(methodConfig, &cfg); err != nil {
		return nil, fmt.Errorf("failed to unmarshal method config: %w", err)
	}

	if cfg.RequestTimeoutSec == 0 {
		cfg.RequestTimeoutSec = defaultRequestTimeoutSec
	}

	if cfg.NodeSendTimeoutSec == 0 {
		cfg.NodeSendTimeoutSec = defaultNodeSendTimeoutSec
	}
	if cfg.NodeSendTimeoutSec > cfg.RequestTimeoutSec {
		cfg.NodeSendTimeoutSec = cfg.RequestTimeoutSec
	}

	switch {
	case cfg.QuorumGraceMillis == 0:
		cfg.QuorumGraceMillis = defaultQuorumGraceMillis
	case cfg.QuorumGraceMillis < 0:
		cfg.QuorumGraceMillis = 0
	}
	if maxGraceMillis := cfg.RequestTimeoutSec * 1000; cfg.QuorumGraceMillis > maxGraceMillis {
		cfg.QuorumGraceMillis = maxGraceMillis
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

**File:** core/services/gateway/handlers/confidentialrelay/handler.go (L438-453)
```go
func (h *handler) HandleNodeMessage(ctx context.Context, resp *jsonrpc.Response[json.RawMessage], nodeAddr string) error {
	l := logger.With(h.lggr, "method", resp.Method, "requestID", resp.ID, "nodeAddr", nodeAddr)
	l.Debugw("handling node response")

	nodeRateLimiter, ok := h.perNodeRateLimiters[nodeAddr]
	if !ok {
		return fmt.Errorf("received message from unexpected node %s", nodeAddr)
	}
	if !nodeRateLimiter.Allow(ctx) {
		l.Debugw("node is rate limited", "nodeAddr", nodeAddr)
		return nil
	}
	if !h.globalNodeRateLimiter.Allow(ctx) {
		l.Debug("global relay rate limit exceeded")
		return nil
	}
```

**File:** core/services/gateway/gateway.go (L220-280)
```go
// Called by the server
func (g *gateway) ProcessRequest(ctx context.Context, rawRequest []byte, auth string) (rawResponse []byte, httpStatusCode int) {
	// decode
	jsonRequest, err := jsonrpc2.DecodeRequest[json.RawMessage](rawRequest, auth)
	if err != nil {
		return newError("", api.UserMessageParseError, err.Error())
	}
	msg, err := g.codec.DecodeJSONRequest(jsonRequest)
	if err != nil {
		return newError(jsonRequest.ID, api.UserMessageParseError, err.Error())
	}
	if len(jsonRequest.ID) > 200 {
		// Arbitrary limit to prevent abuse
		return newError(jsonRequest.ID, api.UserMessageParseError, "request ID is too long: "+strconv.Itoa(len(jsonRequest.ID))+". max is 200 characters")
	}
	isLegacyRequest := false
	var h handlers.Handler
	var handlerKey string
	if msg == nil || msg.Body.DonID == "" {
		serviceName := jsonRequest.ServiceName()
		if handler, ok := g.serviceToMultiHandler[serviceName]; ok {
			h = handler
			handlerKey = serviceName
		} else if donID, ok := g.serviceNameToDonID[serviceName]; ok {
			// Fallback to legacy service name -> DON ID mapping
			if handler, ok := g.handlers[donID]; ok {
				h = handler
				handlerKey = donID
			}
		}
		if h == nil {
			return newError(jsonRequest.ID, api.HandlerError, "Service name not found: "+serviceName)
		}
	} else {
		// Legacy request with DON ID - validate and fetch handler
		isLegacyRequest = true
		if err = msg.Validate(); err != nil {
			return newError(jsonRequest.ID, api.UserMessageParseError, err.Error())
		}
		handlerKey = msg.Body.DonID
		var ok bool
		h, ok = g.handlers[handlerKey]
		if !ok {
			return newError(jsonRequest.ID, api.UnsupportedDONIdError, "Unsupported DON ID: "+handlerKey)
		}
	}

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

**File:** core/services/gateway/handlers/vault/handler.go (L422-441)
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
	if activeRequestErr != nil {
		return activeRequestErr
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
