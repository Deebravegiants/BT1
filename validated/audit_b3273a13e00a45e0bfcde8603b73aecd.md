The code confirms the claim exactly as described. `Authorize` performs `isReplay(claims.ID)` as a check, then does other authorization work, then only calls `recordUsage(claims.ID)` at the end [1](#0-0) . The `isReplay` and `recordUsage` methods use separate lock scopes (`RLock`/`RUnlock` for check, `Lock`/`Unlock` for write) with no atomicity between them [2](#0-1) . This is a genuine, non-atomic check-then-act TOCTOU race: two concurrent requests with the same JWT `jti` can both pass `isReplay` before either calls `recordUsage`, allowing both to be authorized and both to trigger a workflow execution via the internet-facing HTTP trigger gateway path.

Audit Report

## Title
JWT replay-protection check-then-record race in gateway HTTP trigger authorization allows one-time JWT reuse - ([File: core/services/gateway/handlers/capabilities/v2/workflow_metadata_handler.go])

## Summary
`WorkflowMetadataHandler.Authorize` checks whether a JWT's `jti` has been used via `jwtReplayCache.isReplay` and only records it as used via `jwtReplayCache.recordUsage` after subsequent authorization checks succeed. These two operations are protected by independent lock acquisitions (`RLock`/`RUnlock` then later `Lock`/`Unlock`) rather than a single atomic critical section, so two concurrent requests bearing the same JWT can both pass the replay check before either marks the token used.

## Finding Description
`Authorize` is invoked from `httpTriggerHandler.authorizeRequest` for every inbound `workflow.execute` HTTP trigger request, an internet-facing, unprivileged-caller entry point. Inside `Authorize`, `h.jwtCache.isReplay(claims.ID)` is checked early [3](#0-2) , and `h.jwtCache.recordUsage(claims.ID)` is only called near the end of the function, after the workflow-lookup and signer-authorization checks succeed [4](#0-3) . The cache's `isReplay` takes an `RLock`/`RUnlock` and returns, while `recordUsage` separately takes a `Lock`/`Unlock` [2](#0-1) . There is no shared critical section spanning both the check and the write, so two goroutines processing requests with an identical `jti` can both observe `isReplay == false` before either calls `recordUsage`, defeating the single-use design intent stated in the error message "JWT token has already been used. Please generate a new one with new id (jti)."

## Impact Explanation
This allows unauthorized duplicate triggering of a workflow execution using a JWT designed to be single-use, bypassing the gateway's replay protection for the HTTP trigger capability — an in-scope "gateway request impersonation / replay" style impact. The request-ID based de-duplication in `setupCallback` is keyed on `req.ID`, a separate control that does not close this JWT-specific race.

## Likelihood Explanation
Exploitation only requires an external, unprivileged caller to send the same previously-obtained/valid JWT twice in close temporal proximity (e.g., two concurrent requests). The race window is narrow, bounded by the time between the read-lock release in `isReplay` and the write-lock acquisition in `recordUsage`, but it is real, deterministically reachable by an attacker who controls request timing, and does not require any elevated privileges or host/operator access.

## Recommendation
Make the check-and-record operation atomic by acquiring a single write lock across both the membership check and the insertion (e.g., a combined `checkAndRecord(jti string) bool` method using one `Lock`/`Unlock`), or use a concurrency-safe primitive such as `sync.Map.LoadOrStore` so that only one of two concurrent requests bearing the same `jti` can ever succeed.

## Proof of Concept
1. Obtain a valid signed JWT with a fixed `jti` for a `workflow.execute` HTTP trigger request (as in `TestWorkflowMetadataHandler_Authorize`'s "JWT replay protection" subtest).
2. Invoke `handler.Authorize(workflowID, tokenString, req)` concurrently from two goroutines instead of sequentially.
3. Observe that both calls can return a non-nil `*AuthorizedKey` with no error, because both execute `isReplay(claims.ID)` before either executes `recordUsage(claims.ID)`, demonstrating the TOCTOU race and violating the intended single-use JWT guarantee.

### Citations

**File:** core/services/gateway/handlers/capabilities/v2/workflow_metadata_handler.go (L87-107)
```go
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
