### Title
JWT single-use replay protection has a check-then-act race allowing duplicate workflow trigger execution - (File: core/services/gateway/handlers/capabilities/v2/workflow_metadata_handler.go)

### Summary
The HTTP Trigger gateway handler enforces "use once" JWTs by checking a `jwtReplayCache` before authorizing a workflow-trigger request and only marking the JWT as used *after* authorization succeeds. The check (`isReplay`) and the state update (`recordUsage`) are two separate, non-atomic operations. Two concurrent requests carrying the identical signed JWT can both pass the `isReplay` check before either calls `recordUsage`, defeating the intended single-use guarantee — the same conceptual flaw as the Boba report: a state hash/flag meant to prevent re-processing of an already-consumed message is updated too late (or not atomically), letting the same signed request be processed more than once.

### Finding Description
`WorkflowMetadataHandler.Authorize` is the unprivileged-facing authorization entry point for HTTP-triggered workflow executions: [1](#0-0) 

The sequence is:
1. `VerifyRequestJWT` cryptographically verifies the token and digest.
2. `h.jwtCache.isReplay(claims.ID)` takes an `RLock`, checks the map, and releases the lock.
3. Authorized-key lookup happens.
4. `h.jwtCache.recordUsage(claims.ID)` takes a separate `Lock` and finally marks the `jti` as used.

The cache primitives themselves are trivially thread-safe individually, but the *check* and *record* are not combined into one atomic critical section: [2](#0-1) 

If two requests bearing the exact same signed JWT (same `jti`) arrive concurrently — e.g., the client retries a request whose response was lost, or an attacker/proxy duplicates the request — both goroutines can call `isReplay` and get `false` before either calls `recordUsage`. Both then pass authorization and are dispatched via `HandleUserTriggerRequest` → `sendWithRetries` to the DON, causing the workflow to be executed (or attempted) twice from a single signed authorization. [3](#0-2) 

This mirrors the reorg bug class from the report: a protective anti-replay mechanism exists (`_updateDepositHash()` / `jwtReplayCache`), but the code path that consumes/authorizes the message does not atomically couple the check with the state update, allowing the same authorization artifact to be used more than once.

### Impact Explanation
A duplicated JWT allows an unprivileged actor to cause an unauthorized/duplicate job run (workflow trigger execution) from a single valid signed authorization, which the JWT `jti`-based mechanism was explicitly designed to prevent ("Please generate a new one with new id (jti)"). Depending on what the workflow does downstream (side effects, external calls, on-chain actions triggered by the workflow), this can result in duplicated actions/fund movement being initiated twice from what should be a one-time authorization.

### Likelihood Explanation
Exploitation only requires sending the same previously-signed, unexpired JWT twice in close succession (a trivial replay by the legitimate caller or a network intermediary/attacker who captured the request) so that the two `Authorize` calls interleave before `recordUsage` is invoked. No cryptographic bypass is needed — the race window is realistic given normal request concurrency and retry behavior.

### Recommendation
Make the check-and-record operation atomic: hold a single write lock (or use a `sync.Map`/`LoadOrStore`-style compare-and-swap) covering both the "is this jti seen" check and marking it used, so that only one of two concurrent requests with the same `jti` can proceed. For example, replace `isReplay` + `recordUsage` with a single `checkAndRecord(jti) bool` method that atomically inserts the key and returns whether it was already present.

### Proof of Concept
1. Client creates and signs one valid `HTTPTriggerRequest` JWT (`jti = X`) via `CreateRequestJWT`/`VerifyRequestJWT` flow.
2. Client (or an attacker who intercepted the request) fires two concurrent `HandleUserTriggerRequest` calls with the identical JWT.
3. Both goroutines enter `WorkflowMetadataHandler.Authorize`, both call `h.jwtCache.isReplay(X)` before either calls `h.jwtCache.recordUsage(X)`.
4. Both return a valid `*AuthorizedKey`, and both requests are forwarded to the DON via `sendWithRetries`, resulting in two executions triggered by one single-use JWT — violating the documented and tested "already used" rejection in `TestWorkflowMetadataHandler_Authorize`.

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

**File:** core/services/gateway/handlers/capabilities/v2/http_trigger_handler.go (L95-109)
```go
func (h *httpTriggerHandler) HandleUserTriggerRequest(ctx context.Context, req *jsonrpc.Request[json.RawMessage], callback handlers.Callback, requestStartTime time.Time) error {
	triggerReq, err := h.validatedTriggerRequest(ctx, req, callback)
	if err != nil {
		return err
	}

	workflowID, err := h.resolveWorkflowID(ctx, triggerReq, req.ID, callback)
	if err != nil {
		return err
	}

	key, err := h.authorizeRequest(ctx, workflowID, req, callback)
	if err != nil {
		return err
	}
```
