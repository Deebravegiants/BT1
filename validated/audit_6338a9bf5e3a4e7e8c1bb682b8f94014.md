The claim is code-accurate: `WorkflowMetadataHandler.Authorize` calls `h.jwtCache.isReplay(claims.ID)` (RLock, check, release) and then separately calls `h.jwtCache.recordUsage(claims.ID)` (Lock, insert, release) only after signer/authorized-key validation passes, with no shared lock spanning both operations.

Audit Report

## Title
JWT replay-cache check-then-set race allows a workflow HTTP trigger token to be reused (double execution) - (File: core/services/gateway/handlers/capabilities/v2/workflow_metadata_handler.go)

## Summary
`WorkflowMetadataHandler.Authorize` gates HTTP-trigger authorization with a JWT one-time-use ("jti") replay cache, but the check (`isReplay`) and the record (`recordUsage`) are two separate lock acquisitions rather than one atomic check-and-set. [1](#0-0)  This creates a TOCTOU window in which two concurrent requests carrying the same signed JWT can both pass the replay check before either records usage, resulting in the same JWT authorizing two workflow-trigger executions.

## Finding Description
`Authorize` verifies the JWT signature, then checks the cache via `isReplay`, which takes an `RLock`, checks map membership, and releases the lock: [2](#0-1)  Only after subsequent signer/authorized-key validation succeeds does the code call `recordUsage`, which acquires a separate `Lock` and inserts the jti: [3](#0-2)  Because these are two distinct critical sections rather than one atomic check-and-set, two goroutines invoking `Authorize` concurrently with the same `claims.ID` can both observe "not replayed" before either calls `recordUsage`, both passing authorization. This directly contrasts with `RequestReplayGuard.CheckAndRecord` in the vault package, which performs the equivalent check-and-insert atomically under a single mutex — confirming the codebase has, and normally uses, the correct pattern elsewhere, but not here. No other code path was found serializing calls to `Authorize` for the same JWT (the `httpTriggerHandler.setupCallback` dedup keys on request ID, not jti, and would not prevent an attacker from submitting the same JWT under two different request IDs).

## Impact Explanation
A JWT intended to authorize exactly one workflow-trigger execution can, under a race, authorize two (or more), causing duplicate downstream workflow executions dispatched to the DON under a single client authorization. This falls into the "gateway request impersonation / replay-bypass" bucket of in-scope impacts, since it defeats the deliberate one-time-use guarantee enforced by this specific authorization control.

## Likelihood Explanation
This is triggerable by any unprivileged JWT holder able to send two concurrent HTTP trigger requests to the gateway using distinct request IDs but the same signed token — no special privilege, node compromise, or host access is required, just ordinary parallel HTTP calls timed to race within the check-then-set window. The race window is narrow but realistic and reproducible with standard tooling (parallel goroutines/curl), matching a classic, deterministic-under-race TOCTOU pattern rather than a purely theoretical scenario.

## Recommendation
Merge `isReplay` and `recordUsage` into a single atomic check-and-set operation guarded by one mutex (mirroring `RequestReplayGuard.CheckAndRecord`), and call it once immediately after signer/authorized-key validation succeeds, eliminating the window between check and record.

## Proof of Concept
1. Client obtains one valid JWT (`jti = X`) signed for a workflow trigger.
2. Client concurrently fires two HTTP trigger requests to the gateway using the same JWT but distinct request IDs (e.g., two goroutines or parallel curl processes).
3. Both goroutines call `Authorize`; both execute `isReplay(X)` and see `false` before either completes `recordUsage(X)` — feasible because `isReplay` and `recordUsage` are non-atomic, separately-locked operations. [4](#0-3) 
4. Both requests pass authorization and are dispatched as independently authorized executions, violating the intended single-use semantics of the token.
5. A Go unit test can directly exercise this by calling `Authorize` from two goroutines with the same `claims.ID`/token and asserting both succeed under a synchronization barrier placed between the `isReplay` check and the `recordUsage` call (e.g., via a test hook or by racing real goroutines many times to observe non-zero double-success occurrences).

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
