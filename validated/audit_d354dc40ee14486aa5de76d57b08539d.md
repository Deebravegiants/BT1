Confirmed: `gateway.ProcessRequest` at [1](#0-0)  is the internet-facing entry point that decodes an inbound HTTP JSON-RPC request and dispatches it straight to `h.HandleJSONRPCUserMessage(ctx, jsonRequest, callback)` for any unauthenticated caller — there is no global admission/concurrency limiter before the handler is invoked.

### Title
Unbounded per-request memory allocation in Confidential Relay gateway handler via unlimited concurrent user requests - (File: core/services/gateway/handlers/confidentialrelay/handler.go)

### Summary
The Confidential Relay gateway handler creates a new in-memory `activeRequest` (containing a `responses` map) for every distinct JSON-RPC request ID it receives from an unauthenticated internet-facing caller, and only removes it after a fixed timeout (default 30s) or upon completion. There is no limit on the total number of concurrently tracked requests, mirroring the QEMU CVE-2016-7994 pattern where an unprivileged caller repeatedly issuing resource-creation commands (`VIRTIO_GPU_CMD_RESOURCE_CREATE_2D`) causes unbounded memory growth because the resources are never capped, only reclaimed later.

### Finding Description
`gateway.ProcessRequest` [1](#0-0)  is the gateway's HTTP entry point: it decodes the raw JSON-RPC body and, for JSON-RPC style requests, calls `h.HandleJSONRPCUserMessage(ctx, jsonRequest, callback)` directly — no per-caller quota or global request-count limiter guards this call before the message reaches the handler.

For the confidential relay method group, `HandleJSONRPCUserMessage` [2](#0-1)  only validates that `req.ID` is non-empty and ≤200 characters, then calls `h.newActiveRequest(req, labels, callback)`.

`newActiveRequest` [3](#0-2)  unconditionally allocates a new `activeRequest` struct (which itself holds a `map[string]*jsonrpc.Response[json.RawMessage]` sized to the DON member count) and inserts it into `h.activeRequests[req.ID]`. The only rejection condition is a duplicate ID; there is no cap on the total size of `h.activeRequests`.

The map is defined without any bound: [4](#0-3) .

Entries are only removed by the periodic cleanup goroutine that runs every `defaultCleanUpPeriod` (1 second) and evicts requests older than `requestTimeout` (default 30 seconds): [5](#0-4)  and [6](#0-5) .

The existing rate limiters (`globalNodeRateLimiter`, `perNodeRateLimiters`) only throttle inbound *node* responses in `HandleNodeMessage` [7](#0-6)  — they do not throttle the rate at which unauthenticated users can call `HandleJSONRPCUserMessage` and create new `activeRequest` entries. An attacker who can reach the gateway's HTTP endpoint can therefore submit an unbounded stream of requests with unique IDs (unique IDs are trivial to generate and are only rejected if they collide), each one allocating and retaining memory for up to the full `requestTimeout` window before it is reclaimed — directly analogous to the QEMU bug's unmetered `VIRTIO_GPU_CMD_RESOURCE_CREATE_2D` allocations that are only freed later.

### Impact Explanation
This is an unauthenticated, low-effort, remotely triggerable memory-exhaustion (denial of service) vector against the gateway process. A high enough sustained request rate can keep tens of thousands of `activeRequest` entries (each carrying a per-DON-member response map plus the full request/labels) alive simultaneously, exhausting gateway memory and potentially starving legitimate relay requests or crashing the gateway process, which sits on the path for the Confidential Compute vault-secrets flow.

### Likelihood Explanation
Likelihood is high: the entry point (`gateway.ProcessRequest` → `HandleJSONRPCUserMessage`) is explicitly reachable by unauthenticated external callers over HTTP, requires no valid signature/JWT to reach `newActiveRequest` (that validation happens later, inside the DON nodes, not the gateway), and the only per-request cost to the attacker is generating a unique string ID.

### Recommendation
Add an admission-control mechanism in the confidential relay handler (and ideally at `gateway.ProcessRequest` generally) that caps the number of concurrently tracked `activeRequests` per caller and/or globally (e.g., a `limits.RateLimiter`/`limits.ResourcePoolLimiter` similar to the ones already used for node responses and the HTTP action mTLS concurrency limiter at [8](#0-7) ), rejecting new requests once the cap is reached instead of unconditionally growing `h.activeRequests`.

### Proof of Concept
1. Send a high-rate stream of HTTP POST requests to the gateway's `ProcessRequest` endpoint, each a valid JSON-RPC envelope with `method: MethodSecretsGet` (or `MethodCapabilityExec`) and a unique `id` (e.g., incrementing counter or UUID), and arbitrary/garbage `params`.
2. Each request passes the ID length/emptiness check and reaches `newActiveRequest`, which allocates and stores a new entry in `h.activeRequests` before any DON-side authorization or signature check occurs.
3. Sustain the request rate above the eviction rate (entries only expire after `requestTimeout`, default 30s, swept once per second) so that `len(h.activeRequests)` grows without bound, consuming increasing gateway memory until the process is starved or OOM-killed.

### Citations

**File:** core/services/gateway/gateway.go (L221-279)
```go
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

**File:** core/services/gateway/handlers/confidentialrelay/handler.go (L30-47)
```go
const (
	// defaultCleanUpPeriod is how often expired requests are swept and closed grace
	// windows are forwarded, so it also bounds how far past its deadline a grace
	// window can run.
	defaultCleanUpPeriod = time.Second

	defaultRequestTimeoutSec  = 30
	defaultNodeSendTimeoutSec = 10

	// defaultQuorumGraceMillis bounds the extra wait after quorum is reached. It must
	// stay well below the caller's own HTTP deadline, which is what actually cuts the
	// request short when the DON never produces 2F+1 signed responses.
	defaultQuorumGraceMillis = 10_000

	// Re-exported from chainlink-common for local use and test convenience.
	MethodSecretsGet     = relaytypes.MethodSecretsGet
	MethodCapabilityExec = relaytypes.MethodCapabilityExec
)
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

**File:** core/services/gateway/handlers/capabilities/v2/http_handler.go (L159-162)
```go
	mtlsConcurrencyLimiter, err := limits.MakeResourcePoolLimiter(lf, cresettings.Default.GatewayHTTPActionMtlsConcurrencyLimit)
	if err != nil {
		return nil, fmt.Errorf("failed to create mtls concurrency limiter: %w", err)
	}
```
