## Title
Missing allowlist/rate-limit check in legacy web_api_trigger gateway handler allows unauthorized workflow trigger requests - (File: `core/services/gateway/handlers/capabilities/handler.go`)

### Summary
The `handler.HandleLegacyUserMessage` function in the gateway's legacy WebAPI capability handler forwards every incoming `web_api_trigger` request to all DON members without ever checking whether the caller/workflow is allowlisted, unlike its v2 counterpart which explicitly authorizes and rate-limits every trigger request before dispatch. This mirrors the reported `TermMaxRouter.borrowTokenFromGt` bug class: a specific code path forwards a privileged-adjacent action while skipping the whitelist/authorization check that sibling code paths consistently apply.

### Finding Description
`HandleLegacyUserMessage` validates payload decodability, checks the timestamp isn't stale, and checks the method is `MethodWebAPITrigger`, but then goes straight to broadcasting the request to every DON member via `don.SendToNode`, with an explicit TODO marking the missing check: [1](#0-0) [2](#0-1) 

By contrast, the v2 HTTP trigger path (`httpTriggerHandler.HandleUserTriggerRequest`) explicitly calls `h.authorizeRequest(...)` and `h.checkRateLimit(...)` before forwarding any request to the DON: [3](#0-2) 

The legacy handler is reachable directly from the internet-facing `gateway.ProcessRequest` entrypoint whenever a legacy (DON-ID-keyed) request is submitted, with no separate allowlist gate applied in `gateway.go` itself: [4](#0-3) 

### Impact Explanation
Any client able to reach the gateway's legacy HTTP endpoint can trigger a `web_api_trigger` message to be relayed to every node in the target DON, bypassing the per-workflow/per-owner authorization and rate-limiting that the equivalent v2 path enforces. Depending on how downstream nodes trust gateway-forwarded legacy trigger messages, this can result in unauthorized workflow executions being initiated by unvetted callers.

### Likelihood Explanation
The legacy code path remains registered and reachable (`HandleLegacyUserMessage` is dispatched by `gateway.ProcessRequest` for any request presented with a DON ID), so likelihood is high for any deployment where legacy-style requests are still accepted, since no additional caller-side privilege is required to hit this path — the check is literally marked `// TODO: apply allowlist and rate-limiting here`.

### Recommendation
Add the equivalent allowlist authorization and rate-limiting checks used by the v2 `httpTriggerHandler.authorizeRequest`/`checkRateLimit` methods to `HandleLegacyUserMessage` before forwarding the `MethodWebAPITrigger` request to DON members, or disable/reject the legacy path entirely if it is no longer intended to be supported.

### Proof of Concept
Not executed against a live environment; the missing-check condition is directly visible in source: `HandleLegacyUserMessage` performs no analog of `authorizeRequest`/`checkRateLimit` prior to the `don.SendToNode` fan-out loop, as shown in the cited lines above, while the parallel v2 handler enforces both checks for the same class of trigger request.

### Citations

**File:** core/services/gateway/handlers/capabilities/handler.go (L384-396)
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
```

**File:** core/services/gateway/handlers/capabilities/handler.go (L411-421)
```go
	h.mu.Lock()
	h.savedCallbacks[msg.Body.MessageID] = &savedCallback{id: msg.Body.MessageID, createdAt: time.Now(), Callback: callback}
	don := h.don
	h.mu.Unlock()

	// Send original request to all nodes
	for _, member := range h.donConfig.Members {
		err = errors.Join(err, don.SendToNode(ctx, member.Address, req))
	}
	return err
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
