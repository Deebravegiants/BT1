### Title
JWT Replay-Protection Check-Then-Act Race in `WorkflowMetadataHandler.Authorize` Allows Single-Use JWT Reuse - ([File: core/services/gateway/handlers/capabilities/v2/workflow_metadata_handler.go])

### Summary
`WorkflowMetadataHandler.Authorize`, which authenticates unprivileged HTTP-trigger requests reaching the internet-facing gateway, checks whether a JWT has already been used and only *afterwards* marks it as used. The check and the mutation are two separate, non-atomic critical sections (`isReplay` under `RLock`, `recordUsage` under `Lock`, invoked several lines apart), so concurrent requests carrying the same JWT `jti` can all pass the replay check before any of them records usage — exactly the same class of bug as the OpenQ report, where a value (`fundingTotals`) is snapshotted at one point (`closeCompetition`) while the underlying state it depends on (`refundDeposit`) can still be mutated afterward, letting an attacker exploit the gap between check and finalization.

### Finding Description
`Authorize` is called by the HTTP-trigger handler to authenticate a workflow-trigger request coming from an unprivileged external caller (a request that ultimately reaches `HandleJSONRPCUserMessage` / `triggerHandler.HandleUserTriggerRequest`). [1](#0-0) 

The replay-protection logic:
```
if h.jwtCache.isReplay(claims.ID) { ... return error }
...
h.jwtCache.recordUsage(claims.ID)
``` [2](#0-1) 

`isReplay` and `recordUsage` are implemented as two separate lock/unlock operations on `jwtReplayCache.cache`, with no single critical section spanning "check" and "mark used": [3](#0-2) 

Because the check (`isReplay`) and the write (`recordUsage`) are not atomic and are separated by additional map lookups (`h.authorizedKeys[workflowID]`) that involve no locking on `jwtCache`, multiple goroutines processing concurrent requests carrying the identical signed JWT can each observe `isReplay == false` before any of them calls `recordUsage`. This mirrors the root cause of the OpenQ bug: a security-relevant accounting/state value (whether a JWT has been "spent") is read-then-later-written, and an attacker who can race requests can make invalid state changes (multiple uses of what is intended to be a single-use JWT) slip through in the window between the check and the finalize.

### Impact Explanation
Successful exploitation lets an unprivileged client bypass the single-use replay guard on the HTTP Trigger authentication path and submit the same authenticated JWT (and therefore, the same signed authorization) more than once concurrently, causing duplicate workflow-trigger executions to be accepted by the gateway that should have been rejected as replays. This undermines the "unauthorized job run" guarantee the JWT replay cache is meant to provide on the internet-facing gateway.

### Likelihood Explanation
Exploitation requires only sending several concurrent HTTP requests carrying the same previously-valid JWT to the gateway's HTTP trigger endpoint — no privileged access, no node compromise, and no dependency-only conditions are needed. The race window is small but real (it spans a JWT signature verification, an authorized-key map lookup, and lock acquisition), and is reliably triggerable by firing a burst of parallel requests, which is a common technique for winning TOCTOU races.

### Recommendation
Make the "check-not-replayed" and "mark-as-used" operations atomic under a single lock in `jwtReplayCache`, e.g. add a `CheckAndRecord(jti string) bool` method that acquires `mu.Lock()` once, checks existence, and inserts the entry in the same critical section, replacing the separate `isReplay` + `recordUsage` calls in `Authorize`.

### Proof of Concept
1. Obtain (or forge with a leaked/legitimately issued) signed JWT for a workflow trigger request with `jti = X`.
2. Fire N concurrent HTTP requests to the gateway's HTTP trigger endpoint, all presenting the same JWT (`jti = X`).
3. Each goroutine handling a request calls `WorkflowMetadataHandler.Authorize`, which calls `h.jwtCache.isReplay(X)` — because `recordUsage(X)` has not yet completed for any of the concurrent calls, multiple goroutines observe `isReplay == false` and proceed to `h.jwtCache.recordUsage(X)`, each accepting the same JWT as valid and dispatching a duplicate workflow-trigger execution to the DON, defeating the intended single-use ("replay protection") semantics documented at `defaultJWTReplayPeriodMs`. [4](#0-3)

### Citations

**File:** core/services/gateway/handlers/capabilities/v2/workflow_metadata_handler.go (L80-107)
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

**File:** core/services/gateway/handlers/capabilities/v2/http_handler.go (L42-42)
```go
	defaultJWTReplayPeriodMs             = 1000 * 60 * 60 * 24 // 24 hours
```
