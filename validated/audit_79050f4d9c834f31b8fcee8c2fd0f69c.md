## Verification: Confirmed a genuine TOCTOU replay-bypass bug in the JWT replay cache used by the gateway's HTTP Trigger flow.

### Title
JWT Replay Protection is Bypassable via Non-Atomic Check-then-Act (TOCTOU) - (File: core/services/gateway/handlers/capabilities/v2/workflow_metadata_handler.go)

### Summary
The `WorkflowMetadataHandler.Authorize` function, which is invoked by the internet-facing gateway's HTTP Trigger Handler to authenticate every inbound `HTTPTrigger`/`WorkflowExecute` user request, checks JWT replay status and records usage as two separate, independently-locked operations rather than one atomic operation. This mirrors the root cause pattern in the reference report: a security-critical decision is made by reading shared state at one point in time and mutating it at a later, disjoint point in time, leaving a window in which the state is stale relative to concurrent activity.

### Finding Description
`Authorize` calls `h.jwtCache.isReplay(claims.ID)` to check whether a JWT ID (`jti`) has already been used, and only after workflow/signer validation succeeds does it call `h.jwtCache.recordUsage(claims.ID)`: [1](#0-0) 

The cache implementation itself is correct in isolation — `isReplay` takes an `RLock` and `recordUsage` takes a `Lock` — but these are two separate critical sections: [2](#0-1) 

Because `isReplay` (read) and `recordUsage` (write) are not combined into a single atomic "check-and-set" operation (unlike the vault package's `RequestReplayGuard.CheckAndRecord`, which correctly performs the check and insertion under one lock: ` [3](#0-2) `), two concurrent `HandleUserTriggerRequest` calls carrying the identical JWT (same `jti`) can both observe `isReplay(jti) == false` before either one reaches `recordUsage(jti)`. `HandleUserTriggerRequest` is the exact entry point exposed to unprivileged external clients via the gateway: [4](#0-3) 

This is structurally identical to the reported bug class: the security check reads state, but the mutation (write-back) that should make the read-then-decide operation authoritative is deferred/decoupled, so a second actor observing the "before" state instead of the "after" state slips through a control that is supposed to block it exactly once.

### Impact Explanation
The existing unit test `TestWorkflowMetadataHandler_Authorize` (and `duplicate JWT token and request ID` in `http_trigger_handler_test.go`) only validates the sequential/non-concurrent case: [5](#0-4) [6](#0-5) 

Under true concurrency (which the vault package's own `RequestReplayGuard` test suite explicitly stress-tests, e.g. `TestRequestReplayGuard_ConcurrentAccess`, proving the project is aware this race matters), a signed JWT intended to authorize a single workflow-trigger request could be replayed once concurrently, causing the gateway to accept and dispatch the same signed action twice to the workflow DON — an authentication/replay-protection bypass reachable directly from an unprivileged external caller of the gateway.

### Likelihood Explanation
Exploitation requires an attacker (or a legitimate but malicious/misbehaving client) to send the same captured/replayed JWT-bearing request twice in rapid succession so both hit the gateway before the first's `recordUsage` call completes — a narrow but real race window, especially under load or with an intentionally crafted burst. No special privileges are required; it is reachable directly via `HandleUserTriggerRequest` from any external user of the gateway's HTTP Trigger endpoint.

### Recommendation
Merge `isReplay` and `recordUsage` into a single atomic check-and-set method (analogous to the existing, correctly-implemented `vault.RequestReplayGuard.CheckAndRecord`), holding one lock across both the existence check and the insertion, e.g.:
```go
func (cache *jwtReplayCache) checkAndRecord(jti string) bool {
    cache.mu.Lock()
    defer cache.mu.Unlock()
    if _, exists := cache.cache[jti]; exists {
        return false // replay
    }
    cache.cache[jti] = time.Now()
    return true
}
```
and call this single method from `Authorize` instead of the separate `isReplay`/`recordUsage` pair, ensuring only one concurrent caller with a given `jti` can ever succeed.

### Proof of Concept
1. Generate one valid signed JWT (`jti = X`) for a `WorkflowExecute`/`HTTPTrigger` request bound to a registered workflow, as done in `createTestJWTToken`.
2. Fire two concurrent calls to `WorkflowMetadataHandler.Authorize(workflowID, tokenString, req)` (or, end-to-end, two concurrent `HandleUserTriggerRequest` calls) with the identical token.
3. Under the current implementation, both goroutines can call `isReplay(X)` before either calls `recordUsage(X)`, so both return `nil` error / a valid `*gateway.AuthorizedKey`, and the gateway proceeds to dispatch the trigger twice — unlike the sequential test at [7](#0-6)  which only shows the *second, sequential* call is rejected, not the concurrent case.

### Citations

**File:** core/services/gateway/handlers/capabilities/v2/workflow_metadata_handler.go (L80-107)
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

**File:** core/services/gateway/handlers/capabilities/v2/http_trigger_handler.go (L95-109)
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
