The code confirms the claim exactly as described: `isReplay` (RLock-only check) and `recordUsage` (Lock-only write) are two separate lock acquisitions with authorization work happening in between, rather than a single atomic check-and-set operation.Audit Report

## Title
JWT replay guard is check-then-act (non-atomic), allowing a captured JWT to be replayed via concurrent requests - ([File: core/services/gateway/handlers/capabilities/v2/workflow_metadata_handler.go])

## Summary
`WorkflowMetadataHandler.Authorize` protects the HTTP Trigger gateway's unprivileged, internet-facing workflow-execution endpoint against JWT replay by calling `h.jwtCache.isReplay(claims.ID)` and, only after other work completes, `h.jwtCache.recordUsage(claims.ID)`. These are two independent lock acquisitions on `jwtReplayCache` rather than a single atomic check-and-set, so two concurrent requests carrying the same `jti` can both pass the replay check before either records usage.

## Finding Description
`Authorize` performs: (1) JWT signature verification, (2) `h.jwtCache.isReplay(claims.ID)` under `cache.mu.RLock()`, (3) authorized-key/signer lookup, (4) `h.jwtCache.recordUsage(claims.ID)` under a separate `cache.mu.Lock()`. [1](#0-0)  The `isReplay` and `recordUsage` methods use distinct lock sections against the shared `cache map[string]time.Time`: [2](#0-1)  Because the check and the write are not combined into a single atomic critical section, two goroutines processing two concurrent requests with an identical, previously-unused `jti` can both observe `isReplay == false` before either calls `recordUsage`, allowing both to pass authorization.

This is structurally different from another replay guard in the same codebase, `vault.RequestReplayGuard.CheckAndRecord`, which correctly performs the existence-check and the write within a single `mu.Lock()` critical section, guaranteeing atomicity and is explicitly tested for concurrent correctness (`TestRequestReplayGuard_ConcurrentAccess`, which asserts exactly one of 100 concurrent callers succeeds). [3](#0-2) [4](#0-3)  The `jwtReplayCache` used by `WorkflowMetadataHandler` has no equivalent atomic combined operation and no concurrency test covering this race; only a sequential replay test exists. [5](#0-4) 

## Impact Explanation
An attacker (or a client whose JWT is captured/intercepted, or simply a legitimate client racing its own request) can send the same signed, single-use JWT twice concurrently to the gateway's HTTP trigger endpoint, causing both requests to pass the replay check and both to proceed to trigger workflow execution — defeating the single-use guarantee the cache is meant to enforce and resulting in duplicate/unauthorized workflow executions from one signed token. This maps to the in-scope "unauthorized job run" / gateway request impersonation-adjacent impact category.

## Likelihood Explanation
Exploitation requires only the ability to fire two near-simultaneous HTTP requests carrying the same JWT at the gateway's trigger endpoint — well within reach of an unprivileged client, needing no special network position or privileged role. The race window between the `isReplay` read and the `recordUsage` write is narrow but real and reliably triggerable with scripted concurrent requests, especially since substantial work (key/signer lookup) happens between the check and the record, widening the window.

## Recommendation
Make check-and-record atomic: acquire a single write lock, check whether `jti` exists, and if not, insert it immediately in the same critical section (mirroring `RequestReplayGuard.CheckAndRecord`'s pattern), returning "replay detected" otherwise. Perform this reservation immediately after JWT signature verification and before the signer/key authorization work, rolling back the reservation only if subsequent authorization checks fail.

## Proof of Concept
1. Client signs a valid HTTP-trigger JWT with `jti = X` for a workflow key registered in `h.authorizedKeys`.
2. Client sends two concurrent HTTP requests to the gateway's HTTP trigger endpoint, each carrying the identical JWT (`jti = X`).
3. Both requests reach `WorkflowMetadataHandler.Authorize` concurrently.
4. Goroutine A calls `isReplay(X)` → `false`; before A calls `recordUsage(X)`, goroutine B also calls `isReplay(X)` → `false`.
5. Both A and B pass authorization and proceed to trigger workflow execution — a Go unit test spawning two goroutines calling `Authorize` with the same token/claims concurrently (analogous to `TestRequestReplayGuard_ConcurrentAccess` but against `jwtReplayCache`/`Authorize`) would demonstrate both succeeding under race conditions (`go test -race`), unlike the sequential test at `workflow_metadata_handler_test.go` lines 1193-1217 which only exercises the non-concurrent case.

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
