### Title
Non-atomic check-then-act JWT replay guard allows concurrent request authorization bypass in `WorkflowMetadataHandler.Authorize` - (File: core/services/gateway/handlers/capabilities/v2/workflow_metadata_handler.go)

### Summary
`WorkflowMetadataHandler.Authorize` enforces JWT single-use ("replay protection") using two separate, non-atomic operations: `jwtCache.isReplay(claims.ID)` (an `RLock`-guarded read) followed later by `jwtCache.recordUsage(claims.ID)` (a `Lock`-guarded write), with unrelated work (workflow/signer lookups) executing in between. [1](#0-0)  This mirrors the reported Mattermost bug class: failing to enforce atomic single-use consumption of a magic-link/token, allowing an attacker to submit concurrent requests with the same token and have more than one succeed before the token is marked used.

### Finding Description
The replay guard is implemented as a `jwtReplayCache` with independent locked methods `isReplay` and `recordUsage`: [2](#0-1) 

`Authorize` calls `isReplay` first to reject already-used JTIs, then performs workflow lookup and signer authorization checks, and only calls `recordUsage` at the very end, right before returning success: [1](#0-0) 

Because `isReplay` and `recordUsage` are two separate critical sections rather than a single atomic "check-and-set" operation, two (or more) concurrent calls to `Authorize` with the identical signed JWT (same `jti`/digest) can each pass the `isReplay` check before either has called `recordUsage`. Both requests then proceed through workflow/signer validation and both can return a valid `*gateway.AuthorizedKey`, effectively granting the caller a second (or Nth) independent authorization from a single-use token — a classic TOCTOU (time-of-check to time-of-use) race, the same root cause class as the Mattermost advisory (lack of atomic single-use token consumption enabling multiple sessions from concurrent requests).

By contrast, the codebase's own Vault authorizer demonstrates the correct atomic pattern via `RequestReplayGuard.CheckAndRecord`, which performs the "already seen" check and the recording of usage inside a single mutex-held critical section: [3](#0-2) 

The `WorkflowMetadataHandler`'s `jwtReplayCache` lacks an equivalent atomic `CheckAndRecord`-style method, so it doesn't get this protection.

### Impact Explanation
An unprivileged, unprivileged network client capable of obtaining or crafting one valid signed JWT for a workflow-execute request (i.e., one legitimate authorization) can send it concurrently to the gateway's HTTP trigger path (`http_trigger_handler.go`'s `HandleUserTriggerRequest`, which calls into `Authorize`) and obtain multiple independent successful authorizations/executions from what should be a strictly single-use token. This is a request-impersonation / authorization-bypass style issue: it undermines the guarantee that a signed request digest can only ever authorize one action, potentially enabling duplicate workflow triggers or double-processing of otherwise single-use authorized actions.

### Likelihood Explanation
The race window is real but narrow — it requires the attacker to fire near-simultaneous requests with the same token so that both `isReplay` reads occur before either `recordUsage` write completes. This is a bug class specifically called out as exploitable "via concurrent requests" in the referenced advisory, and the intervening workflow/signer-lookup work in `Authorize` (map lookups) provides an appreciable window for the race to be won under load or with deliberately parallelized attacker requests. Likelihood is realistically Medium: a motivated attacker sending several parallel requests can amplify the odds of the race succeeding.

### Recommendation
Make the replay-check-and-record path atomic. Add a single method, e.g. `jwtReplayCache.CheckAndRecord(jti string) error`, that under one `Lock`/`Unlock` critical section checks for existence and inserts the JTI immediately, returning an "already used" error if found — mirroring `RequestReplayGuard.CheckAndRecord` in `core/capabilities/vault/request_replay_guard.go`. Call this atomic method as the very first step of `Authorize`, before performing workflow/signer authorization, so no two concurrent calls with the same `jti` can both pass the check.

### Proof of Concept
Conceptually (not proving exploitation, since PoC execution requires runtime access):
1. Sign one JWT for a valid workflow-execute request (as in `TestWorkflowMetadataHandler_Authorize`'s "successful authorization" subtest).
2. Fire two goroutines that call `handler.Authorize(workflowID, tokenString, req)` concurrently with the same token.
3. Due to the non-atomic `isReplay`→(other logic)→`recordUsage` sequence, both goroutines can observe `isReplay == false` before either executes `recordUsage`, causing both to return a valid `*gateway.AuthorizedKey` instead of the second one failing with "JWT token has already been used" as intended by the existing sequential test at: [4](#0-3)

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
