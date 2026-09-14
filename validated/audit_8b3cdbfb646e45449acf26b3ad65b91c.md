### Title
Legacy Web API Trigger Handler Callback Overwrite Enables Cross-Client Response Misdelivery - (File: `core/services/gateway/handlers/capabilities/handler.go`)

### Summary
The Gateway's legacy web-API-trigger handler stores a per-request callback in a shared map keyed solely by the client-supplied `MessageID`, with no check for an existing in-flight entry with the same key. Any unprivileged client hitting the gateway (e.g. any workflow/external-initiator caller of `HandleLegacyUserMessage`) can choose an arbitrary `MessageID`. If two concurrent requests reuse the same `MessageID`, the second overwrites the first's saved callback, and the DON node's later response for one caller is delivered to the other caller's callback — mirroring the UMA report's root cause (a callback invoked on/delivered to the wrong party) but here manifesting as cross-client response confusion at the gateway boundary.

### Finding Description
`HandleLegacyUserMessage` registers a callback for the incoming request keyed only by the message's `MessageID` field, which is fully attacker/caller controlled: [1](#0-0) 

There is no uniqueness/collision check before this assignment (unlike the newer v2 HTTP trigger handler, which explicitly rejects duplicate in-flight request IDs): [2](#0-1) 

When a node later responds, the gateway looks up and deletes the callback purely by `MessageID` and forwards whatever response arrives first to whichever callback is currently registered under that ID: [3](#0-2) 

Because the `handler` struct's `savedCallbacks` map is shared across all callers of a DON and keyed with no caller/session binding, a request from client B using the same `MessageID` as an in-flight request from client A silently replaces A's registered callback. Both requests are still dispatched to the DON's nodes: [4](#0-3) 

Consequently, whichever node response arrives first for that `MessageID` is routed to B's callback (even if it corresponds to A's original request), while A's request is either answered with B's unrelated response or never completed. This is structurally analogous to the UMA `proposePriceFor` bug: a response/callback intended for the original requester is instead delivered to a different party due to insufficient binding between the response and the correct recipient.

### Impact Explanation
An unprivileged client can cause responses belonging to another client's in-flight webhook/trigger request to be delivered to itself (or vice versa), leading to cross-user response confusion. Depending on what data the observation-source pipeline returns (e.g., HTTP fetch results, bridge responses), this could leak the content of another user's job-run response to an unrelated caller, or cause a legitimate caller to silently receive no response (denial of service for that specific request) while an attacker's later request "steals" the node's answer.

### Likelihood Explanation
Exploitation only requires an unprivileged party able to send a `web_api_trigger` legacy message (e.g. via an external initiator) to the gateway with a `MessageID` chosen to match another concurrently in-flight request. `MessageID` values are short-lived and could collide by ill intent (attacker deliberately reuses a predictable/observed ID) or in high-concurrency environments where clients pick colliding IDs. No signature/session binding ties the saved callback to the original caller, so the race is straightforward to trigger deliberately.

### Recommendation
Bind each entry in `savedCallbacks` to the requester's identity/session in addition to `MessageID` (e.g., include a caller-specific namespace or reject/queue duplicate in-flight `MessageID`s, as already done in `httpTriggerHandler.HandleUserTriggerRequest`'s "duplicate request ID" check). At minimum, `HandleLegacyUserMessage` should check for and reject an already-registered `MessageID` before overwriting it, and callback delivery should validate that the response actually corresponds to the caller who registered the callback.

### Proof of Concept
1. Client A sends a legacy `web_api_trigger` message to the gateway with `MessageID = "X"`; the gateway stores A's callback under `savedCallbacks["X"]` and forwards the request to all DON nodes.
2. Before any node responds, Client B sends another legacy `web_api_trigger` message also with `MessageID = "X"`; the gateway overwrites `savedCallbacks["X"]` with B's callback and forwards B's request to the same nodes.
3. A node finishes processing A's original request first and returns a response with `MessageID = "X"`; `handleWebAPITriggerMessage` looks up `savedCallbacks["X"]`, finds B's callback, deletes the entry, and sends A's result to B.
4. Client A never receives a response (its callback was overwritten), while Client B receives a response corresponding to Client A's request instead of its own.

### Citations

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

**File:** core/services/gateway/handlers/capabilities/v2/http_trigger_handler_test.go (L320-358)
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
	})
```
