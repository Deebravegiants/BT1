### Title
Missing allowlist/rate-limit enforcement for legacy web_api_trigger gateway messages allows unauthorized/unthrottled job triggering - (File: core/services/gateway/handlers/capabilities/handler.go)

### Summary
The reported bug class is "missing protection before executing a sensitive action based on unvalidated/unbounded user input" (stop-loss orders execute with `min_amount_out` hardcoded to `0`, i.e., no enforcement of the safety check the design intends to have). The closest reachable analog in this Chainlink codebase is in the gateway's legacy web API capability handler: `HandleLegacyUserMessage` explicitly skips allowlist and rate-limiting checks that the code itself flags as required, before fanning the request out to every node in the DON.

### Finding Description
`HandleLegacyUserMessage` in `core/services/gateway/handlers/capabilities/handler.go` processes an inbound gateway message (`MethodWebAPITrigger`) by unmarshalling the payload, checking a timestamp/staleness bound, and validating the method name — but it contains an explicit `// TODO: apply allowlist and rate-limiting here` comment immediately before it accepts the message and forwards it to every DON member: [1](#0-0) 

Unlike the node-facing path (`HandleNodeMessage`), which enforces `nodeRateLimiter` and sender/address checks, the legacy user-facing entry point performs no per-sender allowlist check and no rate limiting before calling `don.SendToNode` for every configured DON member: [2](#0-1) 

This mirrors the audit's root cause pattern precisely: a safety/authorization gate that the code's own design intends to apply (analogous to the caller-supplied `min_amount_out` slippage bound) is not actually wired in — it is a no-op/TODO rather than an enforced check, letting the sensitive downstream action (forwarding to all nodes / triggering workflow execution) proceed unconditionally.

### Impact Explanation
Because no allowlist or rate-limiting check gates `HandleLegacyUserMessage`, any client able to reach the gateway's legacy message path can trigger `web_api_trigger` payloads that get broadcast to every member of the DON, unconstrained by the allowlist/quota controls that other gateway handlers (e.g., the vault or node message paths) explicitly enforce. This is a concrete allowlist/quota bypass reachable from an unprivileged request, potentially leading to unauthorized workflow triggering or resource exhaustion (DOS) against DON members.

### Likelihood Explanation
The vulnerable code path is reached whenever a legacy `web_api_trigger` message arrives at this handler; there is no conditional gating it behind privilege checks other than the (missing) allowlist. Given the comment explicitly acknowledges the gap, this is a near-certain gap rather than a subtle edge case, though the exact HTTP/WS entrypoint wiring that exposes this handler to external, unauthenticated callers was not fully traced in this pass — this warrants confirmation of the exact external-reachability path (i.e., whether the legacy webapi capability path is still routed from an internet-facing listener in the current deployment) before treating it as fully proven end-to-end.

### Recommendation
Implement the allowlist and rate-limiting check called out by the TODO before accepting and fanning out `web_api_trigger` legacy messages, mirroring the `nodeRateLimiter` enforcement already present for node-originated messages, and reject/short-circuit any sender that is not present in the DON/workflow allowlist or has exceeded its quota.

### Proof of Concept
1. Send a `web_api_trigger` legacy message with a valid, non-stale timestamp and `MethodWebAPITrigger` to the gateway's legacy user-message path.
2. Observe that `HandleLegacyUserMessage` performs no allowlist lookup or rate-limit check (per the TODO at line 384) and proceeds directly to `don.SendToNode` for every DON member. [3](#0-2) 
3. Repeat the request at arbitrary volume/from arbitrary senders — no rejection occurs based on sender identity or request rate, unlike the equivalent `HandleNodeMessage` path which does enforce `nodeRateLimiter`.

### Citations

**File:** core/services/gateway/handlers/capabilities/handler.go (L359-420)
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
