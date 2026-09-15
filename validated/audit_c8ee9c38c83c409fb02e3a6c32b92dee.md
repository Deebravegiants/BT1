The code confirms the claim precisely. The check-then-record pattern in `Authorize` is exactly as described, with `isReplay` and `recordUsage` as two separate, independently-locked operations with no atomicity across the whole authorization flow.

Audit Report

## Title
JWT replay-nonce check-then-record is not atomic in `WorkflowMetadataHandler.Authorize`, allowing concurrent replay of a single signed HTTP trigger token - (File: `core/services/gateway/handlers/capabilities/v2/workflow_metadata_handler.go`)

## Summary
`Authorize` checks `h.jwtCache.isReplay(claims.ID)` and only calls `h.jwtCache.recordUsage(claims.ID)` after the signer/authorized-key check succeeds, with no lock held across the whole sequence [1](#0-0) . `isReplay` and `recordUsage` each independently acquire/release the cache's `sync.RWMutex` [2](#0-1) , so two concurrent calls with the same JWT can both pass `isReplay` before either calls `recordUsage`, defeating the single-use design.

## Finding Description
`Authorize` verifies the JWT, then performs a read-check `isReplay(claims.ID)`, then looks up authorized keys, and only afterward calls `recordUsage(claims.ID)` [1](#0-0) . The `jwtReplayCache` type's `isReplay` and `recordUsage` methods each take their own lock independently rather than sharing one critical section across the check-and-set [2](#0-1) . This is a genuine TOCTOU (time-of-check-to-time-of-use) race: nothing in `Authorize` prevents a second concurrent call with the identical `jti` from reading `isReplay == false` before the first call's `recordUsage` commits.

This path is reachable by an unprivileged caller of the gateway. `Authorize` is invoked from `httpTriggerHandler.authorizeRequest`, which is called from `HandleUserTriggerRequest` on every inbound trigger request [3](#0-2) , and `HandleUserTriggerRequest` calls `authorizeRequest` on the path from request validation through to dispatch of the request to DON nodes [4](#0-3) . The JWT's `jti` claim is intentionally meant to be single-use, as reflected in the rejection message "JWT token has already been used" [5](#0-4) , and this is the only replay defense on this path — no other mutex or idempotency mechanism wraps the full `Authorize` call.

## Impact Explanation
A captured or leaked single-use JWT could, under a race, authorize two concurrent trigger requests instead of one, causing duplicate/unauthorized workflow executions to be dispatched to the DON — this maps to Chainlink's "unauthorized job run" impact category. However, this is a narrow-window (in-memory map read/write) race requiring precise concurrent submission of two requests carrying the identical token before the first's `recordUsage` executes; there is no code path here that leaks credentials or bypasses signature/authorized-key verification themselves — signature validation and authorized-key checks (steps that already gate the far more privileged part of authorization) remain intact and unaffected by this race.

## Likelihood Explanation
Exploitation only requires possession of one valid signed JWT and firing two requests nearly simultaneously with two different top-level JSON-RPC IDs (bypassing the separate duplicate-request-ID guard, since `jti` and the trigger request ID are distinct fields). No elevated privilege beyond capturing/being issued one legitimate single-use token is needed, making this reachable by any actor who already has legitimate access to trigger the workflow once. The race window is narrow (two map operations), so reliable exploitation requires some retry effort but is realistically achievable given the code allows it deterministically under true concurrency.

## Recommendation
Make the replay check-and-mark atomic: hold a single lock across both the existence check and the insertion (e.g., a `checkAndRecord(jti) bool` method on `jwtReplayCache` that does `cache.mu.Lock(); defer cache.mu.Unlock(); if _, exists := cache.cache[jti]; exists { return false }; cache.cache[jti] = time.Now(); return true`), and call this single atomic operation as the very first replay-relevant action, rejecting the caller immediately if it returns false, before proceeding to the authorized-key check.

## Proof of Concept
1. Register a workflow with an authorized signer key via `WorkflowMetadataHandler` (as in `TestHttpTriggerHandler_HandleUserTriggerRequest_JWTAuthorization`, see [6](#0-5) ).
2. Construct one signed JWT (`req.Auth`) for a trigger request.
3. Spawn two goroutines that each call `handler.workflowMetadataHandler.Authorize(workflowID, token, req)` concurrently (or two goroutines calling `HandleUserTriggerRequest` with two different `req.ID`s but the same `req.Auth`).
4. Under repeated runs (e.g., with `go test -race -count=100` or artificially delaying between `isReplay` and `recordUsage` via test instrumentation/mocking), both calls occasionally return a non-nil `*AuthorizedKey` with no error, demonstrating the single-use token authorized two executions.

### Citations

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

**File:** core/services/gateway/handlers/capabilities/v2/http_trigger_handler.go (L95-147)
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

**File:** core/services/gateway/handlers/capabilities/v2/http_trigger_handler_test.go (L1003-1064)
```go
func TestHttpTriggerHandler_HandleUserTriggerRequest_JWTAuthorization(t *testing.T) {
	handler, mockDon := createTestTriggerHandler(t)
	ctx := t.Context()

	// Setup metadata handler with test data
	err := handler.workflowMetadataHandler.aggs[handler.workflowMetadataHandler.shards[0].donID].Start(ctx)
	require.NoError(t, err)
	defer handler.workflowMetadataHandler.aggs[handler.workflowMetadataHandler.shards[0].donID].Close()

	// Create test keys
	privateKey := createTestPrivateKey(t)
	signerAddr := crypto.PubkeyToAddress(privateKey.PublicKey)

	// Add authorized key to metadata handler
	key := gateway_common.AuthorizedKey{
		KeyType:   gateway_common.KeyTypeECDSAEVM,
		PublicKey: strings.ToLower(signerAddr.Hex()),
	}
	handler.workflowMetadataHandler.authorizedKeys[workflowID] = map[gateway_common.AuthorizedKey]struct{}{key: {}}
	handler.workflowMetadataHandler.workflowIDToRef[workflowID] = workflowReference{
		workflowOwner: workflowOwner,
		workflowName:  "test-workflow",
		workflowTag:   "v1.0",
	}
	// Assign the workflow to all shards so setupCallback/sendWithRetries can
	// fan the request out (these tests populate the metadata maps directly
	// instead of calling registerWorkflow).
	assignWorkflowToAllShards(handler.workflowMetadataHandler, workflowID)

	t.Run("successful JWT authorization", func(t *testing.T) {
		callback := hc.NewCallback()

		triggerReq := createTestTriggerRequest(workflowID)
		reqBytes, err2 := json.Marshal(triggerReq)
		require.NoError(t, err2)

		rawParams := json.RawMessage(reqBytes)
		req := &jsonrpc.Request[json.RawMessage]{
			Version: "2.0",
			ID:      "test-request-id",
			Method:  gateway_common.MethodWorkflowExecute,
			Params:  &rawParams,
		}

		jwtToken := createTestJWTToken(t, req, privateKey)
		req.Auth = jwtToken

		mockDon.EXPECT().SendToNode(mock.Anything, "node1", mock.MatchedBy(func(r *jsonrpc.Request[json.RawMessage]) bool {
			var params gateway_common.HTTPTriggerRequest
			err = json.Unmarshal(*r.Params, &params)
			return err == nil && params.Key.PublicKey == key.PublicKey
		})).Return(nil)
		mockDon.EXPECT().SendToNode(mock.Anything, "node2", mock.Anything).Return(nil)
		mockDon.EXPECT().SendToNode(mock.Anything, "node3", mock.Anything).Return(nil)

		err = handler.HandleUserTriggerRequest(ctx, req, callback, time.Now())
		require.NoError(t, err)
		handler.callbacksMu.Lock()
		_, exists := handler.callbacks[req.ID]
		handler.callbacksMu.Unlock()
		require.True(t, exists)
	})
```
