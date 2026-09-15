### Title
Cross-user response hijacking via attacker-controlled MessageID collision in gateway `WebAPIHandler` savedCallbacks map - (File: `core/services/gateway/handlers/capabilities/handler.go`)

### Summary
`HandleLegacyUserMessage` in the internet-facing gateway's `WebAPIHandler` registers a pending user callback in a shared, unauthenticated map keyed solely by the attacker-supplied `MessageID` field of the JSON-RPC request, with no ownership binding and no collision check. Any unprivileged client can pick an arbitrary/predictable `MessageID` and overwrite another user's in-flight callback entry, causing the victim's trigger response to be delivered to the attacker instead.

### Finding Description
The gateway's `ProcessRequest` entrypoint accepts a JSON-RPC request from any unauthenticated internet client and uses the client-supplied `ID` field directly as `msg.Body.MessageID`: [1](#0-0) [2](#0-1) 

That message is passed to `WebAPIHandler.HandleLegacyUserMessage`, which stores the callback in `h.savedCallbacks` keyed purely by `msg.Body.MessageID`, with **no check for an existing entry** before overwriting it: [3](#0-2) 

When a DON node later returns a trigger response carrying that same `MessageID`, `handleWebAPITriggerMessage` looks the callback up only by `MessageID` and delivers the response to whichever callback is currently registered under that key: [4](#0-3) 

Because `MessageID` is fully attacker-chosen and not namespaced/derived from the caller's identity (e.g., signer address, session, or a server-generated nonce), a second unprivileged request using the same `MessageID` as an in-flight legitimate request silently replaces the original caller's callback in the map. When the node's response arrives, it is routed to the attacker's callback (`savedCb.SendResponse`), leaking the victim's trigger result to the attacker, while the victim's original request never receives a response (it will eventually time out via `callback.Wait(ctx)` in `gateway.go`).

Notably, elsewhere in the codebase (the outgoing connector path used by workflow-initiated fetches) the equivalent registration explicitly guards against this exact class of bug by rejecting duplicate IDs: [5](#0-4) 
This shows the project is aware duplicate-ID registration is unsafe, but the `WebAPIHandler.savedCallbacks` map (reachable directly from unauthenticated gateway HTTP requests) lacks the same protection.

### Impact Explanation
This allows an unprivileged, unauthenticated network client to cause cross-user response confusion on the gateway: intercepting another user's/workflow's trigger response payload (which may contain business-sensitive data returned from the DON), and causing denial-of-service for the legitimate caller whose request is silently orphaned. This satisfies the "cross-user response confusion" acceptance criterion for the internet-facing gateway (message envelope / handler / cache) attack surface.

### Likelihood Explanation
The `MethodWebAPITrigger` gateway endpoint (`HandleLegacyUserMessage`) is reachable by any client able to reach the gateway's HTTP endpoint — no authentication/allowlist is enforced at this layer (a `// TODO: apply allowlist and rate-limiting here` comment even marks this gap explicitly): [6](#0-5) 
An attacker only needs to guess or brute-force a low-entropy/predictable `MessageID` used by a target, or race a flood of requests reusing common IDs while a target's request is in flight (default callback lifetime is up to 120s per `defaultCallbackMaxAgeSec`), making exploitation practically feasible without any credentials.

### Recommendation
- Bind `savedCallbacks` keys to caller identity in addition to `MessageID` (e.g., `sender + MessageID`), or generate the map key server-side rather than trusting the client-supplied ID.
- Reject registration when an entry already exists for the computed key, mirroring the duplicate-ID guard already used in `OutgoingConnectorHandler.handleSingleNodeRequest` (`c.responses.new`).
- Enforce the still-missing allowlist/rate-limiting noted in the `HandleLegacyUserMessage` TODO to reduce the attack surface.

### Proof of Concept
1. Attacker observes or predicts a victim's outbound `MethodWebAPITrigger` request `MessageID` (or races many requests with common/sequential IDs) sent to the gateway's public endpoint.
2. Victim's request completes `HandleLegacyUserMessage`, registering `h.savedCallbacks[MessageID] = victimCallback`.
3. Before the DON node responds, attacker sends their own `MethodWebAPITrigger` request using the identical `MessageID`; `HandleLegacyUserMessage` overwrites the map entry: `h.savedCallbacks[MessageID] = attackerCallback` (no duplicate check, `core/services/gateway/handlers/capabilities/handler.go:411-414`).
4. The DON node responds with the trigger result tagged with `MessageID`; `handleWebAPITriggerMessage` looks up `h.savedCallbacks[MessageID]`, finds the attacker's callback, and delivers the victim's response data to the attacker (`core/services/gateway/handlers/capabilities/handler.go:148-162`).
5. The victim's original HTTP request hangs until gateway timeout, receiving no response, while the attacker has received data intended for the victim.

### Citations

**File:** core/services/gateway/gateway.go (L221-234)
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
```

**File:** core/services/gateway/handlers/common/message_util.go (L46-52)
```go
	var m api.Message
	err := json.Unmarshal(*req.Params, &m)
	if err != nil {
		return nil, fmt.Errorf("failed to unmarshal request params: %w", err)
	}
	m.Body.Method = req.Method
	m.Body.MessageID = req.ID
```

**File:** core/services/gateway/handlers/capabilities/handler.go (L148-162)
```go
func (h *handler) handleWebAPITriggerMessage(ctx context.Context, msg *api.Message, nodeAddr string) error {
	h.mu.Lock()
	savedCb, found := h.savedCallbacks[msg.Body.MessageID]
	delete(h.savedCallbacks, msg.Body.MessageID)
	h.mu.Unlock()

	if found {
		// Send first response from a node back to the user, ignore any other ones.
		// TODO: in practice, we should wait for at least 2F+1 nodes to respond and then return an aggregated response
		// back to the user.
		codec := api.JSONRPCCodec{}
		return savedCb.SendResponse(handlers.UserCallbackPayload{RawResponse: codec.EncodeLegacyResponse(msg), ErrorCode: api.NoError})
	}
	return nil
}
```

**File:** core/services/gateway/handlers/capabilities/handler.go (L384-384)
```go
	// TODO: apply allowlist and rate-limiting here
```

**File:** core/services/gateway/handlers/capabilities/handler.go (L411-414)
```go
	h.mu.Lock()
	h.savedCallbacks[msg.Body.MessageID] = &savedCallback{id: msg.Body.MessageID, createdAt: time.Now(), Callback: callback}
	don := h.don
	h.mu.Unlock()
```

**File:** core/capabilities/webapi/outgoing_connector_handler.go (L136-140)
```go
	ch, err := c.responses.new(messageID)
	if err != nil {
		return nil, fmt.Errorf("duplicate message received for ID: %s", messageID)
	}
	defer c.responses.cleanup(messageID)
```
