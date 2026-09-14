### Title
Gateway `HandleLegacyUserMessage` Forwards Unvalidated External Requests to All DON Nodes Without Allowlist Enforcement - (File: core/services/gateway/handlers/capabilities/handler.go)

### Summary
The `MultipliBridger` bug class is "accepts an unrestricted, attacker-supplied parameter without validating it against a whitelist of supported values, then propagates it downstream where it cannot be safely processed." The `capabilities.handler.HandleLegacyUserMessage` function in the Chainlink gateway exhibits the same pattern for internet-facing user requests: any unauthenticated/unprivileged HTTP client can submit a webhook/trigger payload, and the handler forwards it verbatim to every node in the DON with an explicit code comment acknowledging that allowlist enforcement is not implemented.

### Finding Description
The gateway's HTTP endpoint accepts requests from any external caller and dispatches them to `gateway.ProcessRequest`, which for legacy DON-ID-addressed requests calls `h.HandleLegacyUserMessage(ctx, msg, callback)` [1](#0-0) . That HTTP entry point performs no per-caller authorization beyond an optional bearer token extraction and is reachable by any network client that can reach the configured HTTP path [2](#0-1) .

Inside `HandleLegacyUserMessage`, the code validates payload structure (JSON decode, timestamp presence/staleness, method name) but explicitly skips a whitelist/rate-limit check that the author flagged as missing:
```go
// TODO: apply allowlist and rate-limiting here
if msg.Body.Method != MethodWebAPITrigger {
```
After these checks, the message is unconditionally forwarded to every member of the DON:
```go
for _, member := range h.donConfig.Members {
    err = errors.Join(err, don.SendToNode(ctx, member.Address, req))
}
``` [3](#0-2) 

There is no check that the request's sender/workflow owner is registered/whitelisted for the target DON or capability, unlike the `vault` gateway handler in the same codebase, which explicitly wires an `Authorizer`/allowlist-based authorization chain before processing any request [4](#0-3) . This is precisely analogous to `MultipliBridger.deposit` accepting any `token` address without checking it against a supported list before propagating it into a system (StarkEx L2 / off-chain minting) that assumes only whitelisted values will ever arrive.

### Impact Explanation
Because every legacy webhook/trigger request bypasses allowlist/rate-limit enforcement, any unprivileged network caller can cause the gateway to broadcast attacker-controlled payloads to all nodes of a DON. This is a request-forwarding/resource-consumption path with no whitelist gate, mirroring the "unsupported input accepted and propagated downstream where it cannot be safely handled" root cause from the report: nodes may receive triggers for workflows/methods they were never meant to process, and there is no way to distinguish legitimate versus unauthorized senders at this layer, undermining the intended trust boundary between the internet-facing gateway and DON nodes.

### Likelihood Explanation
The vulnerable code path is reached directly from the gateway's public HTTP endpoint with no authentication requirement beyond structurally valid JSON and a non-stale timestamp [5](#0-4) . The missing check is explicitly marked with a `TODO`, confirming it is a known gap rather than a defense-in-depth omission, making it straightforward for any external, unprivileged actor to trigger.

### Recommendation
Implement the allowlist/rate-limiting check that is called out in the `TODO` before forwarding messages to DON members — verify the message sender/workflow is authorized for the target DON and method, following the same pattern already used by the `vault` gateway handler's `Authorizer`/allowlist chain [4](#0-3) .

### Proof of Concept
1. Send a legacy JSON-RPC request to the gateway's public HTTP endpoint with a valid `DonID`, a fresh `Timestamp`, and `Method` = `web_api_trigger`, without any special credentials.
2. `gateway.ProcessRequest` routes it to `capabilities.handler.HandleLegacyUserMessage` based solely on `msg.Body.DonID` [6](#0-5) .
3. The handler performs structural validation only (no allowlist), then loops over `h.donConfig.Members` and sends the request to every node [7](#0-6) , demonstrating that an unprivileged, unwhitelisted caller can cause payloads to be broadcast to the entire DON.

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

**File:** core/services/gateway/network/httpserver.go (L195-234)
```go
func (s *httpServer) handleRequest(w http.ResponseWriter, r *http.Request) {
	if s.config.CORSEnabled {
		origin := r.Header.Get("Origin")
		if s.isAllowedOrigin(origin) {
			w.Header().Set("Access-Control-Allow-Origin", origin)
			w.Header().Set("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
			w.Header().Set("Access-Control-Allow-Headers", "Content-Type")
		}

		// handle preflight requests
		if r.Method == http.MethodOptions {
			w.WriteHeader(http.StatusNoContent)
			return
		}
	}

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

**File:** core/services/gateway/handlers/capabilities/handler.go (L341-420)
```go
func (h *handler) HandleLegacyUserMessage(ctx context.Context, msg *api.Message, callback handlers.Callback) error {
	body := msg.Body
	var payload webapicap.TriggerRequestPayload
	codec := api.JSONRPCCodec{}
	err := json.Unmarshal(body.Payload, &payload)
	if err != nil {
		h.lggr.Errorw(ErrDecodingPayload, "err", err)
		return callback.SendResponse(handlers.UserCallbackPayload{
			RawResponse: codec.EncodeNewErrorResponse(
				msg.Body.MessageID,
				api.ToJSONRPCErrorCode(api.UserMessageParseError),
				ErrDecodingPayload+" "+err.Error(),
				nil,
			),
			ErrorCode: api.UserMessageParseError,
		})
	}

	if payload.Timestamp == 0 {
		h.lggr.Errorw(ErrDecodingPayload)
		return callback.SendResponse(handlers.UserCallbackPayload{
			RawResponse: codec.EncodeNewErrorResponse(
				msg.Body.MessageID,
				api.ToJSONRPCErrorCode(api.UserMessageParseError),
				ErrDecodingPayload,
				nil,
			),
			ErrorCode: api.UserMessageParseError,
		})
	}

	if uint(time.Now().Unix())-h.config.MaxAllowedMessageAgeSec > uint(payload.Timestamp) { //nolint:gosec // G115: comparing unix timestamps, both fit within uint
		h.lggr.Errorw("stale message")
		return callback.SendResponse(handlers.UserCallbackPayload{
			RawResponse: codec.EncodeNewErrorResponse(
				msg.Body.MessageID,
				api.ToJSONRPCErrorCode(api.HandlerError),
				"stale message",
				nil,
			),
			ErrorCode: api.HandlerError,
		})
	}
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

**File:** core/capabilities/vault/gw_handler.go (L108-126)
```go
	if authorizer == nil {
		allowListBasedAuth := NewAllowListBasedAuth(lggr, workflowRegistrySyncer)
		authorizer = NewAuthorizer(allowListBasedAuth, jwtBasedAuth, lggr)
	}

	requestValidator, err := NewRequestValidatorFromLimitsFactory(limitsFactory)
	if err != nil {
		return nil, fmt.Errorf("failed to create request validator: %w", err)
	}

	metrics, err := newMetrics()
	if err != nil {
		return nil, fmt.Errorf("failed to create metrics: %w", err)
	}

	requestProcessor, err := NewGatewayVaultRequestProcessor(requestValidator, authorizer, true, lggr)
	if err != nil {
		return nil, fmt.Errorf("failed to create gateway vault request processor: %w", err)
	}
```
