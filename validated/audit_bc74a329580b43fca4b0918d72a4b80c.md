### Title
JWT Replay-Protection Check-Then-Act Race Allows Concurrent Reuse of the Same JWT for Repeated Unauthorized Trigger Requests - ([File: core/services/gateway/handlers/capabilities/v2/workflow_metadata_handler.go])

### Summary
`WorkflowMetadataHandler.Authorize` checks whether a JWT `jti` has already been used, and only marks it as used *after* the rest of the authorization logic completes. The "check" (`isReplay`) and the "commit" (`recordUsage`) are two separate, non-atomic operations against the same map, protected by independent lock acquisitions rather than a single atomic add. This mirrors the GMX bug class: state meant to prevent a value from being reused/re-triggered is left un-updated at the moment it matters, letting an unprivileged caller exploit the gap to reuse the same authorization artifact multiple times before it is finally marked "spent."

### Finding Description
`Authorize` is the JWT verification entry point used for HTTP-trigger requests reaching the gateway from an external/unprivileged caller: [1](#0-0) 

The replay-protection cache implementation shows the check and the record are two distinct critical sections: [2](#0-1) 

`isReplay(claims.ID)` takes an `RLock`, reads, and releases the lock. Only later — after signer/authorized-key checks — is `recordUsage(claims.ID)` called, which takes a separate `Lock` to write the entry. Between these two calls there is no lock held across the whole `Authorize` invocation, so if two requests carrying the identical signed JWT (same `jti`, same digest, same signature) arrive concurrently — which an unprivileged external caller fully controls, e.g., by firing the same signed request twice in parallel — both can pass `isReplay` (both see "not present") before either calls `recordUsage`. Both then pass signer/authorized-key checks and are treated as valid, authorized calls, and the JWT is only recorded once both have gone through.

This is structurally the same defect class as the GMX report: a control meant to prevent reuse of a single-use artifact (a decrease order that should be "touched"/consumed on execution; here, a JWT `jti` that should be single-use) is not updated atomically at the point of use, leaving a window where the artifact can be reused by the same untrusted actor to bypass the intended one-time-use guarantee.

### Impact Explanation
JWTs here authorize HTTP trigger requests to workflow nodes on behalf of a workflow owner (`Authorize` gates `h.authorizedKeys[workflowID]` lookups and ultimately reaches `HandleUserTriggerRequest`/node fan-out). The `jti`/replay mechanism is the sole protection against a signed request being submitted more than once by a request-replaying client. A successful race lets an external, unprivileged caller cause a signed trigger request to be authorized and dispatched more than once, defeating the single-use guarantee the replay cache is supposed to provide (analogous to "request impersonation"/"quota/allowlist bypass" — the caller effectively bypasses the intended one-shot authorization limit using only their own already-obtained signed token). The severity is bounded by what duplicate execution of a trigger request can do downstream (duplicate workflow triggering), but the authorization control itself is concretely bypassable via this race.

### Likelihood Explanation
Exploitability requires only that the same unprivileged external caller send two copies of an already-signed request in quick succession — no privileged access, no cryptographic break, and no interaction with other tenants is needed. The window is a few map operations wide (lock-release-to-lock-reacquire), which is small but real under concurrent HTTP dispatch on a busy gateway; network jitter or deliberately parallel submission by the attacker widens the practical chance of winning the race. This is a genuine TOCTOU bug reachable from the internet-facing gateway HTTP trigger path, not a theoretical or mocked-only scenario.

### Recommendation
Make the check-and-mark atomic: acquire a single write lock (or use a `sync.Map`/atomic "load-or-store" primitive) that performs "if jti exists, reject; otherwise insert" as one indivisible operation, and reject the request if insertion finds the key already present. This should happen as early as possible in `Authorize` (ideally immediately after signature/digest verification) rather than deferring `recordUsage` to the end of the function, so no other work is performed for a `jti` that turns out to be a duplicate.

### Proof of Concept
1. An external caller crafts and signs one valid JWT for a JSON-RPC trigger request (valid `jti`, `iss`, `exp`, `digest` matching the request).
2. The caller sends this exact signed request twice concurrently to the gateway's HTTP-trigger endpoint (e.g., two parallel goroutines/HTTP clients hitting the same node).
3. Both requests reach `WorkflowMetadataHandler.Authorize` on separate goroutines at nearly the same time.
4. Goroutine A calls `isReplay(claims.ID)` → not found (cache empty) → proceeds to authorized-key checks.
5. Before goroutine A reaches `recordUsage`, goroutine B calls `isReplay(claims.ID)` → also not found → also proceeds.
6. Both goroutines pass all checks and eventually call `recordUsage`; both were "authorized" using the single JWT, i.e., the replay protection did not prevent the second (replayed) request from being authorized, contrary to its stated purpose ("prevent replay attacks").

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
