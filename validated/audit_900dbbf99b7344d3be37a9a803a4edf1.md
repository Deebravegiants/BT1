Found a concrete match: `HandleLegacyUserMessage` in `core/services/gateway/handlers/capabilities/handler.go` contains `// TODO: apply allowlist and rate-limiting here` at line 384, immediately before the method dispatches the incoming legacy user message to all DON nodes.

### Title
Missing allowlist/rate-limit enforcement on legacy WebAPI trigger messages - (File: core/services/gateway/handlers/capabilities/handler.go)

### Summary
The gateway's `handler.HandleLegacyUserMessage` function processes unauthenticated external HTTP requests that reach the gateway and forwards them to every DON node member, but the code contains an explicit `// TODO: apply allowlist and rate-limiting here` [1](#0-0)  right before it validates the method and fans the request out to `h.donConfig.Members` [2](#0-1) .

### Finding Description
`HandleLegacyUserMessage` decodes the untrusted payload, checks the timestamp for staleness, and then — per the TODO — skips any allowlist or rate-limiting check before validating the message and forwarding it to all DON node members via `don.SendToNode` [3](#0-2) . Other handlers in the gateway consistently gate node-originating traffic through a `nodeRateLimiter.Allow(...)` check, e.g. `handleWebAPIOutgoingMessage` [4](#0-3) , but the legacy user-facing entry point that receives requests from external clients has no equivalent check, only the developer TODO marking it as unimplemented.

### Impact Explanation
Without an allowlist or rate limit at this ingress point, any unprivileged client able to reach the gateway's legacy WebAPI trigger endpoint can flood every member of a DON with forwarded requests, bypassing the per-node/per-client throttling that protects the DON from resource exhaustion and unauthorized triggering of workflow execution. This is a quota/allowlist bypass at the internet-facing gateway boundary.

### Likelihood Explanation
The TODO is unconditional and sits directly in the code path executed for every legacy user message before broadcasting to `h.donConfig.Members`, so the missing check applies to all callers of this handler, not just an edge case. Whether this legacy path is still reachable in the production message-routing configuration (vs. superseded by the v2 handler `core/services/gateway/handlers/capabilities/v2/http_handler.go`) could not be fully confirmed from the available index; the wiring of legacy vs. v2 handler selection would need to be checked in `core/services/gateway/handler_factory.go` and the DON's `HandlerType` configuration.

### Recommendation
Implement allowlist and rate-limiting checks (reusing the existing `nodeRateLimiter` pattern, or an equivalent client/DON allowlist) inside `HandleLegacyUserMessage` before the message is validated and forwarded to DON members, matching the protections already applied in `handleWebAPIOutgoingMessage`.

### Proof of Concept
Not independently reproducible from static review alone — reachability depends on whether `HandleLegacyUserMessage` is still routed to from the gateway's live configuration for a given DON (`HandlerType` = `WebAPICapabilitiesType`, see `core/services/gateway/handler_factory.go`). If so, sending repeated unauthenticated `web_api_trigger` legacy-format messages to the gateway's HTTP ingress would demonstrate the lack of throttling since the code path executes `don.SendToNode` for every DON member without any rate/allowlist gate [5](#0-4) .

**Note:** the other TODOs found during this scan (`core/capabilities/vault/gw_handler.go:78` and `core/capabilities/vault/validator.go:112,154`, all referencing org-resolver work tracked under CRE-1707) relate to scoping limiter/authorization context by organization rather than by owner, but the existing owner-scoped checks remain enforced, so these did not meet the bar for a concrete authentication/authorization bypass and are excluded per the validation rules.

### Citations

**File:** core/services/gateway/handlers/capabilities/handler.go (L164-168)
```go
func (h *handler) handleWebAPIOutgoingMessage(ctx context.Context, msg *api.Message, nodeAddr string) error {
	h.lggr.Debugw("handling webAPI outgoing message", "messageId", msg.Body.MessageID, "nodeAddr", nodeAddr)
	if !h.nodeRateLimiter.Allow(nodeAddr) {
		return fmt.Errorf("rate limit exceeded for node %s", nodeAddr)
	}
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
