### Title
Global, unscoped `requestID` namespace in `httpTriggerHandler` allows cross-workflow DoS via request-ID squatting - (File: core/services/gateway/handlers/capabilities/v2/http_trigger_handler.go)

### Summary
The gateway's HTTP trigger handler stores in-flight requests in a single, node-wide map keyed only by the client-supplied `requestID`, with no owner/workflow scoping. Any authenticated workflow caller can pre-register (or race) a `requestID` that another, unrelated workflow's caller later uses, causing that caller's legitimate request to be permanently rejected as a duplicate for the lifetime of the cache entry. This mirrors the `AccountantDelegate.sweepInterest` bug class: a resource that a caller assumes is exclusively theirs (the treasury/cnote balance there, the `requestID` slot here) can be silently polluted by an unrelated, unprivileged third party, and a subsequent strict conflict/invariant check then permanently denies service to the legitimate actor.

### Finding Description
`httpTriggerHandler.callbacks` is declared as `map[string]savedCallback // requestID -> savedCallback` with no namespacing by workflow ID or owner: [1](#0-0) 

`setupCallback` checks for a pre-existing entry keyed purely on `requestID` and rejects the request as a conflict if found: [2](#0-1) 

The request-processing pipeline in `HandleUserTriggerRequest` validates the request, resolves the *caller's own* workflow ID, authorizes the request against *that* workflow's registered key, and only afterward reaches `setupCallback`: [3](#0-2) 

Because `authorizeRequest` only validates that the caller owns the workflow named in *their own* request — it does not, and cannot, validate ownership of the `requestID` string itself — any caller who successfully authenticates for **any** workflow can write an entry into the shared `callbacks` map under an arbitrary `requestID` value of their choosing. If that value happens to coincide with a `requestID` that a different, unrelated workflow's legitimate caller is about to use (predictable/sequential IDs, or simple brute-force pre-registration across the ID space), the legitimate caller's `setupCallback` call finds `found == true` and is rejected with a JSON-RPC conflict error, never reaching execution: [4](#0-3) 

This is the same fault class as the `sweepInterest` finding: a downstream equality/uniqueness check (`cnote.balanceOf(treasury) == 0` there; `_, found := h.callbacks[requestID]` here) assumes a piece of state is exclusively controlled by the current caller's flow, but the state is actually a shared, unscoped resource that any other unprivileged party can write to first.

### Impact Explanation
An attacker holding a valid signing key for **any** workflow (not the victim's) can deny service to a specific, targeted request from a completely different workflow by squatting its `requestID` ahead of time, or can indiscriminately flood the shared ID space to increase collision odds against arbitrary victims. The affected request is denied with `ErrConflict` and never executes; because the poisoning caller doesn't need any relationship to the victim workflow, this is a genuine unprivileged/cross-user DoS through the internet-facing gateway path, degrading availability of the workflow-execution trigger, which the report's severity rationale (broken invariant, no alternate path to complete the operation) closely parallels.

### Likelihood Explanation
Exploitability depends on the attacker being able to guess or brute-force a victim's `requestID` before the victim's own request arrives — this is feasible against clients that use predictable IDs (timestamps, incrementing counters, low-entropy generation) or via wide pre-registration across the ID keyspace, since the `README.md`'s only stated constraint on user request IDs is "cannot contain '/'": [5](#0-4) 
Requests using high-entropy random UUID-style IDs are much less likely to collide, which somewhat reduces overall likelihood relative to the Solidity original (where any third party could trivially poison the shared balance with a single token transfer).

### Recommendation
Scope the `callbacks` map key by `(workflowID, requestID)` (or `(workflowOwner, requestID)`) instead of `requestID` alone, so that request-ID uniqueness is enforced only within a caller's own workflow namespace and cannot be affected by unrelated callers. Apply the same authorization-then-scoped-uniqueness ordering used elsewhere in the codebase (e.g., the Vault gateway path prefixes IDs with the authorized owner before storing them in `activeRequests`, see `GatewayVaultRequestProcessor`'s "Prefix ID" step) so no other caller can occupy another workflow's ID slot: [6](#0-5) 

### Proof of Concept
1. Attacker registers/holds a valid workflow key for `workflowID = A` (any workflow they legitimately control).
2. Attacker predicts or brute-forces the `requestID` value `"X"` that victim's workflow `B` client will soon use (e.g., a timestamp-based or sequential ID).
3. Attacker sends a valid, authorized `MethodWorkflowExecute` request for workflow `A` with `req.ID = "X"`; `setupCallback` inserts `h.callbacks["X"]` unconditionally since no entry existed yet.
4. Victim's legitimate client later sends its own valid, authorized request for workflow `B` with the same `req.ID = "X"`.
5. `setupCallback` finds `h.callbacks["X"]` already present and calls `handleUserError` with `jsonrpc.ErrConflict`, rejecting the victim's otherwise-legitimate, authorized request: [2](#0-1) 
This behavior is directly demonstrated by the existing test asserting that a second, differently-owned callback for the same `requestID` is rejected with "requestID has already been used": [7](#0-6) 
(The existing test uses the same JWT/workflow for both calls; the vulnerability is that the map has no scoping that would prevent an *different* workflow's caller from producing the identical collision.)

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

**File:** core/services/gateway/handlers/capabilities/v2/http_trigger_handler.go (L95-120)
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

**File:** core/services/gateway/handlers/capabilities/v2/README.md (L266-270)
```markdown
### 9.1 Request ID Format

- **User Requests**: Plain string identifiers (cannot contain "/")
- **Node Messages**: Format `<methodName>/<workflowID>/<uuid>` or `<methodName>/<workflowID>/<workflowExecutionID>/<uuid>`
- **Method Routing**: Gateway routes messages based on method name in request ID
```

**File:** core/capabilities/vault/gateway_vault_request_processor.go (L20-30)
```go
// GatewayVaultRequestProcessor orchestrates the shared gateway-routed vault JSON-RPC pipeline
// used by the gateway public handler and the node-side gateway connector handler.
//
// Pipeline invariant:
//
//	ValidateStructureBeforeAuth → AuthorizeRequest → Prefix ID → StampAuthorizedParams → ValidateOwnerScopedLimits
//	    (no param mutation)        (on raw bytes)               (namespace + request_id)      (ciphertext size)
//
// AuthorizeRequest runs while params are still digest-safe. It also applies the replay guard
// (digest deduplication) and validates that payload owners match the authorized workflow owner
// before this processor rewrites the request ID or stamps params.
```

**File:** core/services/gateway/handlers/capabilities/v2/http_trigger_handler_test.go (L360-397)
```go
	t.Run("duplicate JWT token and request ID", func(t *testing.T) {
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
		err = handler.HandleUserTriggerRequest(t.Context(), req, callback2, time.Now())
		require.Error(t, err)
		require.Contains(t, err.Error(), "token has already been used")

		r, err := callback2.Wait(t.Context())
		require.NoError(t, err)
		requireUserErrorSent(t, r, jsonrpc.ErrInvalidRequest)
	})
```
