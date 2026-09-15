Based on my investigation, I found a concrete gap in the internet-facing gateway path: the legacy WebAPI trigger handler forwards unprivileged, unauthenticated user requests to every DON node without any allowlist or sender-quota check, despite the code explicitly flagging this as missing.

### Title
Missing allowlist/rate-limit enforcement on gateway legacy WebAPI trigger requests allows unauthenticated broadcast to all DON nodes - ([File: core/services/gateway/handlers/capabilities/handler.go])

### Summary
`HandleLegacyUserMessage` in the gateway's WebAPI capabilities handler is the entry point for legacy (non-JSON-RPC) `web_api_trigger` requests coming from the internet-facing gateway HTTP endpoint. It validates payload structure, timestamp, and method name, but has an explicit `// TODO: apply allowlist and rate-limiting here` comment right before it forwards the request to every member of the DON, with no allowlist, per-sender authentication, or per-sender rate limiting check performed anywhere in this path.

### Finding Description
`gateway.go`'s `ProcessRequest` routes any incoming request without a DON ID (or a legacy request with a DON ID) to a handler and calls `HandleLegacyUserMessage` for legacy requests [1](#0-0) . For the WebAPI capabilities handler, that method decodes the payload, checks that the timestamp is non-zero and not stale, and checks that the method equals `MethodWebAPITrigger` — but performs no allowlist or rate-limit check despite an inline TODO acknowledging this gap [2](#0-1) . It then unconditionally saves a callback and forwards the raw request to every configured DON member: [3](#0-2) .

Contrast this with the outgoing (node-to-client) direction in the same file, where `handleWebAPIOutgoingMessage` does enforce `h.nodeRateLimiter.Allow(nodeAddr)` before acting [4](#0-3) , and with the JSON-RPC/vault gateway path where `HandleGatewayMessage` explicitly enforces both a sender and global incoming rate limiter before dispatching [5](#0-4) . The legacy WebAPI trigger path has no analogous protection on the inbound (user-to-DON) direction, which is the side exposed to arbitrary unprivileged internet clients.

This mirrors the "unprotected ABCI/handler function" and "AnteHandler ordering/order-was-the-dream-of-man" bug classes from the referenced report: a message-envelope handler on the internet-facing boundary that is supposed to gate requests by an allowlist/quota before taking action, but the gating logic was never implemented, leaving only structural validation (timestamp/method) in place.

### Impact Explanation
Any unauthenticated client that can reach the gateway's HTTP endpoint can trigger `web_api_trigger` messages that get broadcast to every node in the DON, with no allowlist check restricting which senders/workflows are permitted and no per-sender rate limit bounding request volume. This can be used to flood all DON nodes with attacker-controlled trigger messages (resource exhaustion / DoS against the capability handling pipeline on every node), and potentially to invoke workflow triggers that were never authorized for that sender, since owner/sender identity is not validated before the broadcast to nodes.

### Likelihood Explanation
High: the legacy `HandleLegacyUserMessage` path is reached directly from the internet-facing `gateway.ProcessRequest` for any legacy-format request that matches an existing DON ID and passes basic payload/timestamp checks — no credential, signature-to-allowlist match, or prior authorization is required beyond what is already implemented (payload well-formedness, non-stale timestamp, exact method name). The missing check is explicitly acknowledged in the code via a TODO comment, confirming this is a known, unaddressed gap rather than a theoretical one.

### Recommendation
Implement and enforce an allowlist check (verifying the requester/sender is permitted to trigger the specified workflow/DON) and a per-sender rate limiter in `HandleLegacyUserMessage`, before the loop that calls `don.SendToNode` for every DON member, consistent with the protections already present in `handleWebAPIOutgoingMessage` (node-side) and the JSON-RPC vault gateway path (`incomingRateLimiter.AllowVerbose`).

### Proof of Concept
1. Send an HTTP request to the gateway's public endpoint with a legacy-format JSON body targeting a known DON ID, `Body.Method = "web_api_trigger"`, and a valid (non-stale) `Timestamp` in `TriggerRequestPayload`.
2. No credentials, signature verification against an allowlist, or prior authorization are required for this request to pass all checks in `HandleLegacyUserMessage`.
3. Observe that the message is forwarded to every member of `h.donConfig.Members`, and repeating the request rapidly is not throttled by any inbound rate limiter, unlike the outbound (`handleWebAPIOutgoingMessage`) and JSON-RPC vault paths.

### Citations

**File:** core/services/gateway/gateway.go (L267-276)
```go
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

**File:** core/services/gateway/handlers/capabilities/handler.go (L359-396)
```go
	if payload.Timestamp == 0 {
		h.lggr.Errorw(ErrDecodingPayload)
		return callback.SendResponse(handlers.UserCallbackPayload{
			RawResponse: codec.EncodeNewErrorResponse(
				msg.Body.MessageID,
				api.ToJSONRPCErrorCode(api.UserMessageParseError),
				ErrDecodingPayload,
				nil,
			),
			ErrorCode: api.UserMessageParseError,
		})
	}

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

**File:** core/capabilities/webapi/outgoing_connector_handler.go (L318-332)
```go
	senderAllow, globalAllow := c.incomingRateLimiter.AllowVerbose(body.Sender)
	errJSON := jsonrpc.WireError{
		Code:    500,
		Message: "",
	}
	if !senderAllow {
		errJSON.Message = errorIncomingRatelimitSender
	}
	if !globalAllow {
		if errJSON.Message == "" {
			errJSON.Message = errorIncomingRatelimitGlobal
		} else {
			errJSON.Message += "\n" + errorIncomingRatelimitGlobal
		}
	}
```
