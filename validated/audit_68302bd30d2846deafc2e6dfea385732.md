### Title
TOCTOU race in gateway JWT single-use replay check allows an external caller to reuse the same signed workflow-trigger JWT concurrently, bypassing single-use enforcement - (File: core/services/gateway/handlers/capabilities/v2/workflow_metadata_handler.go)

### Summary
The gateway's `WorkflowMetadataHandler.Authorize` method, which authenticates unprivileged external HTTP-trigger requests to workflows, checks JWT replay (`isReplay`) and records usage (`recordUsage`) as two separate, non-atomic locked operations. An attacker who fires two (or more) concurrent requests carrying the same signed JWT can pass the replay check on all of them before any of them records the `jti`, letting a single-use trigger token authorize multiple workflow executions.

### Finding Description
`Authorize` verifies the request JWT, then performs replay protection via:
```go
if h.jwtCache.isReplay(claims.ID) { ... return error }
...
h.jwtCache.recordUsage(claims.ID)
``` [1](#0-0) 

`isReplay` takes an `RLock`, checks map membership, and returns; `recordUsage` separately takes a `Lock` and inserts the `jti` into the cache: [2](#0-1) 

Because the check-then-record sequence is not atomic and is not guarded by a single lock spanning both steps, two goroutines processing the same JWT (e.g., replayed by the caller in parallel, or retried by an unreliable client/proxy) can both observe `isReplay == false` before either calls `recordUsage`. Both requests then pass the "not authorized" gate concurrently, and — assuming the signer/key check also passes — both proceed to trigger the workflow. This is structurally the same bug class as the external report: a state-changing security control (replay/one-time-use enforcement, analogous to `pause`) has a race window during which an unprivileged caller can slip an action through before the control is durably applied.

This endpoint is reachable directly by unprivileged external callers of the internet-facing gateway's HTTP trigger path (`Authorize` is the JWT authorization entry point for HTTP-triggered workflow execution requests), not by an operator or a mocked-only test path.

### Impact Explanation
A caller possessing one valid signed trigger JWT (which is meant to be single-use per the code's stated intent — "Please generate a new one with new id (jti)") can, via a race, cause the associated workflow to be triggered more than once from a single authorized JWT. Depending on the downstream workflow, this can result in duplicate/unauthorized job runs (e.g., duplicate fund transfers, duplicate external actions, or resource exhaustion) beyond what the token issuer intended to authorize — this matches the "unauthorized job run" bypass category.

### Likelihood Explanation
Exploitability requires only sending the same signed request twice concurrently (e.g., two parallel HTTP connections to the gateway with identical body/JWT) — a trivial action for any external client, no special privilege or malicious node/peer participation required. Because both the read and the write hold independent, narrow locks rather than a single atomic check-and-set, the race window, while short, is deterministically triggerable by concurrency rather than requiring rare timing luck.

### Recommendation
Make the replay check-and-record atomic: acquire a single write lock (or use a `sync.Map`/`LoadOrStore`-style construct) for the combined "check membership, and if absent, insert" operation on `jti`, e.g.:
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
and call this single method from `Authorize` instead of the separate `isReplay` + `recordUsage` calls.

### Proof of Concept
1. Obtain a validly signed workflow-trigger JWT with claim `jti = X` for a registered workflow/signer.
2. Fire two (or more) concurrent HTTP requests to the gateway's HTTP trigger endpoint using the identical JWT.
3. In `Authorize`, both goroutines call `h.jwtCache.isReplay(X)` before either calls `h.jwtCache.recordUsage(X)`; both observe `exists == false` and both requests pass authorization.
4. Both requests proceed to trigger workflow execution, effectively reusing a token intended to be single-use — confirmed by inspecting `isReplay`/`recordUsage` as two distinct locked calls without a shared atomic critical section, per the cited code.

Note: I could not find/verify a downstream enforcement layer (e.g., additional idempotency keys at the workflow-execution layer) that might independently deduplicate the resulting trigger requests; if such a layer exists elsewhere in the trigger-handling pipeline, it would reduce but not eliminate the significance of this race, since the JWT-level replay guard is the documented single-use control point.

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
