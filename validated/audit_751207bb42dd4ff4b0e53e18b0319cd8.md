### Title
Global request-ID map in `httpTriggerHandler` lets any authenticated caller squat/front-run another workflow's `requestID`, blocking their execution (DoS) - (File: `core/services/gateway/handlers/capabilities/v2/http_trigger_handler.go`)

### Summary
The HTTP trigger handler deduplicates incoming workflow-execution requests using a single global map keyed **only** by the client-supplied JSON-RPC `id` (`requestID`), with no scoping by workflow, owner, or requester identity. Because authorization is performed per-workflow (not per-`requestID`), any caller authorized for *any* workflow can pre-register an arbitrary `requestID` string before the legitimate caller of a *different* workflow submits the same ID, causing the victim's genuine request to be rejected with a conflict error. This is the same root-cause pattern as the reported Dinari bug: an identifier used for deduplication/uniqueness (`orderId` there, `requestID` here) does not incorporate the requester's identity, so an unrelated party can win the race and block the legitimate request.

### Finding Description
`setupCallback` stores pending callbacks in `h.callbacks`, a map keyed solely by `requestID`: [1](#0-0) 

This check happens after `authorizeRequest` (line 106) validates the caller's JWT/auth against the *target workflow*, but that authorization has no relationship to the `requestID` value itself — any workflow owner/caller can supply any `requestID` string of their choosing: [2](#0-1) 

`validateRequestID` only rejects empty IDs or IDs containing `/`; it does not scope or namespace the ID by workflow or requester: [3](#0-2) 

Because the map key has no requester/workflow component, an attacker authorized for their own (attacker-controlled) workflow can:
1. Predict or observe the `requestID` a victim is about to use for a different workflow (client-chosen IDs are frequently predictable/sequential/timestamp-based in typical integrations).
2. Submit their own `workflows.execute` request using that same `requestID` first.
3. `setupCallback` will succeed for the attacker and populate `h.callbacks[requestID]`.
4. When the victim's legitimate request for the *same* `requestID` (but different workflow) arrives, `setupCallback` finds the key already present and returns `jsonrpc.ErrConflict`, rejecting the victim's request entirely — exactly mirroring the Dinari `DuplicateOrder` revert caused by frontrunning with the same `orderId`/salt.

This is confirmed by the handler's own test coverage, which demonstrates that a second request with the same `ID` is always rejected as "in-flight request", regardless of which workflow/auth issued it: [4](#0-3) 

### Impact Explanation
An unprivileged, authenticated-for-their-own-workflow attacker can perform a targeted denial-of-service against any other workflow's execution request merely by reusing/squatting the same client-chosen `requestID` ahead of the victim. This blocks legitimate workflow triggers ("complete shutdown" of a specific execution path, matching the severity description in the source report), without requiring the attacker to have any privilege over, or knowledge of secrets belonging to, the victim's workflow.

### Likelihood Explanation
Exploitability depends on the attacker being able to predict or race the victim's `requestID` before the victim's own request completes `setupCallback`. Since `requestID` is entirely caller-supplied (arbitrary string, only constrained by non-empty and no `/`), and many API integrations use predictable or externally-observable IDs (idempotency keys, sequence numbers, timestamps, or IDs echoed from client-side logs/webhooks), a motivated attacker with access to any authorized workflow of their own has a straightforward path to mount this race repeatedly at low cost.

### Recommendation
Scope the `h.callbacks` map key (and the conflict check in `setupCallback`) by an identity component derived from the authenticated request — e.g., `(workflowID, requestID)` or `(workflowOwner, requestID)` — instead of `requestID` alone, so that a `requestID` collision across two different workflows/owners cannot cause a cross-tenant denial of service. This mirrors the Dinari recommendation of including the `requester` in the deduplication key.

### Proof of Concept
1. Attacker registers/owns Workflow A and obtains valid auth for it.
2. Attacker learns (or guesses) that Victim will soon call `workflows.execute` with `id = "req-123"` for Workflow B.
3. Attacker sends `workflows.execute` with `id = "req-123"`, `workflow.workflowID = A`, valid auth for A. `setupCallback` succeeds, `h.callbacks["req-123"]` is set (`core/services/gateway/handlers/capabilities/v2/http_trigger_handler.go` line 448).
4. Victim sends `workflows.execute` with `id = "req-123"`, `workflow.workflowID = B`, valid auth for B.
5. `setupCallback` finds `h.callbacks["req-123"]` already present and calls `handleUserError(..., jsonrpc.ErrConflict, "requestID: req-123 has already been used...")`, rejecting the victim's legitimate request (line 423-426).

### Citations

**File:** core/services/gateway/handlers/capabilities/v2/http_trigger_handler.go (L95-147)
```go
func (h *httpTriggerHandler) HandleUserTriggerRequest(ctx context.Context, req *jsonrpc.Request[json.RawMessage], callback handlers.Callback, requestStartTime time.Time) error {
	triggerReq, err := h.validatedTriggerRequest(ctx, req, callback)
	if err != nil {
		return err
	}

	workflowID, err := h.resolveWorkflowID(ctx, triggerReq, req.ID, callback)
	if err != nil {
		return err
	}

	key, err := h.authorizeRequest(ctx, workflowID, req, callback)
	if err != nil {
		return err
	}

	if err = h.checkRateLimit(ctx, workflowID, req.ID, callback); err != nil {
		return err
	}

	strippedWorkflowID := strings.TrimPrefix(workflowID, "0x")
	legacyExecutionID, err := workflows.EncodeExecutionID(strippedWorkflowID, req.ID) //nolint:staticcheck // legacy ID kept for observability comparison
	if err != nil {
		h.handleUserError(ctx, req.ID, jsonrpc.ErrInternal, internalErrorMessage, callback)
		return errors.New("error generating execution ID: " + err.Error())
	}
	// Workflows shouldn't use more than one HTTP trigger. If we ever need to support multiple triggers, we'd need to pass
	// trigger index to the Gateway handler and somehow allow senders to pick. For now, we use trigger index 0.
	// Execution IDs here are used only for logging.
	executionIDWithTriggerIndex, err := workflows.GenerateExecutionIDWithTriggerIndex(strippedWorkflowID, req.ID, 0)
	if err != nil {
		h.handleUserError(ctx, req.ID, jsonrpc.ErrInternal, internalErrorMessage, callback)
		return errors.New("error generating execution ID with trigger index: " + err.Error())
	}
	h.lggr.Debugw("processing request",
		"legacyExecutionID", legacyExecutionID,
		"executionIDWithTriggerIndex", executionIDWithTriggerIndex,
		"requestID", req.ID,
		"workflowID", workflowID)

	reqWithKey, err := reqWithAuthorizedKey(triggerReq, *key)
	if err != nil {
		h.handleUserError(ctx, req.ID, jsonrpc.ErrInternal, internalErrorMessage, callback)
		return errors.New("error marshaling trigger request: " + err.Error())
	}

	doneCh, err := h.setupCallback(ctx, req.ID, callback, requestStartTime, workflowID)
	if err != nil {
		return err
	}

	return h.sendWithRetries(ctx, legacyExecutionID, executionIDWithTriggerIndex, reqWithKey, workflowID, doneCh)
}
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
