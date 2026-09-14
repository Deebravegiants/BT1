Good — this closes the gap. The node-side `webapiTrigger.processTrigger` in `core/capabilities/webapi/trigger/trigger.go` *does* enforce `trigger.allowedSenders[sender.String()]` and a per-sender rate limiter before dispatching to a workflow, mirroring the Moonwell pattern where the destination-side check (`_queueProposal`'s `intendedRecipient` check) exists on one path. The gateway-side `HandleLegacyUserMessage` in `core/services/gateway/handlers/capabilities/handler.go` is the "fast track" analog: it explicitly skips authorization (`// TODO: apply allowlist and rate-limiting here`) and fans the raw, unauthenticated HTTP payload out to every DON member. Because the actual allowlist enforcement happens downstream, node-side, per workflow, this is a defense-in-depth/DoS gap rather than a full bypass of authorization — matches the Moonwell finding's own caveat about exploitability being constrained. Given the strict validation bar (concrete auth/role bypass, secret disclosure, request impersonation, unauthorized job run or fund movement) and that the sender-allowlist check does still exist node-side before any workflow trigger fires, I can't confirm unauthorized job execution as a certain outcome — only that the gateway's fan-out and rate-limiting layer is missing, which is a weaker, DoS/resource-exhaustion-flavored analog, not a clean unauthorized-run bypass.

### Title
Gateway `HandleLegacyUserMessage` broadcasts unauthenticated user requests to entire DON without allowlist/rate-limit check - (File: core/services/gateway/handlers/capabilities/handler.go)

### Summary
The internet-facing gateway HTTP endpoint (`gateway.ProcessRequest`) forwards any unauthenticated `web_api_trigger` request directly to `handler.HandleLegacyUserMessage`, which — unlike the analogous vault handler path and unlike the node-side `webapiTrigger.processTrigger` — has no allowlist or rate-limiting check before broadcasting the message to every member of the DON.

### Finding Description
`gateway.ProcessRequest` decodes a raw, unauthenticated HTTP request and, for legacy requests, calls `h.HandleLegacyUserMessage(ctx, msg, callback)` directly [1](#0-0) . In `core/services/gateway/handlers/capabilities/handler.go`, `HandleLegacyUserMessage` validates payload structure, checks for a non-zero timestamp, and checks message staleness, but the only authorization-related step is an explicit unimplemented TODO immediately before dispatch: `// TODO: apply allowlist and rate-limiting here`, followed only by a method-name check [2](#0-1) . The handler then unconditionally forwards the original signed-by-nobody-yet request to every node in the DON: `for _, member := range h.donConfig.Members { err = errors.Join(err, don.SendToNode(ctx, member.Address, req)) }` [3](#0-2) .

By contrast, the equivalent vault gateway path enforces authorization before doing anything privileged, via `GatewayVaultRequestProcessor.ProcessRequest`'s `AuthorizeRequest` step [4](#0-3) , and node-side trigger dispatch in `webapiTrigger.processTrigger` enforces `trigger.allowedSenders[sender.String()]` and a per-sender rate limiter before ever forwarding an event into a workflow's execution channel [5](#0-4) . The gap in `HandleLegacyUserMessage` means every unauthenticated caller of the gateway's public HTTP endpoint causes the gateway to fan a full-size message payload out to N DON nodes, with no gateway-level allowlist or rate limiting gating that fan-out — the DON-level allowlist is only checked per-workflow, deep in `processTrigger`, after the message has already traversed the network to every node.

### Impact Explanation
This does not permit forging a workflow trigger from an unauthorized sender — `processTrigger`'s `allowedSenders` check still blocks the trigger from actually firing a workflow. The concrete impact is limited to resource consumption / amplification: an unauthenticated client can force the gateway to relay arbitrary-sender messages to every node in a DON without any per-caller rate limit at the gateway layer, unlike the vault path which authorizes before forwarding. This falls short of the "concrete authentication/role bypass, unauthorized job run, or fund movement" bar required, since the actual job-run gate (`allowedSenders`) is enforced downstream.

### Likelihood Explanation
High reachability — this is the default, unauthenticated code path for every legacy `web_api_trigger` HTTP request hitting the gateway's public user port, requiring no special conditions, keys, or trusted state, unlike the Moonwell analog which required a second chain's governance to emit exactly-matching calldata.

### Recommendation
Implement the outstanding TODO: add a gateway-level allowlist and/or rate limiter check in `HandleLegacyUserMessage` before forwarding to DON members, consistent with the model already used in the vault gateway handler (`GatewayVaultRequestProcessor.AuthorizeRequest`) and the node-side webapi trigger handler.

### Proof of Concept
Not applicable/exhaustive as a full PoC — verified via code inspection that `gateway.ProcessRequest` → `HandleLegacyUserMessage` (`core/services/gateway/handlers/capabilities/handler.go:341-421`) contains no allowlist/rate-limit gate before `don.SendToNode` fan-out, in contrast to the vault handler's `AuthorizeRequest` gate and the node-side `processTrigger`'s `allowedSenders`/`rateLimiter` gate.

**Note on confidence:** Given the strict validation criteria (concrete unauthorized job execution or auth bypass required) and that the sender-allowlist check does still exist node-side, this finding is best characterized as a missing defense-in-depth/rate-limiting control rather than a confirmed unauthorized job-run bypass. I was not able to fully trace whether any other middleware (e.g., at the HTTP server/connection-manager layer) imposes additional caller-level throttling before `gateway.ProcessRequest` is invoked; if such a layer exists, this weakens further to purely amplification/DoS.

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

**File:** core/services/gateway/handlers/capabilities/handler.go (L416-420)
```go
	// Send original request to all nodes
	for _, member := range h.donConfig.Members {
		err = errors.Join(err, don.SendToNode(ctx, member.Address, req))
	}
	return err
```

**File:** core/capabilities/vault/gw_handler.go (L180-211)
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
	case vaulttypes.MethodPublicKeyGet:
		response = h.handlePublicKeyGet(ctx, gatewayID, req)
	default:
		response = h.errorResponse(ctx, gatewayID, req, api.UnsupportedMethodError, errors.New("unsupported method: "+req.Method))
	}
```

**File:** core/capabilities/webapi/trigger/trigger.go (L106-119)
```go
	for _, trigger := range triggers {
		for _, topic := range topics {
			if trigger.allowedTopics[topic] {
				matchedWorkflows++
				if !trigger.allowedSenders[sender.String()] {
					err = fmt.Errorf("unauthorized Sender %s, messageID %s", sender.String(), body.MessageID)
					h.lggr.Debugw(err.Error())
					continue
				}
				if !trigger.rateLimiter.Allow(body.Sender) {
					err = fmt.Errorf("request rate-limited for sender %s, messageID %s", sender.String(), body.MessageID)
					continue
				}
				fullyMatchedWorkflows++
```
