### Title
Missing allowlist/rate-limit enforcement on legacy Web API gateway trigger path allows unauthenticated workflow triggering - (File: core/services/gateway/handlers/capabilities/handler.go)

### Summary
The Bisq v1 incident stemmed from a trade-protocol logic flaw where verification checks were bypassed, letting an attacker's client operate outside the intended authorization path. The analogous condition in this codebase is in the Chainlink Gateway's `capabilities` handler: the legacy user message ingress path, `HandleLegacyUserMessage`, contains an explicit `// TODO: apply allowlist and rate-limiting here` and performs no allowlist or authorization check before dispatching the request to every DON member node.

### Finding Description
`gateway.ProcessRequest` in `core/services/gateway/gateway.go` is the internet-facing entrypoint for external/unprivileged clients. Legacy requests (those carrying a `DonID`) are routed via `h.HandleLegacyUserMessage(ctx, msg, callback)` [1](#0-0) .

Inside `capabilities.handler.HandleLegacyUserMessage`, the code validates payload decoding, timestamp freshness, and method name, but explicitly skips authorization/allowlist checks, as marked by the code comment itself: [2](#0-1) 

After these checks, the message is forwarded unconditionally to every node in the DON: [3](#0-2) 

This contrasts with other, newer handlers in the same gateway package (e.g. `vault`, `confidentialrelay`, `v2/http_handler.go`) which implement `Authorizer`/allowlist-based `AuthorizeRequest` checks before processing requests, as seen for example in the Vault gateway handler's authorization pipeline (`requestProcessor.ProcessRequest` → `AuthorizeRequest`) [4](#0-3) . The `capabilities` legacy handler lacks any equivalent check — it is the one path in the gateway package where no allowlist/rate-limit gate exists on the caller.

### Impact Explanation
Any unprivileged/unauthenticated actor able to reach the gateway's HTTP-facing `ProcessRequest` endpoint with a legacy-format (DonID-bearing) `web_api_trigger` request can have that request broadcast to every node in the target DON without any allowlist verification, effectively bypassing the sender-authorization step that is enforced elsewhere in the gateway (e.g., Vault handler, per-node rate limiters in `v2/http_handler.go`). This is a request-impersonation / authorization-bypass class of bug: unauthenticated requests reach DON nodes and cause workflow-trigger execution, which is business-logic-equivalent to the Bisq incident where a bypass of verification let unauthorized requests proceed to fund-moving/critical operations.

### Likelihood Explanation
Likelihood is High for reachability: the legacy code path is live production code (not test-only, not mocked), directly reachable from `gateway.ProcessRequest`, which is the externally exposed HTTP handler for gateway user requests. There's no indication this legacy path is disabled by default; it's chosen automatically whenever an incoming request has a non-empty `msg.Body.DonID` (i.e., "legacy request"), which is a client-controlled field. No credential, key, or allowlist entry is required to hit this path — only the requirement to construct a validly-signed legacy message (message validity via `msg.Validate()` in `gateway.go`, which — based on available code — checks message signature and payload structure, not sender permission/allowlist membership).

### Recommendation
Implement the allowlist and rate-limiting enforcement referenced by the TODO comment in `HandleLegacyUserMessage` before the request is dispatched to DON nodes, mirroring the `Authorizer`/`AuthorizeRequest` pattern already used in `core/capabilities/vault/gw_handler.go` and the rate limiting present in `v2/http_handler.go`. Specifically, add a sender-allowlist (and optionally per-caller rate limit) check immediately after payload/timestamp validation and before `don.SendToNode` calls, rejecting unauthorized senders with an appropriate JSON-RPC error response consistent with other handlers.

### Proof of Concept
Not independently verified end-to-end (no access to a running gateway instance); the vulnerability is demonstrated by direct code inspection:
1. Craft a validly-signed legacy `api.Message` with `Body.DonID` set to a target DON, `Body.Method = "web_api_trigger"`, and a valid (non-stale) `webapicap.TriggerRequestPayload` timestamp.
2. Submit it to the gateway's `ProcessRequest` entrypoint (the exposed HTTP path invoking `gateway.ProcessRequest`) [5](#0-4) .
3. `HandleLegacyUserMessage` performs decoding/timestamp/method checks only, then forwards the request to all DON members without checking whether the sender is present in any allowlist [6](#0-5) .

Note: due to index size limits, I was not able to confirm whether `msg.Validate()` (called in `gateway.go` for legacy requests) performs any allowlist/sender-authorization checks beyond signature/structure validation. If `msg.Validate()` does include sender-allowlist verification elsewhere, this weakens the finding; I could not locate such logic within the indexed portions of `core/services/gateway/api`. A Devin session with full repository access would be needed to definitively confirm the contents of `msg.Validate()` and rule out authorization checks performed upstream.

### Citations

**File:** core/services/gateway/gateway.go (L221-272)
```go
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
	var h handlers.Handler
	var handlerKey string
	if msg == nil || msg.Body.DonID == "" {
		serviceName := jsonRequest.ServiceName()
		if handler, ok := g.serviceToMultiHandler[serviceName]; ok {
			h = handler
			handlerKey = serviceName
		} else if donID, ok := g.serviceNameToDonID[serviceName]; ok {
			// Fallback to legacy service name -> DON ID mapping
			if handler, ok := g.handlers[donID]; ok {
				h = handler
				handlerKey = donID
			}
		}
		if h == nil {
			return newError(jsonRequest.ID, api.HandlerError, "Service name not found: "+serviceName)
		}
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

**File:** core/services/gateway/handlers/capabilities/handler.go (L383-420)
```go
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
