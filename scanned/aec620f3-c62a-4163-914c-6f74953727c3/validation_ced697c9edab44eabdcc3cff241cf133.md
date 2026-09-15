### Title
JWT replay-cache check-and-record race allows concurrent replay of a single-use HTTP trigger token - ([File: core/services/gateway/handlers/capabilities/v2/workflow_metadata_handler.go])

### Summary
`WorkflowMetadataHandler.Authorize` is meant to enforce that each JWT (identified by its `jti` claim) authorizes exactly one HTTP trigger request. The single-use guarantee is implemented as two separate, non-atomic operations — `isReplay()` (read lock) followed later by `recordUsage()` (write lock) — with unrelated work (signer/authorized-key lookup) happening between them. An unprivileged client that fires the same signed JWT twice concurrently can have both requests pass the `isReplay` check before either calls `recordUsage`, defeating the anti-replay control entirely.

### Finding Description
`Authorize` is the entry point used by the internet-facing gateway to authenticate every incoming HTTP-trigger workflow-execution request: [1](#0-0) 

The single-use enforcement relies on `jwtReplayCache`: [2](#0-1) 

`isReplay(claims.ID)` takes the cache's `RLock`, checks for existence, and releases the lock. `recordUsage(claims.ID)` is called much later in `Authorize`, after the signer lookup and authorized-key membership check, and takes a separate `Lock`. Because the check and the eventual write are two independent critical sections rather than one atomic "check-and-set," two goroutines calling `Authorize` concurrently with the same JWT (identical `jti`) can both observe `isReplay == false` before either has called `recordUsage`. Both requests then proceed past the replay guard, both are treated as authorized, and both go on to call `setupCallback`/`sendWithRetries` in `httpTriggerHandler.HandleUserTriggerRequest`, resulting in two independent workflow executions being triggered from what was supposed to be a single-use, single-execution authorization token.

This is structurally the same bug class as the Dream Health Chain incident: a claimed/consumed state (there: reward payout; here: JWT authorization) is not atomically transitioned before being reused, so the "already spent" check can be bypassed by racing the state transition, letting an unprivileged actor obtain the effect of the protected action (workflow execution / trigger dispatch) more times than the design allows.

### Impact Explanation
An unprivileged external caller who possesses one validly-signed JWT for an HTTP trigger request can, by sending the token in two (or more) concurrent requests, cause the gateway to accept and dispatch more than one workflow execution using a token that was designed to authorize only one. Because `Authorize` also gates the workflow's per-request rate limiter and downstream node dispatch, this is a genuine authorization/anti-replay bypass reachable directly from an unprivileged client over the internet-facing gateway HTTP trigger path, not merely a cosmetic race. Impact scales with how many workflow executions/duplicate triggers a caller can force per signed token before the token's own JWT expiry, and whether the workflow being triggered has side effects (e.g., on-chain writes, fund movement capabilities) that assume single-execution-per-authorization semantics.

### Likelihood Explanation
The race window is bounded but real: it spans from `isReplay()`'s read to `recordUsage()`'s write, during which `utils.VerifyRequestJWT` (crypto/signature verification) and an authorized-key map lookup execute. An attacker fully controls the timing of both requests (simple concurrent HTTP calls) and can amplify the race by sending many duplicate copies simultaneously, which increases the probability that at least two land inside the vulnerable window on typical multi-core/goroutine scheduling. No privileged access or insider assistance is required — only a previously-obtained, still-valid signed JWT, which by design is generated client-side and used to call the public trigger endpoint.

### Recommendation
Make the replay check-and-record atomic: merge `isReplay` and `recordUsage` into a single method that holds the cache's write lock for the whole check-then-insert sequence (i.e., do a `Lock()`, check membership, and insert in one critical section), and call this from `Authorize` immediately after JWT signature verification, before doing any downstream authorized-key work. This guarantees that only the first of any concurrent requests bearing the same `jti` can pass.

### Proof of Concept
1. Client generates one valid signed JWT (`jti = X`) for an HTTP trigger request to a registered workflow, per the flow exercised in `TestHttpTriggerHandler_HandleUserTriggerRequest`.
2. Client fires two (or more) HTTP requests carrying the identical JWT concurrently (e.g., via `sync.WaitGroup` launching two goroutines that both call the gateway's trigger endpoint at the same instant).
3. Both requests reach `WorkflowMetadataHandler.Authorize` concurrently; both execute `h.jwtCache.isReplay(claims.ID)` before either has reached `h.jwtCache.recordUsage(claims.ID)`, since the two calls are not covered by one lock.
4. Both calls to `isReplay` return `false`; both requests pass the signer/authorized-key checks and both call `recordUsage`, and both are accepted by `Authorize`, subsequently triggering two independent workflow executions via `HandleUserTriggerRequest` → `setupCallback` → `sendWithRetries` from a single supposedly single-use JWT.

Note: This is based on static code review; a live test harness (as used in `TestHttpTriggerHandler_HandleUserTriggerRequest` for the "duplicate JWT token and request ID" case) with artificially injected concurrency/delay in `jwtReplayCache` would be needed to deterministically reproduce and confirm the race window in CI.

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
