### Title
Legacy Gateway user-message path processes unauthenticated capability triggers without allowlist or rate-limit checks - (File: core/services/gateway/handlers/capabilities/handler.go)

### Summary
The gateway's newer v2 HTTP trigger path (`httpTriggerHandler.HandleUserTriggerRequest`) enforces authorization and per-workflow rate limiting before dispatching a workflow-trigger request to DON nodes. The legacy sibling path, `handler.HandleLegacyUserMessage` in `core/services/gateway/handlers/capabilities/handler.go`, validates only payload shape, timestamp freshness, and method name, then forwards the request directly to every DON member — explicitly skipping allowlist/rate-limit enforcement, as flagged by its own inline comment.

### Finding Description
`HandleLegacyUserMessage` decodes the incoming `TriggerRequestPayload`, checks that it unmarshals, that `Timestamp != 0`, and that the message isn't older than `MaxAllowedMessageAgeSec`, and that `msg.Body.Method == MethodWebAPITrigger`: [1](#0-0) 

Immediately after those checks, a comment marks the gap explicitly: [2](#0-1) 

No call to any `Authorizer`, allowlist, or `ratelimit.RateLimiter` occurs on the incoming user request in this path (the only rate limiter present, `h.nodeRateLimiter`, is applied to node→gateway `handleWebAPIOutgoingMessage` traffic, not to inbound user triggers): [3](#0-2) 

The request is then saved as a callback and fanned out to every DON member unconditionally: [4](#0-3) 

By contrast, the newer per-request path used for HTTP-triggered workflows (`httpTriggerHandler.HandleUserTriggerRequest` in `core/services/gateway/handlers/capabilities/v2/http_trigger_handler.go`) explicitly calls `h.authorizeRequest(...)` and `h.checkRateLimit(...)` before any request is forwarded to a DON: [5](#0-4) 

This mirrors the reported bug-class pattern: one code path enforces the expected security check (safeTransferFrom's callback, here: authorization/rate-limiting), while a parallel/legacy entry point that reaches the same downstream effect (triggering DON execution) omits it. Any client able to reach `HandleLegacyUserMessage` (registered for `MethodWebAPITrigger` on the `handlers.DON`/gateway multihandler routing, per `core/services/gateway/handlers/handler.go` and `core/services/gateway/multihandler.go`) can dispatch trigger messages to the entire DON membership without being checked against the workflow-registry allowlist or any per-owner/per-workflow rate limit that the v2 path enforces.

### Impact Explanation
If this legacy handler is still reachable from unauthenticated/unprivileged external gateway clients, it allows: (1) bypass of the allowlist gating that restricts which workflows/owners may trigger execution, and (2) bypass of rate limiting, enabling flooding of every DON node with trigger messages. This matches the "allowlist or quota bypass" / "unauthorized job run" categories called out as acceptable analog impact.

### Likelihood Explanation
Likelihood depends on whether `MethodWebAPITrigger`/`HandleLegacyUserMessage` remains an actively enabled, externally reachable route in production configurations, or whether it is a deprecated/legacy code path being phased out in favor of the v2 `httpTriggerHandler`. I could not fully confirm, within available context, whether this legacy handler is currently wired into a live, unprivileged-facing gateway endpoint in the default/production configuration, versus being retained only for backward compatibility with specific already-vetted integrations. This uncertainty should be resolved before treating this as a confirmed exploitable gap — the code-level evidence (missing authz/rate-limit calls plus the explicit `// TODO: apply allowlist and rate-limiting here` comment) is concrete, but reachability by a fully unprivileged actor needs verification against how the gateway routes `MethodWebAPITrigger` messages in deployed configs.

### Recommendation
Add the same allowlist/authorization and rate-limiting enforcement used in `httpTriggerHandler.HandleUserTriggerRequest` to `HandleLegacyUserMessage` before it saves the callback and fans the request out to DON members, or remove/disable the legacy path entirely if it is meant to be superseded by the v2 handler.

### Proof of Concept
Not independently reproducible from the indexed code alone (no live gateway/config available). The concrete evidence is the code-level asymmetry:
1. `HandleLegacyUserMessage` performs no allowlist/authorization/rate-limit check on the inbound request — confirmed by the absence of any such calls and the explicit TODO comment at lines 384–396 of `core/services/gateway/handlers/capabilities/handler.go`.
2. The parallel v2 path `HandleUserTriggerRequest` performs both `authorizeRequest` and `checkRateLimit` before forwarding (lines 106–113 of `http_trigger_handler.go`), demonstrating these checks are considered mandatory for this class of gateway-triggered DON execution elsewhere in the codebase.

### Citations

**File:** core/services/gateway/handlers/capabilities/handler.go (L164-168)
```go
func (h *handler) handleWebAPIOutgoingMessage(ctx context.Context, msg *api.Message, nodeAddr string) error {
	h.lggr.Debugw("handling webAPI outgoing message", "messageId", msg.Body.MessageID, "nodeAddr", nodeAddr)
	if !h.nodeRateLimiter.Allow(nodeAddr) {
		return fmt.Errorf("rate limit exceeded for node %s", nodeAddr)
	}
```

**File:** core/services/gateway/handlers/capabilities/handler.go (L341-396)
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
