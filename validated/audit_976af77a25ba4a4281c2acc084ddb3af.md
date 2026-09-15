Audit Report

## Title
JWT replay protection is bypassable via concurrent duplicate requests (check-then-record race) - (File: core/services/gateway/handlers/capabilities/v2/workflow_metadata_handler.go)

## Summary
`WorkflowMetadataHandler.Authorize` checks for JWT replay via `h.jwtCache.isReplay(claims.ID)` and only marks the JWT as used via `h.jwtCache.recordUsage(claims.ID)` after performing workflow/signer lookups, with the two operations protected by separate, independently-acquired locks rather than a single atomic critical section. [1](#0-0)  This allows two concurrent requests carrying the same one-time JWT to both pass the `isReplay` check before either calls `recordUsage`, defeating the intended single-use guarantee.

## Finding Description
`jwtReplayCache.isReplay` takes a read lock, checks membership, and releases the lock; `recordUsage` separately takes a write lock, inserts the entry, and releases it — these are two distinct critical sections, not one atomic check-and-set. [2](#0-1)  Between the `isReplay` read and the `recordUsage` write in `Authorize`, unrelated work is performed (workflow ID lookup and signer authorization) without holding the JWT cache lock, widening the race window. [3](#0-2) 

This is reachable from an unprivileged, unauthenticated external caller: `gatewayHandler.HandleJSONRPCUserMessage` invokes `triggerHandler.HandleUserTriggerRequest` per incoming JSON-RPC message with no serialization across requests, [4](#0-3)  which in turn calls `authorizeRequest` → `WorkflowMetadataHandler.Authorize` for each request independently. [5](#0-4)  Nothing serializes two concurrent `Authorize` calls for the same `jti` — each request is processed on its own goroutine path without a lock spanning the full request lifecycle. Note that `setupCallback` does deduplicate on `requestID` under `callbacksMu`, [6](#0-5)  but that check happens *after* `authorizeRequest` in `HandleUserTriggerRequest` [7](#0-6)  and only guards duplicate request IDs, not duplicate JWTs — an attacker can send the same JWT with two different `requestID`s to bypass that unrelated guard entirely, or send identical requests where the JWT race itself is the exploited gap prior to `setupCallback` even running.

By contrast, `core/capabilities/vault/request_replay_guard.go`'s `CheckAndRecord` correctly holds a single mutex across both the membership check and the insert, closing this race. [8](#0-7)  The existing test suite only proves sequential replay rejection (`WaitForFirst`, then send second synchronously) and does not exercise or catch the concurrent case. [9](#0-8) 

## Impact Explanation
An external, unprivileged caller who possesses one valid signed JWT intended for single use can, by racing two copies of the same JWT concurrently at the gateway, cause both to be authorized. This results in duplicate/unauthorized execution of the same workflow trigger with a single signed authorization — each accepted request results in real downstream dispatch to workflow DON nodes via `sendWithRetries`/`SendToNode`. [10](#0-9)  This maps to the "unauthorized job run" impact class — the JWT replay protection exists specifically to prevent exactly this outcome and fails to do so under concurrency.

## Likelihood Explanation
Exploitation only requires the attacker's own valid, previously-obtained signed JWT and the ability to fire it twice near-simultaneously — no privileged access, no cryptographic break, and no non-default configuration are needed. The race window spans workflow-ID lookup and signer authorization inside `Authorize`, which is realistically wide enough to hit under concurrent/burst traffic, especially over a network where two connections can arrive within microseconds of each other at the gateway's HTTP layer.

## Recommendation
Make the replay check-and-record atomic by adding a single method, e.g. `jwtReplayCache.CheckAndRecord(jti string) error`, that holds one write lock across both the membership check and the insert (mirroring `RequestReplayGuard.CheckAndRecord`), and have `Authorize` call it in place of the separate `isReplay`/`recordUsage` calls.

## Proof of Concept
1. Register a workflow and generate one valid signed request JWT (`jti = X`), as in `TestHttpTriggerHandler_HandleUserTriggerRequest`'s "duplicate JWT token and request ID" setup. [11](#0-10) 
2. Instead of calling `Authorize` (or `HandleUserTriggerRequest`) sequentially, launch two goroutines that call it concurrently with the same JWT/token (using distinct `requestID`s to bypass the unrelated `callbacksMu`-based `requestID` dedup in `setupCallback`).
3. Add a small artificial delay (or use `sync.WaitGroup`/barrier synchronization) between `isReplay` and `recordUsage` to reliably reproduce the interleave, or run many parallel iterations to hit the natural race; assert that both goroutines return `nil` error from `Authorize` and that `SendToNode` is invoked more than once for the same `jti`.

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

**File:** core/services/gateway/handlers/capabilities/v2/http_handler.go (L392-402)
```go
func (h *gatewayHandler) HandleJSONRPCUserMessage(ctx context.Context, req jsonrpc.Request[json.RawMessage], callback handlers.Callback) error {
	h.metrics.IncrementTriggerRequestCount(ctx, h.lggr)
	err := h.triggerHandler.HandleUserTriggerRequest(ctx, &req, callback, time.Now())
	if err != nil {
		h.lggr.Errorw("failed to handle user trigger request", "requestID",
			req.ID, "err", err)
		// error response is sent to the response channel by the trigger handler
		// so return nil after logging
	}
	return nil
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

**File:** core/services/gateway/handlers/capabilities/v2/http_trigger_handler.go (L643-681)
```go
func (h *httpTriggerHandler) sendWithRetries(ctx context.Context, legacyExecutionID, executionIDWithTriggerIndex string, req *jsonrpc.Request[json.RawMessage], workflowID string, doneCh <-chan struct{}) error {
	if doneCh == nil {
		return errors.New("doneCh cannot be nil")
	}

	assigned := h.workflowMetadataHandler.WorkflowShards(workflowID)
	if len(assigned) == 0 {
		// this shouldn't happen because we checked it in authorizeRequest()
		h.callbacksMu.Lock()
		saved, exists := h.callbacks[req.ID]
		if exists {
			h.handleUserError(ctx, req.ID, jsonrpc.ErrInternal, fmt.Sprintf("Workflow %s is not assigned to any DONs", workflowID), saved.Callback)
			h.cleanupCallback(req.ID)
		}
		h.callbacksMu.Unlock()
		return fmt.Errorf("workflow %s not assigned to any shard", workflowID)
	}

	// Create a context that will be cancelled when the max request duration is reached
	maxDuration := time.Duration(h.config.MaxTriggerRequestDurationMs) * time.Millisecond
	ctxWithTimeout, cancel := context.WithTimeout(ctx, maxDuration)
	defer cancel()

	// Run one send loop per assigned shard in parallel.
	errCh := make(chan error, len(assigned))
	for _, shard := range assigned {
		h.wg.Go(func() {
			errCh <- h.sendToShard(ctxWithTimeout, shard, legacyExecutionID, executionIDWithTriggerIndex, req, doneCh)
		})
	}

	var combinedErr error
	for range assigned {
		if err := <-errCh; err != nil {
			combinedErr = errors.Join(combinedErr, err)
		}
	}
	return combinedErr
}
```

**File:** core/capabilities/vault/request_replay_guard.go (L35-47)
```go
func (g *RequestReplayGuard) CheckAndRecord(digest string, expiresAtUnix int64) error {
	g.mu.Lock()
	defer g.mu.Unlock()

	g.clearExpiredLocked()

	if _, exists := g.seen[digest]; exists {
		return ErrRequestAlreadySeen
	}

	g.seen[digest] = expiresAtUnix
	return nil
}
```

**File:** core/services/gateway/handlers/capabilities/v2/workflow_metadata_handler_test.go (L1193-1217)
```go
	t.Run("JWT replay protection", func(t *testing.T) {
		params := json.RawMessage(`{"test": "data"}`)
		req := &jsonrpc.Request[json.RawMessage]{
			Version: "2.0",
			ID:      "test-request-id-replay",
			Method:  gateway_common.MethodWorkflowExecute,
			Params:  &params,
		}

		token, err := utils.CreateRequestJWT(*req)
		require.NoError(t, err)

		tokenString, err := token.SignedString(privateKey)
		require.NoError(t, err)

		key, err := handler.Authorize(workflowID, tokenString, req)
		require.NoError(t, err)
		require.NotNil(t, key)

		// Second authorization with same JWT should fail (replay attack)
		key, err = handler.Authorize(workflowID, tokenString, req)
		require.Error(t, err)
		require.Contains(t, err.Error(), "JWT token has already been used. Please generate a new one with new id (jti)")
		require.Nil(t, key)
	})
```

**File:** core/services/gateway/handlers/capabilities/v2/http_trigger_handler_test.go (L360-386)
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
```
