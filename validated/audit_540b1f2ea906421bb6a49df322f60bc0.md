## Analysis

The Tokemak bug class is a **checkpoint-after-action race**: the state update that is supposed to gate/limit a benefit (the Synthetix reward checkpoint) is performed *after* the benefit has already been granted, leaving a window where the same actor can re-enter and get the benefit twice before the checkpoint closes it off.

The same pattern exists in the chainlink gateway's JWT replay-protection for the HTTP Trigger unprivileged user path. [1](#0-0) 

### Title
JWT replay-protection check-then-act race allows a single signed trigger request to be executed twice - (File: core/services/gateway/handlers/capabilities/v2/workflow_metadata_handler.go)

### Summary
`WorkflowMetadataHandler.Authorize` decides whether a JWT-signed HTTP trigger request is fresh by calling `h.jwtCache.isReplay(claims.ID)` and only marks the token as consumed afterwards via `h.jwtCache.recordUsage(claims.ID)`, once several unrelated authorization checks have passed. These are two independent, separately-locked critical sections rather than one atomic check-and-set operation.

### Finding Description
`jwtReplayCache.isReplay` acquires an `RLock`, checks map membership, and releases the lock; `jwtReplayCache.recordUsage` acquires a separate `Lock` later, after workflow lookup and signer-authorization checks have run. [2](#0-1) 

Because these are two distinct locked operations rather than a single atomic "check-and-record," two concurrent `Authorize` calls carrying the *same* JWT (same `jti`) can both pass the `isReplay` check before either reaches `recordUsage`. `Authorize` is invoked from `authorizeRequest` in the HTTP Trigger handler, which is on the unauthenticated, internet-facing gateway path taken for every incoming user `HandleUserTriggerRequest`/`workflowExecute` call — i.e., any external client that possesses (or intercepts) one valid signed JWT can win this race. [3](#0-2) 

This mirrors the Tokemak root cause exactly: the "checkpoint" (marking the token/rewarder position as consumed) is applied only after the privileged action (authorization/reward eligibility) has already been evaluated and granted, so a concurrent second call slips through the same window instead of being blocked by the already-recorded state.

### Impact Explanation
A successful race lets a single signed workflow-trigger JWT authorize two (or more) concurrent workflow executions instead of exactly one, defeating the intended one-time-use / anti-replay guarantee documented at the call site ("JWT token has already been used. Please generate a new one with new id (jti)"). This is a concrete request-impersonation / replay bypass that can trigger an unauthorized duplicate job run for a workflow owner's DON, which is exactly the class of impact the validation rules call out (unauthorized job run via allowlist/session-token bypass).

### Likelihood Explanation
Exploitation requires only sending the same previously-observed/valid signed request twice in quick succession (no signing key needed, no elevated privileges, no malicious node/peer). Any client capable of capturing or replaying its own signed trigger request (or one leaked/observed in transit before TLS termination, logs, proxies, etc.) can attempt this; the race window is small (a handful of map lookups) but the check-then-act pattern is a genuine TOCTOU bug, not a hypothetical one — the existing single-threaded tests only assert sequential replay is rejected and do not cover concurrent calls with the same `jti`. [4](#0-3) 

### Recommendation
Make replay-check and consumption atomic: hold a single lock for the whole "check-if-seen, then mark-as-seen" sequence (e.g., a `CheckAndRecord`-style method similar to the pattern already used in `core/capabilities/vault/request_replay_guard.go`, which performs both the lookup and insertion under one mutex acquisition) instead of separate `isReplay`/`recordUsage` calls in `WorkflowMetadataHandler.Authorize`. [5](#0-4) 

### Proof of Concept
1. Obtain one validly signed `workflowExecute` JWT request (e.g., a legitimate workflow owner's own token, or one intercepted before consumption).
2. Fire two concurrent `HandleUserTriggerRequest` calls to the gateway carrying the identical JWT/`jti`.
3. Both goroutines call `WorkflowMetadataHandler.Authorize`; both call `h.jwtCache.isReplay(claims.ID)` before either calls `h.jwtCache.recordUsage(claims.ID)` (each is a separately locked, non-atomic step) — both authorize successfully and the workflow trigger is dispatched twice from a single one-time-use token, matching the concurrent test scenario already exercised for `RequestReplayGuard` (`TestRequestReplayGuard_ConcurrentAccess`) but *not* implemented for the JWT cache in `workflow_metadata_handler.go`. [6](#0-5)

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
