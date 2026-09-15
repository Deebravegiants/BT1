### Title
JWT replay-protection check-then-act race condition allows duplicate workflow execution triggers - ([File: core/services/gateway/handlers/capabilities/v2/workflow_metadata_handler.go])

### Summary
The `WorkflowMetadataHandler.Authorize` function in the HTTP Trigger gateway handler validates a JWT and checks it against a replay-protection cache, but the "check" and "record" operations are not atomic. An unprivileged remote caller can send the same signed HTTP-trigger request concurrently and get it accepted more than once, similar in root cause to the VUSD `processWithdrawals` bug: state that is meant to prevent re-processing of an already-consumed item is updated too late/non-atomically, so a single-use token/request can be "used" multiple times before the guard has a chance to mark it consumed.

### Finding Description
`Authorize` performs the JWT-replay check and the "mark used" write as two separate, non-atomic critical sections: [1](#0-0) 

Specifically:
1. `h.jwtCache.isReplay(claims.ID)` takes an `RLock`, checks presence in the map, and releases the lock. [2](#0-1) 
2. Only after further authorization checks succeed does the code call `h.jwtCache.recordUsage(claims.ID)`, which takes a separate `Lock` and writes the entry. [3](#0-2) 

Because `isReplay` and `recordUsage` are two independent lock acquisitions rather than a single atomic "check-and-set" operation, two (or more) concurrent `Authorize` calls carrying the exact same JWT (same `jti`) can both pass the `isReplay` check before either one calls `recordUsage`. This is the same class of bug as the VUSD report: an array/cache meant to prevent reprocessing of an already-consumed entry is not updated atomically with the check, so the guard can be bypassed by issuing the request multiple times (here, concurrently) before the "already used" marker is committed.

This differs from the `RequestReplayGuard` used by the Vault capability, which correctly implements `CheckAndRecord` as a single locked operation: [4](#0-3) 
The HTTP-trigger `jwtReplayCache` does not follow this safer pattern.

### Impact Explanation
`Authorize` gates `WorkflowMetadataHandler`'s HTTP trigger path, which is reachable directly from unprivileged external clients hitting the gateway's HTTP trigger endpoint (`MethodWorkflowExecute`), and its explicit purpose is single-use replay protection: "JWT token has already been used. Please generate a new one with new id (jti)" (as reflected in the test `TestWorkflowMetadataHandler_Authorize`/"JWT replay protection" and `TestHttpTriggerHandler_HandleUserTriggerRequest`/"duplicate JWT token and request ID"). A successful race bypass means the same signed workflow-execute request can be dispatched to the DON more than once, i.e., an unauthorized duplicate workflow run/job trigger, which is one of the accepted impact categories ("unauthorized job run"). Impact is bounded by how expensive/consequential a single workflow execution is (compute cost, side effects like on-chain writes, external calls), but the confused "single-use" guarantee is broken.

### Likelihood Explanation
Exploitation requires only sending the same valid, signed JWT-bearing request to the gateway's HTTP trigger endpoint concurrently (e.g., two near-simultaneous HTTP calls), something any external, unprivileged caller who has already obtained one valid single-use token can do without needing new secrets — this is a lock-window race, so likelihood depends on network/timing conditions but is not privileged or exotic. No special access beyond a legitimately-issued JWT is required.

### Recommendation
Make the replay check-and-record atomic, matching the pattern used in `RequestReplayGuard.CheckAndRecord`: acquire a single write lock, check for existing `jti`, and if absent, insert immediately in the same critical section, returning "already used" otherwise. E.g.:
```go
func (cache *jwtReplayCache) checkAndRecord(jti string) bool {
    cache.mu.Lock()
    defer cache.mu.Unlock()
    if _, exists := cache.cache[jti]; exists {
        return false
    }
    cache.cache[jti] = time.Now()
    return true
}
```
and call this single atomic method from `Authorize` instead of the separate `isReplay`/`recordUsage` calls, ideally performing the record immediately after JWT signature verification succeeds (or otherwise ensure no other concurrent authorization branch can slip through before the record is committed).

### Proof of Concept
1. Obtain one valid signed JWT (`jti = X`) for a `MethodWorkflowExecute` request to a given `workflowID`.
2. Fire two (or more) concurrent HTTP requests to the gateway's HTTP trigger endpoint with the identical token/request.
3. Both goroutines call `Authorize`; both execute `h.jwtCache.isReplay(claims.ID)` and find it `false` before either has called `recordUsage`, because the two operations are separate lock sections rather than one atomic check-and-set (`core/services/gateway/handlers/capabilities/v2/workflow_metadata_handler.go:87-105`).
4. Both requests pass authorization and both trigger the workflow execution via the DON, violating the intended single-use guarantee that is asserted by the existing sequential test (`TestHttpTriggerHandler_HandleUserTriggerRequest`/"duplicate JWT token and request ID").

Note: I was unable to fully inspect `http_trigger_handler.go`'s exact call site around `.Authorize(` due to tool/iteration limits, so the precise downstream fan-out to DON nodes per duplicated request is inferred from the handler's stated purpose and test names rather than directly confirmed line-by-line.

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
