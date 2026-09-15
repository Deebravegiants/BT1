## Analysis

The Sherlock report describes a class of bug where a resource that should be routed back to the party who initiated an action is instead lost/stuck because the code that tracks "what belongs to whom" doesn't account for overwritten/competing state. The closest reachable analog in this repo is in the Gateway's legacy webapi-trigger callback bookkeeping.

### Root cause

`core/services/gateway/handlers/capabilities/handler.go`'s `HandleLegacyUserMessage` stores the caller's response `callback` keyed **only** by the user-supplied `msg.Body.MessageID`, with an unconditional overwrite and no uniqueness/in-flight check: [1](#0-0) 

Compare this to the newer v2 HTTP trigger handler, which explicitly guards against ID reuse and rejects a second request sharing an in-flight ID: [2](#0-1) 

The legacy handler has no equivalent check. `MessageID` is fully attacker/caller chosen (it becomes the JSON-RPC request `ID` decoded straight from the wire in `gateway.ProcessRequest`, only bounded by a 200-character length check): [3](#0-2) 

When a node eventually responds, dispatch is purely by `MessageID` lookup/delete in the shared map, and the *first* node response found for that ID is delivered to whatever callback currently occupies that slot: [4](#0-3) 

### Vulnerability

Any unprivileged caller submitting a legacy `web_api_trigger` request can deliberately choose (or race to collide with) a `MessageID` that is already in flight for another caller/workflow. Because `savedCallbacks[msg.Body.MessageID] = &savedCallback{...}` overwrites silently:

- The **original** caller's callback entry is evicted and replaced. When the DON node's genuine response for the original request arrives, it is matched by `MessageID` and delivered to whichever callback is currently registered — i.e., the second (attacker/colliding) caller — a direct cross-user response confusion.
- The original caller receives **no response at all** and hangs until `defaultCallbackMaxAgeSec` (120s) elapses and `pruneCallbacks` silently drops the orphaned entry: [5](#0-4) [6](#0-5) 

This mirrors the report's bug class exactly: a value that should flow back to its rightful originator (there, LP tokens; here, the trigger response) gets stuck/misdirected because the bookkeeping key can be hijacked/collided by another (also unprivileged) party, with no ownership check tying the response back to the correct caller.

### Title
Unauthenticated MessageID collision in legacy WebAPI trigger handler causes response misdelivery/loss - (File: `core/services/gateway/handlers/capabilities/handler.go`)

### Summary
`HandleLegacyUserMessage` registers a caller's response callback in `h.savedCallbacks` keyed solely by the caller-supplied `MessageID`, with no duplicate/in-flight check (unlike the v2 handler). A second, unrelated request using the same `MessageID` silently overwrites the first caller's callback entry before the DON responds.

### Finding Description
`MessageID` originates directly from the client-controlled JSON-RPC request `ID` and is only length-checked (≤200 chars) at the gateway ingress (`core/services/gateway/gateway.go`, `ProcessRequest`). No component verifies that a `MessageID` is unique, session-bound, or tied to the sender's identity before it's used as the sole map key for the response callback in `HandleLegacyUserMessage` (`core/services/gateway/handlers/capabilities/handler.go:411-414`). When the node later replies, `handleWebAPITriggerMessage` looks up and deletes `h.savedCallbacks[msg.Body.MessageID]` and forwards the response to whatever callback is currently stored there (`handler.go:148-161`) — it never verifies that the response is actually destined for the caller currently registered under that key.

### Impact Explanation
- Denial of service / lost response for the original caller: their request is silently orphaned and only cleaned up after `CallbackMaxAgeSec` (default 120s), during which the caller receives nothing.
- Cross-user response confusion: a second caller who (deliberately or accidentally) reuses an in-flight `MessageID` receives the DON's response intended for a completely different workflow/trigger invocation.
- Because the gateway is the internet-facing entry point and callers are unauthenticated at this layer for the legacy path, this is exploitable by any unprivileged HTTP client hitting the legacy webapi-trigger endpoint.

### Likelihood Explanation
Exploitability only requires an attacker to send two `web_api_trigger` requests with an identical `MessageID` before the first is answered by the DON — a race condition that is trivial to win from a remote unprivileged client (send request A, then immediately send request B with the same ID). No authentication bypass or cryptographic break is required; the only "difficulty" is winning the timing race, which is straightforward given the multi-hop gateway → DON → gateway round trip latency.

### Recommendation
Enforce the same in-flight/duplicate `MessageID` protection used by the v2 HTTP trigger handler (`core/services/gateway/handlers/capabilities/v2/http_trigger_handler.go`) in the legacy handler: reject (rather than overwrite) a new registration when an existing, non-expired `savedCallbacks` entry already exists for the same `MessageID`, and/or scope the key by sender/signer identity in addition to `MessageID`.

### Proof of Concept
1. Attacker sends legacy request R1 with `Body.MessageID = "X"`, targeting DON A; the gateway stores `savedCallbacks["X"] = cb1` and forwards R1 to all DON members.
2. Before DON A responds, attacker (or any other unprivileged client) sends legacy request R2 with the same `Body.MessageID = "X"`, targeting DON B (or any DON); the gateway overwrites `savedCallbacks["X"] = cb2` (`handler.go:412`), discarding `cb1` with no error.
3. DON A eventually responds for R1 with `MessageID = "X"`. `handleWebAPITriggerMessage` looks up `savedCallbacks["X"]`, finds `cb2`, deletes the entry, and delivers R1's response to `cb2` — the caller of R2 — while the original caller of R1 (`cb1`) never receives anything and times out after `CallbackMaxAgeSec`.

### Citations

**File:** core/services/gateway/handlers/capabilities/handler.go (L43-46)
```go
	defaultCallbackMaxAgeSec        = 120   // 2 minutes
	defaultMaxSavedCallbacks        = 20000 // could briefly exceed under heavy load
	defaultCallbackPruneIntervalSec = 30
)
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

**File:** core/services/gateway/handlers/capabilities/handler.go (L299-312)
```go
func (h *handler) pruneCallbacks() {
	h.mu.Lock()
	defer h.mu.Unlock()

	// First, remove expired callbacks.
	maxAge := time.Duration(h.config.CallbackMaxAgeSec) * time.Second
	now := time.Now()
	var expired int
	for id, cb := range h.savedCallbacks {
		if now.Sub(cb.createdAt) > maxAge {
			delete(h.savedCallbacks, id)
			expired++
		}
	}
```

**File:** core/services/gateway/handlers/capabilities/handler.go (L411-414)
```go
	h.mu.Lock()
	h.savedCallbacks[msg.Body.MessageID] = &savedCallback{id: msg.Body.MessageID, createdAt: time.Now(), Callback: callback}
	don := h.don
	h.mu.Unlock()
```

**File:** core/services/gateway/handlers/capabilities/v2/http_trigger_handler_test.go (L320-357)
```go
	t.Run("duplicate request ID", func(t *testing.T) {
		handler, mockDon := createTestTriggerHandler(t)
		privateKey := createTestPrivateKey(t)
		registerWorkflow(t, handler, workflowID, privateKey)
		callback1 := hc.NewCallback()
		callback2 := hc.NewCallback()

		triggerReq := gateway_common.HTTPTriggerRequest{
			Workflow: gateway_common.WorkflowSelector{
				WorkflowID: workflowID,
			},
			Input: []byte(`{"key": "value"}`),
		}
		reqBytes, err := json.Marshal(triggerReq)
		require.NoError(t, err)

		rawParams := json.RawMessage(reqBytes)
		req := &jsonrpc.Request[json.RawMessage]{
			Version: "2.0",
			ID:      requestID,
			Method:  gateway_common.MethodWorkflowExecute,
			Params:  &rawParams,
		}
		// First request should succeed
		req.Auth = createTestJWTToken(t, req, privateKey)
		mockDon.EXPECT().SendToNode(mock.Anything, mock.Anything, mock.Anything).Return(nil).Times(3)
		err = handler.HandleUserTriggerRequest(t.Context(), req, callback1, time.Now())
		require.NoError(t, err)

		// Second request with same ID should fail
		req.Auth = createTestJWTToken(t, req, privateKey)
		err = handler.HandleUserTriggerRequest(t.Context(), req, callback2, time.Now())
		require.Error(t, err)
		require.Contains(t, err.Error(), "in-flight request")

		r, err := callback2.Wait(t.Context())
		require.NoError(t, err)
		requireUserErrorSent(t, r, jsonrpc.ErrConflict)
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
