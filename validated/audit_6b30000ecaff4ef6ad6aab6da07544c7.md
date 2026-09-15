This confirms the code path: `HandleJSONRPCUserMessage` in `http_handler.go` passes any authenticated JSON-RPC request directly to `HandleUserTriggerRequest` using the client-supplied `req.ID` with no per-caller/per-workflow prefixing at the outer layer. The `callbacks` map key is genuinely global and unscoped, confirming the claim's technical premise. [1](#0-0) [2](#0-1) 

Note that `authorizeRequest` validates a JWT signed over the full request (including `req.ID`) against per-workflow authorized keys before `setupCallback` is reached, so the attacker must possess a valid JWT authorized for *some* workflow (not necessarily the victim's) to reach the collision point. This matches the claim's "any authenticated caller of any workflow" framing.

Audit Report

## Title
Denial of Service via Global (Non-Workflow-Scoped) In-Flight Request ID Collision - (File: core/services/gateway/handlers/capabilities/v2/http_trigger_handler.go)

## Summary
`httpTriggerHandler` tracks in-flight HTTP trigger requests in a single map `callbacks map[string]savedCallback` keyed solely by the client-supplied JSON-RPC `ID`, with no scoping by workflow ID or owner. Any authenticated caller (authorized for any workflow) can occupy an arbitrary `ID` value, causing a legitimate, unrelated request from a different workflow/tenant that later arrives with the same `ID` to be rejected with a `jsonrpc.ErrConflict` error instead of being processed.

## Finding Description
`HandleUserTriggerRequest` validates the request, resolves the workflow, authorizes the JWT (which is bound to a specific workflow and its own `req.ID` at signing time), checks the rate limit, and only then calls `setupCallback(ctx, req.ID, ...)`, which stores the callback keyed purely by `req.ID` in the shared `h.callbacks` map: [3](#0-2) . `setupCallback` itself checks for an existing key and returns `jsonrpc.ErrConflict` if found, with no workflow or owner component in the key: [2](#0-1) . `HandleNodeTriggerResponse` and `cleanupCallback` look up entries the same way, solely by `ID`: [4](#0-3) . The handler's own test confirms a second, differently-workflow-authorized request sharing the same `ID` while the first is in flight is rejected: [5](#0-4) . The outer `gatewayHandler.HandleJSONRPCUserMessage` passes the raw client request straight through to `HandleUserTriggerRequest` without any per-caller/per-workflow ID prefixing: [1](#0-0) , so nothing upstream mitigates the collision.

Existing checks (`validateRequestID`, `authorizeRequest`, `checkRateLimit`) validate format, JWT signature/authorization against the target workflow, and per-workflow rate limits, but none of them scope or namespace the `ID` value itself relative to other workflows/tenants, so they do not prevent the cross-tenant collision.

## Impact Explanation
This is a genuine availability bug: any caller holding valid credentials for workflow A can occupy a request `ID` value that a caller of unrelated workflow B also happens to use, causing workflow B's legitimate request to be rejected with `ErrConflict` for the duration the ID is held (bounded by `MaxTriggerRequestDurationMs`, default 60s). This maps to an in-scope denial-of-service / cross-user response corruption impact category for the gateway's trigger handling. It requires the attacker to be an authorized caller of at least one workflow (not privileged/admin), and the effect is limited to requests that happen to share the exact same client-chosen `ID` string during the same time window — it does not grant access to another tenant's data, keys, or funds.

## Likelihood Explanation
Exploitability is bounded by whether client-generated IDs are predictable enough for an attacker to target a specific victim's `ID`. Well-designed clients using high-entropy UUIDs make deliberate targeting of another specific caller's ID computationally infeasible (a UUIDv4 collision or guessed match is not practically achievable). However, the more likely and realistic risk is unintentional collisions between different tenants using naive/low-entropy ID schemes (e.g., counters or fixed values), and the finding correctly identifies that the map's lack of workflow/owner scoping makes such collisions cross-tenant rather than self-contained, which is the actual root cause worth fixing regardless of targeted-attack feasibility.

## Recommendation
Scope the in-flight callback key by workflow ID (and/or authenticated owner) in addition to the raw request `ID`, e.g. `key := workflowID + "/" + req.ID`, so that identical `ID` values chosen independently by different callers/workflows cannot collide. This eliminates the shared global namespace that currently allows cross-tenant interference.

## Proof of Concept
The existing unit test `TestHttpTriggerHandler_HandleUserTriggerRequest/duplicate_request_ID` demonstrates the mechanism (same workflow, same ID, second request rejected). To fully validate the cross-tenant variant, extend this test to register two distinct workflows (A and B) with separate authorized keys, send a request with `ID = "X"` to workflow A first (leaving it unresolved/in-flight), then send a second request with the same `ID = "X"` — but a valid JWT for workflow B — and confirm it is rejected with `jsonrpc.ErrConflict` per the same code path shown in [5](#0-4) .

### Citations

**File:** core/services/gateway/handlers/capabilities/v2/http_handler.go (L392-402)
```go
func (h *gatewayHandler) HandleJSONRPCUserMessage(ctx context.Context, req jsonrpc.Request[json.RawMessage], callback handlers.Callback) error {
	h.metrics.IncrementTriggerRequestCount(ctx, h.lggr)
	err := h.triggerHandler.HandleUserTriggerRequest(ctx, &req, callback, time.Now())
	if err != nil {
		h.lggr.Errorw("failed to handle user trigger request", "requestID",
			req.ID, "err", err)
		// error response is sent to the response channel by the trigger handler
		// so return nil after logging
	}
	return nil
}
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

**File:** core/services/gateway/handlers/capabilities/v2/http_trigger_handler.go (L463-481)
```go
func (h *httpTriggerHandler) cleanupCallback(requestID string) {
	saved, exists := h.callbacks[requestID]
	if !exists {
		return
	}
	if !saved.processed {
		close(saved.doneCh)
	}
	delete(h.callbacks, requestID)
}

func (h *httpTriggerHandler) HandleNodeTriggerResponse(ctx context.Context, resp *jsonrpc.Response[json.RawMessage], nodeAddr string) error {
	h.lggr.Debugw("handling trigger response", "requestID", resp.ID, "nodeAddr", nodeAddr, "error", resp.Error, "result", resp.Result)
	h.callbacksMu.Lock()
	defer h.callbacksMu.Unlock()
	saved, exists := h.callbacks[resp.ID]
	if !exists {
		return errors.New("callback not found for request ID: " + resp.ID)
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
