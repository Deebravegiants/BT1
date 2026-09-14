### Title
Unauthenticated request-ID collision allows any user to block another user's workflow trigger execution - ([File: core/services/gateway/handlers/capabilities/v2/http_trigger_handler.go])

### Summary
The Gateway's HTTP trigger handler keys its in-flight request bookkeeping map purely by the client-supplied JSON-RPC `id` field, with no binding to the requesting workflow, owner, or authenticated key. Any user who can reach the gateway's trigger endpoint can therefore pick an `id` value that collides with another user's concurrently in-flight (or about-to-be-sent) request, causing the second submission with that `id` to be rejected outright. This is the same bug class as the reported Babylon issue: a user-supplied identifier is trusted as a unique key without being tied to the entity that owns/created the underlying resource, letting an attacker deny service to a victim by squatting on the key.

### Finding Description
`httpTriggerHandler.HandleUserTriggerRequest` validates the client-supplied request ID only for emptiness, length (<=200 chars), and absence of `/`: [1](#0-0) 

It never scopes or namespaces the ID by workflow, owner, or authenticated key before using it as the key of the global `callbacks` map: [2](#0-1) 

The map insertion happens in `setupCallback`, which is called for every trigger request across all workflows/users served by this gateway process, after only workflow-authorization and rate-limit checks (not uniqueness/ownership checks tied to the caller): [3](#0-2) 

If an entry already exists for that `requestID` (regardless of which workflow/owner created it), the new request is rejected with a conflict error rather than being processed: [4](#0-3) 

This mirrors the report's root cause exactly: a value fully controlled by the requester (`unbondingTxHash` in the report, `req.ID` here) is used directly as the unique key for a shared resource without validating that it actually corresponds to, or is scoped to, the requester's own transaction/workflow.

### Impact Explanation
A malicious, unprivileged client can pre-emptively or repeatedly submit trigger requests using request IDs that a targeted victim is likely to use (e.g., predictable, sequential, or leaked IDs, or simply flooding with common values), causing the victim's legitimate `workflows.execute` trigger request to fail with `jsonrpc.ErrConflict` ("requestID ... has already been used"), as demonstrated in the handler's own test: [5](#0-4) 

Since this handler is what triggers workflow executions from the internet-facing gateway, this results in a denial-of-service against a specific victim's workflow invocation — analogous in severity to the original report's "prevent other users from unbonding" impact, but here "prevent other users from triggering their workflow execution."

### Likelihood Explanation
Any client capable of sending authorized-enough requests to invoke the HTTP trigger method can attempt this; no special privilege beyond normal workflow trigger access is required, and the only constraint on `id` is length/format, not uniqueness scoped to the caller. Because the map key space is shared across every user and every workflow on the gateway, collisions are trivial to engineer if the attacker can guess or observe request IDs (e.g., short IDs, IDs derived from public info, or via brute-force submission of common values), giving this a similar high-likelihood profile to the original report.

### Recommendation
Do not use the raw, user-supplied `req.ID` as the sole key for the shared in-flight `callbacks` map. Instead, derive (or additionally key by) a value that is bound to the authenticated caller/workflow context — e.g., combine `requestID` with the authorized workflow ID/owner (similar to how the Vault handler already prefixes response IDs with `owner + vaulttypes.RequestIDSeparator + requestID`, see `core/capabilities/vault/vaulttypes/types.go`) — so that request-ID collisions across different workflows/owners cannot cause cross-user conflicts. Alternatively, scope the "already in use" uniqueness check per-workflow (or per-authorized-key) instead of globally.

### Proof of Concept
1. Attacker learns/guesses a request `id` value that a victim workflow owner is about to use (or floods the gateway with common/sequential IDs).
2. Attacker sends a valid `workflows.execute` JSON-RPC request to the HTTP trigger endpoint with that `id`, for any workflow the attacker is authorized to trigger. `setupCallback` inserts `h.callbacks[id] = ...`.
3. Victim sends their own legitimate `workflows.execute` request with the same `id` value for their own workflow.
4. `setupCallback` finds `h.callbacks[id]` already present and rejects the victim's request with `jsonrpc.ErrConflict`, as shown by the existing unit test `TestHttpTriggerHandler_HandleUserTriggerRequest/duplicate_request_ID`: [6](#0-5)

### Citations

**File:** core/services/gateway/handlers/capabilities/v2/http_trigger_handler.go (L58-72)
```go
type httpTriggerHandler struct {
	services.StateMachine
	config                  ServiceConfig
	shards                  []*shardEndpoint
	nodeAddrToShard         map[string]*shardEndpoint
	lggr                    logger.Logger
	callbacksMu             sync.Mutex
	callbacks               map[string]savedCallback // requestID -> savedCallback
	stopCh                  services.StopChan
	workflowMetadataHandler *WorkflowMetadataHandler
	userRateLimiter         limits.RateLimiter
	metrics                 *metrics.Metrics
	wg                      sync.WaitGroup
	orgResolver             orgresolver.OrgResolver // optional; nil if the node isn't configured to resolve orgs (e.g. no Linking Service)
}
```

**File:** core/services/gateway/handlers/capabilities/v2/http_trigger_handler.go (L95-99)
```go
func (h *httpTriggerHandler) HandleUserTriggerRequest(ctx context.Context, req *jsonrpc.Request[json.RawMessage], callback handlers.Callback, requestStartTime time.Time) error {
	triggerReq, err := h.validatedTriggerRequest(ctx, req, callback)
	if err != nil {
		return err
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

**File:** core/services/gateway/handlers/capabilities/v2/http_trigger_handler.go (L419-434)
```go
func (h *httpTriggerHandler) setupCallback(ctx context.Context, requestID string, callback handlers.Callback, requestStartTime time.Time, workflowID string) (<-chan struct{}, error) {
	h.callbacksMu.Lock()
	defer h.callbacksMu.Unlock()

	if _, found := h.callbacks[requestID]; found {
		h.handleUserError(ctx, requestID, jsonrpc.ErrConflict, fmt.Sprintf("requestID: %s has already been used. Ensure the requestID is unique for each request.", requestID), callback)
		return nil, fmt.Errorf("in-flight request ID: %s", requestID)
	}

	// Build one response aggregator per shard the workflow is assigned to.
	assigned := h.workflowMetadataHandler.WorkflowShards(workflowID)
	if len(assigned) == 0 {
		// this shouldn't happen because we checked it in authorizeRequest()
		h.handleUserError(ctx, requestID, jsonrpc.ErrInternal, fmt.Sprintf("Workflow %s is not assigned to any DONs", workflowID), callback)
		return nil, errors.New("workflow is not assigned to any shards")
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
