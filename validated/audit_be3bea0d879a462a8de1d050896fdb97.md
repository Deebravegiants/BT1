Audit Report

## Title
Global, unscoped `requestID` namespace in `httpTriggerHandler` allows cross-workflow DoS via request-ID squatting - (File: core/services/gateway/handlers/capabilities/v2/http_trigger_handler.go)

## Summary
The gateway's HTTP trigger handler stores in-flight requests in a single, process-wide map keyed only by the client-supplied `requestID`, with no scoping by workflow ID or owner. Any caller holding a valid signing key for **any** registered workflow can insert an entry under an arbitrary `requestID` of their choosing, and if that value collides with a `requestID` that a different, unrelated workflow's legitimate caller is about to use, the victim's request is rejected with a permanent conflict error.

## Finding Description
`httpTriggerHandler.callbacks` is declared as `map[string]savedCallback // requestID -> savedCallback`, with no workflow/owner component in the key: [1](#0-0) 

`setupCallback` checks for a pre-existing entry keyed purely on `requestID` and rejects the caller with `jsonrpc.ErrConflict` if the slot is already occupied, before the entry is even created: [2](#0-1) 

The request pipeline in `HandleUserTriggerRequest` resolves the caller's own `workflowID`, authorizes the request against that workflow via `authorizeRequest` → `WorkflowMetadataHandler.Authorize`, and only afterward calls `setupCallback`: [3](#0-2) 

Reviewing `WorkflowMetadataHandler.Authorize` confirms it validates the JWT signature, checks the request digest (binding the JWT to the *attacker's own* request content, which the attacker fully controls, including `req.ID`), checks JWT replay via `jti`, and checks that the signer is an authorized key *for the workflowID the attacker specified* — it does nothing to bind or reserve the `requestID` string against any other workflow's namespace: [4](#0-3) 

Because a caller fully constructs and signs their own request (including choosing `req.ID` freely, subject only to the "no `/`" constraint), an attacker authorized for workflow A can successfully pass `authorizeRequest` and then call `setupCallback` with any `requestID` string, inserting it into the shared, global `h.callbacks` map. This has nothing to do with workflow B or its owner — the map has no per-workflow partition. If workflow B's legitimate client later uses the same `requestID` value (e.g., through predictable/low-entropy ID schemes), `setupCallback` finds `found == true` and permanently denies that legitimate, correctly-authorized request via `ErrConflict`.

The existing test `TestHttpTriggerHandler_HandleUserTriggerRequest/duplicate JWT token and request ID` demonstrates the exact map-collision rejection behavior (albeit using the same workflow/JWT for both calls, since the test's purpose was JWT replay, not cross-workflow collision): [5](#0-4)  — but nothing in the authorization or setup path changes this outcome when the second call instead comes from a different workflow's differently-signed, fully valid request using the same `requestID`. The `jwtReplayCache` only rejects reuse of the same JWT `jti`, not reuse of the same `requestID` by a different signer/workflow: [6](#0-5) 

This confirms the claimed root cause: `setupCallback`'s uniqueness check operates on a resource (`h.callbacks[requestID]`) that the code implicitly assumes is caller/workflow-exclusive, but is in fact a shared, unscoped namespace writable by any authorized caller of any workflow.

## Impact Explanation
An attacker who holds a valid signing key for any single registered workflow (not necessarily the victim's) can pre-register or race a `requestID` value into the shared `callbacks` map, causing a specific, targeted, or randomly-collided legitimate request from an unrelated workflow to be rejected with `ErrConflict` and never executed. This is a genuine availability/DoS impact against the gateway's HTTP trigger execution path, reachable without any privileged/operator access — only a normal workflow-signing credential is required, and it need not be the victim's. This matches an in-scope "broken invariant with no alternate path to complete the operation" DoS pattern.

## Likelihood Explanation
Exploitability is gated entirely by the attacker's ability to predict or brute-force the victim's `requestID` before the victim's legitimate request lands. The `README.md`'s only constraint on user-supplied request IDs is that they must not contain `/`; there is no server-side entropy or format requirement forcing UUID-style values: [7](#0-6) . Clients using predictable, sequential, or timestamp-based IDs are practically exploitable; clients using high-entropy random UUIDs make collision infeasible. This is a real but conditional risk that depends on client-side ID-generation practice outside the gateway's control, somewhat limiting real-world likelihood, but the underlying code defect (global unscoped namespace, confirmed by direct code review) is genuine and unmitigated by any existing check.

## Recommendation
Scope the `callbacks` map key by `(workflowID, requestID)` or `(workflowOwner, requestID)` instead of `requestID` alone, so uniqueness is enforced only within a caller's own workflow namespace. Apply the authorize-then-scoped-uniqueness ordering pattern already used elsewhere in the codebase (e.g., the Vault gateway path prefixes IDs with the authorized owner before storing them, per `GatewayVaultRequestProcessor`'s documented pipeline): [8](#0-7) 

## Proof of Concept
1. Attacker holds a valid, authorized signing key for workflow `A` (any workflow they legitimately control) — no relationship to victim workflow `B` required.
2. Attacker predicts or brute-forces the `requestID` value `"X"` that a victim client of workflow `B` will soon send (e.g., sequential/timestamp-derived IDs).
3. Attacker sends a fully valid, self-signed `MethodWorkflowExecute` request for workflow `A` with `req.ID = "X"`. `authorizeRequest`/`Authorize` succeeds (valid signature, valid digest over attacker's own request, fresh `jti`), and `setupCallback` inserts `h.callbacks["X"]` unconditionally since no entry pre-existed: [9](#0-8) 
4. Victim's legitimate client later sends its own valid, authorized request for workflow `B` with the same `req.ID = "X"`.
5. `setupCallback` finds `h.callbacks["X"]` already occupied and rejects the victim's otherwise-legitimate request with `jsonrpc.ErrConflict`: [10](#0-9) 
6. A Go unit test extending the existing `duplicate JWT token and request ID` test — but using two *different* registered workflows and two *different* signing keys/JWTs, both using `req.ID = requestID` — would directly demonstrate the cross-workflow collision and confirm the second, unrelated, fully-authorized workflow's request is denied.

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

**File:** core/services/gateway/handlers/capabilities/v2/http_trigger_handler.go (L419-455)
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

	aggregators := make(map[string]*aggregation.IdenticalNodeResponseAggregator, len(assigned))
	for _, shard := range assigned {
		// (N+F)//2 + 1 threshold where N = number of nodes, F = number of faulty nodes
		threshold := (len(shard.members)+shard.f)/2 + 1
		agg, err := aggregation.NewIdenticalNodeResponseAggregator(threshold)
		if err != nil {
			return nil, errors.New("failed to create response aggregator: " + err.Error())
		}
		aggregators[shard.donID] = agg
	}

	doneCh := make(chan struct{})
	h.callbacks[requestID] = savedCallback{
		Callback:            callback,
		requestStartTime:    requestStartTime,
		createdAt:           time.Now(),
		responseAggregators: aggregators,
		doneCh:              doneCh,
	}
	return doneCh, nil
```

**File:** core/services/gateway/handlers/capabilities/v2/workflow_metadata_handler.go (L80-108)
```go
func (h *WorkflowMetadataHandler) Authorize(workflowID string, token string, req *jsonrpc.Request[json.RawMessage]) (*gateway.AuthorizedKey, error) {
	claims, signer, err := utils.VerifyRequestJWT(token, *req)
	if err != nil {
		h.lggr.Errorw("Failed to verify JWT", "error", err)
		return nil, err
	}

	if h.jwtCache.isReplay(claims.ID) {
		h.lggr.Warnw("JWT token has already been used", "workflowID", workflowID, "signer", signer.Hex(), "jti", claims.ID)
		return nil, errors.New("JWT token has already been used. Please generate a new one with new id (jti)")
	}

	keys, exists := h.authorizedKeys[workflowID]
	if !exists {
		h.lggr.Errorw("Workflow ID not found in authorized keys", "workflowID", workflowID)
		return nil, fmt.Errorf("workflow ID %s not found", workflowID)
	}
	key := gateway.AuthorizedKey{
		KeyType:   gateway.KeyTypeECDSAEVM,
		PublicKey: strings.ToLower(signer.Hex()),
	}
	if _, exists = keys[key]; !exists {
		h.lggr.Errorw("Signer not found in authorized keys", "signer", signer.Hex())
		return nil, fmt.Errorf("signer '%s' is not authorized for workflow '%s'. Ensure that the signer is registered in the workflow definition", signer.Hex(), workflowID)
	}
	h.jwtCache.recordUsage(claims.ID)

	return &key, nil
}
```

**File:** core/services/gateway/handlers/capabilities/v2/workflow_metadata_handler.go (L399-412)
```go
func (cache *jwtReplayCache) isReplay(jti string) bool {
	cache.mu.RLock()
	defer cache.mu.RUnlock()

	_, exists := cache.cache[jti]
	return exists
}

func (cache *jwtReplayCache) recordUsage(jti string) {
	cache.mu.Lock()
	defer cache.mu.Unlock()

	cache.cache[jti] = time.Now()
}
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
