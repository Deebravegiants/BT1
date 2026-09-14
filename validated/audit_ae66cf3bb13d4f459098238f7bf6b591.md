The strongest analog to the reported bug class (a callback/handler that doesn't validate the caller before performing consequential action) is in the internet-facing Chainlink Gateway's legacy WebAPI trigger handler.

### Title
Gateway's legacy WebAPI trigger handler forwards unauthenticated user requests to all DON nodes without allowlist or rate-limit checks - (File: core/services/gateway/handlers/capabilities/handler.go)

### Summary
The Gateway's `ProcessRequest` entry point accepts any externally-submitted JSON-RPC/legacy message and, for legacy requests, dispatches it to `handler.HandleLegacyUserMessage`, which forwards the message to every node in the DON without verifying that the caller (sender) is allowlisted or rate-limited, despite an explicit `// TODO: apply allowlist and rate-limiting here` marker in the code.

### Finding Description
The Gateway HTTP endpoint is reachable by any unprivileged client via `gateway.ProcessRequest` [1](#0-0) , which decodes the raw request and routes it to the appropriate handler based on `DonID`/method, then calls `h.HandleLegacyUserMessage(ctx, msg, callback)` for legacy requests [2](#0-1) .

In the WebAPI capabilities handler, `HandleLegacyUserMessage` validates payload structure (`Timestamp`, staleness) and the method name (must be `MethodWebAPITrigger`), but explicitly skips authorization/allowlist and rate-limit checks on the sender before forwarding the message to every node in the DON: [3](#0-2) 

This is unlike the equivalent v2 HTTP trigger handler (`httpTriggerHandler`), which performs JWT-based `authorizeRequest` against a list of `AuthorizedKey`s before dispatching to nodes [4](#0-3) , and the newer `triggerConnectorHandler.processTrigger`, which explicitly checks the message sender against per-topic allowed senders before processing [5](#0-4) . The legacy handler lacks this sender validation entirely — the TODO comment confirms it was never implemented, mirroring the audited bug class where a privileged callback/entry point trusts an unvalidated external initiator.

### Impact Explanation
Any unauthenticated/unprivileged client hitting the Gateway's public HTTP endpoint can submit a `web_api_trigger` legacy message that gets fanned out to every member node of the configured DON via `don.SendToNode`. Because sender identity/allowlist is never checked at this layer, a malicious actor can spoof triggers for workflows/capabilities they are not authorized to invoke, causing unauthorized workflow executions, node resource consumption, and potential downstream side effects (e.g., unauthorized job/workflow runs) — directly analogous to the "unvalidated initiator" root cause in the reported MarginTrading finding.

### Likelihood Explanation
The Gateway HTTP endpoint is internet-facing and designed to accept unauthenticated requests from external clients (that's its purpose for legacy webhook-style triggers); the only checks performed are payload shape/staleness/method name, all of which any attacker can trivially satisfy. Likelihood is high given the Gateway is intentionally exposed and the missing check is an explicit, acknowledged TODO rather than an accidental oversight in defensive code deeper in the stack.

### Recommendation
Implement sender allowlist and rate-limiting checks in `handler.HandleLegacyUserMessage` before forwarding messages to DON nodes, consistent with the pattern already used in `httpTriggerHandler.authorizeRequest` and `triggerConnectorHandler.processTrigger`. At minimum, reject or rate-limit requests whose sender/topic is not registered/authorized for the target capability before any `don.SendToNode` calls occur.

### Proof of Concept
1. Send a raw legacy-format JSON-RPC request to the Gateway's public endpoint with `DonID` set to a valid DON, `Method` set to `web_api_trigger`, and a valid, non-stale `Timestamp` in the payload — no authentication headers, JWT, or allowlisted sender required.
2. `gateway.ProcessRequest` routes it to the capabilities `handler.HandleLegacyUserMessage`.
3. The handler validates payload shape/timestamp/method only, then forwards the message to every DON node member via `don.SendToNode`, regardless of whether the caller is authorized for that topic/workflow — reproducing unauthorized-caller-triggered execution, analogous to an unvalidated flash-loan initiator draining a contract.

### Citations

**File:** core/services/gateway/gateway.go (L220-234)
```go
// Called by the server
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

**File:** core/services/gateway/handlers/capabilities/handler.go (L384-419)
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

**File:** core/capabilities/webapi/trigger/trigger.go (L167-200)
```go
func (h *triggerConnectorHandler) HandleGatewayMessage(ctx context.Context, gatewayID string, req *jsonrpc.Request[json.RawMessage]) error {
	msg, err := hc.ValidatedMessageFromReq(req)
	if err != nil {
		h.lggr.Errorw("error validating message from request", "err", err, "request", req)
		return nil
	}
	body := &msg.Body
	sender := ethCommon.HexToAddress(body.Sender)
	var payload webapicap.TriggerRequestPayload
	err = json.Unmarshal(body.Payload, &payload)
	if err != nil {
		h.lggr.Errorw("error decoding payload", "err", err)
		err = h.sendResponse(ctx, gatewayID, body, ghcapabilities.TriggerResponsePayload{Status: "ERROR", ErrorMessage: fmt.Errorf("error %s decoding payload", err.Error()).Error()})
		if err != nil {
			h.lggr.Errorw("error sending response", "err", err)
		}
		return nil
	}

	switch body.Method {
	case ghcapabilities.MethodWebAPITrigger:
		resp := h.processTrigger(ctx, gatewayID, body, sender, payload)
		var response ghcapabilities.TriggerResponsePayload
		if resp == nil {
			response = ghcapabilities.TriggerResponsePayload{Status: "ACCEPTED"}
		} else {
			response = ghcapabilities.TriggerResponsePayload{Status: "ERROR", ErrorMessage: resp.Error()}
			h.lggr.Errorw("Error processing trigger", "gatewayID", gatewayID, "body", body, "response", resp)
		}
		err = h.sendResponse(ctx, gatewayID, body, response)
		if err != nil {
			h.lggr.Errorw("Error sending response", "body", body, "response", response, "err", err)
		}
		return nil
```
