### Title
JWT replay-protection TOCTOU race allows a single-use HTTP Trigger token to be replayed - (File: core/services/gateway/handlers/capabilities/v2/workflow_metadata_handler.go)

### Summary
The Cork Protocol bug class is a "checkpoint-then-mutate" ordering flaw: state is checkpointed for validation, but a subsequent step mutates the same state without checking the checkpoint, causing conflicting/duplicate use of resources that were supposed to be single-use. The Chainlink HTTP Trigger gateway handler contains the same root-cause pattern: JWT replay protection is implemented as a read-check (`isReplay`) followed by a separate write (`recordUsage`), with no atomicity between them, so concurrent requests carrying the identical JWT can both pass the "already used" check before either marks it used.

### Finding Description
`WorkflowMetadataHandler.Authorize` is the entry point that authenticates unprivileged, internet-facing HTTP Trigger requests coming through the gateway's `HandleUserTriggerRequest` / `HandleJSONRPCUserMessage` path [1](#0-0) . It verifies the request JWT, then checks whether the JWT ID (`jti`) was already used, and only afterwards records the `jti` as used: [2](#0-1) 

The replay cache itself performs the check and the write as two separate, independently-locked operations: [3](#0-2) 

`isReplay` takes an `RLock`, reads, and releases the lock; `recordUsage` is only called later in `Authorize`, well after `isReplay` returned and after the authorized-key lookup completed. There is no single critical section that both checks and marks the `jti` as used atomically (e.g., no compare-and-swap or write-lock spanning the check). This mirrors the Cork Protocol root cause: `PsmLib::_separateLiquidity()` checkpoints `ct` totalSupply, but a later, independent code path (`VaultLib::_liquidatedLp()` → `PsmLib::lvRedeemRaWithCtDs()`) mutates the same underlying state without being aware of, or gated by, that checkpoint — the check and the mutation are decoupled in time, allowing double-counting/double-use.

### Impact Explanation
An unprivileged external caller (any client capable of reaching the gateway's HTTP Trigger endpoint with a validly-signed JWT) can send multiple concurrent copies of the exact same single-use JWT (`jti`). Because `isReplay` and `recordUsage` are not atomic, two or more concurrent `Authorize` calls can each observe `isReplay == false` before any of them calls `recordUsage`, letting the same JWT authenticate and trigger the workflow more than once. This is a concrete authentication/anti-replay bypass: it undermines the single-use guarantee the JWT replay cache is designed to provide, permitting duplicate workflow-trigger execution or duplicate request impersonation using one token that was intended to authorize only one action.

### Likelihood Explanation
Likelihood is moderate-to-high: any external, unauthenticated-by-privilege caller with access to a single valid JWT can trigger this simply by firing a small number of near-simultaneous requests (a trivial, no-cost attack requiring no special network position, matching the "no-privilege by default" bar). The race window is small (microseconds between the `RLock` read in `isReplay` and the later `Lock` write in `recordUsage`), but is fully attacker-controllable by choosing to send duplicate requests concurrently, and the gateway explicitly processes multiple concurrent user JSON-RPC messages.

### Recommendation
Make the check-and-mark operation atomic under a single write lock (or use a `sync.Map`/mutex-guarded "check-and-set" primitive) inside `jwtReplayCache`, e.g. add an `Acquire(jti string) bool` method that takes the `Lock`, checks existence, and inserts within one critical section, then have `Authorize` call this single atomic method instead of separate `isReplay` + `recordUsage` calls.

### Proof of Concept
1. Obtain one valid, signed JWT for an HTTP Trigger request with `jti = X`.
2. Fire two (or more) concurrent `HandleJSONRPCUserMessage` requests to the gateway carrying the identical JWT.
3. Both goroutines call `WorkflowMetadataHandler.Authorize`, each calling `h.jwtCache.isReplay(X)` before either has called `h.jwtCache.recordUsage(X)`.
4. Both requests pass authorization and are dispatched to the DON as legitimate, distinct trigger invocations, despite the JWT being intended for single use.

### Citations

**File:** core/services/gateway/handlers/capabilities/v2/http_handler.go (L392-402)
```go
func (h *gatewayHandler) HandleJSONRPCUserMessage(ctx context.Context, req jsonrpc.Request[json.RawMessage], callback handlers.Callback) error {
	h.metrics.IncrementTriggerRequestCount(ctx, h.lggr)
	err := h.triggerHandler.HandleUserTriggerRequest(ctx, &req, callback, time.Now())
	if err != nil {
		h.lggr.Errorw("failed to handle user trigger request", "requestID",
			req.ID, "err", err)
		// error response is sent to the response channel by the trigger handler
		// so return nil after logging
	}
	return nil
}
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
