## Analysis Result

The strongest reachable analog to CVE-2021-46701 (unauthenticated event interception via a shared transport channel) in this codebase is a **MessageID-based response hijacking flaw in the Gateway's `WebAPIHandler`**, on the internet-facing user endpoint.

### Title
Unauthenticated Cross-User Response Hijacking via MessageID Collision in Gateway WebAPI Handler - (File: core/services/gateway/handlers/capabilities/handler.go)

### Summary
The Gateway's user-facing HTTP endpoint accepts JSON-RPC requests whose `id` field becomes the internal `MessageID` used to route asynchronous node responses back to the originating HTTP caller. This `MessageID` is fully attacker-controlled and is not bound to the caller's identity, nor is uniqueness enforced when storing the pending callback. Any unprivileged client can therefore choose the same `MessageID` as a concurrent, legitimate in-flight request and overwrite the stored callback, causing the eventual node response (intended for the victim) to be delivered to the attacker instead.

### Finding Description
`ProcessRequest` in [1](#0-0)  decodes the raw JSON-RPC request and assigns `msg.Body.MessageID = request.ID` directly from client-supplied JSON, as implemented in [2](#0-1) .

This message is passed to `HandleLegacyUserMessage`, which stores the callback keyed **only** by this client-chosen `MessageID`, with no existence check and no binding to the caller's session, signer, or IP: [3](#0-2) 

Note the explicit code comment acknowledging the missing authorization control on this exact path: [4](#0-3) 

When a DON node later responds with `MethodWebAPITrigger`, the gateway looks up `savedCallbacks[msg.Body.MessageID]` and forwards the result to whatever callback is currently registered under that key — with no verification that the response actually belongs to the original requester: [5](#0-4) 

Contrast this with the sibling `OutgoingConnectorHandler.responses` map, which explicitly rejects a duplicate ID (`already have response for id`) before creating a channel: [6](#0-5) 

`WebAPIHandler.savedCallbacks` has no equivalent duplicate-detection, so a second request using the same `MessageID` silently overwrites (`h.savedCallbacks[msg.Body.MessageID] = &savedCallback{...}`) the map entry for a still-pending, legitimate request.

### Impact Explanation
An unauthenticated/unprivileged client that can reach the gateway's user HTTP port (`/user`, confirmed public-facing in [7](#0-6) ) can:
1. Predict or brute-force an in-flight victim's `MessageID` (client-controlled values are frequently low-entropy or predictable, e.g. sequential IDs, timestamps, or simple strings as shown in the sample script [8](#0-7) ).
2. Send a second request with the identical `MessageID`, overwriting the victim's registered callback.
3. Receive the DON node's response payload that was intended for the victim's original request — a direct cross-user response confusion / information disclosure, and simultaneously the victim's original request is starved of its legitimate response (denial of service to the victim).

This matches the CVE class: an unprivileged actor intercepting/redirecting events meant for another party over a shared channel, without any privilege escalation needed.

### Likelihood Explanation
Likelihood is elevated because:
- The endpoint is explicitly internet/user-facing.
- The code comment at line 384 admits allowlisting/rate-limiting is not yet applied on this path.
- No authentication ties a `MessageID` to the calling identity — only a valid ECDSA signature (self-generated, trivially obtainable by any actor) is required to pass `Validate()`.
- The race window depends on guessing/matching an active MessageID, which is feasible if IDs are predictable or if the attacker floods with many guesses during high request volume.

### Recommendation
- Bind pending callbacks to a unique, gateway-generated correlation key (or at minimum the tuple of `(Sender, MessageID)`) rather than trusting the client-supplied `MessageID` alone.
- Reject requests attempting to reuse an already-pending `MessageID`, mirroring the duplicate check already present in `responses.new()` in `outgoing_connector_handler.go`.
- Implement the allowlist/rate-limiting noted as a TODO in `HandleLegacyUserMessage` before it reaches production traffic.

### Proof of Concept
1. Victim sends a legitimate `web_api_trigger` request to `POST /user` with `id: "X"`.
2. Before the DON node responds, attacker sends their own request to `POST /user` with the same `id: "X"` and a validly self-signed payload.
3. `HandleLegacyUserMessage` overwrites `savedCallbacks["X"]` with the attacker's callback.
4. The DON node's response for message `"X"` arrives at `handleWebAPITriggerMessage`, which looks up `savedCallbacks["X"]` — now the attacker's callback — and delivers the victim's intended response to the attacker's HTTP connection.

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

**File:** core/capabilities/webapi/outgoing_connector_handler.go (L449-462)
```go
func (r *responses) new(id string) (chan *api.Message, error) {
	r.mu.Lock()
	defer r.mu.Unlock()

	_, ok := r.chs[id]
	if ok {
		return nil, fmt.Errorf("already have response for id: %s", id)
	}

	// Buffered so we don't wait if sending
	ch := make(chan *api.Message, 1)
	r.chs[id] = ch
	return ch, nil
}
```

**File:** core/services/gateway/integration_tests/gateway_integration_test.go (L195-199)
```go
	userPort, nodePort := gateway.GetUserPort(), gateway.GetNodePort()
	userURL := fmt.Sprintf("http://localhost:%d/user", userPort)
	nodeURL := fmt.Sprintf("ws://localhost:%d/node", nodePort)
	require.Equal(t, http.StatusServiceUnavailable, getHTTPStatus(t, fmt.Sprintf("http://localhost:%d/health", userPort)))
	require.Equal(t, http.StatusOK, getHTTPStatus(t, fmt.Sprintf("http://localhost:%d/health", nodePort)))
```

**File:** core/scripts/gateway/web_api_trigger/invoke_trigger.go (L56-57)
```go
	messageID := flag.String("id", "12345", "Request ID")
	methodName := flag.String("method", "web_api_trigger", "Method name")
```
