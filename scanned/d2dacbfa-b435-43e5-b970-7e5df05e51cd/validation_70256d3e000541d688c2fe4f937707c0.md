## Title
Gateway legacy web-api-trigger path forwards unauthenticated requests to all DON nodes without allowlist authorization - ([File: core/services/gateway/handlers/capabilities/handler.go])

### Summary
The gateway's legacy JSON-RPC message-handling path (`HandleLegacyUserMessage`) accepts an unauthenticated, unprivileged HTTP request and forwards it, unchecked, to every node of a DON as a `web_api_trigger` message. Unlike the modern JSON-RPC handlers in the same package tree (vault, HTTP-trigger-v2, confidential relay) which perform explicit authorization (`AuthorizeRequest`, JWT/allowlist checks) before dispatching to nodes, this legacy path only validates message structure/timestamp and explicitly documents the missing authorization with a `// TODO: apply allowlist and rate-limiting here` comment.

### Finding Description
`gateway.ProcessRequest` is the entry point invoked directly for any inbound HTTP request to the gateway [1](#0-0) . When the request carries a legacy `DonID` in its body, it is routed to `h.HandleLegacyUserMessage(ctx, msg, callback)` without any prior authentication [2](#0-1) .

Inside `HandleLegacyUserMessage`, the handler decodes the payload, checks that `payload.Timestamp` is non-zero and not stale, and rejects unsupported methods — but performs **no sender/allowlist/authorization check** before dispatching the request to every member of the DON: [3](#0-2) 

The comment on line 384, `// TODO: apply allowlist and rate-limiting here`, is a direct admission that the authorization step present in every sibling handler (vault's `AuthorizeRequest`, the HTTP-trigger-v2 `authorizeRequest`/JWT check, confidential relay's request flow) is missing here. Contrast this with the modern `HandleJSONRPCUserMessage` methods in the neighboring vault and HTTP-trigger-v2 handlers, which call an `Authorizer`/JWT verification before any node dispatch [4](#0-3) [5](#0-4) .

The corresponding unit test file even documents the gap explicitly: `// TODO: Validate Senders and rate limit check, pending question in trigger about where senders and rate limits are validated` [6](#0-5) .

### Impact Explanation
Any unprivileged client that can reach the gateway's public HTTP endpoint can submit a well-formed legacy `web_api_trigger` message with an arbitrary `DonID` and payload. The gateway will save a callback and broadcast the request to `don.SendToNode` for every member of that DON [7](#0-6) , causing DON nodes to process/act on an unauthorized trigger. This is a request-impersonation / allowlist-bypass condition: normal workflow triggers are supposed to be gated by an allowlist/authorization step, but this legacy path skips it entirely, letting an unauthenticated caller impersonate an authorized trigger sender for any DON it can address.

### Likelihood Explanation
The legacy path is reachable directly by decoding any inbound gateway HTTP request that includes a `DonID` — no special network position, node compromise, or operator access is required, only knowledge of a valid `DonID` and constructing a validly-formed `api.Message`. The path is exercised in tests as the primary legacy message flow, indicating it remains live/reachable rather than dead code.

### Recommendation
Add the same authorization step used by the other JSON-RPC handlers (allowlist/JWT-based `Authorizer.AuthorizeRequest`) to `HandleLegacyUserMessage` before saving the callback and dispatching to DON members, resolving the outstanding `// TODO: apply allowlist and rate-limiting here`.

### Proof of Concept
1. Craft a JSON-RPC/legacy gateway request body with a valid `DonID`, `Method: web_api_trigger`, and a non-zero, non-stale `Timestamp` in the `TriggerRequestPayload`.
2. Send it unauthenticated to the gateway's public HTTP endpoint, which is decoded and routed straight to `HandleLegacyUserMessage` [2](#0-1) .
3. Observe that the handler skips any allowlist/authorization check and forwards the request to every DON member via `don.SendToNode` [8](#0-7) , demonstrating that any unprivileged caller can trigger workflow executions on the DON without being an authorized sender.

### Citations

**File:** core/services/gateway/gateway.go (L220-235)
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

**File:** core/services/gateway/handlers/capabilities/handler_test.go (L365-366)
```go
	// TODO: Validate Senders and rate limit check, pending question in trigger about where senders and rate limits are validated
}
```
