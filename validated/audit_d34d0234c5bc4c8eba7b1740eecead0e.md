This confirms the claim's technical mechanics are accurate. The `authorizeRequest` step at [1](#0-0)  only validates JWT signature and workflow-key ownership via `WorkflowMetadataHandler.Authorize`, which checks the JWT replay cache keyed by `claims.ID` (jti) at [2](#0-1)  — this is a separate, independent uniqueness check from the `req.ID`/`requestID` used as the `callbacks` map key. Nothing in the authorization path ties the `requestID` to the caller's specific workflow, and `setupCallback` performs its conflict check purely on the global `requestID` string at [3](#0-2) .

Audit Report

## Title
Global, unscoped `requestID` namespace in `httpTriggerHandler` allows cross-workflow DoS via request-ID squatting - (File: core/services/gateway/handlers/capabilities/v2/http_trigger_handler.go)

## Summary
The gateway's HTTP trigger handler stores in-flight requests in a single, node-wide map keyed only by the client-supplied `requestID`, with no owner/workflow scoping. Any authenticated workflow caller can pre-register a `requestID` that another, unrelated workflow's caller later uses, causing that caller's legitimate request to be permanently rejected as a duplicate.

## Finding Description
`httpTriggerHandler.callbacks` is declared as `map[string]savedCallback // requestID -> savedCallback` with no namespacing by workflow ID or owner [4](#0-3) . `setupCallback` checks for a pre-existing entry keyed purely on `requestID` and rejects the request as a conflict if found [3](#0-2) . `HandleUserTriggerRequest` validates the request, resolves the caller's own workflow ID, authorizes against that workflow's registered key, and only then reaches `setupCallback` [5](#0-4) . `authorizeRequest` verifies the JWT signature/ownership for the caller's own workflow and checks a *separate* JWT-jti replay cache — it never validates or reserves ownership of the `requestID` string itself [2](#0-1) . Consequently, any caller authorized for *any* workflow can insert an entry into the shared `callbacks` map under an arbitrary `requestID` of their choosing, and if that value coincides with the `requestID` a different, unrelated workflow's caller is about to use, the legitimate caller's `setupCallback` call is rejected with `jsonrpc.ErrConflict`.

## Impact Explanation
This is a genuine unprivileged, cross-user denial-of-service on the gateway's internet-facing trigger path: an attacker holding a valid key for any workflow can block execution of another, unrelated workflow's request by pre-registering its `requestID`, and the shared `callbacks` map has no scoping that would prevent this. The affected request is rejected before reaching execution, degrading availability of the workflow-execution trigger for the targeted caller/workflow — this fits the "cross-user response corruption" / availability-of-service impact class rather than fund loss or key exfiltration.

## Likelihood Explanation
Exploitability is conditioned on the attacker successfully guessing/pre-registering the victim's exact `requestID` value ahead of the victim's real request, since the only constraint on user-supplied IDs is that they cannot contain `/` [6](#0-5) . This is realistic against predictable/low-entropy or sequential ID schemes and is directly demonstrated by the existing conflict-rejection test [7](#0-6) , though it is significantly mitigated for clients using high-entropy random IDs (e.g., UUIDv4), which reduces overall practical likelihood.

## Recommendation
Scope the `callbacks` map key by `(workflowID, requestID)` or `(workflowOwner, requestID)` rather than `requestID` alone, so request-ID uniqueness is enforced only within the caller's own workflow namespace, following the same authorize-then-scope pattern used by `GatewayVaultRequestProcessor`, which prefixes IDs with the authorized owner before storing them in `activeRequests` [8](#0-7) .

## Proof of Concept
1. Attacker holds a valid signing key authorized for workflow `A`.
2. Attacker predicts/guesses the `requestID = "X"` that victim workflow `B`'s legitimate client will soon use.
3. Attacker sends a valid `MethodWorkflowExecute` request for workflow `A` with `req.ID = "X"`; `setupCallback` inserts `h.callbacks["X"]` unconditionally [3](#0-2) .
4. Victim sends its legitimate, authorized request for workflow `B` with the same `req.ID = "X"`.
5. `setupCallback` finds `h.callbacks["X"]` already present and rejects the victim's request with `jsonrpc.ErrConflict`, as demonstrated by the existing duplicate-request-ID test [7](#0-6) . A new integration test reproducing steps 1-4 with two *different* workflow IDs/JWTs (rather than the same JWT as in the existing test) would conclusively demonstrate the cross-workflow collision.

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

**File:** core/services/gateway/handlers/capabilities/v2/README.md (L266-270)
```markdown
### 9.1 Request ID Format

- **User Requests**: Plain string identifiers (cannot contain "/")
- **Node Messages**: Format `<methodName>/<workflowID>/<uuid>` or `<methodName>/<workflowID>/<workflowExecutionID>/<uuid>`
- **Method Routing**: Gateway routes messages based on method name in request ID
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
