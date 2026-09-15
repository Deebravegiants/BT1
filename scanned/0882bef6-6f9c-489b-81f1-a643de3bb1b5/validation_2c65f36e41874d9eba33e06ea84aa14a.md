## Finding

### Title
Missing duplicate-check on client-supplied `MessageID` in the legacy WebAPI gateway handler allows cross-user response hijacking (`savedCallbacks` overwrite) - ([File: core/services/gateway/handlers/capabilities/handler.go])

### Summary
The Sherlock report describes a "current state, not actual contributor" bug: Uniswap's `donate()` rewards whichever LP position is *currently* in range at settlement time rather than the position that actually earned the reward, letting an attacker race the settlement to redirect value belonging to other participants. The same root-cause pattern — a shared, unauthenticated key used to attribute a result to "whoever currently owns that key" instead of the party that legitimately earned it — exists in the Chainlink Gateway's legacy WebAPI trigger handler, where the `savedCallbacks` map is keyed purely on the attacker/user-controlled `MessageID`, with no ownership check or duplicate-ID rejection before overwriting an in-flight entry.

### Finding Description
`HandleLegacyUserMessage` unconditionally stores the caller's callback under the client-supplied `msg.Body.MessageID`, with no check for whether an entry already exists for that ID: [1](#0-0) 

Unlike sibling handlers in the same codebase — e.g. the confidential relay handler, which explicitly rejects a request whose ID is already present (`"request ID already exists"`) — this handler performs no such guard: [2](#0-1) [3](#0-2) 

Later, when a DON node responds, the routing logic looks up and deletes whatever callback is *currently* stored for that `MessageID` and delivers the node's response to it — again with no verification that the responding message's sender/owner matches the original requester that registered the callback: [4](#0-3) 

Because `MessageID` is entirely chosen by the unprivileged external client (see test helper constructing `messageID := "12345"`), any unprivileged user can submit a legacy WebAPI trigger request using the same `MessageID` as another in-flight request: [5](#0-4) 

This is structurally identical to the DCA bug class: the "settlement" (delivering the node's response) is attributed based on *whichever party currently occupies the shared slot* (the map entry for a given ID) at the moment the event fires, not the party that actually initiated/earned it. An attacker can overwrite the map entry for a victim's `MessageID` just before the node responds, causing the node's response (intended for the victim) to be delivered to the attacker's callback instead — a direct cross-user response confusion.

### Impact Explanation
An unprivileged external user reachable through the internet-facing Gateway can hijack another user's pending trigger response by colliding on `MessageID`, receiving data/results meant for a different requester and/or silently dropping the legitimate user's response (denial of that specific request). This is a concrete "cross-user response confusion" as called out in the validation criteria, directly reachable from an unauthenticated/unprivileged client request path with no gateway allowlist or per-caller scoping protecting the `savedCallbacks` keyspace.

### Likelihood Explanation
Likelihood is moderate-to-high: exploitation requires only that the attacker know or predict the victim's `MessageID` and send a competing legacy request before the legitimate node response arrives — no cryptographic secret or privileged access is needed, since `MessageID` is fully client-chosen and the map key space is shared and global per handler instance. The absence of any duplicate-ID rejection (present in the sibling confidentialrelay/http_trigger handlers) indicates this path was not hardened the same way the others were.

### Recommendation
Add the same duplicate-`MessageID`/`RequestID` rejection used elsewhere in the gateway (`confidentialrelay` handler, `http_trigger_handler`) to `HandleLegacyUserMessage`: reject or fail the second request instead of silently overwriting the existing `savedCallbacks` entry. Additionally, consider scoping `MessageID` uniqueness per-sender (e.g., composite key of sender + MessageID) and validating that a node's response sender/context matches the original requester before dispatching to the stored callback.

### Proof of Concept
1. Victim sends a legacy WebAPI trigger request with `MessageID = "X"`; handler stores `savedCallbacks["X"] = victimCallback` and forwards to DON nodes.
2. Before a node responds, attacker sends their own signed legacy request also using `MessageID = "X"`; handler overwrites `savedCallbacks["X"] = attackerCallback` with no error (no duplicate check exists, per [6](#0-5) ).
3. A DON node's response for `MessageID = "X"` (destined for the victim's original request) arrives; `handleWebAPITriggerMessage` looks up `savedCallbacks["X"]`, finds the attacker's callback, deletes the entry, and delivers the node's response to the attacker ( [4](#0-3) ).
4. The victim's request now times out / never receives a response, while the attacker has received a response not intended for them.

### Citations

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

**File:** core/services/gateway/handlers/confidentialrelay/handler_test.go (L863-881)
```go
func TestConfidentialRelayHandler_DuplicateRequestID(t *testing.T) {
	t.Parallel()
	h, cb, don, _ := setupHandler(t, 4)
	don.On("SendToNode", mock.Anything, mock.Anything, mock.Anything).Return(nil)

	params := json.RawMessage(`{"workflow_id":"wf1"}`)
	req := jsonrpc.Request[json.RawMessage]{
		ID:     "req-dup",
		Method: MethodCapabilityExec,
		Params: &params,
	}

	err := h.HandleJSONRPCUserMessage(t.Context(), req, cb)
	require.NoError(t, err)

	cb2 := common.NewCallback()
	err = h.HandleJSONRPCUserMessage(t.Context(), req, cb2)
	require.ErrorContains(t, err, "request ID already exists")
}
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

**File:** core/services/gateway/handlers/capabilities/handler_test.go (L193-234)
```go
func triggerRequest(t *testing.T, key *ecdsa.PrivateKey, topics []string, methodName, timestamp, payload string) *api.Message {
	messageID := "12345"
	if methodName == "" {
		methodName = MethodWebAPITrigger
	}
	if timestamp == "" {
		timestamp = strconv.FormatInt(time.Now().Unix(), 10)
	}
	donID := "workflow_don_1"
	var payloadJSON []byte
	if payload == "" {
		ts, err := strconv.ParseInt(timestamp, 10, 64)
		require.NoError(t, err)
		reqPayload := webapicap.TriggerRequestPayload{
			TriggerId:      "web-api-trigger@1.0.0",
			TriggerEventId: "action_1234567890",
			Timestamp:      ts,
			Topics:         topics,
			Params: webapicap.TriggerRequestPayloadParams(map[string]any{
				"bid": "101",
				"ask": "102",
			}),
		}
		payloadJSON, err = json.Marshal(reqPayload)
		require.NoError(t, err)
	} else {
		payloadJSON = []byte(payload)
	}
	msg := &api.Message{
		Body: api.MessageBody{
			MessageID: messageID,
			Method:    methodName,
			DonID:     donID,
			Payload:   json.RawMessage(payloadJSON),
		},
	}
	err := msg.Sign(key)
	require.NoError(t, err)
	err = msg.Validate()
	require.NoError(t, err)
	return msg
}
```
