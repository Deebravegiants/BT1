Audit Report

## Title
HTTP Trigger Gateway request IDs are globally namespaced across all workflows, allowing request-ID front-running to DOS an unrelated workflow's trigger execution - (File: core/services/gateway/handlers/capabilities/v2/http_trigger_handler.go)

## Summary
`httpTriggerHandler.setupCallback` stores in-flight requests in a single map `h.callbacks` keyed only by the caller-supplied `requestID`, and `validateRequestID` only rejects empty IDs or IDs containing `/` without any workflow/owner scoping. Consequently, a caller who can trigger execution of any workflow they control can pre-occupy an arbitrary ID string, causing a later, completely unrelated workflow's request that happens to reuse that same literal ID to be rejected with `jsonrpc.ErrConflict`, denying that legitimate execution.

## Finding Description
The request path is: `validatedTriggerRequest` → `validateRequestID` (checks only for empty string or `/`) [1](#0-0)  → `resolveWorkflowID` → `authorizeRequest` (validates a JWT tied to the specific target workflow's key) [2](#0-1)  → `checkRateLimit` → `setupCallback`, which enforces uniqueness of `requestID` against the single global `h.callbacks` map [3](#0-2) .

`authorizeRequest` authenticates that the caller controls the *targeted workflow*, but it does not bind or scope the `requestID` itself to that workflow or owner — the same string is compared against a process-wide map shared by every workflow the gateway serves [4](#0-3) . Thus two authorized requests for two entirely different workflows/owners collide in the same key space if they pick the same literal `id`. The handler's own test suite demonstrates exactly this collision behavior (same request ID → second request fails with `jsonrpc.ErrConflict`) [5](#0-4) , confirming the map is not partitioned per-workflow.

## Impact Explanation
This allows a caller who can trigger at least one workflow (their own) to deny another workflow owner's trigger request purely by occupying the same `requestID` string first, causing the victim's `workflows.execute` call to fail with a conflict error instead of executing. This is a denial-of-service on a specific victim request, contingent on the attacker being able to guess, predict, or observe the victim's chosen ID (e.g., low-entropy or client-generated deterministic IDs). It does not lead to key/secret exfiltration, fund movement, or cross-user response corruption (the attacker cannot read or redirect the victim's actual response) — the effect is limited to blocking a single specific request attempt tied to a specific ID value, which the victim can typically retry with a different ID.

## Likelihood Explanation
Exploitability requires the attacker to already have a legitimately registered workflow and valid signing key to pass `authorizeRequest`, and further requires the attacker to correctly predict or replay the exact `requestID` string the victim will use before the victim's request lands — a race condition dependent on ID predictability that is not guaranteed by the protocol. This is plausible but not trivially targeted without additional information about the victim's ID-generation scheme.

## Recommendation
Scope the `callbacks` map key by `(workflowID, requestID)` or `(authenticated key/owner, requestID)` instead of raw `requestID` alone, so uniqueness is enforced per-workflow rather than globally across all callers, eliminating the cross-workflow collision surface.

## Proof of Concept
1. Attacker registers Workflow A, submits `workflows.execute` with `id = "shared-id"`, authorized via Workflow A's key, occupying `"shared-id"` in `h.callbacks`.
2. Victim, operating unrelated Workflow B, submits `workflows.execute` with the same `id = "shared-id"`.
3. `setupCallback` finds the key already present and returns `jsonrpc.ErrConflict` to the victim, as reproduced by the existing test `TestHTTPTriggerHandler/.../duplicate request ID` [6](#0-5) .
4. The victim's legitimate execution request is denied due to an ID collision originating from an unrelated workflow/owner.

### Citations

**File:** core/services/gateway/handlers/capabilities/v2/http_trigger_handler.go (L64-65)
```go
	callbacksMu             sync.Mutex
	callbacks               map[string]savedCallback // requestID -> savedCallback
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

**File:** core/services/gateway/handlers/capabilities/v2/http_trigger_handler.go (L368-376)
```go
func (h *httpTriggerHandler) authorizeRequest(ctx context.Context, workflowID string, req *jsonrpc.Request[json.RawMessage], callback handlers.Callback) (*gateway_common.AuthorizedKey, error) {
	h.lggr.Debugw("authorizing request", "workflowID", workflowID, "requestID", req.ID)
	key, err := h.workflowMetadataHandler.Authorize(workflowID, req.Auth, req)
	if err != nil {
		h.handleUserError(ctx, req.ID, jsonrpc.ErrInvalidRequest, "Auth failure: "+err.Error(), callback)
		return nil, errors.Join(errors.New("auth failure"), err)
	}
	return key, nil
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
