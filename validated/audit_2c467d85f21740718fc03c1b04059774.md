## Finding: JWT replay-protection cache in gateway `WorkflowMetadataHandler.Authorize` is not atomic (TOCTOU race)

### Title
JWT replay protection is bypassable via concurrent duplicate requests (check-then-record race) - (File: core/services/gateway/handlers/capabilities/v2/workflow_metadata_handler.go)

### Summary
The gateway's HTTP-trigger authorization path uses a `jwtReplayCache` to prevent a signed JWT (identified by its `jti` claim) from being used more than once. Unlike the analogous `RequestReplayGuard.CheckAndRecord` in the vault package, which performs the "already seen?" check and the "mark as seen" write atomically under a single mutex, the gateway's cache splits these into two independently-locked operations (`isReplay` then `recordUsage`) with unrelated work (workflow lookup, signer authorization) executed in between. This reproduces the same bug class as the CoreWCF advisory: the replay-detection mechanism exists and is enabled, but is inoperative against a token that is reused before the first use finishes recording it.

### Finding Description
`WorkflowMetadataHandler.Authorize` performs:
1. `h.jwtCache.isReplay(claims.ID)` — read lock, check membership, release lock.
2. Workflow/signer lookups (no locking of the JWT cache).
3. `h.jwtCache.recordUsage(claims.ID)` — write lock, insert, release lock. [1](#0-0) 

The cache implementation itself confirms the check and the write are two separate critical sections, not one atomic "check-and-set": [2](#0-1) 

Because the two lock sections are separate, two goroutines processing the same JWT concurrently can both execute `isReplay` and see "not seen yet" before either calls `recordUsage`. Both requests then pass authorization for the same one-time JWT, and the second `recordUsage` call simply overwrites the first entry's timestamp instead of causing a rejection.

This is directly comparable to `core/capabilities/vault/request_replay_guard.go`'s `CheckAndRecord`, which correctly holds a single mutex across the check-and-insert: [3](#0-2) 

That vault implementation is not vulnerable to this race; the gateway's `jwtReplayCache` is.

The `Authorize` method is reachable from an unprivileged/unauthenticated network caller through the HTTP trigger handling path (`HandleUserTriggerRequest`), which is exactly the path exercised by the "duplicate JWT token and request ID" test — that test only proves the *sequential* replay is blocked, not the concurrent case: [4](#0-3) 

### Impact Explanation
An external, unprivileged caller who intended their signed, single-use JWT to be usable exactly once can defeat that guarantee by firing two (or more) copies of the same request/JWT at the gateway in parallel. Both can be accepted as authorized, causing the underlying workflow trigger to be executed/broadcast more than once for a single signed authorization (`mockDon.EXPECT().SendToNode(...).Times(3)` fan-out per accepted request in the referenced test shows each successful authorization results in real downstream node dispatch). This is a duplicate/unauthorized job execution outcome — the same class of impact the advisory describes (a token replay that should have been rejected succeeds), scoped here to duplicate workflow trigger executions rather than a full authentication bypass.

### Likelihood Explanation
Exploitability requires only the ability to send the same signed request/JWT twice at (near-)the same time — something entirely within an external caller's control, requiring no privileged access, no cryptographic breakage, and no non-default configuration. The race window is the time between the `isReplay` read and the `recordUsage` write, which spans the workflow ID lookup and signer authorization logic in `Authorize`, making the window realistically hittable under concurrent load or an intentionally crafted burst.

### Recommendation
Make the replay check-and-record atomic: hold a single write lock for the full "check membership, then insert" sequence (mirroring `RequestReplayGuard.CheckAndRecord` in `core/capabilities/vault/request_replay_guard.go`), e.g. add a combined `jwtReplayCache.CheckAndRecord(jti string) error` method used by `Authorize` instead of separate `isReplay`/`recordUsage` calls.

### Proof of Concept
1. Generate one valid signed request JWT (`jti = X`) for a registered workflow, as done in `TestHttpTriggerHandler_HandleUserTriggerRequest`'s "duplicate JWT token and request ID" subtest setup.
2. Instead of sending it sequentially, dispatch it via two goroutines simultaneously to `WorkflowMetadataHandler.Authorize` (or the higher-level `HandleUserTriggerRequest`).
3. Both goroutines can call `isReplay(X)` before either calls `recordUsage(X)`, so both pass authorization and both trigger downstream `SendToNode` calls — despite the JWT being intended for single use. [5](#0-4)

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
