### Title
HTTP trigger requestIDs are globally namespaced, allowing any authorized caller to grief unrelated workflow executions — ([File: core/services/gateway/handlers/capabilities/v2/http_trigger_handler.go])

### Summary
The Gateway's HTTP Trigger handler tracks in-flight workflow-execution requests in a single map keyed only by the client-supplied JSON-RPC `id`, with no scoping by workflow, owner, or caller. Any caller who can obtain a valid JWT for *any* HTTP-triggered workflow can pre-empt (frontrun) another user's request simply by submitting a request carrying the same `id` first, causing the legitimate request to be rejected with a conflict error — the exact same "user-selected identifier used as a global uniqueness key" bug class described in the external report (a user-chosen `loanId` used directly as the storage key, letting anyone squat on it and revert everyone else's transaction).

### Finding Description
`httpTriggerHandler.setupCallback` stores each pending request in `h.callbacks`, a `map[string]savedCallback` keyed by the raw request ID taken straight from the incoming JSON-RPC request: [1](#0-0) 

```go
func (h *httpTriggerHandler) setupCallback(ctx context.Context, requestID string, callback handlers.Callback, requestStartTime time.Time, workflowID string) (<-chan struct{}, error) {
	h.callbacksMu.Lock()
	defer h.callbacksMu.Unlock()

	if _, found := h.callbacks[requestID]; found {
		h.handleUserError(ctx, requestID, jsonrpc.ErrConflict, fmt.Sprintf("requestID: %s has already been used. Ensure the requestID is unique for each request.", requestID), callback)
		return nil, fmt.Errorf("in-flight request ID: %s", requestID)
	}
	...
```

The only validation performed on this ID is that it is non-empty and does not contain `/`: [2](#0-1) 

`HandleUserTriggerRequest` calls `setupCallback` with the raw `req.ID`, after only validating and authorizing the request against the *target workflow* named in the request — never against the requestID itself or any per-workflow/per-owner namespace: [3](#0-2) 

Because `h.callbacks` is a single flat namespace shared by every workflow and every caller on the DON's gateway, an attacker who is an authorized caller of *any* HTTP-triggered workflow (i.e., someone who has registered their own workflow and holds a valid signing key for it — not a privileged Chainlink operator) can:
1. Predict or observe (e.g. via UUID reuse conventions, application-level leakage, or simply racing) the `id` a victim intends to use for their own, unrelated workflow's trigger request.
2. Submit their own authorized (but otherwise unrelated) trigger request using that same `id` first.
3. Cause the victim's subsequent request with the same `id` to be rejected via the `jsonrpc.ErrConflict` path shown above, because `h.callbacks[requestID]` is already populated.

This is functionally identical to the reported Folks-Finance bug: a client-chosen identifier is used directly as a global uniqueness key with no scoping to the legitimate resource/owner, letting any other party "squat" on the identifier and deny service to the rightful requester.

A dedicated unit test already demonstrates the raw mechanic (same requestID → `ErrConflict` → error surfaced to second caller), which is precisely the collision primitive being exploited here, just triggered by a *different* authorized workflow caller instead of the same one retrying: [4](#0-3) 

By contrast, the sibling Vault gateway handler avoids this exact issue by prefixing the request ID with the cryptographically-authorized owner before using it as a map key (`authorizedOwner + separator + originalRequestID`), so collisions can only happen within a single authenticated owner's own namespace, not across owners: [5](#0-4) 

The HTTP trigger handler has no equivalent owner-prefixing step before using `req.ID` as the map key.

### Impact Explanation
This is a griefing/DoS vector on workflow execution via the internet-facing gateway. Any authorized caller of any registered HTTP-triggered workflow (a low bar — anyone who deploys a workflow and gets a signing key registered) can selectively deny service to other tenants' workflow executions by colliding on request IDs, without needing any privileged role, without needing to target their own workflow, and without any profit motive requirement — matching the "Griefing" impact category. Repeated or automated collision attempts could suppress legitimate executions across many different workflows/owners sharing the same gateway/DON, since the map is global to the `httpTriggerHandler` instance rather than scoped per workflow or per owner.

### Likelihood Explanation
Likelihood is limited by two factors: (1) the attacker must already be an authorized caller for at least one HTTP-triggered workflow (obtainable by any user who registers their own trivial workflow), and (2) they must guess or observe the victim's chosen request ID before the victim's request lands. Since request IDs are often generated deterministically or with predictable patterns by client SDKs/UUID sequences, and since the rate limiter and JWT checks occur before `setupCallback` (so the attack doesn't require breaking authentication, only having *any* valid authorization), this is a plausible, low-cost DoS for a moderately determined actor. It is a real risk primarily in high-value scenarios (predictable or reused IDs, targeted attacks against a specific known caller).

### Recommendation
Scope the `h.callbacks` map key by more than just the raw client-supplied `requestID` — e.g., key by `(workflowID, requestID)` or `(authorizedOwner, requestID)` similar to how the Vault gateway handler namespaces request IDs by `AuthorizedOwner()` before using them as map keys (see `gateway_vault_request_processor.go` `authorizeAndStamp`). This ensures a collision on the identifier can only occur within a single authorized workflow/owner's own request stream, not across arbitrary unrelated callers.

### Proof of Concept
1. Attacker registers/owns Workflow A with a valid HTTP-trigger signing key, giving them a legitimate JWT usable in `authorizeRequest`.
2. Victim is about to call the gateway's `workflows.execute` method to trigger Workflow B with `id = "X"`.
3. Attacker sends their own valid, authorized request for Workflow A also using `id = "X"` and it lands first, causing `setupCallback` to insert `h.callbacks["X"]`.
4. Victim's request for Workflow B with the same `id = "X"` now hits the `found` branch in `setupCallback` and receives `jsonrpc.ErrConflict` ("requestID: X has already been used..."), even though the two requests target completely unrelated workflows and owners. [1](#0-0)

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

**File:** core/capabilities/vault/gateway_vault_request_processor.go (L278-288)
```go
	originalRequestID := req.ID
	authorizedOwner := authResult.AuthorizedOwner()
	prefixedRequestID := authorizedOwner + vaulttypes.RequestIDSeparator + originalRequestID
	req.ID = prefixedRequestID

	if err := stamp(prefixedRequestID); err != nil {
		p.lggr.Errorw("failed to stamp authorized request params", "method", req.Method, "requestID", req.ID, "error", err)
		return nil, fmt.Errorf("failed to stamp authorized request params: %w", err)
	}

	p.lggr.Debugw("authorized gateway vault request", "method", req.Method, "requestID", req.ID, "owner", authorizedOwner, "orgID", authResult.OrgID(), "workflowOwner", authResult.WorkflowOwner())
```
