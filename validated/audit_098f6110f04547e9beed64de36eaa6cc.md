This confirms the analog. The `Authorize` function performs a classic check-then-act (TOCTOU) race: `h.jwtCache.isReplay(claims.ID)` is checked and returned as "not a replay" while holding only an `RLock`, then, after further work (workflow lookup, key match), `h.jwtCache.recordUsage(claims.ID)` is called separately under a fresh `Lock`. The check and the record are not atomic, and nothing serializes concurrent `Authorize` calls for the same `jti` between the two steps.

### Title
JWT replay-protection race condition allows a single-use gateway token to authorize multiple concurrent requests - ([File: core/services/gateway/handlers/capabilities/v2/workflow_metadata_handler.go])

### Summary
`WorkflowMetadataHandler.Authorize` is meant to guarantee that each JWT (`jti` claim) authorizes exactly one HTTP trigger request. It does so with a check-then-act sequence — `isReplay()` then, after further processing, `recordUsage()` — instead of an atomic check-and-set, mirroring the class of bug fixed in the referenced lighthouse commit (state consulted before being registered, allowing the same identity to slip through the gate twice).

### Finding Description
`Authorize` first verifies the JWT signature, then calls `h.jwtCache.isReplay(claims.ID)` which only takes `jwtReplayCache.mu.RLock()` and returns whether the `jti` is present [1](#0-0) . Only after further workflow/key-authorization checks does it call `h.jwtCache.recordUsage(claims.ID)`, which separately takes `mu.Lock()` and writes the entry [2](#0-1) . The read (`isReplay`) and the write (`recordUsage`) are two independent lock acquisitions on the same `jwtReplayCache`, defined as: [3](#0-2) 

If two requests carrying the same JWT (same `jti`) arrive concurrently — trivially achievable by an unprivileged external caller replaying the captured token twice in parallel with two different JSON-RPC `req.ID`s — both goroutines can pass `isReplay` before either calls `recordUsage`, since there is no lock held across the whole "check, authorize, record" sequence. Both then proceed to be treated as authorized.

This is distinct from the JSON-RPC-level dedup in `httpTriggerHandler.setupCallback`, which is atomic under `callbacksMu` [4](#0-3) , but that dedup keys on the JSON-RPC request ID, not on the JWT `jti`. An attacker who varies the outer request ID while reusing the same JWT bypasses the `setupCallback` guard entirely and only depends on the racy `Authorize` check to be rejected as a "duplicate JWT."

### Impact Explanation
A workflow HTTP trigger is meant to be single-use per issued JWT (`ErrInvalidRequest`, "JWT token has already been used"). Winning the race lets an unprivileged caller (anyone in possession of one valid, previously-used-once token, e.g. leaked, intercepted, or logged) trigger duplicate concurrent executions of the same workflow using a token that should only authorize one execution — an unauthorized workflow-run/replay bypass reachable purely from the gateway's public request path, with no privileged access required.

### Likelihood Explanation
The race window spans JWT signature verification plus workflow/key lookups (map reads under `WorkflowMetadataHandler.mu` are not even held during `Authorize`, widening the window further) — a hundreds-of-microseconds-to-millisecond window that is straightforward to hit by firing two HTTP-trigger requests with the same JWT back-to-back from a client, as also demonstrated implicitly by the existing single-threaded regression test (`TestHttpTriggerHandler_HandleUserTriggerRequest`, "duplicate JWT token and request ID") which only exercises the sequential case and does not test concurrent replay.

### Recommendation
Make the "check jti is unused" and "mark jti as used" operations atomic under one critical section (e.g., a single `jwtReplayCache.CheckAndRecord(jti)` method analogous to `vault.RequestReplayGuard.CheckAndRecord`, which already implements this pattern correctly with one lock covering both the existence check and insertion [5](#0-4) ), and call it before doing the authorization-dependent work in `Authorize`, or otherwise ensure only the winning goroutine for a given `jti` proceeds.

### Proof of Concept
1. Register a workflow and obtain one valid JWT for it (as in `TestHttpTriggerHandler_HandleUserTriggerRequest`'s "duplicate JWT token and request ID" subtest).
2. Craft two `jsonrpc.Request` HTTP trigger messages with different `req.ID` values but the same JWT `Auth` token (same `jti`).
3. Dispatch both concurrently to `httpTriggerHandler.HandleUserTriggerRequest` (or directly to `WorkflowMetadataHandler.Authorize`) from two goroutines.
4. Observe that both can pass `isReplay` before either calls `recordUsage`, causing both to be authorized and both to trigger execution of the workflow — instead of the second being rejected with "JWT token has already been used."

### Citations

**File:** core/services/gateway/handlers/capabilities/v2/workflow_metadata_handler.go (L80-90)
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
```

**File:** core/services/gateway/handlers/capabilities/v2/workflow_metadata_handler.go (L92-107)
```go
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
