### Title
Missing allowlist/authorization check on gateway HTTP trigger requests to internal capability handler - (File: core/services/gateway/handlers/capabilities/handler.go)

### Summary
The gateway's `HandleLegacyUserMessage` function, which processes inbound user-initiated web API trigger requests before broadcasting them to all DON node members, contains an explicit `// TODO: apply allowlist and rate-limiting here` comment at the point where authorization should occur, but performs no actual permission/allowlist check before forwarding the request.

### Finding Description
`HandleLegacyUserMessage` in `core/services/gateway/handlers/capabilities/handler.go` validates only payload decoding, a non-zero timestamp, message staleness, and method name equality to `MethodWebAPITrigger` before dispatching the message to every DON member via `don.SendToNode`: [1](#0-0) 

This is unlike the analogous node-originated path `handleWebAPIOutgoingMessage`, which enforces `h.nodeRateLimiter.Allow(nodeAddr)`: [2](#0-1) 

Tracing the call path, `HandleLegacyUserMessage` is invoked from `multiHandler.HandleLegacyUserMessage`, which merely looks up the appropriate sub-handler by method and forwards the call with no authorization/allowlist layer of its own: [3](#0-2) 

This mirrors the reported bug class: an HTTP-reachable endpoint that omits a permission/authorization check before performing a privileged action (here, fanning a user-supplied request out to all nodes of a DON, and later relaying node responses back to that user via a saved callback).

### Impact Explanation
Because no allowlist or per-caller authorization check gates `MethodWebAPITrigger` requests, any unauthenticated/unprivileged external caller reaching the gateway's user-message endpoint can trigger workflow execution requests to every member of a configured DON. This can be used to invoke workflow triggers without being an authorized caller, potentially resulting in unauthorized job/workflow execution and resource consumption across the DON, analogous to the "attackers ... enumerate/exercise functionality without appropriate permission" pattern in the reported advisory.

### Likelihood Explanation
The TODO comment is explicit and unresolved code (not a mocked/test-only path), and the function is on the direct, reachable path from unauthenticated external gateway user messages to node-fanout logic. Likelihood is elevated because the missing check is committed and self-documented as absent, rather than merely a latent design gap.

### Recommendation
Implement the caller/method allowlist and rate-limiting check that the TODO comment references in `HandleLegacyUserMessage` before the message is forwarded to `don.SendToNode`, mirroring the `nodeRateLimiter.Allow` pattern already used for node-originated messages, and gate `MethodWebAPITrigger` invocation on a verified, authorized caller/owner identity.

### Proof of Concept
Not independently exploitable within index-only review; the missing-check location is proven by direct code inspection: [4](#0-3)  shows the TODO comment sitting directly before the method-name check and subsequent `don.SendToNode` fan-out at [5](#0-4) , with no intervening authorization call. Full exploitation would require confirming, via a running Devin session, whether an outer layer (e.g. gateway HTTP router/mux) enforces authorization before calling `HandleLegacyUserMessage`; this could not be fully verified from the indexed context available.

### Citations

**File:** core/services/gateway/handlers/capabilities/handler.go (L164-168)
```go
func (h *handler) handleWebAPIOutgoingMessage(ctx context.Context, msg *api.Message, nodeAddr string) error {
	h.lggr.Debugw("handling webAPI outgoing message", "messageId", msg.Body.MessageID, "nodeAddr", nodeAddr)
	if !h.nodeRateLimiter.Allow(nodeAddr) {
		return fmt.Errorf("rate limit exceeded for node %s", nodeAddr)
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

**File:** core/services/gateway/multihandler.go (L53-60)
```go
func (m *multiHandler) HandleLegacyUserMessage(ctx context.Context, msg *api.Message, callback handlers.Callback) error {
	h, err := m.getHandler(msg.Body.Method)
	if err != nil {
		return fmt.Errorf("failed to get handler for method %s: %w", msg.Body.Method, err)
	}

	return h.HandleLegacyUserMessage(ctx, msg, callback)
}
```
