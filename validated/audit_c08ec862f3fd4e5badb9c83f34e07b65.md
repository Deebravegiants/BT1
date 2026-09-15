## Analog Found

### Title
Global, unscoped `requestID` keyspace in the HTTP trigger handler allows an authenticated attacker to squat a victim's request ID and DOS their workflow execution — ([File: core/services/gateway/handlers/capabilities/v2/http_trigger_handler.go])

### Summary
The Dinari report's root cause is that order IDs are derived only from user-supplied, non-unique data (no sender binding), so an attacker can predict/observe another user's ID and race to consume it first, causing the victim's legitimate request to be rejected. The same pattern exists in the gateway's `httpTriggerHandler`: the in-flight-request map `callbacks` is keyed **solely by the client-supplied JSON-RPC `req.ID` string**, with no binding to the workflow owner, workflow ID, or any Caller identity [1](#0-0) .

### Finding Description
`HandleUserTriggerRequest` validates and authorizes the request, then calls `setupCallback(ctx, req.ID, callback, requestStartTime, workflowID)` [2](#0-1) . Inside `setupCallback`, the only uniqueness check performed is a lookup into the single global map `h.callbacks` keyed by the raw `requestID` string:

```go
if _, found := h.callbacks[requestID]; found {
    h.handleUserError(ctx, requestID, jsonrpc.ErrConflict, fmt.Sprintf("requestID: %s has already been used...", requestID), callback)
    return nil, fmt.Errorf("in-flight request ID: %s", requestID)
}
``` [3](#0-2) 

The only constraint placed on `requestID` is that it must be non-empty and must not contain `/` [4](#0-3) . There is no per-workflow, per-owner, or per-caller namespacing of this key — any authenticated caller (for any workflow they're entitled to trigger) shares the exact same ID keyspace as every other caller/workflow in the gateway instance.

This mirrors the Dinari bug precisely: the ID that guards against duplicate/conflicting in-flight requests is derived purely from attacker-visible/attacker-choosable data, with no sender-binding. An attacker who can predict or observe (e.g. via an application's client-side code, documentation examples, shared automation scripts, or simply guessing common patterns like `"1"`, timestamps, or sequential IDs) the `requestID` a victim's workflow-triggering client is about to use can pre-emptively submit a request with that same ID for a workflow the attacker itself controls/is authorized on. Because `setupCallback` runs its uniqueness check before delivering to nodes, the victim's real, legitimate request will be rejected with `ErrConflict`/`"in-flight request"` [5](#0-4) , exactly the DOS/duplicate-order sandwich pattern from the report (front-run with the same ID, causing the victim's transaction/request to fail).

The handler test file explicitly documents this exact behavior for same-ID collisions (though only tested with same workflow) [6](#0-5) , confirming the map is checked by `requestID` alone before any workflow/owner disambiguation occurs.

### Impact Explanation
An attacker with valid credentials for any workflow can deny service to a specific victim's workflow execution attempt by squatting their request ID window, without needing knowledge of the victim's authorization key/JWT — only the string ID. Given HTTP trigger endpoints are typically invoked by external client applications with predictable ID generation (sequential counters, timestamps, or reused constants across retries), collisions are plausible in practice and let a bad actor selectively block a targeted workflow's inbound trigger.

### Likelihood Explanation
Requires the attacker to (a) be an authorized caller for some workflow (a normal, low-privilege prerequisite for this gateway API) and (b) predict/observe the victim's `requestID` and race it before the victim's request arrives — a similar difficulty/likelihood profile to the original mempool front-run, though here it depends on ID predictability rather than public mempool visibility. Likelihood is Medium: it is not automatically exploitable against arbitrary strangers, but it is a design flaw that removes a defense-in-depth boundary that should exist (per-owner/workflow scoping) and is trivially exploitable whenever an attacker can infer or brute-force IDs from client behavior.

### Recommendation
Scope the `callbacks` map key by workflow identity in addition to `requestID`, e.g. `key := workflowID + ":" + requestID` or a `struct{ workflowID, requestID string }` composite key (analogous to how `vaulttypes.RequestIDSeparator`-based owner-prefixing is already used to prevent cross-owner ID collisions in the vault handler [7](#0-6) ). This ensures request-ID uniqueness is only enforced within a caller's own workflow namespace, eliminating the possibility of a differently-authorized caller squatting a victim's ID.

### Proof of Concept
1. Attacker holds valid auth for `workflowA` (their own workflow).
2. Attacker learns/predicts that a victim's client will submit `HandleUserTriggerRequest` with `req.ID = "order-42"` for `workflowB`.
3. Attacker calls `HandleUserTriggerRequest` with `req.ID = "order-42"` against `workflowA` just before the victim's request lands.
4. `setupCallback` inserts `h.callbacks["order-42"] = ...` for the attacker's workflowA request [8](#0-7) .
5. The victim's subsequent request for `workflowB` with the same `req.ID` hits the `found` branch and is rejected with `jsonrpc.ErrConflict` / `"in-flight request ID"` [5](#0-4) , denying the victim's legitimate trigger — despite the two requests belonging to entirely unrelated workflows/owners.

### Citations

**File:** core/services/gateway/handlers/capabilities/v2/http_trigger_handler.go (L64-66)
```go
	callbacksMu             sync.Mutex
	callbacks               map[string]savedCallback // requestID -> savedCallback
	stopCh                  services.StopChan
```

**File:** core/services/gateway/handlers/capabilities/v2/http_trigger_handler.go (L141-146)
```go
	doneCh, err := h.setupCallback(ctx, req.ID, callback, requestStartTime, workflowID)
	if err != nil {
		return err
	}

	return h.sendWithRetries(ctx, legacyExecutionID, executionIDWithTriggerIndex, reqWithKey, workflowID, doneCh)
```

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

**File:** core/services/gateway/handlers/capabilities/v2/http_trigger_handler.go (L447-454)
```go
	doneCh := make(chan struct{})
	h.callbacks[requestID] = savedCallback{
		Callback:            callback,
		requestStartTime:    requestStartTime,
		createdAt:           time.Now(),
		responseAggregators: aggregators,
		doneCh:              doneCh,
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

**File:** core/services/gateway/handlers/vault/handler_test.go (L683-683)
```go
		expectedRequestID := owner + vaulttypes.RequestIDSeparator + requestID
```
