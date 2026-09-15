Confirmed: `h.callbacks` in `httpTriggerHandler` (core/services/gateway/handlers/capabilities/v2/http_trigger_handler.go) is a single global map keyed purely by the caller-supplied JSON-RPC `req.ID` string — with no per-user/per-owner/per-workflow namespacing. Authorization (`authorizeRequest`) and rate limiting happen *before* `setupCallback` is called, but the map key itself has no sender-scoping, so any authenticated workflow owner who guesses or reuses another owner's in-flight `requestID` will collide in this shared map.

### Title
Unprivileged workflow owner can DoS another user's HTTP trigger request via global requestID collision - (File: core/services/gateway/handlers/capabilities/v2/http_trigger_handler.go)

### Summary
The HTTP trigger handler keys all in-flight requests in one global `map[string]savedCallback` by the client-supplied `req.ID`, without scoping the key to the caller's workflow/owner identity. This mirrors the PSM3 analog bug class: a shared, mutable resource (here, an ID-keyed cache slot) that any unprivileged caller can manipulate to interfere with another unrelated caller's operation.

### Finding Description
`httpTriggerHandler.callbacks` is declared as `map[string]savedCallback // requestID -> savedCallback` [1](#0-0) . When a user submits a trigger request, `HandleUserTriggerRequest` validates the JSON-RPC `req.ID` only for non-emptiness and absence of `/` [2](#0-1) , resolves the workflow, authorizes the caller, and rate-limits by workflow — but never ties `req.ID` uniqueness to the caller's identity [3](#0-2) . Finally `setupCallback` inserts into the shared map keyed solely by `requestID`, rejecting the request outright if that key is already in use by *anyone* — any workflow, any owner: [4](#0-3) 

A test confirms the same-ID-rejects-second-request behavior, though only within a single workflow context: [5](#0-4) .

### Impact Explanation
An unprivileged (but authenticated, since `authorizeRequest` runs first) workflow owner who is aware of or predicts another user's `requestID` (e.g., sequential/predictable client-generated IDs, or IDs echoed back in logs/errors) can pre-empt or collide with that ID while the victim's request is in flight. The victim's legitimate request would then be rejected with `ErrConflict`/"already been used" via `handleUserError`, denying that specific execution — a cross-user, unprivileged-triggered denial of service on the gateway's internet-facing HTTP trigger path, analogous to the PSM3 report's sandwich-based DoS on a shared resource.

### Likelihood Explanation
Exploitability is limited by the fact that `req.ID` values are typically opaque/unpredictable strings chosen by each client and are not inherently guessable across tenants; there's no visible endpoint that leaks another user's live `requestID` to an unprivileged party. Requests are also short-lived (bounded by `MaxTriggerRequestDurationMs`/cleanup), narrowing the collision window. This limits the practical likelihood to cases of colluding/predictable IDs or accidental collisions rather than a straightforward remote attack — similar to the "low risk" acknowledgment in the original PSM3 report.

### Recommendation
Scope the `callbacks` map key by caller identity (e.g., `workflowOwner + ":" + requestID` or `workflowID + ":" + requestID`) instead of the bare client-supplied `req.ID`, so that two different, unrelated callers cannot collide on the same in-flight-request slot regardless of what ID string they choose.

### Proof of Concept
1. User A submits `workflows.execute` with `id = "X"` for workflow W1; `setupCallback` inserts key `"X"` into `h.callbacks`.
2. Before A's request completes, User B (a different authorized workflow owner) submits a request with the same `id = "X"` for a different workflow W2.
3. `setupCallback` finds `"X"` already present and returns `ErrConflict`, denying B's request — or, if B's request lands first, A's subsequent identical-ID retry is denied — even though A and B are unrelated tenants with no shared workflow, demonstrating cross-tenant DoS via a globally-shared ID-keyed cache. [4](#0-3)

### Citations

**File:** core/services/gateway/handlers/capabilities/v2/http_trigger_handler.go (L58-65)
```go
type httpTriggerHandler struct {
	services.StateMachine
	config                  ServiceConfig
	shards                  []*shardEndpoint
	nodeAddrToShard         map[string]*shardEndpoint
	lggr                    logger.Logger
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
