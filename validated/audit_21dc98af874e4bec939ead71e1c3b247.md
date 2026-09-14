## Finding

### Title
Missing allowlist and rate-limiting enforcement in `HandleLegacyUserMessage` despite explicit intent to gate it - ([File: core/services/gateway/handlers/capabilities/handler.go])

### Summary
The original report flags a security control (`nonReentrant`) that is referenced/relied upon but never actually implemented — a modifier applied to `buyShares`/`sellShares` in `GSPFunding.sol` with no underlying protection, giving a false sense of security. The chainlink analog is the `handler.HandleLegacyUserMessage` function in the WebAPI gateway handler, which contains an explicit `// TODO: apply allowlist and rate-limiting here` marker at the exact point where access control should be enforced, but no such control is actually applied before the request is broadcast to every node in the DON.

### Finding Description
`gateway.ProcessRequest` is the entry point invoked directly from the user-facing HTTP server for every incoming client request [1](#0-0) . For legacy (DON-ID-keyed) requests it dispatches straight to `h.HandleLegacyUserMessage(ctx, msg, callback)` [2](#0-1) .

In the `capabilities` package's implementation of that method, after basic payload/staleness checks, there is a comment stating intent to gate the request with an allowlist and rate limiter, immediately followed by only a method-name check — no allowlist or per-caller rate limiting is actually performed: [3](#0-2) 

The function then unconditionally forwards the raw client-supplied request to every member node of the DON: [4](#0-3) 

The only protective control actually present anywhere in this handler is `nodeRateLimiter`, which is applied to node→gateway messages (`handleWebAPIOutgoingMessage`), not to user→gateway requests [5](#0-4) . There is no equivalent limiter or allowlist check on the ingress path from an unprivileged HTTP client.

### Impact Explanation
Any unauthenticated/unprivileged client hitting the gateway's user HTTP port can trigger `web_api_trigger` messages that are relayed to every node of the target DON with no allowlist or rate-limiting, exactly as the TODO comment acknowledges is needed but missing. This mirrors the reported bug class: a named security control that looks present (via comment/expectation) but performs no actual enforcement, allowing the very abuse it was meant to prevent — in this case unrestricted workflow-trigger fan-out to DON nodes, which can be used for resource exhaustion/DoS or unauthorized triggering of workflow executions across the DON.

### Likelihood Explanation
High. This is directly reachable from the internet-facing gateway's user HTTP endpoint with no authentication requirement beyond well-formed JSON-RPC — the code path is exercised on every legacy `web_api_trigger` request via `gateway.ProcessRequest` → `HandleLegacyUserMessage`.

### Recommendation
Implement the allowlist and rate-limiting logic referenced by the TODO comment in `HandleLegacyUserMessage` before broadcasting to `don.SendToNode`, mirroring the per-node/global rate limiting already applied on the node-response path, and validate the caller against a workflow/owner allowlist analogous to the vault handler's `Authorizer` pattern [6](#0-5)  before forwarding requests to DON members.

### Proof of Concept
1. Send a well-formed legacy JSON-RPC request with `Method: web_api_trigger` and a valid non-zero `Timestamp` directly to the gateway's user HTTP port, using any DON ID configured in `serviceNameToDonID`/`handlers` — no credentials required beyond message structure.
2. Observe in `gateway.ProcessRequest` that the request reaches `h.HandleLegacyUserMessage` unconditionally [2](#0-1) .
3. In `HandleLegacyUserMessage`, the request passes the "TODO: apply allowlist" checkpoint without any allowlist/rate check and is fanned out to all `donConfig.Members` [7](#0-6) .
4. Repeat rapidly from a single unprivileged client to demonstrate unmitigated fan-out to every DON node, confirming absence of the intended control.

### Citations

**File:** core/services/gateway/gateway.go (L221-235)
```go
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
	isLegacyRequest := false
```

**File:** core/services/gateway/gateway.go (L270-272)
```go
	if isLegacyRequest {
		method = msg.Body.Method
		err = h.HandleLegacyUserMessage(ctx, msg, callback)
```

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

**File:** core/capabilities/vault/gw_handler.go (L108-111)
```go
	if authorizer == nil {
		allowListBasedAuth := NewAllowListBasedAuth(lggr, workflowRegistrySyncer)
		authorizer = NewAuthorizer(allowListBasedAuth, jwtBasedAuth, lggr)
	}
```
