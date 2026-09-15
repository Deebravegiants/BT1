## Analysis

The reported bug class is a **check-effects-interactions violation**: the "interaction" (granting the reward/response) happens before the "effect" (marking state as consumed) is committed, letting an attacker exploit the gap to reuse a one-time authorization multiple times.

The chainlink codebase has a directly analogous unprivileged-actor-reachable flaw in the CRE Gateway's HTTP-trigger JWT replay guard.

`WorkflowMetadataHandler.Authorize` is the JWT-based, one-time-use authentication check for inbound HTTP trigger requests coming from external, unprivileged clients: [1](#0-0) 

It performs:
1. `h.jwtCache.isReplay(claims.ID)` — a **read-lock-only** check.
2. Authorization/key lookup logic (no locking at all).
3. `h.jwtCache.recordUsage(claims.ID)` — the **effect** that marks the JWT as consumed, done only at the very end, under a separate `Lock()`. [2](#0-1) 

Because `isReplay` (step 1) and `recordUsage` (step 3) are two separate, unsynchronized critical sections rather than one atomic check-and-set, there is a race window: two (or more) concurrent requests carrying the *same* JWT (`jti`) can both pass the `isReplay` check before either has called `recordUsage`. Both are then treated as authorized and each triggers a workflow execution.

This function is invoked directly from the internet-facing gateway on every unauthenticated user request: [3](#0-2) 

which itself is called from `HandleUserTriggerRequest`, the entry point for external client HTTP trigger requests before rate limiting is even applied: [4](#0-3) 

There is an existing sequential test proving the intended single-use invariant (`"JWT token has already been used"`) [5](#0-4) , but that test only exercises the two calls sequentially — it does not cover the concurrent race, so the TOCTOU gap is not caught by existing tests.

### Title
JWT replay-guard TOCTOU allows one-time HTTP-trigger token to authorize multiple concurrent workflow executions - (File: core/services/gateway/handlers/capabilities/v2/workflow_metadata_handler.go)

### Summary
`WorkflowMetadataHandler.Authorize` checks whether a JWT `jti` has been used (`isReplay`) and only records it as used (`recordUsage`) at the very end of the function, with no lock held across the whole authorize-then-record sequence. An unprivileged external client can send multiple concurrent HTTP trigger requests bearing the identical single-use JWT before the first request's `recordUsage` call commits, causing all of them to pass the "already used" check.

### Finding Description
The single-use guarantee for HTTP trigger JWTs is meant to be enforced atomically: check-then-set. Instead it is split into two independently locked operations —
`isReplay` under `cache.mu.RLock()` [6](#0-5)  and `recordUsage` under `cache.mu.Lock()` [7](#0-6) , invoked from `Authorize` at lines 87 and 105 respectively with unrelated key-lookup work executed in between [1](#0-0) . This is the same class of bug as the reported `claimDefaulted` issue: the state-mutating "effect" is deferred until after the "interaction" is permitted, leaving a window where the same credential can be replayed.

### Impact Explanation
An attacker who obtains (or is legitimately given) a single-use signed JWT for an HTTP trigger can fire many concurrent requests with that same token. All requests that reach the `isReplay` check before `recordUsage` commits will be authorized, resulting in duplicate/unbounded workflow executions from a single one-time-use token — an unauthorized job-run bypass of the intended one-time authorization control, and a way to bypass the implicit per-token quota (rate limiting is applied only after authorization succeeds, per `HandleUserTriggerRequest`'s ordering of `authorizeRequest` before `checkRateLimit` [4](#0-3) ).

### Likelihood Explanation
The race window is small but real and trivially triggerable by any external, unprivileged caller by dispatching concurrent HTTP requests to the gateway with the same token — no special network position, node compromise, or privileged role is required.

### Recommendation
Make the check-and-record operation atomic: hold a single lock (or use a compare-and-swap on the map) across both the `isReplay` lookup and the `recordUsage` insert inside `jwtReplayCache`, e.g. add a `CheckAndRecord(jti string) bool` method (mirroring the pattern already used correctly in `RequestReplayGuard.CheckAndRecord` [8](#0-7) ) and call it from `Authorize` instead of the separate `isReplay`/`recordUsage` calls.

### Proof of Concept
1. Obtain a valid signed HTTP-trigger JWT with `jti = X` for workflow `W`.
2. Send two (or more) concurrent JSON-RPC requests to the gateway's `MethodWorkflowExecute` endpoint using the identical token/`jti`.
3. Both requests independently call `WorkflowMetadataHandler.Authorize`, which calls `h.jwtCache.isReplay(X)` before either goroutine reaches `h.jwtCache.recordUsage(X)`.
4. Both requests observe `isReplay(X) == false` and proceed to trigger workflow execution, violating the intended single-use guarantee.

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
