This confirms the claim precisely as described.

The `Authorize` function in `WorkflowMetadataHandler` performs `isReplay` (RLock-protected read) and `recordUsage` (Lock-protected write) as two separate lock acquisitions, with signer/authorized-key validation happening in between [1](#0-0) . The underlying cache methods confirm no shared critical section spans both operations [2](#0-1) . This is a genuine TOCTOU (check-then-act) race: two goroutines processing the same `jti` concurrently can both pass `isReplay` returning `false` before either calls `recordUsage`, since there is no lock held across both calls.

By contrast, the vault package's analogous replay guard performs the check and record atomically under a single `sync.Mutex` critical section via `CheckAndRecord`, which correctly closes this race [3](#0-2) . No caller-side lock wraps `Authorize` to serialize concurrent invocations for the same JWT — it's invoked directly from the gateway's HTTP trigger authorization path with no additional synchronization, so the internal race is real and exploitable by sending two concurrent copies of an identical signed JWT request.

This satisfies the required validation checks: exact in-scope file/function/line references, clear root cause (split check-then-act instead of atomic check-and-record), a reachable exploit path requiring only an unprivileged client capable of sending two concurrent copies of a validly-signed request, and no compensating synchronization elsewhere in the code.

Audit Report

## Title
JWT Replay Cache Check-Then-Act Race Allows Token Reuse in `WorkflowMetadataHandler.Authorize` - (File: core/services/gateway/handlers/capabilities/v2/workflow_metadata_handler.go)

## Summary
`WorkflowMetadataHandler.Authorize` calls `h.jwtCache.isReplay(claims.ID)` (RLock) and `h.jwtCache.recordUsage(claims.ID)` (Lock) as two independent, non-atomic lock acquisitions with authorization logic in between, rather than performing the check and record as a single atomic operation. Two concurrent requests carrying the identical JWT `jti` can both pass the replay check before either records usage, defeating the anti-replay guarantee for gateway workflow-trigger authentication.

## Finding Description
`Authorize` verifies the JWT signature, then checks `isReplay`, then validates the signer against `authorizedKeys`, and only afterward calls `recordUsage` [4](#0-3) . The cache's `isReplay` and `recordUsage` methods acquire and release the mutex independently with no shared critical section [2](#0-1) . This is a textbook check-then-act race: nothing prevents two goroutines from both executing `isReplay` (each seeing `exists == false`) before either executes `recordUsage`. The comparable `vault.RequestReplayGuard.CheckAndRecord` performs the equivalent check-and-record under a single lock, demonstrating the correct pattern is known and used elsewhere in the codebase but not applied here [3](#0-2) .

## Impact Explanation
The JWT `jti` mechanism is intended to make signed HTTP trigger requests single-use. This race allows a client to have two copies of the same signed request both accepted as authorized, bypassing the anti-replay control on the gateway's authentication path for workflow trigger execution. This maps to the in-scope "gateway request impersonation" / authentication-bypass impact category, since a token meant to authorize a single execution can be used twice.

## Likelihood Explanation
Exploitation requires only an unprivileged external client capable of sending (or capturing and resending) two copies of a validly-signed JWT request such that they are processed concurrently by the same `WorkflowMetadataHandler` instance — no privileged role, host access, or special network position needed. The race window is narrow (between two lock acquisitions) but is genuinely reachable in a client-facing code path.

## Recommendation
Merge `isReplay` and `recordUsage` into a single atomic check-and-record method performed under one lock (mirroring `vault.RequestReplayGuard.CheckAndRecord`), and call it in `Authorize` so no window exists where two concurrent requests bearing the same `jti` can both pass the check.

## Proof of Concept
1. Construct a validly-signed JWT trigger request with a fixed `jti`.
2. Fire two goroutines that both call `WorkflowMetadataHandler.Authorize` with the same token/workflowID/request concurrently (or via a unit test directly invoking `jwtCache.isReplay` / `recordUsage` from two goroutines with a `sync.WaitGroup` and a barrier to force interleaving).
3. Observe both calls to `isReplay` returning `false`, and both `Authorize` invocations returning success (no `errors.New("JWT token has already been used...")`), confirming the token was accepted twice.

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
