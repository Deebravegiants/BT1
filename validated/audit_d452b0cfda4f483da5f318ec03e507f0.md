Based on my review, the code exactly matches the citations in the claim, and the vulnerability is real: `Authorize` performs a check-then-act sequence with `isReplay` (RLock) and `recordUsage` (Lock) as two separate, non-atomic operations, creating a genuine TOCTOU race window.

Audit Report

## Title
TOCTOU race in gateway JWT single-use replay check allows an external caller to reuse the same signed workflow-trigger JWT concurrently, bypassing single-use enforcement - (File: core/services/gateway/handlers/capabilities/v2/workflow_metadata_handler.go)

## Summary
`WorkflowMetadataHandler.Authorize` verifies a workflow-trigger JWT and enforces single-use via `h.jwtCache.isReplay(claims.ID)` followed later by `h.jwtCache.recordUsage(claims.ID)`, but these are two independently-locked operations rather than one atomic check-and-set. [1](#0-0)  Two concurrent requests carrying the same signed JWT can both pass `isReplay` before either calls `recordUsage`, allowing a single-use trigger token to authorize more than one workflow execution.

## Finding Description
`isReplay` takes an `RLock`, checks map membership, and releases the lock; `recordUsage` is called later, separately, under a full `Lock`. [2](#0-1)  Between the `isReplay` check at line 87 and the `recordUsage` call at line 105, no lock is held spanning the interval — other authorization steps (workflow ID / signer lookups) occur in between, widening the race window. This is a classic check-then-act race: two goroutines processing identical `(token, jti)` pairs concurrently can both observe `exists == false` in `isReplay` and proceed to `recordUsage` after both have already passed the "already used" gate. No other code path in this file (or, per available search, anywhere else in the indexed codebase) enforces atomicity for this check-and-record sequence. [3](#0-2) 

`Authorize` is invoked as the JWT authorization entry point for unprivileged, internet-facing HTTP-triggered workflow execution requests, so exploitation requires nothing beyond possessing one valid signed trigger JWT and issuing it twice in parallel.

## Impact Explanation
This maps to the in-scope "unauthorized job run" category: a token meant to be single-use (per the handler's own error message, "Please generate a new one with new id (jti)") can be used to trigger a workflow more than once, potentially causing duplicate/unauthorized job executions, duplicate downstream actions, or resource exhaustion beyond what the token issuer authorized.

## Likelihood Explanation
The race requires only firing two (or more) concurrent HTTP requests with an identical valid JWT — trivial for any external caller with a single legitimate token, requiring no elevated privilege, no node/peer compromise, and no unusual timing luck since the window spans multiple lock acquisitions and intervening logic (workflow ID and signer lookups) rather than a few CPU cycles.

## Recommendation
Combine the check and record into a single atomic critical section, e.g., a `checkAndRecord(jti)` method that acquires one write lock, checks for existence, and inserts the timestamp if absent, returning whether the JTI was already used — replacing the separate `isReplay`/`recordUsage` calls in `Authorize`.

## Proof of Concept
1. Obtain a valid signed JWT for a registered workflow/signer with `jti = X`.
2. Issue two concurrent HTTP requests to the gateway's HTTP trigger endpoint carrying identical JWT `X`.
3. Both goroutines call `isReplay(X)` (lines 399-405) before either calls `recordUsage(X)` (lines 407-412); both observe `exists == false`, pass the check at line 87, pass signer authorization, and both call `recordUsage` — both requests return a valid `AuthorizedKey` and proceed to trigger the workflow, confirmed via a Go race-oriented unit test spawning two goroutines calling `Authorize` with the same token and asserting both succeed.

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
