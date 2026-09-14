Based on my investigation, I found a plausible but not fully confirmed analog.

### Title
Unbounded `activeRequests` Map Growth per DON in Confidential Relay Gateway Handler - ([File: core/services/gateway/handlers/confidentialrelay/handler.go])

### Summary
The `HandleJSONRPCUserMessage` entry point in the confidential relay gateway handler accepts unprivileged user requests and immediately inserts an entry into an in-memory `activeRequests` map keyed by request ID, without any admission-time rate limit or bound on the number of concurrent entries, mirroring the Netty `HttpContentEncoder.acceptEncodingQueue` pattern of unbounded per-entity accumulation of attacker-controlled state drained only later.

### Finding Description
`HandleJSONRPCUserMessage` only validates that `req.ID` is non-empty and ≤200 characters before calling `h.newActiveRequest(req, labels, callback)`, which locks `h.mu` and inserts the request into `h.activeRequests[req.ID]` unconditionally (subject only to ID uniqueness) [1](#0-0) . There is no per-user/per-caller rate limiter or maximum-active-requests check applied before this insertion — the only rate limiters present in this handler (`perNodeRateLimiters`, `globalNodeRateLimiter`) gate *node* responses, not the initial *user* request path [2](#0-1) . Each `activeRequest` allocates a `responses` map and metadata that persists until either quorum is reached or `removeExpiredRequests` sweeps it after `h.requestTimeout` (default 30s), which runs on a periodic cleanup timer (`defaultCleanUpPeriod = time.Second`) [3](#0-2) [4](#0-3) . This is structurally analogous to the Netty bug: attacker-controlled inbound messages accumulate in an unbounded structure, filled synchronously on receipt, and only drained by a slower, decoupled process (application response / periodic timer).

The equivalent `vault` handler has the identical pattern in `newActiveRequest` / `HandleJSONRPCUserMessage` [5](#0-4) [6](#0-5) .

### Impact Explanation
If an unprivileged caller can submit user JSON-RPC messages with unique request IDs faster than the 30-second expiry sweep can clear them, each request holds a small but nonzero heap allocation (`activeRequest` struct, `responses` map, mutex, labels) in gateway memory. Sustained high-rate submission could grow memory usage and lock-contention on `h.mu` (a single mutex guarding the whole map) proportionally to `attacker_rate × requestTimeout`, potentially degrading or exhausting gateway resources — a resource-exhaustion condition consistent with CWE-770. I was not able to confirm from the available code whether an upstream admission-layer rate limiter (e.g., a connection-level or global request-rate limiter in `core/services/gateway/gateway.go` or `multihandler.go`) already bounds the rate of `HandleJSONRPCUserMessage` calls before they reach this handler; my last search into those files was cut off before I could verify this, so I cannot rule out that this is already mitigated at a layer above the handler.

### Likelihood Explanation
Reachability from an unprivileged actor is plausible in principle (any caller able to send a JSON-RPC request through the gateway to this handler), but I could not fully verify the absence of an outer per-caller/global admission rate limiter or connection-level throttling in `core/services/gateway/gateway.go`, `connectionmanager.go`, or `multihandler.go` due to running out of investigation iterations. Without confirming that no such upstream control exists, I cannot assert this is concretely exploitable end-to-end.

### Recommendation
If not already present upstream, add an explicit bound on the number of concurrent `activeRequests` per handler (or per caller/org), reject new requests once the bound is reached, and/or apply a request-admission rate limiter before `newActiveRequest` is called in both `core/services/gateway/handlers/confidentialrelay/handler.go` and `core/services/gateway/handlers/vault/handler.go`.

### Proof of Concept
Not constructed — I could not confirm the absence of an upstream rate limiter that would gate this path before it reaches `HandleJSONRPCUserMessage`, so I cannot assert this is concretely reachable and exploitable without further verification of `core/services/gateway/gateway.go` and `core/services/gateway/connector/connector.go`, whose relevant rate-limiting logic I was unable to fully inspect within the available iterations.

### Citations

**File:** core/services/gateway/handlers/confidentialrelay/handler.go (L30-42)
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

**File:** core/services/gateway/handlers/vault/handler.go (L394-454)
```go
func (h *handler) HandleJSONRPCUserMessage(ctx context.Context, req jsonrpc.Request[json.RawMessage], callback gwhandlers.Callback) error {
	if req.ID == "" {
		return errors.New("request ID cannot be empty")
	}
	if len(req.ID) > 200 {
		// Arbitrary limit to prevent abuse
		return errors.New("request ID is too long: " + strconv.Itoa(len(req.ID)) + ". max is 200 characters")
	}

	h.lggr.Debugw("handling vault request", "method", req.Method, "requestID", req.ID, "request", req)
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

	switch req.Method {
	case vaulttypes.MethodSecretsCreate:
		return h.handleSecretsCreate(ctx, ar)
	case vaulttypes.MethodSecretsUpdate:
		return h.handleSecretsUpdate(ctx, ar)
	case vaulttypes.MethodSecretsDelete:
		return h.handleSecretsDelete(ctx, ar)
	case vaulttypes.MethodSecretsList:
		return h.handleSecretsList(ctx, ar)
	default:
		return h.sendResponse(ctx, ar, h.errorResponse(req, api.UnsupportedMethodError, errors.New("this method is unsupported: "+req.Method), nil))
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
