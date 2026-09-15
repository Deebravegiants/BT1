### Title
No access control (allowlist) enforcement on the gateway's legacy `web_api_trigger` user message handler - ([File: core/services/gateway/handlers/capabilities/handler.go])

### Summary
The gateway's internet-facing user endpoint accepts legacy `web_api_trigger` messages and forwards them to every member node of the DON without any allowlist or authorization check, mirroring the reported class of bug where a function intended to be gated behind access control is reachable and actionable by any unprivileged caller.

### Finding Description
Incoming HTTP requests to the gateway's `UserServerConfig` endpoint are decoded and dispatched via `gateway.ProcessRequest`, which for legacy (DON-ID-addressed) requests calls `h.HandleLegacyUserMessage` directly with no caller authentication step in between [1](#0-0) .

Inside `HandleLegacyUserMessage`, the code validates payload shape, message staleness, and method name, but the access-control step is explicitly missing — marked by a `TODO` comment immediately before the request is validated and broadcast to every DON member:

```go
// TODO: apply allowlist and rate-limiting here
if msg.Body.Method != MethodWebAPITrigger {
    ...
}
req, err := common.ValidatedRequestFromMessage(msg)
...
for _, member := range h.donConfig.Members {
    err = errors.Join(err, don.SendToNode(ctx, member.Address, req))
}
``` [2](#0-1) 

This is functionally identical to the reported bug class: a downstream function (`receiveFlashLoan` in the manager contract) that was assumed to be gated by an upstream caller's access-control modifiers, but is in fact reachable and actionable with attacker-controlled input because the actual authorization check was never implemented on the path that matters. Here, `HandleLegacyUserMessage` is the entry point reachable directly from the public, unauthenticated `/user` HTTP endpoint [3](#0-2) , and the comment itself confirms the intended allowlist/rate-limit check is not present, unlike the newer JSON-RPC vault/HTTP-trigger handlers which do call an explicit `authorizeRequest`/`AuthorizeRequest` step before acting [4](#0-3)  and [5](#0-4) .

### Impact Explanation
Because there is no allowlist/authorization enforcement on `HandleLegacyUserMessage`, any unauthenticated client that can reach the gateway's public user endpoint can submit a `web_api_trigger` message that gets forwarded to every node in the DON, triggering workflow execution logic on the node side without any check that the caller is permitted to invoke that workflow/DON. This corresponds to "unauthorized job run" impact — an unprivileged actor causing DON nodes to process/act on a request that was never vetted for legitimacy at the gateway layer, matching the severity class (Medium) of the original finding.

### Likelihood Explanation
The endpoint is internet-facing by design (the gateway `UserServerConfig` HTTP port is meant to receive external client traffic) and the missing check is explicitly flagged by the developers themselves via the `TODO` comment, indicating the gap is a known, real, currently-shipped condition rather than a hypothetical — increasing the likelihood that it is exploitable by any external, unprivileged client that can reach the gateway.

### Recommendation
Implement the allowlist/rate-limiting check referenced by the `TODO` comment in `HandleLegacyUserMessage` before forwarding the request to DON members, consistent with the authorization pattern already used by the newer JSON-RPC handlers (`authorizeRequest` in `http_trigger_handler.go`, `ProcessRequest`/`AuthorizeRequest` in the vault handler). At minimum, reject unallowlisted senders/messages and enforce rate limiting per-sender before any `don.SendToNode` call.

### Proof of Concept
1. Stand up a gateway with the legacy capabilities handler configured for a DON.
2. From an unauthenticated client, POST a JSON payload to the gateway's `UserServerConfig` path with `Method: web_api_trigger`, a valid `Timestamp`, and a well-formed `TriggerRequestPayload`.
3. Observe that `HandleLegacyUserMessage` accepts the message (no allowlist check performed) and forwards it via `don.SendToNode` to all `h.donConfig.Members`, as shown at [6](#0-5) , with no verification that the sender was ever authorized to invoke that DON/workflow.

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

**File:** core/scripts/gateway/sample_config_tls.toml (L1-13)
```text
[UserServerConfig]
Port = 8088
TLSEnabled = true
TLSCertPath = "certificate.pem"
TLSKeyPath = "key.pem"
Path = "/user"
ContentTypeHeader = "application/jsonrpc"
ReadTimeoutMillis = 1000
WriteTimeoutMillis = 1000
RequestTimeoutMillis = 1000
MaxRequestBytes = 10_000
CORSEnabled = false
CORSAllowedOrigins = []
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
