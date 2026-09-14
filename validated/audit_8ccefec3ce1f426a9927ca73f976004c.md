### Title
Gateway `DummyHandler` allows response hijacking via attacker-controlled `MessageID` collision (session ID replay analog) - ([File: core/services/gateway/handlers/handler.dummy.go])

### Summary
The Gateway's `dummyHandler` stores the per-request callback keyed only by the client-supplied `MessageID`, and overwrites any existing entry for that key without checking whether it is already in use or verifying ownership — the exact bug class described in the MCP Ruby SDK advisory (`store_stream_for_session` silently overwriting an existing session's stream). Every other handler in the same package (`vault`, `confidentialrelay`, `capabilities/v2` HTTP trigger handler) explicitly rejects a request when the ID is already in-flight; `dummyHandler` does not.

### Finding Description
`dummyHandler.HandleLegacyUserMessage` unconditionally overwrites the saved callback map entry keyed by `msg.Body.MessageID`: [1](#0-0) 

`MessageID` is derived directly from the JSON-RPC request `ID` supplied by the calling client via `gateway.ProcessRequest`: [2](#0-1) 

There is no uniqueness/ownership check before the write — the second write silently replaces the first entry in `d.savedCallbacks`. When a node eventually responds with that `MessageID`, `HandleNodeMessage` looks up whatever `savedCallback` is currently stored under that key and routes the response there, deleting the entry: [3](#0-2) 

This mirrors the vulnerable "overwrite by key" pattern in the advisory. By contrast, the vault handler and the v2 HTTP trigger handler treat a duplicate/in-flight ID as a conflict and reject the new request instead of overwriting the existing callback: [4](#0-3) [5](#0-4) 

The absence of this check in `dummyHandler` means an unprivileged client can supply a `MessageID` that collides with another in-flight user's request (or simply guess/reuse a commonly-used ID), causing the second registrant's callback to "steal" ownership of that key. When the DON node eventually replies to the original request, `HandleNodeMessage` will deliver the response to whichever caller is currently registered under that ID — the attacker.

### Impact Explanation
If an attacker submits a request through this handler using a `MessageID` value that collides with another (legitimate) user's in-flight request, the eventual node response for that ID is delivered to the attacker's callback instead of the legitimate requester's, and the legitimate requester never receives a response (silent request/response hijack — cross-user response confusion, CWE-384/639 analog). Depending on what the `dummyHandler`-routed DON/capability returns, this could expose data intended for another user.

### Likelihood Explanation
Exploitability depends on the attacker being able to predict or race a `MessageID` value used by a legitimate in-flight request to this specific handler; the gateway does impose a length-limit on request IDs but does not otherwise validate uniqueness for the `dummyHandler`. Because `dummyHandler` is explicitly documented as "forwards each request/response without doing any checks", it is plausible this is intended for internal/test wiring rather than a fully "user-facing" service, so real-world exploitability depends on which gateway deployments route external/unprivileged traffic to a DON configured with this handler. This uncertainty could not be fully resolved from the indexed code available.

### Recommendation
In `dummyHandler.HandleLegacyUserMessage`, before inserting into `d.savedCallbacks`, check whether an entry for `msg.Body.MessageID` already exists and reject the request (mirroring the `vault`/`v2 http_trigger_handler` "request ID already exists" pattern) instead of silently overwriting it.

### Proof of Concept
1. Configure a DON to use `NewDummyHandler`.
2. Client A sends a JSON-RPC request through the gateway with `ID = "X"`, which is dispatched to the DON and its callback saved under `savedCallbacks["X"]`.
3. Before the node responds, Client B (attacker) sends a request with the same `ID = "X"`; `HandleLegacyUserMessage` overwrites `savedCallbacks["X"]` with Client B's callback.
4. When the node responds with `MessageID = "X"`, `HandleNodeMessage` retrieves and deletes the entry currently stored for `"X"` — Client B's callback — and delivers Client A's intended response data to Client B.

### Citations

**File:** core/services/gateway/handlers/handler.dummy.go (L62-66)
```go
func (d *dummyHandler) HandleLegacyUserMessage(ctx context.Context, msg *api.Message, callback Callback) error {
	d.mu.Lock()
	d.savedCallbacks[msg.Body.MessageID] = &savedCallback{msg.Body.MessageID, callback}
	don := d.don
	d.mu.Unlock()
```

**File:** core/services/gateway/handlers/handler.dummy.go (L84-109)
```go
func (d *dummyHandler) HandleNodeMessage(ctx context.Context, resp *jsonrpc.Response[json.RawMessage], nodeAddr string) error {
	var msg api.Message
	err := json.Unmarshal(*resp.Result, &msg)
	if err != nil {
		return err
	}
	msg.Body.MessageID = resp.ID
	err = msg.Validate()
	if err != nil {
		return err
	}
	if nodeAddr != msg.Body.Sender {
		return fmt.Errorf("node address %s does not match message sender %s", nodeAddr, msg.Body.Sender)
	}
	d.mu.Lock()
	savedCb, found := d.savedCallbacks[msg.Body.MessageID]
	delete(d.savedCallbacks, msg.Body.MessageID)
	d.mu.Unlock()

	if found {
		// Send first response from a node back to the user, ignore any other ones.
		codec := api.JSONRPCCodec{}
		return savedCb.SendResponse(UserCallbackPayload{RawResponse: codec.EncodeLegacyResponse(&msg), ErrorCode: api.NoError})
	}
	return nil
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

**File:** core/services/gateway/handlers/vault/handler.go (L457-472)
```go
func (h *handler) newActiveRequest(req jsonrpc.Request[json.RawMessage], callback gwhandlers.Callback) (*activeRequest, error) {
	h.mu.Lock()
	defer h.mu.Unlock()
	if h.activeRequests[req.ID] != nil {
		h.lggr.Errorw("request id already exists", "requestID", req.ID)
		return nil, errors.New("request ID already exists: " + req.ID)
	}
	ar := &activeRequest{
		Callback:  callback,
		req:       req,
		createdAt: h.clock.Now(),
		responses: map[string]*jsonrpc.Response[json.RawMessage]{},
	}
	h.activeRequests[req.ID] = ar
	return ar, nil
}
```

**File:** core/services/gateway/handlers/capabilities/v2/http_trigger_handler.go (L419-427)
```go
func (h *httpTriggerHandler) setupCallback(ctx context.Context, requestID string, callback handlers.Callback, requestStartTime time.Time, workflowID string) (<-chan struct{}, error) {
	h.callbacksMu.Lock()
	defer h.callbacksMu.Unlock()

	if _, found := h.callbacks[requestID]; found {
		h.handleUserError(ctx, requestID, jsonrpc.ErrConflict, fmt.Sprintf("requestID: %s has already been used. Ensure the requestID is unique for each request.", requestID), callback)
		return nil, fmt.Errorf("in-flight request ID: %s", requestID)
	}

```
