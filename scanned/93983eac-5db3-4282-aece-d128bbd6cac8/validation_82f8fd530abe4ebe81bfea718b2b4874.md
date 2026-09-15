## Title
Missing Allowlist and Rate-Limiting Enforcement for User Requests in Gateway Capabilities Handler - (File: core/services/gateway/handlers/capabilities/handler.go)

### Summary
The `capabilities` package's `handler.HandleLegacyUserMessage` function contains an explicit `// TODO: apply allowlist and rate-limiting here` comment marking a security control that was never implemented, directly analogous to the reported TODO-tag bug class (unfinished/commented-out logic that is essential to the system's security posture). This handler is the internet-facing entry point that the Gateway's HTTP server invokes for every unauthenticated legacy user request before fanning it out to all DON member nodes.

### Finding Description
`gateway.ProcessRequest` is the function called directly by the HTTP server for incoming client requests [1](#0-0) . For legacy requests it validates the JSON-RPC envelope, resolves the handler by DON ID, and then calls `h.HandleLegacyUserMessage(ctx, msg, callback)` with no allowlisting or rate limiting applied at this layer [2](#0-1) .

Inside `capabilities.handler.HandleLegacyUserMessage`, after payload decoding and a staleness check, the code contains:
```go
// TODO: apply allowlist and rate-limiting here
if msg.Body.Method != MethodWebAPITrigger {
```
followed immediately by dispatch of the (unauthenticated, unrated) request to every DON member [3](#0-2) .

Contrast this with the sibling `vault` handler, which explicitly requires cryptographic authorization via `h.requestProcessor.ProcessRequest` before dispatching any request other than the public-key lookup [4](#0-3) , and with the newer `capabilities/v2` HTTP trigger handler, which performs JWT-based `authorizeRequest` and `checkRateLimit` before forwarding to nodes [5](#0-4) . The legacy `capabilities` handler used for `MethodWebAPITrigger` has neither of these protections — the TODO was never resolved.

### Impact Explanation
Any unauthenticated client able to reach the Gateway's HTTP endpoint can submit an arbitrary number of `web_api_trigger` legacy messages. Each such message is broadcast to every member node of the configured DON without per-caller allowlisting or throttling [6](#0-5) . This allows resource exhaustion of the DON (each node processes and potentially executes a workflow trigger for every forwarded request) and of the Gateway's `savedCallbacks` map, since only expiry/size-based pruning bounds it, not caller-based quotas [7](#0-6) . This is a quota/allowlist-bypass class issue reachable directly from an unprivileged client request.

### Likelihood Explanation
High. No credentials, signature, or prior relationship with the DON is required to reach `HandleLegacyUserMessage` — only a well-formed JSON-RPC envelope with a valid `MethodWebAPITrigger` and non-stale timestamp, both trivially satisfiable by any caller [8](#0-7) .

### Recommendation
Implement the allowlist and rate-limiting check referenced by the TODO before forwarding `HandleLegacyUserMessage` requests to DON nodes, following the pattern already used in `vault.handler` (`requestProcessor.ProcessRequest` authorization) and `capabilities/v2.httpTriggerHandler` (`authorizeRequest` + `checkRateLimit`) [9](#0-8) .

### Proof of Concept
1. Send a legacy JSON-RPC request to the Gateway's HTTP endpoint with `Method = "web_api_trigger"`, a valid `DonID`, and a fresh `Timestamp`, without any special authorization token.
2. Observe that `gateway.ProcessRequest` routes it straight to `capabilities.handler.HandleLegacyUserMessage`, which — per the unresolved TODO — performs no allowlist or rate-limit check, and forwards the message to every member of the DON [10](#0-9) .
3. Repeat the request at high volume from a single unauthenticated source; because no per-caller allowlist or rate limiter exists in this path, the DON and Gateway callback map absorb unbounded load.

### Citations

**File:** core/services/gateway/gateway.go (L220-272)
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
```

**File:** core/services/gateway/handlers/capabilities/handler.go (L299-334)
```go
func (h *handler) pruneCallbacks() {
	h.mu.Lock()
	defer h.mu.Unlock()

	// First, remove expired callbacks.
	maxAge := time.Duration(h.config.CallbackMaxAgeSec) * time.Second
	now := time.Now()
	var expired int
	for id, cb := range h.savedCallbacks {
		if now.Sub(cb.createdAt) > maxAge {
			delete(h.savedCallbacks, id)
			expired++
		}
	}

	// If there are still too many callbacks, sort them by creation time and remove the oldest ones.
	maxSize := h.config.MaxSavedCallbacks
	var evicted int
	if len(h.savedCallbacks) > maxSize {
		type entry struct {
			id        string
			createdAt time.Time
		}
		entries := make([]entry, 0, len(h.savedCallbacks))
		for id, cb := range h.savedCallbacks {
			entries = append(entries, entry{id, cb.createdAt})
		}
		sort.Slice(entries, func(i, j int) bool {
			return entries[i].createdAt.Before(entries[j].createdAt)
		})
		// Trim to maxSize/2 to avoid sorting the list too frequently.
		for _, e := range entries[:len(entries)-maxSize/2] {
			delete(h.savedCallbacks, e.id)
			evicted++
		}
	}
```

**File:** core/services/gateway/handlers/capabilities/handler.go (L359-420)
```go
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

**File:** core/services/gateway/handlers/vault/handler.go (L422-434)
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
```

**File:** core/services/gateway/handlers/capabilities/v2/http_trigger_handler.go (L95-113)
```go
func (h *httpTriggerHandler) HandleUserTriggerRequest(ctx context.Context, req *jsonrpc.Request[json.RawMessage], callback handlers.Callback, requestStartTime time.Time) error {
	triggerReq, err := h.validatedTriggerRequest(ctx, req, callback)
	if err != nil {
		return err
	}

	workflowID, err := h.resolveWorkflowID(ctx, triggerReq, req.ID, callback)
	if err != nil {
		return err
	}

	key, err := h.authorizeRequest(ctx, workflowID, req, callback)
	if err != nil {
		return err
	}

	if err = h.checkRateLimit(ctx, workflowID, req.ID, callback); err != nil {
		return err
	}
```
