The code exactly matches the claim. The `Authorize` function performs signature verification, a replay check (`isReplay`), authorized-key validation, and only records the JWT ID as used (`recordUsage`) at the very end, with each cache operation acquiring the mutex independently rather than as one atomic check-and-set.

Audit Report

## Title
JWT replay-protection check-then-record TOCTOU allows double-authorization of HTTP trigger requests - (File: core/services/gateway/handlers/capabilities/v2/workflow_metadata_handler.go)

## Summary
`WorkflowMetadataHandler.Authorize` checks JWT replay status via `jwtCache.isReplay` and only marks the token as used via `jwtCache.recordUsage` after several intervening operations (authorized-key lookups), with no shared critical section between the two calls. Two concurrent requests carrying the same signed JWT can both pass the `isReplay` check before either calls `recordUsage`, allowing the same one-time-use JWT to authorize two (or more) concurrent workflow trigger requests.

## Finding Description
`Authorize` verifies the JWT, then calls `h.jwtCache.isReplay(claims.ID)` at line 87, and only calls `h.jwtCache.recordUsage(claims.ID)` at line 105, after unrelated work (workflow lookup, authorized-key map lookup) has executed in between. [1](#0-0) 

The cache's `isReplay` and `recordUsage` methods acquire the `sync.RWMutex` independently for each call rather than as a single atomic check-and-set operation: [2](#0-1) 

Because there is no shared lock spanning both the check and the record, and no other synchronization mechanism (such as a per-`jti` mutex or single atomic map-insert-if-absent primitive) wraps the whole `Authorize` flow, two goroutines invoking `Authorize` concurrently with the same JWT can both observe `isReplay` returning `false` before either executes `recordUsage`. Both then pass the authorized-key check and are granted authorization. This breaks the intended one-time-use security property of the `jti` replay cache.

## Impact Explanation
This is an authorization/replay-protection bypass on the gateway's HTTP trigger authorization path. A single valid signed JWT — normally intended to authorize exactly one triggered workflow execution — can be raced to authorize multiple concurrent executions. If the underlying workflow performs a job run or state-changing/on-chain action, this maps to the "unauthorized job run" impact category, since the same credential is used to unlock more than one authorized action.

## Likelihood Explanation
Exploitation requires only possession of one valid signed JWT (no elevated privilege) and the ability to send it concurrently over two or more connections — a request-racing technique readily available to any network-capable client. The race window depends on timing between the `isReplay` check and workflow-lookup/authorized-key-check work, which is realistic to hit reliably with basic concurrent request tooling, though not guaranteed on every attempt.

## Recommendation
Make the check-and-mark operation atomic: acquire the `jwtReplayCache` mutex once and perform both the existence check and the insertion under the same critical section (e.g., a single `checkAndRecord(jti string) bool` method using `Lock()`/`Unlock()` that returns whether the token was already used and inserts it if not), and call this from `Authorize` in place of the separate `isReplay`/`recordUsage` calls.

## Proof of Concept
1. Obtain one valid signed HTTP-trigger JWT (with a given `jti`) for a workflow.
2. Fire two concurrent HTTP trigger requests to the gateway carrying the identical JWT/token.
3. Both goroutines call `WorkflowMetadataHandler.Authorize`; both call `h.jwtCache.isReplay(claims.ID)` before either calls `h.jwtCache.recordUsage(claims.ID)`, so both return `false`.
4. Both requests pass the authorized-key check and are granted authorization, triggering the workflow twice from a single issued token — this can be demonstrated with a Go unit test that spawns two goroutines calling `Authorize` with the same JWT and asserts both return no error.

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
