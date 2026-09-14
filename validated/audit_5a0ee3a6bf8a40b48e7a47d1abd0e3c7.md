### Title
Cross-user response hijacking via attacker-controlled `MessageID` collision in Gateway WebAPI trigger callback cache - (File: `core/services/gateway/handlers/capabilities/handler.go`)

### Summary
The Chainlink Gateway's legacy WebAPI-trigger user-request path keys its response-matching cache (`savedCallbacks`) solely by the client-supplied JSON-RPC request `ID`, which becomes `Message.Body.MessageID` with no server-side randomization, uniqueness enforcement, or binding to the requester's identity. An unprivileged internet client that submits a request with the same `MessageID` as another in-flight user's request overwrites that user's cache entry; when the DON subsequently returns a trigger response for that `MessageID`, it is delivered to whichever caller currently occupies the slot rather than to the original requester. This mirrors the SushiSwap `RouteProcessor2` bug class: a callback/response-matching mechanism trusts an attacker-suppliable identifier to select which counterparty gets serviced, instead of verifying ownership of that identifier.

### Finding Description
The internet-facing Gateway HTTP entrypoint decodes the raw JSON-RPC request and only bounds the `ID` field length (`len(jsonRequest.ID) > 200`) before treating it as trusted: [1](#0-0) 

For legacy DON-routed requests, `ValidatedMessageFromReq` copies this fully attacker-controlled `req.ID` directly into `Message.Body.MessageID`: [2](#0-1) 

The WebAPI capabilities handler then stores the caller's response callback in a DON-scoped, in-memory map keyed **only** by that attacker-controlled `MessageID`, with no check for an existing/colliding entry: [3](#0-2) 

When a DON node later sends back a `MethodWebAPITrigger` response for that same `MessageID`, the handler looks up and deletes the map entry by that key alone and forwards the node's response to whichever callback is currently stored there: [4](#0-3) 

There is no association between the stored callback and the original caller's session/identity — the map entry is a bare string key to a callback closure. Any second unprivileged client (accidentally reusing an ID, or deliberately targeting a victim's known/predictable/observed ID on the same DON) can overwrite entry `X`. If the legitimate node response for `X` arrives after the overwrite, it is delivered to the attacker's HTTP connection instead of the victim's, and the victim's request instead times out with no response (or, in the reverse ordering, the attacker's own request silently receives no callback because it was pruned/overwritten by a third party). This is directly analogous to the Sushi `RouteProcessor2` `uniswapV3SwapCallback` flaw where an attacker-supplied "pool" identity was accepted without verifying it belonged to the genuine counterparty, letting the attacker intercept/redirect state meant for someone else.

### Impact Explanation
This allows an unprivileged Gateway client to cause cross-user response confusion: intercepting another user's WebAPI trigger response (potentially containing sensitive workflow output data) or denying that user's response, purely by choosing a colliding `MessageID`. Because the cache is shared per-DON across all clients and the key space is entirely attacker-controlled with no per-caller isolation, this is a request-impersonation / response-hijacking primitive reachable directly from any unprivileged HTTP client hitting the Gateway.

### Likelihood Explanation
Exploitability depends on the attacker being able to predict, observe, or intentionally reuse another caller's `MessageID` within the response window (bounded by `defaultCallbackMaxAgeSec` = 120s) on the same DON. Since no randomness or namespacing is added server-side, and callers fully control the ID, collision is trivial whenever IDs are not cryptographically random (e.g., sequential counters, fixed/well-known IDs, or deliberate collision by a malicious co-tenant of the same DON), making this a Medium-to-High likelihood issue for any deployment where `MessageID` generation on the client side is not enforced to be unpredictable.

### Recommendation
- Bind each `savedCallbacks` entry to caller-specific context (e.g., derive/salt the internal cache key from a server-generated nonce or the authenticated sender, not solely the client-chosen `MessageID`), and reject/collision-check insertion if the key is already active.
- Do not allow silent overwrite of an active `savedCallbacks[id]` entry; return an explicit "duplicate/in-flight request ID" error instead.
- Consider using the `handlers/common/requestcache.go` request-cache pattern already present, if it applies stronger identity binding, uniformly for `MethodWebAPITrigger`.

### Proof of Concept
1. Attacker sends a legacy Gateway request (`method=web_api_trigger`, `donID=<target DON>`) with `id = "victim-id"` and a valid signature; `HandleLegacyUserMessage` stores the attacker's callback at `savedCallbacks["victim-id"]` (core/services/gateway/handlers/capabilities/handler.go:411-414).
2. Before the DON responds to a legitimate victim request that also used (or will use) `id = "victim-id"` on the same DON, the attacker's insertion overwrites/precedes the victim's entry in the shared map.
3. When the DON node emits the `web_api_trigger` response for `MessageID = "victim-id"`, `handleWebAPITriggerMessage` looks it up and forwards it to whichever callback currently occupies that key (handler.go:148-162) — potentially the attacker's HTTP connection, receiving the victim's intended trigger response, while the victim's request never resolves.

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

**File:** core/services/gateway/handlers/common/message_util.go (L46-57)
```go
	var m api.Message
	err := json.Unmarshal(*req.Params, &m)
	if err != nil {
		return nil, fmt.Errorf("failed to unmarshal request params: %w", err)
	}
	m.Body.Method = req.Method
	m.Body.MessageID = req.ID
	err = m.Validate()
	if err != nil {
		return nil, err
	}
	return &m, nil
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

**File:** core/services/gateway/handlers/capabilities/handler.go (L411-414)
```go
	h.mu.Lock()
	h.savedCallbacks[msg.Body.MessageID] = &savedCallback{id: msg.Body.MessageID, createdAt: time.Now(), Callback: callback}
	don := h.don
	h.mu.Unlock()
```
