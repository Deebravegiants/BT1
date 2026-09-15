### Title
HTTP Trigger Gateway request IDs are globally namespaced, allowing any workflow owner to front-run another owner's request ID and DOS their execution - ([File: core/services/gateway/handlers/capabilities/v2/http_trigger_handler.go])

### Summary
The `httpTriggerHandler` lets any caller choose an arbitrary `id` for a JSON-RPC `workflows.execute` request, and only validates that it is non-empty and does not contain `/`. This user-supplied ID is used as the sole key in the handler's global `callbacks` map, without any scoping to the workflow or its owner. Any unprivileged actor able to trigger execution of some workflow (even their own) can pre-claim a request ID string, causing an unrelated workflow owner's later request that happens to use the same literal ID to be rejected with a conflict error - a direct DOS via ID front-running, analogous to the reported `OpenQV1.mintBounty` bug where a user-chosen ID with no collision-proofing lets an attacker DOS a legitimate caller.

### Finding Description
`validateRequestID` only rejects empty IDs or IDs containing `/`; any other string is accepted as-is from the caller: [1](#0-0) 

`setupCallback` then enforces uniqueness of this caller-controlled ID using a single global map `h.callbacks`, keyed only by `requestID` — not by workflow ID or owner: [2](#0-1) 

If the ID is already present, the second request is rejected with `jsonrpc.ErrConflict` and never reaches the DON: [3](#0-2) 

The overall request flow shows that authorization (`authorizeRequest`, which validates a JWT signed by the specific workflow's key) happens *before* `setupCallback`'s ID-uniqueness check, but authorization is scoped to whichever workflow the caller specifies, not to the ID string itself: [4](#0-3) 

Because the `callbacks` map key space is shared across *all* workflows served by this handler, any workflow owner (an unprivileged actor with respect to other workflow owners) can submit a trigger request for a workflow they control using a specific `id` value, which occupies that ID globally. If another, unrelated workflow owner later submits a request using the same literal `id` (e.g., a predictable or common client-generated identifier), that second request fails with "already been used" even though the two requests belong to completely different workflows/owners. This is confirmed by the handler's own test suite, which demonstrates the same-ID collision producing `jsonrpc.ErrConflict`: [5](#0-4) 

### Impact Explanation
An unprivileged workflow owner can deny service to another workflow owner's execution request purely by guessing or reusing the same client-chosen request ID before the victim's request lands, since the ID namespace is not partitioned per workflow/owner. This mirrors the `mintBounty` front-running DOS: a caller-chosen, unscoped identifier used as a uniqueness key lets an unrelated party occupy it first and cause the legitimate request to fail.

### Likelihood Explanation
Any actor able to submit HTTP trigger requests for at least one workflow (their own) can attempt this; no privileged access to the target workflow is required. The likelihood of a *targeted* attack depends on the attacker being able to predict or observe the victim's chosen ID (e.g., if clients use low-entropy or fixed IDs, or the ID scheme is otherwise guessable/observable), but no protocol-level relationship between attacker and victim workflow is required to attempt the collision.

### Recommendation
Scope the `callbacks` map key by `(workflowID, requestID)` (or by the authenticated workflow owner plus requestID) rather than by the raw `requestID` alone, so uniqueness is enforced per-workflow rather than globally across all callers.

### Proof of Concept
1. Attacker registers/operates Workflow A and submits `workflows.execute` with `id = "shared-id"`, authorized via Workflow A's key. This inserts `"shared-id"` into `h.callbacks`.
2. Victim, operating unrelated Workflow B, submits `workflows.execute` with the same `id = "shared-id"` (e.g., because their client library generates request IDs deterministically or from a shared counter).
3. `setupCallback` finds `h.callbacks["shared-id"]` already present and returns `jsonrpc.ErrConflict` to the victim, as shown in the existing "duplicate request ID" test: [5](#0-4) 
4. The victim's legitimate workflow execution is denied, even though the collision originated from an unrelated workflow/owner.

### Citations

**File:** core/services/gateway/handlers/capabilities/v2/http_trigger_handler.go (L95-146)
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
