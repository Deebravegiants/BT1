### Title
Cross-workflow request-ID collision lets an unprivileged trigger owner front-run and block another workflow's HTTP trigger execution - (File: core/services/gateway/handlers/capabilities/v2/http_trigger_handler.go)

### Summary
The GEB `auctionDebt` bug lets any unprivileged actor mutate a piece of shared state (the `AccountingEngine`'s coin balance) that a *different* legitimate caller's operation checks, causing that legitimate operation to be blocked/front-run. The `httpTriggerHandler` in the gateway contains a structurally analogous pattern: legitimate, authenticated-but-unprivileged callers (owners of unrelated workflows) can occupy a *globally shared*, non-namespaced key (`requestID`) that gates whether a different workflow's legitimate trigger request is accepted, causing that other request to be rejected with a conflict error.

### Finding Description
`httpTriggerHandler.callbacks` is declared as a map keyed **only by the client-supplied `requestID`**, not by workflow/owner: [1](#0-0) 

`HandleUserTriggerRequest` validates the trigger request, resolves the `workflowID`, authorizes the caller for that workflow, checks rate limits, and only *then* calls `setupCallback`, which performs the "is this ID already in use" check and inserts into the shared `callbacks` map: [2](#0-1) 

`setupCallback` rejects the request outright if `requestID` already exists in the map, regardless of which workflow originally claimed it: [3](#0-2) 

Because the map is keyed solely by `requestID` and any caller who is authorized for *their own* workflow can freely choose that `requestID`'s string value, a fully legitimate but unrelated caller (Workflow A's owner — an "unprivileged actor" with respect to Workflow B) can pre-empt any `requestID` that a Workflow B's client is about to use. This is validated by the existing test that shows the second submission with a duplicate ID is rejected with `"in-flight request"` / `jsonrpc.ErrConflict`: [4](#0-3) 

The root cause mirrors the GEB report precisely: a shared, globally-checkable piece of state (`AccountingEngine`'s balance / here, the `callbacks[requestID]` map) is checked and mutated without being scoped to the caller who legitimately "owns" the operation, so any other authorized-but-unrelated party can pre-populate it and block the intended caller's operation.

### Impact Explanation
If a client library or integration generates `requestID`s in a guessable or low-entropy fashion (e.g., sequential integers, timestamps, or a fixed scheme shared across the platform's example code), any other tenant on the same gateway/DON — who needs no special privilege beyond having their own valid, registered workflow and JWT/auth key — can pre-claim that ID and deny service to the specific execution a victim was about to trigger. The victim's client receives a `jsonrpc.ErrConflict` ("has already been used") and the workflow execution never starts, exactly analogous to the debt-auction DoS: no funds move and no auth is bypassed, but a legitimate, specific action is blocked by an unrelated unprivileged party.

### Likelihood Explanation
Exploitation requires the attacker to know or predict the victim's `requestID` in advance and to race their own (validly authorized, for their own workflow) request in before the victim's. This is a moderate bar: `requestID` is entirely user-supplied with no format requirements beyond "non-empty" and "no `/`" (see `validateRequestID`), so predictable schemes are plausible but not universal. Unlike the GEB bug (any nonzero SAFE-Engine internal-coin holder can trivially cause harm system-wide), this analog needs ID prediction, making it a lower-but-real likelihood, primarily useful as a targeted denial-of-service against a specific known caller/integration rather than a systemic griefing vector.

### Recommendation
Scope the `callbacks` map key by `(workflowID, requestID)` (or `(workflowOwner, requestID)`) instead of `requestID` alone, so that request-ID collisions can only occur within a single, already-authorized workflow's own namespace — mirroring how the vault gateway handler mitigates the same class of issue by stamping request IDs with the authorized owner *before* they are used as a map/dedup key (see `authorizeAndStamp`, which prefixes `req.ID` with `authorizedOwner` prior to any state insertion): [5](#0-4) 

### Proof of Concept
1. Attacker registers/owns Workflow A (a valid, unrelated workflow) and obtains a valid signed auth token for it, satisfying `authorizeRequest` for Workflow A.
2. Attacker learns/predicts the `requestID` value ("req-1") that a victim's client will use to trigger Workflow B (e.g., because the victim's integration uses sequential or fixed IDs).
3. Attacker sends `workflows.execute` for Workflow A with `id: "req-1"`; it passes validation, authorization, and rate-limiting for Workflow A, and `setupCallback` inserts `callbacks["req-1"]`.
4. Victim's legitimate request for Workflow B with `id: "req-1"` arrives; `setupCallback` finds `h.callbacks["req-1"]` already present and rejects it via `handleUserError(..., jsonrpc.ErrConflict, "requestID: req-1 has already been used...")`, exactly as reproduced in the existing unit test: [6](#0-5) 
5. Workflow B's intended execution never starts — a legitimate, targeted action was blocked by an unprivileged, unrelated caller, the same effect class as the GEB `auctionDebt` front-running DoS.

### Citations

**File:** core/services/gateway/handlers/capabilities/v2/http_trigger_handler.go (L64-65)
```go
	callbacksMu             sync.Mutex
	callbacks               map[string]savedCallback // requestID -> savedCallback
```

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

**File:** core/capabilities/vault/gateway_vault_request_processor.go (L260-286)
```go
func (p *GatewayVaultRequestProcessor) authorizeAndStamp(
	ctx context.Context,
	req *jsonrpc.Request[json.RawMessage],
	stamp func(prefixedRequestID string) error,
) (*AuthorizedGatewayVaultRequest, error) {
	incomingOwner := ""
	if idx := strings.Index(req.ID, vaulttypes.RequestIDSeparator); idx != -1 {
		incomingOwner = req.ID[:idx]
	}

	p.lggr.Debugw("authorizing gateway vault request", "method", req.Method, "requestID", req.ID)
	authResult, err := p.authorizer.AuthorizeRequest(ctx, *req)
	if err != nil {
		authErr := fmt.Errorf("request not authorized: %w", err)
		p.lggr.Errorw("gateway vault request authorization failed", "method", req.Method, "requestID", req.ID, "hasAuth", req.Auth != "", "incomingOwner", incomingOwner, "error", authErr)
		return nil, authErr
	}

	originalRequestID := req.ID
	authorizedOwner := authResult.AuthorizedOwner()
	prefixedRequestID := authorizedOwner + vaulttypes.RequestIDSeparator + originalRequestID
	req.ID = prefixedRequestID

	if err := stamp(prefixedRequestID); err != nil {
		p.lggr.Errorw("failed to stamp authorized request params", "method", req.Method, "requestID", req.ID, "error", err)
		return nil, fmt.Errorf("failed to stamp authorized request params: %w", err)
	}
```
