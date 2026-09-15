## Analog Found

### Title
Global, unscoped `requestID` keying in `httpTriggerHandler.setupCallback` allows any unprivileged caller to DoS or collide with another user's in-flight workflow trigger request - (File: core/services/gateway/handlers/capabilities/v2/http_trigger_handler.go)

### Summary
The external report describes `checkLastBlockAction` in LockZap gating deposits with a single global slot keyed only by `msg.sender` and `block.number`, so one legitimate action blocks all subsequent legitimate actions from unrelated users sharing that resource in the same block. The Chainlink Gateway's HTTP trigger handler has the same root-cause pattern: a single global, unscoped tracking map (`h.callbacks`) keyed **only** by the user-supplied `requestID`, with no namespacing by workflow, workflow owner, org, or caller identity.

### Finding Description
`httpTriggerHandler.setupCallback` stores every in-flight trigger request in a single map keyed purely by the client-supplied `req.ID`: [1](#0-0) 

`req.ID` is fully attacker/user-controlled input (it comes straight from the JSON-RPC request the caller sends) and is only checked for non-emptiness and absence of `/`: [2](#0-1) 

Because the `callbacks` map has no per-workflow, per-owner, or per-org partitioning, any unprivileged caller (workflow owner A) can pick a `requestID` that another unprivileged caller (workflow owner B) is currently using for an in-flight request to a completely different workflow. The second caller to arrive is rejected with `jsonrpc.ErrConflict`: [3](#0-2) 

This is confirmed by the handler's own test, which shows a second, unrelated `HandleUserTriggerRequest` call with the same `requestID` is unconditionally rejected while the first is in flight, purely due to the shared global key: [4](#0-3) 

Responses are routed back solely by this same global `resp.ID` key in `HandleNodeTriggerResponse`, with the only additional check being which shard/DON the responding node belongs to — not which user/workflow originally issued the request: [5](#0-4) 

This mirrors the LockZap bug class exactly: a shared, globally-scoped guard (there: `_callerLastBlockAction[msg.sender]`/block; here: `h.callbacks[requestID]`) that should have been scoped per-actor/session but instead affects unrelated legitimate users of the same shared resource (the Gateway node), causing spurious rejections whenever two independent, unprivileged users happen to choose the same `requestID`.

### Impact Explanation
An unprivileged client can grief another unprivileged client's workflow execution requests by deliberately reusing (or brute-forcing/guessing) a `requestID` while the victim's request is in flight, causing the victim's legitimate `workflows.execute` call to be silently blocked with a Conflict error until the attacker's own request completes or is reaped. This is a request-level denial-of-service against legitimate users sharing the same Gateway node, and could also occur accidentally between independent, well-behaved workflows that both use predictable/short IDs (e.g., incrementing counters, "1", "test"), causing unrelated production workflow executions to fail non-deterministically.

### Likelihood Explanation
Likelihood is limited by the requirement that two callers' `requestID`s collide during the same in-flight window (bounded by `CleanUpPeriodMs`/max trigger duration). This can happen unintentionally with poor ID hygiene, or intentionally if an attacker can predict or observe a victim's `requestID` (e.g., via shared/predictable ID schemes, or simply spamming common IDs) and race a request through the gateway to occupy the slot.

### Recommendation
Scope the `callbacks` map key by more than the raw `requestID` — e.g., combine `requestID` with `workflowID`/`workflowOwner` (similar to how `legacyExecutionID`/`executionIDWithTriggerIndex` are already derived) before using it as the map key in `setupCallback`, `cleanupCallback`, `reapExpiredCallbacks`, and `HandleNodeTriggerResponse`. This ensures request-ID collisions across unrelated workflows/owners cannot cause spurious rejections or misrouting between users.

### Proof of Concept
1. Workflow owner A sends `workflows.execute` with `id: "abc"` targeting `workflowID_A`; `setupCallback` inserts `h.callbacks["abc"]`.
2. Before A's request completes/reaps, workflow owner B (unrelated, different workflow/org) sends `workflows.execute` with the same `id: "abc"` targeting `workflowID_B`.
3. `setupCallback` finds `"abc"` already present and rejects B's legitimate request with `jsonrpc.ErrConflict` ("requestID: abc has already been used"), even though B's request has nothing to do with A's workflow — as reproduced by the existing `duplicate request ID` test case using two independent `Callback` objects against the same global map.

### Citations

**File:** core/services/gateway/handlers/capabilities/v2/http_trigger_handler.go (L190-202)
```go
func (h *httpTriggerHandler) validateRequestID(ctx context.Context, requestID string, callback handlers.Callback) error {
	if requestID == "" {
		h.handleUserError(ctx, requestID, jsonrpc.ErrInvalidRequest, "'id' field is required and cannot be empty. Use a new unique request 'id' for each request", callback)
		return errors.New("empty request ID")
	}
	// Request IDs from users must not contain "/", since this character is reserved
	// for internal node-to-node message routing (e.g., "http_action/{workflowID}/{uuid}").
	if strings.Contains(requestID, "/") {
		h.handleUserError(ctx, requestID, jsonrpc.ErrInvalidRequest, "request ID must not contain '/'", callback)
		return errors.New("request ID must not contain '/'")
	}
	return nil
}
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

**File:** core/services/gateway/handlers/capabilities/v2/http_trigger_handler.go (L474-497)
```go
func (h *httpTriggerHandler) HandleNodeTriggerResponse(ctx context.Context, resp *jsonrpc.Response[json.RawMessage], nodeAddr string) error {
	h.lggr.Debugw("handling trigger response", "requestID", resp.ID, "nodeAddr", nodeAddr, "error", resp.Error, "result", resp.Result)
	h.callbacksMu.Lock()
	defer h.callbacksMu.Unlock()
	saved, exists := h.callbacks[resp.ID]
	if !exists {
		return errors.New("callback not found for request ID: " + resp.ID)
	}
	if saved.processed {
		h.lggr.Debugw("request already processed, ignoring late response", "requestID", resp.ID, "nodeAddr", nodeAddr)
		return nil
	}

	// Route the response into the aggregator for the shard that owns this node.
	shard, ok := h.nodeAddrToShard[nodeAddr]
	if !ok {
		return fmt.Errorf("received trigger response from unknown node %s (no owning shard)", nodeAddr)
	}
	agg, ok := saved.responseAggregators[shard.donID]
	if !ok {
		// The node belongs to a shard this workflow isn't assigned to (or the
		// callback was captured before the workflow was assigned there).
		return fmt.Errorf("node %s (shard %s) is not assigned to workflow for request ID %s", nodeAddr, shard.donID, resp.ID)
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
