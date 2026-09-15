### Title
Missing Authorization (No Allowlist/Rate-Limit Enforcement) for Legacy Web API Trigger Messages - ([File: core/services/gateway/handlers/capabilities/handler.go])

### Summary
The Chainlink Gateway's legacy web-API-capabilities handler forwards every unprivileged HTTP client request to all DON nodes without ever checking any allowlist or applying rate limiting, despite an explicit `// TODO: apply allowlist and rate-limiting here` marker in the code. This mirrors the Hangfire "missing authorization with default settings" bug class: a code path that is supposed to be protected by an authorization/allowlist check ships with no such check by default, and any unprivileged internet-facing request is fully processed.

### Finding Description
`gateway.ProcessRequest` is the internet-facing entry point invoked directly by the HTTP server for any incoming legacy (DonID-addressed) JSON-RPC request: [1](#0-0) 

For legacy requests it calls `h.HandleLegacyUserMessage(ctx, msg, callback)` directly — no authentication/authorization gate exists in `gateway.go` itself; that responsibility is delegated entirely to the handler implementation.

In `core/services/gateway/handlers/capabilities/handler.go`, `HandleLegacyUserMessage` performs payload decoding, timestamp/staleness checks, and method-name validation, but immediately after those checks there is a comment stating the missing control: [2](#0-1) 

No call to any allowlist, authorizer, or rate limiter (`nodeRateLimiter` is only used for node→gateway outgoing messages in `handleWebAPIOutgoingMessage`, not for the inbound user path) occurs before the message is forwarded to every DON member: [3](#0-2) 

This is confirmed by the handler's own test suite, which explicitly notes the gap is unresolved: [4](#0-3) 

Compare this to the sibling handler (`v2/http_handler.go`), whose HTTP trigger handling explicitly documents JWT authentication and rate limiting as prerequisites before dispatch — that separate v2 code path does not exhibit this issue. The exposure here is specific to the legacy `handlers/capabilities/handler.go` implementation, which remains reachable and wired into the gateway's routing (`gateway.handlers[donID]` / `multiHandler.HandleLegacyUserMessage`): [5](#0-4) 

### Impact Explanation
Any unauthenticated internet caller who can construct a valid signed `api.Message` with a fresh timestamp and `MethodWebAPITrigger` method can trigger workflow execution on every node in the target DON, with no allowlist restricting which callers/workflows are permitted and no rate limiting to throttle abuse. This allows unauthorized triggering of DON-side workflow executions (a form of unauthorized job run) and enables denial-of-service via unbounded request flooding to all DON members, since node-side per-sender throttling in `nodeRateLimiter` only guards the reverse (node→client) direction.

### Likelihood Explanation
High. The vulnerable method requires only a validly-formed/signed `api.Message` reaching the public gateway HTTP endpoint — `msg.Validate()` in `gateway.go` checks message structure/signature integrity, not sender authorization against a workflow-specific allowlist. Any actor capable of signing a message (the signature check does not tie to a permissioned identity list) can reach `HandleLegacyUserMessage` and have it dispatched to all DON nodes.

### Recommendation
Implement the allowlist and rate-limiting check called out by the `// TODO: apply allowlist and rate-limiting here` comment before forwarding the request to `don.SendToNode`, e.g. reusing the same allowlist/authorization pattern used elsewhere in the codebase (the `Authorizer`/`AllowListBasedAuth` pattern used in `core/capabilities/vault`, or the JWT + authorized-keys pattern used in `core/services/gateway/handlers/capabilities/v2/http_trigger_handler.go`), and add a per-sender rate limiter analogous to `nodeRateLimiter` for inbound legacy trigger requests. Do not rely solely on message-format/signature validation as an authorization proxy.

### Proof of Concept
1. Deploy a Gateway node with a DON configured to use the legacy `capabilities` handler (`NewHandler` in `handler.go`).
2. From any unprivileged network client, send an HTTP JSON-RPC request to the gateway's public endpoint with a legacy-format body: `{"signature": "<valid ECDSA sig>", "body": {"message_id": "x", "method": "web_api_trigger", "don_id": "<target-don>", "payload": {"triggerId": "web-api-trigger@1.0.0", "triggerEventId": "e1", "timestamp": <now>, "topics": ["any"], "params": {...}}}}`.
3. `gateway.ProcessRequest` validates only structure/signature (`msg.Validate()`), then routes to `handler.HandleLegacyUserMessage`.
4. `HandleLegacyUserMessage` checks payload decode success, non-zero timestamp, staleness, and method name — none of which restrict *who* may send the request or *which* workflow/topic they are allowed to trigger — then forwards the message to every node in `donConfig.Members` via `don.SendToNode`.
5. All DON nodes receive and process the trigger request, demonstrating that an unauthenticated/unauthorized caller can invoke workflow triggers with no allowlist or rate-limit gate, exactly as the in-code TODO admits.

### Citations

**File:** core/services/gateway/gateway.go (L253-272)
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
```

**File:** core/services/gateway/handlers/capabilities/handler.go (L372-396)
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

**File:** core/services/gateway/handlers/capabilities/handler_test.go (L365-365)
```go
	// TODO: Validate Senders and rate limit check, pending question in trigger about where senders and rate limits are validated
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
