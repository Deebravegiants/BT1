Confirmed: `HandleLegacyUserMessage` in `core/services/gateway/handlers/capabilities/handler.go` is directly reachable from any unauthenticated HTTP client via `gateway.ProcessRequest` → `h.HandleLegacyUserMessage(ctx, msg, callback)` at [1](#0-0) , with the HTTP layer performing no authentication of the caller beyond an optional JWT header that is merely passed through, not verified, at this layer [2](#0-1) . The handler itself explicitly documents skipping allowlist and rate-limiting checks before broadcasting the request to every DON member.

### Title
Missing allowlist/rate-limit enforcement allows unprivileged clients to broadcast arbitrary triggers to all DON nodes - (File: core/services/gateway/handlers/capabilities/handler.go)

### Summary
The legacy Web API trigger path in the gateway's `capabilities.handler` accepts any externally-submitted `web_api_trigger` message and forwards it, unmodified, to every member node of the DON — with an explicit `// TODO: apply allowlist and rate-limiting here` marking the missing control.

### Finding Description
`(h *handler) HandleLegacyUserMessage` validates only the payload shape (non-zero timestamp, message not stale, method equals `MethodWebAPITrigger`), then immediately fans the request out to all DON members: [3](#0-2) 

There is no check that the sender is an allowlisted workflow owner/consumer, and no per-sender rate limiting is applied at this entry point (the only rate limiter in this handler, `nodeRateLimiter`, throttles node→gateway traffic, not user→gateway traffic) [4](#0-3) . This request path is reached directly from the internet-facing HTTP endpoint: `httpServer.handleRequest` reads the raw body and hands it to `gateway.ProcessRequest` without any authentication gate [5](#0-4) , which in turn dispatches legacy messages straight into the handler [6](#0-5) .

This matches the CVE's bug-class in effect (an external, unauthenticated actor able to flood a target with unrestricted crafted messages, causing unwanted traffic/DoS and triggering unintended downstream processing) but the injection point here is an application-layer missing access-control/rate-limit, not a network/transport-layer issue — i.e., it is a legitimate allowlist/quota-bypass analog reachable by an unprivileged HTTP client, rather than a malicious-node or network-layer flaw.

### Impact Explanation
An unauthenticated caller can repeatedly submit `web_api_trigger` requests that are broadcast to every node in a DON, consuming DON compute/network resources and invoking workflow trigger callbacks without any allowlist check — this is an unauthorized-trigger / quota-bypass condition that can degrade or deny service for legitimate workflow owners on that DON.

### Likelihood Explanation
High: this handler's job is to receive external, unprivileged requests over the gateway's public HTTP endpoint; no code path currently rejects an un-allowlisted sender before fan-out, and the missing control is called out explicitly in the source as a `TODO`, indicating it was never implemented in this code path (in contrast to the JSON-RPC v2 HTTP trigger handler, which does enforce JWT auth and per-owner rate limiting).

### Recommendation
Enforce allowlist checks (e.g., against the DON's authorized workflow owners/consumers) and per-sender rate limiting in `HandleLegacyUserMessage` before fanning requests out to DON members, mirroring the authorization/rate-limiting already implemented for the newer JSON-RPC HTTP trigger handler (`httpTriggerHandler`) at `core/services/gateway/handlers/capabilities/v2/http_trigger_handler.go`.

### Proof of Concept
1. Send a raw legacy-format JSON-RPC POST to the gateway's public HTTP endpoint (`config.Path`) with `Body.DonID` set to a target DON, `Body.Method` = `web_api_trigger`, a valid `Timestamp`, and no prior registration/allowlisting of the sender.
2. Observe in `gateway.ProcessRequest` that the message is routed via `msg.Validate()` then `h.HandleLegacyUserMessage(ctx, msg, callback)` with no authentication/authorization check performed.
3. Observe the handler broadcasts the message to every DON member via `don.SendToNode` for each configured member, confirming the request reached all nodes despite the caller being unauthenticated and un-allowlisted [7](#0-6) .

### Citations

**File:** core/services/gateway/gateway.go (L253-276)
```go
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

**File:** core/services/gateway/handlers/capabilities/handler.go (L48-61)
```go
type handler struct {
	services.StateMachine
	config          HandlerConfig
	don             handlers.DON
	donConfig       *config.DONConfig
	savedCallbacks  map[string]*savedCallback
	mu              sync.Mutex
	lggr            logger.Logger
	httpClient      network.HTTPClient
	nodeRateLimiter *ratelimit.RateLimiter
	wg              sync.WaitGroup
	stopCh          services.StopChan
	metrics         *metrics
}
```

**File:** core/services/gateway/handlers/capabilities/handler.go (L384-420)
```go
	// TODO: apply allowlist and rate-limiting here
	if msg.Body.Method != MethodWebAPITrigger {
		h.lggr.Errorw("unsupported method", "method", body.Method)
		return callback.SendResponse(handlers.UserCallbackPayload{
			RawResponse: codec.EncodeNewErrorResponse(
				msg.Body.MessageID,
				api.ToJSONRPCErrorCode(api.UnsupportedMethodError),
				"invalid method "+msg.Body.Method,
				nil,
			),
			ErrorCode: api.UnsupportedMethodError,
		})
	}
	req, err := common.ValidatedRequestFromMessage(msg)
	if err != nil {
		h.lggr.Errorw(ErrTransformingMessageToRequest)
		return callback.SendResponse(handlers.UserCallbackPayload{
			RawResponse: codec.EncodeNewErrorResponse(
				msg.Body.MessageID,
				api.ToJSONRPCErrorCode(api.UserMessageParseError),
				ErrTransformingMessageToRequest,
				nil,
			),
			ErrorCode: api.UserMessageParseError,
		})
	}

	h.mu.Lock()
	h.savedCallbacks[msg.Body.MessageID] = &savedCallback{id: msg.Body.MessageID, createdAt: time.Now(), Callback: callback}
	don := h.don
	h.mu.Unlock()

	// Send original request to all nodes
	for _, member := range h.donConfig.Members {
		err = errors.Join(err, don.SendToNode(ctx, member.Address, req))
	}
	return err
```
