### Title
JWT Replay-Guard TOCTOU Allows Concurrent Reuse of a Single-Use JWT - ([File: core/services/gateway/handlers/capabilities/v2/workflow_metadata_handler.go])

### Summary
The `jwtReplayCache` used by `WorkflowMetadataHandler.Authorize` performs the replay check (`isReplay`) and the replay recording (`recordUsage`) as two separate, independently-locked operations with unrelated business logic executed in between. This is the same bug class as the reported `openTrove` issue: a value is read into a decision path, other work happens, and the "commit" of state occurs later without atomically incorporating concurrent updates — creating a window where the guard can be bypassed.

### Finding Description
`Authorize` is the JWT-based authentication entry point for HTTP Trigger requests arriving at the gateway from external, unprivileged callers [1](#0-0) . It calls `h.jwtCache.isReplay(claims.ID)` to check whether the JWT id (`jti`) was already used, then performs unrelated map lookups (`authorizedKeys`, signer match), and only afterwards calls `h.jwtCache.recordUsage(claims.ID)` to mark the `jti` as spent [2](#0-1) .

`isReplay` and `recordUsage` each take their own lock independently: [3](#0-2) 

Because the check-then-act is not atomic, two concurrent requests carrying the identical JWT (same `jti`) can both call `isReplay` before either calls `recordUsage`, both observing "not yet used," and both proceed to be authorized and dispatched to the DON. This mirrors the reported bug's root cause: a read of shared state is cached/decided upon, then overwritten/finalized later without accounting for interleaved state changes, defeating the intended invariant (in the original report, `totalActiveDebt` under-counts; here, the JWT replay-guard under-blocks).

### Impact Explanation
The JWT replay guard exists specifically to make each signed HTTP-trigger authorization single-use. A TOCTOU race lets an external, unprivileged caller replay a single valid JWT concurrently to trigger the same workflow execution multiple times before the token is recorded as used, undermining the anti-replay guarantee described in the JWT authentication documentation ("JWT-based authentication," "Duplicate Prevention" per `core/services/gateway/handlers/capabilities/v2/README.md`). This is a concrete authentication/anti-replay bypass reachable directly from unprivileged external HTTP trigger callers hitting the internet-facing gateway.

### Likelihood Explanation
Exploitation requires only sending the same signed request (or replaying a captured one) as two near-simultaneous requests to the gateway — no special privileges, no node compromise, and no reliance on multiple validators colluding. Given the gateway processes trigger requests concurrently per node/request, the race window (map read → key/signer checks → map write) is realistically hittable by an attacker firing duplicate requests in parallel.

### Recommendation
Make the check-and-record atomic: acquire a single write lock (or use a `sync.Map`/`LoadOrStore`-style primitive) that checks for existence of the `jti` and inserts it in one critical section, rejecting the request if it was already present, e.g.:
```go
func (cache *jwtReplayCache) checkAndRecord(jti string) bool {
    cache.mu.Lock()
    defer cache.mu.Unlock()
    if _, exists := cache.cache[jti]; exists {
        return false // replay
    }
    cache.cache[jti] = time.Now()
    return true
}
```
and call this single atomic operation from `Authorize` before performing further checks, instead of the separate `isReplay`/`recordUsage` calls.

### Proof of Concept
1. Obtain (or observe) one valid signed JWT for an HTTP trigger request (`jti = X`).
2. Fire two (or more) concurrent `HandleJSONRPCUserMessage` requests to the gateway carrying the identical JWT.
3. Both goroutines execute `Authorize`: both call `isReplay("X")` before either calls `recordUsage("X")`, since there is no shared lock spanning the whole check-then-record sequence [4](#0-3) .
4. Both requests pass authorization and are dispatched to trigger the workflow, i.e., the single-use JWT is consumed more than once — confirming the replay-guard bypass.

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
