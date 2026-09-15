Audit Report

## Title
Unauthenticated MessageID collision in legacy WebAPI trigger handler causes response misdelivery/loss - (File: `core/services/gateway/handlers/capabilities/handler.go`)

## Summary
`HandleLegacyUserMessage` registers a caller's response callback in `h.savedCallbacks` keyed solely by the caller-supplied `MessageID`, with an unconditional overwrite and no duplicate/in-flight check, unlike the newer v2 HTTP trigger handler which explicitly rejects ID reuse. A second, unrelated request using the same `MessageID` silently evicts the first caller's callback before the DON responds, causing the original caller's response to be lost and delivered to the wrong party instead.

## Finding Description
The legacy handler stores the callback unconditionally: [1](#0-0) 

There is no check for an existing, non-expired entry before this assignment — anywhere between decoding the message and this store, no code validates uniqueness of `msg.Body.MessageID` (only method/timestamp/staleness checks are present). This is in stark contrast to the v2 handler, which has an explicit "in-flight request" rejection path exercised by its own test suite: [2](#0-1) 

When a node responds, dispatch is purely by map lookup/delete on `MessageID`, delivering to whatever callback is currently registered under that key, without any verification that the response actually belongs to the currently-registered caller: [3](#0-2) 

`MessageID` is client-controlled, arriving directly from the JSON-RPC request `ID` on the wire and only checked for length (≤200 chars) at gateway ingress: [4](#0-3) 

Orphaned callbacks (from the original caller whose slot was overwritten) sit unnoticed until `pruneCallbacks` sweeps them after `CallbackMaxAgeSec` (120s default): [5](#0-4) [6](#0-5) 

## Impact Explanation
This is a legitimate cross-user response corruption issue in the gateway, mapping directly to the "cross-user response corruption" in-scope impact category. Concretely:
- The original caller's request is silently orphaned, receiving no response until the 120-second prune window expires (denial of service for that request).
- A second caller who reuses (deliberately or via collision) an in-flight `MessageID` receives the DON's response intended for the original, unrelated workflow invocation — a genuine cross-user response misdelivery.

This is a real, code-confirmed logic gap, not a theoretical claim: the legacy path lacks the exact safeguard the codebase's own newer v2 handler implements and tests for.

## Likelihood Explanation
The gateway's legacy webapi-trigger endpoint accepts unauthenticated/unprivileged client requests, and `MessageID` is fully caller-chosen. Triggering the race only requires sending two requests with the same `MessageID` before the first is answered — a straightforward, remotely-triggerable race given realistic gateway→DON→gateway round-trip latency. No privileged access, credential leakage, or host access is required.

## Recommendation
Add the same in-flight/duplicate `MessageID` protection that the v2 HTTP trigger handler already implements to the legacy handler in `core/services/gateway/handlers/capabilities/handler.go`: reject (rather than silently overwrite) a new registration when a non-expired `savedCallbacks` entry already exists for the same `MessageID`, and/or scope the map key by sender/signer identity in addition to `MessageID`.

## Proof of Concept
1. Attacker sends legacy request R1 with `Body.MessageID = "X"`; gateway stores `savedCallbacks["X"] = cb1` at `handler.go:412` and forwards R1 to DON members.
2. Before any node responds, attacker (or any other unprivileged client) sends legacy request R2 with the same `Body.MessageID = "X"`; the gateway overwrites `savedCallbacks["X"] = cb2`, silently discarding `cb1`.
3. When the DON node responds for R1 with `MessageID = "X"`, `handleWebAPITriggerMessage` (`handler.go:148-161`) looks up `savedCallbacks["X"]`, finds `cb2`, and delivers R1's response to the caller of R2. The original caller (`cb1`) receives nothing and times out after `CallbackMaxAgeSec` (120s), when `pruneCallbacks` removes the orphaned entry.
4. A Go unit test mirroring `http_trigger_handler_test.go`'s "duplicate request ID" case, adapted to `handler_test.go` for `HandleLegacyUserMessage`, would demonstrate that no error is returned on the second registration and that `cb1` never receives a response while `cb2` receives R1's response.

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
