Audit Report

## Title
JWT replay-cache check-then-act race lets a request bypass replay protection - (File: core/services/gateway/handlers/capabilities/v2/workflow_metadata_handler.go)

## Summary
`WorkflowMetadataHandler.Authorize` checks a JWT's `jti` for replay via `jwtCache.isReplay()` and only later marks it used via `jwtCache.recordUsage()`, with unrelated authorization work executed in between. These are two independent lock acquisitions rather than one atomic check-and-set, so two concurrent requests bearing the identical valid JWT can both observe "not replayed" before either records usage.

## Finding Description
`jwtReplayCache` guards its `cache map[string]time.Time` with a `sync.RWMutex`, but exposes `isReplay` (RLock, read-only) and `recordUsage` (Lock, write-only) as two separate methods rather than a single atomic operation: [1](#0-0) 

`Authorize` calls these as two temporally separated steps, with the authorized-key lookup for the workflow interleaved in between: [2](#0-1) 

Because `isReplay` and `recordUsage` do not share a single critical section, concurrent calls to `Authorize` with the same `jti` can both pass the `isReplay` check before either calls `recordUsage`, allowing the same single-use JWT to authorize more than one request. This is directly analogous to the vault package's `RequestReplayGuard.CheckAndRecord`, which correctly performs the check-and-insert under one `mu.Lock()` critical section: [3](#0-2)  The `jwtReplayCache` used in `WorkflowMetadataHandler` has no equivalent atomic primitive, confirming the claimed root cause.

I was unable to fully verify, within the available tool budget, whether `Authorize` is actually invoked concurrently for identical JWTs on the production HTTP-trigger request path (i.e., whether `http_trigger_handler.go`'s request handling permits two simultaneous in-flight calls to `Authorize` for the same token before serializing on some other lock). The existing test `TestHttpTriggerHandler_HandleUserTriggerRequest/duplicate JWT token and request ID` only demonstrates sequential replay rejection, not a concurrent race, which is consistent with the claim's own admission that this exact race has not been reproduced with a runnable PoC.

## Impact Explanation
If exploitable as described, a JWT intended to authorize a single workflow-trigger invocation could authorize two invocations under concurrent submission, resulting in duplicate/unintended workflow executions attributable to one authorized signer — a bypass of the single-use guarantee on the gateway's internet-facing HTTP trigger authorization path. This maps to the in-scope "gateway request impersonation / unauthorized job run" impact category, assuming the race window is actually reachable in the live request path.

## Likelihood Explanation
The vulnerable primitive (non-atomic `isReplay`/`recordUsage`) is real and confirmed in code. However, exploitability depends on the request path actually allowing two goroutines to execute `Authorize` concurrently for the same `jti` without additional serialization (e.g., a per-workflow or per-connection lock elsewhere in the gateway/DON dispatch pipeline) — this could not be confirmed from the available code inspection. No PoC (unit test or reproducible HTTP sequence) was constructed or verified to demonstrate the race actually manifesting; the report itself states this could not be completed.

## Recommendation
Add an atomic `CheckAndRecord`-style method to `jwtReplayCache` (mirroring `RequestReplayGuard.CheckAndRecord` in `core/capabilities/vault/request_replay_guard.go`) that holds a single write lock across the "check membership, then insert" sequence, and have `Authorize` call this single atomic method instead of separate `isReplay`/`recordUsage` calls.

## Proof of Concept
Not verified. A concrete Go test would need to spin up two goroutines calling `WorkflowMetadataHandler.Authorize` concurrently with the same JWT/`jti` and assert that only one succeeds; this was not executed and the actual request-handling concurrency model of `http_trigger_handler.go` was not confirmed to permit this race in practice within the available investigation.

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
