## Analog Found: JWT Replay Check-Then-Record Race in `WorkflowMetadataHandler.Authorize`

### Title
JWT Replay Protection Bypass via Check-Then-Record Race (TOCTOU) - (File: core/services/gateway/handlers/capabilities/v2/workflow_metadata_handler.go)

### Summary
The Sherlock report's core issue is a non-atomic "lock" pattern: a state check (`lastAccrualTime != 0`) is performed, followed by unrelated work, followed by the state update (`lastAccrualTime = 0`) — leaving a window where the check can be satisfied more than once for what should be a single-use guard. The Chainlink analog is `WorkflowMetadataHandler.Authorize`, which checks JWT replay status and records JWT usage as two separate, non-atomic critical sections, with authorization logic executed in between.

### Finding Description
`Authorize` is reachable from any unprivileged HTTP Trigger client via `HandleJSONRPCUserMessage` → `HandleUserTriggerRequest`. It performs replay protection like this: [1](#0-0) 

The check `h.jwtCache.isReplay(claims.ID)` acquires an `RLock`, reads, and releases: [2](#0-1) 

The corresponding "lock" write, `h.jwtCache.recordUsage(claims.ID)`, happens in a *separate* critical section, only after the workflow-ID lookup and signer-authorization checks complete: [3](#0-2) 

Because `isReplay` and `recordUsage` are not combined into a single atomic check-and-set (unlike, e.g., a `LoadOrStore`), two (or more) concurrent requests carrying the identical signed JWT can both pass the `isReplay` check before either calls `recordUsage`. This is structurally the same flaw as the reported Aloe bug: the "already used" state is only checked at entry and only written at the very end, with meaningful work occurring in between, so parallel invocations race through the guard.

### Impact Explanation
An unprivileged client that captures or is issued one valid signed JWT for a workflow trigger request can replay it concurrently to bypass the intended one-time-use replay protection, causing the same signed authorization to be accepted multiple times and multiple workflow trigger executions to be dispatched to the DON from a single token, defeating the anti-replay guarantee documented for `JWTReplayPeriodMs`.

### Likelihood Explanation
This requires only network-level concurrency (firing the same HTTP trigger request twice at (near) the same time) from an external, unprivileged caller — no special privileges, node compromise, or malicious peer assumption needed. This makes it a straightforward, unprivileged-actor-reachable race.

### Recommendation
Replace the separate `isReplay` + `recordUsage` steps with a single atomic check-and-set operation (e.g., hold the cache's write lock for the whole "check ID, and if absent, mark used" sequence, or use a `sync.Map`/similar atomic `LoadOrStore`), so that a JTI can never pass the replay check twice concurrently.

### Proof of Concept
1. Obtain one valid signed request JWT (`jti = X`) for `MethodWorkflowExecute`.
2. Fire two (or more) concurrent `HandleJSONRPCUserMessage` calls carrying the same JWT.
3. Both goroutines call `h.jwtCache.isReplay(X)` before either calls `h.jwtCache.recordUsage(X)`, so both pass the replay check (as demonstrated architecturally by the separated `isReplay`/`recordUsage` critical sections at workflow_metadata_handler.go lines 87 and 105), resulting in two accepted authorizations from a single token instead of one.

### Citations

**File:** core/services/gateway/handlers/capabilities/v2/workflow_metadata_handler.go (L87-105)
```go
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
