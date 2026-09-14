### Title
Global, workflow-unscoped `requestID` namespace in the HTTP Trigger Handler allows any authorized workflow caller to DoS another workflow's execution requests via requestID collision - ([File: core/services/gateway/handlers/capabilities/v2/http_trigger_handler.go])

### Summary
The gateway's `httpTriggerHandler` tracks in-flight trigger requests in a single map keyed only by the client-supplied `requestID` string, with no scoping by workflow ID or owner. Any caller who is authorized for *some* workflow can occupy an arbitrary `requestID` value before it is used by a *different* workflow's legitimate caller, causing that legitimate request to be rejected with a conflict error — mirroring the reported JOJO pattern where an unprivileged submitter can send crafted/incorrect values ahead of time to make another party's legitimate request fail (DoS).

### Finding Description
`httpTriggerHandler.callbacks` is declared as `map[string]savedCallback // requestID -> savedCallback` [1](#0-0)  — the key is the raw JSON-RPC `req.ID` supplied by the caller, with no namespacing by workflow.

`validateRequestID` only checks the ID is non-empty and does not contain `/`; it performs no uniqueness or ownership binding: [2](#0-1) 

The actual "already in use" check happens in `setupCallback`, which is keyed purely on `requestID` regardless of which workflow the request targets: [3](#0-2) 

Processing order in `HandleUserTriggerRequest` is: parse/validate → resolve workflow → `authorizeRequest` (JWT check scoped to the *caller's own* workflow) → rate limit → `setupCallback` (global ID uniqueness check) [4](#0-3) . Because `authorizeRequest` only validates that the caller holds a valid signing key for *a* workflow they control (not that the `requestID` belongs to them), any caller who can get a request authorized for their own workflow reaches `setupCallback` and can insert any `requestID` string into the shared map. If that string later matches (or is pre-emptively chosen to match) a `requestID` that a different, unrelated workflow's legitimate caller is about to use, the legitimate caller's request is rejected via `jsonrpc.ErrConflict`: "requestID: %s has already been used" [5](#0-4) .

This is confirmed by the existing test `TestHttpTriggerHandler_HandleUserTriggerRequest/duplicate request ID`, which demonstrates the second request with a duplicate ID is rejected with an "in-flight request" conflict error — the test only exercises the single-workflow case, but nothing in the code binds the ID to the workflow that is doing the checking: [6](#0-5) .

### Impact Explanation
An attacker who legitimately controls or is authorized to trigger any single workflow can block execution requests for entirely unrelated workflows by squatting on their `requestID`s in the shared, global in-flight map, causing those legitimate requests to fail with a conflict error until the attacker's entry is reaped (`CleanUpPeriodMs`) [7](#0-6) . This is a targeted, cross-tenant denial of service on the internet-facing gateway with no privilege beyond ordinary authorized workflow-caller access, directly analogous to the JOJO report where a caller submits data ahead of time to block another party's otherwise-valid trade/request.

### Likelihood Explanation
Exploitability depends on the attacker being able to predict or guess a victim's chosen `requestID` (e.g., sequential counters, timestamps, or other low-entropy client-generated identifiers) before the victim's request lands, and winning the race to insert it first. Since `requestID` values are entirely caller-chosen with no server-side randomness requirement and no per-workflow namespacing, likelihood is non-trivial for any deployment where clients use predictable IDs, though it requires some timing/guessing effort, making it a plausible but not universally trivial DoS vector.

### Recommendation
Scope the in-flight `callbacks` map key by `(workflowID, requestID)` instead of `requestID` alone, so that request-ID collisions can only occur within the same workflow's own request stream, eliminating cross-workflow interference.

### Proof of Concept
1. Attacker is authorized (holds a valid signing key) for `workflowA`, which they control.
2. Attacker learns or predicts the `requestID` value `X` that a victim's client for `workflowB` intends to use next.
3. Attacker sends a `workflows.execute` trigger request for `workflowA` with `req.ID = X`. This passes `authorizeRequest` (valid for `workflowA`) and reaches `setupCallback`, inserting `X` into the global `h.callbacks` map.
4. Victim's legitimate request for `workflowB` with `req.ID = X` arrives; `setupCallback` sees `X` already present and returns `jsonrpc.ErrConflict`, denying the victim's execution until the attacker's entry expires via the reaper.

### Citations

**File:** core/services/gateway/handlers/capabilities/v2/http_trigger_handler.go (L64-65)
```go
	callbacksMu             sync.Mutex
	callbacks               map[string]savedCallback // requestID -> savedCallback
```

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

**File:** core/services/gateway/handlers/capabilities/v2/http_trigger_handler.go (L561-581)
```go
// reapExpiredCallbacks removes callbacks that are older than the maximum age
func (h *httpTriggerHandler) reapExpiredCallbacks(ctx context.Context) {
	h.callbacksMu.Lock()
	defer h.callbacksMu.Unlock()
	now := time.Now()
	var expiredCount int
	for reqID, callback := range h.callbacks {
		if now.Sub(callback.createdAt) > time.Duration(h.config.CleanUpPeriodMs)*time.Millisecond {
			if !callback.processed {
				h.metrics.IncrementRequestErrors(ctx, jsonrpc.ErrInternal, h.lggr)
			}
			h.cleanupCallback(reqID)
			expiredCount++
		}
	}
	if expiredCount > 0 {
		h.metrics.IncrementPendingRequestsCleanUpCount(ctx, int64(expiredCount), h.lggr)
		h.lggr.Infow("Removed expired callbacks", "count", expiredCount, "remaining", len(h.callbacks))
	}
	h.metrics.RecordPendingRequestsCount(ctx, int64(len(h.callbacks)), h.lggr)
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
