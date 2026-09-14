### Title
Missing allowlist and rate-limiting authorization on legacy web_api_trigger gateway path allows unauthenticated fan-out to all DON nodes - ([File: core/services/gateway/handlers/capabilities/handler.go])

### Summary
The externally-reachable gateway `ProcessRequest` path routes legacy (non-JSON-RPC) requests bearing a `DonID` into `handler.HandleLegacyUserMessage`, which forwards the request to every member of the DON without performing the authorization check ("allowlist") that other message paths in the same codebase (e.g. the Vault gateway handler) explicitly implement before dispatch.

### Finding Description
`gateway.ProcessRequest` decodes an inbound raw request and, for legacy requests carrying a `DonID`, calls `h.HandleLegacyUserMessage(ctx, msg, callback)` directly after only structural validation (`msg.Validate()`), with no authorization/allowlist step gating which callers may reach a given DON: [1](#0-0) 

Inside `HandleLegacyUserMessage`, after payload decoding, timestamp/staleness, and method checks, the code contains an explicit unimplemented gate before dispatching the message to every DON node: [2](#0-1) 

The comment `// TODO: apply allowlist and rate-limiting here` confirms that the intended per-caller authorization/allowlist check that should occur before this dispatch is not implemented on this path, unlike the analogous Vault gateway pipeline, which mandates `AuthorizeRequest` (allowlist-based or JWT-based) before any request is forwarded/stamped: [3](#0-2)  and [4](#0-3) .

This is architecturally analogous to CVE-2023-43644 (sing-box SOCKS): a request-processing state machine that should gate on an authorization check before acting on a client-supplied command, but instead proceeds to the privileged action (here: fan-out of a user-controlled message to every capability-hosting DON node) without that gate being enforced.

### Impact Explanation
Any unprivileged caller able to reach the gateway's public `ProcessRequest` endpoint with a well-formed legacy message (`DonID` set, valid signature per `msg.Validate()`/`ValidatedRequestFromMessage`, fresh timestamp, method `web_api_trigger`) can have that message broadcast to every node in the target DON, since no allowlist/rate-limit is applied at this layer. This crosses the criterion of "allowlist or quota bypass" and "unauthorized job run" — the request reaches DON nodes and triggers workflow execution paths without the intended caller-level gating that the codebase otherwise enforces (e.g., Vault's allowlist), and without the per-node rate limiting that only occurs on the *outgoing* (node→client) side (`nodeRateLimiter.Allow` in `handleWebAPIOutgoingMessage`), not on inbound triggers.

### Likelihood Explanation
The vulnerable code path (`HandleLegacyUserMessage`) is reachable directly from the internet-facing gateway `ProcessRequest` entry point with no additional privilege beyond producing a validly-signed legacy message, and the missing check is explicitly flagged as a TODO in the shipped code, indicating the gap is a known, currently-unaddressed gap rather than a hypothetical one.

### Recommendation
Implement the allowlist/rate-limiting check referenced by the TODO in `HandleLegacyUserMessage` before the loop that calls `don.SendToNode` for each DON member, mirroring the `AuthorizeRequest` gating pattern used in the Vault gateway pipeline (`core/capabilities/vault/gateway_vault_request_processor.go`, `core/capabilities/vault/allow_list_based_auth.go`) so that only authorized senders/methods can trigger fan-out to DON nodes.

### Proof of Concept
1. Craft a legacy `api.Message` with `Body.DonID` set to a valid, in-service DON ID, `Body.Method = "web_api_trigger"`, a fresh `Timestamp`, and a signature that satisfies `msg.Validate()` / `ValidatedRequestFromMessage` structural/signature checks.
2. Submit it to the gateway's public HTTP endpoint that calls `gateway.ProcessRequest`.
3. Observe in `gateway.go` that the message is routed to `h.HandleLegacyUserMessage` solely based on `DonID` presence, with no allowlist check performed: [1](#0-0) 
4. Observe in `handler.go` that after payload/timestamp/method checks, the request is sent to **all** DON members via `don.SendToNode` without any allowlist/rate-limit gate, as marked by the TODO comment: [2](#0-1) 

**Note on confidence/uncertainty:** I was unable to fully inspect `msg.Validate()` and `common.ValidatedRequestFromMessage` (in `core/services/gateway/handlers/common/message_util.go` and `core/services/gateway/api/message.go`) within the available iterations to confirm exactly what authentication/authorization semantics (e.g., sender identity binding, DON membership check) those functions already provide. It is possible those functions perform some sender-authentication that partially mitigates this issue (e.g., verifying the message signature belongs to a registered client), but the explicit `// TODO: apply allowlist and rate-limiting here` comment strongly suggests the intended caller/method-level authorization gate is not yet implemented on this path, distinct from whatever cryptographic signature check may already exist.

### Citations

**File:** core/services/gateway/gateway.go (L253-265)
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

**File:** core/capabilities/vault/gw_handler.go (L180-206)
```go
func (h *GatewayHandler) HandleGatewayMessage(ctx context.Context, gatewayID string, req *jsonrpc.Request[json.RawMessage]) (err error) {
	reqLggr := h.requestLogger(req, gatewayID)
	reqLggr.Debugw("received message from gateway", "req", req)

	var response *jsonrpc.Response[json.RawMessage]
	var authResult *AuthResult

	switch req.Method {
	case vaulttypes.MethodSecretsCreate, vaulttypes.MethodSecretsUpdate:
		publicKey, pkErr := h.getMasterPublicKey(ctx)
		if pkErr != nil {
			response = h.gatewayErrorResponse(ctx, gatewayID, req, pkErr)
			break
		}
		authorized, pipelineErr := h.requestProcessor.ProcessRequest(ctx, req, publicKey)
		if pipelineErr != nil {
			response = h.gatewayErrorResponse(ctx, gatewayID, req, pipelineErr)
			break
		}
		authResult = authorized.AuthResult
	case vaulttypes.MethodSecretsDelete, vaulttypes.MethodSecretsList:
		authorized, pipelineErr := h.requestProcessor.ProcessRequest(ctx, req, nil)
		if pipelineErr != nil {
			response = h.gatewayErrorResponse(ctx, gatewayID, req, pipelineErr)
			break
		}
		authResult = authorized.AuthResult
```

**File:** core/capabilities/vault/gateway_vault_request_processor.go (L260-276)
```go
func (p *GatewayVaultRequestProcessor) authorizeAndStamp(
	ctx context.Context,
	req *jsonrpc.Request[json.RawMessage],
	stamp func(prefixedRequestID string) error,
) (*AuthorizedGatewayVaultRequest, error) {
	incomingOwner := ""
	if idx := strings.Index(req.ID, vaulttypes.RequestIDSeparator); idx != -1 {
		incomingOwner = req.ID[:idx]
	}

	p.lggr.Debugw("authorizing gateway vault request", "method", req.Method, "requestID", req.ID)
	authResult, err := p.authorizer.AuthorizeRequest(ctx, *req)
	if err != nil {
		authErr := fmt.Errorf("request not authorized: %w", err)
		p.lggr.Errorw("gateway vault request authorization failed", "method", req.Method, "requestID", req.ID, "hasAuth", req.Auth != "", "incomingOwner", incomingOwner, "error", authErr)
		return nil, authErr
	}
```
