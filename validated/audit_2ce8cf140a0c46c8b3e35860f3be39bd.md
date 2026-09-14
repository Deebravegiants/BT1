### Title
Check-then-act TOCTOU race in JWT replay-guard allows a single-use HTTP trigger token to authorize two concurrent workflow executions - (File: core/services/gateway/handlers/capabilities/v2/workflow_metadata_handler.go)

### Summary
`WorkflowMetadataHandler.Authorize` performs a classic time-of-check/time-of-use race: it checks JWT replay status via `jwtCache.isReplay(claims.ID)` and only records the token as used via `jwtCache.recordUsage(claims.ID)` several statements later, with no lock held across the whole "check → validate signer → record" sequence.

### Finding Description
`Authorize` first verifies the JWT and extracts its `jti` (`claims.ID`), then calls `h.jwtCache.isReplay(claims.ID)` to check for reuse. `isReplay` takes only a read lock on the cache and releases it immediately after reading [1](#0-0) . Execution then proceeds to look up authorized keys and validate the signer, and only afterwards calls `h.jwtCache.recordUsage(claims.ID)`, which takes a separate write lock [2](#0-1) . Because the "check" and the "record" are two independent lock acquisitions rather than one atomic critical section, two concurrent unprivileged client requests presenting the identical externally-supplied JWT (same `jti`) can both pass `isReplay` (both return `false`) before either one calls `recordUsage`. Both requests then pass signer authorization and are treated as valid single-use tokens, each triggering a full `SendToNode` broadcast to the DON via `HandleUserTriggerRequest`/`authorizeRequest` [3](#0-2) . This directly mirrors the underlying CVE's bug class (TOCTOU race allowing a check to be bypassed by concurrent access) applied to the gateway's own request-impersonation-prevention mechanism.

Notably, the codebase already implements a race-safe pattern for the analogous problem in `core/capabilities/vault/request_replay_guard.go`, where `CheckAndRecord` performs the existence check and the map write atomically under a single mutex acquisition [4](#0-3) , and that guard's own unit test explicitly validates the race-safe behavior under 100 concurrent goroutines, ensuring exactly one winner [5](#0-4) . The `jwtReplayCache` in the HTTP trigger handler path does not follow this pattern.

### Impact Explanation
A single "one-time-use" workflow-execution JWT can be replayed exactly once under a race window, causing the DON to receive and process a duplicate `MethodWorkflowExecute` trigger for the same request. This undermines the single-use guarantee the code explicitly documents and tests for (`"token has already been used"` / `"JWT token has already been used"`), enabling limited request duplication/impersonation of the same authenticated caller. Because authorization/signer checks still succeed independently for both racing requests, the impact is confined to duplicate execution rather than a full authentication bypass — it does not grant access to a different signer's identity or workflow.

### Likelihood Explanation
Exploitation requires an attacker (or a legitimate but hostile client) to send the same signed JWT to the gateway twice in rapid succession, which is fully controllable and repeatable — no privileged position or network-layer manipulation is needed. The race window is narrow (only the code between the `isReplay` read-lock release and the `recordUsage` write-lock acquisition), but for a client controlling timing of both requests (e.g., firing simultaneous connections) it is straightforward to hit, especially under any concurrent processing/goroutine scheduling. Likelihood is moderate: it requires precise concurrent request timing but no other privilege.

### Recommendation
Make the replay check-and-record atomic, following the exact pattern already used in `core/capabilities/vault/request_replay_guard.go`: combine `isReplay` and `recordUsage` into a single method that takes the write lock once, checks for existence, and inserts the `jti` before releasing the lock, returning an error if it was already present. Update `Authorize` in `workflow_metadata_handler.go` to call this atomic method instead of the separate check/record calls.

### Proof of Concept
1. Register a workflow and its authorized signer key (as in `TestWorkflowMetadataHandler_Authorize`).
2. Create one valid `MethodWorkflowExecute` request signed with a JWT (`jti` = X).
3. Fire two goroutines simultaneously, each calling `handler.Authorize(workflowID, tokenString, req)` (or equivalently POST the same JSON-RPC request with the same `Auth` token twice concurrently to the gateway's HTTP trigger endpoint).
4. Under the current implementation, both calls can observe `isReplay(X) == false` before either calls `recordUsage(X)`, so both succeed and both are forwarded via `SendToNode` to the DON, whereas the existing sequential test (`TestWorkflowMetadataHandler_Authorize/"JWT replay protection"`) only demonstrates correct rejection for sequential (non-concurrent) calls, leaving the concurrent path unverified and exploitable. [6](#0-5)

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

**File:** core/services/gateway/handlers/capabilities/v2/workflow_metadata_handler.go (L399-405)
```go
func (cache *jwtReplayCache) isReplay(jti string) bool {
	cache.mu.RLock()
	defer cache.mu.RUnlock()

	_, exists := cache.cache[jti]
	return exists
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

**File:** core/capabilities/vault/request_replay_guard_test.go (L96-126)
```go
func TestRequestReplayGuard_ConcurrentAccess(t *testing.T) {
	guard := NewRequestReplayGuard()
	futureExpiry := time.Now().UTC().Unix() + 100

	const goroutines = 100
	results := make([]error, goroutines)
	var wg sync.WaitGroup
	wg.Add(goroutines)

	for i := range goroutines {
		go func(idx int) {
			defer wg.Done()
			results[idx] = guard.CheckAndRecord("same-digest", futureExpiry)
		}(i)
	}
	wg.Wait()

	successCount := 0
	duplicateCount := 0
	for _, err := range results {
		if err == nil {
			successCount++
		} else {
			require.ErrorIs(t, err, ErrRequestAlreadySeen)
			duplicateCount++
		}
	}

	assert.Equal(t, 1, successCount, "exactly one goroutine should succeed")
	assert.Equal(t, goroutines-1, duplicateCount, "all others should be rejected as duplicates")
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
