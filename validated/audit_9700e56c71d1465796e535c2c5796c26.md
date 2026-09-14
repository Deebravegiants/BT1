## Finding: Unauthenticated Web API Trigger Forwarding to DON Nodes (missing allowlist check)

### Title
Legacy Gateway `web_api_trigger` messages are forwarded to DON nodes without authentication/allowlist checks - (File: core/services/gateway/handlers/capabilities/handler.go)

### Summary
The CVE describes a TLS 1.3 implementation bug where application data is accepted and processed before the peer's identity/authorization (client certificate `Finished`) has been verified, allowing a client to skip authentication and still have its data processed by the server. The closest reachable analog in this repository is the Gateway's legacy capabilities handler, which forwards an unprivileged HTTP client's `web_api_trigger` payload to every node of a DON *before any allowlist or authorization check is performed* — a check explicitly marked as missing via a `TODO` comment.

### Finding Description
`gateway.ProcessRequest` accepts requests over the public gateway HTTP endpoint. For "legacy" requests (those carrying a `DonID`), it only validates the envelope shape (`msg.Validate()`) and resolves the target handler by `DonID`, then calls straight into the handler: [1](#0-0) 

That handler, `handler.HandleLegacyUserMessage` in the capabilities package, decodes the payload, checks a timestamp bound, and confirms the method is `MethodWebAPITrigger` — but performs **no sender authentication, allowlist, or rate-limiting check** before forwarding the request body to every node in the DON: [2](#0-1) 

The comment directly above the method dispatch makes the gap explicit:
```go
// TODO: apply allowlist and rate-limiting here
if msg.Body.Method != MethodWebAPITrigger {
``` [3](#0-2) 

After this check, the handler saves a callback keyed by the caller-controlled `MessageID` and forwards the caller's raw request to `don.SendToNode` for **every member of the DON**: [4](#0-3) 

This mirrors the CVE's root cause structurally: data from an unauthenticated/unverified party (`ApplicationData` in TLS, or here the HTTP-facing `web_api_trigger` message) is accepted and acted upon (forwarded into the trusted DON) *before* the identity/authorization step that is supposed to gate it. In the vault gateway handler, by contrast, the same class of request is explicitly gated by an authorization pipeline (`AuthorizeRequest` before any processing/forwarding), as seen in `core/capabilities/vault/gateway_vault_request_processor.go` and `core/services/gateway/handlers/vault/handler.go` — showing the intended pattern that this legacy capabilities path fails to follow.

### Impact Explanation
Any unprivileged client capable of reaching the Gateway's public HTTP endpoint can submit a legacy `web_api_trigger` message for any `DonID` known to the gateway and have it delivered directly to every node in that DON, without being on any allowlist. Depending on how the receiving DON's `WebAPITrigger` capability processes incoming triggers, this could allow unauthorized workflow triggering — i.e., "unauthorized job run" from an unprivileged actor, which is explicitly in-scope per the validation rules.

### Likelihood Explanation
High: the vulnerable path is directly reachable from an unauthenticated/unprivileged HTTP client hitting the gateway's legacy JSON-RPC endpoint; no signature, session, or allowlist check is interposed before the message is dispatched to `HandleLegacyUserMessage`, and the missing-check is explicitly flagged by the maintainers' own `TODO` comment rather than being a subtle omission.

### Recommendation
Add sender authentication and allowlist enforcement for `MethodWebAPITrigger` (and the other legacy methods) in `HandleLegacyUserMessage`, mirroring the `Authorizer`/allowlist pattern already used in the vault gateway handler (`core/capabilities/vault/gateway_vault_request_processor.go`), before saving the callback and forwarding to `don.SendToNode`.

### Proof of Concept
1. Identify a live `DonID` served by a Gateway instance (these are often discoverable/config-known).
2. Send a legacy JSON-RPC request to the gateway's public HTTP endpoint with `Body.DonID` set to that DON and `Body.Method = "web_api_trigger"`, with an arbitrary `Timestamp` within `MaxAllowedMessageAgeSec` and an arbitrary trigger `Payload`.
3. Observe in `core/services/gateway/handlers/capabilities/handler.go:HandleLegacyUserMessage` that the message passes the method/timestamp checks and is forwarded via `don.SendToNode` to every DON member — with no allowlist or sender-authorization check ever consulted, confirming the request reaches the DON without authorization gating.

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
