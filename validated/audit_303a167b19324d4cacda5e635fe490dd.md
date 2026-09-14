Based on my investigation, this specific bug class (a state-mutating action, like minting, that is missing an authorization/allowlist check while dependent, sibling endpoints in the same module do enforce one) has a valid analog in the gateway's legacy `WebAPIHandler`.

### Title
Missing allowlist/rate-limit enforcement before fan-out to DON in `HandleLegacyUserMessage` - ([File: core/services/gateway/handlers/capabilities/handler.go])

### Summary
`handler.HandleLegacyUserMessage`, the entry point for unprivileged, gateway-facing user requests targeting the `web_api_trigger` capability, forwards every structurally-valid request to all DON members without any workflow-owner allowlist or per-caller rate-limit check. The code explicitly marks this gap with `// TODO: apply allowlist and rate-limiting here` immediately before the method dispatch and fan-out logic, analogous to the reported `mintRebalancer` case where a state-changing entry point lacked the access-control check that its design intended.

### Finding Description
`HandleLegacyUserMessage` validates payload structure, timestamp freshness, and method name, but performs no authorization of the caller/workflow-owner before saving a callback and broadcasting the request to every DON member: [1](#0-0) 
The callback is registered and the message is forwarded unconditionally: [2](#0-1) 
This contrasts with the newer v2 HTTP trigger handler in the same codebase, which enforces JWT-based authorization and per-workflow rate limiting before dispatching to the DON: [3](#0-2) [4](#0-3) 
and the sibling node-outgoing path in the same legacy handler does apply a rate limiter (`h.nodeRateLimiter.Allow(nodeAddr)`), showing that access-control was clearly intended but omitted for the user-facing ingress path: [5](#0-4) 

### Impact Explanation
Any external caller able to reach the gateway's legacy message path can trigger `web_api_trigger` workflow executions on every member of a DON without being checked against a workflow/topic allowlist or throttled per caller, since the enforcement code was never implemented (only a `TODO` placeholder exists). This can lead to unauthorized triggering of workflow runs DON-wide and resource exhaustion (unbounded `savedCallbacks` growth /fan-out), which maps to "unauthorized job run" impact in the requested vulnerability classes.

### Likelihood Explanation
Likelihood depends on whether the legacy gateway message path (as opposed to the v2 JSON-RPC path) is still exposed in current deployments; the codebase keeps this handler and its dispatch (`multihandler.go`, `gateway.go`) actively wired, and the missing check is unconditional (not behind a feature flag), so likelihood is High if this legacy handler is reachable from the public/unprivileged gateway ingress.

### Recommendation
Implement the allowlist and rate-limiting check called out by the `TODO` in `HandleLegacyUserMessage` before registering the callback and fanning the request out to DON members — mirroring the JWT/authorized-key check and `checkRateLimit` pattern already implemented in `httpTriggerHandler.HandleUserTriggerRequest` (`authorizeRequest` / `checkRateLimit`).

### Proof of Concept
1. Send a well-formed `api.Message` with `Body.Method == MethodWebAPITrigger`, a valid (non-zero, non-stale) `Timestamp`, and a valid payload directly to the gateway's legacy handler entry point.
2. Because no allowlist or authorization check exists between the timestamp check and the method-name check, the message is accepted regardless of sender identity or workflow ownership.
3. The handler stores a callback and forwards the message to every DON member (`don.SendToNode`) unconditionally, achieving DON-wide workflow execution from an unauthenticated/unauthorized caller — confirmed by reading the omitted-check code path at [6](#0-5) .

Note: I could not fully verify, within available tool calls, whether the legacy gateway ingress path (as opposed to the v2 JSON-RPC/HTTP trigger path) is still exposed to external, unprivileged callers in current production configurations, or whether it has been fully superseded by the v2 handler. This should be confirmed before treating the finding as exploitable in production.

### Citations

**File:** core/services/gateway/handlers/capabilities/handler.go (L164-168)
```go
func (h *handler) handleWebAPIOutgoingMessage(ctx context.Context, msg *api.Message, nodeAddr string) error {
	h.lggr.Debugw("handling webAPI outgoing message", "messageId", msg.Body.MessageID, "nodeAddr", nodeAddr)
	if !h.nodeRateLimiter.Allow(nodeAddr) {
		return fmt.Errorf("rate limit exceeded for node %s", nodeAddr)
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

**File:** core/services/gateway/handlers/capabilities/v2/http_trigger_handler.go (L368-376)
```go
func (h *httpTriggerHandler) authorizeRequest(ctx context.Context, workflowID string, req *jsonrpc.Request[json.RawMessage], callback handlers.Callback) (*gateway_common.AuthorizedKey, error) {
	h.lggr.Debugw("authorizing request", "workflowID", workflowID, "requestID", req.ID)
	key, err := h.workflowMetadataHandler.Authorize(workflowID, req.Auth, req)
	if err != nil {
		h.handleUserError(ctx, req.ID, jsonrpc.ErrInvalidRequest, "Auth failure: "+err.Error(), callback)
		return nil, errors.Join(errors.New("auth failure"), err)
	}
	return key, nil
}
```
