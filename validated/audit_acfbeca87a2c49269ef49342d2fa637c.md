## Finding: Legacy gateway web-API trigger path lacks the allowlist check its own code flags as missing

The Filecoin snap bug is fundamentally about an **unauthorized/unauthenticated caller being able to invoke a privileged operation with no allowlist check**, because "any dapp" can hit `fil_configure`. The closest concrete analog in this chainlink repo is in the Gateway's legacy web-API-trigger message path, where the handler code explicitly documents that the allowlist/rate-limit check it should apply is missing.

### Root cause

Any HTTP request to the Gateway's public-facing `UserServerConfig` port is passed, without any prior authentication, into `gateway.ProcessRequest`: [1](#0-0) 

`ProcessRequest` decodes the payload and, for "legacy" requests (those carrying a `DonID`), dispatches straight to `HandleLegacyUserMessage` on the resolved handler — no allowlist/authorization check happens at this layer: [2](#0-1) 

The web-API capabilities handler's `HandleLegacyUserMessage` implementation only validates the JSON-RPC method name and message staleness/timestamp before forwarding the request to **every DON member node** via `don.SendToNode`. Crucially, the code contains an explicit acknowledgment that authorization is not enforced: [3](#0-2) 

The line `// TODO: apply allowlist and rate-limiting here` at `core/services/gateway/handlers/capabilities/handler.go:384` sits directly before the method-name check, confirming that no authorization/allowlist gate exists for this legacy `web_api_trigger` request path, unlike the newer JSON-RPC v2 HTTP trigger path (`http_trigger_handler.go`) which does call `authorizeRequest`: [4](#0-3) 

### Why this matches the analog class

- **Unprivileged-actor reachable**: the Gateway's `UserServerConfig` HTTP port is the "internet-facing gateway" endpoint reachable by any client, with no session/token/API-key check performed before `HandleLegacyUserMessage` runs. [5](#0-4) 
- **Allowlist bypass by design gap**: the code comment itself flags the missing enforcement, meaning any external caller with knowledge of the legacy JSON-RPC schema (method `web_api_trigger`, a `DonID`, and a message ID/timestamp) can have arbitrary payloads broadcast to all workflow DON nodes as a "trigger," analogous to the unauthenticated `fil_configure` call mutating shared snap state.
- **Shared/broadcast impact**: the request is fanned out to every node in `donConfig.Members`, so a single unauthenticated caller can influence behavior across the whole DON, echoing the Filecoin report's point about a malicious caller affecting "shared instance" state used by other consumers. [6](#0-5) 

### Recommendation
Apply the allowlist/authorization check (as already implemented in the v2 HTTP trigger handler's `authorizeRequest`) to the legacy `HandleLegacyUserMessage` path in `core/services/gateway/handlers/capabilities/handler.go` before forwarding requests to DON nodes, or remove/deprecate the legacy unauthenticated path entirely in favor of the authenticated v2 flow.

### Citations

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
