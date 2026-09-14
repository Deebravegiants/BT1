### Title
JWT Replay-Protection Race Condition Allows Reuse of a Single-Use Workflow-Trigger Token - ([File: core/services/gateway/handlers/capabilities/v2/workflow_metadata_handler.go])

### Summary
The `jwtReplayCache` used to enforce single-use semantics on JWTs presented to HTTP-trigger workflow execution requests performs its "already used" check and its "mark as used" write as two separate, non-atomic locked operations. A caller who sends the same signed JWT concurrently (multiple simultaneous requests) can pass the `isReplay` check on more than one goroutine before either one calls `recordUsage`, allowing the single-use token to authorize more than one workflow execution.

### Finding Description
`WorkflowMetadataHandler.Authorize` verifies the JWT, then calls `h.jwtCache.isReplay(claims.ID)` to reject already-used tokens, performs the authorized-key lookup, and only at the very end calls `h.jwtCache.recordUsage(claims.ID)`: [1](#0-0) 

The cache itself implements the read and the write as two independently-locked critical sections rather than a single atomic check-and-set: [2](#0-1) 

`isReplay` takes an `RLock`, reads, and releases; `recordUsage` is only invoked after JWT verification, workflow lookup, and authorized-key matching complete in `Authorize`. There is a window between the `isReplay` check and the `recordUsage` write during which a second, concurrent call to `Authorize` with the identical JWT (`jti`) will also observe `isReplay == false` and proceed to be authorized. This is the same class of bug as the reported `TrufVesting.claimable()` issue: a value/credential that is supposed to be single-use is checked against stale state instead of atomically updated, so repeated/concurrent invocations before the state update lands can all succeed.

`Authorize` is invoked directly from the HTTP trigger handler's `authorizeRequest`, which is on the path reachable by any unprivileged client sending workflow-execute requests to the gateway: [3](#0-2) 

### Impact Explanation
A single valid signed JWT—intended by design to authorize exactly one workflow execution request (as explicitly tested and documented, "token has already been used")—can be replayed to trigger multiple executions of the same paid/rate-limited workflow if the attacker (or a buggy/duplicating client) sends the same signed request in parallel. This breaks the single-use/anti-replay guarantee that downstream logic (billing, rate limiting assumptions, deduplication) relies on, enabling unauthorized duplicate job/workflow runs from a single credential grant.

### Likelihood Explanation
Exploitation requires only the ability to send the same signed JWT-bearing HTTP trigger request twice in close succession (e.g., via two parallel HTTP connections), which is trivial for any external, unprivileged caller who already possesses one valid signed token — no special access or node compromise needed. The race window is real but narrow (JWT verification + workflow lookup time), so reliability depends on request timing, making this a race-based rather than deterministic bypass.

### Recommendation
Make the check-and-record operation atomic: acquire a single lock for the entire "check `jti`, then mark it used" sequence in `jwtReplayCache`, e.g. add a combined `CheckAndRecord(jti string) bool` method (mirroring the pattern already used correctly in `RequestReplayGuard.CheckAndRecord` in `core/capabilities/vault/request_replay_guard.go`) that holds the write lock across both the existence check and the insertion, and have `Authorize` call it once instead of separate `isReplay`/`recordUsage` calls.

### Proof of Concept
1. Register a workflow and obtain one authorized signer key, as in `TestWorkflowMetadataHandler_Authorize`.
2. Create a single JWT for a `HTTPTriggerRequest`/`MethodWorkflowExecute` request signed by the authorized key (as done via `utils.CreateRequestJWT` / `createTestJWTToken`).
3. From two goroutines, concurrently call `handler.Authorize(workflowID, tokenString, req)` (or send the equivalent HTTP trigger requests concurrently through `httpTriggerHandler.HandleUserTriggerRequest`) with the identical token.
4. Under the current implementation, both goroutines can observe `isReplay(claims.ID) == false` before either calls `recordUsage`, so both return a valid `*gateway.AuthorizedKey` and both requests proceed to trigger workflow execution — demonstrating that the single-use JWT was consumed twice.

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
