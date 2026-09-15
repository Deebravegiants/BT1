### Title
Legacy WebAPI trigger gateway handler forwards unauthenticated user requests to all DON nodes without allowlist/sender authorization - ([File: core/services/gateway/handlers/capabilities/handler.go])

### Summary
The legacy `web_api_trigger` gateway message path in `handler.HandleLegacyUserMessage` accepts an inbound message from an external HTTP client and forwards it to every member of the DON without performing any allowlist, sender-authorization, or rate-limit check, unlike the newer v2 HTTP trigger path which explicitly authorizes the request against a workflow's registered key before dispatch.

### Finding Description
`HandleLegacyUserMessage` in `core/services/gateway/handlers/capabilities/handler.go:341-421` decodes the payload, checks only timestamp staleness and method name, then immediately fans the request out to every DON member: [1](#0-0) 

The code contains an explicit acknowledgement of the missing control:
```go
// TODO: apply allowlist and rate-limiting here
if msg.Body.Method != MethodWebAPITrigger {
``` [2](#0-1) 

This is the same bug class as the Avo advisory: an endpoint that performs a privileged/impactful action (here, dispatching a workflow trigger request to every node in a DON) before the documented/expected authorization check (`allowlist`/sender validation) is applied — mirroring how `Avo::AttachmentsController#create` persisted and attached blobs before invoking `upload_<field>?`/`update?` policy checks.

By contrast, the newer `v2` HTTP trigger handler for the same conceptual operation does enforce authorization before any dispatch, calling `h.workflowMetadataHandler.Authorize(...)` and failing closed on error: [3](#0-2) [4](#0-3) 

The corresponding test suite for the legacy path also documents the gap as an open, unresolved question rather than a verified safe design:
```go
// TODO: Validate Senders and rate limit check, pending question in trigger about where senders and rate limits are validated
``` [5](#0-4) 

### Impact Explanation
If reachable, an unauthenticated or unprivileged HTTP client hitting the gateway's legacy `web_api_trigger` method could cause the gateway to broadcast a crafted trigger request to all nodes of a DON — i.e., an unauthorized job/workflow run — bypassing whatever authorization mechanism (allowlist, sender/key validation) is expected to gate this operation, analogous to the Avo report's "unauthorized job run" / field-level-policy bypass class.

### Likelihood Explanation
I was not able to fully confirm, within the available tool budget, whether the legacy `web_api_trigger` message path is still reachable from genuinely unprivileged external HTTP clients in current deployments, or whether it has been effectively superseded/gated by the v2 HTTP trigger handler (which is explicitly authorized) and other upstream request validation in `gateway.ProcessRequest` (e.g., `msg.Validate()`, DON-ID routing) that may implicitly restrict senders. The code comments themselves flag this as an open, unresolved item ("pending question ... where senders and rate limits are validated"), so likelihood is uncertain and requires further investigation of `msg.Validate()` and the message signature/sender verification path before treating this as confirmed exploitable.

### Recommendation
- Implement the TODO in `HandleLegacyUserMessage`: enforce sender allowlisting and rate limiting before forwarding messages to DON members, consistent with the authorization-before-action pattern used in the v2 `httpTriggerHandler.HandleUserTriggerRequest`.
- Confirm whether `msg.Validate()` / message signature checks already constrain the sender to an authorized set; if not, add explicit authorization prior to `don.SendToNode` calls.
- Consider deprecating/removing the legacy path once the v2 authorized path fully supersedes it, to eliminate the divergent-authorization footgun (mirrors Avo's recommendation to make the direct/legacy endpoint consistent with the well-authorized codepath).

### Proof of Concept
Not independently constructed/verified in this pass — would require confirming the gateway/DON wiring that routes the legacy `web_api_trigger` JSON-RPC message to `HandleLegacyUserMessage` and testing whether an unsigned/unauthorized sender's request is dispatched to DON nodes (as suggested by the existing unit test comment at `core/services/gateway/handlers/capabilities/handler_test.go:365-366` noting this validation is not yet exercised by tests).

### Citations

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

**File:** core/services/gateway/handlers/capabilities/handler_test.go (L365-366)
```go
	// TODO: Validate Senders and rate limit check, pending question in trigger about where senders and rate limits are validated
}
```
