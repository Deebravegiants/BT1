### Title
JWT replay-cache check-then-act race condition allows single-use token to authorize multiple concurrent requests - (File: core/services/gateway/handlers/capabilities/v2/workflow_metadata_handler.go)

### Summary
`WorkflowMetadataHandler.Authorize` is reachable from an unprivileged client via `HandleUserTriggerRequest` → `authorizeRequest` in the HTTP trigger gateway path [1](#0-0) . It is meant to enforce single-use JWTs by rejecting a `jti` that has already been recorded, but the "check" and the "commit" happen as two separate, non-atomic lock sections, mirroring the CVE-2021-23133 bug class where a list mutation happened without holding the lock that guards the whole invariant, opening a TOCTOU race window exploitable by an unprivileged caller.

### Finding Description
`Authorize` performs the replay check via `h.jwtCache.isReplay(claims.ID)` (which takes `cache.mu.RLock()` and releases it) [2](#0-1) , then does signer/authorized-key lookups, and only afterward calls `h.jwtCache.recordUsage(claims.ID)` (which takes `cache.mu.Lock()` separately) to mark the `jti` as used [3](#0-2) . Between the `isReplay` read-lock release and the `recordUsage` write-lock acquisition there is no lock held that spans the entire check-then-act sequence, so two (or more) concurrent requests carrying the identical JWT (same `jti`) can both call `isReplay` and both observe "not yet used" before either calls `recordUsage`. Both requests then pass authorization and both proceed to trigger the workflow.

This is structurally the same defect class as CVE-2021-23133: the kernel removed a list element from `auto_asconf_splist` without holding the lock (`addr_wq_lock`) that was supposed to protect the entire operation, allowing a concurrent actor to race the unprotected window. Here, the entire "is this JWT already used, and if not, mark it used" operation should be a single atomic critical section (e.g., `LoadOrStore`), but it is split into two independently-locked steps, creating an unprotected race window between two concurrent unprivileged requests.

### Impact Explanation
A single-use, time-bound authorization token (JWT) is a security control meant to bound how many workflow-trigger requests a given signed credential can authorize. The race allows an attacker (or even a legitimate but retrying/concurrent client) to reuse one valid JWT across multiple concurrent requests, effectively bypassing the single-use / anti-replay guarantee documented in the code's own comment ("prevent replay attacks"). Depending on downstream rate limiting and workflow semantics, this could lead to duplicate/unauthorized workflow executions triggered from a single credential — an authentication/authorization control bypass in the internet-facing gateway HTTP trigger path.

### Likelihood Explanation
Exploitation requires only sending the same signed JWT-bearing request concurrently (e.g., two parallel HTTP requests with identical `Authorization` header/JWT) to the gateway's HTTP trigger endpoint — no elevated privileges, no node/peer compromise, and no special timing tools beyond ordinary request concurrency. The race window is small but real; concurrent identical requests are trivial for a client to produce reliably.

### Recommendation
Make the check-and-record operation atomic under a single lock acquisition (or use a `sync.Map`/map with `LoadOrStore` semantics) so that only one caller can observe "not replayed" and successfully claim the `jti`. For example, merge `isReplay` and `recordUsage` into one method that holds `cache.mu.Lock()` for the whole "look up, and if absent, insert" sequence and returns whether the token was newly claimed, then reject if it was already present.

### Proof of Concept
1. Obtain (or forge, if signer key is otherwise available) a valid JWT for a workflow trigger request with a fixed `jti`.
2. Send two (or more) concurrent `HandleUserTriggerRequest` calls to the gateway's HTTP trigger handler using the identical JWT in the `Authorize` call path [4](#0-3) .
3. Both goroutines call `h.jwtCache.isReplay(claims.ID)` before either calls `h.jwtCache.recordUsage(claims.ID)` [5](#0-4) ; both return `false` for "isReplay" and both proceed to pass authorization, resulting in the same single-use JWT authorizing two separate workflow trigger executions.

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

**File:** core/services/gateway/handlers/capabilities/v2/workflow_metadata_handler.go (L399-405)
```go
func (cache *jwtReplayCache) isReplay(jti string) bool {
	cache.mu.RLock()
	defer cache.mu.RUnlock()

	_, exists := cache.cache[jti]
	return exists
}
```
