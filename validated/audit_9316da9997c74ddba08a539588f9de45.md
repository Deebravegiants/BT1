### Title
JWT replay-protection check-then-act race allows single-use HTTP trigger tokens to be reused for concurrent requests - ([File: core/services/gateway/handlers/capabilities/v2/workflow_metadata_handler.go])

### Summary
The reported zkSync bug is a class of "check-uses-stale/mutated-state" flaw: a validation gate reads shared state, but the state that backs the decision is not updated atomically with the check, so a second concurrent operation can pass a check that should have failed. The `jwtReplayCache` used to enforce single-use JWTs on the gateway's HTTP-trigger authorization path has the same structural flaw: `isReplay` and `recordUsage` are two separate, non-atomic locked operations, so two concurrent requests carrying the identical externally-supplied JWT can both observe "not yet used" before either records usage.

### Finding Description
`WorkflowMetadataHandler.Authorize` is the entry point that authorizes an unprivileged, externally-supplied HTTP-trigger request signed with a workflow-owner JWT: [1](#0-0) 

The flow is:
1. `h.jwtCache.isReplay(claims.ID)` — takes an `RLock`, checks the map, releases the lock.
2. Signer/authorized-key checks.
3. `h.jwtCache.recordUsage(claims.ID)` — takes a separate `Lock`, writes the map, releases the lock.

`isReplay` and `recordUsage` are implemented as independent critical sections: [2](#0-1) 

Because the "check" and the "mark as used" happen in two separate lock acquisitions with unrelated business logic executed in between, there is a window in which the jti has not yet been recorded. Two (or more) requests presenting the exact same JWT `jti` concurrently can both pass `isReplay` and both proceed to `recordUsage` — effectively defeating the single-use replay guard the design explicitly documents ("prevents replay of already-processed requests"). This mirrors the zkSync root cause: the enforcement decision is made against a base/state value that the concurrent execution path itself is about to (or has just) mutated, so the gate does not reflect the true up-to-date state at decision time.

### Impact Explanation
The JWT replay cache is the mechanism that guarantees a caller-issued, single-use trigger token can only invoke a workflow execution once. If the check-then-act race is exploitable, an external, unprivileged caller who possesses (or intercepts/observes) a single valid signed JWT can trigger the same workflow execution multiple times concurrently instead of once, i.e., an unauthorized/duplicate job run bypassing the intended one-shot authorization control. This is a quota/replay-bypass class issue rather than a full authentication bypass — the caller must still hold a validly signed JWT — but it defeats the specific anti-replay guarantee the code is designed to provide.

### Likelihood Explanation
Exploitability depends on being able to fire multiple requests with the identical JWT within the narrow window between `isReplay` and `recordUsage` (network round trips to the gateway, not local in-process latency, so the race window is realistically hittable by an attacker sending parallel requests). No privileged access is required — only possession of one valid signed JWT for the target workflow, which is a normal unprivileged-client artifact for HTTP-triggered workflows.

### Recommendation
Make the check-and-record operation atomic: acquire a single lock (or use an atomic "insert-if-absent" map operation) that performs the existence check and the insertion in one critical section, e.g. change `jwtReplayCache` to expose a single `CheckAndRecord(jti string) error`-style method (mirroring the pattern already used correctly elsewhere in the codebase, e.g. `RequestReplayGuard.CheckAndRecord` in `core/capabilities/vault/request_replay_guard.go`), and update `Authorize` to call this single atomic method instead of separate `isReplay`/`recordUsage` calls.

### Proof of Concept
1. Obtain one valid signed JWT (`jti = X`) authorized for a given workflow ID for the HTTP trigger method.
2. Fire two (or more) concurrent `HandleUserTriggerRequest`/gateway requests using the identical JWT.
3. Both goroutines call `Authorize`, each independently calling `h.jwtCache.isReplay(X)` before either has called `h.jwtCache.recordUsage(X)`.
4. Both calls to `isReplay` return `false` (not yet recorded), so both requests pass authorization and both trigger workflow execution — i.e., the single-use token executes the workflow more than once, even though the code explicitly intends "generate a new one with new id (jti)" per single use (see the error message at line 89 of `workflow_metadata_handler.go`).

Note: I was not able to fully trace every caller path of `Authorize`/`HandleUserTriggerRequest` due to the final-iteration constraint (the `http_trigger_handler.go` read did not return content), so the exact HTTP entry point details for the trigger request are based on the `Authorize` signature and its documented purpose rather than a fully-verified end-to-end trace; the vulnerable check-then-act pattern itself, however, is confirmed directly from the cited source.

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
