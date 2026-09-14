### Title
Global (non-namespaced) `requestID` map in the HTTP Trigger Handler lets any unprivileged caller squat on another workflow's request ID and block its execution - (File: `core/services/gateway/handlers/capabilities/v2/http_trigger_handler.go`)

### Summary
The external report's bug class is a "resource-ID collision blocks the legitimate operation": an attacker who can predict/reuse the same identifier (a Safe deployment `nonce`) as a victim's pending operation makes the victim's operation permanently fail via a hard error. The Chainlink `httpTriggerHandler` exhibits an analogous pattern: pending trigger requests are tracked in a single, gateway-wide map keyed only by the caller-supplied `requestID`, with no per-workflow or per-owner namespacing. Any authenticated-but-unprivileged caller (owner of *any* workflow with a valid authorized key) can pick a `requestID` that collides with another, unrelated workflow's in-flight trigger request and cause that legitimate request to be rejected with a conflict error.

### Finding Description
`httpTriggerHandler.setupCallback` stores in-flight trigger requests in `h.callbacks map[string]savedCallback`, keyed purely by `requestID` (the value taken directly from the caller-controlled JSON-RPC `req.ID`), with no workflow or owner prefix: [1](#0-0) [2](#0-1) 

`HandleUserTriggerRequest` authorizes the caller against the *target* workflow's authorized keys via `authorizeRequest` (a JWT check scoped to that specific `workflowID`) before reaching `setupCallback`: [3](#0-2) 

However, this authorization check only proves the caller controls a valid key *for the workflow they are targeting* — it does not scope the `requestID` uniqueness check to that workflow. Because `h.callbacks` is a single global map, any caller who is authorized for **their own** workflow can submit a trigger request whose `req.ID` collides with the `req.ID` a completely different, unrelated workflow's legitimate caller is about to use (or is already using). The `setupCallback` check will reject the second submission outright:
```go
if _, found := h.callbacks[requestID]; found {
    h.handleUserError(ctx, requestID, jsonrpc.ErrConflict, fmt.Sprintf("requestID: %s has already been used...", requestID), callback)
    return nil, fmt.Errorf("in-flight request ID: %s", requestID)
}
```
This is confirmed by the existing test that demonstrates a same-workflow duplicate ID is rejected with `jsonrpc.ErrConflict`/"in-flight request": [4](#0-3) 

Notably, sibling handlers in the same codebase (`vault` and `confidentialrelay`) mitigate exactly this class of cross-tenant collision by namespacing the request key with the authorized owner before using it as a map key (`owner + RequestIDSeparator + requestID`): [5](#0-4) 
The HTTP trigger handler has no equivalent per-workflow/per-owner namespacing, so it remains exposed to the same cross-tenant ID-squatting pattern the report describes for the Safe `nonce`.

### Impact Explanation
An unprivileged, authenticated caller of workflow A (holding only a valid authorized key for A, not for the victim's workflow B) can choose a `requestID` string that they predict or know will be used by workflow B's legitimate caller (e.g. common idempotency keys, sequential counters, timestamps, or any externally-visible identifier). If the attacker's request lands first, the victim's legitimate trigger request for workflow B is rejected outright with `jsonrpc.ErrConflict` and never dispatched to the DON, denying that workflow execution — directly analogous to the report's "block the counterpart deployment" impact, but here it is "block the counterpart workflow execution."

### Likelihood Explanation
Exploitation requires the attacker to hold *any* valid authorized key for *some* workflow (a low bar — an unprivileged external caller of the gateway's public HTTP trigger endpoint) and to guess or learn the victim's upcoming `requestID`. Likelihood is moderate: it depends on `requestID` predictability, which is entirely under the discretion of the calling application and not enforced to be high-entropy/opaque by the handler.

### Recommendation
Namespace the `h.callbacks` key (and the `HandleNodeTriggerResponse` lookup) by `workflowID` (or by the authorized owner) in addition to the caller-supplied `requestID`, mirroring the `owner + RequestIDSeparator + requestID` pattern already used in `core/services/gateway/handlers/vault/handler.go` and `core/capabilities/vault` code. This prevents a caller authorized only for one workflow from colliding with, and blocking, another unrelated workflow's in-flight request.

### Proof of Concept
1. Attacker registers/holds an authorized key for workflow A (any workflow they can legitimately trigger).
2. Attacker learns or guesses that workflow B's legitimate caller will submit a trigger request with `requestID = "X"` (e.g., a predictable idempotency key).
3. Attacker sends a valid `workflows.execute` JSON-RPC request to the gateway for workflow A with `ID: "X"`, correctly JWT-signed for workflow A. This succeeds and inserts `h.callbacks["X"]`.
4. Victim's legitimate caller sends the workflow B trigger request with `ID: "X"`. `setupCallback` finds `h.callbacks["X"]` already present (owned by the attacker's workflow-A request) and rejects it with `jsonrpc.ErrConflict`, per [6](#0-5) , exactly as exercised in the existing duplicate-ID test at [4](#0-3) .

### Citations

**File:** core/services/gateway/handlers/capabilities/v2/http_trigger_handler.go (L63-65)
```go
	lggr                    logger.Logger
	callbacksMu             sync.Mutex
	callbacks               map[string]savedCallback // requestID -> savedCallback
```

**File:** core/services/gateway/handlers/capabilities/v2/http_trigger_handler.go (L95-113)
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

**File:** core/services/gateway/handlers/vault/handler_test.go (L296-316)
```go
		rawPayload := json.RawMessage(`{"request_id":"test_request_id","encrypted_secrets":[{"id":{"key":"test_id","owner":"0xworkflow","namespace":"default"},"encrypted_value":"abc123"}]}`)

		var forwarded jsonrpc.Request[json.RawMessage]
		don.On("SendToNode", mock.Anything, mock.Anything, mock.Anything).Run(func(args mock.Arguments) {
			forwarded = *args.Get(2).(*jsonrpc.Request[json.RawMessage])
		}).Return(nil)

		req := jsonrpc.Request[json.RawMessage]{
			ID:     "1",
			Method: vaulttypes.MethodSecretsCreate,
			Params: &rawPayload,
		}

		err = h.HandleJSONRPCUserMessage(t.Context(), req, common.NewCallback())
		require.NoError(t, err)

		require.NotNil(t, forwarded.Params)
		var forwardedCreateRequest vaultcommon.CreateSecretsRequest
		require.NoError(t, json.Unmarshal(*forwarded.Params, &forwardedCreateRequest))
		require.Equal(t, "0xworkflow"+vaulttypes.RequestIDSeparator+"1", forwardedCreateRequest.RequestId)
	})
```
