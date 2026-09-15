The claim accurately describes the code. Verified: `Authorize` at lines 80-108 checks `isReplay` and later calls `recordUsage` as two separate, independently-locked operations rather than one atomic check-and-record. This matches the exact TOCTOU (time-of-check-to-time-of-use) pattern described.

Audit Report

## Title
JWT Replay Guard Uses Non-Atomic Check-Then-Record, Allowing Concurrent Replay of a Single JWT in HTTP Trigger Workflow Authorization - (File: core/services/gateway/handlers/capabilities/v2/workflow_metadata_handler.go)

## Summary
`WorkflowMetadataHandler.Authorize` checks JWT replay via `h.jwtCache.isReplay(claims.ID)` and later marks it used via `h.jwtCache.recordUsage(claims.ID)`, but these are two separately-locked operations on `jwtReplayCache` rather than one atomic critical section. Concurrent requests carrying the same JWT can both pass the `isReplay` check before either calls `recordUsage`, defeating the single-use replay guarantee.

## Finding Description
`Authorize` at [1](#0-0)  verifies the JWT, calls `h.jwtCache.isReplay(claims.ID)` to reject already-used tokens, performs signer authorization checks against `h.authorizedKeys`, and only afterward calls `h.jwtCache.recordUsage(claims.ID)` to mark the `jti` as spent.

The `jwtReplayCache` implements `isReplay` and `recordUsage` as independently-locked methods: `isReplay` acquires an `RLock`, reads, and releases; `recordUsage` acquires a separate `Lock` afterward and writes, as seen at [2](#0-1) . There is no shared critical section spanning both the check and the write. Two goroutines invoking `Authorize` with an identical JWT concurrently can both execute `isReplay` and observe `exists == false` before either executes `recordUsage`, and both would then pass through the signer-authorization checks and return a valid `*gateway.AuthorizedKey`. Existing checks (JWT signature verification, signer allowlist lookup in `h.authorizedKeys`) do not address this gap since they operate on the JWT/signer validity, not on single-use enforcement, which is exactly what the non-atomic cache fails to guarantee under concurrency.

## Impact Explanation
This is a genuine TOCTOU race in a security-critical replay-prevention primitive that is exposed at the internet-facing gateway HTTP trigger path (`HandleUserTriggerRequest` → `Authorize`). An attacker in possession of one valid signed JWT (e.g., a client replaying its own token, or an intermediary who captured a token in transit) can send concurrent duplicate requests and get more than one accepted as authorized, resulting in duplicate/unauthorized triggering of a workflow execution from a single token — an "unauthorized job run" style impact.

## Likelihood Explanation
The exploit requires only ordinary unprivileged capability to send two or more concurrent HTTP requests with an identical valid JWT — no elevated privileges, host access, or network position are required. The race window is narrow (two independent mutex acquisitions completed in quick succession within the same request-processing pipeline), so success is probabilistic and depends on precise timing, but it is achievable by a remote actor issuing concurrent requests, and the existing test suite (`TestWorkflowMetadataHandler_Authorize`'s "JWT replay protection" subtest) only validates the sequential case, confirming the concurrent path is untested and unguarded.

## Recommendation
Replace `isReplay`/`recordUsage` with a single atomic `CheckAndRecord(jti)` method on `jwtReplayCache` that holds the write lock for the entire check-and-insert operation (mirroring `RequestReplayGuard.CheckAndRecord` in `core/capabilities/vault/request_replay_guard.go`), and update `Authorize` to call this atomic method instead of the two separate calls.

## Proof of Concept
1. Obtain one valid signed JWT for a given request (`jti = X`).
2. Launch two goroutines/HTTP requests calling `WorkflowMetadataHandler.Authorize` concurrently with the same `workflowID`, `token`, and `req`.
3. Both goroutines call `h.jwtCache.isReplay(claims.ID)` before either calls `recordUsage`; since no entry exists yet for `jti=X`, both return `false`.
4. Both proceed through signer/authorized-key checks and both return a non-nil `*gateway.AuthorizedKey`, demonstrating the same JWT was accepted twice — provable via a Go unit test that runs `Authorize` in two goroutines synchronized with a barrier immediately before the `isReplay` call, asserting both return `nil` error.

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
