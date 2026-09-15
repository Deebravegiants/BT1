Found it. The `WorkflowMetadataHandler.Authorize` function in `core/services/gateway/handlers/capabilities/v2/workflow_metadata_handler.go` has exactly this class of bug: a check-then-act TOCTOU gap between the JWT replay check (`isReplay`) and the replay record (`recordUsage`), which are two *separate* lock acquisitions rather than one atomic operation — this is the direct Go analog of a missing reentrancy guard (the "check" and "effect" are not atomic, so a second concurrent call can slip through the check before the first call records its usage).

### Title
Non-Atomic JWT Replay Check-and-Record in `WorkflowMetadataHandler.Authorize` Allows Concurrent JWT Reuse - (File: `core/services/gateway/handlers/capabilities/v2/workflow_metadata_handler.go`)

### Summary
`Authorize` calls `h.jwtCache.isReplay(claims.ID)` and, later, `h.jwtCache.recordUsage(claims.ID)` as two independent, separately-locked operations rather than a single atomic "check-and-record" step. This is structurally the same class of bug as the reported "missing nonReentrant guard": the state-mutating effect (marking the JWT as used) happens after other logic has already run, leaving a window in which two concurrent invocations with the same JWT can both pass the check before either records usage.

### Finding Description
`Authorize` first verifies the JWT and signer, then checks replay status via `jwtReplayCache.isReplay`, which only takes an `RLock`: [1](#0-0) 

It then proceeds through authorized-key lookups (`h.authorizedKeys[workflowID]`, signer membership check) and only calls `h.jwtCache.recordUsage(claims.ID)` at the very end of the function, which acquires a separate `Lock`: [2](#0-1) [3](#0-2) 

Because `isReplay` (read) and `recordUsage` (write) are two distinct critical sections rather than one atomic check-and-set (compare with the properly atomic pattern in `RequestReplayGuard.CheckAndRecord`, which holds a single mutex across both the existence check and the insert: `core/capabilities/vault/request_replay_guard.go` lines 35-47), two goroutines handling the same JWT concurrently (e.g., the caller retries the HTTP trigger request while the first attempt is still in flight, or an attacker deliberately races the same signed JWT) can both observe `isReplay == false` and both proceed to be authorized before either records the JTI as used.

### Impact Explanation
`HTTPTriggerHandler.HandleUserTriggerRequest` calls `authorizeRequest`, which calls `WorkflowMetadataHandler.Authorize` to validate a caller-supplied JWT before forwarding a workflow-execute request to the DON: [4](#0-3) 

A successful bypass of the single-use JWT replay guard lets an unprivileged caller reuse one signed authorization to admit more than one concurrent workflow-execute request past authorization, undermining the intended one-request-per-JWT guarantee that the replay cache exists to enforce (as demonstrated by the sequential replay test at `workflow_metadata_handler_test.go` lines 1193-1217, which only proves the sequential case, not the concurrent race).

### Likelihood Explanation
Exploitation requires only sending the same signed JWT-bearing request twice in close succession (a race, not a complex precondition), reachable directly from any unprivileged client via `HandleUserTriggerRequest`. However, the outer duplicate-request-ID and downstream idempotent-execution dedup logic (`ExecutionsStore.Add` / `ErrDuplicateExecution` in `core/services/workflows/v2/engine.go`) may absorb some of the practical impact depending on how request IDs and execution IDs are derived, which somewhat lowers real-world severity versus the immediate authorization bypass itself.

### Recommendation
Merge the check and the record into one atomic operation under a single mutex, mirroring `RequestReplayGuard.CheckAndRecord`:
```go
func (cache *jwtReplayCache) checkAndRecord(jti string) error {
    cache.mu.Lock()
    defer cache.mu.Unlock()
    if _, exists := cache.cache[jti]; exists {
        return errors.New("JWT token has already been used...")
    }
    cache.cache[jti] = time.Now()
    return nil
}
```
and call it immediately after JWT signature verification, before any authorization-dependent logic, so no two concurrent calls can pass the check for the same `jti`.

### Proof of Concept
1. Sign a valid trigger-request JWT with `jti = "X"`.
2. Fire two concurrent `HandleUserTriggerRequest` calls with the identical JWT.
3. Both goroutines call `Authorize`; both call `isReplay("X")` before either calls `recordUsage("X")`, since these are separate lock sections with attacker-controllable timing (e.g., via slow signer-lookup contention on `h.mu.RLock()` in between).
4. Both requests pass authorization and are forwarded, defeating the intended single-use enforcement.

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

**File:** core/services/gateway/handlers/capabilities/v2/workflow_metadata_handler.go (L407-412)
```go
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
