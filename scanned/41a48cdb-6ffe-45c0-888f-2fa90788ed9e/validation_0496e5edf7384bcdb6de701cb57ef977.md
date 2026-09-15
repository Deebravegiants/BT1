### Title
JWT replay-guard TOCTOU race lets an unprivileged HTTP-trigger caller replay a token and duplicate a workflow execution - (File: core/services/gateway/handlers/capabilities/v2/workflow_metadata_handler.go)

### Summary
The external report's underlying bug class is a checks-effects-interactions violation: a security-relevant state flag (`fundsTransfered[user]`) is written *after* the risky operation instead of before, opening a window for reentrant/duplicate execution. The closest analog reachable from an unprivileged client in this codebase is the JWT replay guard used to authorize HTTP Trigger requests to workflows through the gateway.

### Finding Description
`WorkflowMetadataHandler.Authorize` is the method that authenticates an inbound HTTP trigger request's JWT before dispatching it to the workflow DON, called from the unprivileged, internet-facing path `HandleUserTriggerRequest` → `authorizeRequest` → `Authorize`: [1](#0-0) 

The replay check and the recording of "this JWT ID has been used" are two separate, independently-locked operations rather than one atomic check-and-set: [2](#0-1) 

```go
if h.jwtCache.isReplay(claims.ID) {   // takes RLock, releases it
    ...
    return nil, errors.New(...)
}
...
h.jwtCache.recordUsage(claims.ID)    // takes Lock, releases it — only now is it marked "used"
```

`isReplay` and `recordUsage` are implemented with independent mutex acquisitions: [3](#0-2) 

There is a window between the `isReplay` check and the `recordUsage` write during which a second, concurrent request bearing the *same* signed JWT (same `jti`) can also observe `isReplay == false` and pass authorization, because nothing marks the token "seen" until after the check completes. This is structurally the same class of bug as the reported `sendFunds` issue: the state that is supposed to prevent duplicate/unauthorized use is committed too late relative to the operation it's meant to gate.

By contrast, the codebase's own Vault-capability replay guard demonstrates the correct pattern — check and record happen atomically under a single lock: [4](#0-3) 

The HTTP-trigger `jwtReplayCache` does not follow this pattern.

### Impact Explanation
An unprivileged external caller who can send two copies of the same signed JWT-backed trigger request concurrently (e.g., a client retry that races on the network, or a deliberate duplicate submission) can cause the workflow trigger to be authorized and dispatched to the DON more than once for what is supposed to be a single-use token. Depending on the workflow's side effects, this can result in duplicate workflow executions from a single authorization — analogous to draining/duplicating an action that should only be permitted once. This is a real integrity issue in the replay-protection guarantee documented in the JWT format ("jti... REQUIRED... for replay protection"), though the impact is bounded to duplicate authorization/execution rather than direct fund loss, since actual node-level fulfillment still goes through further DON-side processing.

### Likelihood Explanation
Exploitation only requires an attacker (or a client experiencing normal retry behavior) to send the same already-signed JWT twice in close succession — no privileged access, no valid token forgery, and no other systems need to cooperate. The race window is small (two lock acquisitions), but is real; a client can also intentionally fire concurrent duplicate requests to maximize the chance of winning the race. This is a genuine, if narrow, timing-dependent bypass rather than a guaranteed one, so likelihood is moderate.

### Recommendation
- Short term: Merge `isReplay` and `recordUsage` into a single atomic check-and-record method under one lock (mirroring `vault.RequestReplayGuard.CheckAndRecord`), so a JWT ID is recorded as used in the same critical section that checks it.
- Long term: Apply the checks-effects-interactions discipline consistently across all gateway replay/authorization caches: record any consumption-marking state before dispatching the associated privileged operation (forwarding the trigger to the DON), not after.

### Proof of Concept
Conceptually (not executed, network calls not available in this environment):
1. Obtain a validly signed workflow-trigger JWT with a fixed `jti` for a target workflow.
2. Fire two HTTP requests to the gateway's HTTP-trigger endpoint carrying the identical JWT at effectively the same time (e.g., two goroutines/connections).
3. Both requests can reach `WorkflowMetadataHandler.Authorize` and call `isReplay(claims.ID)` before either has called `recordUsage(claims.ID)`, so both may pass authorization and both get dispatched via `sendWithRetries`, causing duplicate execution of the workflow trigger from a single, meant-to-be-single-use JWT.

Note: I could not execute this against a live gateway instance in this environment; the race is inferred directly from the non-atomic check/record implementation shown above, and confirming the exact exploitability window (timing tolerance) would require a running test harness, which a Devin session with full repo/test execution access could verify.

### Citations

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
