### Title
Missing Allowlist/Authorization on Gateway `web_api_trigger` User Messages Allows Unauthorized DON-Wide Workflow Triggers - (File: core/services/gateway/handlers/capabilities/handler.go)

### Summary
The gateway's capabilities `handler.HandleLegacyUserMessage` accepts any incoming user JSON-RPC message targeting the `web_api_trigger` method and forwards it to every node in the DON with no authorization or allowlist check, mirroring the `createPosition()` issue where a privileged-looking operation was reachable by any unprivileged caller.

### Finding Description
`HandleLegacyUserMessage` validates message age, decodes the payload, and checks that the method equals `MethodWebAPITrigger`, but explicitly skips any authorization step, marked by the comment `// TODO: apply allowlist and rate-limiting here` immediately before the method dispatch [1](#0-0) . After that check it builds a validated request and broadcasts it to every DON member unconditionally: [2](#0-1) 

This is functionally analogous to the reported `createPosition()` bug: a state/behavior-changing entry point (`NFTPool.createPosition()` minting a position vs. here, triggering a workflow run on every DON node) that should be restricted to an authorized caller (Gateway contract vs. an allowlisted external initiator/user) but is instead reachable by any unauthenticated caller of the gateway's user-facing endpoint.

By contrast, the newer vault gateway path (`core/services/gateway/handlers/vault/handler.go`) enforces authorization via `requestProcessor.ProcessRequest` before dispatching to nodes [3](#0-2) , and the capabilities' `HandleJSONRPCUserMessage` path is outright disabled [4](#0-3) , showing that the maintainers recognize authorization is required on this class of handler — but the legacy `web_api_trigger` path was left with only a TODO instead of an enforced allowlist.

### Impact Explanation
Any unauthenticated client capable of reaching the gateway's HTTP/JSON-RPC user endpoint can submit a `web_api_trigger` message, which the gateway will unconditionally relay to every node in the target DON via `don.SendToNode` [5](#0-4) . This can trigger workflow executions DON-wide without any check that the caller is an authorized workflow owner/initiator, enabling unauthorized job/workflow runs, resource exhaustion of DON nodes, and potential downstream fund-moving or state-changing workflow actions depending on what workflows are registered — directly matching the "unauthorized job run" acceptance criterion.

### Likelihood Explanation
The `TODO: apply allowlist and rate-limiting here` comment directly next to the dispatch logic confirms that no allowlist enforcement currently exists on this path [6](#0-5) , and the function is reachable from any external gateway user message without prior authentication beyond basic payload/timestamp validation, making exploitation straightforward for any client that can reach the gateway.

### Recommendation
Implement the allowlist/rate-limiting check called out in the TODO before forwarding `web_api_trigger` messages to DON nodes in `HandleLegacyUserMessage`, mirroring the authorization pipeline already used by the vault gateway handler (`GatewayVaultRequestProcessor.ProcessRequest`) — validate the caller against a workflow/owner allowlist and apply per-sender rate limiting prior to `don.SendToNode` calls.

### Proof of Concept
Send a JSON-RPC/HTTP request to the gateway's legacy user endpoint with `msg.Body.Method == MethodWebAPITrigger` and a valid `payload.Timestamp` within the allowed age window, using arbitrary/unregistered sender credentials. Because no allowlist check exists prior to the `don.SendToNode` broadcast loop [7](#0-6) , the request will be relayed to every DON member, triggering workflow execution without any authorization.

### Citations

**File:** core/services/gateway/handlers/capabilities/handler.go (L295-297)
```go
func (h *handler) HandleJSONRPCUserMessage(_ context.Context, _ jsonrpc.Request[json.RawMessage], _ handlers.Callback) error {
	return errors.New("capabilities handler does not support JSON-RPC user messages")
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
