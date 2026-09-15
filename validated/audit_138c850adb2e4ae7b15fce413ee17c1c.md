Confirms the claim: the confidential relay gateway's public HTTP user endpoint indeed accepts unauthenticated requests (only an optional JWT header, not verified before dispatch), has no per-user rate limiter or `activeRequests` size cap, and only reaps entries once per second on a 30-second timeout. This matches a genuine, structural gap analogous to the `requestcache.maxCacheSize` protection that exists elsewhere in the codebase but is missing here.

Audit Report

## Title
Unbounded `activeRequests` map growth from unauthenticated gateway user requests enables memory-exhaustion DoS - ([File: core/services/gateway/handlers/confidentialrelay/handler.go])

## Summary
`HandleJSONRPCUserMessage` inserts every incoming user request into the in-memory `activeRequests` map keyed by caller-supplied request ID, gated only by a non-empty/≤200-char check, with no authentication, no per-caller/global rate limiter, and no maximum-size cap before insertion. This lets any client reaching the gateway's public HTTP endpoint flood the map with unique-ID requests faster than the once-per-second cleanup sweep can reclaim them, causing unbounded memory growth and per-request fan-out CPU/network work.

## Finding Description
`HandleJSONRPCUserMessage` validates only `req.ID` length/non-emptiness before calling `newActiveRequest`, which locks `h.mu` and unconditionally inserts into `h.activeRequests[req.ID]`, then calls `fanOutToNodes` to send the request to every DON member: [1](#0-0) [2](#0-1) 

By contrast, `HandleNodeMessage` is gated by `perNodeRateLimiters` and `globalNodeRateLimiter` before touching state: [3](#0-2)  No equivalent limiter exists for the user-facing path, and unlike `common/requestcache.go`'s `NewRequest`, which enforces `len(c.cache) >= int(c.maxCacheSize)` before inserting, `newActiveRequest` has no size cap: [4](#0-3) 

Entries are removed only by a periodic sweep tied to `defaultCleanUpPeriod` (1s) and `defaultRequestTimeoutSec` (30s), or upon completion: [5](#0-4) [6](#0-5) 

Critically, I confirmed that the gateway's top-level HTTP entrypoint performs no authentication before dispatching to the handler. `handleRequest` in the HTTP server reads the body (bounded only by `MaxRequestBytesLimiter`, a payload-size limit, not a rate limiter), optionally extracts a bearer token into a string without validating it, and calls `ProcessRequest` directly: [7](#0-6)  `gateway.ProcessRequest` then only checks message-format validity and the 200-char request-ID cap before routing to `HandleJSONRPCUserMessage`: [8](#0-7) [9](#0-8)  There is no global or per-IP rate limiter anywhere in the HTTP server (`httpserver.go` contains no `RateLimiter` usage) and no signature/JWT verification step is invoked on this path — the `auth`/`jwtToken` string is passed through but never checked by `ProcessRequest` or the confidential relay handler. This confirms the claim that any unauthenticated caller reaching this endpoint can trigger unbounded map growth by submitting unique request IDs faster than the 1-second sweep interval, for up to the 30-second timeout window per request, with each insertion also triggering a `fanOutToNodes` call that does network I/O to every DON member.

## Impact Explanation
An unauthenticated caller can grow `activeRequests` without bound (limited only by their own send rate and the ~30s TTL), consuming increasing gateway memory and forcing repeated fan-out network calls to DON members per request, degrading or potentially crashing the gateway process and denying service to legitimate DON users. This is a concrete availability impact on gateway infrastructure, consistent with a DoS/resource-exhaustion bounty category.

## Likelihood Explanation
Likelihood is high: the only preconditions to reach `HandleJSONRPCUserMessage` are a well-formed JSON-RPC request with a unique ID ≤200 characters, and I found no authentication or rate-limiting check anywhere between the public HTTP listener (`httpserver.go`'s `handleRequest`) and the map insertion in `newActiveRequest`. This requires no privilege and is trivially repeatable by any HTTP client with unique IDs per request.

## Recommendation
- Enforce a maximum size on `activeRequests` (mirroring `requestcache.maxCacheSize`), rejecting new insertions once the cap is reached.
- Add a per-caller/IP and/or global rate limiter to `HandleJSONRPCUserMessage` (or upstream in `gateway.ProcessRequest`/`httpserver.handleRequest`) before any map insertion or DON fan-out work occurs.
- Consider verifying the JWT/auth token before dispatching to handlers, or otherwise require some form of caller identification for rate-limiting purposes.
- Reduce the cleanup sweep interval or make eviction proportional to load/size rather than relying solely on the fixed 1s/30s timers.

## Proof of Concept
1. POST a JSON-RPC request to the gateway's public HTTP endpoint (`config.Path` on the user-facing `httpServer`) targeting a service/DON mapped to the confidential relay handler, with `method` = `MethodSecretsGet` or `MethodCapabilityExec` and a fresh unique `id` (≤200 chars), without any valid `Authorization` header.
2. Observe the request succeeds past `httpServer.handleRequest` → `gateway.ProcessRequest` → `HandleJSONRPCUserMessage` → `newActiveRequest`, confirmed by tracing the code path above — no rejection occurs for lack of auth.
3. Repeat at a rate exceeding one request/second sustained over 30+ seconds with distinct IDs each time; `h.activeRequests` grows unbounded until the sweep in `removeExpiredRequests` catches up, and each insertion also triggers `fanOutToNodes` against all DON members.
4. A Go unit test can instantiate `handler` directly (as in existing `_test.go` files for this package), call `HandleJSONRPCUserMessage` in a loop with unique IDs faster than `defaultCleanUpPeriod`, and assert `len(h.activeRequests)` grows without bound before the timeout elapses.

### Citations

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

**File:** core/services/gateway/gateway.go (L221-234)
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
