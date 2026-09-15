### Title
User-controlled JSON-RPC `id` enables cross-workflow request collision / DoS on the HTTP Trigger Gateway handler - (File: core/services/gateway/handlers/capabilities/v2/http_trigger_handler.go)

### Summary
The Gateway's `httpTriggerHandler` keys its in-flight callback map solely by the client-supplied JSON-RPC `id` field, with no per-workflow, per-owner, or per-key namespacing. Any authenticated caller (for any workflow) can pre-occupy an `id` value before another user's request with the same `id` arrives, causing the legitimate request to be rejected. This mirrors the reported bug class: relying on user-supplied IDs for uniqueness enables front-running/collision-based denial of service.

### Finding Description
`HandleUserTriggerRequest` validates and authorizes a request for a specific `workflowID`, then calls `setupCallback`, which stores the pending callback in a single, gateway-wide map keyed only by the raw request ID: [1](#0-0) 

```go
callbacksMu             sync.Mutex
callbacks               map[string]savedCallback // requestID -> savedCallback
``` [2](#0-1) 

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

Critically, the uniqueness check is against the **global** `h.callbacks` map, not scoped by `workflowID`, `workflowOwner`, or the `AuthorizedKey` returned by `authorizeRequest`. `validateRequestID` only rejects empty IDs or IDs containing `/`; it performs no additional entropy or scoping requirements: [3](#0-2) 

Because authorization (`authorizeRequest`) only requires the caller to have a valid key for *some* workflow — not the victim's workflow — any unprivileged, authenticated caller can submit a trigger request using the same `id` value they anticipate another user (or their own competing job) will use for a *different* workflow, occupying the map slot first. The subsequent legitimate request with the same `id` then fails with `jsonrpc.ErrConflict` ("has already been used"), even though it targets a completely different workflow. The existing unit test confirms this exact race behavior is by design of the map, not scoped per-workflow: [4](#0-3) 

### Impact Explanation
An attacker who is merely an authorized caller for any workflow on the gateway (not necessarily the victim's workflow) can deny service to a targeted workflow execution by "claiming" its expected request ID first. This is a direct availability impact on the internet-facing Gateway's HTTP trigger path — legitimate workflow executions can be blocked without any privilege escalation, satisfying the "unauthorized job run" / gateway handler analog category (DoS of specific caller's job execution via ID collision).

### Likelihood Explanation
Exploitability depends on the attacker being able to predict or observe the victim's chosen request ID. In many integrations, request IDs are deterministic or low-entropy (e.g., incrementing counters, timestamps, or fixed strings reused by client libraries), making prediction plausible. Even without prediction, this is a straightforward design flaw consistent with the reported bug class: no internal, collision-resistant ID generation exists, and uniqueness is enforced across all workflows on the node globally rather than scoped to the requester's own workflow/key.

### Recommendation
Scope the in-flight callback key to include the resolved `workflowID` (or the authorized key/owner) in addition to the client-supplied `id`, e.g. key by `workflowID + "/" + requestID` (already partially supported since `/` is reserved for internal routing) instead of the raw client ID alone. This prevents cross-workflow ID collisions while preserving per-caller idempotency semantics.

### Proof of Concept
1. Attacker holds a valid authorized key for `workflowA` (any workflow they control).
2. Attacker observes/predicts that a victim will soon submit a trigger request for `workflowB` with JSON-RPC `id = "X"`.
3. Attacker submits a JSON-RPC request for `workflowA` with `id = "X"` first; `setupCallback` inserts `h.callbacks["X"]`.
4. Victim's request for `workflowB` with `id = "X"` arrives at `setupCallback`, hits the `found` branch, and is rejected with `jsonrpc.ErrConflict` ("requestID: X has already been used"), denying the victim's workflow execution.

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
