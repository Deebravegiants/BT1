### Title
Unprivileged users can DOS the Gateway and DON nodes via unrestricted `web_api_trigger` legacy messages - ([File: core/services/gateway/handlers/capabilities/handler.go])

### Summary
`gateway.ProcessRequest` (`core/services/gateway/gateway.go:221-295`) routes any legacy JSON-RPC request carrying a `DonID` straight to `handler.HandleLegacyUserMessage` without any per-user allowlist or rate-limit check. [1](#0-0)  Inside `HandleLegacyUserMessage`, the only checks performed are payload decode, a non-zero timestamp check, and a staleness window check; there is an explicit `// TODO: apply allowlist and rate-limiting here` immediately before the message is fanned out to every DON member. [2](#0-1) 

### Finding Description
This mirrors the referenced SUI bug class: an unprivileged actor can repeatedly submit "negligible-value" requests (here, cheap, valid-shaped `web_api_trigger` JSON-RPC calls) because the code path that is supposed to enforce authorization/quota (allowlisting and rate-limiting) is not implemented at all, only stubbed with a TODO comment.

Concretely:
- `HandleLegacyUserMessage` accepts any message with `Method == MethodWebAPITrigger`, a non-zero `Timestamp`, and a timestamp not older than `MaxAllowedMessageAgeSec`. [3](#0-2) 
- Right after those checks, the code comments `// TODO: apply allowlist and rate-limiting here` — no allowlist or per-sender rate limiter is invoked in this path, unlike the newer `v2` HTTP trigger path which does enforce `authorizeRequest`/JWT and `checkRateLimit` (`core/services/gateway/handlers/capabilities/v2/http_trigger_handler.go:95-146`), and unlike `handleWebAPIOutgoingMessage` for node-originated messages which does call `h.nodeRateLimiter.Allow(nodeAddr)` (`core/services/gateway/handlers/capabilities/handler.go:164-168`). [4](#0-3) 
- The request is then transformed and forwarded to `don.SendToNode` for **every member of the DON**, and a callback entry is stored in the handler's `savedCallbacks` map, gated only by `MaxSavedCallbacks`/pruning, not by rejecting the request up front. [5](#0-4) 
- Existing tests explicitly acknowledge this gap: `handler_test.go` contains the comment `// TODO: Validate Senders and rate limit check, pending question in trigger about where senders and rate limits are validated`, confirming the maintainers know this path is unguarded. [6](#0-5) 

Because `NewGatewayFromConfig`/`gateway.ProcessRequest` is the internet-facing gateway entry point (`g.httpServer.SetHTTPRequestHandler(gw)`), any external, unauthenticated (or minimally authenticated) client can hit this handler directly by sending legacy-format JSON-RPC requests with a valid `DonID`. [7](#0-6) 

### Impact Explanation
An unprivileged client can spam cheap, well-formed `web_api_trigger` requests to flood every node in the DON with unauthorized/unthrottled messages, exhausting gateway CPU/memory (via unbounded `savedCallbacks` growth up to `MaxSavedCallbacks`, plus per-request goroutines/HTTP calls in the eventual outgoing flow) and DON node processing capacity. This is a direct availability/DOS impact on the internet-facing gateway analogous to the SUI report's unlimited free-deposit spam vector, though here the "value" being drained is compute/network resources rather than funds.

### Likelihood Explanation
High. The vulnerable path is reachable by any unauthenticated external caller through the gateway's public HTTP endpoint with no special privileges, only a syntactically valid legacy JSON-RPC request (correct `DonID`, `MethodWebAPITrigger`, and a recent `Timestamp`). No allowlist entry, JWT, or signature is currently required or checked before fan-out to nodes — the code comment and matching test TODO both confirm this is unimplemented rather than a design choice enforced elsewhere.

### Recommendation
Implement the allowlist and rate-limiting logic referenced by the TODO in `HandleLegacyUserMessage` (`core/services/gateway/handlers/capabilities/handler.go`) before forwarding requests to `don.SendToNode`, mirroring the pattern already used in the `v2` HTTP trigger handler (`authorizeRequest` + `checkRateLimit` in `core/services/gateway/handlers/capabilities/v2/http_trigger_handler.go`) and in the node-message path's `nodeRateLimiter.Allow`. At minimum, add per-sender and global rate limiting plus a sender allowlist check prior to storing the callback and fanning out to DON members.

### Proof of Concept
Not independently reproducible from static analysis alone (no live gateway/DON instance available); the vulnerability is demonstrated by direct code inspection:
1. Send a legacy JSON-RPC POST to the gateway's user-facing HTTP port with a valid `DonID`, `Method: "web_api_trigger"`, and a payload containing a fresh `Timestamp` (any value satisfying the staleness check).
2. `gateway.ProcessRequest` routes it to `HandleLegacyUserMessage` (no auth/rate-limit gate). [1](#0-0) 
3. The message passes the format/staleness checks and is immediately forwarded to `don.SendToNode` for every DON member. [5](#0-4) 
4. Repeating this request in a loop has no built-in throttling in this handler, allowing unbounded request volume to reach the DON and consume gateway callback-tracking memory until pruning triggers.

### Citations

**File:** core/services/gateway/gateway.go (L170-183)
```go
func NewGateway(codec api.Codec, httpServer gw_net.HTTPServer, handlers map[string]handlers.Handler, serviceNameToDonID map[string]string, serviceToMultiHandler map[string]handlers.Handler, connMgr ConnectionManager, gMetrics *monitoring.GatewayMetrics, lggr logger.Logger) Gateway {
	gw := &gateway{
		codec:                 codec,
		httpServer:            httpServer,
		handlers:              handlers,
		serviceNameToDonID:    serviceNameToDonID,
		serviceToMultiHandler: serviceToMultiHandler,
		connMgr:               connMgr,
		gMetrics:              gMetrics,
		lggr:                  logger.Named(lggr, "Gateway"),
	}
	httpServer.SetHTTPRequestHandler(gw)
	return gw
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

**File:** core/services/gateway/handlers/capabilities/handler.go (L341-420)
```go
func (h *handler) HandleLegacyUserMessage(ctx context.Context, msg *api.Message, callback handlers.Callback) error {
	body := msg.Body
	var payload webapicap.TriggerRequestPayload
	codec := api.JSONRPCCodec{}
	err := json.Unmarshal(body.Payload, &payload)
	if err != nil {
		h.lggr.Errorw(ErrDecodingPayload, "err", err)
		return callback.SendResponse(handlers.UserCallbackPayload{
			RawResponse: codec.EncodeNewErrorResponse(
				msg.Body.MessageID,
				api.ToJSONRPCErrorCode(api.UserMessageParseError),
				ErrDecodingPayload+" "+err.Error(),
				nil,
			),
			ErrorCode: api.UserMessageParseError,
		})
	}

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

**File:** core/services/gateway/handlers/capabilities/handler_test.go (L360-367)
```go
		handler.mu.Lock()
		require.Empty(t, handler.savedCallbacks, "error paths must not leave entries in savedCallbacks")
		handler.mu.Unlock()
	})

	// TODO: Validate Senders and rate limit check, pending question in trigger about where senders and rate limits are validated
}

```
