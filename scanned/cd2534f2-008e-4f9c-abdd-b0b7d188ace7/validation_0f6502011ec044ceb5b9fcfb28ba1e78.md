## Title
JWT replay-cache check-then-set race allows a workflow HTTP trigger token to be reused (double execution) - (File: core/services/gateway/handlers/capabilities/v2/workflow_metadata_handler.go)

### Summary
The OpenQ bug is a classic check-then-act flaw: `claimOngoingPayout()` computes a claim id and immediately marks it "claimed" and pays out, without first verifying it wasn't already claimed, so the same `claimId` can be paid twice via concurrent/duplicate submissions. The closest reachable analog in this repo's unprivileged-actor, internet-facing path is the JWT replay-protection cache used by `WorkflowMetadataHandler.Authorize`, which gates authorization of HTTP-trigger requests coming from an unprivileged client through the gateway.

### Finding Description
`WorkflowMetadataHandler.Authorize` is the authentication gate for the gateway's HTTP Trigger Handler, used to authorize inbound workflow-execution requests signed with a client JWT [1](#0-0) . It performs replay protection with two separate, non-atomic operations on the `jwtReplayCache`:

1. `h.jwtCache.isReplay(claims.ID)` — acquires an `RLock`, checks membership, and releases the lock [2](#0-1) .
2. Later, after signer/authorized-key validation succeeds, `h.jwtCache.recordUsage(claims.ID)` — acquires a separate `Lock` and inserts the jti [3](#0-2) [4](#0-3) .

Because the "check" (`isReplay`) and the "record" (`recordUsage`) are not performed under one atomic critical section, this is structurally the same pattern as the OpenQ bug: the "already used" state is checked, but the actor can slip a second (or many concurrent) request(s) through before the state is recorded. If two requests carrying the same signed JWT (same `jti`/`claims.ID`) arrive concurrently at the gateway, both can pass `isReplay` (both see "not yet recorded") before either calls `recordUsage`, and both will be authorized and dispatched to the DON as legitimate distinct trigger executions.

This is in clear contrast to the vault package's `RequestReplayGuard.CheckAndRecord`, which performs the check-and-set atomically under a single mutex [5](#0-4) , correctly closing this exact race. The `WorkflowMetadataHandler`'s jwt cache does not use this pattern.

Note: the `httpTriggerHandler.setupCallback` request-ID in-flight map check is a separate, unrelated dedup mechanism keyed on request ID (not the JWT `jti`), and is itself checked/inserted under a single lock (atomic) [6](#0-5) , so it does not close the JWT-jti race described above — a duplicate submission using the same JWT but a distinct request ID would bypass that check while still hitting the racy jwt replay cache.

### Impact Explanation
A successful race lets an unprivileged, unauthenticated-beyond-signing client trigger the same signed workflow-execution authorization twice (or more) using a single valid JWT that was intended to authorize exactly one execution. Depending on downstream capability/workflow semantics this can translate into duplicate/unauthorized workflow executions being dispatched to the DON under one authorization event — a request-impersonation/replay-bypass class of issue, mirroring the "claim same ID twice" fund/authorization double-dip in the original report. The severity is bounded by whatever the workflow does per-trigger (e.g., duplicate on-chain writes, redundant capability calls, resource exhaustion), but the authorization control itself is provably bypassable.

### Likelihood Explanation
Exploitation requires the attacker (a legitimate JWT holder for their own workflow) to fire two (or more) requests carrying the same signed JWT to the gateway at effectively the same time so both goroutines observe the pre-recorded state before either records usage — a narrow but realistic race window (network round-trip skew, or deliberately parallel connections), no special network position or malicious node needed. This is a standard, reproducible TOCTOU race with off-the-shelf tooling (e.g., parallel HTTP requests), which is straightforward for a single unprivileged client to trigger.

### Recommendation
Merge the replay-cache check and insert into one atomic operation guarded by a single mutex, analogous to `RequestReplayGuard.CheckAndRecord` in the vault package:
```go
func (cache *jwtReplayCache) checkAndRecord(jti string) error {
    cache.mu.Lock()
    defer cache.mu.Unlock()
    if _, exists := cache.cache[jti]; exists {
        return ErrJWTAlreadyUsed
    }
    cache.cache[jti] = time.Now()
    return nil
}
```
Call this once, immediately after successful signer/authorized-key validation (replacing the separate `isReplay` + `recordUsage` calls), so no window exists between checking and recording jti usage.

### Proof of Concept
1. Client signs one JWT (`jti = X`) for a workflow-trigger request.
2. Client fires two HTTP trigger requests to the gateway with distinct request IDs but the same JWT (`Auth` header/token) concurrently (e.g., via `go func(){...}()` twice, or two parallel curl processes).
3. Goroutine A: `Authorize` calls `isReplay(X)` → false (not yet seen). Proceeds to validate signer, succeeds, calls `recordUsage(X)`.
4. Goroutine B: if its `isReplay(X)` call executes before A's `recordUsage(X)` completes, it also observes false, passes validation, and is authorized.
5. Both requests pass authorization and are dispatched via `HandleUserTriggerRequest`/DON fan-out as independently authorized executions from the single JWT, despite the intended one-time-use ("already been used") semantics documented in the code comment [7](#0-6) .

### Citations

**File:** core/services/gateway/handlers/capabilities/v2/workflow_metadata_handler.go (L80-90)
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
```

**File:** core/services/gateway/handlers/capabilities/v2/workflow_metadata_handler.go (L105-106)
```go
	h.jwtCache.recordUsage(claims.ID)

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

**File:** core/services/gateway/handlers/capabilities/v2/http_trigger_handler.go (L419-426)
```go
func (h *httpTriggerHandler) setupCallback(ctx context.Context, requestID string, callback handlers.Callback, requestStartTime time.Time, workflowID string) (<-chan struct{}, error) {
	h.callbacksMu.Lock()
	defer h.callbacksMu.Unlock()

	if _, found := h.callbacks[requestID]; found {
		h.handleUserError(ctx, requestID, jsonrpc.ErrConflict, fmt.Sprintf("requestID: %s has already been used. Ensure the requestID is unique for each request.", requestID), callback)
		return nil, fmt.Errorf("in-flight request ID: %s", requestID)
	}
```
