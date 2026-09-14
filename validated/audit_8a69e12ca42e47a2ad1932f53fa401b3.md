### Title
Missing allowlist/rate-limit enforcement in legacy WebAPI trigger gateway handler allows unrestricted forwarding of unauthenticated user requests to DON nodes - (File: core/services/gateway/handlers/capabilities/handler.go)

### Summary
The Sherlock report flags `Manager.sol::deploy()` for accepting an externally supplied component (`metadataRenderer`) and using it without verifying it actually implements the expected interface/contract, allowing the protocol's core invariants to be silently broken. The applicable bug class — accepting and acting on unvalidated/unchecked externally-supplied input in a critical path without the guard that is explicitly expected to exist — has a direct analog in the chainlink gateway's legacy WebAPI capabilities handler, where an explicitly-flagged missing allowlist/rate-limit check lets any external, unauthenticated caller reach the DON dispatch path.

### Finding Description
`HandleLegacyUserMessage` in `core/services/gateway/handlers/capabilities/handler.go` processes inbound legacy user messages that get forwarded to all DON nodes. The code path validates payload structure and staleness, but explicitly skips the allowlist/rate-limiting check that other parts of the codebase (and the design intent) expect to be present: [1](#0-0) 

```go
	// TODO: apply allowlist and rate-limiting here
	if msg.Body.Method != MethodWebAPITrigger {
		...
	}
```

Compare this to the modern outgoing-connector path, which explicitly enforces sender/global rate limiting before dispatch: [2](#0-1) 

And compare with the new-style HTTP capability handler which is expected to apply allowlists/rate limiting as part of its request lifecycle — this legacy code path bypasses that entirely, forwarding the message to every DON member unconditionally: [3](#0-2) 

```go
	h.mu.Lock()
	h.savedCallbacks[msg.Body.MessageID] = &savedCallback{id: msg.Body.MessageID, createdAt: time.Now(), Callback: callback}
	don := h.don
	h.mu.Unlock()

	// Send original request to all nodes
	for _, member := range h.donConfig.Members {
		err = errors.Join(err, don.SendToNode(ctx, member.Address, req))
	}
```

This is analogous to the audited bug: a critical component in the request-processing pipeline (allowlist verification) that is assumed by the surrounding design to gate access is not actually invoked, so unvalidated/unchecked external input flows straight into the core execution path (dispatch to DON nodes), similar to how the unchecked `metadataRenderer` flows straight into core protocol execution (minting) in the Solidity report.

### Impact Explanation
Because the allowlist and rate-limiting check is a `TODO` and not implemented, any external HTTP caller reaching this legacy gateway endpoint can trigger `web_api_trigger` requests that are forwarded to every member node of the DON without any authorization or per-sender quota enforcement. This is an allowlist/quota-bypass class issue on an internet-facing gateway handler, potentially enabling spam/DoS of DON nodes or unauthorized triggering of workflow executions by unprivileged/unauthenticated actors — consistent with the "allowlist or quota bypass" and "unauthorized job run" acceptance criteria.

### Likelihood Explanation
The missing check is explicitly marked with a `TODO` comment in production code (`core/services/gateway/handlers/capabilities/handler.go:384`), confirming this is not merely theoretical — the check is known to be absent by the developers and reachable from any external, unauthenticated caller of the legacy WebAPI trigger message path (`HandleLegacyUserMessage`), which per the code's own comments handles requests before more advanced (v2) handlers are used. I was unable to fully trace every HTTP route wiring that ultimately invokes `HandleLegacyUserMessage` in this session (index coverage limits prevented tracing the full call graph to the outer HTTP router), so the exact deployment conditions under which this legacy path is still reachable in current configs should be confirmed with a full repository checkout.

### Recommendation
Implement the allowlist and rate-limiting check that the `TODO` comment indicates was intended before forwarding messages to DON nodes in `HandleLegacyUserMessage`, mirroring the enforcement already done in `OutgoingConnectorHandler.HandleGatewayMessage` (`incomingRateLimiter.AllowVerbose`) and the node-side rate limiter (`nodeRateLimiter.Allow`) used elsewhere in the same package.

### Proof of Concept
1. Locate a gateway deployment where the legacy WebAPI capabilities handler is wired to accept `MethodWebAPITrigger` user messages via `HandleLegacyUserMessage`.
2. Send a crafted `web_api_trigger` message with a valid non-stale timestamp but from an arbitrary/unauthorized sender (no allowlist entry required, since the check is never invoked).
3. Observe that the message passes directly to `don.SendToNode` for every DON member (`core/services/gateway/handlers/capabilities/handler.go:417-419`) with no allowlist or per-sender rate limit rejection, unlike the equivalent flow in `OutgoingConnectorHandler.HandleGatewayMessage`, confirming the bypass.

### Citations

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

**File:** core/services/gateway/handlers/capabilities/handler.go (L410-420)
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

**File:** core/capabilities/webapi/outgoing_connector_handler.go (L318-333)
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
