### Title
JWT replay protection in `WorkflowMetadataHandler.Authorize()` has a check-then-act race allowing single-use JWT reuse - (File: `core/services/gateway/handlers/capabilities/v2/workflow_metadata_handler.go`)

### Summary
The Sherlock report describes `SingleSidedLiquidityVault.claimRewards()` reading/using accounting state (accumulated rewards) without atomically updating the internal state that governs future accounting, letting a user extract more than their share. The equivalent bug class here is "check state → act → update state" performed as non-atomic, separately-locked steps rather than a single atomic operation. In chainlink's gateway HTTP-Trigger auth path, `WorkflowMetadataHandler.Authorize()` implements JWT replay protection with exactly this pattern: it checks `isReplay(jti)` and only records the JWT as used (`recordUsage(jti)`) at the very end of the function, with unrelated map lookups and no locking in between, and using two independently-locked cache operations instead of one atomic check-and-set.

### Finding Description
`Authorize()` in `workflow_metadata_handler.go` performs: [1](#0-0) 

1. `h.jwtCache.isReplay(claims.ID)` — acquires `jwtReplayCache.mu` as an `RLock`, checks membership, and releases the lock. [2](#0-1) 
2. Unrelated authorization checks (`h.authorizedKeys[workflowID]`, signer key membership) run without holding the `jwtCache` lock.
3. Only after all checks pass does it call `h.jwtCache.recordUsage(claims.ID)`, which acquires a *separate* `Lock()` on the same map. [3](#0-2) 

Because the "check" and the "record" are two independent, non-atomic critical sections, two (or more) concurrent `Authorize()` calls carrying the *same* JWT (same `jti`) can both pass `isReplay()` before either has called `recordUsage()`. Both calls will then proceed as authorized, defeating the single-use JWT/replay-protection contract that the cache is explicitly designed to enforce (per its doc comment: "jwtReplayCache manages used JWT IDs to prevent replay attacks").

This is reachable directly by an unprivileged client: `Authorize()` is invoked from `httpTriggerHandler.authorizeRequest()`, which is called on every inbound HTTP-Trigger request forwarded from the internet-facing Gateway before dispatching a workflow execution to nodes. [4](#0-3) 

### Impact Explanation
An external, unauthenticated-by-session (only JWT-bearing) client can send the same signed JWT-authenticated trigger request twice concurrently (e.g., duplicate the same HTTP POST in parallel) and have both instances pass the "already used" replay guard, causing the same one-time-intended token to authorize two workflow executions/job runs instead of one. This is a request-impersonation/replay-bypass analogous to the reward-double-counting bug class: state meant to gate a one-time action is read and acted upon before it is durably updated, letting an unprivileged actor trigger an extra, unauthorized action (duplicate workflow run) that the design intended to prevent exactly once per token.

### Likelihood Explanation
Likelihood is moderate: it requires the attacker (or a legitimate but malicious/misbehaving client) to fire the same signed request twice in a very tight time window to win the race between two `Authorize()` invocations on different goroutines. This is trivially achievable by any external caller who controls when/how many times they submit an HTTP trigger request with the same JWT (e.g., via simple concurrent HTTP calls), and does not require any privileged access — only a single valid JWT.

### Recommendation
Merge the check-and-record into a single atomic operation under one lock (e.g., a `CheckAndRecord`-style method similar to `RequestReplayGuard.CheckAndRecord` used elsewhere in the vault package, which correctly performs the check and insertion under a single `mu.Lock()`): [5](#0-4) 

Concretely, refactor `jwtReplayCache` to expose a single `CheckAndRecord(jti string) bool` (or error) method that takes the write lock once, checks for existence, and inserts the entry before releasing the lock, and update `Authorize()` to call it instead of the separate `isReplay`/`recordUsage` pair.

### Proof of Concept
1. Obtain (or intercept) one valid, unexpired, correctly-signed JWT for an HTTP Trigger request with a given `jti`.
2. Fire two (or more) concurrent HTTP requests to the Gateway's HTTP Trigger endpoint using the identical JWT/request body at nearly the same time.
3. Both requests reach `httpTriggerHandler.authorizeRequest()` → `WorkflowMetadataHandler.Authorize()` concurrently.
4. Both goroutines call `h.jwtCache.isReplay(claims.ID)` before either calls `h.jwtCache.recordUsage(claims.ID)`, since these are separate, non-atomic lock sections; both observe "not replayed" and proceed.
5. Both requests pass authorization and go on to trigger workflow execution, i.e., the single-use JWT was consumed twice — confirming the replay-protection bypass. (This was verified statically from the exact non-atomic check/record structure in `Authorize()`; a live concurrency test to definitively trigger the race window under the actual mutex scheduling was not executed as part of this analysis and would need to be confirmed with a targeted race-condition test.)

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

**File:** core/services/gateway/handlers/capabilities/v2/http_trigger_handler.go (L368-376)
```go
func (h *httpTriggerHandler) authorizeRequest(ctx context.Context, workflowID string, req *jsonrpc.Request[json.RawMessage], callback handlers.Callback) (*gateway_common.AuthorizedKey, error) {
	h.lggr.Debugw("authorizing request", "workflowID", workflowID, "requestID", req.ID)
	key, err := h.workflowMetadataHandler.Authorize(workflowID, req.Auth, req)
	if err != nil {
		h.handleUserError(ctx, req.ID, jsonrpc.ErrInvalidRequest, "Auth failure: "+err.Error(), callback)
		return nil, errors.Join(errors.New("auth failure"), err)
	}
	return key, nil
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
