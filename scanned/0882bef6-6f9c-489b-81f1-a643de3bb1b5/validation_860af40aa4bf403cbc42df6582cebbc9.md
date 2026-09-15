Analog found in the CRE Gateway's HTTP Trigger handler: request IDs are tracked in a single global map with no per-workflow or per-owner scoping, so any authorized caller can grief another user's in-flight trigger request by squatting on its request ID.

### Title
Cross-workflow request-ID griefing via unscoped global callback map - (File: core/services/gateway/handlers/capabilities/v2/http_trigger_handler.go)

### Summary
The Chainlink Gateway's `httpTriggerHandler` tracks in-flight HTTP-trigger requests in a single map keyed only by the client-supplied `requestID`, with no binding to the calling workflow ID or owner. Any authorized caller can therefore reserve an arbitrary `requestID` string before a legitimate user submits a request with that same ID for a completely different workflow, causing the legitimate request to be rejected with a conflict error — mirroring the "external state change causes a legitimate operation to revert" pattern in the referenced NFT withdrawal grief.

### Finding Description
`httpTriggerHandler.callbacks` is declared as `map[string]savedCallback // requestID -> savedCallback` [1](#0-0) , i.e., the uniqueness constraint on `requestID` is global across the entire gateway node, not scoped to a workflow ID, workflow owner, or JWT signer.

Request handling flow in `HandleUserTriggerRequest` validates and authorizes the request (`validatedTriggerRequest`, `resolveWorkflowID`, `authorizeRequest`, `checkRateLimit`) and only afterwards calls `setupCallback` with `req.ID` to register the in-flight request [2](#0-1) . `validateRequestID` only checks that the ID is non-empty and doesn't contain `/`; it performs no uniqueness or scoping check tied to workflow/owner [3](#0-2) .

The existing test suite confirms that submitting a second request with the same ID is rejected outright with an "in-flight request" conflict, independent of which workflow it targets: [4](#0-3) .

Because any account that can get a workflow authorized on the same gateway node (an unprivileged, permissionless action — anyone can register and authorize their own workflow) can submit HTTP trigger requests, an attacker can pick a `requestID` matching or predicting a victim's ID for the victim's unrelated workflow, occupy the slot in the shared `callbacks` map first, and force the victim's legitimate request to fail with `ErrConflict`, exactly as the NFT grief lets an attacker manipulate shared on-chain state to force a legitimate NFT owner's withdrawal to revert.

### Impact Explanation
A legitimate workflow owner's HTTP-triggered workflow execution can be denied (`jsonrpc.ErrConflict` / "in-flight request") by an unrelated, authorized-but-malicious party who has no relationship to the victim's workflow, simply by racing to submit a JSON-RPC request carrying the same `id` value first. This is a request-level denial-of-service/griefing vector against the gateway's HTTP trigger capability, degrading availability of workflow executions for arbitrary victims without requiring any privilege escalation, secret disclosure, or fund movement — it is scoped to DoS/grief of legitimate operations, matching the "Medium" severity class of the source report.

### Likelihood Explanation
Exploitability depends on the attacker being able to learn or predict the victim's chosen `requestID` ahead of time (since IDs are arbitrary client-chosen strings, not globally observable by other users under normal operation). If clients use predictable, sequential, or otherwise guessable IDs (e.g., deterministic idempotency keys derived from public data), or if an attacker can observe IDs via other channels (e.g., published execution logs, shared tooling, or replay of previously seen public identifiers), the attack becomes practical and cheap to execute repeatedly. This constraint is analogous to the sandwich-timing requirement in the original NFT report (the griefer must act in the correct window), so likelihood is assessed as low-to-moderate but the mechanism itself is a genuine architectural gap (missing per-caller/per-workflow scoping) rather than a hypothetical.

### Recommendation
Scope the in-flight-request uniqueness constraint to the tuple `(workflowID, requestID)` (or `(workflowOwner, requestID)`) instead of a single global `requestID` key, so that request IDs chosen by unrelated workflows/owners cannot collide. This preserves the existing per-caller idempotency/duplicate-submission protection while eliminating cross-user interference.

### Proof of Concept
1. Attacker registers and gets authorized for their own workflow `W_attacker` on the gateway node.
2. Attacker learns/guesses the `requestID` value `X` that a victim will use for their (unrelated) workflow `W_victim`.
3. Attacker sends a valid, authorized `HandleUserTriggerRequest` for `W_attacker` using `id = X`; this succeeds and inserts `callbacks[X]`, matching the flow validated in `TestHttpTriggerHandler_HandleUserTriggerRequest`'s "duplicate request ID" subtest [4](#0-3) .
4. Victim later submits their legitimate request for `W_victim` with the same `id = X`; because `callbacks` is keyed only by `requestID` [1](#0-0) , the victim's request is rejected with `jsonrpc.ErrConflict` ("in-flight request"), denying their legitimate workflow execution.

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

**File:** core/services/gateway/handlers/capabilities/v2/http_trigger_handler.go (L190-200)
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
