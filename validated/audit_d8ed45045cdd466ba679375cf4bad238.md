## #Analysis Result

### Title
Unauthenticated Message-ID Collision Causes Cross-User Response Hijacking in Gateway WebAPI Trigger Handler - ([File: core/services/gateway/handlers/capabilities/handler.go])

### Summary
The Gateway's legacy WebAPI trigger handler stores pending-response callbacks in a shared map keyed solely by the client-supplied `MessageID`, with no ownership check before overwriting an existing entry. Any unprivileged client reaching the gateway's `/v2` legacy HTTP endpoint can submit a request whose `MessageID` collides with another user's in-flight request, hijacking the callback slot so that the next DON node response for that ID is delivered to the attacker instead of (or as well as) the legitimate requester.

### Finding Description
Incoming user requests are parsed by `gateway.ProcessRequest`, where the JSON-RPC request ID becomes `msg.Body.MessageID` directly from client input, with only a length check (≤200 chars) and no uniqueness enforcement: [1](#0-0) 

For legacy requests, this flows into `handler.HandleLegacyUserMessage`, which unconditionally writes into the shared `savedCallbacks` map keyed by `msg.Body.MessageID`, overwriting whatever was previously stored under that key without checking for an existing pending entry: [2](#0-1) 

When a DON node later responds with that same `MessageID`, `handleWebAPITriggerMessage` looks the ID up in `savedCallbacks`, deletes it, and forwards the response to whichever callback is currently registered for that ID — with no verification that the response actually corresponds to the original requester's session: [3](#0-2) 

This is a real gap relative to the newer v2 HTTP trigger handler, which explicitly rejects a request whose ID is already in-flight (`ErrConflict`, "requestID has already been used"): [4](#0-3) 

The legacy `handler.go` path has no equivalent check, so a second (malicious) request using the same `MessageID` as a pending, legitimate request silently replaces the saved callback.

### Impact Explanation
An unprivileged client can hijack the response destined for another user's in-flight WebAPI trigger request by submitting a colliding `MessageID`. Since the trigger response payload can carry externally-fetched data/results tied to another user's workflow request, this results in cross-user response confusion/disclosure — an attacker receives data intended for a victim's request. It can also cause denial of service for the legitimate requester, whose callback is silently dropped and who will instead simply time out.

### Likelihood Explanation
Exploitation only requires an unauthenticated/unprivileged client to send an HTTP request to the gateway's legacy `/v2` endpoint with a `MessageID` matching (or predicting/guessing/brute-forcing within a narrow window) another concurrently pending request's ID. Because `MessageID` is fully attacker-controlled and there is no per-sender or per-session binding on `savedCallbacks`, the only obstacle is timing/ID knowledge, which is feasible if IDs are predictable or if an attacker races many candidate IDs against high-traffic periods.

### Recommendation
In `HandleLegacyUserMessage` (and equivalently in `handler.dummy.go`'s `HandleLegacyUserMessage`), reject the request (return a conflict-style error, mirroring the v2 `httpTriggerHandler.setupCallback` behavior) if `msg.Body.MessageID` already exists in `savedCallbacks`, instead of silently overwriting the existing callback. Consider additionally binding responses to the original requester's connection/session context rather than relying purely on `MessageID` matching.

### Proof of Concept
1. Victim sends a legitimate WebAPI trigger request to the gateway's legacy endpoint with `MessageID = "X"`; `HandleLegacyUserMessage` stores victim's callback under key `"X"` in `savedCallbacks` and forwards the request to DON nodes.
2. Before the DON node responds, attacker sends their own legacy trigger request also using `MessageID = "X"`. `HandleLegacyUserMessage` overwrites `savedCallbacks["X"]` with the attacker's callback (`core/services/gateway/handlers/capabilities/handler.go:411-414`).
3. When a DON node returns its response tagged with `MessageID = "X"`, `handleWebAPITriggerMessage` looks up `savedCallbacks["X"]`, finds the attacker's callback, and delivers the victim's response data to the attacker (`core/services/gateway/handlers/capabilities/handler.go:148-161`).
4. The victim's original HTTP request either hangs until timeout or never receives a response.

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

**File:** core/services/gateway/handlers/capabilities/handler.go (L148-161)
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
```

**File:** core/services/gateway/handlers/capabilities/handler.go (L411-414)
```go
	h.mu.Lock()
	h.savedCallbacks[msg.Body.MessageID] = &savedCallback{id: msg.Body.MessageID, createdAt: time.Now(), Callback: callback}
	don := h.don
	h.mu.Unlock()
```

**File:** core/services/gateway/handlers/capabilities/v2/http_trigger_handler.go (L419-426)
```go
func (h *httpTriggerHandler) setupCallback(ctx context.Context, requestID string, callback handlers.Callback, requestStartTime time.Time, workflowID string) (<-chan struct{}, error) {
	h.callbacksMu.Lock()
	defer h.callbacksMu.Unlock()

	if _, found := h.callbacks[requestID]; found {
		h.handleUserError(ctx, requestID, jsonrpc.ErrConflict, fmt.Sprintf("requestID: %s has already been used. Ensure the requestID is unique for each request.", requestID), callback)
		return nil, fmt.Errorf("in-flight request ID: %s", requestID)
	}
```
