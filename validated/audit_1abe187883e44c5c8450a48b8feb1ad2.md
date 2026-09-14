### Title
JWT replay-protection check-then-act race in `WorkflowMetadataHandler.Authorize` allows reuse of a single-use signed trigger request - ([File: core/services/gateway/handlers/capabilities/v2/workflow_metadata_handler.go])

### Summary
`WorkflowMetadataHandler.Authorize`, the JSON-RPC gateway authorization path invoked by every unprivileged HTTP trigger request (`HandleUserTriggerRequest` → `authorizeRequest` → `Authorize`), is intended to allow a signed JWT (`jti`) to be used exactly once. The "already used" check (`jwtCache.isReplay`) and the "mark used" step (`jwtCache.recordUsage`) are implemented as two separate, non-atomic critical sections, so concurrent requests presenting the identical signed JWT can both pass the replay check before either records usage — reusing a single-use authorization to trigger the workflow twice.

### Finding Description
`Authorize` reads the replay cache and records usage as two independent lock/unlock cycles instead of a single atomic check-and-record operation: [1](#0-0) 

Specifically, `isReplay` takes an `RLock`, checks membership, and releases the lock: [2](#0-1) 

Only after further work (looking up `authorizedKeys[workflowID]`, verifying the signer) does `recordUsage` take a *separate* `Lock` to insert the `jti`: [3](#0-2) 

Because there is no lock held across the whole "check-then-record" sequence, two goroutines handling concurrent requests that carry the exact same signed JWT can both call `isReplay(claims.ID)` and get `exists == false` before either calls `recordUsage`. Both requests are then treated as authorized and each proceeds to fan out a `workflows.execute` trigger to the DON shards via `sendWithRetries`: [4](#0-3) 

This is the same class of bug as the reported Ajna issue: an enforcement check that exists on one code path (in Ajna, `claimRewards`'s `isEpochClaimed` check) is either missing or not applied atomically elsewhere (Ajna's `_unstake`), letting the same single-use credential be consumed more than once. Here, the intended one-time-use guarantee for a JWT is undermined by a classic TOCTOU race between the check and the record step, both reachable directly from an unauthenticated/unprivileged HTTP client hitting the gateway's trigger endpoint.

Notably, the codebase has a correct pattern for exactly this problem elsewhere — `RequestReplayGuard.CheckAndRecord` in the Vault gateway path performs the lookup and insertion under one held lock: [5](#0-4) 

The HTTP trigger handler's `jwtReplayCache` does not follow this atomic pattern, which is the root cause.

### Impact Explanation
An unprivileged actor who can send an HTTP trigger request to the gateway (the same message envelope any client uses to invoke `workflows.execute`) can, by sending two copies of the same signed request concurrently, cause the workflow to be triggered twice using a JWT that is supposed to be single-use. This is a concrete bypass of a security control (JWT replay/quota protection) enforced on the internet-facing gateway, potentially causing duplicate/unauthorized workflow executions, resource consumption, or duplicate side effects downstream (e.g., duplicate on-chain actions initiated by the workflow), i.e., "unauthorized job run" / "quota bypass" as called out in the validation criteria.

### Likelihood Explanation
Triggering the race requires only replaying the identical HTTP request (same signed JWT, same body) concurrently or in close temporal proximity — something trivially scriptable by any caller with a valid signed request, with no special privileges beyond what's needed to obtain one legitimate trigger authorization. The narrow window between `isReplay` and `recordUsage` (network I/O, key lookups, and shard fan-out logic run in between) makes the race practically achievable, not merely theoretical.

### Recommendation
Make the check-and-record operation atomic, following the existing `RequestReplayGuard` pattern already used for Vault requests: hold a single lock (or use `sync.Map`/an atomic "insert-if-absent" primitive) across both the existence check and the insertion of `claims.ID`, e.g.:

```go
func (cache *jwtReplayCache) checkAndRecord(jti string) error {
    cache.mu.Lock()
    defer cache.mu.Unlock()
    if _, exists := cache.cache[jti]; exists {
        return ErrJTIAlreadyUsed
    }
    cache.cache[jti] = time.Now()
    return nil
}
```
and call this once from `Authorize` in place of the separate `isReplay`/`recordUsage` calls, ideally as early as possible (immediately after JWT signature verification) to minimize the window an attacker could exploit even without concurrency.

### Proof of Concept
1. Obtain one validly signed HTTP trigger request (JSON-RPC `workflows.execute`) with JWT `Auth` header containing `jti = X`, targeting a valid `workflowID`.
2. Fire two copies of this exact request concurrently at the gateway's HTTP trigger endpoint (e.g., using two goroutines/curl processes started at the same time).
3. Both requests reach `httpTriggerHandler.HandleUserTriggerRequest` → `authorizeRequest` → `WorkflowMetadataHandler.Authorize` nearly simultaneously.
4. Both goroutines execute `h.jwtCache.isReplay(claims.ID)` before either has called `h.jwtCache.recordUsage(claims.ID)`, so both see `exists == false` and pass authorization.
5. Both requests proceed past `authorizeRequest`, each generating its own execution ID and calling `sendWithRetries`, resulting in two separate workflow executions triggered from a single supposedly single-use signed JWT — confirmed by the DON receiving two distinct `workflows.execute` node sends for the same signer/workflow instead of one being rejected with "JWT token has already been used."

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

**File:** core/services/gateway/handlers/capabilities/v2/http_trigger_handler.go (L106-146)
```go
	key, err := h.authorizeRequest(ctx, workflowID, req, callback)
	if err != nil {
		return err
	}

	if err = h.checkRateLimit(ctx, workflowID, req.ID, callback); err != nil {
		return err
	}

	strippedWorkflowID := strings.TrimPrefix(workflowID, "0x")
	legacyExecutionID, err := workflows.EncodeExecutionID(strippedWorkflowID, req.ID) //nolint:staticcheck // legacy ID kept for observability comparison
	if err != nil {
		h.handleUserError(ctx, req.ID, jsonrpc.ErrInternal, internalErrorMessage, callback)
		return errors.New("error generating execution ID: " + err.Error())
	}
	// Workflows shouldn't use more than one HTTP trigger. If we ever need to support multiple triggers, we'd need to pass
	// trigger index to the Gateway handler and somehow allow senders to pick. For now, we use trigger index 0.
	// Execution IDs here are used only for logging.
	executionIDWithTriggerIndex, err := workflows.GenerateExecutionIDWithTriggerIndex(strippedWorkflowID, req.ID, 0)
	if err != nil {
		h.handleUserError(ctx, req.ID, jsonrpc.ErrInternal, internalErrorMessage, callback)
		return errors.New("error generating execution ID with trigger index: " + err.Error())
	}
	h.lggr.Debugw("processing request",
		"legacyExecutionID", legacyExecutionID,
		"executionIDWithTriggerIndex", executionIDWithTriggerIndex,
		"requestID", req.ID,
		"workflowID", workflowID)

	reqWithKey, err := reqWithAuthorizedKey(triggerReq, *key)
	if err != nil {
		h.handleUserError(ctx, req.ID, jsonrpc.ErrInternal, internalErrorMessage, callback)
		return errors.New("error marshaling trigger request: " + err.Error())
	}

	doneCh, err := h.setupCallback(ctx, req.ID, callback, requestStartTime, workflowID)
	if err != nil {
		return err
	}

	return h.sendWithRetries(ctx, legacyExecutionID, executionIDWithTriggerIndex, reqWithKey, workflowID, doneCh)
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
