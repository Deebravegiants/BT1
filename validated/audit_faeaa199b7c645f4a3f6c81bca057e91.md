This is the legacy `HandleLegacyUserMessage` path in `core/services/gateway/handlers/capabilities/handler.go` (lines 341-421). The code explicitly contains a `// TODO: apply allowlist and rate-limiting here` comment right before dispatching an unprivileged, internet-facing user request to all DON members — meaning no allowlist/authorization check gates who can trigger a WebAPI Trigger job run on the DON.### Title
Missing allowlist/authorization check lets any internet-facing client trigger DON workflow runs via the legacy WebAPI Trigger gateway handler - (File: core/services/gateway/handlers/capabilities/handler.go)

### Summary
The gateway's legacy `HandleLegacyUserMessage` path for `web_api_trigger` requests accepts any signed message from the public internet and forwards it to all DON nodes to trigger a workflow run, without performing any allowlist or authorization check on the sender. The code contains an explicit `// TODO: apply allowlist and rate-limiting here` marker at the exact point where such a check should exist but does not.

### Finding Description
`(*handler).HandleLegacyUserMessage` in `core/services/gateway/handlers/capabilities/handler.go` is the entry point invoked by the internet-facing `gateway.ProcessRequest` for legacy (DON-ID-based) requests [1](#0-0) . This handler performs payload decoding, a staleness/timestamp check, and a method-name check, but the only authorization-adjacent step is a comment stating that allowlist and rate-limiting enforcement is still a TODO, immediately followed by unconditional forwarding of the request to every DON member: [2](#0-1) 

Unlike the newer, structurally similar handlers in the same package family — e.g. the HTTP trigger handler (`h.authorizeRequest` via JWT/authorized-key verification) [3](#0-2)  and the vault handler (`h.requestProcessor.ProcessRequest` for allowlist authorization) [4](#0-3)  — this legacy capabilities handler has no equivalent authorization/allowlist gate before dispatching to the DON. Signature validation only proves the message is well-formed (`msg.Sign`/`common.ValidatedRequestFromMessage`), not that the sender is permitted to trigger this particular workflow/DON; any party who can reach the gateway's HTTP endpoint and produce a validly-signed `web_api_trigger` message (using any key, since there is no check against an authorized-key list) can cause the DON nodes to process the trigger and execute workflow logic.

This directly mirrors the reported bug class: a function/path that is expected to be reached only after upstream checks (an allowlist/authorization gate, analogous to the Router's checks/token transfer in the original Vader finding) is instead externally reachable and unconditionally performs the state-changing action (forwarding to DON nodes / initiating workflow runs) because the intended access-control check was never implemented — evidenced by the handler's own TODO comment.

### Impact Explanation
An unprivileged, unauthenticated internet client can invoke `web_api_trigger` legacy requests against any known/guessable DON ID and have the message unconditionally forwarded to every node of that DON, initiating workflow trigger processing without any check that the sender/key is authorized for the target workflow. This can lead to unauthorized job/workflow execution requests being consumed by the DON, and combined with rate-limiting also being un-implemented, allows spamming DON nodes with attacker-controlled trigger payloads that pass all format checks. This is a request-impersonation / allowlist-bypass style issue directly reachable from an unprivileged client.

### Likelihood Explanation
High. The path is reached directly from the public HTTP-facing `gateway.ProcessRequest` entry point for any legacy DON-ID-addressed request whose method is `web_api_trigger`; only trivial preconditions (well-formed payload, valid signature over the message, timestamp not too old) must be satisfied, none of which require possession of an authorized/allowlisted key. The absence of the check is self-documented in the code via the TODO comment, confirming it is not implemented rather than implemented elsewhere.

### Recommendation
Implement the allowlist/authorization check called out in the TODO before forwarding the message to DON nodes: verify that the signer/sender of the `web_api_trigger` request is authorized for the target DON/workflow (analogous to `WorkflowMetadataHandler.Authorize` used by the v2 HTTP trigger handler, or the `requestProcessor.ProcessRequest` authorization used by the vault handler), and add rate-limiting per sender/workflow before the `don.SendToNode` fan-out in `HandleLegacyUserMessage`.

### Proof of Concept
1. Craft a `web_api_trigger` legacy `api.Message` with `Body.DonID` set to a known/target DON ID, `Body.Method = "web_api_trigger"`, a valid (non-stale) `TriggerRequestPayload`, and sign it with any arbitrary private key (not one on any authorized-key list, since none is checked here).
2. Encode via `api.JSONRPCCodec{}.EncodeLegacyRequest` and POST it to the gateway's public user-facing HTTP endpoint (as done by `core/scripts/gateway/web_api_trigger/invoke_trigger.go`) [5](#0-4) .
3. `gateway.ProcessRequest` routes the request to the capabilities handler's `HandleLegacyUserMessage` [1](#0-0) .
4. The handler passes all format/timestamp/method checks and, absent any allowlist check (per the TODO), forwards the trigger to every member of the target DON [6](#0-5) , demonstrating that an arbitrary unauthorized signer can cause the DON to process a workflow trigger request.

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

**File:** core/services/gateway/handlers/capabilities/handler.go (L372-420)
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

**File:** core/services/gateway/handlers/capabilities/v2/http_trigger_handler.go (L95-109)
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

**File:** core/scripts/gateway/web_api_trigger/invoke_trigger.go (L98-112)
```go
	msg := &api.Message{
		Body: api.MessageBody{
			MessageID: *messageID,
			Method:    *methodName,
			DonID:     *donID,
			Payload:   payloadJSON,
		},
	}
	if err = msg.Sign(key); err != nil {
		fmt.Println("error signing message", err)
		return
	}

	codec := api.JSONRPCCodec{}
	rawMsg, err := codec.EncodeLegacyRequest(msg)
```
