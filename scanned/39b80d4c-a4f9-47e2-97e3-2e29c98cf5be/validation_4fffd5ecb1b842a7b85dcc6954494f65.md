### Title
JWT replay-guard TOCTOU race in HTTP Trigger gateway allows duplicate workflow trigger execution - (File: core/services/gateway/handlers/capabilities/v2/workflow_metadata_handler.go)

### Summary
This is the closest chainlink analog to the reported "no time delay when replacing an active state" bug class: an unprivileged caller can exploit a check-then-act race window in the internet-facing HTTP Trigger gateway path to bypass single-use JWT enforcement, causing the same signed trigger request to be accepted more than once before it is recorded as "seen."

### Finding Description
The HTTP Trigger V2 gateway handler authenticates inbound trigger requests using per-request JWTs, and relies on `jwtReplayCache` to reject reuse of the same JWT ID (`jti`). The `Authorize` method performs the replay check and the "record as used" step as two separate, non-atomic critical sections: [1](#0-0) 

Specifically, `isReplay` takes a read lock, checks map membership, and releases the lock; only afterward — after also validating claims and authorized keys — does `recordUsage` take a write lock and insert the `jti`: [2](#0-1) 

Because `isReplay` (read) and `recordUsage` (write) are separate lock acquisitions rather than one atomic "check-and-record" operation, two (or more) concurrent `HandleUserTriggerRequest` calls carrying the identical JWT can both pass `isReplay` before either calls `recordUsage`. This mirrors the report's root cause exactly: the code lacks a delay/atomicity guarantee between the moment a state is "checked" and the moment it is durably updated, so a state actor (an unprivileged external caller) sending near-simultaneous duplicate requests can slip through a race window that the single-use design intends to prevent.

Notably, this same package contains a correctly-implemented atomic version of this exact pattern in the Vault capability's `RequestReplayGuard.CheckAndRecord`, which performs the lookup and insert under one mutex acquisition: [3](#0-2) 

That design is explicitly validated for concurrency safety in `TestRequestReplayGuard_ConcurrentAccess`, which asserts exactly one goroutine wins under concurrent identical-digest calls. No equivalent concurrency test exists for `jwtReplayCache`, and the code path structurally cannot provide the same guarantee since `isReplay`/`recordUsage` are decoupled.

The path is reachable directly from an unauthenticated/unprivileged network caller: `HandleUserTriggerRequest` → `authorizeRequest` → `WorkflowMetadataHandler.Authorize`, on every inbound HTTP trigger request to the gateway. [4](#0-3) 

### Impact Explanation
An attacker (or any client with a single valid signed JWT for one workflow trigger) can fire the same request concurrently to exploit the race window and get the trigger dispatched to the DON more than once for what should be a single-use authorization token. Depending on the downstream workflow, this can cause duplicate/unauthorized workflow executions, double side effects (e.g., duplicate on-chain actions, duplicate billing/rate-limit bypass), undermining the intended "exactly once" guarantee the replay cache exists to enforce. This is a concrete authentication/replay-protection bypass reachable by an unprivileged external actor, matching the "unauthorized job run" impact category.

### Likelihood Explanation
Exploitation only requires an attacker who already possesses one valid JWT for a trigger (the same precondition needed to trigger the workflow once at all) and the ability to send that same JWT twice in quick succession/concurrently — trivially achievable over HTTP. The race window is small (map lock hold time), but it is real and requires no special network position, no privilege escalation, and no cooperation from the node operator — purely client-side timing, analogous to the front-running/racing scenario in the original report.

### Recommendation
Make the replay check and record atomic, exactly like `vault.RequestReplayGuard.CheckAndRecord`: combine `isReplay` and `recordUsage` into a single critical section guarded by one lock (e.g., a `CheckAndRecord(jti)` method returning an error if already present, otherwise inserting), and call it once from `Authorize` before/instead of the separate `isReplay`/`recordUsage` calls. Add a concurrency test analogous to `TestRequestReplayGuard_ConcurrentAccess` to assert that only one of N concurrent identical-JWT requests succeeds.

### Proof of Concept
1. Obtain a single valid JWT for an HTTP Trigger workflow request (`jti = X`).
2. Send two (or more) copies of the same signed request concurrently to the gateway's HTTP Trigger endpoint.
3. Both goroutines/requests independently call `WorkflowMetadataHandler.Authorize`, each calling `h.jwtCache.isReplay(claims.ID)` before either has called `h.jwtCache.recordUsage(claims.ID)`.
4. Because the check and the record are not under the same lock, both requests observe `isReplay == false` and both proceed to authorize and dispatch the trigger to the DON, resulting in two workflow executions from a single-use JWT — the analog of `activateProposal()`/`vote()` racing on a shared, non-atomically-guarded state transition in the original report. [1](#0-0)

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
