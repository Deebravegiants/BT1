This confirms `gateway.ProcessRequest` reaches `HandleJSONRPCUserMessage` after only decoding, basic ID-length, and legacy validation checks — no per-client submission rate limiter or cap gates entry into `newActiveRequest`, and the callback then blocks (`callback.Wait(ctx)`) on the handler completing, consistent with the claim. The confidential relay handler's only rate limiters (`globalNodeRateLimiter`, `perNodeRateLimiters`) are applied solely in `HandleNodeMessage` (for DON node responses), not on the initial client-submitted request path, matching the claim precisely.

Audit Report

## Title
Unbounded growth of `activeRequests` map in `ConfidentialRelayHandler` enables DoS via periodic full-map sweep - ([File: core/services/gateway/handlers/confidentialrelay/handler.go])

## Summary
`handler.HandleJSONRPCUserMessage`, reached directly from `gateway.ProcessRequest` for every client request routed to the confidential relay handler, inserts entries into `h.activeRequests` via `newActiveRequest` with only a duplicate-ID check and no maximum size enforced. A background goroutine started in `Start` sweeps the entire map every second via `forwardGracedRequests` and `removeExpiredRequests`, so both memory and per-tick sweep cost scale linearly with the number of outstanding requests, which an unprivileged client fully controls.

## Finding Description
`gateway.ProcessRequest` decodes the request, does only a 200-character ID-length check and (for legacy requests) `msg.Validate()`, then dispatches to `h.HandleJSONRPCUserMessage(ctx, jsonRequest, callback)` [1](#0-0) . Inside the confidential relay handler, `HandleJSONRPCUserMessage` performs its own ID checks and calls `newActiveRequest`, which rejects only on duplicate ID and otherwise unconditionally inserts into `h.activeRequests` with no size cap [2](#0-1) . This is in contrast to the sibling `common.RequestCache`, which explicitly enforces `maxCacheSize` and rejects insertion once full [3](#0-2) . The cleanup goroutine ticks every second and calls `forwardGracedRequests`/`removeExpiredRequests`, both of which iterate the entire map under `h.mu.RLock()` [4](#0-3) [5](#0-4) [6](#0-5) . The handler's two rate limiters (`globalNodeRateLimiter`, `perNodeRateLimiters`) are applied only in `HandleNodeMessage`, gating DON node responses, not the initial client submission path that creates entries [7](#0-6) . Entries are removed only in `sendResponseAndClearRequest`, which fires on completion, expiry (`requestTimeout`, default 30s), or grace-window elapse [8](#0-7) . Thus a client submitting unique-ID requests faster than the 30-second timeout retires old ones grows `activeRequests` without bound.

## Impact Explanation
An unprivileged client flooding the gateway with distinct-ID `MethodSecretsGet`/`MethodCapabilityExec` requests grows `activeRequests` unbounded, increasing memory (each entry holds the request, a per-node response map, and callback) and making the once-per-second sweep progressively more expensive while it holds `h.mu.RLock()`, contending with the `Lock()` taken by `newActiveRequest`/`sendResponseAndClearRequest`. This can degrade or stall processing of legitimate relay requests to the confidential relay/vault-secrets DON, an availability/DoS impact rather than a fund-loss one, consistent with a Medium-severity finding.

## Likelihood Explanation
`HandleJSONRPCUserMessage` is reachable by any client able to reach the gateway's user-facing endpoint, with the only per-request cost gate being the 200-character ID check; nothing throttles the *rate or count* of newly submitted client requests before insertion into `activeRequests`. This makes the DoS straightforward and repeatable against any DON configured with the `confidentialrelay` handler.

## Recommendation
Add an explicit maximum size to `activeRequests` (mirroring `common.RequestCache`'s `maxCacheSize`) and reject new requests once the cap is reached in `newActiveRequest`. Additionally, apply a rate limiter to inbound client requests (not just node responses) before creating an `activeRequest` entry, and consider bounding sweep cost (e.g., timer-indexed structures or sharded maps) so cleanup cost does not scale linearly with total outstanding requests.

## Proof of Concept
1. Configure a DON with the `confidentialrelay` handler at default settings (`requestTimeoutSec=30`, cleanup tick=1s).
2. As an unprivileged client, repeatedly POST JSON-RPC requests to the gateway with unique `ID` values for `MethodCapabilityExec`/`MethodSecretsGet`, at a rate faster than the 30s timeout can retire them (e.g., thousands per second).
3. Observe `activeRequests` grow without bound (rejected only on duplicate ID) and the 1-second `removeExpiredRequests`/`forwardGracedRequests` sweep taking progressively longer under `h.mu.RLock()`, delaying concurrent legitimate request processing.

### Citations

**File:** core/services/gateway/gateway.go (L221-276)
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

**File:** core/services/gateway/handlers/confidentialrelay/handler.go (L605-614)
```go
func (h *handler) forwardGracedRequests(ctx context.Context) {
	h.mu.RLock()
	var graced []*activeRequest
	now := h.clock.Now()
	for _, ar := range h.activeRequests {
		if ar.graceElapsed(now) {
			graced = append(graced, ar)
		}
	}
	h.mu.RUnlock()
```

**File:** core/services/gateway/handlers/confidentialrelay/handler.go (L735-755)
```go
func (h *handler) sendResponseAndClearRequest(ctx context.Context, ar *activeRequest, payload gwhandlers.UserCallbackPayload) error {
	if !ar.completed.CompareAndSwap(false, true) {
		// Another path already answered this request.
		return nil
	}

	sendErr := ar.SendResponse(payload)

	h.mu.Lock()
	delete(h.activeRequests, ar.req.ID)
	h.mu.Unlock()

	if sendErr != nil {
		h.lggr.Errorw("error sending response to user", "requestID", ar.req.ID, "executionID", ar.labels.ExecutionID, "error", sendErr)
		return sendErr
	}

	h.recordMetrics(ctx, payload.ErrorCode)
	h.lggr.Debugw("response sent to user", "requestID", ar.req.ID, "executionID", ar.labels.ExecutionID, "errorCode", payload.ErrorCode)
	return nil
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
