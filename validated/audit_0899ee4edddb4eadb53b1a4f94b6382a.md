The code matches the claim exactly as described. The `isReplay` check (RLock, L399-405) and `recordUsage` write (Lock, L407-412) in `workflow_metadata_handler.go` are separate critical sections, with unrelated authorization logic (workflow/signer lookup) executed in between them inside `Authorize` (L80-108). This is a genuine TOCTOU race: two concurrent calls with an identical `jti` can both pass `isReplay` before either calls `recordUsage`, allowing the same signed JWT to be accepted twice.Based on my review, the code exactly matches the claim. `WorkflowMetadataHandler.Authorize` at [1](#0-0)  calls `isReplay` (RLock-based read) before workflow/signer lookups, and only calls `recordUsage` (Lock-based write) after those checks succeed — with `jwtReplayCache.isReplay` and `recordUsage` implemented as two independently-locked critical sections at [2](#0-1) . This is a genuine TOCTOU gap: nothing prevents two concurrent `Authorize` calls with the same `jti` from both passing `isReplay` before either reaches `recordUsage`. The codebase already demonstrates the correct atomic pattern elsewhere via `RequestReplayGuard.CheckAndRecord`, which performs the existence check and insertion under a single `Lock`/`Unlock` [3](#0-2) , confirming the JWT cache's split-lock design is inconsistent with the project's own established, safer pattern.

Audit Report

## Title
JWT replay-protection check-then-record race allows replay of a workflow-trigger JWT - ([File: core/services/gateway/handlers/capabilities/v2/workflow_metadata_handler.go])

## Summary
`WorkflowMetadataHandler.Authorize` checks JWT replay via `jwtReplayCache.isReplay` (RLock) and only records usage via `recordUsage` (Lock) after unrelated workflow/signer authorization logic completes. Because the check and the record are not one atomic operation, two concurrent requests carrying an identical `jti` can both pass the replay check before either records it, allowing a single-use, signed JWT to be accepted twice.

## Finding Description
In `Authorize` (`core/services/gateway/handlers/capabilities/v2/workflow_metadata_handler.go`, L80-108), `h.jwtCache.isReplay(claims.ID)` is called first and releases its `RLock` immediately after reading `cache.cache[jti]`. Only after the workflow ID and signer are validated does the function call `h.jwtCache.recordUsage(claims.ID)`, which takes a separate `Lock` to insert the jti. Because these are two independent critical sections rather than one atomic "check-and-insert," a race window exists between the read in `isReplay` and the write in `recordUsage`. This mirrors the already-fixed pattern in `RequestReplayGuard.CheckAndRecord`, which correctly combines existence-check and insertion under a single lock, proving the split-lock design in `jwtReplayCache` is an inconsistency/regression relative to the codebase's own established safe pattern.

## Impact Explanation
A successfully exploited race lets an external caller cause the gateway to accept and dispatch the same signed, single-use JWT-authorized trigger request more than once to DON nodes, resulting in duplicate/unauthorized workflow execution requests beyond what the caller's single credential should permit. This falls into the "unauthorized job run" / "gateway request impersonation-adjacent replay bypass" impact category.

## Likelihood Explanation
The race is triggerable by any unprivileged external caller who controls when they submit their own two copies of the same signed request over the gateway's HTTP-trigger path — no privileged role, node compromise, or special network position is required. However, the race window is narrow (bounded by the time between the `isReplay` read and the `recordUsage` write, which includes a couple of map lookups), so success is probabilistic rather than deterministic per attempt, though repeatable with retries.

## Recommendation
Merge `isReplay` and `recordUsage` into a single atomic check-and-record operation performed under one `Lock`, analogous to `RequestReplayGuard.CheckAndRecord`, and call it once from `Authorize` in place of the separate calls.

## Proof of Concept
1. Craft one valid signed JWT for a request with a fixed `jti` for an authorized workflow/signer.
2. Launch two goroutines concurrently calling `WorkflowMetadataHandler.Authorize(workflowID, token, &req)` with the identical token.
3. Under a `go test -race` timing where both goroutines execute `isReplay` before either executes `recordUsage`, both return success (`*gateway.AuthorizedKey`, nil), demonstrating double-acceptance of a single-use JWT. This can be implemented as a Go unit test in `core/services/gateway/handlers/capabilities/v2/workflow_metadata_handler_test.go` using a barrier (e.g., a channel/WaitGroup) to align both goroutines just past the `isReplay` check before either proceeds.

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
