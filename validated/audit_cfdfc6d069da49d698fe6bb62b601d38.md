Confirmed: `msg.Body.MessageID` is set directly from the attacker-controlled JSON-RPC request ID (`request.ID`) in `JSONRPCCodec.DecodeJSONRequest` at [1](#0-0) , with no server-side uniqueness enforcement before it reaches the handler.

### Title
Cross-user response hijacking via unvalidated, client-controlled MessageID collision in gateway webapi capabilities handler - (File: core/services/gateway/handlers/capabilities/handler.go)

### Summary
The gateway's legacy webapi-trigger request path keys pending user callbacks in a shared in-memory map (`savedCallbacks`) using the `MessageID` field taken verbatim from the untrusted, client-supplied JSON-RPC request ID. Because the map write is an unconditional overwrite with no uniqueness/ownership check, a second unprivileged request using the same ID as an in-flight request from a different caller silently replaces the first caller's registered callback. When the DON node eventually responds with that MessageID, the response is routed to whichever caller's callback is currently registered — potentially the attacker's — rather than the original requester's.

### Finding Description
In `gateway.ProcessRequest`, the JSON-RPC request `ID` is decoded straight from the raw, unauthenticated request body [2](#0-1)  and is only checked for length (`<=200` chars), never for collision with other in-flight requests. That ID becomes `msg.Body.MessageID`: [1](#0-0) .

`handler.HandleLegacyUserMessage` then stores the caller's `Callback` in a shared map keyed solely by this attacker-controlled `MessageID`, overwriting any existing entry unconditionally: [3](#0-2) .

When the corresponding DON node later replies with the same `MessageID`, `handleWebAPITriggerMessage` looks up and deletes whichever callback currently occupies that map slot and sends the node's response to it — with no verification that it matches the original requester: [4](#0-3) .

This is structurally analogous to the reentrancy pattern in the reported Uniswap incident: an intervening operation (a second, attacker-issued request) is allowed to mutate shared state (`savedCallbacks[msgID]`) before the first operation (the legitimate request's response delivery) completes, and the system commits to the corrupted state rather than the original intent.

### Impact Explanation
An unprivileged network caller who can predict or brute-force another in-flight request's `MessageID` (or simply race using a duplicate ID before the legitimate response returns, since a large `defaultCallbackMaxAgeSec` of 120s gives a wide race window) can hijack that request's response — a cross-user response confusion. Depending on what data web-api-trigger payloads carry back through this path, this could leak response content intended for another user to the attacker, or cause the legitimate user to silently receive nothing (their callback was evicted) while the attacker's callback fires instead.

### Likelihood Explanation
Exploitability requires the attacker to guess/collide a `MessageID` that another legitimate, concurrently pending request is using. If IDs are unpredictable random UUIDs chosen by well-behaved clients, likelihood is low; however, nothing in the gateway enforces ID unpredictability or per-caller namespacing, so a caller that reuses fixed/sequential/short IDs (or an attacker who can observe the pattern) makes this straightforward. The existing test suite explicitly asserts only that invalid messages don't leave stale entries [5](#0-4) , but there is no test covering same-ID overwrite behavior from two concurrent valid callers, indicating this collision case is unhandled/unvalidated by design.

### Recommendation
Namespace `savedCallbacks` keys by both the caller identity/connection and the client-supplied `MessageID` (or generate a server-side unique correlation ID independent of client input), and reject/queue rather than silently overwrite when a collision on an in-flight ID is detected.

### Proof of Concept
1. Caller A sends a `web_api_trigger` request through the gateway with JSON-RPC `id = "X"`, which is forwarded to DON nodes and registers `savedCallbacks["X"] = callbackA` via `HandleLegacyUserMessage`.
2. Before the DON node responds, Caller B (attacker) sends another request with the same `id = "X"`; this overwrites `savedCallbacks["X"] = callbackB`.
3. The DON node responds with `MessageID = "X"`; `handleWebAPITriggerMessage` looks up `savedCallbacks["X"]`, finds `callbackB`, deletes the entry, and delivers the node's response to attacker B instead of legitimate caller A, whose request then times out.

Note: I could not fully trace whether upstream authentication/session binding (e.g., per-connection scoping enforced elsewhere in the HTTP server or connection manager) mitigates this before requests reach the handler; the gateway code reviewed here shows no such binding at the `savedCallbacks` layer itself.

### Citations

**File:** core/services/gateway/api/jsonrpccodec.go (L26-35)
```go
func (*JSONRPCCodec) DecodeJSONRequest(request jsonrpc2.Request[json.RawMessage]) (*Message, error) {
	var msg Message
	err := json.Unmarshal(*request.Params, &msg)
	if err != nil {
		return nil, err
	}
	msg.Body.MessageID = request.ID
	msg.Body.Method = request.Method
	return &msg, nil
}
```

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

**File:** core/services/gateway/handlers/capabilities/handler_test.go (L339-363)
```go
	t.Run("savedCallbacks stored only when message is valid", func(t *testing.T) {
		require.Empty(t, handler.savedCallbacks)

		invalidPayloadMsg := triggerRequest(t, nodes[0].PrivateKey, []string{"daily_price_update"}, "", "123456", `{"foo":"bar"}`)
		cb := hc.NewCallback()
		err := handler.HandleLegacyUserMessage(ctx, invalidPayloadMsg, cb)
		require.NoError(t, err)
		_, _ = cb.Wait(t.Context())

		staleMsg := triggerRequest(t, nodes[0].PrivateKey, []string{"daily_price_update"}, "", "123456", "")
		cb2 := hc.NewCallback()
		err = handler.HandleLegacyUserMessage(ctx, staleMsg, cb2)
		require.NoError(t, err)
		_, _ = cb2.Wait(t.Context())

		badMethodMsg := triggerRequest(t, nodes[0].PrivateKey, []string{"daily_price_update"}, "foo", "", "")
		cb3 := hc.NewCallback()
		err = handler.HandleLegacyUserMessage(ctx, badMethodMsg, cb3)
		require.NoError(t, err)
		_, _ = cb3.Wait(t.Context())

		handler.mu.Lock()
		require.Empty(t, handler.savedCallbacks, "error paths must not leave entries in savedCallbacks")
		handler.mu.Unlock()
	})
```
