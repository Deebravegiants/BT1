Audit Report

## Title
Unauthenticated caller can cause unbounded per-request memory growth in the Confidential Relay gateway handler - ([File: core/services/gateway/handlers/confidentialrelay/handler.go])

## Summary
The Confidential Relay gateway handler's `HandleJSONRPCUserMessage` accepts JSON-RPC requests routed by service name with no authentication, authorization, or per-caller rate limiting, and inserts a tracked `activeRequest` entry into an unbounded `map[string]*activeRequest` keyed solely by the caller-supplied `req.ID`. An unauthenticated network client can flood the endpoint with unique IDs faster than the once-per-second expiry sweep can reclaim them, growing gateway memory without bound and additionally fanning out an RPC to every DON member per request.

## Finding Description
`gateway.ProcessRequest` routes any request without `msg.Body.DonID` set purely by JSON-RPC `ServiceName()` lookup into `g.serviceToMultiHandler`, calling `HandleJSONRPCUserMessage` directly — the `msg.Validate()` signature-check path only runs for legacy DON-ID requests: [1](#0-0) 

`HandleJSONRPCUserMessage` in the confidential relay handler performs only trivial ID-length validation before creating a new `activeRequest` and fanning it out to all DON nodes — there is no authentication, authorization, or per-sender/global limiter on this ingress path: [2](#0-1) 

Each accepted request is unconditionally inserted into `h.activeRequests`, keyed only by attacker-controlled `req.ID`, with no size cap: [3](#0-2) 

The only rate limiters the handler constructs (`globalNodeRateLimiter`, `perNodeRateLimiters`) are wired to throttle *node* responses coming back from the DON in `HandleNodeMessage`, not incoming user requests: [4](#0-3)  The handler struct itself carries no incoming-user rate limiter field: [5](#0-4) 

Entries are reclaimed only by a periodic sweep, once per second, that removes requests older than `requestTimeout` (default 30s): [6](#0-5) [7](#0-6) 

By contrast, the sibling HTTP Capabilities v2 handler requires JWT authentication and dual (global + per-sender) user-facing rate limiting before dispatching to nodes, demonstrating that this protection pattern exists elsewhere in the gateway but is absent here: [8](#0-7) [9](#0-8) 

The gateway's HTTP server config (`UserServerConfig`) only bounds request body size (`MaxRequestBytes`) and connection timeouts — it provides no per-caller request-rate limiting, so nothing at the transport layer compensates for the missing application-level check.

## Impact Explanation
This is a legitimate denial-of-service vector reachable without credentials: an attacker who can reach the gateway's public user-facing HTTP port and knows the public method constants `MethodSecretsGet`/`MethodCapabilityExec` can create arbitrarily many concurrent `activeRequest` map entries within any 30-second window (default `requestTimeout`), each also triggering an RPC fan-out to every DON member. Sustained flooding at a rate exceeding the 1/sec cleanup sweep grows gateway memory unboundedly and imposes proportional load on the DON, degrading or crashing the gateway process and disrupting confidential-relay service availability for legitimate workflow executions. This maps to an in-scope availability/DoS impact against gateway request handling.

## Likelihood Explanation
Likelihood is high. The attack requires only network access to the gateway's `/user`-facing endpoint and a valid unique `id`/`method` per JSON-RPC POST — no signature, JWT, or DON-membership credential is checked on this path, as confirmed by tracing `ProcessRequest` → `HandleJSONRPCUserMessage`. The per-request attacker cost (a small HTTP POST) is far below the server-side cost (map insertion, per-request state, and a fan-out RPC to every DON member), making the attack cheap and repeatable.

## Recommendation
Add a bound on concurrent `activeRequests` (e.g., reject once a `maxActiveRequests` cap is reached, mirroring `handlers/common.RequestCache.maxCacheSize`'s "request cache is full" behavior) and/or introduce a per-sender and global incoming rate limiter in `HandleJSONRPCUserMessage`, consistent with the JWT authentication and dual rate limiting already implemented in the HTTP Capabilities v2 trigger handler, before creating and fanning out new `activeRequest` entries.

## Proof of Concept
1. Identify the gateway's public user-facing HTTP endpoint and a configured Confidential Relay service/DON.
2. Loop sending JSON-RPC POSTs with unique `id` values and arbitrary `params`, no signature/auth attached, e.g. `{"jsonrpc":"2.0","id":"<uuid>","method":"confidentialrelay_secretsGet","params":{}}`.
3. Each request passes the trivial ID-length checks in `HandleJSONRPCUserMessage`, is inserted unconditionally into `h.activeRequests`, and triggers a fan-out send to every DON member.
4. Sustain a request rate exceeding the once-per-second cleanup sweep's reclamation capability (relative to the 30s default `requestTimeout`) to grow `h.activeRequests` without bound, observable via increasing gateway process memory.

### Citations

**File:** core/services/gateway/gateway.go (L238-276)
```go
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
```

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

**File:** core/services/gateway/handlers/capabilities/v2/http_handler.go (L149-152)
```go
	userRateLimiter, err := lf.MakeRateLimiter(cresettings.Default.PerWorkflow.HTTPTrigger.RateLimit)
	if err != nil {
		return nil, fmt.Errorf("failed to create user rate limiter: %w", err)
	}
```

**File:** core/services/gateway/handlers/capabilities/v2/README.md (L203-216)
```markdown
## 7. Security Features

### 7.1 Authentication & Authorization

- **JWT Verification**: All trigger requests must include valid JWT tokens
- **Address Validation**: All addresses must be 0x-prefixed and lowercase
- **Workflow-Scoped Auth**: Each workflow maintains its own authorized key set

### 7.2 Rate Limiting

- **Dual Rate Limiting**: Separate limits for node and user requests
- **Per-Sender Limits**: Individual rate limits per sending entity
- **Global Limits**: System-wide rate limiting for overall protection

```
