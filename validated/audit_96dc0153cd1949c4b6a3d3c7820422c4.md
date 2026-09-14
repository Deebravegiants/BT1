### Title
Missing Allowlist/Rate-Limit Validation on Legacy Web API Gateway Trigger Messages Allows Unrestricted Fan-out to All DON Nodes - ([File: core/services/gateway/handlers/capabilities/handler.go])

### Summary
`handler.HandleLegacyUserMessage` in the Web API capabilities gateway handler is reachable directly from an unprivileged HTTP client via `gateway.ProcessRequest`, but performs no sender/workflow allowlist check and no rate-limiting before broadcasting the incoming trigger request to every node in the DON.

### Finding Description
`gateway.ProcessRequest` decodes an incoming JSON-RPC request from an untrusted HTTP caller and, for legacy requests (those carrying a `DonID`), dispatches directly to the resolved handler's `HandleLegacyUserMessage` with no authorization step in between: [1](#0-0) 

For the Web API capabilities handler, `HandleLegacyUserMessage` validates payload shape, timestamp/staleness, and method name, but the code contains an explicit unaddressed TODO immediately before it forwards the request to nodes: [2](#0-1) 

After these checks, the handler stores a callback and unconditionally sends the client-supplied request to **every** member node of the DON, with no verification that the caller (sender/workflow owner) is authorized to trigger this DON or that the caller has not exceeded a request quota: [3](#0-2) 

This directly matches the reported bug class ("Missing Input Validation" — absence of existence/authorization checks before a privileged, state-changing action) mapped onto an unprivileged-actor-reachable gateway code path: the caller-supplied request is trusted and fanned out to DON nodes without any allowlist or quota gate, unlike the analogous v2 HTTP trigger path (`httpTriggerHandler.HandleUserTriggerRequest`), which explicitly performs `authorizeRequest` and `checkRateLimit` before dispatch: [4](#0-3) 

Note that `nodeRateLimiter` in this handler is only applied to the reverse direction — outbound HTTP messages initiated by DON nodes (`handleWebAPIOutgoingMessage`) — not to inbound user-triggered requests: [5](#0-4) 

### Impact Explanation
Any unprivileged client capable of reaching the gateway's public HTTP endpoint can submit an arbitrary well-formed `web_api_trigger` legacy message for a given `DonID` and have it broadcast to all nodes of that DON without any allowlist/authorization check confirming the caller is entitled to trigger that DON's workflow, and without any per-caller rate limiting. This can lead to unauthorized job/workflow triggering across the DON and to resource-exhaustion/DoS against DON nodes, since the gateway itself imposes no throttling on this inbound path.

### Likelihood Explanation
The path is reachable directly from `gateway.ProcessRequest`, which is the top-level entrypoint invoked by the gateway's HTTP server for any external caller; no authentication beyond message-shape validation (`msg.Validate()`) is required before dispatch to `HandleLegacyUserMessage`. The missing-check TODO is explicit in the source, and the corresponding v2 implementation already demonstrates the expected authorize/rate-limit calls are both feasible and considered necessary, indicating the legacy path is a known, still-open gap rather than an intentional design choice.

### Recommendation
Add caller/workflow authorization (allowlist check) and per-sender rate limiting to `HandleLegacyUserMessage` prior to storing the callback and calling `don.SendToNode`, mirroring the `authorizeRequest`/`checkRateLimit` pattern used in `httpTriggerHandler.HandleUserTriggerRequest`. At minimum, reject unauthorized/non-allowlisted senders and enforce a quota before any fan-out to DON nodes.

### Proof of Concept
1. Craft a signed legacy JSON-RPC request with `Body.Method = "web_api_trigger"`, a valid `TriggerRequestPayload` (fresh `Timestamp`), and a target `DonID` for a DON the caller is not authorized to trigger.
2. Submit it to the gateway's HTTP endpoint, which routes to `gateway.ProcessRequest` → `handler.HandleLegacyUserMessage` (as exercised by `TestHandlerReceiveHTTPMessageFromClient` in `core/services/gateway/handlers/capabilities/handler_test.go`).
3. Observe that the request passes payload/timestamp/method checks and is forwarded via `don.SendToNode` to every member of `h.donConfig.Members`, with no allowlist or rate-limit rejection, confirming any caller able to reach the gateway can trigger fan-out to all DON nodes.

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

**File:** core/services/gateway/handlers/capabilities/handler.go (L164-168)
```go
func (h *handler) handleWebAPIOutgoingMessage(ctx context.Context, msg *api.Message, nodeAddr string) error {
	h.lggr.Debugw("handling webAPI outgoing message", "messageId", msg.Body.MessageID, "nodeAddr", nodeAddr)
	if !h.nodeRateLimiter.Allow(nodeAddr) {
		return fmt.Errorf("rate limit exceeded for node %s", nodeAddr)
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

**File:** core/services/gateway/handlers/capabilities/handler.go (L411-420)
```go
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
