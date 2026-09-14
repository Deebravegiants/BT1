### Title
JWT Replay-Protection Check-Then-Act Race Allows Trigger Request Replay Bypass - ([File: core/services/gateway/handlers/capabilities/v2/workflow_metadata_handler.go])

### Summary
The HTTP Trigger Handler's JWT replay-protection cache in `WorkflowMetadataHandler.Authorize` performs the "is this JWT already used" check and the "mark this JWT as used" write as two separate, non-atomic lock-protected operations. Concurrent requests carrying the same JWT can both pass the replay check before either records usage, defeating the intended one-time-use guarantee — analogous to the Ajna report's root cause where a piece of tracked state (there, LP position; here, JWT-usage state) is checked/consumed without an atomic guarantee, allowing the associated value/guarantee to be used more than once.

### Finding Description
`Authorize` is the authentication entry point for inbound HTTP Trigger requests reaching the gateway from unprivileged, internet-facing clients, per the HTTP Handlers V2 flow ("Authentication: Verifies JWT token (ECDSA signature) and checks authorized keys"). [1](#0-0) 

The implementation is: [2](#0-1) 

The replay cache exposes `isReplay` (acquires `RLock`, reads, releases) and `recordUsage` (acquires `Lock`, writes, releases) as two independent critical sections: [3](#0-2) 

Because `isReplay(claims.ID)` and `recordUsage(claims.ID)` are not combined into a single atomic "check-and-set" operation, two (or more) concurrent `Authorize` calls carrying the identical JWT (`jti`) can each execute `isReplay` and observe "not yet used" before either has called `recordUsage`. Both requests then proceed to be authorized and dispatched to the workflow DON as valid trigger invocations, even though the JWT was intended to be single-use.

### Impact Explanation
This breaks the single-use guarantee of the JWT that gates unprivileged access to HTTP Trigger capability invocation. An attacker (or a legitimate caller replaying a captured request) who fires the same signed JWT-bearing trigger request concurrently can cause the workflow to be triggered more than once from a single, intended one-time authorization — a concrete authorization/replay-protection bypass on the internet-facing gateway path. Depending on the workflow being triggered, this can cause duplicate/unauthorized job runs, similar in effect to the "unauthorized job run" category, and mirrors the underlying bug class from the source report: a check on tracked per-identity state is not enforced atomically with the corresponding state mutation, letting the same authorization be "spent" more than once instead of being safely reflected only once.

### Likelihood Explanation
The race window requires only that two identical JWT-bearing requests race in flight before the first request's `recordUsage` call executes — trivially achievable by any external caller sending the same signed request twice in rapid succession (no special privileges, insider access, or node compromise required), which is consistent with the "unprivileged-actor" and "internet-facing gateway" scope. The likelihood is moderate-to-high in a busy gateway where request dispatch/response paths involve network I/O between the check and the record call, widening the race window.

### Recommendation
Make replay detection and recording atomic: acquire a single write lock for both the lookup and the insertion (e.g., a `CheckAndRecord(jti string) bool` method that holds `cache.mu.Lock()` for the entire "if exists return true; else set and return false" sequence), and update `Authorize` to call this single atomic method instead of separate `isReplay`/`recordUsage` calls.

### Proof of Concept
1. Client obtains/crafts a valid signed HTTP Trigger request with JWT `jti = X`.
2. Client sends the identical request twice concurrently (e.g., two parallel HTTP connections) to the gateway's HTTP Trigger endpoint.
3. Goroutine A calls `Authorize`, executes `h.jwtCache.isReplay(X)` → `false` (not yet recorded).
4. Before goroutine A reaches `h.jwtCache.recordUsage(X)` at [4](#0-3) , goroutine B calls `Authorize` for the same `jti = X`, and `h.jwtCache.isReplay(X)` also returns `false`.
5. Both goroutines pass the signer/authorized-key check and both call `recordUsage(X)`; both requests are treated as authorized and forwarded to the workflow DON — the "one-time" JWT has been consumed twice.

### Citations

**File:** core/services/gateway/handlers/capabilities/v2/README.md (L78-82)
```markdown

1. **Request Validation**: Validates JSON-RPC format, method, and parameters
2. **Workflow Resolution**: Resolves workflow ID from selector (ID, owner, name, tag)
3. **Authentication**: Verifies JWT token (ECDSA signature) and checks authorized keys
4. **Rate Limiting**: Enforces per-workflow-owner rate limits
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
