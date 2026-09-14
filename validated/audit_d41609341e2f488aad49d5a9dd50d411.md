### Title
Non-atomic JWT replay check-and-record in `WorkflowMetadataHandler.Authorize` allows concurrent replay of a single HTTP-trigger JWT - ([File: core/services/gateway/handlers/capabilities/v2/workflow_metadata_handler.go])

### Summary
The reported bug class is a classic reentrancy pattern: a function performs a state check, does external/interleaving work, and only updates its protective state afterward — leaving a window where the same input can be processed twice. The closest reachable analog in this Go codebase (which has no Solidity `nonReentrant` concept) is a check-then-act race condition in the unprivileged-facing HTTP Trigger gateway path, where the JWT replay-protection cache is read and written under two separate, non-atomic mutex sections.

### Finding Description
`WorkflowMetadataHandler.Authorize` is invoked from the internet-facing HTTP Trigger handler to authenticate an inbound JWT-signed trigger request before dispatching a workflow execution to DON nodes: [1](#0-0) 

The replay-protection check and the replay-protection record are two separate operations, each independently locked: [2](#0-1) 

`isReplay(claims.ID)` takes an `RLock`, checks membership, and releases the lock. Only afterward — following JWT signature verification, workflow lookup, and signer-authorization checks — does `recordUsage(claims.ID)` take a separate `Lock` to mark the token as used, at line 105 of `Authorize`. There is no single critical section covering "check-not-seen" + "mark-seen"; the mutex is released between the check and the eventual mark. This is structurally the same bug class as the reported Solidity issue: a state-changing/effect operation occurs after other work has run, rather than atomically with the guard check, creating a reentrant window during which the "external" work (JWT verification, authorized-key lookup) can be repeated concurrently before the guard state is committed.

This is unlike the properly-implemented analog for the sibling Vault gateway component, where `RequestReplayGuard.CheckAndRecord` performs the check and the record write inside one held lock: [3](#0-2) 

The `WorkflowMetadataHandler.Authorize`/`jwtReplayCache` pair lacks this atomicity.

### Impact Explanation
If two requests carrying the identical signed JWT (identical `jti`) arrive concurrently at the gateway's HTTP Trigger endpoint — reachable directly by an unprivileged external client — both can pass `isReplay` before either calls `recordUsage`, because the two calls are not covered by one lock. Both concurrent requests then pass signer-authorization and are allowed to trigger the workflow, defeating the single-use guarantee that the JWT `jti` is supposed to provide (as documented in `core/utils/jwt.go`'s JWT design comment). This enables a duplicate/unauthorized workflow execution using a single authorized token — i.e., "unauthorized job run" via replay/duplication, which is one of the accepted impact categories for this class of finding.

### Likelihood Explanation
Exploitability requires the attacker (or a legitimate but hostile intermediary) to fire the same signed JWT request twice in rapid succession/concurrently at the gateway, which is trivial for an external HTTP client with no special privileges — they simply need one previously-issued valid JWT and can race two copies of the same request. The race window is small (bounded by JWT verification + workflow/authorized-key lookup time) but is a genuine, deterministic TOCTOU gap rather than a purely theoretical one, since the check and the write are demonstrably in separate critical sections.

### Recommendation
Make the check-and-mark operation atomic: acquire a single `Lock` (not `RLock`) that spans both the "already used" check and the "mark used" write for a given `jti`, analogous to `RequestReplayGuard.CheckAndRecord`. Concretely, replace the separate `isReplay`/`recordUsage` calls in `Authorize` with a single `jwtReplayCache.checkAndRecord(jti)` method that performs the existence check and the map write under one `mu.Lock()`/`defer mu.Unlock()` block, returning "already used" if the entry exists and otherwise inserting it before returning success — mirroring the pattern already used correctly in `core/capabilities/vault/request_replay_guard.go`.

### Proof of Concept
1. Register a workflow and obtain a valid signed JWT for an `HTTPTriggerRequest` (as done in `TestHttpTriggerHandler_HandleUserTriggerRequest`).
2. Fire two goroutines simultaneously calling `WorkflowMetadataHandler.Authorize(workflowID, tokenString, req)` (or the equivalent `handler.HandleUserTriggerRequest` path) with the identical token, similar to the concurrency pattern in `TestRequestReplayGuard_ConcurrentAccess` (`core/capabilities/vault/request_replay_guard_test.go` lines 96-126) but applied to `jwtReplayCache`/`Authorize` instead of `RequestReplayGuard`.
3. Because `isReplay` and `recordUsage` are separately locked, both goroutines can observe `isReplay == false` before either calls `recordUsage`, resulting in both authorizations succeeding — contrary to the single-use guarantee validated for the vault path but absent here.

Note: I was not able to execute this PoC directly (no code execution access); the race is inferred from the non-atomic locking structure of `isReplay`/`recordUsage` versus the atomic `CheckAndRecord` pattern used elsewhere in the codebase, and from the absence of any equivalent concurrency test for `jwtReplayCache` (unlike `TestRequestReplayGuard_ConcurrentAccess` for the vault guard).

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
