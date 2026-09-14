### Title
Unauthenticated caller can cause unbounded per-request memory growth in the Confidential Relay gateway handler - ([File: core/services/gateway/handlers/confidentialrelay/handler.go])

### Summary
The gateway's Confidential Relay handler accepts JSON-RPC user requests over the internet-facing `/user` gateway endpoint without any authentication, authorization, or per-caller quota, and stores state for every accepted request in an in-memory map until a fixed timeout elapses. An unprivileged/unauthenticated client can flood the endpoint with unique request IDs to grow this map without bound until node memory is exhausted, closely mirroring the Xen `xenstored` bug class in ALPINE-CVE-2022-42317 where an unprivileged guest could force unbounded server-side memory allocation by issuing many outstanding requests.

### Finding Description
`gateway.ProcessRequest` is the entry point for all HTTP requests to the gateway's user-facing endpoint. For JSON-RPC (non-legacy) requests it resolves a handler purely by service name and invokes `HandleJSONRPCUserMessage` — the legacy `msg.Validate()`/signature check path is only exercised when `msg.Body.DonID != ""`, so JSON-RPC-routed requests bypass that check entirely: [1](#0-0) 

The Confidential Relay handler's `HandleJSONRPCUserMessage` performs only trivial request-ID length checks (empty / >200 chars) before creating a new tracked `activeRequest` entry and fanning it out to DON nodes — there is no authentication, no authorization, and no per-sender/global rate limiting on the incoming path: [2](#0-1) 

Each accepted request is inserted into an unbounded `map[string]*activeRequest`, keyed only by the caller-supplied `req.ID`, with no cap on the number of concurrent entries (`h.activeRequests[req.ID] = ar`): [3](#0-2) 

The only rate limiters present in this handler (`globalNodeRateLimiter`, `perNodeRateLimiters`) throttle *node* responses coming back from the DON, not incoming *user* requests: [4](#0-3) 

Entries are only removed by a periodic sweep (`removeExpiredRequests`, run once per second) once `now.Sub(createdAt) > h.requestTimeout` (default 30 seconds): [5](#0-4) [6](#0-5) 

By contrast, other gateway subsystems bound this exposure explicitly: the generic `RequestCache` used elsewhere in the gateway enforces a `maxCacheSize` and rejects new requests once full (`"request cache is full"`): [7](#0-6) 
and the HTTP capabilities v2 handler requires JWT authentication plus per-sender/global rate limiting for inbound triggers: [8](#0-7) 

The Confidential Relay handler has neither protection: any caller who can reach the gateway's `/user` HTTP endpoint can create an arbitrary number of distinct `activeRequest` entries (unique `req.ID` per call) within any 30-second window, each holding a request, labels, and a `responses` map, and each additionally triggering a fan-out RPC to every DON member. Sustained flooding accumulates memory proportional to the attacker's request rate × retention window, unconstrained by any cap.

### Impact Explanation
This is a Denial-of-Service vector reachable by any unauthenticated network client that can send HTTP requests to the gateway's user endpoint (no signature, JWT, or DON membership required for this handler/method routing path). Sustained flooding can exhaust gateway process memory, degrading or crashing the gateway and disrupting confidential-relay service for legitimate workflow executions — directly analogous to the "malicious guest exhausts server memory via many outstanding/unread requests" bug class in the cited Xen advisory, but reachable here by an unprivileged external HTTP caller rather than a privileged guest.

### Likelihood Explanation
Likelihood is high: the attack requires only network access to the gateway's public user-facing port and knowledge of the Confidential Relay method names (`MethodSecretsGet`/`MethodCapabilityExec`), which are public constants. No credentials, signatures, or DON membership are needed to reach `HandleJSONRPCUserMessage`, and the per-request cost to the attacker (a small HTTP POST) is far lower than the cumulative server-side cost (map entry + goroutine + fan-out RPCs to every DON member per request).

### Recommendation
Add a bound on concurrent `activeRequests` (reject/",request cache is full"-style, similar to `common.RequestCache.maxCacheSize`) and/or a per-sender and global incoming rate limiter on `HandleJSONRPCUserMessage`, mirroring the JWT authentication and dual rate limiting already used by the HTTP capabilities v2 trigger handler, before creating and fanning out new `activeRequest` entries.

### Proof of Concept
1. Identify the gateway's public `/user` HTTP endpoint and a configured Confidential Relay DON (`MethodSecretsGet` or `MethodCapabilityExec`).
2. In a loop, send JSON-RPC POST requests with a unique `id` field each time and arbitrary/garbage `params` (no signature or auth token attached), e.g.:
   `{"jsonrpc":"2.0","id":"<random-uuid>","method":"confidentialrelay_secretsGet","params":{}}`
3. Each request passes the ID-length checks in `HandleJSONRPCUserMessage`, is inserted into `h.activeRequests`, and triggers a fan-out to all DON members, without any authentication or per-sender throttling.
4. Repeat at a rate exceeding the 1-request-per-second cleanup sweep's ability to expire entries (default `requestTimeout` = 30s) to grow `h.activeRequests` unboundedly and exhaust gateway memory.

*Note: I could not fully verify whether an upstream reverse proxy or infrastructure-level rate limiter is deployed in front of the gateway in production, since that would be outside the indexed application code — this finding is scoped strictly to the application-level authorization/rate-limiting gap in the handler itself.*

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

**File:** core/services/gateway/handlers/confidentialrelay/handler.go (L36-42)
```go
	defaultRequestTimeoutSec  = 30
	defaultNodeSendTimeoutSec = 10

	// defaultQuorumGraceMillis bounds the extra wait after quorum is reached. It must
	// stay well below the caller's own HTTP deadline, which is what actually cuts the
	// request short when the DON never produces 2F+1 signed responses.
	defaultQuorumGraceMillis = 10_000
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

**File:** core/services/gateway/handlers/common/requestcache.go (L60-66)
```go
	_, ok := c.cache[key]
	if ok {
		return errors.New("request already exists")
	}
	if len(c.cache) >= int(c.maxCacheSize) {
		return errors.New("request cache is full")
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
