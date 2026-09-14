This confirms the finding: `gateway.ProcessRequest` at `core/services/gateway/gateway.go:220-295` accepts unauthenticated HTTP requests from external clients and dispatches legacy requests directly to `h.HandleLegacyUserMessage(ctx, msg, callback)` with no authentication or allowlist check performed by the gateway core itself [1](#0-0) . In `capabilities.handler.HandleLegacyUserMessage`, the only checks performed are payload decoding, a timestamp/staleness check, and a method-name check — there is an explicit `// TODO: apply allowlist and rate-limiting here` immediately before the request is forwarded to every DON node [2](#0-1) .

### Title
Missing Allowlist/Access Control on Gateway Legacy WebAPI Trigger Handler - (File: core/services/gateway/handlers/capabilities/handler.go)

### Summary
`handler.HandleLegacyUserMessage` in the WebAPI capabilities gateway handler forwards any unauthenticated, internet-facing `web_api_trigger` request to every node in the DON without checking any allowlist of authorized senders, mirroring the reported Comet `set_freeze_status` pattern where a state-changing/dispatch action lacked an access-control check before executing.

### Finding Description
The gateway's public HTTP entrypoint `gateway.ProcessRequest` routes any legacy-format request (only requiring a `DonID`) straight to `handler.HandleLegacyUserMessage` [1](#0-0) . Inside that handler, the code validates payload structure, checks message freshness, and validates the method name equals `MethodWebAPITrigger`, but explicitly skips authorization: the comment `// TODO: apply allowlist and rate-limiting here` sits directly before the method-name check and before the request is fanned out to every DON member via `don.SendToNode` [3](#0-2) . Unlike the sibling vault and v2 HTTP-trigger handlers, which run requests through `AuthorizeRequest`/JWT or allowlist-based authorizers before dispatch (`authorizeRequest` in `core/capabilities/vault/authorizer.go` and `authorizeRequest` in `core/services/gateway/handlers/capabilities/v2/http_trigger_handler.go:106`), this legacy handler has no equivalent gate [4](#0-3) [5](#0-4) .

### Impact Explanation
Any unauthenticated client able to reach the gateway's user-facing HTTP endpoint can craft a legacy JSON message with a valid `DonID` and `web_api_trigger` method and have it broadcast to every node of the target DON, triggering downstream workflow execution logic on the nodes without being an allowlisted/authorized sender. This is analogous to the Comet bug: a privileged/gated operation (dispatching triggers to the DON) executable by any caller due to a missing access-control check, rather than a functionally-scoped bypass elsewhere in the stack.

### Likelihood Explanation
Likelihood is high for any deployment still routing traffic through this legacy handler path, since the missing check is unconditional (not behind a feature flag) and is reachable directly from the internet-facing gateway HTTP server with no precondition beyond a syntactically valid, non-stale message.

### Recommendation
Implement allowlist/authorization enforcement in `HandleLegacyUserMessage` before dispatching to `don.SendToNode`, consistent with the pattern already used in the vault (`Authorizer.AuthorizeRequest`) and v2 HTTP trigger (`authorizeRequest`) handlers — verify the sender/workflow owner against a DON- or workflow-specific allowlist and reject/rate-limit unauthorized senders prior to fan-out.

### Proof of Concept
1. Send an HTTP POST to the gateway's user port with a legacy-format JSON-RPC message containing a valid `don_id` matching a configured DON, `method: "web_api_trigger"`, and a `payload` with a fresh `Timestamp`.
2. Because `HandleLegacyUserMessage` performs no allowlist check (see the TODO at line 384), the message passes all checks and is forwarded via `don.SendToNode` to every DON member, as shown in the loop at `core/services/gateway/handlers/capabilities/handler.go:417-419` [6](#0-5) .

Note: I was not able to verify from the indexed code whether an allowlist check is enforced at a layer above `gateway.ProcessRequest` (e.g., in HTTP server middleware or connection manager) that might mitigate this in practice; the `gateway.go` and `gw_net` HTTP server code available did not show such a check, but full verification would require inspecting the HTTP server/middleware setup in a live Devin session with complete file access.

### Citations

**File:** core/services/gateway/gateway.go (L253-272)
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
```

**File:** core/services/gateway/handlers/capabilities/handler.go (L371-420)
```go

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

**File:** core/capabilities/vault/authorizer.go (L121-128)
```go
func (a *authorizer) authorizeRequest(ctx context.Context, req jsonrpc.Request[json.RawMessage]) (*AuthResult, error) {
	// Requests without req.Auth continue using the allowlist-based path for backwards compatibility.
	// Existing clients do not populate the auth field yet, so treating an empty value as JWT would break them.
	if req.Auth == "" {
		return a.authorizeAllowListBasedAuth(ctx, req)
	}
	return a.authorizeJWTBasedAuth(ctx, req)
}
```

**File:** core/services/gateway/handlers/capabilities/v2/http_trigger_handler.go (L106-109)
```go
	key, err := h.authorizeRequest(ctx, workflowID, req, callback)
	if err != nil {
		return err
	}
```
